// Visualizzatore in sola lettura del modello 3D Salamai.
// Le modifiche al modello passano dai sorgenti JSON/Python e dalla
// rigenerazione: qui si consulta soltanto (nessuna scrittura, nessun comando).
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { DataError, loadCatalog, loadLayout } from './data.js';
import { ModelPane } from './pane.js';
import { DIFF_LABELS, diffManifests } from './compare.js';
import { dist3, fmtCm, fmtM, fmtSizeCm, fmtVec } from './transform.js';
import './style.css';

const DATA = './data/';
const STATUS_TEXT = {
  measured: 'misurato',
  declared: 'dichiarato',
  derived: 'derivato',
  assumed: 'ASSUNTO',
  unknown: 'SCONOSCIUTO (valore provvisorio)',
};
const STATE_TEXT = { existing: 'esistente', installed: 'installato', planned: 'pianificato', placeholder: 'SEGNAPOSTO' };
const KIND_TEXT = {
  real_plan: 'reale · pianificato',
  real_as_built: 'reale · rilevato',
  hypothetical_demo: 'IPOTESI DIMOSTRATIVA — non è uno storico reale',
};
const STRUCT = [
  ['floor', 'Pavimento'],
  ['ceiling', 'Soffitto'],
  ['wall_y0', 'Parete porta'],
  ['wall_y1', 'Parete di fondo'],
  ['wall_x0', 'Parete sinistra'],
  ['wall_x1', 'Parete destra'],
];

const $ = (sel) => document.querySelector(sel);
const el = (tag, attrs = {}, ...kids) => {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === 'class') e.className = v;
    else if (k.startsWith('on')) e.addEventListener(k.slice(2), v);
    else if (v !== undefined && v !== null) e.setAttribute(k, v);
  }
  for (const k of kids.flat()) if (k !== null && k !== undefined) e.append(k.nodeType ? k : String(k));
  return e;
};

const state = {
  catalog: null,
  a: null, // { entry, manifest }
  b: null,
  panes: [],
  mode: 'select',
  measure: [],
  snap: true,
  dims: false,
  diff: null,
};

// ------------------------------------------------------------ avvio

function webglAvailable() {
  try {
    const c = document.createElement('canvas');
    return !!(window.WebGL2RenderingContext && c.getContext('webgl2'));
  } catch {
    return false;
  }
}

function showError(msg) {
  const box = $('#error');
  box.querySelector('.msg').textContent = msg;
  box.hidden = false;
}

function setLoading(on, text = 'Caricamento…') {
  $('#loading').hidden = !on;
  $('#loading .txt').textContent = text;
}

let camera;
let controls = [];

function setupCamera() {
  camera = new THREE.PerspectiveCamera(45, 1, 0.02, 100);
}

function makeControls(pane) {
  const c = new OrbitControls(camera, pane.renderer.domElement);
  c.enableDamping = false;
  c.screenSpacePanning = true;
  c.touches = { ONE: THREE.TOUCH.ROTATE, TWO: THREE.TOUCH.DOLLY_PAN };
  if (controls.length) c.target = controls[0].target; // camera sincronizzata fra i riquadri
  c.addEventListener('change', requestRender);
  return c;
}

let renderQueued = false;
function requestRender() {
  if (renderQueued) return;
  renderQueued = true;
  requestAnimationFrame(() => {
    renderQueued = false;
    for (const p of state.panes) {
      if (p.selBox) p.selBox.update();
      p.render(camera);
    }
  });
}

function layoutPanes() {
  const host = $('#panes');
  host.classList.toggle('split', state.panes.length === 2);
  let aspect = 1;
  for (const p of state.panes) aspect = p.resize();
  camera.aspect = aspect;
  camera.updateProjectionMatrix();
  requestRender();
}

