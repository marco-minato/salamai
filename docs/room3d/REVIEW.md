# Revisione indipendente — room3d

Stato: **revisione 1 eseguita da Codex su `14b2495`: modifiche richieste (4 finding).** Correzioni in un commit successivo, in attesa della riverifica (revisione 2). Nessuna approvazione è dichiarata da chi ha implementato.

Come è stata eseguita: Claude Code dentro Herdr (`HERDR_ENV=1`) ha aperto un pannello Codex (`herdr agent start reviewer --kind codex -- --no-daemon`) in un worktree separato `../salamai-review`, HEAD detached sul commit da esaminare, con la consegna della sezione 2 delle specifiche. Codex ha scritto il report nel worktree; il testo qui sotto è copiato senza modifiche, salvo il livello dei titoli. Le richieste di Codex di eseguire comandi fuori dal suo sandbox (npm ci, Blender batch, test, Chrome headless) sono state approvate dall'utente o, su sua delega, solo quando scrivevano nel worktree di revisione o in `/tmp`.

## Correzioni (commit successivo a `14b2495`)

| Finding | Correzione | Prove aggiunte |
|---|---|---|
| F1 — Alta | Cartella di revisione `layouts/<layout_id>/<build_id>` (configurazione + geometria generata) al posto di `<config_hash[:12]>`. GLB e PNG con i primi 16 caratteri dello SHA256 nel nome; `images_sha256` nel manifest. Nginx: `immutable` solo per `*-<sha16>.glb/png`, `manifest.json` `no-cache`. I cicli registrano `build_id` (obbligatorio) e `semantic_hash`; `resolve_build` li verifica insieme a `config_hash` ed esce con 2 se non coincidono. Commit dei sorgenti diverso o build con modifiche non registrate → `provenance_warnings` nel pacchetto (la geometria è vincolata dal `build_id`). `sync-data.mjs` verifica anche le immagini. | `test_generator_change_changes_revision` (copia del generatore con cornice 15→20 mm: stesso `config_hash`, `build_id` e cartella diversi), `test_revision_paths_are_content_addressed`, `test_changed_geometry_same_config_rejected`, `test_source_commit_mismatch_is_reported`. Container `nginx:1.30.5-alpine`: intestazioni Cache-Control controllate con curl, POST → 405, e2e completo via `--url`. |
| F2 — Media | Disponibilità calcolata sulle letture dell'intervallo di ciascun layout. Un punto è "con dati" solo con campioni validi (`valid_samples`); `measured_by` e `sensors_without_data` derivano dai dati validi; zona con sonda ma senza dati → "NON OSSERVATA: sonda presente ma nessun dato valido". L'osservazione fissa "una sola sonda (B1)" è ora calcolata. | `test_zone_without_valid_data_is_not_observed`, `test_coverage_is_per_layout_interval`. |
| F3 — Media | Una sola funzione `classify` per aggregati e istantanea: numeri finiti come float, NaN/Inf/testo e stati diversi da on/off → qualità `non valida`, valore `null`, grezzo in `raw`. | `test_instant_flags_invalid_values`. |
| F4 — Media | Testi di botola e porta generati da `derive_openings` (`openings.*.texts`) e usati da cartiglio PNG, note delle entità, suffissi delle quote e visualizzatore. | `test_opening_texts_follow_data` (variante centro e porta misurata), controlli sul manifest della variante centro in `test_parameter_change_moves_without_duplicates`, controllo e2e che il pannello mostri i testi del manifest caricato. |

Verifiche dell'implementatore sul nuovo commit (non sono una revisione): `tools/room3d/build_all.sh` exit 0 con 62 test Python superati; `npm run e2e` superato sia col server interno sia sul container Nginx. `build_id` di L001 e L900_DEMO invariati (`1ff600bc3a7b36eee701`, `274d53fea584bd3da762`): le correzioni non cambiano la geometria.

## Revisione 2

In attesa della riverifica di Codex sul nuovo commit.

## Revisione 1 — report di Codex su `14b2495`

## Revisione indipendente Salamai room3d — 14b2495

Data: 28 ottobre 2026. Revisore: Codex.

