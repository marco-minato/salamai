#!/usr/bin/env bash
# Ricostruisce tutto il modello 3D da zero, senza GUI e senza MCP:
# validazione -> scena Blender (.blend, .glb, manifest, PNG) -> pacchetto di
# analisi d'esempio -> test -> visualizzatore web (dist/).
#
# Uso: tools/room3d/build_all.sh            (dalla radice del repository o altrove)
# Variabili: BLENDER=percorso/blender  ENGINE=workbench|cycles
#            SKIP_TESTS=1  SKIP_WEB=1
set -euo pipefail
cd "$(dirname "$0")/../.."

BLENDER="${BLENDER:-blender}"
ENGINE="${ENGINE:-workbench}"
OUT="build/room3d"

echo "== validazione"
python3 tools/room3d/validate_config.py --config model/room3d/room.json

echo "== scena Blender ($("$BLENDER" --version | head -1))"
rm -rf "$OUT"
"$BLENDER" --background --factory-startup --python-exit-code 1 \
  --python tools/room3d/build_scene.py -- \
  --config model/room3d/room.json --output "$OUT" --engine "$ENGINE"

echo "== pacchetto di analisi d'esempio (dati SINTETICI)"
python3 tools/room3d/export_analysis.py \
  --cycle model/room3d/cycles/examples/SINTETICO_2026-01-10_0800 --build "$OUT"

if [ "${SKIP_TESTS:-0}" != 1 ]; then
  echo "== test"
  BLENDER="$BLENDER" python3 -m unittest discover -s tools/room3d/tests
fi

if [ "${SKIP_WEB:-0}" != 1 ]; then
  echo "== visualizzatore web"
  (cd web/room3d-viewer && npm ci --no-audit --no-fund && npm run build && npm run check)
fi
echo "== fatto: $OUT e web/room3d-viewer/dist"
