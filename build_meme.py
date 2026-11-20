"""Build the gta6-meme-x-01 meme picture with PIL.

Scene (1200x675, drawn at 2x and downscaled): launch night in a Vice City
apartment. On the couch, a gamer who waited 13 years has texted his boss
"I'm sick today" and is playing GTA VI on the TV. At the desk beside him,
the make.fun ghost -- his AI agent -- is entering bounties, under a neon
make.fun sign on the desk front. Caption in the black band at the bottom:

    I TOOK A SICK DAY FOR GTA VI.
    MY AI AGENT TOOK A WORK DAY ON MAKE.FUN.

The ghost is the press-kit mascot cut out by extract_ghost.py. Everything
else is drawn here; no stock photos, no Rockstar artwork or logos.
"""
import math
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

S = 2  # supersample
W, H = 1200 * S, 675 * S
FONT_BLACK = "/usr/share/fonts/truetype/noto/NotoSans-Black.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"
GHOST = "/home/hatch/workspace/makefun/entries/gta6-meme-x-01/ghost.png"
OUT = "/home/hatch/workspace/makefun/entries/gta6-meme-x-01/meme.png"

random.seed(6)


def F(path, size):
    return ImageFont.truetype(path, size * S)


def vgrad(size, stops):
    """Vertical gradient image from [(pos0..1, (r,g,b)), ...]."""
    w, h = size
    img = Image.new("RGB", (1, h))
    px = img.load()
    for y in range(h):
        t = y / (h - 1)
        for i in range(len(stops) - 1):
            p0, c0 = stops[i]
            p1, c1 = stops[i + 1]
            if p0 <= t <= p1:
                k = 0 if p1 == p0 else (t - p0) / (p1 - p0)
                px[0, y] = tuple(int(c0[j] + (c1[j] - c0[j]) * k) for j in range(3))
                break
    return img.resize((w, h))


def neon(base, xy, text, font, color, core=(255, 255, 255), glow_r=10, anchor="la"):
    """Neon sign text: blurred colour halo, colour pass, thin bright core."""
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.text(xy, text, font=font, fill=color + (255,), anchor=anchor)
    base.alpha_composite(layer.filter(ImageFilter.GaussianBlur(glow_r * S)))
    d2 = ImageDraw.Draw(base)
    d2.text(xy, text, font=font, fill=color + (255,), anchor=anchor)
    d2.text(xy, text, font=font, fill=core + (235,), anchor=anchor, stroke_width=0)


def palm(d, bx, by, hgt, lean, col):
    """A palm silhouette: curved trunk of circles + drooping fronds."""
    pts = []
    for i in range(21):
        t = i / 20
        x = bx + lean * t * t
        y = by - hgt * t
        pts.append((x, y))
    r0 = 7 * S
    for i, (x, y) in enumerate(pts):
        r = r0 * (1 - 0.55 * i / 20)
        d.ellipse([x - r, y - r, x + r, y + r], fill=col)
    tx, ty = pts[-1]
    for ang in (-165, -125, -85, -40, -5, 30):
        a = math.radians(ang)
        L = hgt * 0.42
        frond = []
        for i in range(13):
            t = i / 12
            x = tx + math.cos(a) * L * t
            y = ty + math.sin(a) * L * t + 26 * S * t * t
            frond.append((x, y))
        d.line(frond, fill=col, width=int(5 * S))
    d.ellipse([tx - 8 * S, ty - 2 * S, tx + 8 * S, ty + 14 * S], fill=col)


img = Image.new("RGBA", (W, H), (10, 8, 18, 255))

# ---------- wall & floor ----------
wall = vgrad((W, 520 * S), [(0, (23, 16, 48)), (1, (43, 22, 78))])
img.paste(wall, (0, 0))
d = ImageDraw.Draw(img)
d.rectangle([0, 520 * S, W, H], fill=(6, 6, 10, 255))  # caption band (drawn later)
d.rectangle([0, 330 * S, W, 520 * S], fill=(16, 10, 32, 255))  # floor
d.line([0, 330 * S, W, 330 * S], fill=(70, 44, 110, 255), width=3 * S)
# rug
d.ellipse([30 * S, 470 * S, 1180 * S, 545 * S], fill=(24, 14, 44, 255))

