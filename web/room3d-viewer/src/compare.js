// Confronto fra due manifest tramite ID stabili e dati JSON.
import { dist3 } from './transform.js';

const MOVE_TOL = 0.001; // m

function bodies(manifest) {
  const map = new Map();
  for (const e of manifest.entities) {
    if (e.role === 'body') map.set(e.entity_id, e);
  }
  return map;
}

const json = (o) => JSON.stringify(o ?? null);

export function diffManifests(a, b) {
  const A = bodies(a);
  const B = bodies(b);
  const rows = [];
  for (const [id, ea] of A) {
    const eb = B.get(id);
    if (!eb) {
      rows.push({ id, kind: 'removed', name: ea.name, detail: 'presente solo in A' });
      continue;
    }
    const ca = ea.center ?? ea.bbox_center;
    const cb = eb.center ?? eb.bbox_center;
    const d = dist3(ca, cb);
    const changes = [];
    if (d > MOVE_TOL) changes.push(`spostato di ${(d * 100).toFixed(1).replace('.', ',')} cm`);
    if (json(ea.orientation) !== json(eb.orientation)) changes.push('orientamento');
    if (json(ea.bbox_size) !== json(eb.bbox_size)) changes.push('dimensioni');
    if (json(ea.pipe?.points) !== json(eb.pipe?.points)) changes.push('percorso');
    if (json(ea.properties) !== json(eb.properties)) changes.push('proprietà');
    if (ea.state !== eb.state || ea.data_status !== eb.data_status) changes.push('stato dati');
    // le frecce e le altre parti dello stesso componente contano nel confronto
    const partsA = a.entities.filter((e) => e.entity_id === id).map((e) => e.semantic_hash).sort();
    const partsB = b.entities.filter((e) => e.entity_id === id).map((e) => e.semantic_hash).sort();
    const geomChanged = json(partsA) !== json(partsB);
    if (!changes.length && geomChanged) changes.push('geometria');
    if (changes.length) {
      rows.push({ id, kind: d > MOVE_TOL ? 'moved' : 'modified', name: ea.name, detail: changes.join(', ') });
    }
  }
  for (const [id, eb] of B) {
    if (!A.has(id)) rows.push({ id, kind: 'added', name: eb.name, detail: 'presente solo in B' });
  }
  const order = { added: 0, removed: 1, moved: 2, modified: 3 };
  rows.sort((x, y) => order[x.kind] - order[y.kind] || x.id.localeCompare(y.id));
  return rows;
}

export const DIFF_LABELS = {
  added: 'aggiunto',
  removed: 'rimosso',
  moved: 'spostato',
  modified: 'modificato',
};
