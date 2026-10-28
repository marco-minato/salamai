// Un riquadro 3D: scena, modello GLB, layer, selezione, quote e misure.
// Tutto lo stato è locale alla consultazione: nulla viene scritto altrove.
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { CSS2DObject, CSS2DRenderer } from 'three/addons/renderers/CSS2DRenderer.js';
import { FrameTransform, fmtCm } from './transform.js';

const DIFF_COLORS = { added: 0x18a058, removed: 0xd03050, moved: 0x2080f0, modified: 0xf0a020 };
const STRUCT_IDS = ['floor', 'ceiling', 'wall_y0', 'wall_y1', 'wall_x0', 'wall_x1'];

function label(text, cls) {
  const div = document.createElement('div');
  div.className = cls;
  div.textContent = text;
  return new CSS2DObject(div);
}

export class ModelPane {
  constructor(container, title) {
    this.container = container;
    this.renderer = new THREE.WebGLRenderer({ antialias: true });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.setClearColor(0xf4f4f2);
    container.appendChild(this.renderer.domElement);
    this.css = new CSS2DRenderer();
    this.css.domElement.className = 'css-layer';
    container.appendChild(this.css.domElement);
    if (title) {
      const t = document.createElement('div');
      t.className = 'pane-title';
      container.appendChild(t);
      this.titleEl = t;
    }
    this.scene = new THREE.Scene();
    this.scene.add(new THREE.HemisphereLight(0xffffff, 0x8899aa, 2.2));
    const sun = new THREE.DirectionalLight(0xffffff, 1.6);
    sun.position.set(3, 6, 4);
    this.scene.add(sun);
    this.root = new THREE.Group();
    this.dimGroup = new THREE.Group();
    this.measureGroup = new THREE.Group();
    this.scene.add(this.root, this.dimGroup, this.measureGroup);
    this.objects = new Map(); // id -> Object3D
    this.layerVisible = new Map();
    // all'apertura soffitto e parete porta sono trasparenti: si vede l'interno
    this.structMode = new Map(STRUCT_IDS.map((id) => [id, ['ceiling', 'wall_y0'].includes(id) ? 'transparent' : 'visible']));
    this.selected = null;
    this.selBox = null;
    this.raycaster = new THREE.Raycaster();
  }

  setTitle(text, demo) {
    if (!this.titleEl) return;
    this.titleEl.textContent = text;
    this.titleEl.classList.toggle('demo', !!demo);
  }

  resize() {
    const w = this.container.clientWidth;
    const h = this.container.clientHeight;
    this.renderer.setSize(w, h, false);
    this.renderer.domElement.style.width = `${w}px`;
    this.renderer.domElement.style.height = `${h}px`;
    this.css.setSize(w, h);
    return w / Math.max(h, 1);
  }

  render(camera) {
    this.renderer.render(this.scene, camera);
    this.css.render(this.scene, camera);
  }

  async load(manifest, glb) {
    this.clear();
    this.manifest = manifest;
    this.tf = new FrameTransform(manifest);
    const gltf = await new Promise((resolve, reject) =>
      new GLTFLoader().parse(glb, '', resolve, (e) => reject(new Error(`GLB non valido: ${e.message ?? e}`))),
    );
    const sceneBuild = gltf.scene.userData?.salamai_build_id;
    if (sceneBuild !== manifest.build.build_id) {
      throw new Error(`GLB e manifest di build diverse (${sceneBuild} ≠ ${manifest.build.build_id})`);
    }
    this.byId = new Map(manifest.entities.map((e) => [e.id, e]));
    gltf.scene.traverse((o) => {
      const id = o.userData?.salamai_id;
      if (!id) return;
      if (!this.byId.has(id)) throw new Error(`Oggetto ${id} del GLB assente nel manifest`);
      this.objects.set(id, o);
      o.traverse((m) => {
        if (!m.isMesh) return;
        m.material = m.material.clone();
        m.material.side = THREE.DoubleSide;
        m.userData.baseOpacity = m.material.opacity;
        m.userData.baseTransparent = m.material.transparent;
        m.userData.baseEmissive = m.material.emissive?.getHex?.() ?? 0;
      });
    });
    for (const e of manifest.entities) {
      if (!this.objects.has(e.id)) throw new Error(`Oggetto ${e.id} del manifest assente nel GLB`);
    }
    this.root.add(gltf.scene);
    for (const l of manifest.layers) this.layerVisible.set(l.id, true);
    this.buildDimensions();
    this.applyVisibility();
  }

