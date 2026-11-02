#!/bin/sh
# Rigenera schema X4: drawio, json, pagina HTML e anteprima PNG.
# Uso (dalla radice del repo): sh documentazione/sorgenti/x4/build.sh
set -e
cd "$(dirname "$0")"
python3 gen_x4.py ../../scatola-x4.drawio x4.json
python3 - <<'P'
t=open('page_x4_tpl.html').read().replace('__DATA__',open('x4.json').read())
pre='<!doctype html><html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><style>*{box-sizing:border-box}body{margin:0}[hidden]{display:none!important}</style></head><body>'
open('../../scatola-x4.html','w').write(pre+t+'</body></html>')
P
python3 render.py ../../scatola-x4.drawio anteprima.png 1 40 60 720 600
echo "OK: scatola-x4.drawio, scatola-x4.html, anteprima.png"