**Commit esaminato:** `14b2495136eea9c2583a1e8b5f695a95ce7ca470`, HEAD detached nel worktree `/home/marco/lab/salamai-review`, snapshot indicato di `feat/room3d`.

**Verdetto: modifiche richieste; snapshot non approvato.** La build completa, i 54 test Python e la suite browser passano, ma restano **4 finding: 1 alta, 3 media, 0 bassa, 0 critica**. In particolare l'identità usata per conservare e recuperare le revisioni non vincola la geometria prodotta dal generatore.

### Perimetro e integrità

Letti prima `docs/room3d/REVIEW.md`, la sezione 2 di `documentazione/Salamai_Blender_Claude_Herdr_Codex.md`, `docs/room3d/README.md` e `docs/room3d/ASSUMPTIONS.md`. Ispezionati configurazioni stanza/layout, mapping e contratto ciclo, validatore, generatore, esportatore analisi, test, frontend Three.js, sincronizzazione asset, lockfile e configurazione Docker/Nginx. Confrontati i mapping principali con `homeassistant/salumi_log.py`, `homeassistant/salumi.yaml` e i firmware ESPHome presenti.

Nessuna modifica ai file tracciati, nessun commit, nessun collegamento alla scena Blender condivisa o al socket MCP. Non usato il worktree principale per build o modifiche. Blender è stato avviato in processi batch separati con `--factory-startup`; gli output sono in questo worktree e in `/tmp`. Le mutazioni sperimentali descritte sotto riguardano esclusivamente copie in `/tmp`. `git diff --exit-code` e `git diff --cached --exit-code` risultano puliti prima della scrittura del report.

Un comando iniziale di ricerca `find .. -name AGENTS.md -print`, troppo ampio, è stato interrotto: ha elencato percorsi di repository adiacenti e ricevuto alcuni errori di permesso. Nessun file d'implementazione esterno è stato modificato o usato come input della revisione. Il controllo mirato successivo dei file AGENTS negli antenati e nel worktree non ha trovato istruzioni applicabili.

### Ambiente e comandi eseguiti

Ambiente rilevato: Blender **5.2.3 LTS**, hash `e13b728c6880`; Python **3.14.4**; Node **v24.14.0**; npm **11.9.0**; Chrome di sistema `/usr/bin/google-chrome`. Non sono state aggiornate le versioni delle dipendenze.

I comandi sono eseguiti dalla radice del worktree salvo indicazione diversa. I log in `/tmp` sono artefatti locali di questa revisione, non file consegnati nel repository.