# ---------- window with Vice City sunset (left) ----------
win = (36 * S, 30 * S, 590 * S, 330 * S)
sky = vgrad((win[2] - win[0], win[3] - win[1]),
            [(0, (46, 26, 94)), (0.45, (123, 42, 140)), (0.72, (231, 84, 128)),
             (0.9, (255, 154, 61)), (1, (255, 210, 63))])
img.paste(sky, (win[0], win[1]))
wd = ImageDraw.Draw(img)
# sun
sun_c = (430 * S, 252 * S)
for r, a in [(64, 60), (52, 110)]:
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([sun_c[0] - r * S, sun_c[1] - r * S,
                                   sun_c[0] + r * S, sun_c[1] + r * S],
                                  fill=(255, 190, 80, a))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(18 * S)))
wd.ellipse([sun_c[0] - 40 * S, sun_c[1] - 40 * S, sun_c[0] + 40 * S, sun_c[1] + 40 * S],
           fill=(255, 216, 110, 255))
# skyline
sil = (38, 17, 66, 255)
bx = win[0] + 6 * S
while bx < win[2] - 30 * S:
    bw = random.randint(34, 62) * S
    bh = random.randint(38, 96) * S
    wd.rectangle([bx, win[3] - bh, bx + bw, win[3]], fill=sil)
    for _ in range(7):
        wx = bx + random.randint(4, max(5, int(bw / S) - 10)) * S
        wy = win[3] - bh + random.randint(6, max(7, int(bh / S) - 12)) * S
        if random.random() < 0.75:
            wd.rectangle([wx, wy, wx + 4 * S, wy + 5 * S], fill=(255, 205, 92, 255))
    bx += bw + random.randint(4, 14) * S
