# Camera salumi — specifiche del firmware ESP32

Versione 2, 20/10/2026 (nodo in camera). Versione 1, 18/10/2026. Riferimenti: `prompt_schema_qelectrotech.md` (hardware
e collegamenti), `strategia_processo.md` (diagnosi e decisioni),
`regole_supervisione.md` (cosa può fare Claude Code).

## 1. Principi

1. **Autonomia.** L'ESP32 governa la camera da solo. Home Assistant e Claude
   Code servono a supervisione e regolazione, ma non sono indispensabili:
   senza di loro il ciclo continua con gli ultimi parametri.
2. **Parametri, non codice.** Tutto ciò che si regola durante un ciclo è
   un'entità `number`, `select` o `switch` esposta a HA, salvata in memoria
   flash (`restore_value: true`) e con limiti minimo e massimo scritti nel
   firmware. Durante un ciclo nessuna correzione richiede di ricompilare.
3. **Riavvio senza perdite.** Inizio ciclo, fase, peso iniziale e parametri
   stanno in flash. Dopo un riavvio i relè partono aperti, poi il ciclo
   riprende dal punto calcolato sull'ora corrente.
4. **Temperature fisse.** Seguono il programma e non hanno correzioni
   regolabili. Si regola solo l'umidità.
5. **Sicurezza prima del processo.** Senza letture valide della sonda, tutti
   gli attuatori vanno spenti.

## 2. Hardware e pin

| Funzione | Risorsa |
|---|---|
| Lampade IR 1, 2, 3 (contattori KM1–KM3) | relè CH1 GPIO1, CH2 GPIO2, CH3 GPIO41 |
| Umidificatore 1 (KM4) | CH4 GPIO42 |
| Umidificatore 2 (KM5) | CH5 GPIO45 |
| Estrattore (KM6) | CH6 GPIO46 |
| Ventole, bilancia, sonde di parete e pavimento | sul **nodo in camera** (§2 bis), letti e comandati via Modbus |
| RS485 Modbus RTU, 9600 8N1 | UART GPIO17/18, direzione automatica |
| — sonda S-TH-01 | indirizzo 1: T reg 0x0000 (×0,01), UR 0x0001 (×0,01), rugiada 0x0002 |
| — contatore Eastron SDM120 Modbus (`sdm_meter`) | indirizzo 2 e 9600 baud (da impostare: esce a 1 e 2400): tensione, corrente, potenza, cos φ, energia degli attuatori |
| — seconda sonda S-TH-01, **cantina** | indirizzo 3 (da impostare): T e UR dell'aria che entra col ricambio |
| — nodo in camera (XIAO ESP32C3, `salumi-nodo.yaml`) | indirizzo 4: registri in §2 bis |
| RTC Waveshare Pico-RTC-DS3231, innestato sul connettore Pico | SDA GPIO4, SCL GPIO5 |
| Buzzer, LED RGB | GPIO21, GPIO38 |

CH5 e CH6 sono su pin di strapping: all'accensione possono scattare per un
attimo. Il firmware deve forzarli spenti il prima possibile (`on_boot` con
priorità alta).

GPIO liberi sulla scheda: 6–16 (tranne 10 da evitare se si rimette la
basetta X5), 39, 40, 47, 48.

**Senza rete nessun riavvio**: `api` e `wifi` con `reboot_timeout: 0s`, su
entrambe le schede. Con il valore di fabbrica (15 min) una caduta di HA o del
Wi-Fi farebbe riavviare la scheda a metà ciclo.

## 2 bis. Nodo in camera

Una XIAO ESP32C3 con la sua scheda RS485 sta in una scatola stagna dentro la
camera (X6) e porta i sensori e le ventole vicini al prodotto. È un
dispositivo **comandato**: non decide nulla, la Waveshare lo legge e gli
scrive la velocità delle ventole. La sonda camera S-TH-01 è sullo stesso bus
ma la Waveshare la legge **direttamente**: se il nodo si ferma, temperatura,
umidità e sicurezze della stufa restano valide.

| Funzione | Pin XIAO |
|---|---|
| RS485 (scheda Seeed 113991354) | TX D4 (GPIO6), RX D5 (GPIO7), direzione D2 (GPIO4) |
| HX711 (cella 2 kg) | DOUT D1 (GPIO3), SCK D3 (GPIO5) |
| DS18B20 parete e pavimento, stesso bus 1-Wire | D10 (GPIO10), pull-up 4,7 kΩ verso 3V3 |
| PWM ventole, tramite modulo MOSFET A2 verso massa (uscita **invertita**), LEDC **1 kHz** (a 20 kHz il modulo è troppo lento: prova al banco del 30/10/2026) | D7 (GPIO20) |
| Giri ventola M5 / M6 / M7 (2 impulsi a giro), pull-up interne | D0 (GPIO2) / D8 (GPIO8) / D6 (GPIO21) |
| Libero | D9 (GPIO9, tasto BOOT) |