| Comando / controllo | Esito ed evidenza |
|---|---|
| `pwd`, `git status --short`, `git rev-parse HEAD` | Worktree corretto, inizialmente pulito, commit sopra riportato. |
| `cat`, `sed`, `nl -ba`, `rg` sui file citati | Ispezione documentale e statica; riferimenti puntuali nei finding. |
| `tools/room3d/build_all.sh > /tmp/salamai-review-build.log 2>&1` nel sandbox | Generati entrambi i layout e gli 8 PNG, ma Blender resta bloccato in chiusura con `pa_write() ... Operation not permitted`; tentativo interrotto, exit 130. Anche il semplice probe `blender -noaudio --background --factory-startup --python-expr 'print("REVIEW_AUDIO_PROBE")'` si blocca in chiusura. Non classificato come difetto del modello. |
| Prima suite `python3 -m unittest discover -s tools/room3d/tests -v` nel sandbox | Interrotta perché la build Blender di preparazione resta bloccata nello stesso ambiente. Nessun successo attribuito a questo tentativo. |
| `npm ci --no-audit --no-fund --cache /tmp/salamai-review-npm-cache` in `web/room3d-viewer` | Primo tentativo ristretto fallito (`Exit handler never called`), rieseguito con escalation autorizzata: **exit 0**, 19 pacchetti installati. |
| `python3 -m unittest discover -s tools/room3d/tests -p test_core.py -v` | **37 test passati**, log `/tmp/salamai-review-core.log`. |
| `blender --background --factory-startup --python-exit-code 1 --python tools/room3d/build_scene.py -- --config model/room3d/room.json --output /tmp/salamai-review-build2 --no-render` fuori sandbox | **Exit 0**, seconda build indipendente; log `/tmp/salamai-review-build2.log`. |
| `python3 tools/room3d/export_analysis.py --cycle model/room3d/cycles/examples/SINTETICO_2026-01-10_0800 --build build/room3d` | **Exit 0**, pacchetto sintetico generato. |
| `python3 -m unittest discover -s tools/room3d/tests -v` fuori sandbox | **54 test passati**, nessuno saltato, in 10,177 s; log `/tmp/salamai-review-tests-unsandboxed.log`. |
| `npm run build && npm run check` in `web/room3d-viewer` | **Exit 0** dopo installazione completata. Prima di questa, un tentativo ha restituito `vite: not found`; non è un finding dello snapshot. |
| `npm run e2e -- --out /tmp/salamai-review-e2e` | Nel sandbox fallisce il bind HTTP con `listen EPERM`; rieseguito con escalation autorizzata: **exit 0, tutte le verifiche superate**. Log `/tmp/salamai-review-e2e.log`, screenshot nella directory omonima. |
| `tools/room3d/build_all.sh > /tmp/salamai-review-build-full.log 2>&1` fuori sandbox | **Exit 0 dell'intero comando unico**: validazione, rendering, esportazione analisi, 54 test, npm ci, bundle e controllo sola lettura. Termina con `== fatto: build/room3d e web/room3d-viewer/dist`. |
| `python3 /tmp/salamai-review-variants.py` | Prepara copie isolate del generatore e della configurazione per F1/F4. Nessuna modifica ai sorgenti revisionati. |
| Build del generatore copiato con `--python /tmp/salamai-review-variants/tools/build_scene.py -- --config /home/marco/lab/salamai-review/model/room3d/room.json --output /tmp/salamai-review-generator-change --no-render` e gli stessi flag batch sopra | **Exit 0**. Nella copia cambia soltanto la larghezza della cornice generata, `fw = 0.015` → `0.020` in `opening_parts`. Verifica F1. Log `/tmp/salamai-review-generator-change.log`. |
| Build originale con `--config /tmp/salamai-review-variants/model/room.json --output /tmp/salamai-review-center --layout L001` e gli stessi flag batch sopra | **Exit 0**, quattro PNG della variante documentata `offset_reference=center`; estrattore, valvola e primi punti del tubo riallineati a Y=0,40 come nel test esistente. Log `/tmp/salamai-review-center.log`. |
| `python3 /tmp/salamai-review-probes.py` | **Exit 0** nella riesecuzione a build completata. Mutazioni solo del CSV copiato: F2/F3 e confronto fra build. Log `/tmp/salamai-review-probes.log`. Il primo tentativo durante la rigenerazione non disponeva ancora del catalogo ed è fallito; non è stato usato come evidenza. |
| `node /tmp/salamai-review-browser-probe.mjs` fuori sandbox | **Exit 0**: serve il bundle originale con gli asset della variante center, legge manifest e testo UI e salva `/tmp/salamai-review-center-browser.png`. Log `/tmp/salamai-review-browser-probe.log`; conferma F4 nel browser. |
| `view_image` sugli output | Controllate tutte le 4 viste di L001 e tutte le 4 di L900_DEMO, la sezione A della variante center e gli screenshot browser desktop iniziale/confronto e mobile iniziale/pannello. |

### Controlli positivi sullo snapshot

#### Coordinate, quote e geometria