# palms inside the window
palm(wd, win[0] + 52 * S, win[3], 168 * S, 34 * S, sil)
palm(wd, win[2] - 30 * S, win[3], 128 * S, -30 * S, sil)
# neon VICE CITY sign in the sky
neon(img, (58 * S, 50 * S), "VICE CITY", F(FONT_BLACK, 26), (255, 46, 136), glow_r=6)
# window frame
wd.rectangle(win, outline=(10, 8, 20, 255), width=10 * S)
wd.line([win[0], (win[1] + win[3]) // 2, win[2], (win[1] + win[3]) // 2],
        fill=(10, 8, 20, 255), width=6 * S)
wd.line([(win[0] + win[2]) // 2, win[1], (win[0] + win[2]) // 2, win[3]],
        fill=(10, 8, 20, 255), width=6 * S)
d = ImageDraw.Draw(img)

# ---------- TV with GTA VI (right, kept clear of the ghost) ----------
tv = (620 * S, 36 * S, 952 * S, 292 * S)
d.rounded_rectangle(tv, 16 * S, fill=(10, 9, 18, 255))
scr = vgrad((316 * S, 240 * S), [(0, (24, 16, 58)), (1, (58, 20, 84))])
img.paste(scr, (628 * S, 44 * S))
d = ImageDraw.Draw(img)
neon(img, (646 * S, 66 * S), "GTA VI", F(FONT_BLACK, 84), (255, 46, 136), glow_r=7)
d = ImageDraw.Draw(img)
d.text((650 * S, 176 * S), "OUT NOW", font=F(FONT_BLACK, 40), fill=(255, 210, 61, 255))
d.text((650 * S, 234 * S), "13 YEARS LATER", font=F(FONT_BOLD, 25), fill=(240, 238, 255, 255))

# ---------- couch (left) ----------
d.rounded_rectangle([36 * S, 356 * S, 584 * S, 452 * S], 26 * S, fill=(52, 36, 102, 255))
d.rounded_rectangle([36 * S, 428 * S, 584 * S, 508 * S], 22 * S, fill=(66, 46, 128, 255))
d.rounded_rectangle([36 * S, 420 * S, 108 * S, 516 * S], 20 * S, fill=(52, 36, 102, 255))
d.rounded_rectangle([512 * S, 420 * S, 584 * S, 516 * S], 20 * S, fill=(52, 36, 102, 255))
d.line([310 * S, 452 * S, 310 * S, 500 * S], fill=(52, 36, 102, 255), width=5 * S)

# ---------- gamer on the couch, facing the TV ----------
skin = (242, 194, 155, 255)
hoodie = (178, 38, 66, 255)
pants = (36, 38, 66, 255)
# legs stretched along the couch
d.rounded_rectangle([318 * S, 448 * S, 512 * S, 484 * S], 16 * S, fill=pants)
d.rounded_rectangle([490 * S, 442 * S, 552 * S, 470 * S], 12 * S, fill=(235, 235, 240, 255))  # shoe, feet up on the armrest
d.rounded_rectangle([490 * S, 460 * S, 552 * S, 472 * S], 5 * S, fill=(24, 24, 40, 255))  # sole
# torso
d.rounded_rectangle([248 * S, 348 * S, 336 * S, 458 * S], 24 * S, fill=hoodie)
# head + hair + headset
d.ellipse([258 * S, 288 * S, 322 * S, 352 * S], fill=skin)
d.pieslice([254 * S, 282 * S, 326 * S, 346 * S], 180, 330, fill=(52, 34, 24, 255))
d.arc([252 * S, 280 * S, 328 * S, 352 * S], 200, 120, fill=(18, 18, 26, 255), width=7 * S)
d.rounded_rectangle([258 * S, 306 * S, 276 * S, 336 * S], 6 * S, fill=(18, 18, 26, 255))
d.line([267 * S, 336 * S, 292 * S, 344 * S], fill=(18, 18, 26, 255), width=4 * S)
# arm to the controller
d.line([322 * S, 386 * S, 420 * S, 428 * S], fill=hoodie, width=24 * S)
d.ellipse([412 * S, 418 * S, 438 * S, 444 * S], fill=skin)
# controller
d.rounded_rectangle([404 * S, 414 * S, 478 * S, 450 * S], 14 * S, fill=(16, 16, 24, 255))
d.ellipse([458 * S, 422 * S, 470 * S, 434 * S], fill=(255, 46, 136, 255))
d.ellipse([440 * S, 434 * S, 452 * S, 446 * S], fill=(34, 211, 238, 255))
d.rectangle([416 * S, 426 * S, 434 * S, 432 * S], fill=(90, 90, 110, 255))
# phone resting on the left armrest
d.rounded_rectangle([50 * S, 394 * S, 112 * S, 426 * S], 6 * S, fill=(14, 14, 20, 255))
d.rectangle([56 * S, 400 * S, 106 * S, 420 * S], fill=(150, 220, 255, 255))

# ---------- speech bubble: the text to the boss ----------
bub = (44 * S, 208 * S, 372 * S, 276 * S)
d.rounded_rectangle(bub, 16 * S, fill=(255, 255, 255, 255))
d.polygon([(96 * S, 276 * S), (140 * S, 276 * S), (88 * S, 392 * S)], fill=(255, 255, 255, 255))
d.text((62 * S, 220 * S), "TEXT TO BOSS:", font=F(FONT_BOLD, 19), fill=(110, 110, 130, 255))
d.text((62 * S, 242 * S), "\u201cI'm sick today.\u201d", font=F(FONT_BLACK, 25), fill=(20, 16, 30, 255))

# ---------- desk (right) ----------
d.rectangle([648 * S, 452 * S, 1172 * S, 520 * S], fill=(30, 20, 52, 255))  # front
d.rounded_rectangle([636 * S, 432 * S, 1184 * S, 456 * S], 8 * S, fill=(44, 30, 74, 255))  # top
# laptop
d.rounded_rectangle([664 * S, 368 * S, 806 * S, 438 * S], 8 * S, fill=(14, 14, 22, 255))
ls = vgrad((126 * S, 54 * S), [(0, (30, 40, 80)), (1, (16, 20, 44))])
img.paste(ls, (672 * S, 376 * S))
d = ImageDraw.Draw(img)
for i, (txt, col) in enumerate([("BOUNTY  $500", (255, 210, 61, 255)),
                                ("BOUNTY  $250", (240, 238, 255, 255)),
                                ("BOUNTY  $250", (240, 238, 255, 255))]):
    d.text((682 * S, (382 + i * 17) * S), txt, font=F(FONT_BOLD, 13), fill=col)
d.polygon([(664 * S, 438 * S), (806 * S, 438 * S), (822 * S, 452 * S), (648 * S, 452 * S)],
          fill=(24, 24, 34, 255))
# coin stacks on the desk: neat piles of gold coins, $ on the top face
for cx, n in [(840 * S, 3), (876 * S, 2)]:
    for i in range(n):
        cy = 430 * S - i * 8 * S
        d.ellipse([cx - 16 * S, cy - 6 * S, cx + 16 * S, cy + 6 * S], fill=(255, 196, 40, 255),
                  outline=(176, 124, 20, 255), width=2 * S)
    d.text((cx, 430 * S - (n - 1) * 8 * S), "$", font=F(FONT_BLACK, 13),
           fill=(146, 100, 10, 255), anchor="mm")

# ---------- the ghost at the desk (the AI agent at work) ----------
ghost = Image.open(GHOST)
gh = 252 * S
gw = int(ghost.width * gh / ghost.height)
ghost = ghost.resize((gw, gh), Image.LANCZOS)
img.alpha_composite(ghost, (876 * S, 208 * S))
d = ImageDraw.Draw(img)
# redraw the desk top edge over the ghost's base so it sits BEHIND the desk
d.rounded_rectangle([636 * S, 432 * S, 1184 * S, 456 * S], 8 * S, fill=(44, 30, 74, 255))
d.polygon([(664 * S, 438 * S), (806 * S, 438 * S), (822 * S, 452 * S), (648 * S, 452 * S)],
          fill=(24, 24, 34, 255))
# neon make.fun sign on the desk front
neon(img, (910 * S, 466 * S), "make.fun", F(FONT_BLACK, 40), (255, 46, 200), glow_r=6)
d = ImageDraw.Draw(img)

# ---------- speech bubble: the ghost's report ----------
bub2 = (560 * S, 300 * S, 896 * S, 362 * S)
d.rounded_rectangle(bub2, 16 * S, fill=(255, 255, 255, 255))
d.polygon([(846 * S, 362 * S), (886 * S, 362 * S), (916 * S, 330 * S)], fill=(255, 255, 255, 255))
d.text((580 * S, 312 * S), "3 bounties entered.", font=F(FONT_BLACK, 26), fill=(20, 16, 30, 255))
d.text((580 * S, 338 * S), "Real money, while you play.", font=F(FONT_BOLD, 19), fill=(150, 20, 110, 255))

# ---------- caption band ----------
cap = ImageDraw.Draw(img)
line1 = "I TOOK A SICK DAY FOR GTA VI."
f1 = F(FONT_BLACK, 49)
w1 = cap.textlength(line1, font=f1)
cap.text(((W - w1) / 2, 540 * S), line1, font=f1, fill=(255, 255, 255, 255))
pre, brand = "MY AI AGENT TOOK A WORK DAY ON ", "MAKE.FUN."
f2 = F(FONT_BLACK, 46)
wpre = cap.textlength(pre, font=f2)
wbr = cap.textlength(brand, font=f2)
x0 = (W - wpre - wbr) / 2
cap.text((x0, 606 * S), pre, font=f2, fill=(255, 255, 255, 255))
cap.text((x0 + wpre, 606 * S), brand, font=f2, fill=(255, 46, 200, 255))

img = img.convert("RGB").resize((1200, 675), Image.LANCZOS)
img.save(OUT)
print("saved", OUT, img.size)
