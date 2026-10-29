# Salamai — Ridisegnare lo schema della scatola X6 con i cavetti C1, C2, C3

## Contesto

Progetto: camera di stagionatura salumi. La scatola **X6** (IP65, 150×110×70 mm) sta
dentro la camera e contiene:

- **A6**: XIAO ESP32C3 innestata sulla scheda Seeed XIAO RS485 Breakout. Sulla breakout
  ci sono due file di 7 pin maschi a passo 2,54 mm.
  - Fila sinistra, dal lato USB: D0, D1, D2, D3, D4, D5, D6.
  - Fila destra, dal lato USB: 5V, GND, 3V3, D10, D9, D8, D7.
- **A4**: HX711, con 4 pin in fila (GND, DT, SCK, VCC).
- **A2**: modulo MOSFET a morsetti a vite.
- Wago 221 per +12 V, 0 V, GND sensori, 3,3 V, 1-Wire, giri M5 e giri M6.
- Pressacavi per W3, B1, B3, B4, W5 e B2.

Lo schema è una pagina HTML interattiva. Le sue funzioni:

- clic su un filo o su una rete per evidenziarla;
- zoom e pan;
- livelli;
- legenda;
- checklist di montaggio con il pulsante "Mostra", che seleziona la rete.

Lo schema esiste anche come file `.drawio`.

## La modifica richiesta (il motivo di questo lavoro)

I collegamenti verso la XIAO e l'HX711 non si fanno più con cavetti Dupont sciolti. Si fanno
con **3 cavetti a 4 fili, ricavati da prolunghe 4 pin per ventole PC** tagliate a metà. I fili
sono tutti neri; quello con la riga è il n. 1. Sui capi verso la XIAO ci sono pin Dupont
femmina, in **due gusci 1×6**:

- **guscio sinistro** su D0–D5, con un tappo vuoto da 1 su D6;
- **guscio destro** su GND–D7, con un tappo vuoto da 1 sul 5V.