- Stanza interna **3,03 × 1,60 × 2,10 m**; volume lordo **10,1808 m³**, distinto esplicitamente dal volume libero.
- Porta sulla parete Y=0, **X=1,04–1,69**, centro **1,365 m**, luce **0,65 m**. Altezza `unknown` con `value:null`, disegno a **1,90 m**, marcato provvisorio.
- Botola **X=1,205–1,525**, **Y=0,40–0,85**, centro **(1,365; 0,625)**, **Z=2,10 m**, dimensioni **0,32 × 0,45 m**. Interpretazione dei 40 cm al bordo vicino esplicitamente assunta e non confermata.
- Il parametro center produce correttamente **Y=0,175–0,625**, centro Y=0,40; la geometria funziona, la comunicazione presenta F4.
- Tolleranza configurata **0,0005 m**; i test sulle aperture usano anche tolleranze più strette per i valori derivati. Il test d'integrazione sul GLB usa **0,0001 m** sugli ingombri trasformati.
- La suite riapre il `.blend` e verifica con raggi la luce libera di porta e botola, oltre a parete e soffitto pieni. Quindi le aperture non sono semplici rettangoli sovrapposti.
- Spessori convenzionali esterni al volume interno; tre ventole di ricircolo distinte dall'estrattore, frecce nominali non simulate; placeholder prodotto e geometrie provvisorie riconoscibili.
- Il percorso del tubo contiene tratti e raccordi con ID e raggi; la lunghezza deriva da tratti + archi, non da una dichiarazione di acquisto. Lo scarto rispetto ai 3 m acquistati è documentato. Non sono inventati coefficienti di perdita o portate da PWM/RPM.

#### Z-up/Y-up, ID e riproducibilità

Trasformazione canonica → glTF **(x,y,z) → (x,z,−y)**, inversa **(xg,yg,zg) → (xg,−zg,yg)**. Esportazione Y-up esplicita; test su soffitto, parete di fondo, ventola, tubo, anta ed estrattore verificano orientamento e scala. Nel browser `FrameTransform` è condiviso da quote, hit test convertito e misure; lo snap applica prima la `matrixWorld` del vertice.

Due build originali indipendenti hanno gli stessi ID, config hash, semantic hash, build ID e SHA256 GLB, per entrambi i layout. Non è stata richiesta identità binaria del `.blend`. I manifest hanno SHA diversi per metadati/immagini di build, come atteso dai due invocamenti; il problema degli URL immutabili è discusso in F1.

| Layout | Oggetti | Config hash | Semantic hash | Build ID |
|---|---:|---|---|---|
| L001 | 35 | `e6524a05288a297be4751cb6faff4af62fb90e8a7a84e4615c82b6bc341de87d` | `1556fc63c52529de0cf0ff8675cd526d12efda987958b010763bbc032fc8b769` | `1ff600bc3a7b36eee701` |
| L900_DEMO | 34 | `9787bd0a77d91e8a53127eb1805f8cdd160a4492c0a3812f7bf4a40ecf9cfdbe` | `f1d6990a44465513db60e33dbfb7afcb13054668663a2e6a57cd8f1fe828574f` | `274d53fea584bd3da762` |

Testata l'uguaglianza fra nomi/ID dei nodi GLB e manifest, extras degli oggetti e build ID della scena. Cambio parametro senza duplicazione degli ID verificato dalla suite. Validazione negativa coperta per dimensioni negative, duplicati, assi nulli/non normalizzati, aperture fuori stanza, NaN/Inf nella configurazione, unknown con valore e componenti esterni non motivati.

#### Associazione cicli, provenienza e immagini

L'esempio è inequivocabilmente sintetico: cartella, `synthetic:true`, avviso e README del pacchetto. Il test verifica che il suo config hash coincida con L001. Superati test di cambio layout durante ciclo, intervalli sovrapposti, letture fuori validità e revisione assente: quest'ultima restituisce codice 2 invece di applicare il layout corrente. F1 riguarda il caso diverso di stessa configurazione con generatore cambiato.

Mapping corrente T/UR/stufa/umidificatore coerente con le stringhe del logger; firmware con due soli ingressi giri, terza ventola non risolta; canale umidificatore non attribuito arbitrariamente a M2/M3. Identificativi futuri sono marcati non verificati. Non verificata l'esistenza effettiva di questi ID su un'installazione HA attiva.

Carichi e rimozioni sono eventi; non si dichiara vuoto il lato sinistro dopo tre giorni. Osservazioni, inferenze e ipotesi sono sezioni separate e non compaiono campi di velocità o conclusioni automatiche di sicurezza alimentare. Restano i difetti di qualità F2/F3.

