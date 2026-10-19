#!/bin/sh
# Ferma la supervisione: toglie la riga di giro.sh dal cron. Un controllo già
# in corso finisce da solo (massimo 20 min).

DIR=/homeassistant/salumi/supervisione
crontab -l 2>/dev/null | grep -v "$DIR/giro.sh" | crontab -
echo "Supervisione fermata. Righe di cron rimaste:"
crontab -l 2>/dev/null || true
