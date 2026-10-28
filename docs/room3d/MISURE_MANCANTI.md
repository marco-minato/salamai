# Misure mancanti — camera salumi (room3d)

Dati che il modello 3D oggi **disegna con valori provvisori**. Quando una misura è disponibile si scrive nella colonna "Misurato". Poi si aggiorna il JSON indicato, con `"status": "measured"`, e si rigenera la build (`tools/room3d/build_all.sh`, vedi `README.md`).

Riferimento delle coordinate: origine nell'angolo **interno sinistro della parete porta**, guardando dentro la camera. **X** va lungo la parete porta verso destra, **Y** verso il fondo, **Z** è l'altezza da terra. Misure in metri o centimetri, basta indicarlo.

File: `room.json` = `model/room3d/room.json`; `L001` = `model/room3d/layouts/L001_progetto.json`.

Fonte: elenco `unknowns` e `assumptions` del manifest di L001, build `c08d7f70134af6a6cfe7`.

## Stanza e aperture

| # | Cosa | Provvisorio | Misurato | Dove si aggiorna |
|---|---|---|---|---|
| 1 | La distanza porta–botola di 40 cm è misurata fino al **bordo vicino** della botola o fino al **centro**? | bordo vicino (Y 0,40–0,85 m) | | `room.json` → `openings.hatch.offset_reference` |
| 2 | Altezza della luce della porta | 1,90 m | | `room.json` → `openings.door.height` |
| 3 | Verso di apertura della porta (dentro / fuori) | fuori | | `room.json` → `openings.door.swing` |
| 4 | Lato delle cerniere (sinistra X 1,04 / destra X 1,69) | destra | | `room.json` → `openings.door.hinge_side` |
| 5 | Spessore dell'anta | 4 cm | | `room.json` → `openings.door.leaf_thickness` |
| 6 | Spessore delle pareti | 10 cm | | `room.json` → `room.wall_thickness` |
| 7 | Spessore del pavimento | 10 cm | | `room.json` → `room.floor_thickness` |
| 8 | Spessore del soffitto | 10 cm | | `room.json` → `room.ceiling_thickness` |

## Stufa E1 e presa XS4

| # | Cosa | Provvisorio | Misurato | Dove si aggiorna |
|---|---|---|---|---|
| 9 | Stufa: larghezza (X) × profondità (Y) × altezza (Z) | 30 × 45 × 85 cm | | `L001` → `heater_e1.geometry.size` |
| 10 | Stufa: X del centro | 2,63 m | | `L001` → `heater_e1.geometry.center.x` |
| 11 | Stufa: altezza del centro (o della base da terra) | centro a 42,5 cm (appoggiata) | | `L001` → `heater_e1.geometry.center.z` |
| 12 | Presa XS4: Y e altezza | Y 1,12 m, Z 45 cm | | `L001` → `socket_xs4.geometry.center` |
| 13 | Presa XS4: dimensioni | 7 × 10 × 13 cm | | `L001` → `socket_xs4.geometry.size` |

## Umidificatori M2 e M3

| # | Cosa | Provvisorio | Misurato | Dove si aggiorna |
|---|---|---|---|---|
| 14 | M2: dimensioni | 25 × 25 × 30 cm | | `L001` → `humidifier_m2.geometry.size` |
| 15 | M2: posizione X, Y, altezza del centro | X 2,85 · Y 0,30 · Z 0,38 m | | `L001` → `humidifier_m2.geometry.center` |
| 16 | M3: dimensioni | 25 × 25 × 30 cm | | `L001` → `humidifier_m3.geometry.size` |
| 17 | M3: posizione X, Y, altezza del centro | X 2,85 · Y 1,30 · Z 0,38 m | | `L001` → `humidifier_m3.geometry.center` |
| 18 | Tubi della nebbia T2/T3: diametro esterno | 3,2 cm | | `L001` → `mist_tube_m2/m3.geometry.outer_diameter` |

## Estrattore, valvola, tubo e ingresso aria

