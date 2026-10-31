#!/bin/sh
# Rigenera lo schema del quadro: drawio, schema.json, pagina HTML e anteprima PNG.
# Uso (dalla radice del repo): sh documentazione/sorgenti/quadro/build.sh
set -e
cd "$(dirname "$0")"
python3 export.py
cp q6.drawio ../../quadro-disposizione.drawio
python3 - <<'P'
t=open('page_tpl.html').read().replace('__DATA__',open('schema.json').read())
pre='<!doctype html><html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><style>*{box-sizing:border-box}body{margin:0}[hidden]{display:none!important}</style></head><body>'
open('../../schema-quadro.html','w').write(pre+t+'\n</body></html>\n')
P
python3 render.py q6.drawio anteprima.png 0.45 0 0 1400 2000
rm -f q6.drawio
echo "OK: quadro-disposizione.drawio, schema-quadro.html, anteprima.png"
