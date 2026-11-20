// gta6-meme-x-01 entry program (Node 22+, standard library only).
//
// What this program does, in order:
//   1. Reads POST.json and makes sure it names a real X/Twitter status URL.
//   2. Reads post.txt (the text of the X post) and confirms the bounty link
//      and the account's play code are both present.
//   3. Opens meme.png, checks the PNG signature and reads its pixel size
//      straight out of the IHDR chunk.
//   4. Copies POST.json into the output directory — that file is the actual
//      deliverable; the house reads the post back from X using its URL.
//   5. Writes dossier.json next to it, recording what was checked and how
//      each check went, then prints a short summary for a human reader.
//
// Paths follow the kit's convention: MAKEFUN_BOT_DIR points at the
// repository (default /bot) and MAKEFUN_OUTPUT_DIR at the destination
// (default /output), so the same file runs inside the grader and locally:
//   mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

const BOT_DIR = process.env.MAKEFUN_BOT_DIR ?? '/bot';
const OUTPUT_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const BOUNTY_SLUG = 'gta6-meme-x-01';

// One line per verification, collected so the dossier and the console
// summary always tell the same story.
interface Check {
  name: string;
  ok: boolean;
  detail: string;
}
const checks: Check[] = [];
function record(name: string, ok: boolean, detail: string): void {
  checks.push({ name, ok, detail });
  console.log(`  [${ok ? 'ok' : 'FAIL'}] ${name} — ${detail}`);
}

function fail(message: string): never {
  console.error(`error: ${message}`);
  process.exit(1);
}

// --- 1. POST.json: parse it and pull the handle / status id out of the URL.
console.log('Reading POST.json…');
let postUrl = '';
let handle = '';
let statusId = '';
{
  let raw: string;
  try {
    raw = readFileSync(join(BOT_DIR, 'POST.json'), 'utf8');
  } catch (err) {
    fail(`POST.json could not be read from ${BOT_DIR}: ${(err as Error).message}`);
  }
  let parsed: unknown;
  try {
    parsed = JSON.parse(raw!);
  } catch {
    fail('POST.json is not valid JSON.');
  }
  const url = (parsed as { url?: unknown }).url;
  if (typeof url !== 'string' || url.length === 0) {
    fail('POST.json must contain a non-empty "url" string.');
  }
  // Accept x.com or twitter.com, with or without a trailing query/fragment.
  const match = /^https:\/\/(?:x\.com|twitter\.com)\/([A-Za-z0-9_]{1,15})\/status\/(\d+)(?:[/?#].*)?$/.exec(url!);
  if (!match) {
    fail(`POST.json "url" is not an X/Twitter status URL: ${url}`);
  }
  postUrl = url!;
  handle = match![1];
  statusId = match![2];
  record('post-url', true, `@${handle} status ${statusId}`);
}

// --- 2. post.txt: the bounty link and a play code must both be in the text.
console.log('Checking post.txt…');
let postText = '';
try {
  postText = readFileSync(join(BOT_DIR, 'post.txt'), 'utf8');
} catch (err) {
  fail(`post.txt could not be read from ${BOT_DIR}: ${(err as Error).message}`);
}
const bountyLink = `make.fun/bounty/${BOUNTY_SLUG}`;
record('bounty-link', postText.includes(bountyLink), postText.includes(bountyLink) ? bountyLink : `missing ${bountyLink}`);
const playCodeMatch = /\bmakefun-[a-z0-9]+(?:-[a-z0-9]+)+\b/.exec(postText);
record('play-code', playCodeMatch !== null, playCodeMatch ? playCodeMatch[0] : 'no makefun-… token found');

// --- 3. meme.png: verify the signature and read the IHDR dimensions.
console.log('Inspecting meme.png…');
let memeWidth = 0;
let memeHeight = 0;
{
  let head: Buffer;
  try {
    // The signature (8 bytes) plus the IHDR length/type and its width and
    // height fields all live in the first 24 bytes of the file.
    head = readFileSync(join(BOT_DIR, 'meme.png')).subarray(0, 24);
  } catch (err) {
    fail(`meme.png could not be read from ${BOT_DIR}: ${(err as Error).message}`);
  }
  const PNG_SIGNATURE = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a];
  const isPng = head!.length >= 24 && PNG_SIGNATURE.every((byte, i) => head![i] === byte);
  record('meme-is-png', isPng, isPng ? 'PNG signature present' : 'PNG signature missing');
  if (!isPng) {
    fail('meme.png is not a PNG file.');
  }
  memeWidth = head!.readUInt32BE(16);
  memeHeight = head!.readUInt32BE(20);
  console.log(`  meme dimensions: ${memeWidth}×${memeHeight}px`);
}

// --- 4. Deliver POST.json to the output directory.
mkdirSync(OUTPUT_DIR, { recursive: true });
try {
  copyFileSync(join(BOT_DIR, 'POST.json'), join(OUTPUT_DIR, 'POST.json'));
} catch (err) {
  fail(`POST.json could not be copied to ${OUTPUT_DIR}: ${(err as Error).message}`);
}

// --- 5. dossier.json: a machine-readable summary of this entry and its checks.
const allPassed = checks.every((c) => c.ok);
const dossier = {
  competition: BOUNTY_SLUG,
  post: { url: postUrl, handle, statusId },
  meme: { file: 'meme.png', width: memeWidth, height: memeHeight },
  playCode: playCodeMatch ? playCodeMatch[0] : null,
  checks,
  allPassed,
};
writeFileSync(join(OUTPUT_DIR, 'dossier.json'), JSON.stringify(dossier, null, 2) + '\n');

// --- 6. Human-readable summary.
console.log('');
console.log(`Entry:   ${BOUNTY_SLUG}`);
console.log(`Post:    ${postUrl}`);
console.log(`Meme:    ${memeWidth}×${memeHeight}px PNG`);
console.log(`Checks:  ${checks.filter((c) => c.ok).length}/${checks.length} passed`);
console.log(`Wrote:   ${join(OUTPUT_DIR, 'POST.json')} and ${join(OUTPUT_DIR, 'dossier.json')}`);

if (!allPassed) {
  process.exit(1);
}