function ensurePanes(n) {
  const host = $('#panes');
  while (state.panes.length < n) {
    const div = el('div', { class: 'pane' });
    host.append(div);
    const pane = new ModelPane(div, true);
    state.panes.push(pane);
    controls.push(makeControls(pane));
    bindPointer(pane);
  }
  while (state.panes.length > n) {
    const pane = state.panes.pop();
    controls.pop().dispose();
    pane.renderer.dispose();
    pane.container.remove();
  }
  layoutPanes();
}

// ------------------------------------------------------------ viste

function roomCenterAndRadius() {
  const m = state.a.manifest;
  const [sx, sy, sz] = m.room.interior_size;
  return { c: [sx / 2, sy / 2, sz / 2], r: Math.hypot(sx, sy, sz) / 2 };
}

function setView(name) {
  const pane = state.panes[0];
  const { c, r } = roomCenterAndRadius();
  const dirs = {
    top: [0, -0.0001, 1],
    front: [0, -1, 0.0],
    side: [1, 0, 0.0],
    axon: [-0.75, -1.1, 0.95],
  };
  const d = dirs[name];
  const n = Math.hypot(...d);
  const dist = (r / Math.tan(THREE.MathUtils.degToRad(camera.fov / 2)) / Math.min(1, camera.aspect)) * 0.95;
  const eye = c.map((v, i) => v + (d[i] / n) * dist);
  camera.position.copy(pane.tf.toGltf(eye));
  controls[0].target.copy(pane.tf.toGltf(c));
  camera.up.set(0, 1, 0);
  camera.lookAt(controls[0].target);
  for (const ctl of controls) ctl.update();
  document.querySelectorAll('[data-view]').forEach((b) => b.classList.toggle('active', b.dataset.view === name));
  requestRender();
}

// ------------------------------------------------------------ caricamento layout

async function openLayouts(aId, bId) {
  setLoading(true);
  $('#error').hidden = true;
  try {
    const entryA = state.catalog.layouts.find((e) => e.layout_id === aId);
    if (!entryA) throw new DataError(`Layout ${aId} non presente nel catalogo`);
    const entryB = bId ? state.catalog.layouts.find((e) => e.layout_id === bId) : null;
    if (bId && !entryB) throw new DataError(`Layout ${bId} non presente nel catalogo`);
    const [la, lb] = await Promise.all([loadLayout(DATA, entryA), entryB ? loadLayout(DATA, entryB) : null]);
    ensurePanes(entryB ? 2 : 1);
    await state.panes[0].load(la.manifest, la.glb);
    state.a = { entry: entryA, manifest: la.manifest };
    state.panes[0].setTitle(entryB ? `A · ${entryA.layout_id}` : '', entryA.kind === 'hypothetical_demo');
    if (entryB) {
      await state.panes[1].load(lb.manifest, lb.glb);
      state.b = { entry: entryB, manifest: lb.manifest };
      state.panes[1].setTitle(`B · ${entryB.layout_id}`, entryB.kind === 'hypothetical_demo');
      state.diff = diffManifests(la.manifest, lb.manifest);
    } else {
      state.b = null;
      state.diff = null;
    }
    state.measure = [];
    applyUiStateToPanes();
    renderLayoutInfo();
    renderLayers();
    renderDiff();
    renderSelection(null);
    renderMeasure();
    layoutPanes();
    setView('axon');
    const url = new URL(window.location.href);
    url.searchParams.set('layout', aId);
    if (bId) url.searchParams.set('compare', bId);
    else url.searchParams.delete('compare');
    history.replaceState(null, '', url);
  } catch (e) {
    console.error(e);
    showError(e.message);
  } finally {
    setLoading(false);
  }
}

function applyUiStateToPanes() {
  for (const p of state.panes) {
    p.setDimensions(state.dims);
    p.tintDiff(state.diff);
  }
  // la visibilità dei layer è condivisa fra i riquadri
  const src = state.panes[0];
  for (const p of state.panes.slice(1)) {
    for (const [k, v] of src.layerVisible) p.setLayer(k, v);
    for (const [k, v] of src.structMode) p.setStruct(k, v);
  }
}