  clear() {
    this.root.clear();
    this.dimGroup.clear();
    this.clearMeasure();
    this.objects.clear();
    this.selected = null;
    if (this.selBox) this.scene.remove(this.selBox);
    this.selBox = null;
    // le etichette CSS2D rimosse dalla scena vanno tolte anche dal DOM
    this.css.domElement.replaceChildren();
  }

  // ---------------------------------------------------------------- layer

  entityVisible(id) {
    const e = this.byId.get(id);
    if (!this.layerVisible.get(e.layer)) return false;
    if (STRUCT_IDS.includes(id) && this.structMode.get(id) === 'hidden') return false;
    return true;
  }

  applyVisibility() {
    for (const [id, o] of this.objects) {
      o.visible = this.entityVisible(id);
      if (STRUCT_IDS.includes(id)) {
        const transparent = this.structMode.get(id) === 'transparent';
        o.traverse((m) => {
          if (!m.isMesh) return;
          m.material.transparent = transparent || m.userData.baseTransparent;
          m.material.opacity = transparent ? 0.18 : m.userData.baseOpacity;
          m.material.depthWrite = !transparent;
          m.material.needsUpdate = true;
        });
      }
    }
    if (this.selected && !this.entityVisible(this.selected)) this.select(null);
  }

  setLayer(layer, on) {
    this.layerVisible.set(layer, on);
    this.applyVisibility();
  }

  setStruct(id, mode) {
    this.structMode.set(id, mode);
    this.applyVisibility();
  }

  // ---------------------------------------------------------------- selezione

  /** Oggetti colpibili: visibili e non trasparenti, così si raggiungono gli interni. */
  pickables() {
    const out = [];
    for (const [id, o] of this.objects) {
      if (!this.entityVisible(id)) continue;
      if (STRUCT_IDS.includes(id) && this.structMode.get(id) === 'transparent') continue;
      out.push(o);
    }
    return out;
  }

  hit(ndc, camera) {
    this.raycaster.setFromCamera(ndc, camera);
    const hits = this.raycaster.intersectObjects(this.pickables(), true);
    // le zone segnaposto sono volumi traslucidi che contengono altri oggetti:
    // si selezionano solo se lungo il raggio non c'è nulla di solido
    // (un componente dentro la zona vince; la zona vince su pavimento e pareti dietro)
    let zoneHit = null;
    for (const h of hits) {
      let o = h.object;
      while (o && !o.userData?.salamai_id) o = o.parent;
      if (!o) continue;
      const r = { id: o.userData.salamai_id, point: h.point, object: h.object, face: h.face };
      const type = this.byId.get(r.id).type;
      if (type === 'product_zone') {
        zoneHit ??= r;
        continue;
      }
      if (type === 'structure' && zoneHit) return zoneHit;
      return r;
    }
    return zoneHit;
  }

  select(id) {
    if (this.selBox) {
      this.scene.remove(this.selBox);
      this.selBox.geometry.dispose();
      this.selBox = null;
    }
    this.selected = id;
    if (!id || !this.objects.has(id)) return;
    this.selBox = new THREE.BoxHelper(this.objects.get(id), 0xffcc00);
    this.selBox.material.depthTest = false;
    this.selBox.renderOrder = 10;
    this.scene.add(this.selBox);
  }

  tintDiff(rows) {
    for (const [, o] of this.objects) {
      o.traverse((m) => m.isMesh && m.material.emissive?.setHex(m.userData.baseEmissive));
    }
    for (const r of rows ?? []) {
      for (const [id, o] of this.objects) {
        if (this.byId.get(id).entity_id !== r.id) continue;
        o.traverse((m) => {
          if (m.isMesh && m.material.emissive) {
            m.material.emissive.setHex(DIFF_COLORS[r.kind]);
            m.material.emissiveIntensity = 0.55;
          }
        });
      }
    }
  }

