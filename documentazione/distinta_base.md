# Camera salumi — distinta base definitiva

Versione 3 del 18/10/2026 (ventole PWM a 12 V, tutto su guida DIN, nessuna saldatura). Le sigle sono quelle dello schema
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
| -A2 | 1 | Modulo MOSFET dual a morsetti (10 pz), sul filo PWM delle ventole: protegge la scheda, nessuna saldatura | [B0GL1NWZQH](https://www.amazon.it/dp/B0GL1NWZQH) | 8,99 € | C |
| -X5 | 1 | Basetta a morsetti Freenove per Raspberry Pi Pico, su guida DIN con le clip: un morsetto a vite etichettato per ogni pin, LED di stato | [B0BFB53Y2N](https://www.amazon.it/dp/B0BFB53Y2N) | 14,95 € | C |
| — | 1 | Cavetti Dupont (kit 120 pz, con maschio-maschio): dalle prese sopra l'RTC alle prese della basetta X5, nessun taglio | [B01N40EK6M](https://www.amazon.it/dp/B01N40EK6M) | 9,99 € | C |
| — | 1 | Quadro IP65 Intratec 48 moduli, 4 file, sportello trasparente | [B08614GVLN](https://www.amazon.it/dp/B08614GVLN) | 69,69 € | C |
| — | 1 | Clip DIN per circuiti stampati (modulo MOSFET A2, basetta X5) | [B0FCM3N3P9](https://www.amazon.it/dp/B0FCM3N3P9) (20 pz) | 8,99 € | C |
| — | 1 | Pressacavi M20 IP68 (quadro) | [B0GYRDCC9Z](https://www.amazon.it/dp/B0GYRDCC9Z) (26 pz) | 7,99 € | C |
| -X2… | 1 | Morsetti Wago 221 assortiti (2, 3, 5 vie) | [B06XRJHTS3](https://www.amazon.it/dp/B06XRJHTS3) (40 pz) | 21,96 € | C/F |
| — | 1 | Resistenza 4,7 kΩ (pull-up 1-Wire) | [B0FPX6T6SC](https://www.amazon.it/dp/B0FPX6T6SC) | 9,99 € | C/F |
| | | **Subtotale** | | **360,05 €** | |

## 2. Sensori

| Sigla | Q.tà | Componente | Codice / link | Prezzo | Stato |
|---|---:|---|---|---:|:-:|
| -B1 | 1 | Sonda Seeed S-TH-01 T/UR RS485, **camera**, indirizzo 1 | Seeed 101990881 | — | P (oggi sulla XIAO) |
| -B5 | 1 | Sonda Seeed S-TH-01, **cantina**, indirizzo 3 (stesso modello di B1, per avere una differenza di umidità affidabile) | Seeed 101990881, stesso canale d'acquisto della prima | da verificare | **C** |
| -B3, -B4 | 2 | DS18B20 impermeabile, cavo 3 m: **parete** e **pavimento** | [B07CZ1G29V](https://www.amazon.it/dp/B07CZ1G29V) (2 pz) | 18,26 € | C |
| -A4, -B2 | 1 | HX711 + cella di carico 2 kg | — | — | P (oggi sulla XIAO, da calibrare) |
| — | 1 | Scatolina IP65 per HX711 e derivazione delle DS18B20 | [B0F8NW1YZ2](https://www.amazon.it/dp/B0F8NW1YZ2) | 8,59 € | C |
| — | 1 | Termometro a infrarossi (test di preriscaldo: pavimento, angoli, pareti) | [TempPro TP30, B0BGGJH3G2](https://www.amazon.it/dp/B0BGGJH3G2) | 16,27 € | C |
| | | **Subtotale** (senza B5) | | **43,12 €** | |

La XIAO ESP32-C3 con la scheda RS485 resta di scorta dopo la migrazione.
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
| -W2 | 10 m | FROR 4G1,5, quadro → prese umidificatori | [B01FSZYK4I](https://www.amazon.it/dp/B01FSZYK4I) | 24,01 € | C |
| -W3, -W4, -W5 | 30 m | Cat6 FTP schermato, da tagliare: W3 sonda B1, W4 HX711 + B3 + B4, W5 ventole (12 V, PWM, giri), avanzo per B5 in cantina | [B0CGDQT3P4](https://www.amazon.it/dp/B0CGDQT3P4) | 27,99 € | C |
| -X1 | 1 | Presa doppia IP55 Schuko/bipasso con coperchio (umidificatori) | [B0HJD4BD28](https://www.amazon.it/dp/B0HJD4BD28) | 16,99 € | C |
| -XS3 | 1 | Contenitore Electraline FIXA con presa (estrattore, fuori dalla camera) | [B0G71348W7](https://www.amazon.it/dp/B0G71348W7) | 4,90 € | C |
| -XS4 | 1 | Presa CEE da parete 16 A 5 poli IP44 (stufa) | [B001BAVXZO](https://www.amazon.it/dp/B001BAVXZO) | 22,45 € | C |
| -XP4 | 1 | Spina CEE 16 A 5 poli (cavo stufa) | [B0002YZJDW](https://www.amazon.it/dp/B0002YZJDW) | 16,95 € | C |
| -X4 | 1 | Scatola IP65 150×110×70 con pressacavi (derivazione ventole) | [B0F6YGYR7K](https://www.amazon.it/dp/B0F6YGYR7K) | 13,49 € | C |
| — | 1 | Kit 32 pressacavi M12–M25 (pannello botola, scatole) | [B0BFL3VQYQ](https://www.amazon.it/dp/B0BFL3VQYQ) | 10,24 € | C |
| — | 10 m | Tubo corrugato Ø 25, in due tratti (230 V e bassa tensione) | [B0FNKPP8DK](https://www.amazon.it/dp/B0FNKPP8DK) | 15,90 € | C |
| — | 1 | Filo in silicone 18 AWG (collegamenti interni alla stufa) | [B07TT68455](https://www.amazon.it/dp/B07TT68455) | da verificare | C |
| | | **Subtotale** | | **181,51 €** | |

## 5. Ferramenta e negozio di materiale elettrico

- Spina Schuko per il Vents TT-100.
- 2 resistenze 10 kΩ (pull-up dei giri delle ventole, solo se quelli interni della scheda non bastano): si serrano nei morsetti, senza saldare.
- Pannello per chiudere la botola: multistrato 10 mm o PVC espanso, con un foro Ø 100 per l'estrattore e i fori per i pressacavi.
- Foro Ø 100 nella porta della camera, in basso, per la griglia d'ingresso.
- Apertura fissa in alto sulla porta esterna della cantina: griglia o feritoia.
- Clip fermacavo, fascette, puntalini.
- Silicone neutro o nastro di alluminio per fissare B3 e B4 alle piastrelle.

## 6. Totale

| Gruppo | Importo |
|---|---:|
| Quadro e logica | 360,05 € |
| Sensori (senza B5) | 43,12 € |
| Attuatori e aria (con Vents TT-100) | 123,25 € |
| Cavi, prese e scatole (senza filo in silicone) | 181,51 € |
| **Totale Amazon** | **≈ 708 €** |
| + sonda S-TH-01 B5, filo in silicone, ferramenta | da aggiungere |

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
- PZEM-016 e modulo RTC sciolto: non si fissano alla guida DIN; sostituiti dal contatore SDM120 e dal Pico-RTC-DS3231. Niente saldature sulle schede: i segnali passano dal connettore Pico con cavetti Dupont fino alla basetta a morsetti X5 su guida DIN.
- Ventole ELUTENG USB 5 V con DC-DC e modulo MOSFET: sostituite dalle ventole PWM 12 V (velocità minima più bassa e stabile, lettura dei giri). Le ELUTENG restano libere.
- Serrande motorizzate: i relè sono tutti usati, bastano Y1 e la griglia con valvola.

## 8. Da verificare all'arrivo

- Contattori: soppressione interna della bobina (se presente, niente diodi), larghezza effettiva in moduli.
- Waveshare: profondità e posizione sulla fila 3.
- Vents TT-100: morsettiera e collegamento alla velocità bassa.
- Contatore SDM120 e B5: indirizzo Modbus (SDM120 a 2 e 9600 baud dai tasti frontali; B5 a 3), uno alla volta, da soli sul bus.
- Pico-RTC-DS3231: che il coperchio della scheda chiuda con il modulo e i cavetti Dupont innestati.
- B5: alimentazione a 12 V (range 3,6–30 V).
