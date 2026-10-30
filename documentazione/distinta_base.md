# Camera salumi — distinta base definitiva

Versione 4.11 del 30/10/2026: quadro su 3 guide DIN da 270 mm (Q1, contatore, contattori e fusibili sulla guida 2; X2 e X3 sulla guida 3, in acciaio), tolta la morsettiera X0 (puntalini doppi sulle uscite di Q1), display rimandato, modulo MOSFET nella scatola X4, terza ventola M7. Versione 4.10 del 27/10/2026: fusibili F1 (W3, camera) e F2 (W6, cantina) su portafusibili UK5-HESI (sulla guida 2 dalla rev. 4.11), con la nuova morsettiera X5 dei 12 V protetti (un conduttore del Cat5e per morsetto); tolti i diodi 1N4007 (soppressione integrata nei contattori) e presa e spina CEE della stufa (W1 arriva direttamente alla stufa). Versione 4.9 del 27/10/2026: Cat5e UTP già in possesso al posto del Cat6 FTP (niente schermi); guida DIN in acciaio zincato da negozio per le guide 2 e 4. Versione 4.8 del 26/10/2026: schema della scatola X6 (pin da saldare sulla breakout, niente resistenze dei giri e R2, una sola coppia di alimentazione in W5). Versione 4.7 del 26/10/2026: righe del quadro ridistribuite (stacco di ~9 mm tra canaline e componenti sulle guide 1 e 4, display attaccato, niente fascia libera in basso); Waveshare 145×90×40 mm. Versione 4.6 del 25/10/2026: cassetta più grande, BOXEXPERT Fleet 600×400×200 con 4 guide DIN; display D1 in versione con case, agganciato alla guida 2 con clip DIN (si legge attraverso lo sportello, si tocca aprendolo). Versione 4.5 del 25/10/2026: tolto il ripartitore X7, fase dei contattori di nuovo in catena con puntalini doppi; X3 con 12 morsetti + 3 di terra. Versione 4.4 del 25/10/2026: Waveshare e pinza con puntalini già in possesso. Versione 4.3 del 25/10/2026: ripartitore unipolare Elettrocanali (X7) per la fase dei contattori al posto della catena con puntalini doppi; 6 fili da 2,5 mm². Versione 4.2 del 24/10/2026: magnetotermico generale C10 (Q1) nel quadro, già in possesso. Versione 4.1 del 20/10/2026: morsetti ricontati; spelafili già in possesso; umidificatori a spina su prese fuori dalla camera, ognuna con terra propria. Versione 4 del 20/10/2026: nodo XIAO in camera, quadro con piastra di fondo. Versione 3 del 18/10/2026 (ventole PWM a 12 V, tutto su guida DIN, nessuna saldatura). Le sigle sono quelle dello schema
(`prompt_schema_qelectrotech.md`). Prezzi Amazon.it rilevati tra il 17 e il
18/10/2026, indicativi.

Stato: **C** = da comprare · **P** = già in possesso · **F** = ferramenta o
negozio di materiale elettrico.

## 1. Quadro e logica

