# Camera salumi — regole per la supervisione di Claude Code

Versione 2 del 18/10/2026. Le istruzioni operative che Claude riceve a ogni
controllo automatico sono in `supervisione/prompt.md` e derivano da qui.

**Autonomia piena da subito**, entro i limiti sotto.

## Ruoli

- **ESP32**: controllo in tempo reale (programma del ciclo, attuatori,
  sicurezze). Funziona da solo anche senza Home Assistant o Claude.
- **Home Assistant**: dashboard, archivio, allarmi Pushover, interfaccia tra
  Claude e l'ESP32.
- **Claude Code**: analisi periodica, correzione dei parametri entro i limiti,
  diario del ciclo, avvisi all'utente quando serve una decisione.

Claude agisce solo sui **parametri** esposti dal firmware (entità di HA salvate
nella memoria dell'ESP32). Non modifica il firmware durante un ciclo senza l'ok
esplicito dell'utente.

## Cosa può cambiare Claude

| Parametro | Regola |
|---|---|
| **Temperature** | **Mai.** Si seguono quelle del programma |
| **Correzione dell'UR target** rispetto al programma | Fino a ±5 punti: in autonomia, annotata solo nel diario. Oltre ±5 e fino a ±10: applica e **avvisa** l'utente. Oltre ±10: **chiede il permesso** prima di applicare |
| Strumenti per ottenere l'UR: minuti di estrattore, lavoro/pausa e PWM delle ventole (entro il tetto), margine sul punto di rugiada per l'umidificatore | In autonomia, entro i limiti scritti nel firmware |

**Condensa**: la correzione negativa dell'UR **non** si usa per compensare
una parete fredda. Se il margine di condensa (T parete − rugiada) non regge
con l'UR nel target, Claude avvisa l'utente del conflitto invece di
abbassare l'UR del prodotto.

**Si guarda la misura, non il setpoint**: a ogni controllo Claude confronta
UR misurata e target, con minimi, massimi e durata degli scostamenti.

Dopo una correzione, aspettare almeno qualche ora prima di correggere di nuovo
lo stesso parametro: l'effetto sull'UR e sul calo peso arriva lentamente, e
correzioni troppo ravvicinate fanno oscillare la camera.

## Frequenza dei controlli

| Periodo | Ogni quanto |
|---|---|
| Preriscaldo, sgocciolamento, giorni 1–3 | ogni ora |
| Giorni 4–15 | ogni 2 ore |
| Anomalia segnalata da HA (file di richiesta) | subito (entro 5 min) |

Dopo una correzione dell'umidità, almeno 2 ore prima di ritoccare lo stesso
parametro. Nei controlli intermedi: osservare e annotare.

## Esecuzione automatica

- **Cron**: `crond` dell'add-on Claude Code esegue ogni 5 min
  `supervisione/giro.sh`. Il giro chiede a `strumenti.py turno` se è ora di
  un controllo (ritmi della tabella sopra, o file di richiesta di HA); in quel
  caso lancia `claude -p` con tempo massimo di 20 min, solo gli strumenti di
  `strumenti.py` e scrittura solo in `/share/salumi/`. Un solo controllo alla
  volta (lock).
- **Modelli**: Sonnet per i controlli periodici, Opus quando la richiesta
  arriva da HA (anomalia o risposta a una proposta).
- **Battito**: a ogni giro scrive `/share/salumi/battito`. HA (sensore sull'età
  del file) manda un Pushover se il ciclo è attivo e il battito è più vecchio
  di 3 h ("supervisione ferma").
- **Avvio**: `supervisione/avvia.sh` (installa la riga di cron e avvia
  `crond`); `supervisione/ferma.sh` la toglie. **Dopo un riavvio dell'add-on**
  il cron non riparte da solo (l'add-on non ha comandi di avvio
  personalizzabili): HA avvisa con "supervisione ferma" e si rilancia
  `avvia.sh` dal terminale dell'add-on. L'ESP32 nel frattempo continua da solo.
- **Modalità** (`input_select.salumi_supervisione`): *osservazione* (Claude
  analizza, scrive il diario e avvisa, ma `strumenti.py imposta` rifiuta ogni
  modifica), *attiva* (modifiche entro i limiti), *sospesa* (nessun controllo).
- **Permessi**: lettura di dati e foto, scrittura solo in `/share/salumi/` e
  `/media/salumi/`, chiamate a HA solo per i parametri dei salumi e per gli
  avvisi.

## Quando avvisare l'utente

- **Decisioni**: correzione dell'UR oltre ±5 punti (avviso) od oltre ±10
  (richiesta di permesso); correzioni ripetute che non funzionano; muffa
  anomala nelle foto (spessa, grigia, verde); calo peso fuori dalla fascia;
  modifiche al programma o al firmware.
- **Allarmi** (già gestiti da HA/ESP32): sonda ferma, contattore incollato,
  lampada bruciata, temperatura fuori controllo, umidificatori senza acqua.
- **Niente riassunto via Pushover**: il riassunto quotidiano va solo nel diario.

## Foto

- Due al giorno dello stesso salame, con il flash, sempre dalla stessa
  posizione.
- L'utente le carica dall'app di HA in Media → Media locali → cartella `salumi`.
- Claude le rinomina con data e ora, le confronta con le precedenti e le
  collega alla voce del diario.

## Diario

In `/share/salumi/<ciclo>/`, accanto a quello che già scrive HA:
- cosa è stato osservato (dati e foto);
- cosa è stato cambiato, di quanto e perché;
- esito delle correzioni precedenti.
