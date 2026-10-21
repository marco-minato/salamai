# Camera salumi — distinta base definitiva

Versione 4.1 del 20/10/2026: morsetti ricontati; spelafili già in possesso; umidificatori a spina su prese fuori dalla camera, ognuna con terra propria. Versione 4 del 20/10/2026: nodo XIAO in camera, quadro con piastra di fondo. Versione 3 del 18/10/2026 (ventole PWM a 12 V, tutto su guida DIN, nessuna saldatura). Le sigle sono quelle dello schema
(`prompt_schema_qelectrotech.md`). Prezzi Amazon.it rilevati tra il 17 e il
18/10/2026, indicativi.

Stato: **C** = da comprare · **P** = già in possesso · **F** = ferramenta o
negozio di materiale elettrico.

## 1. Quadro e logica

| Sigla | Q.tà | Componente | Codice / link | Prezzo | Stato |
|---|---:|---|---|---:|:-:|
| -A1 | 1 | Waveshare ESP32-S3-Relay-6CH | [B0CXPG4XGZ](https://www.amazon.it/dp/B0CXPG4XGZ) | 43,99 € | C |
| -T1 | 1 | Alimentatore Mean Well HDR-60-12 (12 V, 4,5 A, DIN) | [B072DXXRW3](https://www.amazon.it/dp/B072DXXRW3) | 20,73 € | C |
| -KM1…6 | 6 | Contattore modulare HCH8s-25Z, bobina 12 V DC, 25 A 2NA | [B0BKWQ2P32](https://www.amazon.it/dp/B0BKWQ2P32) | 6 × 12,00 € | C |
| -V1…6 | 6 | Diodo 1N4007 sulla bobina (solo se il contattore non ha soppressione interna: verificare col tester all'arrivo) | [B01F4SQ6KU](https://www.amazon.it/dp/B01F4SQ6KU) (100 pz) | 9,99 € | C |
| -A3 | 1 | Contatore Eastron SDM120 Modbus, monofase 45 A a inserzione diretta, **1 modulo DIN**, RS485 (consumi degli attuatori) | [B08X8SD1FD](https://www.amazon.it/dp/B08X8SD1FD) | 40,80 € | C |
| -A5 | 1 | Waveshare Pico-RTC-DS3231, si innesta sul connettore Pico della scheda (nessun filo) | [B0915KRWNZ](https://www.amazon.it/dp/B0915KRWNZ) | 19,99 € | C |
| — | 1 | **Quadro BOXEXPERT Fleet 500×400×240**, ABS, IP65, sportello trasparente, piastra di fondo in lamiera (verificare sulla pagina che piastra e sportello trasparente siano nella variante scelta) | [B0CBS922L8](https://www.amazon.it/dp/B0CBS922L8) | 78,04 € | C |
| — | 2 | Guida DIN 35 mm, 1 m (3 spezzoni da ~45 cm) | [Stok, 2 × 1 m, B07VDG4BVZ](https://www.amazon.it/dp/B07VDG4BVZ) | da verificare | C |
| — | 2 | Canalina asolata 25×40 grigia con coperchio, barra da 2 m | [Elettrocanali ECA2540 (Comcavi)](https://www.comcavi.shop/prodotto/elettrocanali-eca2540-canale-asolato-25x40/) | da verificare | C |
| -X0, -X2, -X3 | 2 | Kit morsetti su guida UK2.5B, 5 colori: per kit 20 morsetti, 2 di terra, 2 ponticelli FBI-10-6, 4 fermi, 4 coperchi, marcatori. In due kit: 40 morsetti (ne servono 23, blu per N), 8 fermi | [HERKINDNESS, B0857JK8PY](https://www.amazon.it/dp/B0857JK8PY) | 2 × 18,99 € | C |
| -X0, -X2, -X3 | 10 | Morsetti di terra USLKG2.5 giallo-verdi, si serrano sulla guida (ne servono 7, più i 4 dei kit di scorta) | [B0H8T4TXXR](https://www.amazon.it/dp/B0H8T4TXXR) | 10,05 € | C |
| — | 1 | Pinza a cricchetto 0,25–10 mm² con 1250 puntalini | [Preciva, B0CRCVMNQZ](https://www.amazon.it/dp/B0CRCVMNQZ) | 29,99 € | C |
| — | 1 | Spelafili (già in possesso): fili da 0,2 mm² in su, lunghezza di spelatura 11 mm per i Wago | — | — | P |
| — | 1 | Cavo 1,5 mm² marrone, blu, giallo-verde, 10 m (cablaggio 230 V) | [Electraline 25139, B00IJCW374](https://www.amazon.it/dp/B00IJCW374) | da verificare | C |
| — | 10 m | Cavo H05V-K 0,75 mm² rosso e nero (12 V: COM dei relè, bobine) | [ManoMano](https://www.manomano.it/cat/cavo+unipolare+rosso) | da verificare | C/F |
| — | 5 | Valvole anticondensa (di compensazione) in nylon, M12×1,5, IP68: una per il quadro, X6 e X4, due di scorta (verificare dado e guarnizione) | [SHINEOFI, B0HG57QS4F](https://www.amazon.it/dp/B0HG57QS4F) | 19,09 € | C |
| — | 1 | Pressacavi M20 IP68 (quadro) | [B0GYRDCC9Z](https://www.amazon.it/dp/B0GYRDCC9Z) (26 pz) | 7,99 € | C |
| — | 1 | Morsetti Wago 221 assortiti (2, 3, 5 vie): giunzioni in X6 e nelle scatole | [B06XRJHTS3](https://www.amazon.it/dp/B06XRJHTS3) (40 pz) | 21,96 € | C/F |
| -R1 | 1 | Resistenza 120 Ω (terminazione RS485 lato quadro, solo se la scheda A1 non ha il ponticello) | negozio di elettronica | — | F |
| | | **Subtotale** (prezzi noti) | | **≈ 412 €** | |

## 1 bis. Nodo in camera (scatola X6)

| Sigla | Q.tà | Componente | Codice / link | Prezzo | Stato |
|---|---:|---|---|---:|:-:|
| -A6 | 1 | XIAO ESP32C3 + Seeed XIAO RS485 Breakout: è la sonda-th di oggi, riusata con il firmware `salumi-nodo.yaml` | 102010633 + 113991354 | — | P |
| -A2 | 1 | Modulo MOSFET dual a morsetti (10 pz), sul filo PWM delle ventole: protegge la XIAO, nessuna saldatura | [B0GL1NWZQH](https://www.amazon.it/dp/B0GL1NWZQH) | 8,99 € | C |
| -X6 | 1 | Scatola stagna IP65 150×110×70 con pressacavi (A6, A4, A2, Wago, resistenze), in alto sopra la bilancia | [B0F6YGYR7K](https://www.amazon.it/dp/B0F6YGYR7K) | 13,49 € | C |
| -R3 | 1 | Resistenza 4,7 kΩ (pull-up 1-Wire) | [B0FPX6T6SC](https://www.amazon.it/dp/B0FPX6T6SC) | 9,99 € | C/F |
| -R4, -R5 | 2 | Resistenze 10 kΩ (pull-up dei giri delle ventole) | negozio di elettronica | — | F |
| -R2 | 1 | Resistenza 120 Ω (terminazione RS485 lato camera, solo se la breakout non l'ha già) | negozio di elettronica | — | F |
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
| -M5, -M6 | 3 | **Ventole ARCTIC P12 Slim PWM PST** 120 mm, 12 V, 4 fili, 200–2100 giri/min (confezione da 3, una di scorta). PWM collegato direttamente alla scheda tramite il transistor Q1, giri letti dalla scheda | [B09RWTCXRR](https://www.amazon.it/dp/B09RWTCXRR) | 19,22 € | C |
| — | 1 | Prolunghe 4 pin PWM (6 pz), da tagliare per collegare le ventole in X4 senza toccarle | [B09SKYRB3V](https://www.amazon.it/dp/B09SKYRB3V) | 6,99 € | C |
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
| -W1 | 10 m | FROR 5G1,5, quadro → presa CEE stufa | [B01FSZYO08](https://www.amazon.it/dp/B01FSZYO08) | 28,59 € | C |
| -W2a, -W2b, -W7 | 25 m | FROR 3G1,5: spezzoni di ~1 m dal quadro alle prese XS1, XS2, XS3 e i due cavi allungati degli umidificatori (fino a ~10 m ciascuno, senza giunzioni in camera) | [B0DH3X2ZXS](https://www.amazon.it/dp/B0DH3X2ZXS) | 38,55 € | C |
| -W3, -W5, -W6 | 30 m | Cat6 FTP schermato, **rame pieno (non CCA)**, da tagliare: W3 quadro → X6 (~10 m: 12 V, 0 V, A, B), W5 X6 → X4 ventole (~2,5 m), W6 quadro → B5 cantina (~2 m); avanzo di scorta | [B0CGDQT3P4](https://www.amazon.it/dp/B0CGDQT3P4) | 27,99 € | C |
| -XS1, -XS2, -XS3 | 3 | Contenitore Electraline FIXA con presa, fuori dalla camera accanto al quadro (umidificatore 1, umidificatore 2, estrattore) | [B0G71348W7](https://www.amazon.it/dp/B0G71348W7) | 3 × 4,90 € | C |
| -XS4 | 1 | Presa CEE da parete 16 A 5 poli IP44 (stufa) | [B001BAVXZO](https://www.amazon.it/dp/B001BAVXZO) | 22,45 € | C |
| -XP4 | 1 | Spina CEE 16 A 5 poli (cavo stufa) | [B0002YZJDW](https://www.amazon.it/dp/B0002YZJDW) | 16,95 € | C |
| -X4 | 1 | Scatola IP65 150×110×70 con pressacavi (derivazione ventole; valvola anticondensa dalla confezione del quadro) | [B0F6YGYR7K](https://www.amazon.it/dp/B0F6YGYR7K) | 13,49 € | C |
| — | 1 | Kit 32 pressacavi M12–M25 (pannello botola, scatole) | [B0BFL3VQYQ](https://www.amazon.it/dp/B0BFL3VQYQ) | 10,24 € | C |
| — | 10 m | Tubo corrugato Ø 25, in due tratti (230 V e bassa tensione) | [B0FNKPP8DK](https://www.amazon.it/dp/B0FNKPP8DK) | 15,90 € | C |
| — | 1 | Filo in silicone 18 AWG (collegamenti interni alla stufa) | [B07TT68455](https://www.amazon.it/dp/B07TT68455) | da verificare | C |
| | | **Subtotale** | | **188,86 €** | |

## 5. Ferramenta e negozio di materiale elettrico

- Spina Schuko per il Vents TT-100.
- Resistenze 120 Ω e 10 kΩ (sezioni 1 e 1 bis): si serrano nei Wago, senza saldare.
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
| Quadro e logica (prezzi noti) | ≈ 412 € |
| Nodo in camera (prezzi noti) | ≈ 65 € |
| Sensori (senza B5) | 34,53 € |
| Attuatori e aria (con Vents TT-100) | 123,25 € |
| Cavi, prese e scatole (senza filo in silicone) | 188,86 € |
| **Totale con i prezzi noti** | **≈ 824 €** |
| + guide DIN, canaline, cavi 1,5 e 0,75 mm², sonda S-TH-01 B5, filo in silicone, ferramenta | da aggiungere |

Si possono togliere:
- RTC: −20 €;
- Wago e resistenza, se si prendono in negozio: −32 €;
- Airope al posto del Vents: −18 €.

## 7. Escluso per scelta (dalle liste precedenti)

- Termostato meccanico di sicurezza: scelta dell'utente, resta l'antiribaltamento della stufa.
- Salvavita nel quadro: la linea arriva già protetta dal quadro di casa (16 A + Id 30 mA).
- Contattori Finder: si usano gli HCH8s-25Z, uno per carico.
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

- Contattori: soppressione interna della bobina (se presente, niente diodi), larghezza effettiva in moduli.
- Waveshare: spessore con l'RTC innestato (dato Waveshare 40 mm) e posizione sulla guida 1.
- Ponticelli di terminazione 120 Ω: attivi solo sulla Waveshare e in X6 (breakout della XIAO o resistenza R2); spenti sugli altri.
- XIAO: come si collegano oggi HX711 e alimentazione alla breakout (stesso metodo per DS18B20, PWM e giri).
- Cat6: rame pieno, non CCA.
- Kit morsetti HERKINDNESS: quanti morsetti blu ci sono (servono 6 per N; se mancano, morsetti grigi con marcatore N).
- Cavo degli umidificatori: se si allunga con una giunzione, farla fuori dalla camera (o sostituire il cavo per intero); la spina si monta dopo aver passato il cavo nel pressacavo della botola.
- Vents TT-100: morsettiera e collegamento alla velocità bassa.
- Contatore SDM120 e B5: indirizzo Modbus (SDM120 a 2 e 9600 baud dai tasti frontali; B5 a 3), uno alla volta, da soli sul bus.
- Pico-RTC-DS3231: che il coperchio della scheda chiuda con il modulo innestato.
- B5: alimentazione a 12 V (range 3,6–30 V).
