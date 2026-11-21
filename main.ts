// news-image-20261121 entry — copy the rendered entry.png into the grader output dir.
// Deterministic: same bytes in, same bytes out, verified byte-for-byte after copy.
import { copyFileSync, mkdirSync, readFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const source = join(here, "entry.png");
const outDir = resolve(process.env.MAKEFUN_OUTPUT_DIR ?? "/output");
mkdirSync(outDir, { recursive: true });
const target = join(outDir, "entry.png");
copyFileSync(source, target);
const before = readFileSync(source);
const after = readFileSync(target);
if (!before.equals(after)) {
  console.error("entry.png copy mismatch");
  process.exit(1);
}
console.log(`copied entry.png (${before.length} bytes) -> ${target}`);
