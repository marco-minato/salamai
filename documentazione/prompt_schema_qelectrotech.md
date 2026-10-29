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
> - nuovo **piano dei morsetti X0, X2, X3** con la numerazione (netlist);
> - (rev. 4.6) cassetta **BOXEXPERT Fleet 600×400×200** con **4 guide DIN**;
>   **tolto il ripartitore X7**, la fase dei contattori torna **in catena con
>   puntalini doppi**; X3 sulla guida 2 (12 morsetti + 3 di terra); nuovo
>   **display -D1** (versione con case) sulla guida 2 con clip DIN, sul bus
>   RS485.
> - (rev. 4.10) **fusibili -F1 e -F2** (portafusibili UK5-HESI, 5×20) sulla
>   guida 3 con la nuova morsettiera **-X5** dei 12 V protetti: F1 sul +12 V
>   di W3 (camera, ventole comprese), F2 sul +12 V di W6 (sonda cantina B5);
>   un conduttore del Cat5e per morsetto; **tolti i diodi V1–V6** (i contattori
>   hanno la soppressione integrata) e **presa e spina CEE XS4/XP4** (W1 arriva
>   direttamente alla stufa).

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
| 3 | Stufa (3 lampade IR) | contattori KM1–KM3 → cavo W1 5G1,5 direttamente nella stufa → interruttori interni → lampade → antiribaltamento → N |
| 4 | Prese di servizio | KM4, KM5, KM6 → prese XS1, XS2 (umidificatori) e XS3 (estrattore), tutte **fuori** dalla camera, accanto al quadro; i cavi degli apparecchi escono dalla botola |
| 5 | Bassa tensione 12 V | alimentatore 12 V, scheda Waveshare, relè K1–K6 → bobine 12 V dei contattori KM1–KM6 (soppressione integrata); fusibili F1 e F2 e morsettiera X5; 12 V e 0 V verso la camera nel cavo W3 (dopo F1) e verso la cantina nel cavo W6 (dopo F2) |
| 6 | Bus RS485 e nodo in camera | bus RS485 (Waveshare, SDM120, display D1, sonda cantina B5, cavo W3, sonda camera B1, nodo A6) con le due terminazioni 120 Ω; dentro la scatola X6: nodo A6, HX711 + cella di carico, sonde DS18B20 di parete e pavimento, modulo MOSFET A2 e ventole M5/M6 (via W5 e X4); RTC Pico-RTC-DS3231 innestato sul connettore Pico |
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
| -A1 | **Waveshare ESP32-S3-Relay-6CH** (Amazon B0CXPG4XGZ) | 6 relè 10 A 250 VAC, RS485 isolato con direzione automatica, alimentazione 7–36 V DC, custodia ABS per guida DIN (non a profilo modulare), 145 mm in larghezza × 90 mm in altezza × 40 mm di profondità (dato Waveshare; profondità misurata). Relè: CH1=GPIO1, CH2=GPIO2, CH3=GPIO41, CH4=GPIO42, CH5=GPIO45, CH6=GPIO46. RS485 interno su GPIO17/18. Buzzer GPIO21, LED RGB GPIO38. Uscite relè su morsetti a 3 poli COM/NA/NC. RS485 **isolato galvanicamente**, morsettiera a 3 poli A / B / Earth. Due connettori a 20 pin H1/H2 (piedinatura sotto, dallo schema elettrico ufficiale Waveshare) |
| -T1 | **Mean Well HDR-60-12** (B072DXXRW3) | 230 VAC → 12 V DC 4,5 A, guida DIN 3 moduli (dimensionato per scheda + 6 bobine + ventole) |
| -KM1…-KM6 | **Contattore modulare HCH8s-25Z**, bobina **12 V DC**, 25 A, 2 NA (B0BKWQ2P32) | ~1 modulo ciascuno (da verificare). Usato un solo contatto NA (1→2), il secondo (3→4) resta libero. KM1–KM3 lampade 1–3, KM4 umidificatore 1, KM5 umidificatore 2, KM6 estrattore. Bobina A1/A2, contatto di potenza 1→2 |
| -F1, -F2 | **Portafusibili UK5-HESI** su guida DIN, fusibili **5×20** (B0FGD7CXSN, compatibili Phoenix, non originali) | sulla guida 3, a destra. F1 = +12 V del ramo camera (W3 → X6, ventole comprese); F2 = +12 V del ramo cantina (W6 → B5). Valori **da confermare** (candidati: F1 1 A rapido, F2 0,25 A ritardato): scriverli nello schema come "1 A F (da conf.)" e "0,25 A T (da conf.)". Lo 0 V non passa dai fusibili. Nessun diodo sulle bobine: gli HCH8s-25Z hanno la soppressione integrata |
| -A2 | **Modulo MOSFET dual** a morsetti (B0GL1NWZQH, PWM fino a 20 kHz, ingresso 3,3 V) | **nella scatola X6 in camera**; usato come interruttore verso massa (collettore aperto) sul filo PWM delle ventole: protegge il GPIO della XIAO dal pull-up interno della ventola (fino a 5 V). PWM a 20 kHz, invertito nel firmware. Nessuna saldatura |
| -A6 | **Nodo in camera: Seeed XIAO ESP32C3** (102010633) **+ Seeed XIAO RS485 Breakout** (113991354) | nella scatola X6. La breakout ha il ricetrasmettitore RS485 (direzione su D2) e accetta 12 V con il suo step-down. Pin: RS485 TX D4 / RX D5 / DE D2; HX711 DOUT D1, SCK D3; DS18B20 D10; PWM ventole D7 → A2; TACH M5 D0, TACH M6 D8; liberi D6, D9. Due file di pin maschi da 7 saldate nei fori accanto alle prese della breakout (pin verso l'alto): da lì cavetti Dupont femmina verso Wago e HX711. Morsettiere della breakout: bus A / B / GND e alimentazione INT / 5V / 12V (ordine da verificare sulla serigrafia); interruttori 120R su ON e 5V su OUT. Modbus indirizzo 4, 9600 baud. È la XIAO della sonda attuale (sonda-th), riusata |
| -X6 | **Scatola stagna IP65** in policarbonato/ABS (~150×110×70 mm o più grande se serve) con **valvola anticondensa M12** in basso | dentro la camera, **in alto sulla parete della porta, sopra la bilancia** (zona più calda e asciutta, lontana dal getto della nebbia e dal fascio della stufa). Pressacavi tutti verso il basso con ansa di gocciolamento. Contiene A6, A4, A2, i Wago di giunzione e le resistenze R1–R4. Schede trattate con vernice protettiva (conformal coating), morsetti esclusi |
| -R1, -R2 | **Resistenze 120 Ω** | terminazioni del bus RS485 ai due estremi: R1 nel quadro (o il ponticello di terminazione della scheda A1), in X6 la terminazione è l'interruttore 120R della breakout su ON (niente resistenza R2). Solo due in tutto il bus |
| -R3 | **Resistenza 4,7 kΩ** | pull-up del bus 1-Wire, tra DATA (D10) e 3V3, in X6 |
| -Q1 | **Magnetotermico 1P+N C10**, 4,5 kA, Gewiss MTC45 GW90026 (già in possesso) | generale del quadro, primo a sinistra sulla guida 4 (1 modulo). La linea di casa entra direttamente nei suoi morsetti superiori L e N; le uscite inferiori vanno ai morsetti di ingresso X0. C10 protegge tutti i cavi da 1,5 mm² a valle. La protezione differenziale 30 mA è quella del quadro di casa, a monte della linea |
| -D1 | **Display Waveshare ESP32-S3-Touch-LCD-4.3B, versione con case** (B0DCNSRT31) | 4,3" 800×480 touch, alimentazione 7–36 V (preso dal 12 V), RS485 a vite sul retro. Agganciato alla guida 2 con una clip DIN avvitata ai fori a 75 mm del case: si legge attraverso lo sportello trasparente, si tocca aprendolo. Collegato a X3 (sotto) con fili H05V-K 0,75 mm². Sul bus RS485 insieme ad A1, A3, B5 e A6. Mostra i valori della camera; non comanda nulla |
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
| -X4 | Scatolina IP65 di derivazione ventole, con **valvola anticondensa M12** in basso | in alto sulla parete destra, tra le due ventole; da W5 si divide verso M5 e M6 (+12 V, 0 V e PWM in parallelo, TACH separati) |
| -B3 | **Sonda DS18B20** impermeabile (parete) | incollata/fissata a una piastrella in basso, cavo da 3 m fino a X6 |
| -B4 | **Sonda DS18B20** impermeabile (pavimento) | uguale a B3, fissata a una piastrella del pavimento vicino al muro; in parallelo a B3 sullo stesso bus 1-Wire (A6 D10) |
| -B5 | **Sonda Seeed S-TH-01** (101990881), seconda unità | in **cantina**, fuori dalla camera, vicino alla griglia d'ingresso dell'aria; RS485 in parallelo, **indirizzo 3**, con lo spezzone W6 dal quadro (breve derivazione: a 9600 baud non dà problemi); alimentata a 12 V dal Mean Well |
| -X0, -X2, -X3 | Morsetti su guida **UK2.5B** (blu per N), morsetti di terra **USLKG2.5** giallo-verdi, ponticelli FBI e fermi | X0 ingresso linea L/N/PE; X2 uscite 230 V (L1–L6, N per ogni carico, PE per ogni carico); X3 bassa tensione e X5 12 V protetti dopo F1/F2 (+12 V, 0 V, A, B, terre). Numerazione nel "Piano dei morsetti" |
| — | Morsetti **Wago 221** | giunzioni nella scatola X6 (12 V, 0 V, A, B, 3V3, 1-Wire) e nelle scatole in camera |
| -W1 | Cavo **FG16OR16 5G1,5** quadro → stufa, diretto (pressacavo sulla stufa) | L1, L2, L3, N, PE |
| -W2a, -W2b, -W7 | Spezzoni **FROR 3G1,5** quadro → prese accanto al quadro, ~1 m | W2a: L4 (KM4), N, PE → XS1 · W2b: L5 (KM5), N, PE → XS2 · W7: L6 (KM6), N, PE → XS3 |
| -W3 | Cavo **Cat5e UTP** (rame pieno, non CCA, già in possesso) quadro → scatola X6 in camera, ~10 m | coppia 1 (blu): A = blu / B = bianco-blu; coppia 2 (arancio): +12 V = arancio / 0 V = bianco-arancio; coppia 3 (verde): +12 V = verde / 0 V = bianco-verde (in parallelo alla 2); coppia 4 (marrone) di riserva; non schermato. 24 AWG (~0,2 mm²). Nel quadro: A/B su X3, +12 V su X5:2 e X5:3 (dopo F1), 0 V su X5:4 e X5:5, un conduttore per morsetto. Carico ~0,3 A: caduta ~0,25 V; posarlo a qualche cm dai cavi 230 V |
| -W5 | Spezzone **Cat5e UTP** X6 → X4 ventole, ~2,5 m | coppia 1 (blu): +12 V = blu / 0 V = bianco-blu (0,2 A per due ventole: basta una coppia); coppia 2 (arancio) di riserva; coppia 3 (verde): PWM = verde, bianco-verde di riserva; coppia 4 (marrone): TACH M5 = marrone / TACH M6 = bianco-marrone |
| -W6 | Spezzone **Cat5e UTP** quadro → sonda cantina B5, ~2 m | coppia 1: A / B (X3:5 / X3:2); coppia 2: +12 V / 0 V (X5:1 dopo F2 / X5:6) |
| — | Filo silicone 18 AWG (B07TT68455) | collegamenti interni alla stufa (zona calda) |
| — | Quadro **BOXEXPERT Fleet 600×400×200 mm**, ABS, IP65, sportello trasparente, **piastra di fondo** in lamiera zincata (B07C84YMZN, interno 548×341×189); 4 guide DIN 35 mm da ~25 cm avvitate alla piastra; **canaline asolate 25×40** sopra e sotto ogni guida e sui due lati; morsetti UK2.5B su guida con fermi; valvola anticondensa M12; pressacavi M20 (B0GYRDCC9Z) | meccanica |

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

### Piano dei morsetti X0, X2, X3, X5
Un filo per morsetto; i morsetti dello stesso potenziale sono uniti con
ponticelli FBI. I morsetti di terra (USLKG, giallo-verdi) si serrano sulla
guida, che fa da barra di terra: la guida 4 e la guida 2 sono unite da un
filo giallo-verde, e un filo giallo-verde porta la terra alla piastra di fondo.
Disegnare le quattro morsettiere con questi numeri:

| Morsettiera | Morsetto | Funzione | Lato interno | Lato campo |
|---|---|---|---|---|
| -X0 (guida 4) | 1, 2 (ponte) | L | T1 L · A3 L ingresso | Q1 uscita L |
| | 3, 4 (ponte, blu) | N | T1 N · A3 N | Q1 uscita N |
| | PE | PE | piastra di fondo | linea di casa PE |
| -X2 (guida 4) | 1–3 | L1, L2, L3 | KM1, KM2, KM3 morsetto 2 | W1 |
| | 4 | L4 | KM4 morsetto 2 | W2a |
| | 5 | L5 | KM5 morsetto 2 | W2b |
| | 6 | L6 | KM6 morsetto 2 | W7 |
| | 7–10 (ponte, blu) | N | filo da X0 N (sul 7) | W1 · W2a · W2b · W7 |
| | PE1–PE4 | PE | — | W1 · W2a · W2b · W7 |
| -X3 (guida 2) | PE1, PE2, PE3 | PE | Earth RS485 di A1 (PE1) · filo verso X2 PE4 sulla guida 4 (PE3) | PE2 libero (cavi Cat5e non schermati) |
| | 1–3 (ponte) | B | A1 B (1) · A3 B (3) | W3 coppia 1 (1) · W6 coppia 1 (2) · D1 B (3) |
| | 4–6 (ponte) | A | A1 A (4) · A3 A (6) | W3 coppia 1 (4) · W6 coppia 1 (5) · D1 A (6) |
| | 7–9 (ponte) | 0 V | A1 GND (7) · T1 −V (8) · ritorno delle bobine, − di KM1–KM6 in catena con puntalini doppi (9) | filo 0 V verso X5:4 (7) · libero (8) · D1 0 V (9) |
| | 10–12 (ponte) | +12 V **non protetto** | A1 12 V (10) · T1 +V (11) · COM dei relè (12) | ingresso di F1 (10) · ingresso di F2 (11) · D1 +12 V (12) |
| -X5 (guida 3, dopo F1 e F2) | 1 | +12 V cantina (dopo F2) | uscita di F2 | W6 coppia 2, +12 V |
| | 2–3 (ponte) | +12 V camera (dopo F1) | uscita di F1 (2) · libero (3) | W3 arancio (2) · W3 verde (3) |
| | 4–6 (ponte) | 0 V | filo da X3:7 (4) · liberi (5, 6) | W3 bianco-arancio (4) · W3 bianco-verde (5) · W6 coppia 2, 0 V (6) |

Su X5 il "lato campo" è **sopra** (i Cat5e arrivano dalla canalina tra le
guide 2 e 3) e il lato interno **sotto**. Ordine sulla guida, da sinistra:
fermo · F1 · F2 · X5:1 … X5:6 · fermo. **X5:1 non è ponticellato a X5:2**, e
nessun morsetto di X5 è collegato al gruppo X3:10–12: altrimenti i fusibili
sarebbero scavalcati.

Totale: 32 morsetti di passaggio (6 blu per N; 6 su X5) e 8 di terra, 2 portafusibili, più i fermi a
fine di ogni morsettiera.

### Folio 2 — 230 V
- Linea **L / N** dal quadro di casa → **Q1** magnetotermico C10 (morsetti in alto) → uscite di Q1 → morsetti di ingresso del quadro (-X0). **PE** della linea direttamente al morsetto di terra di X0.
- **N** e **PE** distribuiti con morsetti a tutti gli utilizzatori.
- **L** → T1 (Mean Well) ingresso L; N → T1 ingresso N (la serie HDR è in classe II: **nessun morsetto PE**).
- Ordine sulla fase: morsetto di ingresso -X0 → **derivazione per T1**
  (alimentatore 12 V) → A3 **SDM120** (L ingresso → L uscita, in serie; N al
  suo morsetto N) → linea "L-carichi" → morsetto **1** (ingresso potenza)
  di KM1, poi **in catena** sul morsetto 1 di KM2…KM6 con **puntalini
  doppi** 2×1,5 mm² (filo marrone 1,5 mm²); carico massimo ~6 A. Il contatore
  misura quindi **solo gli attuatori** (lampade, umidificatori, estrattore),
  non l'elettronica.
  Gli allarmi per singolo carico sono calcolati dal firmware (potenza attesa
  in base ai relè chiusi, variazione a ogni commutazione).
- **Nessun 230 V sui morsetti dei relè K1–K6 della scheda A1.**

### Folio 3 — Stufa
- W1 arriva **direttamente nella stufa** (nessuna presa/spina): si giunta ai
  fili interni nella parte bassa della stufa.
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
- T1 +12 V / 0 V → morsettiera bassa tensione (-X3, +12 V non protetto) →
  **X3:10 → F1 → X5:2–3** → W3 arancio e verde verso la scatola X6 in camera
  (alimenta A6, B1, A2 e le ventole); **X3:11 → F2 → X5:1** → W6 +12 V verso
  B5. 0 V: X3:7 → X5:4–6 → W3 bianco-arancio, bianco-verde e W6 0 V (comune,
  senza fusibili). Waveshare, display e bobine restano sul +12 V non protetto
  di X3. Fili interni H05V-K 0,75 mm² con puntalino.
- X3:12 (+12 V) → **COM di K6** → ponticello → COM K5 → … → COM K1 (un solo
  gruppo, tutto a 12 V; filo rosso 0,75–1 mm², puntalini doppi sui COM).
- Su X3 **un solo filo per foro**: contatore, ritorno bobine e COM dei relè
  usano i fori liberi sopra dei gruppi ponticellati.
- K*n* NA → morsetto **+** della bobina di KM*n* (n = 1…6); morsetti **−** di KM1–KM6 in catena (puntalini doppi) → X3:9 sopra (0 V); +V e −V di T1 indicati come +12 V e 0 V in tutto lo schema.
- Nessun diodo sulle bobine: gli HCH8s-25Z hanno la soppressione integrata.
- Morsetti NC di K1–K6: non collegati.
- Masse 0 V di T1 e A1 in comune.

### Folio 6 — Bus RS485 e nodo in camera
- **Bus in linea**: A1 RS485 A/B → morsettiera X3 → A3 (SDM120) A/B → W3
  coppia 1 → X6. In X6 la coppia A/B si divide con due Wago 221 verso la
  scheda RS485 di A6 e verso la sonda B1 (tratti di pochi cm).
- Derivazione B5: da X3 lo spezzone W6 (coppia 1) porta A/B alla sonda di
  cantina B5 (~2 m, accettabile a 9600 baud).
- **Terminazioni 120 Ω solo ai due estremi**: R1 sulla scheda A1 (ponticello
  di terminazione abilitato) e in X6 l'interruttore 120R della breakout di A6 su ON. Verificare che
  l'SDM120 e le sonde **non** abbiano altre terminazioni attive.
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
- W5 coppia 1 (blu) → X4 → +12 V e GND di M5 e M6 in parallelo.
- TACH M5 → X4 → W5 coppia 4 → A6 **D0**; TACH M6 → X4 → W5 coppia 4 → A6
  **D8**, con le pull-up interne della XIAO attive nel firmware (niente resistenze).
- **Dentro X4**: il cavo di ciascuna ventola entra da un pressacavo con la sua
  spina 4 pin; la spina si innesta nella presa di una prolunga tagliata, i cui
  4 fili vanno sui Wago insieme ai conduttori di W5 (Wago +12 V: W5 blu + M5 + M6;
  Wago 0 V: W5 bianco-blu + M5 + M6; Wago PWM: W5 verde + M5 + M6; TACH M5 e TACH M6 con un Wago a 2 vie ciascuno verso W5 coppia 4).
  Tutte le giunzioni restano nella scatola. Il TACH della seconda ventola è
  separato: non usare la catena PST tra le due ventole.
- **Dentro X6** (rev. 4.8, disegno `scatola-x6.drawio`): Wago liberi nella scatola.
  +12 V: Wago da 5 + Wago da 3 uniti da un ponticello (W3 arancio e verde,
  12V della breakout, B1 +, A2 DC+, W5 blu). 0 V: due Wago da 5 uniti
  (W3 bianco-arancio e bianco-verde, GND del bus della breakout, B1 −, A2 DC−,
  A2 GND del segnale, W5 bianco-blu; un foro libero). RS485 A e B: Wago da 3 ciascuno (W3, breakout, B1). GND
  sensori: Wago da 5 (pin GND della XIAO, HX711 GND, B3 e B4 nero; un foro libero).
  3,3 V: Wago da 5 (pin 3V3, HX711 VCC, B3 e B4 rosso, R3). 1-Wire: Wago da 5
  (D10, B3 e B4 giallo, R3). Giri: Wago da 2 per D0 + W5 marrone e per D8 + W5
  bianco-marrone. Diretti: HX711 DT → D1 e SCK → D3 (cavetti da prolunghe ventola: C1 HX711 con connettore sull'HX711, C2 GND/3V3/D10, C3 D0/D8/D7; pin Dupont femmina crimpati, sulla XIAO due gusci 1×6, D0–D5 e GND–D7, tappi da 1 su D6 e 5V),
  D7 → PWM di A2, OUT− di A2 → W5 verde, cella → HX711 (E+ rosso, E− nero,
  A− bianco, A+ verde). W3 e W5 in Cat5e UTP: niente schermi.
- A5 Pico-RTC-DS3231 innestato sul connettore H1/H2 di A1: SDA = **GPIO4**
  (H1 pin 15), SCL = **GPIO5** (H1 pin 14), alimentato dal connettore.
  Nessun filo.

---

## Disposizione sulla piastra (folio 7)

Cassetta BOXEXPERT Fleet 600 × 400 × 200 mm (altezza × larghezza ×
profondità) con piastra di fondo e sportello trasparente. Vano interno 548 × 341 × 189 mm; piastra da
misurare (nel disegno stimata 300 × 510). Quattro guide DIN da ~25 cm (240 mm utili) avvitate alla
piastra, canaline asolate 25 × 40 sopra e sotto ogni guida e sui due lati
(1 modulo = 17,5 mm). Righe (rev. 4.7): guide 1 e 4 con ~9 mm di stacco sopra e sotto
tra componenti e canaline, guida 2 (display) e guida 3 (contattori) quasi a contatto;
la canalina inferiore è sul bordo della piastra, senza fascia libera sotto. Ingombri da verificare all'arrivo dei componenti. Disegno in scala: `quadro-disposizione.drawio` (draw.io).

Quote di montaggio (rev. 4.7, mm dal bordo alto della piastra; in larghezza dal bordo sinistro):

| Elemento | Quota |
|---|---|
| Canalina orizzontale 1 (in alto) | 0–25 |
| Asse guida 1 | 79 |
| Canalina orizzontale 2 | 133–158 |
| Asse guida 2 | 198 |
| Canalina orizzontale 3 | 238–263 |
| Asse guida 3 | 308 |
| Canalina orizzontale 4 | 353–378 |
| Asse guida 4 | 431 |
| Canalina orizzontale 5 (in basso) | 484–509 |
| Canaline laterali | 0–25 e 275–300 in larghezza, tutta altezza |
| Canaline orizzontali | lunghe 250, tra le due laterali |
| Guide DIN | da 27 a 273 (246 mm), centrate sull'asse |

Se la piastra vera è più alta di 510, la differenza va divisa tra gli stacchi delle guide 1 e 4.

| Guida | Da sinistra a destra |
|---|---|
| 1 (in alto) — bassa tensione | T1 Mean Well HDR-60 (3 mod) · A1 Waveshare con A5 innestato (145 × 90 × 40 mm) · ~35 mm liberi |
| 2 — display e morsetti 12 V | D1 display con case su clip DIN (~116 mm, alto 79) · morsettiera bassa tensione X3 su morsetti UK2.5B: 3 di terra + B, A, 0 V, +12 V (12 morsetti) (~97 mm con i fermi) |
| 3 — contattori e fusibili 12 V | KM1 · KM2 · KM3 · KM4 · KM5 · KM6 (~6 mod; bobina con diodo interno, + sopra e − sotto) · spazio libero per ~3 contattori · a destra: fermo, **F1, F2** (UK5-HESI, 8,2 mm ciascuno, alti ~72,5), **X5** 1–6 (UK2.5B), fermo (~67 mm) |
| 4 (in basso) — 230 V | Q1 magnetotermico C10 (1 mod) · morsetti di ingresso X0 (L, L, N, N + 1 di terra) · A3 SDM120 (1 mod) · morsettiera di uscita X2: L1, L2, L3 (stufa), L4, L5 (umidificatori), L6 (estrattore), 4 × N blu, 4 di terra (UK2.5B e USLKG giallo-verdi; 14 morsetti, ~75 mm) · spazio libero |

- 230 V in basso perché i cavi W1, W2a, W2b e W7 escono dal basso; bassa
  tensione in alto, lontana dalla potenza.
- Pressacavi tutti sul fondo: a **sinistra** quelli a 230 V (linea, W1, W2a,
  W2b, W7), a **destra** quelli a bassa tensione (W3, W6). Canalina laterale
  sinistra per il 230 V, destra per la bassa tensione.
- Valvola anticondensa M12 in nylon (di compensazione, IP68) sul fondo, al centro.
- **Display -D1** sulla guida 2, in alto: si legge attraverso lo sportello trasparente e si tocca aprendolo.
- I fili relè → bobine (12 V) scendono dalla guida 1 alla guida 3 nella canalina sinistra insieme ai 230 V: isolamento 300/500 V (H05V-K).

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
  al centro la stufa E1, puntata contro il muro (W1 entra direttamente nella stufa). Sopra la
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