D0 e D8 sono pin di strapping, ma l'avvio lo decide D9: con D9 alto la XIAO
parte normalmente qualunque cosa ci sia su D0 e D8. D9 non si usa per i giri,
perché una ventola che gira lo porterebbe basso all'avvio (modalità download).

**Registri** (holding, lettura 0x03, scrittura 0x06/0x10):

| Registro | Contenuto | Tipo |
|---|---|---|
| 0x0000 | versione della mappa (1) | U_WORD |
| 0x0001 | battito, +1 al secondo | U_WORD |
| 0x0002–0x0003 | peso grezzo HX711 (INT32_MIN = non valido) | S_DWORD, parola alta prima |
| 0x0004 | T parete × 100 (−32768 = non valida) | S_WORD |
| 0x0005 | T pavimento × 100 (−32768 = non valida) | S_WORD |
| 0x0006 / 0x0007 | giri ventola M5 / M6 (giri/min) | U_WORD |
| 0x0008 | PWM ventole applicato (%) | U_WORD |
| 0x0009 | stato: bit 0 ventole in sicurezza, bit 1 HX711 valido, bit 2 parete valida, bit 3 pavimento valido | U_WORD |
| 0x000A | giri ventola M7 (giri/min) | U_WORD |
| 0x0010 | PWM ventole richiesto (%, 0–100), **lettura e scrittura** | U_WORD |

- **Lettura**: la Waveshare legge 0x0000–0x000A ogni 15 s.
- **Ventole**: la Waveshare riscrive 0x0010 ogni 30 s anche se non cambia.
  Senza scritture per 90 s il nodo porta le ventole a `pwm_sicurezza`
  (0 %, ferme) e alza il bit 0. Il tetto `ventole_pwm_max` lo applica la
  Waveshare, che conosce la fase: il nodo accetta 0–100.
- **Peso**: il nodo manda la lettura grezza, la conversione in grammi (tara e
  fattore, §7) la fa la Waveshare. Così la taratura non richiede di
  ricompilare il nodo.
- **Nodo fermo**: se il battito non cambia per 60 s la Waveshare alza
  "Nodo camera non risponde". Peso, superfici e giri diventano non validi;
  il ciclo continua (§9).
- **Wi-Fi del nodo**: solo aggiornamenti e diagnostica. I dati del processo
  passano tutti dal bus.

## 3. Ora e stato persistente

- **Fonti dell'ora**, in ordine: HA (`time: homeassistant`), poi SNTP, poi il
  DS3231 se montato.
- **Senza ora valida** il ciclo resta in **attesa sicura**: lampade sul
  target della fase salvata, nessun avanzamento di fase, allarme dopo 10 min.
- **In flash**: stato (spento / preriscaldo / ciclo / terminato), timestamp di
  inizio preriscaldo e di inizio ciclo, peso iniziale, lampada di base
  corrente, tutti i parametri.
- **Fase**: calcolata ogni minuto dall'ora corrente e dal timestamp di
  inizio, mai contata con un contatore (sopravvive a riavvii e cadute di rete).
- **Modalità test**: `ore_per_giorno` e `ore_sgocciolamento` regolabili, ma
  **non salvati**: a ogni avvio tornano a 24 h e 12 h.

## 4. Programma del ciclo

| Fase | Durata | T | UR programma | Umidificatore |
|---|---|---:|---:|---|
| Preriscaldo | `ore_preriscaldo` (default 24 h) | 22 °C | — | spento |
| Sgocciolamento | 12 h | 22 °C | 62 % | abilitato (in pratica spento) |
| Giorno 1 | 24 h | 20 °C | 72 % | abilitato |
| Giorno 2 | 24 h | 18 °C | 72 % | abilitato |
| Giorno 3 | 24 h | 18 °C | 74 % | abilitato |
| Giorno 4 | 24 h | 16 °C | 76 % | abilitato |
| Giorno 5 | 24 h | 16 °C | 78 % | abilitato |
| Giorni 6–7 | 24 h | 14 °C | 80 % | abilitato |
| Giorni 8–15 | 24 h | 12 °C | 80 % | abilitato |
| Terminato | — | — | — | tutto spento, allarme informativo |

