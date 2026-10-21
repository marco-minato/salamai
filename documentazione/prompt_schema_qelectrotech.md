# Prompt per Claude Code — Schema elettrico "Camera salumi" in QElectroTech

> Copia tutto questo file come primo messaggio a Claude Code, sul PC dove è
> installato QElectroTech (https://qelectrotech.org/download.php).

---

> **Revisione C (20/10/2026) — se hai già lo script `genera_camera_salumi.py`
> della revisione B, aggiornalo invece di ripartire da zero.** Cosa cambia:
> - nuovo **nodo in camera -A6** (XIAO ESP32C3 + scheda RS485) nella scatola
>   stagna **-X6**: porta HX711, DS18B20, PWM e giri delle ventole, e parla
>   con la Waveshare via Modbus (indirizzo 4);
> - verso la camera un solo cavo di bassa tensione, **W3** (12 V, 0 V, A, B);
>   **W4 eliminato**, **W5** diventa uno spezzone corto X6 → X4;
> - **eliminati dal quadro** la basetta X5, i cavetti Dupont e il modulo
>   MOSFET A2 (che va in X6); sulla Waveshare resta innestato solo l'RTC A5;
> - **quadro** nuovo: cassetta BOXEXPERT Fleet 500×400×240 con piastra di
>   fondo, guide DIN e canaline (folio 7 rifatto);
> - **umidificatori a spina fuori dalla camera**: il loro cavo, allungato, esce
>   dalla botola e si inserisce nelle prese XS1 e XS2 accanto al quadro (come
>   l'estrattore su XS3); **eliminati la scatola prese X1 e il cavo W2**;
> - nuovo **piano dei morsetti X0, X2, X3** con la numerazione (netlist).

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
   componenti che non esistono (scheda Waveshare, XIAO ESP32C3 con scheda RS485, Eastron SDM120, Pico-RTC-DS3231, HX711, sonda RS485,
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
| 4 | Prese di servizio | KM4, KM5, KM6 → prese XS1, XS2 (umidificatori) e XS3 (estrattore), tutte **fuori** dalla camera, accanto al quadro; i cavi degli apparecchi escono dalla botola |
| 5 | Bassa tensione 12 V | alimentatore 12 V, scheda Waveshare, relè K1–K6 → bobine 12 V dei contattori KM1–KM6 (con diodi); 12 V e 0 V verso la camera nel cavo W3 |
| 6 | Bus RS485 e nodo in camera | bus RS485 (Waveshare, SDM120, sonda cantina B5, cavo W3, sonda camera B1, nodo A6) con le due terminazioni 120 Ω; dentro la scatola X6: nodo A6, HX711 + cella di carico, sonde DS18B20 di parete e pavimento, modulo MOSFET A2 e ventole M5/M6 (via W5 e X4); RTC Pico-RTC-DS3231 innestato sul connettore Pico |
| 7 | Disposizione sulla piastra | vista della piastra di fondo del quadro con guide DIN, canaline e ingombri (vedi "Disposizione") |
| 8 | Distinta componenti | tabella nomenclatura (QElectroTech la genera dagli elementi, se la versione lo consente) |
| 9 | Planimetria e percorso cavi | pianta della camera (vedi "Planimetria") con posizione di quadro, botola, dispositivi, scatole e tracciato dei cavi W1, W3, W5, W6 e dei cavi di M2, M3, M4 |

Cartiglio: progetto "Camera salumi — controllo ESP32", revisione C, data di oggi,
autore da compilare.

---

## Descrizione dell'impianto

Una piccola stanza in cantina ("camera") viene usata per asciugare e stagionare
salumi con un ciclo di ~15 giorni a temperatura e umidità decrescenti
(da 20 °C / 72 % UR fino a 12 °C / 80 % UR). La camera è una vecchia botte da
vino in cemento (1900), pareti e pavimento in piastrelle vetrificate, 303 × 160 cm,
alta 210 cm (~10 m³). Si usa da metà dicembre a metà febbraio, con la cantina a
6–8 °C. Il quadro di comando sta **fuori dalla camera**, a muro a destra della
porta; in camera ci sono stufa, umidificatori, ventole, sonde, bilancia e una
scatola stagna con il nodo di bassa tensione (XIAO ESP32C3). Tutti
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
- **Ventole** a velocità variabile via PWM (modulo MOSFET), comandate dal nodo
  in camera su richiesta della Waveshare.
- **Nodo in camera** (XIAO ESP32C3): legge bilancia, sonde di parete e
  pavimento e giri delle ventole e comanda il PWM. Sul bus RS485 è un
  dispositivo comandato (indirizzo 4): non decide nulla. La sonda camera B1 è
  sullo stesso bus ma la Waveshare la legge direttamente, così stufa e
  sicurezze non dipendono dal nodo.
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
| -A2 | **Modulo MOSFET dual** a morsetti (B0GL1NWZQH, PWM fino a 20 kHz, ingresso 3,3 V) | **nella scatola X6 in camera**; usato come interruttore verso massa (collettore aperto) sul filo PWM delle ventole: protegge il GPIO della XIAO dal pull-up interno della ventola (fino a 5 V). PWM a 20 kHz, invertito nel firmware. Nessuna saldatura |
| -A6 | **Nodo in camera: Seeed XIAO ESP32C3** (102010633) **+ Seeed XIAO RS485 Breakout** (113991354) | nella scatola X6. La breakout ha il ricetrasmettitore RS485 (direzione su D2) e accetta 12 V con il suo step-down. Pin: RS485 TX D4 / RX D5 / DE D2; HX711 DOUT D1, SCK D3; DS18B20 D10; PWM ventole D7 → A2; TACH M5 D0, TACH M6 D8; liberi D6, D9. Modbus indirizzo 4, 9600 baud. È la XIAO della sonda attuale (sonda-th), riusata |
| -X6 | **Scatola stagna IP65** in policarbonato/ABS (~150×110×70 mm o più grande se serve) con **valvola anticondensa M12** in basso | dentro la camera, **in alto sulla parete della porta, sopra la bilancia** (zona più calda e asciutta, lontana dal getto della nebbia e dal fascio della stufa). Pressacavi tutti verso il basso con ansa di gocciolamento. Contiene A6, A4, A2, i Wago di giunzione e le resistenze R1–R4. Schede trattate con vernice protettiva (conformal coating), morsetti esclusi |
| -R1, -R2 | **Resistenze 120 Ω** | terminazioni del bus RS485 ai due estremi: R1 nel quadro (o il ponticello di terminazione della scheda A1), R2 in X6 tra A e B (oppure la terminazione della breakout, se presente). Solo due in tutto il bus |
| -R3 | **Resistenza 4,7 kΩ** | pull-up del bus 1-Wire, tra DATA (D10) e 3V3, in X6 |
| -R4, -R5 | **Resistenze 10 kΩ** | pull-up dei TACH M5 (D0) e M6 (D8) verso 3V3, in X6 |
| -A3 | **Contatore Eastron SDM120 Modbus** (B08X8SD1FD) | monofase a inserzione diretta 45 A, **1 modulo DIN**, RS485 Modbus RTU: tensione, corrente, potenza, cos φ, energia. Esce a indirizzo 1 e 2400 baud: **da impostare a indirizzo 2 e 9600 baud** dai tasti frontali |
| -B1 | **Sonda Seeed S-TH-01** (101990881) | temperatura/umidità RS485 Modbus, indirizzo 1, 9600 baud, alimentazione **3,6–30 V DC** (dato Seeed), consumo 4 mA a 24 V: alimentata a 12 V dal Mean Well tramite W3. Il suo cavo entra in X6 e si collega sui Wago di A, B, 12 V e 0 V; la sonda resta nell'aria della camera |
| -A4 | **Modulo HX711** | nella scatola X6, sopra la cella (agganciata alla struttura dei salami): cavo della cella corto |
| -B2 | **Cella di carico** | 4 fili E+, E−, A+, A− verso HX711 |
| -A5 | **Waveshare Pico-RTC-DS3231** (B0915KRWNZ) | si innesta sul connettore Pico della scheda (espansione prevista da Waveshare), I²C su GPIO4/GPIO5 con la configurazione di fabbrica; batteria tampone CR1220. È l'unica cosa collegata al connettore Pico |
| -E1 | **Stufa a 3 lampade IR**, 1200 W totali | interruttori interni S1 (rosso, luminoso), S2, S3; S4 rotazione **non usato**; antiribaltamento -S5 a pulsante sotto la base; motorino rotazione -M1 **scollegato** |
| -E1.1/2/3 | Lampade IR 1, 2, 3 | ~400 W ciascuna, 230 V |
| -M2, -M3 | **Umidificatori a ultrasuoni** 1 e 2 | a spina; cavo di alimentazione allungato (FROR 3G1,5, senza giunzioni dentro la camera) fino alle prese XS1 e XS2 fuori dalla camera |
| -M4 | **Estrattore in linea Ø 100 mm Vents TT-100** (B01LZQA9U9), in alternativa Airope (B08QFYMFJL) | flusso misto, 145/187 m³/h, 21/33 W, 230 V, collegato alla velocità bassa, con spina Schuko aggiunta su XS3; montato nella botola, tubo flessibile Ø 100 fino all'angolo opposto alla porta |
| -Y2 | **Griglia d'ingresso Ø 100 con valvola antiritorno magnetica** (B0F52BLHQ4) | sulla porta della camera, in basso, si apre verso la camera: ingresso dell'aria della cantina durante il ricambio |
| -Y1 | **Valvola antiritorno a molla Ø 100 mm** neverest RKI (B08LNS7TCV) | subito dopo l'estrattore, lato cantina: chiude la botola quando l'estrattore è fermo |
| -M5, -M6 | **Ventole ARCTIC P12 Slim PWM PST** 120 mm (confezione da 3, B09RWTCXRR; una di scorta) | 12 V, 4 fili (GND, +12 V, TACH, PWM), 200–2100 giri/min, 15 mm di spessore; collegate in X4 con prolunghe 4 pin tagliate (B09SKYRB3V), così la ventola resta integra |
| -XS1, -XS2 | Prese Schuko IP44/IP55 **fuori dalla camera**, accanto al quadro e a XS3 | umidificatore 1 (KM4) e umidificatore 2 (KM5); ognuna con L, N e PE propri dal quadro |
| -XS3 | Presa Schuko IP44/IP55 **fuori dalla camera**, accanto al quadro | estrattore (il suo cavo esce dalla botola) |
| -XS4 / -XP4 | **Presa e spina CEE 16 A 5 poli (3P+N+PE)**, IP44/IP67 | presa in camera vicino alla stufa (fine di W1), spina sul cavo della stufa: la stufa si stacca a fine stagione |
| -X4 | Scatolina IP65 di derivazione ventole, con **valvola anticondensa M12** in basso | in alto sulla parete destra, tra le due ventole; da W5 si divide verso M5 e M6 (+12 V, 0 V e PWM in parallelo, TACH separati) |
| -B3 | **Sonda DS18B20** impermeabile (parete) | incollata/fissata a una piastrella in basso, cavo da 3 m fino a X6 |
| -B4 | **Sonda DS18B20** impermeabile (pavimento) | uguale a B3, fissata a una piastrella del pavimento vicino al muro; in parallelo a B3 sullo stesso bus 1-Wire (A6 D10) |
| -B5 | **Sonda Seeed S-TH-01** (101990881), seconda unità | in **cantina**, fuori dalla camera, vicino alla griglia d'ingresso dell'aria; RS485 in parallelo, **indirizzo 3**, con lo spezzone W6 dal quadro (breve derivazione: a 9600 baud non dà problemi); alimentata a 12 V dal Mean Well |
| -X0, -X2, -X3 | Morsetti su guida **UK2.5B** (blu per N), morsetti di terra **USLKG2.5** giallo-verdi, ponticelli FBI e fermi | X0 ingresso linea L/N/PE; X2 uscite 230 V (L1–L6, N per ogni carico, PE per ogni carico); X3 bassa tensione (+12 V, 0 V, A, B, terre). Numerazione nel "Piano dei morsetti" |
| — | Morsetti **Wago 221** | giunzioni nella scatola X6 (12 V, 0 V, A, B, 3V3, 1-Wire) e nelle scatole in camera |
| -W1 | Cavo **FG16OR16 5G1,5** quadro → presa CEE stufa | L1, L2, L3, N, PE |
| -W2a, -W2b, -W7 | Spezzoni **FROR 3G1,5** quadro → prese accanto al quadro, ~1 m | W2a: L4 (KM4), N, PE → XS1 · W2b: L5 (KM5), N, PE → XS2 · W7: L6 (KM6), N, PE → XS3 |
| -W3 | Cavo **Cat6 FTP** (rame pieno, non CCA) quadro → scatola X6 in camera, ~10 m | coppia 1: A / B; coppia 2: +12 V / 0 V; coppia 3: +12 V / 0 V (in parallelo alla 2); coppia 4 di riserva; schermo a PE solo lato quadro. Carico ~0,3 A: caduta ~0,25 V |
| -W5 | Spezzone **Cat6 FTP** X6 → X4 ventole, ~2,5 m | coppia 1: +12 V / 0 V; coppia 2: +12 V / 0 V (in parallelo); coppia 3: PWM / 0 V; coppia 4: TACH M5 / TACH M6; schermo a 0 V solo lato X6 |
| -W6 | Spezzone **Cat6 FTP** quadro → sonda cantina B5, ~2 m | coppia 1: A / B; coppia 2: +12 V / 0 V; schermo a PE solo lato quadro |
| — | Filo silicone 18 AWG (B07TT68455) | collegamenti interni alla stufa (zona calda) |
| — | Quadro **BOXEXPERT Fleet 500×400×240 mm**, ABS, IP65, sportello trasparente, **piastra di fondo** in lamiera zincata (B0CBS922L8); 3 guide DIN 35 mm da ~45 cm avvitate alla piastra; **canaline asolate 25×40** sopra e sotto ogni guida e sui due lati; morsetti UK2.5B su guida con fermi; valvola anticondensa M12; pressacavi M20 (B0GYRDCC9Z) | meccanica |

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
| 6 | GPIO10 (libero) | GPIO15 |
| 7 | GPIO9 (libero) | GPIO16 |
| 8 | GND | GND |
| 9 | GPIO8 (libero) | GPIO47 |
| 10 | GPIO7 (libero) | GPIO48 |
| 11 | 3V3 | GPIO17 (RS485 TX, **occupato**) |
| 12 | GPIO6 (libero) | GPIO18 (RS485 RX, **occupato**) |
| 13 | GND | GND |
| 14 | GPIO5 → RTC SCL (A5) | GPIO35 (evitare: PSRAM) |
| 15 | GPIO4 → RTC SDA (A5) | GPIO36 (evitare: PSRAM) |
| 16 | GPIO40 (libero) | GPIO37 (evitare: PSRAM) |
| 17 | GPIO39 (libero) | GPIO38 (LED RGB, **occupato**) |
| 18 | GND | GND |
| 19 | GPIO3 (strapping, evitare) | GPIO11 (libero) |
| 20 | GPIO21 (buzzer, **occupato**) | GPIO12 (libero) |

Sul connettore Pico è innestato solo l'RTC A5 (GPIO4/GPIO5). Tutti gli altri
GPIO del connettore restano liberi per espansioni: 6–16, 39, 40, 47, 48.
Nessuna saldatura sulle schede.

---

## Netlist (collegamenti da disegnare)

### Piano dei morsetti X0, X2, X3
Un filo per morsetto; i morsetti dello stesso potenziale sono uniti con
ponticelli FBI. I morsetti di terra (USLKG, giallo-verdi) si serrano sulla
guida, che fa da barra di terra: la guida 3 e la guida 1 sono unite da un
filo giallo-verde, e un filo giallo-verde porta la terra alla piastra di fondo.
Disegnare le tre morsettiere con questi numeri:

| Morsettiera | Morsetto | Funzione | Lato interno | Lato campo |
|---|---|---|---|---|
| -X0 (guida 3) | 1, 2 (ponte) | L | T1 L · A3 L ingresso | linea di casa L |
| | 3, 4 (ponte, blu) | N | T1 N · A3 N | linea di casa N |
| | PE | PE | piastra di fondo | linea di casa PE |
| -X2 (guida 3) | 1–3 | L1, L2, L3 | KM1, KM2, KM3 morsetto 2 | W1 |
| | 4 | L4 | KM4 morsetto 2 | W2a |
| | 5 | L5 | KM5 morsetto 2 | W2b |
| | 6 | L6 | KM6 morsetto 2 | W7 |
| | 7–10 (ponte, blu) | N | filo da X0 N (sul 7) | W1 · W2a · W2b · W7 |
| | PE1–PE4 | PE | — | W1 · W2a · W2b · W7 |
| -X3 (guida 1) | 1, 2 (ponte) | +12 V | T1 +V | W3 coppie 2 e 3 · W6 coppia 2 |
| | 3–5 (ponte) | 0 V | T1 −V · ritorno delle bobine (A2 di KM1–KM6 in catena con puntalini doppi) | W3 coppie 2 e 3 · W6 coppia 2 |
| | 6, 7 (ponte) | A | A1 A · A3 A | W3 coppia 1 · W6 coppia 1 |
| | 8, 9 (ponte) | B | A1 B · A3 B | W3 coppia 1 · W6 coppia 1 |
| | PE1, PE2 | PE | Earth RS485 di A1 · filo verso la guida 3 | schermi di W3 e W6 |

Totale: 23 morsetti di passaggio (6 blu per N) e 7 di terra, più i fermi a
fine di ogni morsettiera.

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
- KM4 morsetto 2 → X2:4 → W2a **L4** → XS1 L (umidificatore 1, M2); W2a N e PE → XS1.
- KM5 morsetto 2 → X2:5 → W2b **L5** → XS2 L (umidificatore 2, M3); W2b N e PE → XS2.
- Ogni presa ha L, N e PE propri fino al quadro. XS1, XS2 e XS3 sono fuori
  dalla camera, accanto al quadro; i cavi di M2, M3 e M4 escono dalla botola.
- KM6 morsetto 2 → X2:6 → W7 **L6** → XS3 L (estrattore M4); W7 N e PE → XS3.
- Nota: K5 e K6 della scheda sono su GPIO di strapping (45/46): possibile breve
  scatto all'accensione, per questo comandano KM5/KM6 (carichi non critici).

### Folio 5 — Bassa tensione
- T1 **+12 V / 0 V** → A1 morsetti alimentazione (7–36 V).
- T1 +12 V / 0 V → morsettiera bassa tensione (-X3) → W3 coppie 2 e 3 verso
  la scatola X6 in camera (alimenta A6, B1, A2 e le ventole) e W6 coppia 2
  verso B5.
- T1 **+12 V** → **COM di K1** → ponticello → COM K2 → … → COM K6 (un solo
  gruppo, tutto a 12 V; filo rosso 0,75–1 mm², puntalini doppi).
- K*n* NA → bobina **A1** di KM*n* (n = 1…6); bobina **A2** di KM1–KM6 → 0 V comune (morsetto **−V** di T1, distribuito con morsettiera/Wago; +V e −V di T1 indicati come +12 V e 0 V in tutto lo schema).
- Diodo V*n* in parallelo a ogni bobina KM*n*: catodo su A1, anodo su A2.
  Montato fisicamente **sui morsetti A1/A2 del contattore** (disegnarlo
  accanto alla bobina, non sulla scheda). Nota nello schema: "da confermare —
  omettere se la bobina ha soppressione interna (verifica col tester)".
- Morsetti NC di K1–K6: non collegati.
- Masse 0 V di T1 e A1 in comune.

### Folio 6 — Bus RS485 e nodo in camera
- **Bus in linea**: A1 RS485 A/B → morsettiera X3 → A3 (SDM120) A/B → W3
  coppia 1 → X6. In X6 la coppia A/B si divide con due Wago 221 verso la
  scheda RS485 di A6 e verso la sonda B1 (tratti di pochi cm).
- Derivazione B5: da X3 lo spezzone W6 (coppia 1) porta A/B alla sonda di
  cantina B5 (~2 m, accettabile a 9600 baud).
- **Terminazioni 120 Ω solo ai due estremi**: R1 sulla scheda A1 (ponticello
  di terminazione abilitato) e R2 in X6 tra A e B. Verificare che la breakout
  di A6, l'SDM120 e le sonde **non** abbiano altre terminazioni attive.
- Morsetto **Earth** dell'RS485 di A1 → PE (scarica le protezioni; il lato
  RS485 è isolato). Lo 0 V del bus è quello di T1, portato in camera da W3.
- Indirizzi Modbus: B1 = 1, A3 = 2, B5 = 3, A6 = 4.
- **In X6**: W3 +12 V → Wago 12 V → ingresso 12 V della breakout A6, +12 V di
  B1, alimentazione di A2, W5 +12 V. W3 0 V → Wago 0 V → GND di A6, B1, A2,
  W5 0 V.
- B2 cella → A4 HX711: E+, E−, A+, A−.
- A4 VCC ← A6 **3V3**; A4 GND ← A6 GND; A4 DOUT → A6 **D1**; A4 SCK ← A6
  **D3**.
- B3 DS18B20 parete e B4 pavimento in parallelo: DATA → A6 **D10**, VDD → A6
  3V3, GND → GND; **R3 4,7 kΩ** tra D10 e 3V3.
- PWM: A6 **D7** → ingresso segnale di A2; uscita di A2 (lato massa, OUT−) →
  W5 coppia 3 → X4 → PWM di M5 e M6 in parallelo (il pull-up è interno alle
  ventole).
- W5 coppie 1 e 2 → X4 → +12 V e GND di M5 e M6 in parallelo.
- TACH M5 → X4 → W5 coppia 4 → A6 **D0**; TACH M6 → X4 → W5 coppia 4 → A6
  **D8**. **R4, R5 10 kΩ** tra ciascun TACH e 3V3.
- **Dentro X4**: il cavo di ciascuna ventola entra da un pressacavo con la sua
  spina 4 pin; la spina si innesta nella presa di una prolunga tagliata, i cui
  4 fili vanno sui Wago insieme ai conduttori di W5 (Wago +12 V: W5 coppie 1 e
  2 + M5 + M6; Wago 0 V: W5 coppie 1, 2, 3 + M5 + M6; Wago PWM: W5 coppia 3 +
  M5 + M6; TACH M5 e TACH M6 con un Wago a 2 vie ciascuno verso W5 coppia 4).
  Tutte le giunzioni restano nella scatola. Il TACH della seconda ventola è
  separato: non usare la catena PST tra le due ventole.
- A5 Pico-RTC-DS3231 innestato sul connettore H1/H2 di A1: SDA = **GPIO4**
  (H1 pin 15), SCL = **GPIO5** (H1 pin 14), alimentato dal connettore.
  Nessun filo.

---

## Disposizione sulla piastra (folio 7)

Cassetta BOXEXPERT Fleet 500 × 400 × 240 mm (altezza × larghezza ×
profondità) con piastra di fondo. Tre guide DIN da ~45 cm avvitate alla
piastra, canaline asolate 25 × 40 sopra e sotto ogni guida e sui due lati
(1 modulo = 17,5 mm). Ingombri da verificare all'arrivo dei componenti.

| Guida | Da sinistra a destra |
|---|---|
| 1 (in alto) — bassa tensione | T1 Mean Well HDR-60 (3 mod) · A1 Waveshare con A5 innestato (~150 mm, alta ~90 mm, profonda ~40 mm più l'RTC) · morsettiera bassa tensione X3 su morsetti UK2.5B: +12 V, 0 V, A, B (9 morsetti) + 2 di terra (~60 mm) |
| 2 — contattori | KM1 · KM2 · KM3 · KM4 · KM5 · KM6 (~6 mod) con i diodi V1–V6 sui morsetti delle bobine · spazio libero per contattori aggiuntivi |
| 3 (in basso) — 230 V | morsetti di ingresso X0 (L, L, N, N + 1 di terra) · A3 SDM120 (1 mod) · morsettiera di uscita X2: L1, L2, L3 (stufa), L4, L5 (umidificatori), L6 (estrattore), 4 × N blu, 4 di terra (UK2.5B e USLKG giallo-verdi; 14 morsetti, ~75 mm) · spazio libero |

- 230 V in basso perché i cavi W1, W2a, W2b e W7 escono dal basso; bassa
  tensione in alto, lontana dalla potenza.
- Pressacavi tutti sul fondo: a **sinistra** quelli a 230 V (linea, W1, W2a,
  W2b, W7), a **destra** quelli a bassa tensione (W3, W6). Canalina laterale
  sinistra per il 230 V, destra per la bassa tensione.
- I fili a 12 V delle bobine passano nelle canaline orizzontali tra guida 1 e
  guida 2 insieme ai 230 V: devono avere isolamento 300/500 V o superiore
  (H05V-K o H07V-K).
- Valvola anticondensa M12 in nylon (di compensazione, IP68) sul fondo, al centro.

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
  stufa niente salami. Scatolina ventole X4 in alto tra le ventole, fuori dal getto di nebbia.
  I cavi degli umidificatori salgono alla botola senza giunzioni in camera.
- **Botola** sul soffitto, 32 × 45, vicino alla porta: estrattore M4 + valvola Y1;
  tubo flessibile Ø 100 fino all'**angolo opposto alla porta** (dietro i salami).
- **Bilancia**: cella B2 sulla parete della porta, a metà della zona salami;
  **scatola X6** (nodo A6, HX711 A4, MOSFET A2) subito sopra, in alto; sonda di parete B3 su una piastrella vicina, **in basso** (la condensa si forma su pareti e pavimento, non sul soffitto);
  sonda di pavimento B4 sotto, fissata a una piastrella del pavimento a pochi
  cm dal muro (posizione definitiva dopo il test di preriscaldo: dove il
  termometro a infrarossi trova la superficie più fredda).
- **Sonda di cantina B5** (fuori dalla camera): vicino alla porta, all'altezza
  della griglia d'ingresso dell'aria, lontana dallo scarico dell'estrattore
  (botola) e dal quadro (che scalda).
- **Sonda B1**: al centro della zona salami, a ~1,2 m da terra, ad almeno 1 m
  dalla parete destra e lontana dalla bocca del tubo; il suo cavo arriva a X6.
- **W5**: spezzone corto da X6 a X4, lungo il soffitto e la parete destra.
- **Percorso**: dal quadro i cavi salgono sul muro esterno, passano **sopra il
  tetto della botte** ed entrano dalla botola attraverso un pannello con
  pressacavi (lo stesso che porta l'estrattore). Due tubi corrugati separati:
  uno per 230 V (W1 e i cavi di M2, M3), uno per bassa tensione (W3). Dentro la camera
  cavi fissati a soffitto e parete con clip; pressacavi delle scatole rivolti
  verso il basso con ansa di gocciolamento.

---

## Consegna

- Il file `camera_salumi.qet` apribile in QElectroTech.
- Lo script Python che lo genera (così posso rigenerarlo con modifiche).
- Un breve riepilogo di cosa hai disegnato, cosa hai semplificato e cosa resta
  da completare a mano.