| Cavetto | Filo | Capo A | Capo B |
|---|---|---|---|
| **C1 HX711** (metà prolunga con il connettore femmina, innestato direttamente sui 4 pin dell'HX711) | GND | HX711 GND | Wago GND sensori |
| | DT | HX711 DT | XIAO D1 (guscio sinistro) |
| | SCK | HX711 SCK | XIAO D3 (guscio sinistro) |
| | VCC | HX711 VCC | Wago 3,3 V |
| **C2 sensori** | 1 | XIAO GND (guscio destro) | Wago GND sensori |
| | 2 | XIAO 3V3 (guscio destro) | Wago 3,3 V |
| | 3 | XIAO D10 (guscio destro) | Wago 1-Wire |
| | 4 | di riserva, isolato | — |
| **C3 ventole** | 1 | XIAO D0 (guscio sinistro) | Wago giri M5 |
| | 2 | XIAO D8 (guscio destro) | Wago giri M6 |
| | 3 | XIAO D7 (guscio destro) | MOSFET morsetto PWM |
| | 4 | di riserva, isolato | — |

**Problema:** nella versione attuale (`anteprima-attuale.png`, `scatola-x6.html`) i cavetti
sono disegnati come fasce grigie sotto i singoli fili. Si sovrappongono ai fili sciolti e non
si capisce quale filo appartiene a quale cavetto. Per l'utente il disegno "non si capisce".

**Obiettivo:** a colpo d'occhio deve essere chiaro:

1. che dalla XIAO escono **3 cavetti** (più l'HX711 collegato con C1);
2. dove ogni cavetto si apre;
3. quale filo di ogni cavetto va a quale pin, Wago o morsetto.

Il modo lo decidi tu. Alcune idee:

- un **cavo unico** (tratto spesso) per ciascun cavetto, dal guscio fino a un punto di
  apertura vicino alle destinazioni, con i singoli fili colorati solo nell'ultimo tratto,
  come in uno schema di cablaggio (harness);
- lo stesso stile già usato per i cavi Cat5e: fascia da pressacavo a punto di apertura
  `splits`;
- un riquadro di dettaglio dei due gusci 1×6, con il numero del foro e il cavetto·filo;
- un riquadro con la tabella dei cavetti.

## File (cartella `documentazione/sorgenti/x6/`)

| File | Cosa contiene |
|---|---|
| `gen_x6.py` | Generatore attuale, con le fasce grigie. Disegna le schede in scala (mm), i Wago in fila, gli instradamenti a corsie (`route`, `lane`) e i cavi (`CHAN`, `cab_start`); la funzione `band()` disegna le fasce dei cavetti. Calcola le reti con union-find sui nomi dei capi. |
| `gen_x6.prima-dei-cavetti.py` | Generatore prima di questa modifica, utile per confronto. |
| `page_x6_tpl.html` | Modello della pagina interattiva. Al posto di `__DATA__` va il contenuto di `x6.json`. Contiene la legenda, le note (`<li>`) e la checklist (`STEPS`, ogni passo `[testo, nome rete opzionale]`). |
| `x6.json` | Dati generati: `V` (rettangoli e testi), `wires` (kind, pts, a, b, net), `nets`, `splits`. |
| `render.py` | Anteprima PNG senza testi, per controllare la geometria. |
| `build.sh` | Rigenera `documentazione/scatola-x6.drawio`, `documentazione/scatola-x6.html` e `anteprima.png`. |
| `anteprima.png` | Anteprima della versione da migliorare. |

Costruzione, dalla radice del repo:

```
sh documentazione/sorgenti/x6/build.sh
```

Non modificare a mano `documentazione/scatola-x6.html` e `.drawio`: si rigenerano dal
generatore e dal modello.

## Vincoli

- **Non cambiare i collegamenti elettrici.** Le reti devono restare le stesse 17, con gli
  stessi capi; ogni rete elenca i suoi capi. Puoi aggiungere capi per i punti di apertura dei
  cavetti, purché siano chiari.
- **Nomi dei capi:** restano quelli attuali, ad esempio "XIAO D7 (pin)", "HX711 DT",
  "Wago GND sensori foro 1". La checklist usa i **nomi delle reti** per il pulsante
  "Mostra": se cambi un nome, aggiorna anche `STEPS`.
- **Funzioni della pagina da conservare:**
  - selezione di una rete con il clic e attenuazione di tutto il resto;
  - zoom e pan;
  - livelli;
  - legenda;
  - checklist con il salvataggio in `localStorage` (chiave `x6-salumi-montaggio`).
- **Stili da conservare:**
  - colori delle reti;
  - fili GND tratteggiati;
  - testi in italiano semplice, rivolti a un utente non elettricista.
- **Disegno pulito:**
  - nessun filo sovrapposto a un altro;
  - nessun testo sopra un filo o una scheda;
  - incroci ridotti al minimo.
- **Telefono:** la pagina deve restare leggibile, con larghezza minima 360 px e zoom.
- **Misure delle schede e dei gusci:** in scala, in mm, passo 2,54. I Wago possono restare
  disegnati in fila.
- **Coerenza tra i file:** `.drawio` e `.html` devono restare allineati.
- **Note e checklist:** aggiornale solo se il nuovo disegno lo richiede. Il contenuto tecnico
  resta quello della tabella sopra.

## Controlli prima di consegnare

1. Lo script del generatore stampa le reti: devono essere 17, con gli stessi capi di
   `x6.json` attuale. Unica eccezione ammessa: eventuali capi nuovi dei punti di apertura.
2. Il JavaScript estratto dalla pagina deve passare `node --check`.
3. Tutti i nomi di rete usati in `STEPS` devono esistere in `nets`.
4. Controlla l'anteprima PNG (`render.py`) e, se puoi, uno screenshot della pagina.
5. Lavora sul ramo `x6-cavetti`. Fai commit di generatore, modello, `x6.json`,
   `anteprima.png` e dei due file rigenerati in `documentazione/`. Nella pull request scrivi
   in poche righe come hai rappresentato i cavetti.
6. Non toccare gli altri file del repo: quadro, distinta, prompt, firmware.
