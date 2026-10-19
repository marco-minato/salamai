# Prompt per Claude Code — Schema elettrico "Camera salumi" in QElectroTech

> Copia tutto questo file come primo messaggio a Claude Code, sul PC dove è
> installato QElectroTech (https://qelectrotech.org/download.php).

---

## Il tuo compito

Devi produrre un **progetto QElectroTech (`.qet`)** con lo schema elettrico completo
dell'impianto descritto sotto: una camera di asciugatura/stagionatura salumi
controllata da una scheda ESP32-S3 con 6 relè (ESPHome), integrata in Home Assistant.

Lingua di etichette, titoli e note: **italiano**. Simboli: **IEC** (quelli della
collezione standard di QElectroTech). Sigle dei componenti secondo IEC 81346
(`-Q`, `-K`, `-T`, `-A`, `-X`, `-E`, `-M`, `-B`, `-S`…).

### Come lavorare (importante)

Il formato `.qet` è XML, ma i dettagli cambiano tra versioni: **non scriverlo a memoria**.

1. **Trova l'installazione** di QElectroTech e la sua versione
   (`qelectrotech --version`, oppure cartella di installazione). Individua la
   **collezione elementi** (file `.elmt`, di solito in `elements/10_electric/...`).
2. **Impara il formato reale.** Cerca file `.qet` di esempio nell'installazione.
   Se non ce ne sono, chiedimi di creare dalla GUI un progetto minimo
   (2 elementi collegati da un conduttore, un secondo folio, un cartiglio)
   e di salvarlo: lo analizzi e usi esattamente quella struttura
   (`<project>`, `<diagram>`, `<elements>`, `<terminals>`, `<conductors>`,
   `<collection>` con gli elementi incorporati, uuid, coordinate, orientamento).
3. **Genera il progetto con uno script Python**, non a mano: definisci
   componenti, morsetti e collegamenti come dati (netlist sotto) e fai
   produrre l'XML allo script. Posiziona tutto su griglia (multipli di 10 px),
   flusso da sinistra a destra / dall'alto in basso, senza sovrapposizioni.
4. **Usa elementi reali della collezione** (relè, contatti NA/NC, lampade,
   prese, motori, alimentatore, morsetti, termostato, pulsante…). Per i
   componenti che non esistono (scheda Waveshare, Eastron SDM120, Pico-RTC-DS3231, HX711, sonda RS485,
   modulo MOSFET, convertitore DC-DC) **crea elementi personalizzati** semplici
   (rettangolo + morsetti con nome) e incorporali nel progetto.
5. **Verifica**: apri il file in QElectroTech (`qelectrotech file.qet`),
   controlla che i conduttori siano agganciati ai morsetti e che non ci siano
   errori di caricamento. Se qualcosa non torna, correggi lo script e rigenera.
   Puoi chiedermi screenshot.
6. Se dopo alcuni tentativi la generazione XML si rivela impraticabile,
   fermati e proponimi un piano B (es. elementi personalizzati generati e
   collegamenti da tracciare a mano seguendo una tabella che mi prepari).

### Folii richiesti

| # | Folio | Contenuto |
|---|---|---|
| 1 | Copertina e legenda | titolo, descrizione, elenco folii, legenda sigle e colori dei fili |
| 2 | Alimentazione 230 V | arrivo linea, contatore Eastron SDM120 Modbus (inserzione diretta), distribuzione L/N/PE |
| 3 | Stufa (3 lampade IR) | contattori KM1–KM3 → cavo W1 5G1,5 → presa/spina CEE 5 poli in camera → cavo stufa → interruttori interni → lampade → antiribaltamento → N |
| 4 | Prese di servizio | KM4–KM5 → cavo W2 → scatola IP66 con 2 prese in camera (umidificatori); KM6 → presa estrattore **fuori** dalla camera, accanto al quadro |
| 5 | Bassa tensione 12 V | alimentatore 12 V, scheda Waveshare, relè K1–K6 → bobine 12 V dei contattori KM1–KM6 (con diodi), 2 ventole PWM 12 V a 4 fili con modulo MOSFET A2 sul segnale PWM e lettura giri; basetta a morsetti X5 collegata al connettore Pico con cavetti Dupont |
| 6 | Bus RS485 e sensori | sonda S-TH-01, contatore SDM120 (lato RS485), terminazione 120 Ω; HX711 + cella di carico; sonde DS18B20 di parete e di pavimento; seconda sonda S-TH-01 in cantina; RTC Pico-RTC-DS3231 innestato sul connettore Pico |
| 7 | Fronte/disposizione quadro | vista del quadro 48 moduli su 4 file con ingombri (vedi "Disposizione") |
| 8 | Distinta componenti | tabella nomenclatura (QElectroTech la genera dagli elementi, se la versione lo consente) |
| 9 | Planimetria e percorso cavi | pianta della camera (vedi "Planimetria") con posizione di quadro, botola, dispositivi, scatole e tracciato dei cavi W1–W5 |

Cartiglio: progetto "Camera salumi — controllo ESP32", revisione A, data di oggi,
autore da compilare.

---

## Descrizione dell'impianto

Una piccola stanza in cantina ("camera") viene usata per asciugare e stagionare
salumi con un ciclo di ~15 giorni a temperatura e umidità decrescenti
(da 20 °C / 72 % UR fino a 12 °C / 80 % UR). La camera è una vecchia botte da
vino in cemento (1900), pareti e pavimento in piastrelle vetrificate, 303 × 160 cm,
alta 210 cm (~10 m³). Si usa da metà dicembre a metà febbraio, con la cantina a
6–8 °C. Il quadro di comando sta **fuori dalla camera**, a muro a destra della
porta; in camera ci sono stufa, umidificatori, ventole, sonde e bilancia. Tutti
i cavi entrano in camera **dalla botola del soffitto** (32 × 45 cm, accessibile
da sopra), insieme al tubo dell'estrattore.

**Logica (nel firmware ESPHome della scheda, non va disegnata ma serve a capire lo schema):**
- **Nessun carico a 230 V passa dai relè della scheda.** I relè K1–K6 della
  scheda comandano solo le bobine a 12 V DC di 6 contattori modulari KM1–KM6
  (uno per carico); i 230 V passano dai contatti dei contattori. Motivo: lo
  spunto a freddo delle lampade IR (~13,7 Ω a freddo → ~17 A efficaci, ~24 A
  di picco per lampada) e la separazione netta tra bassa tensione e rete.
- La stufa ha **3 lampade IR da ~400 W** comandate **una per una** (KM1–KM3):
  più la temperatura è lontana dal target, più lampade si accendono; vicino
  al target ne resta una o nessuna. La lampada "di base" ruota per uniformare l'usura.
- **Due umidificatori a ultrasuoni** (KM4, KM5) per ridondanza. Quando
  umidificano, almeno una lampada è accesa (il calore aiuta a disperdere la
  nebbia) e le **ventole** girano piano. Ventole **in alto** sulla parete destra, soffiano orizzontali sopra i salami
  verso la parete opposta (ricircolo lento: l'aria non deve mai muovere i salami; PWM con tetto massimo).
  Umidificatori rialzati da terra, nebbia portata in alto con **tubi in PVC** che escono accanto alle ventole,
  sopra la zona della stufa (dove non ci sono salami).
- **Estrattore** (KM6) sul lato opposto alle ventole per il ricambio d'aria:
  ventole + estrattore creano un flusso trasversale. Il ricambio si fa quando
  l'umidità assoluta della cantina è inferiore a quella della camera, e a
  intervalli brevi per rinnovare l'aria.
- **Ventole** a velocità variabile via PWM (modulo MOSFET).
- Il ricambio d'aria non parte mentre un umidificatore è acceso.
- **Fase 0 – preriscaldo**: 24 h prima dell'inizio, stufa sola a camera vuota
  per scaldare il cemento (riduce la condensa iniziale).
- **Sonda di parete** (DS18B20 su una piastrella): l'umidificatore non parte se
  la parete è sotto il punto di rugiada dell'aria (+ margine), per non fare
  condensa e pozze sul pavimento.
- Temperatura/umidità della **cantina** da una seconda sonda RS485 (B5) letta
  dall'ESP32 (per decidere i ricambi); riserva uno Shelly via Home Assistant,
  se mancano entrambi ricambi brevi a tempo.
- **Sonda di pavimento** (B4, DS18B20 sullo stesso bus della B3): conta la
  superficie più fredda tra parete e pavimento.
- **Bilancia** (HX711 + cella di carico) per seguire il calo peso reale.
- **Contatore Eastron SDM120 Modbus** (guida DIN) misura i consumi degli
  attuatori e permette di rilevare lampada bruciata / relè incollato.
- Sicurezze: relè tutti aperti all'avvio; stop se la sonda non risponde;
  **antiribaltamento** della stufa sempre in serie. Nessun termostato
  meccanico (scelta voluta): un contattore incollato lascia accesa al massimo una
  lampada da 400 W; il firmware lo rileva (SDM120: potenza con relè aperto, o
  temperatura che sale/non scende a lampade spente) e manda un allarme.

---

## Distinta componenti

| Sigla | Componente | Note |
|---|---|---|
| -A1 | **Waveshare ESP32-S3-Relay-6CH** (Amazon B0CXPG4XGZ) | 6 relè 10 A 250 VAC, RS485 isolato con direzione automatica, alimentazione 7–36 V DC, custodia ABS per guida DIN (non a profilo modulare), 88 mm in larghezza × 122 mm in altezza (dato Waveshare; ~5 moduli di larghezza; profondità da misurare). Relè: CH1=GPIO1, CH2=GPIO2, CH3=GPIO41, CH4=GPIO42, CH5=GPIO45, CH6=GPIO46. RS485 interno su GPIO17/18. Buzzer GPIO21, LED RGB GPIO38. Uscite relè su morsetti a 3 poli COM/NA/NC. RS485 **isolato galvanicamente**, morsettiera a 3 poli A / B / Earth. Due connettori a 20 pin H1/H2 (piedinatura sotto, dallo schema elettrico ufficiale Waveshare) |
| -T1 | **Mean Well HDR-60-12** (B072DXXRW3) | 230 VAC → 12 V DC 4,5 A, guida DIN 3 moduli (dimensionato per scheda + 6 bobine + ventole) |
| -KM1…-KM6 | **Contattore modulare HCH8s-25Z**, bobina **12 V DC**, 25 A, 2 NA (B0BKWQ2P32) | ~1 modulo ciascuno (da verificare). Usato un solo contatto NA (1→2), il secondo (3→4) resta libero. KM1–KM3 lampade 1–3, KM4 umidificatore 1, KM5 umidificatore 2, KM6 estrattore. Bobina A1/A2, contatto di potenza 1→2 |
| -V1…-V6 | **Diodo 1N4007** | uno per bobina, in antiparallelo (catodo/riga verso A1 = +12 V, anodo verso A2 = 0 V): smorza la sovratensione allo spegnimento della bobina |
| -A2 | **Modulo MOSFET dual** a morsetti (B0GL1NWZQH, PWM fino a 20 kHz, ingresso 3,3 V) | su clip DIN; usato come interruttore verso massa (collettore aperto) sul filo PWM delle ventole: protegge il GPIO dal pull-up interno della ventola (fino a 5 V). PWM a 20 kHz, invertito nel firmware. Nessuna saldatura |
| -X5 | **Basetta a morsetti Freenove Breakout Board per Raspberry Pi Pico** (B0BFB53Y2N) | fissata alla guida DIN con le clip per circuiti stampati; ha le prese femmina di un Pico e un morsetto a vite etichettato (GP0…GP28) per ogni pin, con LED di stato bufferizzati. Collegata alla scheda A1 con **cavetti Dupont maschio-maschio** dalle prese sopra l'RTC A5 alle prese della basetta, **stessa posizione di pin** (così le etichette GP restano valide, vedi tabella). I cavi W3/W4/W5 e le resistenze di pull-up si serrano nei suoi morsetti. Il morsetto VREF non si usa (ha un LED non bufferizzato) |
| -A3 | **Contatore Eastron SDM120 Modbus** (B08X8SD1FD) | monofase a inserzione diretta 45 A, **1 modulo DIN**, RS485 Modbus RTU: tensione, corrente, potenza, cos φ, energia. Esce a indirizzo 1 e 2400 baud: **da impostare a indirizzo 2 e 9600 baud** dai tasti frontali |
| -B1 | **Sonda Seeed S-TH-01** (101990881) | temperatura/umidità RS485 Modbus, indirizzo 1, 9600 baud, alimentazione **3,6–30 V DC** (dato Seeed), consumo 4 mA a 24 V: alimentata a 12 V dal Mean Well |
| -A4 | **Modulo HX711** | in scatolina IP65 dentro la camera, sulla parete della porta a metà della zona salami, vicino alla cella (agganciata alla struttura dei salami) |
| -B2 | **Cella di carico** | 4 fili E+, E−, A+, A− verso HX711 |
| -A5 | **Waveshare Pico-RTC-DS3231** (B0915KRWNZ) | si innesta sul connettore Pico della scheda (espansione prevista da Waveshare), I²C su GPIO4/GPIO5 con la configurazione di fabbrica; batteria tampone CR1220; impilabile: sopra ripete tutti i pin, dove si innestano i cavetti Dupont verso X5 |
| -E1 | **Stufa a 3 lampade IR**, 1200 W totali | interruttori interni S1 (rosso, luminoso), S2, S3; S4 rotazione **non usato**; antiribaltamento -S5 a pulsante sotto la base; motorino rotazione -M1 **scollegato** |
| -E1.1/2/3 | Lampade IR 1, 2, 3 | ~400 W ciascuna, 230 V |
| -M2, -M3 | **Umidificatori a ultrasuoni** 1 e 2 | a spina |
| -M4 | **Estrattore in linea Ø 100 mm Vents TT-100** (B01LZQA9U9), in alternativa Airope (B08QFYMFJL) | flusso misto, 145/187 m³/h, 21/33 W, 230 V, collegato alla velocità bassa, con spina Schuko aggiunta su XS3; montato nella botola, tubo flessibile Ø 100 fino all'angolo opposto alla porta |
| -Y2 | **Griglia d'ingresso Ø 100 con valvola antiritorno magnetica** (B0F52BLHQ4) | sulla porta della camera, in basso, si apre verso la camera: ingresso dell'aria della cantina durante il ricambio |
| -Y1 | **Valvola antiritorno a molla Ø 100 mm** neverest RKI (B08LNS7TCV) | subito dopo l'estrattore, lato cantina: chiude la botola quando l'estrattore è fermo |
| -M5, -M6 | **Ventole ARCTIC P12 Slim PWM PST** 120 mm (confezione da 3, B09RWTCXRR; una di scorta) | 12 V, 4 fili (GND, +12 V, TACH, PWM), 200–2100 giri/min, 15 mm di spessore; collegate in X4 con prolunghe 4 pin tagliate (B09SKYRB3V), così la ventola resta integra |
| -X1 | Scatola **IP66 con 2 prese Schuko** con coperchio, in camera sulla parete destra, fuori dal getto della nebbia | XS1 umidificatore 1, XS2 umidificatore 2 (si staccano senza attrezzi per pulire la membrana) |
| -XS3 | Presa Schuko IP44/IP55 **fuori dalla camera**, accanto al quadro | estrattore (la sua spina esce dalla botola) |
| -XS4 / -XP4 | **Presa e spina CEE 16 A 5 poli (3P+N+PE)**, IP44/IP67 | presa in camera vicino alla stufa (fine di W1), spina sul cavo della stufa: la stufa si stacca a fine stagione |
| -X4 | Scatolina IP65 di derivazione ventole | in alto sulla parete destra, tra le due ventole; da W5 si divide verso M5 e M6 (+12 V, 0 V e PWM in parallelo, TACH separati) |
| -B3 | **Sonda DS18B20** impermeabile (parete) | incollata/fissata a una piastrella, collegata nella scatolina dell'HX711; resistenza di pull-up 4,7 kΩ tra DATA e 3,3 V nel quadro |
| -B4 | **Sonda DS18B20** impermeabile (pavimento) | uguale a B3, fissata a una piastrella del pavimento vicino al muro; in parallelo a B3 sullo stesso bus 1-Wire (GPIO7) |
| -B5 | **Sonda Seeed S-TH-01** (101990881), seconda unità | in **cantina**, fuori dalla camera, vicino alla griglia d'ingresso dell'aria; RS485 in parallelo a B1, **indirizzo 3**; alimentata a 12 V dal Mean Well |
| -X2… | Morsetti Wago 221 / morsettiere | distribuzione N e PE, bassa tensione |
| -W1 | Cavo **FG16OR16 5G1,5** quadro → presa CEE stufa | L1, L2, L3, N, PE |
| -W2 | Cavo **FG16OR16 4G1,5** quadro → X1 prese umidificatori | L4 (KM4), L5 (KM5), N, PE |
| -W3 | Cavo **Cat6 FTP** quadro → sonda B1 | coppia 1: A / B; coppia 2: +12 V / 0 V; coppia 3: +12 V / 0 V (in parallelo); coppia 4 di riserva; schermo a PE solo lato quadro |
| -W4 | Cavo **Cat6 FTP** quadro → scatolina HX711 | coppia 1: DOUT / 0 V; coppia 2: SCK / 0 V; coppia 3: 3,3 V / 0 V; coppia 4: DATA DS18B20 / 0 V; schermo a PE solo lato quadro |
| -W5 | Cavo **Cat6 FTP** quadro → X4 ventole | coppia 1: +12 V / 0 V; coppia 2: +12 V / 0 V (in parallelo); coppia 3: PWM / 0 V; coppia 4: TACH M5 / TACH M6; schermo a PE solo lato quadro |
| — | Filo silicone 18 AWG (B07TT68455) | collegamenti interni alla stufa (zona calda) |
| — | Quadro IP65 **Intratec 48 moduli, 4 file da 12** (B08614GVLN, 645×305×144 mm, sportello trasparente), con ~15 moduli liberi per espansioni (modulo relè Modbus + contattori aggiuntivi), clip DIN per PCB (B0FCM3N3P9), pressacavi M20 (B0GYRDCC9Z), scatolina IP65 per HX711 (B0F8NW1YZ2) | meccanica |

Linea di alimentazione: arriva da una presa/linea della cantina **già protetta
dal differenziale e magnetotermico di casa** (disegnarlo come "da quadro
generale, protetto 16 A + Id 30 mA").


### Piedinatura connettori della scheda A1 (schema Waveshare ESP32-S3-Relay-6CH)

| Pin | H1 | H2 |
|---|---|---|
| 1 | 5V | TXD0 (GPIO43, log seriale) |
| 2 | VSYS | RXD0 (GPIO44, log seriale) |
| 3 | GND | GND |
| 4 | 3V3 | GPIO13 |
| 5 | 3V3 | GPIO14 |
| 6 | GPIO10 (libero; su X5 corrisponde a VREF, da non usare) | GPIO15 |
| 7 | GPIO9 (libero) | GPIO16 |
| 8 | GND | GND |
| 9 | GPIO8 (libero) | GPIO47 |
| 10 | GPIO7 → X5 → DS18B20 B3/B4 | GPIO48 |
| 11 | 3V3 | GPIO17 (RS485 TX, **occupato**) |
| 12 | GPIO6 → X5 → HX711 SCK | GPIO18 (RS485 RX, **occupato**) |
| 13 | GND | GND |
| 14 | GPIO5 → RTC SCL (A5) | GPIO35 (evitare: PSRAM) |
| 15 | GPIO4 → RTC SDA (A5) | GPIO36 (evitare: PSRAM) |
| 16 | GPIO40 → X5 → HX711 DOUT | GPIO37 (evitare: PSRAM) |
| 17 | GPIO39 → A2 → PWM ventole | GPIO38 (LED RGB, **occupato**) |
| 18 | GND | GND |
| 19 | GPIO3 (strapping, evitare) | GPIO11 → X5 → TACH ventola M6 |
| 20 | GPIO21 (buzzer, **occupato**) | GPIO12 → X5 → TACH ventola M5 |

**Corrispondenza sui morsetti della basetta X5** (etichetta Pico → GPIO della scheda → uso):

| Morsetto X5 | Pin Pico | GPIO A1 | Uso |
|---|---:|---|---|
| 3V3 | 36 | 3,3 V | alimentazione HX711, DS18B20, pull-up |
| GND | 38 e altri | 0 V | masse |
| GP20 / GP21 | 26 / 27 | GPIO4 / GPIO5 | RTC A5 (già sul connettore, nessun filo esterno) |
| GP22 | 29 | GPIO6 | HX711 SCK |
| GP26 | 31 | GPIO7 | DS18B20 B3/B4 (pull-up 4,7 kΩ verso 3V3) |
| GP18 | 24 | GPIO39 | PWM ventole → A2 |
| GP19 | 25 | GPIO40 | HX711 DOUT |
| GP15 | 20 | GPIO12 | TACH ventola M5 |
| GP14 | 19 | GPIO11 | TACH ventola M6 |

Cavetti Dupont maschio-maschio tra le prese sopra l'RTC e le prese della basetta solo per queste posizioni (più 3V3 e GND).

Liberi di riserva: GPIO8, 9, 10, 13–16, 47, 48. Il connettore H1/H2 della scheda è **femmina**: l'RTC A5 vi si innesta e i cavetti Dupont si innestano sopra l'RTC. Nessuna saldatura sulle schede.

---

## Netlist (collegamenti da disegnare)

### Folio 2 — 230 V
- Linea **L / N / PE** dal quadro di casa → morsetti di ingresso del quadro (-X0).
- **N** e **PE** distribuiti con morsetti a tutti gli utilizzatori.
- **L** → T1 (Mean Well) ingresso L; N → T1 ingresso N (la serie HDR è in classe II: **nessun morsetto PE**).
- Ordine sulla fase: morsetto di ingresso -X0 → **derivazione per T1**
  (alimentatore 12 V) → A3 **SDM120** (L ingresso → L uscita, in serie; N al
  suo morsetto N) → linea "L-carichi" verso il morsetto **1** (ingresso
  potenza) di KM1–KM6 (distribuzione con pettine o morsetti, sezione 1,5 mm²;
  sezione 2,5 mm² sul tratto comune fino alla distribuzione). Il contatore
  misura quindi **solo gli attuatori** (lampade, umidificatori, estrattore),
  non l'elettronica.
  Gli allarmi per singolo carico sono calcolati dal firmware (potenza attesa
  in base ai relè chiusi, variazione a ogni commutazione).
- **Nessun 230 V sui morsetti dei relè K1–K6 della scheda A1.**

### Folio 3 — Stufa
- W1 termina sulla **presa CEE XS4** in camera; la stufa ha il suo cavo con
  **spina CEE XP4** (stessi 5 conduttori). Disegnare la coppia presa/spina.
- KM1 morsetto 2 → W1 conduttore **L1** → ingresso **S1** (interruttore rosso) → **lampada 1**.
- KM2 morsetto 2 → W1 conduttore **L2** → ingresso **S2** → **lampada 2**.
- KM3 morsetto 2 → W1 conduttore **L3** → ingresso **S3** → **lampada 3**.
- **Cavallotto originale tra S1–S2–S3–S4 rimosso**: le tre lampade sono indipendenti.
  S1, S2, S3 restano su "acceso" (servono solo come esclusione manuale).
- S4 (rotazione) e motorino M1: **non alimentati** (disegnarli tratteggiati / "non collegato").
- Ritorni delle 3 lampade uniti (filo blu interno) → **S5 antiribaltamento** → W1 **N**.
  (Verificato con il tester: in origine l'antiribaltamento era **sulla fase**,
  prima dell'interruttore S1. Viene **spostato sul neutro comune** delle
  lampade: annotarlo nello schema come modifica rispetto all'originale.)
- W1 **PE** → carcassa della stufa (giallo-verde interno).
- Annotazione: giunzione W1 ↔ fili interni nella parte bassa della stufa; da lì
  agli interruttori filo silicone 18 AWG in guaina di vetro.

### Folio 4 — Prese
- KM4 morsetto 2 → W2 **L4** → X1 / XS1 L (umidificatore 1, M2).
- KM5 morsetto 2 → W2 **L5** → X1 / XS2 L (umidificatore 2, M3).
- W2 N e PE → XS1 e XS2.
- KM6 morsetto 2 → XS3 L (estrattore M4, presa fuori dalla camera accanto al quadro); N e PE dai morsetti del quadro.
- Nota: K5 e K6 della scheda sono su GPIO di strapping (45/46): possibile breve
  scatto all'accensione, per questo comandano KM5/KM6 (carichi non critici).

### Folio 5 — Bassa tensione
- T1 **+12 V / 0 V** → A1 morsetti alimentazione (7–36 V).
- T1 +12 V / 0 V → W3 (coppie 2 e 3) verso sonda B1 (alimentazione).
- T1 **+12 V** → **COM di K1** → ponticello → COM K2 → … → COM K6 (un solo
  gruppo, tutto a 12 V; filo rosso 0,75–1 mm², puntalini doppi).
- K*n* NA → bobina **A1** di KM*n* (n = 1…6); bobina **A2** di KM1–KM6 → 0 V comune (morsetto **−V** di T1, distribuito con morsettiera/Wago; +V e −V di T1 indicati come +12 V e 0 V in tutto lo schema).
- Diodo V*n* in parallelo a ogni bobina KM*n*: catodo su A1, anodo su A2.
  Montato fisicamente **sui morsetti A1/A2 del contattore** (disegnarlo
  accanto alla bobina, non sulla scheda). Nota nello schema: "da confermare —
  omettere se la bobina ha soppressione interna (verifica col tester)".
- Morsetti NC di K1–K6: non collegati.
- T1 **+12 V / 0 V** → W5 (coppie 1 e 2) → X4 → +12 V e GND di M5 e M6 in parallelo.
- PWM: A1 **GPIO39** (H1 pin 17) → Dupont → X5 → ingresso segnale di A2; uscita di A2 (lato massa, OUT−) → X5 → W5 coppia 3 → X4 → PWM di M5 e M6 in parallelo (il pull-up è interno alle ventole). A2 alimentato a 12 V da T1.
- TACH M5 → W5 coppia 4 → X5 → Dupont → A1 **GPIO12** (H2 pin 20); TACH M6 → W5 coppia 4 → X5 → Dupont → A1 **GPIO11** (H2 pin 19). Pull-up interni dell'ESP32; se servono, resistenze 10 kΩ serrate su X5 tra TACH e 3,3 V.
- Masse 0 V di T1, A1 e A2 in comune.

### Folio 6 — RS485 e sensori
- A1 RS485 **A** → B1 A e A3 (SDM120) A (in parallelo); A1 **B** → B1 B e A3 B.
- Terminazione 120 Ω: ponticello H3 sulla scheda A1 abilitato (nota).
- Morsetto **Earth** dell'RS485 di A1 → PE (scarica le protezioni; il lato RS485 è isolato).
- A1 RS485 A/B → anche B5 (sonda cantina) A/B, in parallelo, con un breve
  tratto di cavo dal quadro.
- Indirizzi Modbus: B1 = 1, A3 = 2, B5 = 3.
- B2 cella → A4 HX711: E+, E−, A+, A−.
- A4 VCC ← A1 **3,3 V** (H1 pin 4); A4 GND ← A1 GND (H1 pin 8); A4 DOUT → A1 **GPIO40** (H1 pin 16);
  A4 SCK ← A1 **GPIO6** (H1 pin 12) (via cavo W4, coppie come in distinta, e basetta X5 + cavetti Dupont nel quadro).
- B3 DS18B20 parete: DATA → W4 coppia 4 → A1 **GPIO7** (H1 pin 10); VDD 3,3 V e GND presi
  nella scatolina dell'HX711; **pull-up 4,7 kΩ** tra DATA e 3,3 V, serrata su X5 lato quadro.
- B4 DS18B20 pavimento: in parallelo a B3 (stessi DATA, VDD, GND) nella
  scatolina dell'HX711; un solo pull-up per il bus.
- A5 Pico-RTC-DS3231 innestato sul connettore H1/H2: SDA = **GPIO4** (H1 pin 15), SCL = **GPIO5** (H1 pin 14), alimentato dal connettore. Nessun filo.

---

## Disposizione nel quadro (folio 7)

Quadro IP65, 48 moduli su 4 file da 12 (1 modulo = 17,5 mm):

| Fila | Da sinistra a destra |
|---|---|
| 1 — 230 V | morsetti ingresso -X0 (~2 mod) · T1 Mean Well HDR-60 (3 mod) · A3 contatore SDM120 (1 mod) · ~6 mod liberi |
| 2 — contattori | KM1 · KM2 · KM3 · KM4 · KM5 · KM6 (~6 mod) · morsetti uscita L1/L2/L3 stufa e prese (~3 mod) · ~3 mod liberi |
| 3 — scheda | A1 Waveshare (~5 mod di larghezza, alta 122 mm, faccia piatta: niente mostrina su questo tratto, si vede sotto lo sportello trasparente) · morsetti +12 V / 0 V (Wago) e RS485 (~3 mod) · ~4 mod liberi |
| 4 — bassa tensione / riserva | A2 modulo MOSFET su clip DIN (~4 mod) · X5 basetta a morsetti Freenove su clip DIN (~5 mod) · **~3 mod liberi per espansione** (modulo relè Modbus RTU sul bus RS485, contattori aggiuntivi) |

Pressacavi separati per i cavi a 230 V (W1, W2, XS3) e per quelli a bassa
tensione (W3, W4, W5). Fuori dal quadro: A4 HX711 (in scatolina IP65) **dentro
la camera**; X1 prese umidificatori e XS4 presa stufa **dentro la camera**;
XS3 presa estrattore accanto al quadro.

---

## Planimetria e percorso cavi (folio 9)

Pianta della camera, misure in cm (lato lungo 303 = 104 muro + 65 porta + 134
muro; lato corto 160; altezza 210). Disegnarla semplice (rettangoli, testo, frecce).

- **Porta** sul lato lungo "in basso", apre verso l'interno. **Quadro** fuori, a
  muro **a destra della porta**.
- **Salami**: metà destra della camera (~130 × 150), appesi a una struttura.
- **Parete corta destra**: in alto le due ventole M5 e M6, che soffiano
  orizzontali sopra i salami verso la parete opposta, con accanto le uscite dei
  tubi PVC della nebbia; più in basso gli umidificatori M2 e M3 rialzati da terra;
  al centro la stufa E1, puntata contro il muro (presa CEE XS4 accanto). Sopra la
  stufa niente salami. Scatola prese X1 accanto agli umidificatori, scatolina
  ventole X4 in alto tra le ventole, entrambe fuori dal getto di nebbia.
- **Botola** sul soffitto, 32 × 45, vicino alla porta: estrattore M4 + valvola Y1;
  tubo flessibile Ø 100 fino all'**angolo opposto alla porta** (dietro i salami).
- **Bilancia**: cella B2 + HX711 A4 sulla parete della porta, a metà della zona
  salami; sonda di parete B3 su una piastrella vicina, **in basso** (la condensa si forma su pareti e pavimento, non sul soffitto);
  sonda di pavimento B4 sotto, fissata a una piastrella del pavimento a pochi
  cm dal muro (posizione definitiva dopo il test di preriscaldo: dove il
  termometro a infrarossi trova la superficie più fredda).
- **Sonda di cantina B5** (fuori dalla camera): vicino alla porta, all'altezza
  della griglia d'ingresso dell'aria, lontana dallo scarico dell'estrattore
  (botola) e dal quadro (che scalda).
- **Sonda B1**: al centro della zona salami, a ~1,2 m da terra, ad almeno 1 m
  dalla parete destra e lontana dalla bocca del tubo.
- **Percorso**: dal quadro i cavi salgono sul muro esterno, passano **sopra il
  tetto della botte** ed entrano dalla botola attraverso un pannello con
  pressacavi (lo stesso che porta l'estrattore). Due tubi corrugati separati:
  uno per 230 V (W1, W2), uno per bassa tensione (W3, W4, W5). Dentro la camera
  cavi fissati a soffitto e parete con clip; pressacavi delle scatole rivolti
  verso il basso con ansa di gocciolamento.

---

## Consegna

- Il file `camera_salumi.qet` apribile in QElectroTech.
- Lo script Python che lo genera (così posso rigenerarlo con modifiche).
- Un breve riepilogo di cosa hai disegnato, cosa hai semplificato e cosa resta
  da completare a mano.
