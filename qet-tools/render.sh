#!/usr/bin/env bash
# Render a QElectroTech project to PNG by opening it in the real GUI on a virtual display.
# Usage: render.sh project.qet out.png [wait_seconds]      (QET_SCREEN=WxH, default 1920x1200)
# Only the first folio is visible: use Project.save(path, first=N) to check another one.
set -euo pipefail
src=$(realpath "$1"); out=$(realpath -m "$2"); wait_s=${3:-8}
screen=${QET_SCREEN:-1920x1200}; W=${screen%x*}; H=${screen#*x}
work=$(mktemp -d); trap 'rm -rf "$work"' EXIT
cp "$src" "$work/project.qet"; chmod u+w "$work/project.qet"
cfg="${XDG_CONFIG_HOME:-$HOME/.config}/qet-headless/"; mkdir -p "$cfg"
# Private data dir: keeps QET's autosave/restore files away from the user's real session.
export XDG_DATA_HOME="$work/data"
export work out wait_s cfg W H
xvfb-run -a -s "-screen 0 ${W}x${H}x24" bash -c '
  export QT_QPA_PLATFORM=xcb
  qelectrotech --config-dir="$cfg" "$work/project.qet" >"$work/qet.log" 2>&1 &
  pid=$!
  sleep "$wait_s"
  win=$(xdotool search --onlyvisible --name "QElectroTech" | head -1)
  xdotool windowmove "$win" 0 0 windowsize "$win" "$W" "$H"
  sleep 1
  xdotool mousemove $((W * 47 / 100)) $((H - 70)) click 1
  xdotool key --clearmodifiers ctrl+9
  sleep 2
  import -window root "$out"
  kill "$pid" 2>/dev/null || true
  cp "$work/qet.log" "$out.log" 2>/dev/null || true
'
echo "$out"