| # | Cosa | Provvisorio | Misurato | Dove si aggiorna |
|---|---|---|---|---|
| 19 | Estrattore M4: diametro × lunghezza | 17 × 25 cm | | `L001` → `extractor_m4.geometry` |
| 20 | Estrattore M4: altezza del centro | 2,25 m | | `L001` → `extractor_m4.geometry.center.z` |
| 21 | Valvola antiritorno Y1: altezza del centro e lunghezza | 2,43 m · 10 cm | | `L001` → `check_valve_y1.geometry` |
| 22 | Tubo principale D1 Ø100: diametro esterno e raggio della curva sotto la botola | 10,5 cm · raggio 10 cm | | `L001` → `exhaust_duct_01.geometry` |
| 23 | Raccordo a T: X lungo la parete di fondo, distanza dalla parete, altezza, ingombro | X 1,365 (in linea con la botola) · asse a 10 cm dalla parete · Z 1,92 m · 22 × 12 × 12 cm | | `L001` → `duct_tee_01.geometry` e ultimo punto di `exhaust_duct_01` |
| 23a | Rami D2 e D3 Ø80: diametro esterno, altezza, posizione delle bocche (distanza dalle pareti, rivolte verso il muro o verso il basso) | 8,4 cm · Z 1,92 m · bocche orizzontali a 10 cm dalle pareti laterali | | `L001` → `exhaust_duct_02/03.geometry` |
| 24 | Griglia d'ingresso Y2 sulla porta: X, altezza da terra, spessore | X 1,365 · Z 0,15 m · 4 cm | | `L001` → `inlet_y2.geometry` |

## Ventole di ricircolo F1, F2, F3 e scatola X4

| # | Cosa | Provvisorio | Misurato | Dove si aggiorna |
|---|---|---|---|---|
| 25 | F1 (M5): Y, altezza, distanza dalla parete destra | Y 0,35 · Z 1,85 m · X 2,995 | | `L001` → `fan_01.geometry.center` |
| 26 | F2 (M6): Y, altezza, distanza dalla parete destra | Y 1,25 · Z 1,85 m · X 2,995 | | `L001` → `fan_02.geometry.center` |
| 27 | F3: Y, altezza, distanza dalla parete destra | Y 0,80 · Z 1,85 m · X 2,995 | | `L001` → `fan_03.geometry.center` |
| 28 | Diametro del rotore (tutte e tre) | 11 cm | | `L001` → `fan_0*.geometry.rotor_diameter` |
| 29 | Verso del soffio di ciascuna ventola | verso la parete opposta (−X) | | `L001` → `fan_0*.geometry` (orientamento) |
| 30 | Scatola di derivazione X4: Y e altezza | Y 0,575 · Z 1,85 m | | `L001` → `junction_box_x4.geometry.center` |

## Sonde e nodo

| # | Cosa | Provvisorio | Misurato | Dove si aggiorna |
|---|---|---|---|---|
| 31 | B1 (camera, S-TH-01): Y e diametro | Y 0,80 m · Ø 6 cm | | `L001` → `sensor_b1_sth01.geometry` |
| 32 | B3 (parete, DS18B20): X e altezza | X 2,50 · Z 0,30 m | | `L001` → `sensor_b3_wall.geometry.center` |
| 33 | B4 (pavimento, DS18B20): posizione finale X, Y (il punto più freddo trovato) | X 0,10 · Y 0,80 m | | `L001` → `sensor_b4_floor.geometry.center` |
| 34 | Cella di carico B2: Y, altezza, dimensioni | Y 0,10 · Z 1,55 m · 13 × 3 × 3 cm | | `L001` → `load_cell_b2.geometry` |
| 35 | Scatola nodo X6: altezza | 1,85 m | | `L001` → `node_box_x6.geometry.center.z` |
| 36 | B5 (cantina, fuori camera): posizione e diametro | X 0,85 · Y −0,20 · Z 0,15 m · Ø 6 cm | | `L001` → `sensor_b5_cantina.geometry` |

## Prodotto

| # | Cosa | Provvisorio | Misurato | Dove si aggiorna |
|---|---|---|---|---|
| 37 | Zona salami Z1: ingombro (X, Y), altezza minima e massima, tipo di supporto | segnaposto | | `L001` → `zone_salami` |
| 38 | Zona cacciatorini Z2: idem | segnaposto | | `L001` → `zone_cacciatorini` |
| 39 | Zona coppa, lonzino, guanciale Z3: idem | segnaposto | | `L001` → `zone_tagli_interi` |

## Non misurabili col metro (solo per completezza)

- Portata delle ventole e dell'estrattore: nel repository non c'è. PWM e giri **non** sono misure di portata.
- Coefficienti di perdita del tubo: non disponibili, il modello non ne inventa.
- Giri della terza ventola: il firmware ha solo due ingressi giri (M5, M6). È un limite del cablaggio, non una misura.

Basta un metro. Va bene anche una foto o uno schizzo quotato: la traduzione in coordinate la fa chi aggiorna il modello.