// ------------------------------------------------------------ pannelli

function badge(text, cls) {
  return el('span', { class: `badge ${cls}` }, text);
}

function statusBadge(st) {
  return badge(STATUS_TEXT[st] ?? st, `st-${st}`);
}

function renderLayoutInfo() {
  const box = $('#layout-info');
  const m = state.a.manifest;
  const e = state.a.entry;
  box.replaceChildren(
    el('div', {}, el('strong', {}, `${e.layout_id} rev ${e.revision}`), ' ', badge(KIND_TEXT[e.kind] ?? e.kind, `kind-${e.kind}`)),
    el('div', { class: 'muted' }, m.layout.title),
    el('div', { class: 'small' }, `Stanza interna ${fmtSizeCm(m.room.interior_size)} · volume lordo ${m.room.volume_gross_m3.toLocaleString('it-IT')} m³ (non è il volume libero)`),
    el('div', { class: 'small mono' }, `build ${m.build.build_id} · config ${m.build.config_hash.slice(0, 12)}${m.build.source_commit ? ` · commit ${m.build.source_commit.slice(0, 8)}${m.build.source_dirty ? ' (modifiche non registrate)' : ''}` : ''}`),
    state.catalog.layouts.filter((x) => x.kind.startsWith('real')).length === 1
      ? el('div', { class: 'small warn' }, 'Esiste una sola disposizione reale (pianificata). Gli altri layout sono ipotesi dimostrative.')
      : null,
    el('div', { class: 'small warn' }, 'Botola: 40 cm dalla parete porta al bordo vicino = ASSUNZIONE NON CONFERMATA. Altezza porta sconosciuta (1,90 m solo per il disegno).'),
  );
}

function renderLayers() {
  const box = $('#layers');
  const m = state.a.manifest;
  const pane = state.panes[0];
  const list = el('div', { class: 'layer-list' });
  for (const l of m.layers) {
    if (l.id === 'quote_annotazioni') continue;
    const id = `layer-${l.id}`;
    const cb = el('input', { type: 'checkbox', id });
    cb.checked = pane.layerVisible.get(l.id);
    cb.disabled = l.count === 0;
    cb.addEventListener('change', () => {
      for (const p of state.panes) p.setLayer(l.id, cb.checked);
      requestRender();
    });
    list.append(
      el('label', { for: id, class: l.count === 0 ? 'disabled' : '' }, cb, ` ${l.label} `, el('span', { class: 'muted' }, `(${l.count})`)),
    );
    if (l.count === 0 && l.note) list.append(el('div', { class: 'small muted indent' }, l.note));
  }
  const all = (on) => () => {
    for (const p of state.panes) for (const l of m.layers) p.setLayer(l.id, on);
    renderLayers();
    requestRender();
  };
  const struct = el('div', { class: 'struct-list' });
  for (const [sid, name] of STRUCT) {
    const sel = el('select', { 'aria-label': name },
      el('option', { value: 'visible' }, 'visibile'),
      el('option', { value: 'transparent' }, 'trasparente'),
      el('option', { value: 'hidden' }, 'nascosto'));
    sel.value = pane.structMode.get(sid);
    sel.addEventListener('change', () => {
      for (const p of state.panes) p.setStruct(sid, sel.value);
      requestRender();
    });
    struct.append(el('label', {}, el('span', {}, name), sel));
  }
  box.replaceChildren(
    el('div', { class: 'row' }, el('button', { onclick: all(true) }, 'Mostra tutto'), el('button', { onclick: all(false) }, 'Nascondi tutto')),
    list,
    el('h4', {}, 'Struttura'),
    struct,
    el('div', { class: 'small muted' }, 'Le parti trasparenti non intercettano la selezione: si raggiungono gli elementi interni.'),
  );
}

function kv(k, v) {
  return el('div', { class: 'kv' }, el('span', { class: 'k' }, k), el('span', { class: 'v' }, v));
}

