# Assunzioni, dati sconosciuti e conflitti — room3d

Nessuna quota sconosciuta è presentata come reale.

- Nei JSON ogni dato ha uno stato. Gli `unknown` hanno `value: null` e un `draw_value` usato solo per disegnare.
- Nei PNG questi dati sono in **arancio** con `[A]`; i segnaposto hanno `[P]`.
- Nel visualizzatore hanno badge arancio o rosso.

L'elenco completo e aggiornato a ogni build è in `manifest.json` → `unknowns`.

## Indice

- [Misure dichiarate (base del modello)](#misure-dichiarate-base-del-modello)
- [Assunzioni sulla stanza (`room.json`)](#assunzioni-sulla-stanza-roomjson)
- [Conflitti fra le fonti](#conflitti-fra-le-fonti)
- [Assunzioni sul layout L001](#assunzioni-sul-layout-l001)
- [Collegamenti agli ID reali non risolti](#collegamenti-agli-id-reali-non-risolti)
- [Rilievo da fare, in ordine di utilità](#rilievo-da-fare-in-ordine-di-utilità)

## Misure dichiarate (base del modello)

| Dato | Valore | Fonte |
|---|---|---|
| X interno | 3,03 m = 1,04 + 0,65 + 1,34 | schizzo |
| Y interno | 1,60 m | schizzo |
| Z interno | 2,10 m | schizzo ("ALTEZZA 210") |
| Porta | X 1,04–1,69 m, centro 1,365, sulla parete Y=0 | schizzo |
| Botola | 0,32 m (X) × 0,45 m (Y), centrata sulla porta in X | schizzo + utente |
| Distanza porta–botola | 0,40 m | utente |
| Volume lordo | 10,1808 m³, derivato. **Non** è il volume libero | — |

Le misure in pixel dello schizzo non sono usate. Lo schizzo è archiviato in `model/room3d/sources/` con il suo SHA256.

## Assunzioni sulla stanza (`room.json`)

| ID | Assunzione | Effetto | Alternativa |
|---|---|---|---|
| `a01_hatch_offset_reference` | **ASSUNZIONE NON CONFERMATA.** I 40 cm vanno dalla faccia interna della parete porta al **bordo più vicino** della botola: Y 0,40–0,85 m, centro Y 0,625 | foro nel soffitto, estrattore, valvola, attacco del tubo | se riferiti al **centro**: Y 0,175–0,625. Cambiare `offset_reference` in `center` (testato) |
| `a02_door_height` | Altezza della porta sconosciuta; disegnata a 1,90 m | foro nella parete porta, anta | — |
| `a03_thickness` | Spessori di pareti, soffitto e pavimento sconosciuti; disegnati a 10 cm **all'esterno** del volume interno | solo grafica: le quote interne non cambiano | — |
| `a04_door_swing` | Verso di apertura e cerniera non confermati. Anta disegnata aperta di 90° verso l'esterno, con cerniera sul lato X=1,69 | anta (esterna, classificata) | vedi conflitto C1 |

## Conflitti fra le fonti

| # | Conflitto | Scelta nel modello |
|---|---|---|
| C1 | Verso della porta: lo schizzo sembra mostrare apertura **verso l'esterno**; `prompt_schema_qelectrotech.md:417` dice "apre verso l'**interno**" | `unknown`, disegnata verso l'esterno solo come interpretazione grafica |
| C2 | Numero di ventole: la distinta (`distinta_base.md:70`) ne compra 3 ma ne siglia 2 (M5, M6) più una di scorta; il firmware legge i giri di **due** sole; l'utente dichiara **tre** ventole di ricircolo | tre ventole (`fan_01..03`), separate dall'estrattore. `fan_03` non ha lettura dei giri (`unresolved` in `mapping.json`) |
| C3 | Estrattore: `strategia_processo.md:306-309` lo dà come non deciso, mentre la distinta indica il modello (Vents TT-100) | si usa la distinta, che è più recente; posizione nella botola |
| C4 | Zona salami: `prompt_schema_qelectrotech.md:419` parla di ~130 × 150 cm, ma le regole di carico (15–20 cm dalle pareti, niente sopra la stufa) riducono l'ingombro | zona segnaposto 1,08 × 1,20 × 1,40 m, marcata `placeholder` |

## Assunzioni sul layout L001

| ID | Assunzione |
|---|---|
| `l001_fan_layout` | Tre ventole in alto sulla parete destra (X≈3,00), a Y 0,35 / 0,80 / 1,25 e Z 1,85, che soffiano verso −X. Distribuzione, quota e orientamento **da studiare**. Le frecce indicano la direzione **nominale, non simulata** |
| `l001_duct_corner` | **Percorso dichiarato dall'utente (28/10/2026, `src_user_20261028`):** Ø100 dalla botola verso la parete lunga di fondo; lì un T (`duct_tee_01`) divide in due rami Ø80 (`exhaust_duct_02`, `exhaust_duct_03`) che arrivano agli angoli in fondo a sinistra e a destra; bocche **in alto**. **Assunti:** quota dei tubi 1,92 m, asse a 10 cm dalla parete di fondo, T in linea con la botola (X 1,365), bocche orizzontali a 10 cm dalle pareti laterali, ingombro del T, raggio della curva sotto la botola (10 cm). Lunghezze dell'asse disegnato nel manifest: circa 1,0 m di Ø100 e 1,27 m + 1,57 m di Ø80. Tubi Ø80 e T non sono in distinta. Sostituisce la versione precedente (unico tubo con bocca in basso a 0,50 m nell'angolo in fondo a sinistra) |
| `l001_equipment_sizes` | Ingombri di stufa, umidificatori, estrattore, valvola, prese e tubi nebbia non documentati: forme provvisorie |
| `l001_product_zones` | Zone prodotto provvisorie (salami, cacciatorini, tagli interi). Mancano strutture, altezze e ingombri reali |
| `l001_sensor_positions` | Sonde descritte solo a parole: B1 a X 2,03 (≥ 1 m dalla parete destra, derivato) e Z 1,20 (dichiarato); le altre coordinate sono provvisorie |

Carico e rimozioni si registrano come eventi del ciclo. Il modello **non** assume che la zona sinistra si svuoti dopo 3 giorni: la permanenza dei cacciatorini non è specificata. Questa è una descrizione del processo dell'utente, non una validazione del trattamento.

## Collegamenti agli ID reali non risolti

Sono in `model/room3d/mapping.json`:

- Giri della terza ventola: il firmware ha solo due ingressi.
- Quale umidificatore (M2, M3 o entrambi) comanda oggi il canale `switch.sonoff_1001f24fe4_1`.
- Corrispondenza CH4/CH5 ↔ M2/M3 nel nuovo firmware.
- Sonda cantina B5: indirizzo Modbus 3, commentata nel firmware.
- Entità `salumi-camera` / `salumi-nodo`: derivate dalle regole ESPHome, non ancora presenti in Home Assistant.
- `sensor.cantina_sonda_th_peso`: prefisso anomalo, forse rinominato.
- `switch.salumi_aspiratore`: citato in `salumi_log.py` ma inesistente.

## Rilievo da fare, in ordine di utilità

1. Distanza porta–botola: bordo vicino o centro (`a01`). Basta un metro.
2. Altezza della porta, lato cerniera, verso di apertura; posizione e altezza della griglia Y2 sull'anta.
3. Posizione, quota e orientamento delle tre ventole, e il loro supporto.
4. Tubo di aspirazione: posizione del T sulla parete di fondo, quota dei tubi e delle bocche, distanza delle bocche dalle pareti, diametri esterni, raggio della curva sotto la botola.
5. Ingombri reali di stufa (con distanza dal muro), umidificatori (con rialzo), estrattore e valvola.
6. Posizione di B1, B3, B4, B5, della cella di carico e delle scatole X4/X6.
7. Struttura in legno di appensione: ingombri, altezze, file.
8. Spessori di pareti e soffitto, solo se servono per forature o passaggi.
