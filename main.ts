// Entry point for the news-image-20261121 make.fun submission.
// Copies the pre-rendered front page (entry.png, drawn by draw.py) into
// the grader's output directory and proves the copy is byte-identical,
// so what gets graded is exactly the image reviewed in this repo.
import { copyFileSync, mkdirSync, readFileSync } from "node:fs";
import { join, resolve } from "node:path";

const repoRoot = resolve(import.meta.dirname);
const source = join(repoRoot, "entry.png");
const outDir = resolve(process.env.MAKEFUN_OUTPUT_DIR ?? "/output");
mkdirSync(outDir, { recursive: true });
const target = join(outDir, "entry.png");
copyFileSync(source, target);

const before = readFileSync(source);
const after = readFileSync(target);
if (!before.equals(after)) {
  throw new Error("entry.png copy mismatch: bytes differ after copy");
}
console.log(`entry.png -> ${target} (${after.length} bytes, verified identical)`);