function renderSelection(id, paneIndex = 0) {
  const box = $('#selection');
  const man = paneIndex === 1 && state.b ? state.b.manifest : state.a?.manifest;
  if (!id || !man) {
    box.replaceChildren(el('div', { class: 'muted' }, 'Tocca o clicca un componente per vederne i dati.'));
    return;
  }
  const e = man.entities.find((x) => x.id === id);
  const layer = man.layers.find((l) => l.id === e.layer);
  const flagged = e.state === 'placeholder' || ['assumed', 'unknown'].includes(e.data_status);
  const rows = [
    el('div', { class: 'sel-title' }, e.tag ? `${e.tag} — ` : '', e.name),
    flagged ? el('div', { class: 'warn small' }, 'Contiene dati assunti, sconosciuti o segnaposto: posizione e dimensioni sono provvisorie, da rilevare.') : null,
    kv('ID', el('code', {}, e.id)),
    kv('Layer', layer?.label ?? e.layer),
    kv('Tipo', e.type),
    kv('Stato', badge(STATE_TEXT[e.state] ?? e.state, `state-${e.state}`)),
    kv('Dati geometrici', statusBadge(e.data_status)),
    e.placement !== 'interior' ? kv('Posizione', `${e.placement}${e.placement_reason ? ` — ${e.placement_reason}` : ''}`) : null,
    kv('Centro', fmtVec(e.center ?? e.bbox_center)),
    kv('Dimensioni', fmtSizeCm(e.size ?? e.bbox_size)),
    kv('Ingombro min', fmtVec(e.bbox_min)),
    kv('Ingombro max', fmtVec(e.bbox_max)),
  ];
  if (e.orientation?.axis) {
    rows.push(kv('Orientamento', `${e.orientation.meaning}: [${e.orientation.axis.map((v) => v.toFixed(3)).join(', ')}]`));
  }
  if (e.fan) {
    rows.push(kv('Ventola', `telaio ${fmtCm(e.fan.frame_size)}, spessore ${fmtCm(e.fan.depth)}, girante ${fmtCm(e.fan.rotor_diameter)}`));
    rows.push(el('div', { class: 'small warn' }, 'Freccia = direzione NOMINALE del soffio, non simulata. PWM e giri non sono misure di portata.'));
  }
  if (e.pipe) {
    rows.push(kv('Lunghezza asse', `${fmtCm(e.pipe.length_m)} (${e.pipe.length_note})`));
    rows.push(kv('Diametri', `esterno ${fmtCm(e.pipe.outer_diameter)}${e.pipe.inner_diameter ? `, interno ${fmtCm(e.pipe.inner_diameter)}` : ''}`));
    rows.push(el('ul', { class: 'small' },
      ...e.pipe.straights.map((s) => el('li', {}, `${s.id}: tratto ${fmtCm(s.length_m)}`)),
      ...e.pipe.bends.map((b) => el('li', {}, `${b.id}: curva ${b.angle_deg.toFixed(1)}°, R ${fmtCm(b.radius_m)}, ${fmtCm(b.length_m)}`)),
    ));
    rows.push(el('div', { class: 'small muted' }, 'Coefficienti di perdita: non disponibili.'));
  }
  if (e.status_detail && Object.keys(e.status_detail).length) {
    const det = Object.entries(e.status_detail).filter(([, v]) => typeof v === 'string');
    rows.push(el('h4', {}, 'Provenienza per campo'), el('div', { class: 'small' }, ...det.map(([k, v]) => el('div', {}, `${k}: `, statusBadge(v)))));
  }
  if (e.properties && Object.keys(e.properties).length) {
    rows.push(el('h4', {}, 'Caratteristiche'));
    for (const [k, q] of Object.entries(e.properties)) {
      const val = q.value ?? (q.draw_value !== undefined && q.draw_value !== null ? `${q.draw_value} (provvisorio)` : '—');
      rows.push(el('div', { class: 'small' }, el('strong', {}, k), `: ${val} `, statusBadge(q.status), q.source ? el('span', { class: 'muted' }, ` [${q.source}]`) : null, q.note ? el('div', { class: 'muted indent' }, q.note) : null));
    }
  }
  if (e.notes?.length) rows.push(el('h4', {}, 'Note'), el('ul', { class: 'small' }, ...e.notes.map((n) => el('li', {}, n))));
  box.replaceChildren(...rows.filter(Boolean));
  openPanelSection('sec-selection');
  if (document.body.classList.contains('panel-open')) $('#sec-selection').scrollIntoView({ block: 'start' });
}