- **Partenza del preriscaldo**: pulsante, oppure automatica alle ore
  `partenza_programmata − ore_preriscaldo`.
- **Partenza del ciclo**: pulsante "Partenza ciclo", da premere quando i
  salumi sono dentro. Copia il peso attuale in `peso_iniziale`.
- **Pulsanti** "Fase successiva" e "Ferma ciclo" (con conferma in dashboard).
- **Target effettivo**: `UR_target = UR_programma + correzione_ur`.

## 5. Temperatura (lampade)

Regolazione a gradini sull'errore `e = T_target − T`, con isteresi:

| Lampade accese | Condizione (salendo) | Condizione (scendendo) |
|---|---|---|
| 3 | e > 3,0 °C | e < 2,0 °C → 2 lampade |
| 2 | e > 1,5 °C | e < 0,8 °C → 1 lampada |
| 1 | e > 0,2 °C | e < −0,2 °C → 0 lampade |

- **Tempi minimi**: acceso 2 min, spento 2 min per ogni lampada (come
  `min_cycle_duration` attuale).
- **Accensioni sfalsate**: almeno 3 s tra una lampada e l'altra (spunto
  ~24 A di picco per lampada a freddo).
- **Rotazione**: la lampada "di base" (la prima ad accendersi) cambia ogni
  giorno, per uniformare l'usura.
- **Tetto**: T > T_target + 2 °C → tutte spente, anche se una regola chiede
  calore.
- **Limite assoluto**: T > 30 °C → tutte spente e allarme.

## 6. Umidità

### 6.1 Umidità assoluta

- **Camera**: da T e UR della sonda (formula di Magnus).
- **Cantina**: dalla seconda sonda S-TH-01 sul bus RS485, letta
  direttamente dall'ESP32 (stesso modello della sonda di camera: la
  differenza di umidità assoluta, che decide i ricambi, non risente delle
  differenze di taratura tra marche). L'aria della cantina cambia col tempo
  esterno (più secca col sole, più umida con la nebbia): per questo si misura
  in continuo e non si usa un valore fisso. Riserva: lo Shelly H&T via HA
  (valido se ha meno di 3 h); senza nessuno dei due, ricambi a tempo.
- **Rugiada**: punto di rugiada dell'aria della camera, confrontato con la
  superficie più fredda: `T_fredda` = min(`T_parete`, `T_pavimento`). Se una
  delle due sonde manca si usa l'altra, con allarme.
- **Margine di condensa** = `T_fredda` − rugiada della camera. È il numero
  che decide la condensa, non l'UR impostata: con UR misurata più alta del
  target la parete può condensare anche se il setpoint è basso.

### 6.2 Troppo umido → ricambio

Il ricambio parte solo se sono vere **tutte** queste condizioni:
- UR > UR_target + `isteresi_ur`;
- AH_camera − AH_cantina ≥ `delta_ah_min`;
- nessun umidificatore acceso;
- pausa dall'ultima raffica ≥ `pausa_min_estrattore`;
- minuti di estrattore nell'ultima ora < `max_min_ora_estrattore`.

Comportamento:
- **Raffica**: `durata_raffica` minuti, poi pausa. Si ripete finché la
  condizione resta vera.
- **Cantina non disponibile**: ricambi prudenti a tempo, solo se
  UR > UR_target + 5: una raffica ogni 60 min.
- **Ventole durante la raffica**: al PWM di lavoro, per non estrarre solo
  l'aria vicino alla bocca del tubo.
- **Portata effettiva**: a ogni raffica il firmware stima la portata reale
  dal calo dell'umidità assoluta, Q ≈ (V / t) · ln[(AH_inizio − AH_cantina) /
  (AH_fine − AH_cantina)], con V = 10,2 m³ e t la durata della raffica. È
  per difetto, perché i salami continuano a cedere acqua. Media mobile delle
  ultime 10 raffiche, esposta a HA.

### 6.2 bis Rischio condensa → ricambio anche con UR nel target

Se il margine di condensa è < `margine_condensa` (default 2 °C) il ricambio
parte anche quando l'UR non supera il target, con le stesse condizioni di
6.2 (ΔAH ≥ `delta_ah_min`, umidificatori spenti, pause, minuti massimi),
**ma non sotto** UR_target − `ur_sotto_target_max` (default 5 punti): non si
asciuga il prodotto senza limite per compensare una parete fredda.

