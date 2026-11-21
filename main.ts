// Round 2 entry runner for make.fun news-image-20261121.
// Copies ./entry.png into the grader output directory and verifies the
// copy byte-for-byte, so the graded file is exactly the drawn image.
import { copyFileSync, mkdirSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const src = join(here, "entry.png");
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
mkdirSync(outDir, { recursive: true });
const dest = join(outDir, "entry.png");

copyFileSync(src, dest);

const original = readFileSync(src);
const copied = readFileSync(dest);
if (!original.equals(copied)) {
  console.error(`entry.png copy mismatch: ${src} -> ${dest}`);
  process.exit(1);
}
console.log(`entry.png (${original.length} bytes) copied to ${dest}, byte-identical`);
