// Caricamento in sola lettura: solo richieste GET verso file statici.
const SUPPORTED_MANIFEST = '1.0';
const SUPPORTED_CATALOG = '1.0';

export class DataError extends Error {}

async function get(url, kind) {
  let res;
  try {
    res = await fetch(url, { method: 'GET', cache: kind === 'catalogo' ? 'no-cache' : 'default' });
  } catch (e) {
    throw new DataError(`Impossibile scaricare ${kind} (${url}): ${e.message}`);
  }
  if (!res.ok) throw new DataError(`File ${kind} mancante o non accessibile: ${url} (HTTP ${res.status})`);
  return res;
}

export async function loadCatalog(base) {
  const url = `${base}catalog.json`;
  const res = await get(url, 'catalogo');
  let cat;
  try {
    cat = await res.json();
  } catch {
    throw new DataError(`Catalogo non leggibile (JSON non valido): ${url}`);
  }
  if (cat.catalog_version !== SUPPORTED_CATALOG) {
    throw new DataError(`Versione catalogo ${cat.catalog_version} non supportata (attesa ${SUPPORTED_CATALOG})`);
  }
  if (!Array.isArray(cat.layouts) || !cat.layouts.length) throw new DataError('Il catalogo non contiene layout');
  return cat;
}

export async function loadLayout(base, entry) {
  const mres = await get(base + entry.manifest, 'manifest');
  let manifest;
  try {
    manifest = await mres.json();
  } catch {
    throw new DataError(`Manifest non leggibile: ${entry.manifest}`);
  }
  if (manifest.manifest_version !== SUPPORTED_MANIFEST) {
    throw new DataError(`Manifest versione ${manifest.manifest_version} incompatibile (attesa ${SUPPORTED_MANIFEST})`);
  }
  if (manifest.build?.build_id !== entry.build_id || manifest.layout?.layout_id !== entry.layout_id) {
    throw new DataError(
      `Manifest di un'altra build: catalogo ${entry.layout_id}/${entry.build_id}, ` +
        `manifest ${manifest.layout?.layout_id}/${manifest.build?.build_id}`,
    );
  }
  const gres = await get(base + entry.glb, 'modello GLB');
  const glb = await gres.arrayBuffer();
  if (crypto?.subtle) {
    const digest = await crypto.subtle.digest('SHA-256', glb);
    const hex = [...new Uint8Array(digest)].map((b) => b.toString(16).padStart(2, '0')).join('');
    if (hex !== manifest.gltf.sha256) {
      throw new DataError(`GLB non corrispondente al manifest (sha256 ${hex.slice(0, 12)}… ≠ ${manifest.gltf.sha256.slice(0, 12)}…)`);
    }
  }
  return { manifest, glb };
}
