#!/bin/sh
# Avvia la supervisione: salva l'ambiente per crond, installa la riga di cron
# (giro.sh ogni 5 min) e avvia crond. Da rilanciare dopo ogni riavvio
# dell'add-on Claude Code (HA avvisa con "supervisione ferma").

DIR=/homeassistant/salumi/supervisione
RIGA="*/5 * * * * $DIR/giro.sh >/dev/null 2>&1"

if [ ! -x /usr/local/bin/claude ]; then
  echo "Qui non c'è claude ($(hostname)): lanciare dalla pagina dell'add-on Claude Code, non dal Terminal & SSH." >&2
  exit 1
fi
if [ -z "$SUPERVISOR_TOKEN" ]; then
  echo "Manca SUPERVISOR_TOKEN: lanciare dalla pagina dell'add-on Claude Code con '!'." >&2
  exit 1
fi

mkdir -p "$DIR/stato" /share/salumi
umask 077
cat > "$DIR/stato/ambiente" <<EOF
SUPERVISOR_TOKEN='$SUPERVISOR_TOKEN'
PATH='$PATH'
export SUPERVISOR_TOKEN PATH
EOF
chmod +x "$DIR/giro.sh"

( crontab -l 2>/dev/null | grep -v "$DIR/giro.sh"; echo "$RIGA" ) | crontab -
pgrep -x crond >/dev/null || crond

echo "Supervisione avviata:"
crontab -l | grep "$DIR/giro.sh"
pgrep -x crond >/dev/null && echo "crond attivo" || echo "ATTENZIONE: crond non attivo"