| Sigla | Q.tà | Componente | Codice / link | Prezzo | Stato |
|---|---:|---|---|---:|:-:|
| -A1 | 1 | Waveshare ESP32-S3-Relay-6CH (già in possesso) | [B0CXPG4XGZ](https://www.amazon.it/dp/B0CXPG4XGZ) | — | P |
| -T1 | 1 | Alimentatore Mean Well HDR-60-12 (12 V, 4,5 A, DIN) | [B072DXXRW3](https://www.amazon.it/dp/B072DXXRW3) | 20,73 € | C |
| -KM1…6 | 6 | Contattore modulare HCH8s-25Z, bobina 12 V DC, 25 A 2NA | [B0BKWQ2P32](https://www.amazon.it/dp/B0BKWQ2P32) | 6 × 12,00 € | C |
| -Q1 | 1 | Magnetotermico Gewiss MTC45 GW90026, 1P+N **C10**, 4,5 kA, 1 modulo: generale del quadro, protegge i cavi da 1,5 mm². Il differenziale 30 mA è quello del quadro di casa | — | — | P |
| -A3 | 1 | Contatore Eastron SDM120 Modbus, monofase 45 A a inserzione diretta, **1 modulo DIN**, RS485 (consumi degli attuatori) | [B08X8SD1FD](https://www.amazon.it/dp/B08X8SD1FD) | 40,80 € | C |
| -A5 | 1 | Waveshare Pico-RTC-DS3231, si innesta sul connettore Pico della scheda (nessun filo) | [B0915KRWNZ](https://www.amazon.it/dp/B0915KRWNZ) | 19,99 € | C |
| — | 1 | **Quadro BOXEXPERT Fleet 600×400×200**, ABS, IP65, variante grigia con sportello trasparente, piastra di fondo zincata inclusa. Interno 548×341×189 mm (dato venditore); piastra da misurare (nel disegno stimata 300×510) | [B07C84YMZN](https://www.amazon.it/dp/B07C84YMZN) | 81,17 € | C |
| — | 3 | Guide DIN 35×7,5 da 270 mm (rev. 4.11: tre guide, già montate). **La guida 3 deve essere in acciaio**: i morsetti di terra di X2 e X3 si serrano lì (verificare con una calamita) | negozio di materiale elettrico | — | P |
| — | 2 | Canalina asolata 25×40 grigia con coperchio, barra da 2 m (servono ~2,3 m: 2 pezzi verticali da ~51 cm, 5 orizzontali da ~25 cm; misure da riprendere sulla piastra) | in negozio di materiale elettrico; riferimento [Elettrocanali ECA2540](https://www.comcavi.shop/prodotto/elettrocanali-eca2540-canale-asolato-25x40/) | da verificare | F |
| -X2, -X3, -X5 | 2 | Kit morsetti su guida UK2.5B: per kit 20 morsetti (4 blu), 2 di terra, 2 ponticelli fissi, 5 fermi, 2 guide da 20 cm. In due kit: 40 morsetti (ne servono 28, di cui 4 blu per N: 22 su X2 e X3 e 6 su X5), 4 di terra, 4 ponticelli da tagliare a misura, 10 fermi (ne servono 6) | [JINXM, B08MKZ7FQ1](https://www.amazon.it/dp/B08MKZ7FQ1) (il kit HERKINDNESS B0857JK8PY non è più disponibile) | 2 × 23,89 € | C |
| -X2, -X3 | 5 | Morsetti di terra UK2.5 giallo-verdi a vite, si serrano sulla guida. Ne servono 8: 4 dai due kit + 5 di questa confezione = 9 | [B0DGX4DRB9](https://www.amazon.it/dp/B0DGX4DRB9) (i USLKG2.5 B0H8T4TXXR arrivano solo a metà novembre) | 14,99 € | C |
| -F1, -F2 | 4 | **Portafusibili UK5-HESI** per guida DIN 35 mm, fusibili cilindrici 5×20 (marca Be Your Mind, compatibili Phoenix Contact ma non originali): 2 montati sulla guida 3 (F1 ramo camera W3, F2 ramo cantina W6), 2 di scorta. Dati dell'originale Phoenix: largo 8,2 mm, alto ~72,5 mm, 6,3 A, conduttori 0,2–4 mm²; da controllare sui pezzi | [B0FGD7CXSN](https://www.amazon.it/dp/B0FGD7CXSN) | — | P |
| -F1, -F2 | 1 | **Fusibili 5×20 in vetro, ritardati (T)**: F1 **1 A T**, F2 **0,25 A T**, con un paio di scorte ciascuno. F1 scelto dopo la misura del 30/10/2026 (vedi sotto) | negozio di elettronica | — | F |
| — | 1 | Pinza a cricchetto Preciva con 1200 puntalini, anche doppi (2×0,5 · 2×0,75 · 2×1 · 2×1,5 mm²): già in possesso | [B0CRCVMNQZ](https://www.amazon.it/dp/B0CRCVMNQZ) | — | P |
| — | 1 | Spelafili (già in possesso): fili da 0,2 mm² in su, lunghezza di spelatura 11 mm per i Wago | — | — | P |
| — | 8 m | Cavo H07V-K 1,5 mm² (cablaggio 230 V nel quadro): **marrone 4 m**, **blu 2 m**, **giallo-verde 2 m** (nello schema ~2,2 / 1,2 / 1,3 m, più margine per canaline e morsetti; in matassine da 5 m: 5 m per colore) | negozio di materiale elettrico; in alternativa [Electraline 25139, B00IJCW374](https://www.amazon.it/dp/B00IJCW374) | da verificare | F |
| — | 11 m | Cavo H05V-K 0,75 mm² (12 V nel quadro): **rosso 7 m** (+12 V, COM dei relè, bobine dei contattori), **nero 4 m** (0 V) (nello schema ~4 / ~2 m, più margine; in matassine: 10 m rosso e 5 m nero) | negozio di materiale elettrico; in alternativa [ManoMano](https://www.manomano.it/cat/cavo+unipolare+rosso) | da verificare | F |
| — | 5 | Valvole anticondensa (di compensazione) in nylon, M12×1,5, IP68: una per il quadro, X6 e X4, due di scorta (verificare dado e guarnizione) | [SHINEOFI, B0HG57QS4F](https://www.amazon.it/dp/B0HG57QS4F) | 19,09 € | C |
| — | 1 | Pressacavi M20 IP68 (quadro) | [B0GYRDCC9Z](https://www.amazon.it/dp/B0GYRDCC9Z) (26 pz) | 7,99 € | C |
| — | 1 | Morsetti Wago 221 assortiti (2, 3, 5 vie): giunzioni in X6 e nelle scatole | [B06XRJHTS3](https://www.amazon.it/dp/B06XRJHTS3) (40 pz) | 21,96 € | C/F |
| -R1 | 1 | Resistenza 120 Ω (terminazione RS485 lato quadro, solo se la scheda A1 non ha il ponticello) | negozio di elettronica | — | F |
| | | **Subtotale** (prezzi noti) | | **≈ 417 €** | |

## 1 bis. Nodo in camera (scatola X6)

| Sigla | Q.tà | Componente | Codice / link | Prezzo | Stato |
|---|---:|---|---|---:|:-:|
| -A6 | 1 | XIAO ESP32C3 + Seeed XIAO RS485 Breakout: è la sonda-th di oggi, riusata con il firmware `salumi-nodo.yaml` | 102010633 + 113991354 | — | P |
| -A2 | 1 | Modulo MOSFET dual a morsetti (10 pz), sul filo PWM delle ventole, nella scatola X4: protegge la XIAO, nessuna saldatura | [B0GL1NWZQH](https://www.amazon.it/dp/B0GL1NWZQH) | 8,99 € | C |
| -X6 | 1 | Scatola stagna IP65 150×110×70 con pressacavi (A6, A4, Wago, resistenza R3), in alto sopra la bilancia | [B0F6YGYR7K](https://www.amazon.it/dp/B0F6YGYR7K) | 13,49 € | C |
| -R3 | 1 | Resistenza 4,7 kΩ (pull-up 1-Wire) | [B0FPX6T6SC](https://www.amazon.it/dp/B0FPX6T6SC) | 9,99 € | C/F |
| — | 1 | Pin maschi a passo 2,54 mm in strip (2 file da 7 da saldare sulla breakout) | negozio di elettronica | — | F |
| — | 1 | Kit Dupont 2,54 mm SeKi 17422 (gusci, pin maschi e femmina a crimpare, pinza): pin femmina sui cavetti C1–C3 verso la XIAO, due gusci 1×6 sulle file della XIAO, un guscio da 1 su D6 (giri M7) e un tappo da 1 sul 5V | — | — | P |
| — | 1 | Vernice protettiva acrilica per circuiti stampati, spray 400 ml (morsetti e connettori esclusi) | [Electrolube APL (RS)](https://it.rs-online.com/web/p/rivestimenti/4090956) | 26,30 € + IVA | C |
| | | **Subtotale** (prezzi noti, IVA compresa) | | **≈ 65 €** | |

## 2. Sensori

| Sigla | Q.tà | Componente | Codice / link | Prezzo | Stato |
|---|---:|---|---|---:|:-:|
| -B1 | 1 | Sonda Seeed S-TH-01 T/UR RS485, **camera**, indirizzo 1 | Seeed 101990881 | — | P (oggi sulla XIAO) |
| -B5 | 1 | Sonda Seeed S-TH-01, **cantina**, indirizzo 3 (stesso modello di B1, per avere una differenza di umidità affidabile) | Seeed 101990881, stesso canale d'acquisto della prima | da verificare | **C** |
| -B3, -B4 | 2 | DS18B20 impermeabile, cavo 3 m: **parete** e **pavimento** | [B07CZ1G29V](https://www.amazon.it/dp/B07CZ1G29V) (2 pz) | 18,26 € | C |
| -A4, -B2 | 1 | HX711 + cella di carico 2 kg | — | — | P (oggi sulla XIAO, da calibrare) |
| — | 1 | Termometro a infrarossi (test di preriscaldo: pavimento, angoli, pareti) | [TempPro TP30, B0BGGJH3G2](https://www.amazon.it/dp/B0BGGJH3G2) | 16,27 € | C |
| | | **Subtotale** (senza B5) | | **34,53 €** | |

La XIAO ESP32-C3 con la scheda RS485 diventa il nodo in camera A6 (sezione 1 bis).
Lo Shelly H&T Cantina resta come riserva della B5.

## 3. Attuatori e circuito dell'aria

| Sigla | Q.tà | Componente | Codice / link | Prezzo | Stato |
|---|---:|---|---|---:|:-:|
| -E1 | 1 | Stufa a 3 lampade IR, 1200 W, con antiribaltamento | — | — | P |
| -M2, -M3 | 2 | Umidificatori a ultrasuoni, a spina | — | — | P |
| -M5, -M6, -M7 | 3 | **Ventole ARCTIC P12 Slim PWM PST** 120 mm, 12 V, 4 fili, 200–2100 giri/min (confezione da 3, tutte e tre in fila: nessuna di scorta). PWM collegato direttamente alla scheda tramite il transistor Q1, giri letti dalla scheda | [B09RWTCXRR](https://www.amazon.it/dp/B09RWTCXRR) | 19,22 € | C |
| — | 1 | Prolunghe 4 pin PWM (6 pz): 3 da tagliare per collegare le ventole in X4 senza toccarle, 2 tagliate a metà per i cavetti C1 (HX711), C2 (sensori) e C3 (ventole) in X6, 1 di scorta | [B09SKYRB3V](https://www.amazon.it/dp/B09SKYRB3V) | 6,99 € | C |
| -M4 | 1 | **Estrattore, consigliato: Vents TT-100**, in linea a flusso misto, 145/187 m³/h, 21/33 W, collegato alla velocità bassa; **senza spina** (aggiungere una spina Schuko) | [B01LZQA9U9](https://www.amazon.it/dp/B01LZQA9U9) | 40,55 € | C |
| -M4 (alt.) | 1 | Estrattore assiale Airope, 107 m³/h a bocca libera, 14 W, con spina: più economico, ma con 3 m di tubo e la valvola perde molta portata | [B08QFYMFJL](https://www.amazon.it/dp/B08QFYMFJL) | 22,90 € | in alternativa |
| -Y1 | 1 | Valvola antiritorno a molla Ø 100, neverest RKI (uscita, lato cantina) | [B08LNS7TCV](https://www.amazon.it/dp/B08LNS7TCV) | 15,99 € | C |
| — | 1 | Tubo flessibile alluminio Ø 100, 3 m, con 2 fascette (aspirazione fino all'angolo opposto) | [B0FB3BBDSW](https://www.amazon.it/dp/B0FB3BBDSW) | 12,06 € | C |
| — | 1 | **Griglia d'ingresso** Ø 100 inox con valvola antiritorno magnetica, sulla porta in basso, montata in modo che si apra **verso la camera** | [B0F52BLHQ4](https://www.amazon.it/dp/B0F52BLHQ4) | 28,44 € | C |
| | | **Subtotale** (con Vents TT-100) | | **123,25 €** | |

**Perché il Vents TT-100.**
- **Portata:** il motore a flusso misto regge meglio la resistenza di tubo, curva e valvola. A parità di aria ricambiata lavora meno minuti.
- **Consumi:** la differenza col Airope è di pochi Wh al giorno, per circa 2–3 ore di funzionamento. Il calore perso dipende dai m³ d'aria ricambiata, non dall'estrattore.
- **Prezzo:** costa 18 € in più. Il Vortice Lineo 100 suggerito dal documento costa invece circa 230 €, e l'ho scartato.

## 4. Cavi, prese e scatole

| Sigla | Q.tà | Componente | Codice / link | Prezzo | Stato |
|---|---:|---|---|---:|:-:|
| -W1 | 10 m | FROR 5G1,5, quadro → stufa, diretto (niente presa e spina) | [B01FSZYO08](https://www.amazon.it/dp/B01FSZYO08) | 28,59 € | C |
| -W2a, -W2b, -W7 | 25 m | FROR 3G1,5: spezzoni di ~1 m dal quadro alle prese XS1, XS2, XS3 e i due cavi allungati degli umidificatori (fino a ~10 m ciascuno, senza giunzioni in camera) | [B0DH3X2ZXS](https://www.amazon.it/dp/B0DH3X2ZXS) | 38,55 € | C |
| -W3, -W5, -W6 | ~15 m | Cat5e UTP **rame pieno (non CCA)**, già in possesso, da tagliare: W3 quadro → X6 (~10 m: 12 V, 0 V, A, B), W5 X6 → X4 ventole (~2,5 m), W6 quadro → B5 cantina (~2 m). Non schermato: posarlo a qualche cm dai cavi 230 V | — | — | P |
| -XS1, -XS2, -XS3 | 3 | Contenitore Electraline FIXA con presa, fuori dalla camera accanto al quadro (umidificatore 1, umidificatore 2, estrattore) | [B0G71348W7](https://www.amazon.it/dp/B0G71348W7) | 3 × 4,90 € | C |
| -X4 | 1 | Scatola IP65 150×110×70 con pressacavi (derivazione ventole e modulo MOSFET A2; valvola anticondensa dalla confezione del quadro) | [B0F6YGYR7K](https://www.amazon.it/dp/B0F6YGYR7K) | 13,49 € | C |
| — | 1 | Kit 32 pressacavi M12–M25 (pannello botola, scatole) | [B0BFL3VQYQ](https://www.amazon.it/dp/B0BFL3VQYQ) | 10,24 € | C |
| — | 10 m | Tubo corrugato Ø 25, in due tratti (230 V e bassa tensione) | [B0FNKPP8DK](https://www.amazon.it/dp/B0FNKPP8DK) | 15,90 € | C |
| — | 1 | Filo in silicone 18 AWG (collegamenti interni alla stufa) | [B07TT68455](https://www.amazon.it/dp/B07TT68455) | da verificare | C |
| | | **Subtotale** | | **149,46 €** | |

## 5. Ferramenta e negozio di materiale elettrico

- Spina Schuko per il Vents TT-100.
- Resistenze R1 (120 Ω, solo se serve) e R3 (4,7 kΩ): si serrano nei Wago, senza saldare. Bassa priorità: R4 33 kΩ e R5 10 kΩ (1/4 W) sul morsetto PWM del modulo MOSFET in X4, per avere le ventole ferme a XIAO spenta (issue #5). Giri delle ventole con le pull-up interne della XIAO; terminazione in X6 con l'interruttore 120R della breakout.
- Viti autofilettanti 4,2×13 (o M4 con dado) per guide e canaline sulla piastra, basette adesive per fascette, marcafili.
- Pannello per chiudere la botola: multistrato 10 mm o PVC espanso, con un foro Ø 100 per l'estrattore e i fori per i pressacavi.
- Foro Ø 100 nella porta della camera, in basso, per la griglia d'ingresso.
- Apertura fissa in alto sulla porta esterna della cantina: griglia o feritoia.
- Clip fermacavo, fascette, puntalini.
- Nastro autoagglomerante in gomma, 19 mm: spessorare i cavi delle ventole nei pressacavi M20, proteggere gli innesti esposti.
- Silicone neutro o nastro di alluminio per fissare B3 e B4 alle piastrelle.

## 6. Totale

| Gruppo | Importo |
|---|---:|
| Quadro e logica (prezzi noti, senza display) | ≈ 346 € |
| Nodo in camera (prezzi noti) | ≈ 65 € |
| Sensori (senza B5) | 34,53 € |
| Attuatori e aria (con Vents TT-100) | 123,25 € |
| Cavi, prese e scatole (senza filo in silicone) | 149,46 € |
| **Totale con i prezzi noti** | **≈ 718 €** |
| + guide DIN, canaline, cavi 1,5 e 0,75 mm², sonda S-TH-01 B5, filo in silicone, fusibili, ferramenta | da aggiungere |

Si possono togliere:
- RTC: −20 €;
- Wago e resistenza, se si prendono in negozio: −32 €;
- Airope al posto del Vents: −18 €.

## 7. Escluso per scelta (dalle liste precedenti)

- Termostato meccanico di sicurezza: scelta dell'utente, resta l'antiribaltamento della stufa.
- Differenziale nel quadro: la linea è già protetta dal differenziale 30 mA di casa; nel quadro solo il magnetotermico C10 (Q1).
- Contattori Finder: si usano gli HCH8s-25Z, uno per carico.
- Diodi 1N4007 sulle bobine (versioni fino alla 4.9): gli HCH8s-25Z hanno la soppressione integrata.
- Presa e spina CEE 5 poli della stufa XS4/XP4 (versioni fino alla 4.9): W1 arriva direttamente alla stufa.
- Display D1 Waveshare ESP32-S3-Touch-LCD-4.3B con case e clip DIN (rimandato il 30/10/2026): con il case è alto 79 mm e tra le canaline della guida 2 ce ne sono 80, senza spazio per i cavi. Non serve: tutto si legge da Home Assistant.
- Ripartitore unipolare Elettrocanali X7 e cavo da 2,5 mm² (versioni 4.3–4.4): con le guide da ~25 cm non ci sta; la fase torna in catena sul morsetto 1 dei contattori con puntalini doppi.
- Display su guida DIN Norvi IIOT: schermo da 0,96", 24 V.
- Display fissato dentro lo sportello (versione 4.5): si leggeva ma non si poteva toccare.
- Quadro BOXEXPERT Fleet 500×400×240 (ordine annullato): interno largo 340 mm, guide da ~25 cm, il display non ci stava.
- Mean Well HDR-15/30, quadri da 12, 24 e 36 moduli, prese da guida DIN.
- Vortice Lineo 100, troppo caro.
- PZEM-016 e modulo RTC sciolto: non si fissano alla guida DIN; sostituiti dal contatore SDM120 e dal Pico-RTC-DS3231.
- Presa doppia X1 in camera e cavo W2 4G1,5 (versione 4): gli umidificatori si collegano a prese fuori dalla camera.
- Kit morsetti suaywo (versione 4): 20 morsetti e 2 di terra non bastano.
- Basetta Freenove X5, cavetti Dupont e clip DIN (versione 3): con il nodo in camera il connettore Pico porta solo l'RTC.
- Quadro Intratec 48 moduli (versione 3): sostituito dalla cassetta con piastra di fondo, più spaziosa.
- Cat6 W4 verso l'HX711 (versione 3): HX711 e sonde sono collegati al nodo in camera con i loro cavi.
- Ventole ELUTENG USB 5 V con DC-DC e modulo MOSFET: sostituite dalle ventole PWM 12 V (velocità minima più bassa e stabile, lettura dei giri). Le ELUTENG restano libere.
- Serrande motorizzate: i relè sono tutti usati, bastano Y1 e la griglia con valvola.

## 8. Da verificare all'arrivo

- **Piastra di fondo: misure reali.** Il disegno usa 330×510 (larghezza dalle guide da 270 mm, altezza stimata), 3 guide. Guida 2: Q1, contatore, contattori ≈ 150 mm + X5 con F1, F2 ≈ 67 mm. Guida 3: X2 ≈ 97 mm + X3 ≈ 97 mm.
- Puntalino doppio 2×1,5 (TE1508) nel morsetto 1 dei contattori, per la catena della fase.
- Profondità: interno 189 mm, circa 160 mm davanti alla guida. Waveshare 40 mm (misurata); il più sporgente è il magnetotermico (~70 mm). Margine ampio: resta da misurare solo di quanto è rialzata la piastra.
- Contattori: larghezza effettiva in moduli (soppressione della bobina integrata: niente diodi esterni).
- **Portafusibili UK5-HESI (B0FGD7CXSN), non originali Phoenix:** larghezza (8,2 mm?), altezza (~72,5 mm?: tra le canaline della guida 2 ci sono ~137 mm), profondità; serraggio di un filo da 0,75 mm² con puntalino; portata dichiarata; **senza LED** (se hanno la spia, una piccola corrente passa anche col fusibile bruciato e la sonda B5, che consuma pochi mA, potrebbe restare accesa: in quel caso toglierla o usare i due di scorta); da che lato si apre lo sportellino e se il lato aperto va chiuso con una piastrina; fusibile senza tensione quando lo sportellino è aperto.
- **Fusibili:** misura al banco del 30/10/2026, tre ventole al massimo: 0,40 A a regime, 0,49 A all'accensione (lettura del tester); con scheda RS485, XIAO e sonda B1 ~0,5 A a regime e ~0,6 A all'accensione. **F1 1 A ritardato (T)**: il rapido rischierebbe di saltare sui picchi di accensione delle ventole. **F2 0,25 A ritardato (T)** (B5 consuma pochi mA). Preferire fusibili che dichiarano anche la tensione in continua. Comportamento dell'alimentatore HDR-60 in sovraccarico (limitazione o intermittenza) da leggere sul foglio Mean Well.
- Morsetti UK2.5B: che serrino bene un solo conduttore rigido del Cat5e (0,2 mm²; prova a strappo).
- Waveshare: spessore con l'RTC innestato (dato Waveshare 40 mm) e posizione sulla guida 1.
- Ponticelli di terminazione 120 Ω: attivi solo sulla Waveshare e in X6 (interruttore 120R della breakout della XIAO); spenti sugli altri.
- Breakout della XIAO: ordine dei poli delle due morsettiere (serigrafia) e versione della scheda (V1.2: direzione automatica, D2 libero).
- Cat5e di casa: rame pieno, non CCA (scritta "Cu" sulla guaina o filo grattato).
- Morsetti di terra B0DGX4DRB9: che abbiano il piedino metallico che si serra sulla guida (contatto con la guida, come gli USLKG); se no, renderli.
- Kit morsetti JINXM: che i ponticelli fissi siano FBI da 10 poli tagliabili (ne servono 9 pezzi da 2–4 poli, 22 poli in tutto).
- Cavo degli umidificatori: se si allunga con una giunzione, farla fuori dalla camera (o sostituire il cavo per intero); la spina si monta dopo aver passato il cavo nel pressacavo della botola.
- Vents TT-100: morsettiera e collegamento alla velocità bassa.
- Contatore SDM120 e B5: indirizzo Modbus (SDM120 a 2 e 9600 baud dai tasti frontali; B5 a 3), uno alla volta, da soli sul bus.
- Pico-RTC-DS3231: che il coperchio della scheda chiuda con il modulo innestato.
- B5: alimentazione a 12 V (range 3,6–30 V).
