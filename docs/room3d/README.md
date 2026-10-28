# Modello 3D della camera — room3d

Modello tecnico parametrico della camera di asciugatura salumi. Il modello si
genera con Blender da file JSON e si consulta con un visualizzatore web in sola
lettura. Serve a progettare tubazioni e ventole e a mettere in relazione la
disposizione fisica con lo storico dei cicli.

**La fonte autorevole è il JSON.** Il `.blend`, il `.glb`, il manifest e le
immagini sono derivati: si rigenerano e non vanno modificati a mano.

## Indice

- [Contenuto](#contenuto)
- [Frame e unità](#frame-e-unità)
- [Versioni usate](#versioni-usate)
- [Comando unico](#comando-unico)
- [Output della build](#output-della-build)
- [Visualizzatore web](#visualizzatore-web)
- [Come modificare il modello (anche tramite AI)](#come-modificare-il-modello-anche-tramite-ai)
- [Collegamento ai cicli](#collegamento-ai-cicli)
- [Verifiche](#verifiche)
- [Misure ancora necessarie](#misure-ancora-necessarie)

## Contenuto

| Percorso | Cosa contiene |
|---|---|
| `model/room3d/room.json` | Stanza, aperture, fonti e assunzioni (fonte autorevole) |
| `model/room3d/layouts/` | Catalogo dei layout e componenti. `L001` è il layout reale pianificato; `L900_DEMO` è un'**ipotesi dimostrativa** |
| `model/room3d/room.schema.json` | Schema JSON (documentazione e interoperabilità). Il validatore autorevole è `validate_config.py` |
| `model/room3d/mapping.json` | Collegamento fra componenti e ID reali (Home Assistant, ESPHome, Modbus, colonne CSV) |
| `model/room3d/cycles/` | Contratto ciclo ↔ layout (`cycle.schema.json`) ed esempio con dati **sintetici** |
| `model/room3d/sources/` | Schizzo originale quotato, con SHA256 registrato in `room.json` |
| `tools/room3d/room3d_core.py` | Nucleo in Python puro: validazione, geometria, hash |
| `tools/room3d/validate_config.py` | Validazione da riga di comando |
| `tools/room3d/build_scene.py` | Generatore Blender headless |
| `tools/room3d/export_analysis.py` | Pacchetto di analisi per le AI (ciclo + layout valido + dati) |
| `tools/room3d/make_synthetic_cycle.py` | Rigenera il ciclo d'esempio sintetico |
| `tools/room3d/build_all.sh` | Comando unico che ricostruisce tutto |
| `tools/room3d/tests/` | Test unitari e di integrazione con Blender |
| `web/room3d-viewer/` | Visualizzatore Three.js, con configurazione Nginx/Docker |
| `docs/room3d/ASSUMPTIONS.md` | Assunzioni, dati sconosciuti, conflitti fra le fonti |
| `docs/room3d/REVIEW.md` | Revisione indipendente di Codex |

## Frame e unità

- **Unità.** I dati sono in metri. Le quote si mostrano in centimetri, con la virgola decimale.
- **Sistema di riferimento.** Destrorso, Z verso l'alto.
  - Origine: sul pavimento, nell'angolo sinistro della parete con la porta (faccia interna, come nella pianta).
  - X: verso destra lungo la parete della porta.
  - Y: verso la parete opposta.
  - Z: verso il soffitto.
- **glTF.** Il formato è Y-up: il punto canonico `(x, y, z)` diventa `(x, z, -y)`. La matrice è nel manifest (`gltf.gltf_to_canonical`). Il visualizzatore la usa per oggetti, quote, misure e selezione. I test verificano orientamento e scala del GLB esportato.
- **Provenienza dei dati.** Ogni dato ha uno stato: `measured`, `declared`, `derived`, `assumed` o `unknown`. Un dato `unknown` ha `value: null`; per disegnarlo si usa `draw_value`, che resta un valore provvisorio e non diventa mai un dato reale.

## Versioni usate

| Componente | Versione |
|---|---|
| Blender | 5.2.3 LTS, tarball ufficiale; Python incluso 3.13 |
| Motori di render | Workbench (default) oppure Cycles su CPU (`--engine cycles`), senza bisogno di GPU |
| Node.js | 24.14 (minimo 20) |
| three | 0.186.1 |
| vite | 8.3.4 |
| playwright-core | 1.64.0, solo per i test; usa Chrome di sistema |
| Nginx (Docker) | `nginx:1.30.5-alpine` |
| Python di sistema | 3.14, nessuna dipendenza esterna |

Le dipendenze web sono fissate in `package.json` e `package-lock.json`. Nessuna risorsa viene caricata da CDN.

## Comando unico

Dalla radice del repository:

```bash
tools/room3d/build_all.sh
```

Il comando esegue, in ordine:

1. validazione;
2. scena Blender: `.blend`, `.glb`, manifest e 4 PNG per ogni layout;
3. pacchetto di analisi d'esempio;
4. test;
5. visualizzatore web (`dist/`).

Variabili utili:

- `BLENDER=/percorso/blender`
- `ENGINE=cycles`
- `SKIP_TESTS=1`
- `SKIP_WEB=1`

Solo la scena, con il comando previsto dalle specifiche:

```bash
blender --background --factory-startup --python-exit-code 1 \
  --python tools/room3d/build_scene.py -- --config model/room3d/room.json --output build/room3d
```

Opzioni dopo `--`:

- `--layout L001`: costruisce un solo layout;
- `--engine cycles`;
- `--no-render`: salta i PNG;
- `--resolution 2400`.

Se la configurazione non è valida o la build fallisce, il comando stampa l'elenco degli errori con il percorso JSON ed esce con un codice diverso da zero.

Per la sola validazione, senza Blender:

```bash
python3 tools/room3d/validate_config.py
```

## Output della build

La build scrive in `build/room3d/`, che non è versionata:

```text
build/room3d/
  catalog.json                       # layout costruiti, con hash e percorsi
  layouts/<layout_id>/<config_hash[:12]>/
    model.blend   model.glb   manifest.json
    views/pianta.png  sezione_A_x.png  sezione_B_y.png  assonometria_aperta.png
  analysis/<cycle_id>/              # pacchetti di analisi
```

- **Percorsi immutabili.** Ogni percorso contiene l'hash della configurazione. A una revisione corrisponde sempre lo stesso percorso, quindi il browser e i cicli non possono mescolare file di revisioni diverse.
- **Manifest.** Per ogni entità riporta ID stabile, layer, stato, provenienza, centro, ingombro e orientamento nel frame canonico, oltre all'hash semantico. Contiene anche aperture, quote, assunzioni, dati sconosciuti, fonti e lo SHA256 del GLB.
- **Nodi glTF.** Hanno lo stesso nome degli ID e portano negli `extras` `salamai_id`, layer, stato e provenienza. La scena glTF porta `salamai_build_id`.
- **Riproducibilità.** Due build della stessa configurazione hanno gli stessi ID, `config_hash`, `semantic_hash` e `build_id`. I file `.blend` non sono identici byte per byte, e non è richiesto.

## Visualizzatore web

Il visualizzatore è solo per consultazione e analisi: non modifica la geometria, non scrive nei sorgenti e non comanda dispositivi. Visibilità, camera, trasparenza e misure valgono solo per la sessione nel browser.

```bash
cd web/room3d-viewer
npm ci
npm run build        # copia build/room3d (senza .blend) in public/data e crea dist/
npm run check        # verifica di sola lettura su sorgenti e bundle
npm run preview      # http://127.0.0.1:4173/
```

**Funzioni:**

- rotazione, zoom e spostamento con mouse e touch;
- viste dall'alto, fronte, lato e assonometrica, più ripristino dell'inquadratura;
- layer attivabili uno per uno;
- ogni elemento di struttura (pavimento, soffitto, pareti) visibile, trasparente o nascosto. Le parti trasparenti non intercettano la selezione;
- pannello del componente con ID, coordinate canoniche, dimensioni, orientamento, caratteristiche e provenienza. Assunzioni e segnaposto sono evidenziati;
- quote;
- misura della distanza rettilinea 3D, con aggancio ai vertici. È distinta dalla lunghezza delle tubazioni;
- confronto fra due layout con camera sincronizzata e lista di elementi aggiunti, rimossi, spostati e modificati;
- messaggi di errore per file mancanti o incompatibili e per WebGL assente.

**Pubblicazione.** Il build usa percorsi relativi, quindi funziona in qualunque sottopercorso. La configurazione Nginx in Docker è pronta ma **non distribuita**:

```bash
cd web/room3d-viewer
npm run build
docker build -f deploy/Dockerfile -t salamai-room3d-viewer .                      # sottopercorso /salamai/room3d
docker build -f deploy/Dockerfile --build-arg SUBPATH=/x/y -t salamai-room3d-viewer .  # altro sottopercorso
docker run --rm -p 127.0.0.1:8088:8080 salamai-room3d-viewer
# http://127.0.0.1:8088/salamai/room3d/
```

Nginx si comporta così:

- accetta solo GET e HEAD; gli altri metodi ricevono 405;
- invia una Content-Security-Policy restrittiva;
- serve i file di revisione con cache `immutable` e `catalog.json` con `no-cache`.

Un server statico qualsiasi va bene: il visualizzatore non richiede Blender, MCP né servizi AI.

## Come modificare il modello (anche tramite AI)

**Percorso obbligato:**

1. Richiesta all'AI.
2. Modifica del JSON (o degli script).
3. `validate_config.py` e test.
4. Revisione.
5. `build_all.sh`, che rigenera GLB, manifest e viste.
6. Aggiornamento dei file serviti dal web.

> Le modifiche fatte a mano in Blender, anche via MCP, **non sono riportate nel JSON e si perdono alla rigenerazione**. Non è implementata un'esportazione Blender → JSON. MCP si può usare per esplorare o provare una posizione; poi la modifica va scritta nel JSON.

**Spostare un componente.** Nel layout cambiare la coordinata e il suo stato. Esempio: ventola 1 alzata a 1,90 m e misurata con il metro:

```json
"z": {"value": 1.90, "status": "measured", "source": "src_rilievo_2026_11", "note": "misurata al centro del telaio"}
```

Una misura `measured` richiede una fonte in `room.json` → `sources`, per esempio un rilievo con data. Se il dato non è misurato, usare `assumed` con una nota, oppure `unknown` con `draw_value`.

**Aggiungere una ventola.** Copiare un componente `fan_0N` con un nuovo `id` (minuscolo, univoco) e un nuovo `tag`. Poi impostare:

- `center`;
- `axis`, un versore: è il verso nominale dell'aria;
- `layer: "ricircolo"`;
- `state` (`planned` oppure `installed`).

Se esiste un ingresso giri, aggiungere il collegamento in `mapping.json`. Il validatore rifiuta:

- ID duplicati;
- assi nulli o non normalizzati;
- elementi fuori dalla stanza senza `placement` e motivazione.

**Cambiare il percorso di una tubazione.** Modificare `geometry.points` (assi, almeno 2 punti) e `bend_radius`, che è obbligatorio quando ci sono curve. Tratti, curve e lunghezza nel manifest si ricalcolano dalla geometria. Una curva che non sta nel tratto disponibile è un errore. Non vanno inseriti coefficienti di perdita.

**Cambiare un layer.** Impostare `layer` su uno degli ID in `room3d_core.LAYERS`.

**Nuova revisione di un layout già usato da cicli registrati.** Non modificare il file del layout, ma crearne uno nuovo:

- nuovo `layout_id`, per esempio `L002`, con `derived_from: "L001"`;
- aggiungerlo a `layouts/catalog.json`.

Così i cicli precedenti restano associati alla revisione che avevano.

**Rendere reale il disegno.** Quando una misura viene rilevata, sostituire `unknown` o `assumed` con `measured` più la fonte. Le etichette `[A]` nei PNG e gli avvisi nel visualizzatore si aggiornano da soli.

## Collegamento ai cicli

- **ID del ciclo.** L'unico identificativo esistente è il nome della cartella di archivio `/share/salumi/<YYYY-MM-DD_HHMM>/` (vedi `homeassistant/salumi.yaml`), che contiene `letture.csv`.
- **`cycle.json`.** Accanto al CSV va un file `cycle.json` (vedi `model/room3d/cycles/cycle.schema.json`) con:
  - `layout_refs`: `layout_id`, `config_hash` (dal manifest o da `catalog.json`), `source_commit` e intervallo di validità. Se la disposizione cambia durante il ciclo, si aggiunge un nuovo intervallo;
  - `events`: carico, rimozioni, cambi di layout e note, con timestamp. Una rimozione non vuol dire che la zona è vuota.
- **`mapping.json`.** Collega componenti e colonne CSV agli ID reali, con questi stati:
  - `in_use`: oggi usato nel repository;
  - `derived_unverified`: ricavato per il nuovo firmware, non verificato;
  - `unresolved`: nessun ID reale. Esempi: giri della terza ventola, quale umidificatore comanda il canale attuale.

Generare il pacchetto di analisi:

```bash
python3 tools/room3d/export_analysis.py --cycle <cartella_ciclo> [--at 2026-01-11T12:00:00]
```

- **Scelta del layout.** Lo script usa la revisione registrata nel ciclo. Se nella build non c'è, esce con codice 2: **non applica mai il layout corrente ai cicli storici**.
- **Conservare le revisioni.** Per interpretare cicli passati si possono archiviare le cartelle `build/room3d/layouts/<id>/<hash>/`, che sono immutabili. In alternativa si rigenerano dal `source_commit`.
- **Contenuto del pacchetto.** Il pacchetto (`package.json` più `README.md` testuale) riporta:
  - geometria, layout, unità e immagini;
  - copertura e qualità delle misure, lacune e aggregati per fase;
  - eventi e carico;
  - punti misurati, zone **non osservate** e osservazioni.

  Inferenze e ipotesi sono sezioni separate e vuote finché qualcuno non le scrive con il metodo usato.
- **Limiti.** Il pacchetto non interpola nello spazio, non costruisce campi di velocità e non trae conclusioni di sicurezza alimentare.
- **Esempio.** `model/room3d/cycles/examples/SINTETICO_2026-01-10_0800/` contiene **dati sintetici**: lo dicono il nome della cartella, `synthetic: true` e la prima riga del README del pacchetto. Va rigenerato con `make_synthetic_cycle.py` quando cambia L001, altrimenti il suo `config_hash` non corrisponde più (un test lo segnala).
- **Visualizzatore.** In questa prima versione non mostra dati temporali: il collegamento live non è un prerequisito.

## Verifiche

```bash
python3 -m unittest discover -s tools/room3d/tests -v      # 54 test (Blender per integrazione e analisi)
cd web/room3d-viewer && npm run build && npm run check && npm run e2e
```

I test coprono:

- quote, porta e botola (`x` 1,205–1,525, `y` 0,40–0,85, `z` 2,10);
- la variante "centro" della botola (`y_min` 0,175);
- volume 10,1808 m³;
- dati non validi con messaggi chiari: dimensioni negative, ID duplicati, assi nulli, aperture fuori stanza, NaN/Inf, `unknown` con valore, elementi esterni senza motivazione;
- riproducibilità semantica fra due build;
- orientamento e scala Y-up del GLB;
- nodi glTF uguali agli ID del manifest;
- `.blend` riaperto, con raggi che attraversano porta e botola senza colpire nulla;
- cambio di un parametro senza oggetti duplicati;
- codice d'uscita diverso da zero sugli errori;
- contratto dei cicli.

I test end-to-end girano su Chrome headless, in un sottopercorso, su desktop e su telefono (390×844, touch). Verificano:

- rotazione con mouse, dito e pizzico;
- layer;
- trasparenza che lascia raggiungere la sonda interna;
- selezione;
- quote;
- misura della luce della porta = **65,0 cm**;
- confronto;
- errori (layout inesistente, manifest mancante, GLB non valido, WebGL assente);
- solo richieste GET verso la stessa origine.

La stessa suite è stata eseguita anche sul container Nginx.

## Misure ancora necessarie

L'elenco completo e motivato è in [ASSUMPTIONS.md](ASSUMPTIONS.md). In sintesi:

1. Riferimento della distanza porta–botola di 40 cm: bordo vicino o centro.
2. Altezza della porta, lato cerniera e verso di apertura (le fonti sono in conflitto).
3. Spessori di pareti, soffitto e pavimento.
4. Posizione, quota e orientamento delle tre ventole.
5. Percorso reale del tubo Ø100 e quota della bocca; quale angolo è "opposto alla porta".
6. Ingombri e posizioni di stufa, umidificatori, estrattore, X4, X6 e prese.
7. Posizione rilevata delle sonde (B1, B3, B4, B5) e della cella di carico.
8. Strutture di appensione e ingombri reali del prodotto.