Gli otto PNG sono leggibili alla risoluzione prodotta, con cartiglio, quote esterne, richiami e assi. I due layout sono distinguibili e il demo è esplicitamente un'ipotesi, non uno storico. In alcune proiezioni componenti si sovrappongono geometricamente, ma i richiami permettono di identificarli; non ho rilevato un difetto bloccante nella leggibilità delle viste di default. La griglia disegnata in posizione di porta chiusa mentre l'anta è aperta è una convenzione esplicitamente annotata nel layout, non una misura in opera.

#### Visualizzatore web

Verificati runtime con Chrome headless e server statico nel sottopercorso `/salamai/room3d/`, con asset locali e senza dipendenze runtime da Blender/MCP. La suite effettua soltanto GET e non richiede risorse esterne; 33 richieste GET/HEAD complessive registrate dal server. Lettura del codice e controllo statico del bundle non mostrano percorsi per salvare configurazioni o comandare dispositivi.

Su desktop: caricamento, rotazione mouse, layer nascosti non selezionabili, parete opaca/trasparente con selezione della sonda interna, pannello componente e assunzioni, 15 quote, misura della luce porta **65,0 cm** con coordinate canoniche, confronto e sincronizzazione camera. Nel confronto risultano correttamente spostamento fan_02, orientamento fan_03, aggiunte/rimozioni e percorso tubo modificato; demo etichettato. Gestiti layout inesistente, manifest 404, GLB incompatibile/non corrispondente e WebGL assente. Nessun errore JavaScript nel percorso nominale testato.

Su viewport mobile **390×844**, touch emulato: rotazione a un dito, pinch a due dita, selezione della stufa e apertura pannello, assenza di overflow orizzontale della pagina. Screenshot ispezionati: comandi distribuiti su più righe, modello visibile, pannello scorrevole. Questo non equivale a certificazione su dispositivi fisici o su ogni dimensione schermo.

Coerenza asset: `sync-data.mjs` verifica SHA manifest/GLB del catalogo prima della copia; caricamento browser verifica versione, layout/build ID, SHA GLB quando Web Crypto è disponibile, extras della scena e corrispondenza completa degli ID. Questi controlli rilevano diverse mescolanze, ma non correggono la collisione di percorsi fra build differenti di F1.

### Finding

#### F1 — Alta — La revisione identificata dal ciclo e dagli URL non include il generatore

**File:** `tools/room3d/room3d_core.py:115`, `tools/room3d/build_scene.py:648`, `tools/room3d/build_scene.py:653`, `tools/room3d/export_analysis.py:99`; rilevante anche `web/room3d-viewer/deploy/nginx.conf.template` (cache immutable).

**Evidenza:** `config_hash` include soltanto JSON stanza + layout. `build_id` include anche l'hash semantico, ma la directory continua a essere `layouts/<layout_id>/<config_hash[:12]>`. `resolve_build` controlla il config hash, senza vincolare semantic/build ID o verificare `source_commit` del riferimento.

Riproduzione eseguita: nella sola copia `/tmp/salamai-review-variants/tools/room3d_core.py`, cambio della cornice generata da 15 a 20 mm, poi build sugli stessi JSON originali. Entrambi i layout mantengono **stesso config hash e stesso percorso**, ma hanno **semantic hash e build ID diversi**. Per L001 il semantic hash diventa `13b6b084dc8040a89f1a463d640a6e7a80c81125cd81ffe68e8d8ddc44fb0e29`. Passando all'esportatore il riferimento del ciclo sintetico originale e questa nuova build, `resolve_build` la accetta. Un ulteriore probe con `source_commit` deliberatamente diverso viene ugualmente accettato.

**Impatto:** una correzione legittima al generatore può sovrascrivere la geometria associata a cicli pregressi senza cambiare il riferimento registrato. Gli URL dichiarati immutabili possono cambiare contenuto: cache vecchie possono mostrare una vecchia revisione o provocare errori di incompatibilità con il nuovo catalogo. Anche il manifest cambia per timestamp/metadata sotto lo stesso URL tra rigenerazioni originali.

