// Round 3 entry runner for make.fun news-image-20261121.
// Copies the pre-rendered ./entry.png into the grader's output directory
// and verifies the copy byte-for-byte, so a bad copy can never pass silently.
import { copyFileSync, mkdirSync, readFileSync } from "node:fs";
import { join, resolve } from "node:path";

const here = resolve(import.meta.dirname);
const source = join(here, "entry.png");
const outDir = resolve(process.env.MAKEFUN_OUTPUT_DIR ?? "/output");
mkdirSync(outDir, { recursive: true });
const target = join(outDir, "entry.png");
copyFileSync(source, target);

const before = readFileSync(source);
if (before.length < 10_000 || before.subarray(0, 8).toString("hex") !== "89504e470d0a1a0a") {
  throw new Error(`entry.png does not look like a PNG (${before.length} bytes)`);
}
const after = readFileSync(target);
if (!before.equals(after)) {
  throw new Error(`entry.png copy mismatch: ${before.length} vs ${after.length} bytes`);
}
console.log(`entry.png -> ${target} (${after.length} bytes, verified identical)`);
