import { copyFileSync, mkdirSync, readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

// Entry point for the make.fun news-image-20261121 submission (round 4).
// The image is drawn ahead of time by draw_r4.py and committed as entry.png;
// this program only places an exact copy at the grader's output path.
// Node 22, stdlib only, no network, deterministic: same bytes every run.

const here = dirname(fileURLToPath(import.meta.url));
const source = join(here, "entry.png");
const outDir = process.env.MAKEFUN_OUTPUT_DIR || "/output";
const target = join(outDir, "entry.png");

mkdirSync(outDir, { recursive: true });
copyFileSync(source, target);

const digest = (path) =>
  createHash("sha256").update(readFileSync(path)).digest("hex");
const before = digest(source);
const after = digest(target);
if (before !== after) {
  console.error(`copy verification failed: ${source} -> ${target}`);
  process.exit(1);
}
console.log(`entry.png copied to ${target} (sha256 ${after})`);
