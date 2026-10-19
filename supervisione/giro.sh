#!/bin/sh
# Giro della supervisione salumi. Lo lancia crond ogni 5 min (avvia.sh).
#   giro.sh           chiede a strumenti.py se è ora di un controllo
#   giro.sh --prova   controllo subito, in sola osservazione (per il collaudo)
#
# Un controllo = una sessione `claude -p` con le istruzioni di prompt.md,
# solo gli strumenti di strumenti.py e scrittura solo in /share/salumi.

DIR=/homeassistant/salumi/supervisione
SHARE=/share/salumi
LOG=$SHARE/supervisione.log
mkdir -p "$SHARE" "$DIR/stato"

# Ambiente salvato da avvia.sh: crond parte senza variabili
[ -f "$DIR/stato/ambiente" ] && . "$DIR/stato/ambiente"

log() { echo "$(date '+%d/%m %H:%M') $*" >> "$LOG"; }

# Battito per HA (sensor.salumi_supervisione_battito): il runner è vivo
touch "$SHARE/battito"

# Un controllo alla volta
exec 9> "$DIR/stato/giro.lock"
flock -n 9 || exit 0

PROVA=0
[ "$1" = "--prova" ] && PROVA=1

if [ $PROVA = 1 ]; then
  MOTIVO="giro di prova manuale: SOLO OSSERVAZIONE, nessuna modifica, nessun avviso"
else
  T=$(python3 "$DIR/strumenti.py" turno 2>&1) || { log "errore turno: $T"; exit 1; }
  case "$T" in
    esegui*) MOTIVO=${T#esegui } ;;
    *) exit 0 ;;
  esac
fi

# Richiesta di HA: si consuma subito, così una nuova che arriva durante il
# controllo non va persa. Le richieste da HA usano Opus, i periodici Sonnet.
MODELLO=sonnet
case "$MOTIVO" in
  *richiesta*) rm -f "$SHARE/richiesta_analisi"; MODELLO=opus ;;
esac

log "inizio: $MOTIVO ($MODELLO)"
cd "$SHARE" || exit 1
PROMPT="$(cat "$DIR/prompt.md")

---
Ora: $(date '+%d/%m/%Y %H:%M'). Motivo di questo controllo: $MOTIVO"

# Ambiente pulito: niente variabili della sessione interattiva di Claude Code
env -i HOME=/root PATH="$PATH" LANG=C.UTF-8 SUPERVISOR_TOKEN="$SUPERVISOR_TOKEN" \
  timeout 1200 claude -p "$PROMPT" \
    --model "$MODELLO" \
    --permission-mode dontAsk \
    --strict-mcp-config \
    --no-session-persistence \
    --allowedTools \
      "Bash(python3 /homeassistant/salumi/supervisione/strumenti.py *)" \
      "Read(//share/salumi/**)" "Read(//media/salumi/**)" "Read(//homeassistant/salumi/**)" \
      "Write(//share/salumi/**)" "Edit(//share/salumi/**)" \
  >> "$LOG" 2>&1
ESITO=$?

if [ $PROVA = 0 ]; then
  python3 "$DIR/strumenti.py" fine_turno "uscita $ESITO" >> "$LOG" 2>&1
fi
log "fine: uscita $ESITO"

# Log: ultime 5000 righe
tail -n 5000 "$LOG" > "$LOG.tmp" && mv "$LOG.tmp" "$LOG"
