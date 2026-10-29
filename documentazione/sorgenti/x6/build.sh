#!/bin/sh
# Rigenera schema X6: drawio, json, pagina HTML e anteprima PNG.
# Uso (dalla radice del repo): sh documentazione/sorgenti/x6/build.sh
set -e
cd "$(dirname "$0")"
python3 gen_x6.py ../../scatola-x6.drawio x6.json
python3 - <<'P'
t=open('page_x6_tpl.html').read().replace('__DATA__',open('x6.json').read())
pre='<!doctype html><html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><style>*{box-sizing:border-box}body{margin:0}[hidden]{display:none!important}</style></head><body>'
open('../../scatola-x6.html','w').write(pre+t+'</body></html>')
P
python3 render.py ../../scatola-x6.drawio anteprima.png 0.8 40 60 1220 760
echo "OK: scatola-x6.drawio, scatola-x6.html, anteprima.png"
