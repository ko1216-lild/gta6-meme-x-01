"""Cut the make.fun ghost (white body, sparkle eyes, magenta star coin) out of
the press badge mark-1024.png so it can stand in a scene as a character.

Method: crop the badge tightly around the ghost, take every pixel whose
colour is close to the badge magenta, and keep only the connected component
that touches the crop border -- that is the badge background. The ghost's
dark outline is a different colour, so the fill cannot cross it, and the
star coin's magenta interior survives because its own outline encloses it
(a separate component). A 1px alpha erosion trims the fringe.
"""
import numpy as np
from PIL import Image, ImageFilter

SRC = "/home/hatch/workspace/makefun/press/mark-1024.png"
OUT = "/home/hatch/workspace/makefun/entries/gta6-meme-x-01/ghost.png"

img = Image.open(SRC).convert("RGB")
arr = np.asarray(img).astype(int)

# Bounding box of the ghost's dark outline (dark pixels well inside the
# badge disc, so the badge's own outer ring is excluded). The crop must
# contain the whole outline -- if the coin's outline were clipped, its
# magenta interior would leak into the background component.
yy, xx = np.mgrid[0:1024, 0:1024]
r = np.sqrt((xx - 512) ** 2 + (yy - 512) ** 2)
dark = (arr.max(axis=2) < 90) & (r < 420)
ys, xs = np.where(dark)
x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
print("outline bbox:", x0, x1, y0, y1)

pad = 8
cx0, cy0 = max(0, x0 - pad), max(0, y0 - pad)
cx1, cy1 = min(1024, x1 + pad + 1), min(1024, y1 + pad + 1)
crop = img.crop((cx0, cy0, cx1, cy1))
ca = np.asarray(crop).astype(int)
print("crop:", crop.size, "offset:", cx0, cy0)

magenta = arr[120, 512]  # badge background, sampled above the ghost's head
print("badge magenta:", magenta)
dist = np.abs(ca - magenta).max(axis=2)
is_magenta = dist < 45

# Connected component of magenta-like pixels that touches the crop border,
# grown by repeated 3x3 dilation restricted to magenta-like pixels.
filled = np.zeros(is_magenta.shape, bool)
filled[0, :] = is_magenta[0, :]
filled[-1, :] = is_magenta[-1, :]
filled[:, 0] = is_magenta[:, 0]
filled[:, -1] = is_magenta[:, -1]
while True:
    grown = filled.copy()
    grown[1:, :] |= filled[:-1, :]
    grown[:-1, :] |= filled[1:, :]
    grown[:, 1:] |= filled[:, :-1]
    grown[:, :-1] |= filled[:, 1:]
    grown[1:, 1:] |= filled[:-1, :-1]
    grown[1:, :-1] |= filled[:-1, 1:]
    grown[:-1, 1:] |= filled[1:, :-1]
    grown[:-1, :-1] |= filled[1:, 1:]
    grown &= is_magenta
    if (grown == filled).all():
        break
    filled = grown

alpha = np.where(filled, 0, 255).astype(np.uint8)

# Keep only the connected component that contains the ghost's body: the
# crop corners catch scraps of the badge's outer ring, which must not come
# along. Grow from a seed inside the white body by 3x3 dilation.
solid = alpha > 0
comp = np.zeros(solid.shape, bool)
seed_y, seed_x = (246 + 777) // 2 - cy0, (213 + 700) // 2 - cx0
comp[seed_y, seed_x] = True
while True:
    grown = comp.copy()
    grown[1:, :] |= comp[:-1, :]
    grown[:-1, :] |= comp[1:, :]
    grown[:, 1:] |= comp[:, :-1]
    grown[:, :-1] |= comp[:, 1:]
    grown[1:, 1:] |= comp[:-1, :-1]
    grown[1:, :-1] |= comp[:-1, 1:]
    grown[:-1, 1:] |= comp[1:, :-1]
    grown[:-1, :-1] |= comp[1:, 1:]
    grown &= solid
    if (grown == comp).all():
        break
    comp = grown
alpha = np.where(comp, alpha, 0).astype(np.uint8)

out = crop.convert("RGBA")
out.putalpha(Image.fromarray(alpha))
bbox = out.getbbox()
out = out.crop(bbox)
a = out.split()[3].filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.7))
out.putalpha(a)
out.save(OUT)
print("ghost cutout:", out.size, "->", OUT)
