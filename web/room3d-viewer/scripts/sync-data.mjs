// Copia gli output del generatore (build/room3d) in public/data per il web.
// Solo catalogo, manifest, GLB e immagini: il .blend non serve al browser.
// Uso: node scripts/sync-data.mjs [cartella_build]   (default ../../build/room3d)
import { cpSync, existsSync, mkdirSync, readFileSync, rmSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const src = resolve(process.argv[2] ?? join(here, '..', '..', '..', 'build', 'room3d'));
const dst = resolve(join(here, '..', 'public', 'data'));

const catPath = join(src, 'catalog.json');
if (!existsSync(catPath)) {
  console.error(`Catalogo non trovato: ${catPath}\nEseguire prima la build Blender (vedi docs/room3d/README.md).`);
  process.exit(1);
}
const catalog = JSON.parse(readFileSync(catPath, 'utf8'));
const sha = (p) => createHash('sha256').update(readFileSync(p)).digest('hex');

rmSync(dst, { recursive: true, force: true });
mkdirSync(dst, { recursive: true });
for (const e of catalog.layouts) {
  // coerenza: manifest e GLB devono essere quelli registrati nel catalogo
  if (sha(join(src, e.manifest)) !== e.manifest_sha256) throw new Error(`manifest alterato: ${e.manifest}`);
  if (sha(join(src, e.glb)) !== e.glb_sha256) throw new Error(`GLB alterato: ${e.glb}`);
  // immagini: hash nel manifest e nel nome del file (servite con cache immutabile)
  const man = JSON.parse(readFileSync(join(src, e.manifest), 'utf8'));
  for (const [view, rel] of Object.entries(man.images ?? {})) {
    const h = sha(join(src, e.path, rel));
    if (h !== man.images_sha256?.[view] || !rel.endsWith(`-${h.slice(0, 16)}.png`)) throw new Error(`immagine alterata: ${rel}`);
  }
  cpSync(join(src, e.path), join(dst, e.path), {
    recursive: true,
    filter: (p) => !p.endsWith('.blend') && !p.endsWith('.blend1'),
  });
}
cpSync(catPath, join(dst, 'catalog.json'));
console.log(`Dati copiati in ${dst}: ${catalog.layouts.map((e) => e.layout_id).join(', ')}`);