**Correzione proposta:** distinguere hash configurazione e identità completa dell'artefatto. Conservare revisioni con chiave che includa geometria/generatore e pin del ciclo a build/semantic hash o equivalente verificabile; controllare la provenienza dichiarata. Per file con cache immutable usare URL basati sul contenuto effettivo, oppure non riscrivere un artefatto già pubblicato e spostare metadata variabili fuori dalla revisione. Aggiungere test che cambino solo il generatore e provino sia il recupero storico sia la pubblicazione con cache.

#### F2 — Media — Una zona viene dichiarata osservata anche senza alcuna misura valida

**File:** `tools/room3d/export_analysis.py:236`, `tools/room3d/export_analysis.py:253`, `tools/room3d/export_analysis.py:259`.

**Evidenza:** `measurement_points` viene popolato dalla presenza del mapping, non dalla disponibilità di letture valide. `sensors_in` controlla colonna e posizione ma non la copertura; `sensors_without_data` esclude quindi anche sonde mappate senza dati.

Riproduzione `/tmp/salamai-review-probes.py`: nella sola copia CSV, tutte le letture `temperatura` e `umidita` diventano `unknown`. Il pacchetto continua a riportare per `zone_salami`:

```json
{"measured_by":["sensor_b1_sth01"],"observation":"osservata da una sola sonda puntuale"}
```

Il probe con `peso_g=unknown` per l'intero ciclo mostra analogamente B2 tra i punti misurati con copertura **0,0%**. La disponibilità non viene inoltre ricalcolata nell'intervallo di ciascun layout quando un ciclo ne contiene più di uno.

**Impatto:** il pacchetto AI comunica una zona come osservata anche quando contiene solo missing; la distinzione fra collocazione di progetto di una sonda e osservazione effettiva risulta ambigua proprio nei cicli incompleti.

**Correzione proposta:** separare sonde previste/mappate da sonde con campioni validi, calcolare copertura per quantità e intervallo di layout e dichiarare esplicitamente `nessun dato valido` quando è zero. Derivare `measured_by` e `sensors_without_data` dalla disponibilità effettiva, mantenendo comunque l'incertezza della posizione. Testare colonna assente, tutti missing/invalid e dati disponibili solo prima/dopo un cambio layout.

#### F3 — Media — Il dettaglio per istante assegna qualità “ok” a valori numerici invalidi

**File:** `tools/room3d/export_analysis.py:292`.

**Evidenza:** `column_stats` riconosce stringhe non numeriche e valori non finiti, ma il ramo `--at` verifica soltanto i sentinel mancanti e l'età del record. Nella copia CSV il primo campione contiene `temperatura=NaN` e `umidita=nonsense`; esportando esattamente il timestamp della prima riga si ottiene:

```json
"temperatura": {"value":"NaN","unit":"°C","quality":"ok"},
"umidita": {"value":"nonsense","unit":"%","quality":"ok"}
```

Nello stesso pacchetto l'aggregato temperatura conta correttamente un campione `invalid`. Riproduzione e risultati in `/tmp/salamai-review-probes.py` e `.log`.

**Impatto:** un consumatore dell'istantanea può trattare come misura valida un errore del logger o un valore non finito; contraddizione con la qualità dichiarata negli aggregati.

**Correzione proposta:** condividere parsing e classificazione dei campioni tra aggregati e istantanee. Per le grandezze numeriche validare numero finito, esportare un numero o null e qualità `non valida`; conservare il dato grezzo separatamente se utile. Validare anche gli stati previsti invece di considerare qualsiasi stringa recente “ok”. Testare NaN, Inf e testo non numerico con `--at`.

#### F4 — Media — Testi di botola/porta fissati nel codice contraddicono varianti valide

**File:** `web/room3d-viewer/src/main.js:251`, `tools/room3d/build_scene.py:520`, `tools/room3d/room3d_core.py:935` (nota botola).

**Evidenza:** UI, cartiglio PNG e nota dell'entità mantengono letteralmente «40 cm ... al bordo vicino»; la UI mantiene anche «altezza porta sconosciuta (1,90 m)». Questi testi non sono derivati dai dati della revisione caricata.