  // ---------------------------------------------------------------- quote

  buildDimensions() {
    const mat = new THREE.LineBasicMaterial({ color: 0x222222, depthTest: false });
    const matA = new THREE.LineBasicMaterial({ color: 0xd06000, depthTest: false });
    for (const d of this.manifest.dimensions) {
      const o = d.offset ?? [0, 0, 0];
      const a = [d.p1[0] + o[0], d.p1[1] + o[1], d.p1[2] + o[2]];
      const b = [d.p2[0] + o[0], d.p2[1] + o[1], d.p2[2] + o[2]];
      const pts = [d.p1, a, a, b, b, d.p2].map((c) => this.tf.toGltf(c));
      const geo = new THREE.BufferGeometry().setFromPoints(pts);
      const assumed = !['measured', 'declared', 'derived'].includes(d.status);
      const seg = new THREE.LineSegments(geo, assumed ? matA : mat);
      seg.renderOrder = 5;
      this.dimGroup.add(seg);
      const l = label(d.label, assumed ? 'dim-label assumed' : 'dim-label');
      l.position.copy(this.tf.toGltf([(a[0] + b[0]) / 2, (a[1] + b[1]) / 2, (a[2] + b[2]) / 2]));
      this.dimGroup.add(l);
    }
    this.dimGroup.visible = false;
  }

  setDimensions(on) {
    this.dimGroup.visible = on;
    this.dimGroup.traverse((o) => {
      if (o.isCSS2DObject) o.element.style.display = on ? '' : 'none';
    });
  }

  // ---------------------------------------------------------------- misure

  clearMeasure() {
    this.measureGroup.traverse((o) => o.isCSS2DObject && o.element.remove());
    this.measureGroup.clear();
  }

  drawMeasure(points) {
    this.clearMeasure();
    const dotGeo = new THREE.SphereGeometry(0.012, 12, 8);
    const dotMat = new THREE.MeshBasicMaterial({ color: 0xff2266, depthTest: false });
    for (const p of points) {
      const s = new THREE.Mesh(dotGeo, dotMat);
      s.position.copy(this.tf.toGltf(p));
      s.renderOrder = 20;
      this.measureGroup.add(s);
    }
    if (points.length === 2) {
      const geo = new THREE.BufferGeometry().setFromPoints(points.map((p) => this.tf.toGltf(p)));
      const line = new THREE.Line(geo, new THREE.LineBasicMaterial({ color: 0xff2266, depthTest: false }));
      line.renderOrder = 20;
      this.measureGroup.add(line);
      const d = Math.hypot(points[1][0] - points[0][0], points[1][1] - points[0][1], points[1][2] - points[0][2]);
      const l = label(`${fmtCm(d)} (rettilinea 3D)`, 'measure-label');
      l.position.copy(this.tf.toGltf(points[0]).add(this.tf.toGltf(points[1])).multiplyScalar(0.5));
      this.measureGroup.add(l);
    }
  }

  /** Punto colpito in coordinate canoniche, con aggancio al vertice più vicino entro snapM. */
  canonicalHit(hit, snapM) {
    let p = hit.point.clone();
    if (snapM > 0 && hit.object.geometry) {
      const pos = hit.object.geometry.attributes.position;
      const v = new THREE.Vector3();
      let best = null;
      let bestD = snapM;
      // tutti i vertici della mesh: il triangolo colpito può non contenere lo spigolo più vicino
      for (let idx = 0; idx < pos.count; idx++) {
        v.fromBufferAttribute(pos, idx).applyMatrix4(hit.object.matrixWorld);
        const d = v.distanceTo(hit.point);
        if (d <= bestD) {
          bestD = d;
          best = v.clone();
        }
      }
      if (best) p = best;
    }
    return { point: this.tf.toCanonical(p), snapped: !p.equals(hit.point) };
  }

  /** Box del modello in coordinate glTF, per inquadrare. */
  bounds() {
    return new THREE.Box3().setFromObject(this.root);
  }
}
