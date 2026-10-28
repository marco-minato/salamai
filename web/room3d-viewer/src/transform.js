// Unica trasformazione fra glTF (Y-up) e frame canonico (Z-up, metri).
// La matrice arriva dal manifest: oggetti, quote, misure e selezione
// passano tutti da qui.
import { Vector3 } from 'three';

const EXPECTED = [[1, 0, 0], [0, 0, -1], [0, 1, 0]];

export class FrameTransform {
  constructor(manifest) {
    const m = manifest?.gltf?.gltf_to_canonical;
    if (!Array.isArray(m) || m.length !== 3 || m.some((r) => !Array.isArray(r) || r.length !== 3)) {
      throw new Error('Manifest senza matrice gltf_to_canonical valida');
    }
    const det =
      m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1]) -
      m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0]) +
      m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]);
    if (Math.abs(det - 1) > 1e-9) throw new Error('Matrice gltf_to_canonical non è una rotazione propria');
    this.m = m;
    this.standard = JSON.stringify(m) === JSON.stringify(EXPECTED);
  }

  /** glTF (Vector3) -> canonico [x, y, z] */
  toCanonical(v) {
    const m = this.m;
    return [
      m[0][0] * v.x + m[0][1] * v.y + m[0][2] * v.z,
      m[1][0] * v.x + m[1][1] * v.y + m[1][2] * v.z,
      m[2][0] * v.x + m[2][1] * v.y + m[2][2] * v.z,
    ];
  }

  /** canonico [x, y, z] -> glTF Vector3 (inversa = trasposta) */
  toGltf(c) {
    const m = this.m;
    return new Vector3(
      m[0][0] * c[0] + m[1][0] * c[1] + m[2][0] * c[2],
      m[0][1] * c[0] + m[1][1] * c[1] + m[2][1] * c[2],
      m[0][2] * c[0] + m[1][2] * c[1] + m[2][2] * c[2],
    );
  }
}

const nf = (digits) => new Intl.NumberFormat('it-IT', { minimumFractionDigits: digits, maximumFractionDigits: digits });
const cm1 = nf(1);
const m3 = nf(3);

export const fmtCm = (meters) => `${cm1.format(meters * 100)} cm`;
export const fmtM = (meters) => `${m3.format(meters)} m`;
export const fmtVec = (c) => `X ${m3.format(c[0])} · Y ${m3.format(c[1])} · Z ${m3.format(c[2])} m`;
export const fmtSizeCm = (s) => s.map((v) => cm1.format(v * 100)).join(' × ') + ' cm';
export const dist3 = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);