Riproduzione eseguita sulla variante documentata `offset_reference=center`: manifest **Ymin=0,175, Ymax=0,625**, centro Y=0,40. La sezione A renderizzata mostra correttamente la quota **17,5 cm ASSUNTO** al bordo, mentre il cartiglio dice ancora **40 cm al bordo vicino**. Immagine: `/tmp/salamai-review-center/layouts/L001/9f81e6b518be/views/sezione_A_x.png`.

Con il bundle originale e questi asset, Chrome carica senza errori la build `093d0ffdf3b8c2765b57`; il probe legge `offset_reference:'center'` dal manifest ma trova nel pannello «Botola: 40 cm dalla parete porta al bordo vicino». Screenshot `/tmp/salamai-review-center-browser.png`, log `/tmp/salamai-review-browser-probe.log`.

**Impatto:** la procedura documentata per cambiare riferimento produce una vista tecnica e un visualizzatore contraddittori; analogamente il testo porta resterebbe obsoleto dopo un rilievo. Un utente può riportare in opera la distanza riferita al punto sbagliato.

**Correzione proposta:** generare cartiglio, note e avvisi dai valori e dagli stati effettivi di `openings` nel JSON/manifest; includere il riferimento bordo/centro corrente e l'altezza effettiva/provvisoria. Aggiornare coerentemente le descrizioni delle assunzioni. Testare il testo renderizzato e la UI con variante center e porta misurata, oltre ai soli numeri geometrici.

### Verifiche non eseguite e limiti

- Nessun rilievo fisico: non confermati bordo/centro dei 40 cm, altezza/verso porta, spessori, posizioni, ingombri e supporti delle apparecchiature/prodotti. Le assunzioni dichiarate non diventano misure reali per effetto dei test.
- Nessuna connessione a Home Assistant, dispositivi, Modbus o telemetria reale; mapping verificato solo rispetto ai sorgenti disponibili, non contro un impianto attivo. Nessuna validazione del processo alimentare, della portata o del dimensionamento impiantistico.
- Non eseguiti Docker build/run e test HTTP su Nginx effettivo: configurazione ispezionata staticamente. Non verificati runtime CSP, cache e rifiuto metodi del container; il server statico della suite è un'altra implementazione. Nessuna pubblicazione su infrastrutture reali.
- Browser verificato su Chrome headless/SwiftShader; non su telefono fisico, Safari/iOS, Firefox, GPU hardware o tutte le viewport. Su mobile i test eseguiti coprono rotazione, pinch, selezione e pannello; non è stata ripetuta su telefono l'intera sequenza desktop di layer, misura nota, confronto ed errori. Pan e accessibilità tastiera/screen reader non sono stati verificati con prove dedicate.
- Rendering verificato con Workbench, non con Cycles. Nessuna prova interattiva nella GUI Blender né uso di MCP; riapertura `.blend` verificata dai test batch.
- Verifica degli hash/ID e delle aperture non equivale a prova esaustiva di ogni faccia della mesh o di tutte le configurazioni accettate. Non eseguito fuzzing completo dello schema/validatore, benchmark o audit di sicurezza delle dipendenze. Non serviva una consultazione di servizi esterni per verificare lo snapshot locale.
- Non testata direttamente una cache browser persistente durante deploy successivi: F1 è dimostrato tramite collisione del percorso e accettazione della geometria cambiata nel recupero storico, non tramite simulazione completa di rollout.
- I primi blocchi audio/thumbnail e i divieti di bind/network sono limiti del sandbox; la riesecuzione autorizzata risolve gli impedimenti e consente l'esito positivo completo. Non sono attribuiti come finding all'implementazione.

### Verdetto finale

**Richieste correzioni prima dell'approvazione**, in particolare F1 per l'integrità della correlazione storica. Coordinate e aperture dello snapshot, trasformazioni, ID, build originale e principali funzioni browser sono sostenuti da verifiche riprodotte; questo non annulla i quattro difetti dimostrati. Dopo le correzioni occorre una nuova revisione su commit preciso, con prove mirate per ciascun finding. Nessuna approvazione della scena condivisa o dell'impianto reale è implicita nel presente report.