function renderDiff() {
  const box = $('#diff');
  const sec = $('#sec-diff');
  if (!state.diff) {
    sec.hidden = true;
    return;
  }
  sec.hidden = false;
  const a = state.a.entry;
  const b = state.b.entry;
  const head = el('div', { class: 'small' },
    el('div', {}, `A: ${a.layout_id} `, badge(KIND_TEXT[a.kind], `kind-${a.kind}`)),
    el('div', {}, `B: ${b.layout_id} `, badge(KIND_TEXT[b.kind], `kind-${b.kind}`)),
    el('div', { class: 'muted' }, 'Confronto per ID stabili e dati del manifest. Colori: verde aggiunto, rosso rimosso, blu spostato, arancio modificato.'));
  const list = el('div', { class: 'diff-list' });
  if (!state.diff.length) list.append(el('div', { class: 'muted' }, 'Nessuna differenza.'));
  for (const r of state.diff) {
    list.append(el('button', {
      class: `diff-row diff-${r.kind}`,
      onclick: () => {
        const inA = state.panes[0].byId.has(r.id);
        selectEntity(inA ? r.id : null, inA ? 0 : 1, inA ? null : r.id);
      },
    }, el('span', { class: 'diff-kind' }, DIFF_LABELS[r.kind]), ` ${r.id} — ${r.detail}`));
  }
  box.replaceChildren(head, list);
}

function renderMeasure() {
  const box = $('#measure');
  const pts = state.measure;
  const rows = [
    el('label', {}, Object.assign(el('input', { type: 'checkbox' }), {
      checked: state.snap,
      onchange: (ev) => { state.snap = ev.target.checked; },
    }), ' aggancia ai vertici (entro 3 cm)'),
    el('div', { class: 'small muted' }, state.mode === 'measure' ? 'Modalità misura attiva: tocca due punti del modello.' : 'Attiva «Misura» nella barra per misurare.'),
  ];
  pts.forEach((p, i) => rows.push(kv(`P${i + 1}${p.snapped ? ' (vertice)' : ''}`, fmtVec(p.point))));
  if (pts.length === 2) {
    rows.push(el('div', { class: 'measure-result' }, `Distanza rettilinea 3D: ${fmtCm(dist3(pts[0].point, pts[1].point))}`));
    rows.push(el('div', { class: 'small muted' }, 'È la distanza in linea retta fra due punti, in centimetri, nel frame canonico (Z verso l\'alto). Non è la lunghezza di un percorso di tubazione: quella è nel pannello del tubo.'));
  }
  box.replaceChildren(...rows);
}

function openPanelSection(id) {
  const d = document.getElementById(id);
  if (d && d.tagName === 'DETAILS') d.open = true;
}

// ------------------------------------------------------------ interazione

function selectEntity(id, paneIndex = 0, idB = null) {
  state.panes.forEach((p, i) => {
    const target = i === paneIndex ? id : null;
    // la stessa entità resta evidenziata anche nell'altro riquadro, se esiste
    const ent = target ?? (idB && i === 1 ? idB : (id && p.byId?.has(id) ? id : null));
    p.select(ent);
  });
  renderSelection(id ?? idB, id ? paneIndex : 1);
  requestRender();
}