**Conflitto di condensa** (allarme, e Claude avvisa l'utente): margine
< `margine_rugiada` per più di 60 min e almeno una di queste:
- l'UR è già a UR_target − `ur_sotto_target_max`;
- ΔAH < `delta_ah_min` (la cantina non asciuga più: è satura o troppo
  calda);
- le raffiche non fanno risalire il margine.

In conflitto il firmware non fa altro da solo: serve una decisione
(preriscaldo più lungo, cantina da ventilare, programma da rivedere).

### 6.3 Troppo secco → umidificatore

L'umidificatore parte solo se sono vere **tutte** queste condizioni:
- UR < UR_target − `isteresi_ur`;
- fase con umidificatore abilitato;
- estrattore spento;
- `T_fredda` ≥ rugiada + `margine_rugiada`. Se la parete è più fredda,
  l'umidificatore resta bloccato e il blocco viene registrato come evento
  ("umidificazione bloccata per condensa").

Comportamento:
- **Una lampada accesa**: almeno una lampada accesa da 30 s prima e fino a
  1 min dopo, salvo T > T_target + 1 °C.
- **Ventole**: al PWM di lavoro per tutta l'umidificazione e per 1 min dopo.
- **Alternanza**: usa l'umidificatore "preferito" (alternato ogni giorno),
  l'altro è la riserva.
- **Controllo di efficacia**: dopo `verifica_umid` minuti (default 10)
  l'UR deve essere salita di almeno 1 punto.
  - Se non sale e il contatore mostra la potenza "a vuoto" (serbatoio vuoto) →
    passa all'altro umidificatore e manda l'allarme "acqua finita".
  - Se non sale per altri motivi → allarme.
- **Tempi minimi**: acceso 1 min, spento 2 min.

### 6.4 Ricircolo (ventole)

- **Ciclo base**: `ventole_lavoro_min` di lavoro al `ventole_pwm`, poi
  `ventole_pausa_min` di pausa. Default 5 min di lavoro, 55 min di pausa,
  PWM al minimo utile.
- **Tetto**: `ventole_pwm_max` limita qualunque richiesta. L'aria non deve
  mai muovere i salami.
- **Giri**: le ventole vanno da 200 a 2100 giri/min; il tetto si tara in giri
  (test con l'incenso) e il firmware espone i giri reali. Sotto ~5 % di PWM le
  ventole si fermano: la pausa si fa a PWM 0.
- **Preriscaldo** (camera vuota): ventole **sempre accese** a
  `ventole_pwm_preriscaldo` (default 100 %), senza il tetto
  `ventole_pwm_max` perché non ci sono salami. Servono a scaldare prima pareti
  e pavimento e a non lasciare l'aria calda al soffitto.
- **Partenza ciclo**: le ventole tornano subito al ciclo base lavoro/pausa con
  il tetto. Da qui vale solo il ricircolo lento.

## 7. Peso

- **Lettura**: HX711 con mediana; peso registrato solo durante la pausa delle
  ventole, a ventole ferme da almeno 2 min.
- **Taratura**: `tara` e `fattore` come parametri, più il pulsante "Tara".
- **Calo**: `calo_% = (1 − peso / peso_iniziale) × 100`, confrontato con la
  curva attesa `2,9 × giorni^0,631` (fascia: minimo `1,94 × g^0,705`,
  massimo `4,56 × g^0,544`).
- **Caduta**: un calo di peso > 5 % in meno di 10 min è un'anomalia (salame
  staccato), non un calo. Allarme e calo congelato.

## 8. Consumi e diagnosi (contatore SDM120)

- **Potenze di riferimento** come parametri, misurate nei test a vuoto:
  lampada ~400 W, umidificatore in funzione / a vuoto, estrattore ~14 W.
- **A ogni manovra**: dopo 5 s la variazione di potenza deve stare entro
  ±30 % di quella attesa. Altrimenti allarme "lampada bruciata" o "carico che
  non si accende".
- **Tutti i carichi spenti**: potenza > 15 W per più di 30 s → allarme
  "contattore incollato".
- **Lampade spente**: T che sale di oltre 1 °C in 15 min → allarme
  "calore non comandato".

## 9. Sicurezze e allarmi

| Evento | Azione |
|---|---|
| Avvio dell'ESP32 | Relè tutti aperti, poi ripristino dello stato |
| Sonda senza risposta > 2 min | Lampade e umidificatori spenti, estrattore spento, allarme |
| T > 30 °C | Lampade spente, allarme |
| Ora non valida > 10 min | Attesa sicura, allarme |
| Umidificatore inefficace o senza acqua | Cambio sull'altro, allarme |
| Contattore incollato, lampada bruciata, calore non comandato | Allarme (l'antiribaltamento resta l'unica sicurezza meccanica, per scelta) |
| Conflitto di condensa (6.2 bis) | Ricambio fermo al limite di UR, allarme |
| Margine di condensa < 0 °C per > 30 min | Allarme (la parete sta condensando) |
| Ventola ferma (giri < 100 con PWM ≥ 20 % per > 1 min) | Allarme; l'umidificatore si blocca se sono ferme entrambe |
| Sonda di cantina senza risposta | Riserva Shelly via HA, poi ricambio a tempo, allarme |
| Sonda di parete o di pavimento senza risposta | Si usa l'altra, allarme |
| Nodo in camera fermo (battito fermo da 60 s) | Allarme. Il ciclo continua; senza superfici l'umidificatore resta bloccato (§6.3), il peso non si registra. Ventole: il nodo le porta a `pwm_sicurezza` da solo |
| HA non raggiungibile | Nessuna azione: il ciclo continua (la cantina è letta dall'ESP32) |

Ogni allarme è una `binary_sensor` di diagnostica, più un evento HA
`esphome.salumi_allarme` con codice e testo. HA lo inoltra via Pushover e lo
scrive nel diario.

## 10. Entità esposte a HA

**Sensori**:
- T, UR, rugiada, umidità assoluta della camera; T, UR, rugiada e umidità
  assoluta della cantina; T parete, T pavimento; margine di condensa;
- minuti al giorno con margine di condensa < `margine_rugiada` e < 0;
- minuti al giorno con UR fuori fascia (oltre ±`isteresi_ur` + 3 punti dal
  target), con minimo e massimo del giorno;
- portata effettiva stimata dell'estrattore (m³/h);
- peso, calo %, calo atteso;
- potenza ed energia;
- minuti di estrattore e di umidificatore (oggi e nel ciclo), stima
  dell'acqua estratta (g);
- fase e ore alla fine della fase;
- lampade accese, PWM e giri delle ventole;
- "ultima azione" (testo: cosa ha fatto il controllo e perché).

**Parametri regolabili (`number`, salvati in flash)**:

| Parametro | Default | Limiti firmware |
|---|---:|---:|
| `correzione_ur` (punti %) | 0 | −15 … +15 |
| `isteresi_ur` | 2 | 1 … 6 |
| `delta_ah_min` (g/m³) | 0,5 | 0,2 … 3 |
| `durata_raffica` (min) | 3 | 1 … 10 |
| `pausa_min_estrattore` (min) | 10 | 3 … 120 |
| `max_min_ora_estrattore` | 20 | 0 … 40 |
| `margine_rugiada` (°C) | 1,0 | 0 … 4 |
| `margine_condensa` (°C), soglia del ricambio anticondensa | 2,0 | 0,5 … 5 |
| `ur_sotto_target_max` (punti %) | 5 | 0 … 10 |
| `verifica_umid` (min) | 10 | 5 … 30 |
| `ventole_pwm` (%) | da tarare | 0 … `ventole_pwm_max` |
| `ventole_pwm_max` (%) | da tarare | 0 … 100 (solo l'utente) |
| `ventole_lavoro_min` | 5 | 0 … 30 |
| `ventole_pausa_min` | 55 | 5 … 240 |
| `ore_preriscaldo` | 24 | 0 … 72 |
| `ventole_pwm_preriscaldo` | 100 % | 0 … 100 % |
| `kg_camera` | 55 | 1 … 200 |
| Potenze di riferimento, taratura bilancia | dai test | — |

**Comandi**: avvia preriscaldo, partenza ciclo, fase successiva, ferma ciclo,
tara bilancia, test di ogni attuatore (solo a ciclo fermo).

**Input da HA**: partenza programmata, programma scelto (Morganline o
Zanotti), T e UR della cantina dallo Shelly solo come riserva.

## 11. Migrazione da HA

- Il controllo (`climate.salumi_stufa`, `humidifier.salumi_umidita`,
  `script.salumi_applica_setpoint`) passa all'ESP32.
- Il pacchetto `salumi.yaml` resta per dashboard, archivio (`salumi_log.py`),
  notifiche, calo atteso e stima dell'estrattore.
- Prima della stagione: test a camera vuota (vedi `strategia_processo.md`),
  poi un ciclo accelerato completo con la supervisione di Claude attiva.
