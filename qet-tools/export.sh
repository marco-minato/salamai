#!/usr/bin/env bash
# Export every folio of a QElectroTech project through the program's own export dialog
# (clean output: no grid, no terminals). Usage: export.sh project.qet out_dir [png|svg]
# Drives the Italian 0.9 GUI at fixed coordinates on a 1920x1200 virtual display.
set -euo pipefail
src=$(realpath "$1"); outdir=$(realpath -m "$2"); fmt=${3:-png}
work=$(mktemp -d); trap 'rm -rf "$work"' EXIT
mkdir -p "$outdir" "$work/p"
cp "$src" "$work/p/$(basename "$src")"
export XDG_DATA_HOME="$work/data" work fmt
export proj="$work/p/$(basename "$src")"
xvfb-run -a -s "-screen 0 1920x1200x24" bash -c '
  export QT_QPA_PLATFORM=xcb
  qelectrotech --config-dir="$HOME/.config/qet-headless/" "$proj" >"$work/qet.log" 2>&1 &
  pid=$!; sleep 9
  win=$(xdotool search --onlyvisible --name "QElectroTech" | head -1)
  xdotool windowmove "$win" 0 0 windowsize "$win" 1920 1200; sleep 1
  xdotool mousemove 900 1130 click 1
  xdotool key --clearmodifiers ctrl+shift+x; sleep 3
  if [ "$fmt" = svg ]; then
    xdotool mousemove 683 634 click 1; sleep 1
    xdotool mousemove 664 713 click 1; sleep 1
  fi
  xdotool mousemove 1299 831 click 1; sleep 10
  kill "$pid" 2>/dev/null || true
'
find "$work/p" -maxdepth 1 -type f ! -name '*.qet' -exec mv -t "$outdir" {} +
if [ "$fmt" = svg ]; then
  # Qt writes sizes in mm at 72 dpi with no viewBox and generic font names: make the files scale and
  # render the same in a browser.
  python3 -I - "$outdir" <<'PY'
import re, sys, pathlib
for f in pathlib.Path(sys.argv[1]).glob("*.svg"):
    s = f.read_text()
    m = re.search(r'<svg width="([\d.]+)mm" height="([\d.]+)mm"', s)
    if m and "viewBox" not in s[:400]:
        w, h = (round(float(v) * 72 / 25.4) for v in m.groups())
        s = s.replace(m.group(0), f'{m.group(0)} viewBox="0 0 {w} {h}"', 1)
    s = s.replace('font-family="Sans Serif"', 'font-family="Noto Sans"').replace('font-family="Sans"', 'font-family="Noto Sans"')
    f.write_text(s)
PY
fi
ls "$outdir"