function bindPointer(pane) {
  const dom = pane.renderer.domElement;
  let down = null;
  dom.addEventListener('pointerdown', (e) => {
    down = { x: e.clientX, y: e.clientY, t: performance.now() };
  });
  dom.addEventListener('pointerup', (e) => {
    if (!down) return;
    const moved = Math.hypot(e.clientX - down.x, e.clientY - down.y);
    const quick = performance.now() - down.t < 600;
    down = null;
    if (moved > 6 || !quick) return;
    const r = dom.getBoundingClientRect();
    const ndc = new THREE.Vector2(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1);
    const h = pane.hit(ndc, camera);
    const idx = state.panes.indexOf(pane);
    if (state.mode === 'measure') {
      if (!h) return;
      const p = pane.canonicalHit(h, state.snap ? 0.03 : 0);
      if (state.measure.length >= 2) state.measure = [];
      state.measure.push(p);
      for (const q of state.panes) q.clearMeasure();
      pane.drawMeasure(state.measure.map((m) => m.point));
      renderMeasure();
      openPanelSection('sec-measure');
      requestRender();
      return;
    }
    selectEntity(h ? h.id : null, idx);
  });
}

function setMode(mode) {
  state.mode = mode;
  $('#btn-measure').classList.toggle('active', mode === 'measure');
  if (mode !== 'measure') {
    state.measure = [];
    for (const p of state.panes) p.clearMeasure();
  }
  renderMeasure();
  requestRender();
}

function fillLayoutSelects() {
  const selA = $('#sel-a');
  const selB = $('#sel-b');
  const opts = (withNone) => [
    ...(withNone ? [el('option', { value: '' }, '— nessun confronto —')] : []),
    ...state.catalog.layouts.map((e) => el('option', { value: e.layout_id }, `${e.layout_id} · ${e.kind === 'hypothetical_demo' ? 'IPOTESI DIMOSTRATIVA' : 'reale pianificato'}`)),
  ];
  selA.replaceChildren(...opts(false));
  selB.replaceChildren(...opts(true));
}

async function main() {
  if (!webglAvailable()) {
    showError('WebGL 2 non è disponibile in questo browser o è disattivato: il modello 3D non può essere mostrato. Le immagini PNG della build restano consultabili.');
    return;
  }
  setupCamera();
  setLoading(true, 'Caricamento catalogo…');
  try {
    state.catalog = await loadCatalog(DATA);
  } catch (e) {
    setLoading(false);
    showError(e.message);
    return;
  }
  fillLayoutSelects();
  const params = new URLSearchParams(window.location.search);
  const a = params.get('layout') ?? state.catalog.default_layout ?? state.catalog.layouts[0].layout_id;
  const b = params.get('compare') ?? '';
  $('#sel-a').value = a;
  $('#sel-b').value = b;
  $('#sel-a').addEventListener('change', () => openLayouts($('#sel-a').value, $('#sel-b').value || null));
  $('#sel-b').addEventListener('change', () => openLayouts($('#sel-a').value, $('#sel-b').value || null));
  document.querySelectorAll('[data-view]').forEach((btn) => btn.addEventListener('click', () => setView(btn.dataset.view)));
  $('#btn-reset').addEventListener('click', () => setView('axon'));
  $('#btn-dims').addEventListener('click', () => {
    state.dims = !state.dims;
    $('#btn-dims').classList.toggle('active', state.dims);
    for (const p of state.panes) p.setDimensions(state.dims);
    requestRender();
  });
  $('#btn-measure').addEventListener('click', () => setMode(state.mode === 'measure' ? 'select' : 'measure'));
  $('#btn-panel').addEventListener('click', () => {
    const open = document.body.classList.toggle('panel-open');
    $('#btn-panel').classList.toggle('active', open);
    layoutPanes();
  });
  $('#error .close').addEventListener('click', () => { $('#error').hidden = true; });
  window.addEventListener('resize', layoutPanes);
  await openLayouts(a, b || null);
}

// Accesso in lettura per i test end-to-end (scripts/e2e.mjs): nessuna funzione di modifica.
window.__salamai = { state, getCamera: () => camera, getControls: () => controls };

main();
