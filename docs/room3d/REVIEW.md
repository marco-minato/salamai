# Revisione indipendente — room3d

Stato: **revisione 4 di Codex su `f219e49` (nuovo percorso del tubo di aspirazione): geometria coerente, nessuna collisione, un finding F6 (media) sulle note del flusso.** F6 corretto nel commit successivo, in attesa della revisione 5. L'ultima approvazione completa di Codex resta quella di `11a0d31` (revisione 3) e non copre le modifiche successive al modello. Nessuna approvazione è dichiarata da chi ha implementato.

Come è stata eseguita: Claude Code dentro Herdr (`HERDR_ENV=1`) ha aperto un pannello Codex (`herdr agent start reviewer --kind codex -- --no-daemon`) nel worktree separato `../salamai-review`, con HEAD detached sul commit da esaminare e la consegna della sezione 2 delle specifiche. Codex scrive ogni report nel worktree; qui sotto i report sono copiati senza modifiche, salvo il livello dei titoli. Le richieste di Codex di eseguire comandi fuori dal suo sandbox (npm ci, Blender batch, test, Chrome headless, Docker locale) sono state approvate dall'utente o, su sua delega, solo per azioni locali con output nel worktree di revisione o in `/tmp`.

| Revisione | Commit | Esito |
|---|---|---|
| 1 | `14b2495` | Modifiche richieste: F1 alta, F2–F4 medie |
| 2 | `4337901` | F1–F4 risolti; F5 media (contratto dei cicli) |
| 3 | `11a0d31` | Approvato: F1–F5 risolti, nessun nuovo finding |
| 4 | `f219e49` | Nuovo percorso del tubo (T + due rami Ø80, bocche in alto): geometria ok; F6 media |
| 5 | commit di correzione di F6 | in attesa |

## Correzioni

### Commit `4337901` (F1–F4)

| Finding | Correzione | Prove aggiunte |
|---|---|---|
| F1 — Alta | Cartella di revisione `layouts/<layout_id>/<build_id>` (configurazione + geometria generata) al posto di `<config_hash[:12]>`. GLB e PNG con i primi 16 caratteri dello SHA256 nel nome; `images_sha256` nel manifest. Nginx: `immutable` solo per `*-<sha16>.glb/png`, `manifest.json` `no-cache`. I cicli registrano `build_id` (obbligatorio) e `semantic_hash`; `resolve_build` li verifica insieme a `config_hash` ed esce con 2 se non coincidono. Commit dei sorgenti diverso o build con modifiche non registrate → `provenance_warnings` nel pacchetto (la geometria è vincolata dal `build_id`). `sync-data.mjs` verifica anche le immagini. | `test_generator_change_changes_revision` (copia del generatore con cornice 15→20 mm: stesso `config_hash`, `build_id` e cartella diversi), `test_revision_paths_are_content_addressed`, `test_changed_geometry_same_config_rejected`, `test_source_commit_mismatch_is_reported`. Container `nginx:1.30.5-alpine`: intestazioni Cache-Control controllate con curl, POST → 405, e2e completo via `--url`. |
| F2 — Media | Disponibilità calcolata sulle letture dell'intervallo di ciascun layout. Un punto è "con dati" solo con campioni validi (`valid_samples`); `measured_by` e `sensors_without_data` derivano dai dati validi; zona con sonda ma senza dati → "NON OSSERVATA: sonda presente ma nessun dato valido". L'osservazione fissa "una sola sonda (B1)" è ora calcolata. | `test_zone_without_valid_data_is_not_observed`, `test_coverage_is_per_layout_interval`. |
| F3 — Media | Una sola funzione `classify` per aggregati e istantanea: numeri finiti come float, NaN/Inf/testo e stati diversi da on/off → qualità `non valida`, valore `null`, grezzo in `raw`. | `test_instant_flags_invalid_values`. |
| F4 — Media | Testi di botola e porta generati da `derive_openings` (`openings.*.texts`) e usati da cartiglio PNG, note delle entità, suffissi delle quote e visualizzatore. | `test_opening_texts_follow_data` (variante centro e porta misurata), controlli sul manifest della variante centro in `test_parameter_change_moves_without_duplicates`, controllo e2e che il pannello mostri i testi del manifest caricato. |

### Commit `11a0d31` (F5)

| Finding | Correzione | Prove aggiunte |
|---|---|---|
| F5 — Media | `cycle.schema.json` passa a `schema_version` **1.1**: `build_id` obbligatorio (`^[0-9a-f]{20}$`), `semantic_hash` opzionale (SHA256), formati per `layout_id`, `config_hash`, `source_commit`. `load_cycle` applica gli stessi formati prima di costruire percorsi e risponde con `AnalysisError` (codice 1) e il percorso del campo. I cicli 1.0 sono rifiutati con un messaggio che spiega come integrarli dalla build storica; il README documenta la procedura. Esempio sintetico e `make_synthetic_cycle.py` portati a 1.1. | `TestCycleContract`: l'esempio è valido per schema e runtime; `build_id` mancante, intero, vuoto o con percorso, `semantic_hash` malformato, `layout_id` con `..`, `config_hash` corto, `source_commit` non esadecimale e contratto 1.0 sono rifiutati **sia** dallo schema (`jsonschema`) **sia** dal runtime. |

Verifiche dell'implementatore sul commit di F5 (non sono una revisione): `tools/room3d/build_all.sh` exit 0 con 65 test Python superati; `npm run e2e` superato. `build_id` invariati.

### Commit successivo a `f219e49` (F6)

| Finding | Correzione | Prove aggiunte |
|---|---|---|
| F6 — Media | Le due note su sbilanciamento dei rami e percorso dell'aria riscritte come **IPOTESI** / intento di progetto, con "nessuna ripartizione di portata calcolata o misurata" e "percorso reale dell'aria non misurato né simulato". Arrivano così marcate anche a manifest, visualizzatore e pacchetto di analisi. | `test_flow_claims_in_notes_are_marked_as_hypotheses`: ogni nota dei layout che parla di aspirazione, percorso, ripartizione o portata deve essere marcata come ipotesi o direzione nominale. La vecchia frase fa fallire il test. |

Verifiche dell'implementatore (non sono una revisione): `build_all.sh` exit 0 con 67 test superati; `npm run e2e` superato. `semantic_hash` di L001 invariato (`8eebc290011f…`); `build_id` cambiato perché le note fanno parte della configurazione (`ce7905cd44a7e4c12fd9`); ciclo d'esempio rigenerato.

## Revisione 4 — report di Codex su `f219e49`

### Riverifica 4 — Salamai room3d, f219e49

Data: 28 ottobre 2026. Revisore indipendente: Codex.

**Commit esaminato:** `f219e493f4080cdcfd9ade7664620e19d0716c42`, HEAD detached nel worktree `/home/marco/lab/salamai-review`.

**Verdetto: modifiche richieste per F6 (media).** La geometria rappresentata è coerente con la nuova indicazione, build e test passano e non sono state trovate interferenze con i componenti richiesti nelle forme attualmente disegnate. Rimane una nuova affermazione non verificata sul comportamento dell'aria nelle note autorevoli, propagata al browser e al pacchetto AI. **Finding: 0 critici, 0 alti, 1 medio, 0 bassi.**

#### Perimetro e integrità

Letto il diff `11a0d31..f219e49`, inclusi il commit documentale `9fdc067`, il nuovo layout, la fonte utente, il ciclo sintetico, i test e la documentazione. Nel range compare anche `58d9514`, copia documentale del report della revisione 3. Diff conservato in `/tmp/salamai-review-f219e49.diff`.

Nessuna modifica all'implementazione, alle configurazioni autorevoli o alla scena condivisa; nessun commit, nessun accesso MCP e nessuna scrittura nel worktree principale. Build standard nel solo worktree di revisione; script, log e screenshot aggiuntivi in `/tmp/salamai-review-f219e49/`. Blender avviato in batch separato con `--factory-startup`. Eseguite con autorizzazione le prove fuori sandbox necessarie per Blender e Chrome.

`git diff --exit-code`, `git diff --cached --exit-code` e `git diff --check` puliti. Prima della scrittura del report erano non tracciati soltanto i tre report precedenti.

#### Comandi ed esiti

Ambiente invariato: Blender 5.2.3 LTS, Python 3.14.4, Node v24.14.0, npm 11.9.0 e Chrome di sistema. Comandi dalla radice del worktree salvo indicazione diversa.

| Comando / controllo | Esito |
|---|---|
| `git rev-parse HEAD`, `git status --short`, `git diff --stat 11a0d31..f219e49`, lettura del diff e dei file modificati | Snapshot corretto, sorgenti puliti, ispezione completata. |
| `tools/room3d/build_all.sh > /tmp/salamai-review-f219e49-build.log 2>&1` | **Exit 0**: validazione, due layout, otto PNG e altri derivati, pacchetto sintetico, **66 test passati in 11,928 s**, npm ci, build web e controllo sola lettura. Nessun test segnalato come saltato. |
| `python3 /tmp/salamai-review-f219e49/probe.py` | **Exit 0**: confronto ID/configurazioni/mesh con `11a0d31`, percorsi e lunghezze, stati e fonti, separazione degli ingombri, associazione ciclo/build, estrazione note e percorsi immagini. Log `probe.log`, ingombri in `bounds.json`. |
| `blender --background --factory-startup --python-exit-code 1 --python /tmp/salamai-review-f219e49/collision_blender.py` | **Exit 0**. BVH delle superfici generate: nessuna intersezione tra D1/T/D2/D3 e ventole, frecce, tubi nebbia, zone prodotto, pareti o soffitto. Log `collision.log`, risultato `collision.json` uguale a `[]`. |
| `npm run e2e -- --out /tmp/salamai-review-f219e49/e2e` in `web/room3d-viewer` | **Exit 0, tutte le verifiche superate**. Log `e2e.log`, screenshot nella directory `e2e`. |
| `node /tmp/salamai-review-f219e49/browser.mjs` | **Exit 0**: selezione reale con click di T, D2 e D3 dalla vista alta, lettura dei pannelli, screenshot e confronto con L900_DEMO. Log `browser.log`, immagini `duct_tee_01.png`, `exhaust_duct_02.png`, `exhaust_duct_03.png`, `compare.png`. |
| Sonda Python di SHA256 su catalogo, manifest, GLB e PNG di entrambi i layout | Tutti gli hash verificati; `ALL_CATALOG_ASSET_HASHES_OK`. |
| Lettura del pacchetto sintetico generato | Nuove entità e note presenti; le sezioni `hypotheses` e `inferences` sono vuote. Evidenza per F6. |
| `view_image` | Ispezionati pianta e assonometria L001 rigenerate, screenshot web iniziale assonometrico e screenshot della selezione del T dall'alto. |
| `git diff --exit-code`, `git diff --cached --exit-code`, `git diff --check` | Nessuna modifica tracciata introdotta dalla revisione. |

I log con nome relativo sono in `/tmp/salamai-review-f219e49/`.

#### Geometria rispetto all'indicazione

La fonte `src_user_20261028` registra esplicitamente: tubo dalla botola verso la parete lunga di fondo, raccordo a T, due rami Ø80 agli angoli lontani dalla porta e bocche in alto. Il modello realizza questa topologia nel frame canonico Z-up, con parete porta Y=0 e fondo Y=1,60.

| Elemento | Coordinate / dimensioni rappresentate | Esito |
|---|---|---|
| D1 `exhaust_duct_01` | Asse `(1,365; 0,625; 2,10)` → `(1,365; 0,625; 1,92)` → `(1,365; 1,50; 1,92)`; curva R=0,10 m | Parte dalla botola e va verso +Y, al fondo. |
| T `duct_tee_01` | Centro `(1,365; 1,50; 1,92)`; ingombro provvisorio 0,22×0,12×0,12 m | D1 termina nel centro del T; raccordo rappresentato schematicamente da un box. |
| D2 `exhaust_duct_02` | Dal centro T a `(0,10; 1,50; 1,92)` | Bocca nell'angolo sinistro di fondo, in alto. |
| D3 `exhaust_duct_03` | Dal centro T a `(2,93; 1,50; 1,92)` | Bocca nell'angolo destro di fondo, in alto. |

Le bocche sono a 18 cm dal soffitto lungo l'asse Z, a 10 cm dalla parete di fondo e a 10 cm dalle pareti laterali lungo l'asse X. Questi sono **valori assunti**, non quote rilevate. I due rami sono orizzontali lungo X, con terminali geometrici rivolti verso le pareti laterali: anche questo dettaglio è documentato come provvisorio.

Lunghezze derivate dal percorso effettivo:

- D1: **1,01208 m**, due tratti e una curva;
- D2: **1,265 m**, un tratto rettilineo;
- D3: **1,565 m**, un tratto rettilineo.

Il Ø100 nominale conserva la fonte `src_distinta`; i Ø80 nominali e le connessioni del T hanno stato `declared` e fonte `src_user_20261028`. I diametri esterni sono sconosciuti, disegnati rispettivamente a 0,105 e 0,084 m. Le coordinate del T e dei rami sono `assumed`; l'ingombro del T è `unknown`, con `value:null` e `draw_value`. Raggio della curva, materiale dei nuovi tubi e coefficienti di perdita rimangono sconosciuti. Nessuna quota esatta dei nuovi rami è promossa a misura reale.

Tutti i nuovi componenti sono `planned`, nel layer `estrazione_ingresso`; il browser evidenzia correttamente dati assunti/sconosciuti. La fonte utente descrive la topologia senza inventare coordinate esatte. L'assunzione `l001_duct_corner` distingue la decisione dichiarata dalle quote provvisorie; il problema F6 riguarda invece le note sul flusso.

#### Collisioni e interferenze

La sonda confronta prima gli AABB ricavati dalle mesh canoniche. Una distanza positiva tra AABB è un limite inferiore conservativo della distanza fra le forme; non è una misura in opera. Non risultano sovrapposizioni tra la nuova rete e ventole, tubi nebbia o zone prodotto.

Esempi di separazione minima conservativa nelle forme disegnate:

| Coppia / vincolo | Separazione ricavata |
|---|---:|
| T – parete di fondo | **4,0 cm** |
| Rami Ø80 – parete di fondo | **5,8 cm** |
| D3 – zona salami | **5,8 cm**, lungo Y |
| D3 – ventola `fan_02` | **almeno 15,88 cm**, distanza tra AABB |
| D3 – tubo nebbia M3 | **almeno 22,77 cm**, distanza tra AABB |
| Rami Ø80 – soffitto | **13,8 cm**, in Z |
| T – soffitto | **12,0 cm**, in Z |
| Bocche – rispettive pareti laterali | **10,0 cm**, in X |

Per D1 l'AABB globale del soffitto si sovrappone al punto di attacco Z=2,10, ma non descrive il foro della botola. Il controllo successivo delle superfici con `mathutils.bvhtree.BVHTree` non rileva intersezioni, confermando che D1 arriva nella botola libera e non attraversa la parte piena del soffitto.

Le sovrapposizioni fra T e tubi sono le connessioni schematiche previste, non collisioni con apparecchiature. I rami arrivano al centro del box T: non vengono modellati innesti, spessori, guarnizioni o volume idraulico interno del raccordo. Non è stata interpretata questa schematizzazione come raccordo costruttivo validato.

Il BVH delle superfici non trova intersezioni della nuova rete con le categorie richieste. Il controllo resta limitato agli ingombri attuali: supporti reali, isolamento, tolleranze di montaggio e prodotto effettivamente appeso non sono modellati. In particolare i 5,8 cm rispetto al placeholder salami non garantiscono la distanza reale dal prodotto.

#### ID, associazione dei cicli e regressioni

Confronto riprodotto contro il JSON di `11a0d31`, estratto con `git show` e valutato in memoria:

- **aggiunti soltanto** `duct_tee_01`, `exhaust_duct_02`, `exhaust_duct_03`;
- nessun ID rimosso o rinominato;
- fra i componenti già presenti cambia soltanto la configurazione di `exhaust_duct_01`;
- fra le mesh/hash semantici delle entità preesistenti cambia soltanto `exhaust_duct_01`. Ventole, tubi nebbia, zone prodotto, struttura e aperture restano invariati.

L001 passa da 35 a **38 entità**, con:

```text
config_hash   4ec3494e994a72cfb9b32cd59664b1476e84f5bfa198550d516ba4c77825b5e2
semantic_hash 8eebc290011fb8c7f1afe59fbea621fb5e7c8fbf7ee0c3077fe71dbe4a8f4da1
build_id      c08d7f70134af6a6cfe7
```

Tutti e tre coincidono con il riferimento nel ciclo sintetico aggiornato. Il comando unico esporta il pacchetto senza errori e lo marca come sintetico. I test confermano il riferimento alla revisione esatta, senza assegnare retroattivamente la nuova disposizione ai cicli storici.

L900_DEMO rimane geometricamente invariato: 34 entità e semantic hash `f1d6990a44465513db60e33dbfb7afcb13054668663a2e6a57cd8f1fe828574f`. Il suo build ID diventa `9d83373ca77b8b87025d` perché il config hash include anche `room.json`, dove è stata aggiunta la fonte utente. È una conseguenza del contratto di hash esistente, non uno spostamento nascosto del layout demo.

Il nuovo test `test_exhaust_tee_two_branches_high_in_back_corners` verifica attacco D1/T, partenza dei rami, diametro nominale e collocazione delle bocche. Il test sulla lunghezza aggiorna le attese al numero di punti, mantenendo il controllo tratti+archi. Passano anche i test precedenti di coordinate, aperture, Z-up/Y-up, scala, ID GLB/manifest, riproducibilità, contratti 1.1, missing/invalid e generatore modificato. Il test nuovo usa soglie ampie di posizione e non copre collisioni né classificazione delle note: le sonde aggiuntive hanno verificato separatamente questi aspetti.

#### Documentazione e controllo visivo/web

`ASSUMPTIONS.md` e README sostituiscono correttamente il precedente tubo verso un solo angolo con bocca bassa. Sono allineati a T, rami Ø80 e bocche alte; quote esatte e orientamento delle bocche restano da confermare. Le lunghezze arrotondate del documento sono coerenti con quelle calcolate. È segnalata la necessità di acquistare T e tubi Ø80, assenti dalla distinta.

`MISURE_MANCANTI.md` indica il build ID corretto `c08d7f70134af6a6cfe7`; righe 22, 23 e 23a riportano diametri esterni, raggio, posizione/ingombro T e bocche come provvisori, con i percorsi JSON da aggiornare. I valori delle ventole e degli altri componenti ispezionati corrispondono al layout. Non è stato necessario aggiornare il mapping dei dispositivi per i raccordi passivi.

Ispezionate le immagini rigenerate:

- `build/room3d/layouts/L001/c08d7f70134af6a6cfe7/views/pianta-e38414a6af48c644.png`;
- `build/room3d/layouts/L001/c08d7f70134af6a6cfe7/views/assonometria_aperta-8fd8667659498b55.png`.

Entrambe mostrano il percorso verso il fondo e i rami alti correttamente; T, D2 e D3 sono riconoscibili nei richiami, con marcatura `[A]`. Le sovrapposizioni prospettiche non corrispondono a collisioni 3D secondo le sonde. Nessun difetto bloccante di leggibilità nelle due viste richieste.

Il visualizzatore carica il nuovo build ID. La sonda aggiuntiva seleziona con click i tre nuovi componenti dalla vista alta e legge ID, layer, quote, diametri, lunghezze e stati corretti. I loro nomi e metadati sono presenti negli asset. Nel confronto con il demo sono elencati i tre componenti presenti solo in A e il percorso D1 differente; le viste restano sincronizzate.

La suite e2e completa passa: layer, trasparenza, selezione interna, quote, misura porta **65,0 cm**, confronto, errori, sola lettura e assenza di CDN; sul telefono emulato 390×844 passano rotazione, pinch, selezione, pannello e assenza di overflow orizzontale. Il finding seguente è stato osservato anche leggendo i pannelli effettivi del browser.

#### Finding

##### F6 — Media — Le note presentano inferenze sul flusso come comportamenti accertati

**File:** `model/room3d/layouts/L001_progetto.json:297`, `:359`, `:421`.

**Evidenza:** nel raccordo T compare:

> Con rami di lunghezza diversa (1,27 m e 1,57 m disegnati) aspira di più il ramo corto.

I due rami riportano inoltre come conseguenza certa dell'ingresso basso e delle bocche alte che l'aria attraversi la camera dal basso verso l'alto. Queste frasi non sono marcate come ipotesi, non hanno una fonte di misura o un metodo di calcolo e non specificano condizioni di validità. La fonte `src_user_20261028` dichiara il percorso desiderato, non queste prestazioni. Materiali dei rami, perdite del T/bocche e coefficienti di perdita sono esplicitamente sconosciuti nel medesimo modello.

**Riproduzione:** build completa, selezione con click di `duct_tee_01` e dei rami nel visualizzatore (`/tmp/salamai-review-f219e49/browser.log`): le frasi compaiono nel pannello “Note”. Sono copiate nel manifest e in `build/room3d/analysis/SINTETICO_2026-01-10_0800/package.json` nelle note dei componenti, mentre `hypotheses` e `inferences` del pacchetto sono vuote. La propagazione è quindi effettiva, non solo un commento interno del sorgente.

**Impatto:** la disposizione geometrica può essere interpretata come dimostrazione dello sbilanciamento fra rami o della distribuzione dell'aria nella camera. La sola differenza di lunghezza e la posizione delle aperture non costituiscono nel modello una verifica di tali risultati; il requisito originale separa osservazioni, inferenze e ipotesi e non presenta direzioni o campi di flusso come misure. I badge dei dati geometrici provvisori non classificano esplicitamente queste conclusioni fluidodinamiche.

**Correzione proposta:** eliminare le conclusioni certe oppure riscriverle esplicitamente come ipotesi/intento di progetto, ad esempio “possibile sbilanciamento tra i rami, da verificare; nessuna ripartizione di portata calcolata” e “disposizione pensata per ingresso basso e aspirazione alta; percorso reale dell'aria non verificato”. Mantenerle separate da osservazioni misurate nel pacchetto AI e verificare che la classificazione resti chiara nel browser. Non servono CFD o coefficienti inventati per correggere il problema. Aggiungere una verifica mirata sulle note esportate così che ipotesi di flusso non risultino affermazioni accertate.

#### Verifiche non eseguite e limiti

- Nessun rilievo fisico o prova con apparecchiature reali. Quote, distanze, ingombri e supporti non misurati restano provvisori; nessuna certificazione costruttiva o di montabilità.
- Nessuna misura/calcolo di portata, bilanciamento dei rami, campo d'aria, perdite, rumore o efficacia di asciugatura; nessuna validazione del processo alimentare. F6 riguarda proprio la classificazione delle affermazioni non verificate.
- Interferenze controllate sulle mesh generate e sui placeholder correnti, con separazione AABB e intersezione superfici BVH. Non verificati montanti/supporti mancanti, prodotto reale, tolleranze, accesso per manutenzione, innesti e volume idraulico interno del T. Nessuna analisi degli ostacoli al flusso oltre alla geometria disegnata.
- Il BVH non è un controllo esaustivo di contenimento di solidi arbitrari. Per le categorie richieste, salvo il soffitto perforato, gli AABB positivamente separati escludono anche il contenimento; per D1/soffitto sono stati controllati il foro e le superfici reali generate.
- Ispezionate manualmente pianta e assonometria richieste, non tutte le sezioni/viste del demo rigenerate. Rendering Workbench; non Cycles, Blender GUI o MCP.
- Browser Chrome headless/SwiftShader, touch emulato: non telefono fisico, Safari/iOS, Firefox o tutte le viewport. Non eseguita una nuova suite specifica mobile per i tre nuovi componenti; selezione mirata effettuata su desktop.
- Non ripetuti Docker/Nginx e test cache HTTP: configurazione di deploy e codice web invariati nel diff. Hash degli asset verificati localmente e caricamento web eseguito; nessun rollout su infrastrutture reali.
- Nessuna modifica ai cicli reali né migrazione di archivi storici. Il ciclo aggiornato è esclusivamente l'esempio sintetico. Nessun audit dipendenze o fuzzing esaustivo.

#### Verdetto finale

**Geometria, provenienze geometriche, ID, ciclo sintetico e documentazione tecnica della nuova disposizione risultano coerenti con l'indicazione e con le prove eseguite. Nessuna collisione rilevata nelle forme disegnate; build e test superati.** Lo snapshot `f219e49` non riceve approvazione complessiva finché F6 non distingue esplicitamente le ipotesi sul flusso dalle affermazioni accertate. I precedenti finding F1–F5 non sono stati riaperti dalle verifiche effettuate.


## Revisione 3 — report di Codex su `11a0d31`

### Riverifica 3 — Salamai room3d, 11a0d31

Data: 28 ottobre 2026. Revisore indipendente: Codex.

**Commit esaminato:** `11a0d31c5f45eb3ed2c72d0d21b0f942ab08edc8`, HEAD detached nel worktree `/home/marco/lab/salamai-review`.

**Verdetto: approvato nel perimetro della revisione software e delle verifiche eseguite. F1–F5 risolti; nessun nuovo finding.** La build completa termina con exit 0, i **65 test** passano e la suite Chrome desktop/mobile passa. La correzione F5 è confermata da sonde indipendenti schema/runtime e da invocazioni CLI senza traceback sui casi richiesti. I limiti riportati sotto restano validi: questa approvazione non certifica misure fisiche, impianto o processo alimentare.

#### Perimetro e integrità

Letti `docs/room3d/REVIEW.md`, sezione Correzioni F5, e il diff `4337901..11a0d31`, inclusi schema, runtime, generatore sintetico, esempio, test e documentazione della migrazione. Confrontati i risultati con `CODEX_REVIEW_4337901.md` e le sonde delle revisioni precedenti.

Il diff riguarda sette file: README e REVIEW, schema ed esempio ciclo, `export_analysis.py`, `make_synthetic_cycle.py`, `test_analysis.py`. Non modifica generatore geometrico, frontend, sync-data o template Nginx. Il diff è salvato in `/tmp/salamai-review-11a0d31/diff.patch`.

Nessuna modifica ai sorgenti tracciati, nessun commit, nessun uso della scena condivisa o di MCP, nessuna scrittura nel worktree principale. Configurazioni e generatore modificati nelle sonde sono copie in `/tmp/salamai-review-11a0d31/`. La build standard scrive soltanto nel worktree di revisione; gli altri output sono in `/tmp`. Blender usa processi batch separati con `--factory-startup`.

`git diff --exit-code`, `git diff --cached --exit-code` e `git diff --check` risultano puliti. Prima della scrittura del presente report erano non tracciati soltanto i due report precedenti.

#### Comandi ed esiti

Ambiente come nelle revisioni precedenti: Blender 5.2.3 LTS, Python 3.14.4, Node v24.14.0, npm 11.9.0 e Chrome di sistema. `jsonschema` è disponibile: i controlli sullo schema sono stati realmente eseguiti, non saltati. Nessuna installazione aggiuntiva di librerie Python.

I comandi sono eseguiti dalla radice del worktree salvo indicazione diversa. Blender/build e browser sono stati eseguiti fuori sandbox con autorizzazione, per evitare i limiti ambientali già dimostrati nelle revisioni precedenti.

| Comando / prova | Esito ed evidenza |
|---|---|
| `git rev-parse HEAD`, `git status --short`, `git diff 4337901..11a0d31 --stat`, lettura del diff e delle correzioni | Commit corretto; sorgenti puliti; ispezione completata. |
| `tools/room3d/build_all.sh > /tmp/salamai-review-11a0d31-build.log 2>&1` | **Exit 0**. Validazione, due layout e otto PNG, GLB/manifest/blend, pacchetto sintetico, **65 test passati in 11,193 s**, npm ci, build web e controllo sola lettura. Nessun test segnalato come saltato. Gli errori previsti dai test negativi non costituiscono fallimenti. |
| `python3 /tmp/salamai-review-11a0d31/contract_probe.py` | **Exit 0**: 30 casi schema/runtime concordanti, più l'esatto ciclo legacy estratto dal commit `14b2495`. Log `contract_probe.log`, risultati strutturati `contracts.json`. |
| `python3 /tmp/salamai-review-11a0d31/variants.py` | **Exit 0**: prepara copie isolate di strumenti e configurazioni; la cornice nel solo generatore copiato cambia 15→20 mm. |
| `blender --background --factory-startup --python-exit-code 1 --python /tmp/salamai-review-11a0d31/variants/tools/build_scene.py -- --config /home/marco/lab/salamai-review/model/room3d/room.json --output /tmp/salamai-review-11a0d31/generator-change --no-render` | **Exit 0**, sonda F1. Log `generator-change.log`. |
| `python3 /tmp/salamai-review-11a0d31/probes.py` | **Exit 0**: CSV copiato con missing/invalid, qualità e disponibilità, warning di provenienza e rifiuto della geometria cambiata. Log `probes.log`. |
| `python3 /tmp/salamai-review-11a0d31/cli_probe.py` | **Exit 0** delle asserzioni della sonda: sette invocazioni CLI, migrazione storica e controlli mirati F1/F4. Log `cli_probe.log`. |
| `python3 tools/room3d/make_synthetic_cycle.py --build build/room3d --output /tmp/salamai-review-11a0d31/synthetic` | **Exit 0**, esempio rigenerato con 855 righe e contratto 1.1. Log `synthetic.log`. Successiva verifica con schema e `load_cycle`: accettato da entrambi, build ID L001 corretto. |
| `npm run e2e -- --out /tmp/salamai-review-11a0d31/e2e` in `web/room3d-viewer` | **Exit 0, tutte le verifiche superate**. Log `e2e.log`, screenshot nella directory `e2e`. |
| `view_image` su `/tmp/salamai-review-11a0d31/e2e/telefono_pannello.png` | Screenshot della revisione corrente ispezionato: pannello e avvisi leggibili, commit corretto, nessuna regressione visiva evidente rispetto alla revisione precedente. |
| `git diff --exit-code`, `git diff --cached --exit-code`, `git diff --check` | Nessuna modifica ai file tracciati o errore whitespace introdotto dalla revisione. |

I log indicati con nomi relativi sono in `/tmp/salamai-review-11a0d31/`.

#### F5 — Risolto: contratto 1.1 e validazione prima dei percorsi

Riferimenti esaminati: `model/room3d/cycles/cycle.schema.json`, `tools/room3d/export_analysis.py:35` e `:75`, `tools/room3d/make_synthetic_cycle.py`, sezione Collegamento ai cicli del README.

Lo schema richiede ora `build_id`, stringa esadecimale minuscola di 20 caratteri. `semantic_hash` è opzionale/null oppure SHA256 di 64 caratteri; sono specificati anche i formati di layout, config hash e commit. Il runtime controlla tipi e formati prima di costruire i percorsi. Il contratto passa esplicitamente a **1.1** e la migrazione da 1.0 è descritta sia nel messaggio d'errore sia nella documentazione.

##### Sonde schema/runtime indipendenti

Ogni caso usa una copia del JSON in `/tmp`. La verifica schema usa `jsonschema.Draft202012Validator`; il runtime usa `load_cycle`. Nessun caso seguente ha prodotto un'eccezione non gestita.

| Gruppo di casi | Schema | Runtime |
|---|---|---|
| Esempio attuale 1.1 | Accetta | Accetta |
| Contratto 1.0; versione sconosciuta 9.9 | Rifiuta | `AnalysisError`, codice 1 |
| `build_id` assente, intero 123, vuoto, `../../etc`, caratteri non esadecimali, lunghezza 19 o 21, null, booleano | Rifiuta | `AnalysisError`, codice 1, percorso `layout_refs[0].build_id` |
| `semantic_hash` testo `xyz`, intero, vuoto, 63 caratteri | Rifiuta | `AnalysisError`, codice 1, percorso del campo |
| `semantic_hash` null oppure assente | Accetta | Accetta, coerentemente con il carattere opzionale |
| `config_hash` corto o booleano | Rifiuta | `AnalysisError`, codice 1 |
| `layout_id` con `../`, vuoto o intero | Rifiuta | `AnalysisError`, codice 1 |
| `source_commit` non esadecimale o intero | Rifiuta | `AnalysisError`, codice 1 |
| `source_commit` esadecimale di 7 caratteri oppure null | Accetta | Accetta |
| `layout_refs` vuoto, oggetto anziché array, elemento intero anziché oggetto | Rifiuta | `AnalysisError`, codice 1 |

**Totale: 30 casi concordanti.** È una matrice mirata sui campi interessati da F5, non una dimostrazione di equivalenza esaustiva fra tutto lo schema e il runtime.

È stato anche estratto l'esatto esempio legacy con:

```bash
git show 14b2495:model/room3d/cycles/examples/SINTETICO_2026-01-10_0800/cycle.json
```

Schema e runtime lo rifiutano. Il runtime specifica che occorre aggiungere build ID/semantic hash dalla **build storica verificata**, impostare `schema_version` a 1.1 e non usare la build corrente al suo posto.

##### Ripetizione tramite CLI e migrazione

La sonda lancia realmente `python3 tools/room3d/export_analysis.py --cycle <copia> --build build/room3d --output <directory-in-tmp>` per legacy 1.0, build ID mancante/intero/vuoto/con percorso e semantic hash malformato. Tutti terminano con **exit 1**, messaggio `ERRORE:` e **nessun traceback**. L'esempio valido termina con **exit 0** e produce il pacchetto sintetico.

Per il ciclo legacy copiato è stata inoltre provata la procedura documentata: lettura del catalogo originale conservato dalla prima revisione in `/tmp/salamai-review-build2/catalog.json`, verifica del config hash, copia dei suoi build ID e semantic hash nel riferimento e passaggio a 1.1. Il nuovo esportatore accetta il ciclo così migrato con **exit 0**. Gli ID geometrici storici coincidono con quelli attuali, come già dimostrato nelle revisioni precedenti: non sono stati inventati riferimenti da una disposizione differente. La prova riguarda una copia sintetica, non modifica archivi reali.

L'esempio rigenerato da `make_synthetic_cycle.py` è anch'esso 1.1 e valido per schema e runtime. Non è più riproducibile il precedente `TypeError` con `build_id:123`.

#### F1–F4 — Conferma delle correzioni precedenti

| Finding | Stato | Test e sonda mirata della revisione corrente |
|---|---|---|
| **F1 — Alta**, identità revisioni e cache | **Risolto** | Passano test di identità, nomi con hash, riproducibilità, generatore modificato e rifiuto della geometria discordante. Ripetuta indipendentemente la modifica della cornice: stessa configurazione, build ID e directory differenti. `resolve_build` rifiuta il riferimento originale con codice 2 quando è disponibile solo la geometria modificata. |
| **F2 — Media**, zona osservata senza dati | **Risolto** | Passano test missing e copertura per intervallo. Sonda CSV tutta missing su T/UR: zona salami con `measured_by:[]`, nessuna quantità osservata, B1 indicata senza dati validi; messaggio globale coerente. B2 con peso missing ha zero campioni e avviso esplicito. |
| **F3 — Media**, istantanea con invalidi “ok” | **Risolto** | Passa `test_instant_flags_invalid_values`. Ripetuta sonda con NaN, testo non numerico, stato invalido e inf: istantanea null/“non valida” con `raw`, aggregato temperatura con due invalidi esclusi dai valori validi. |
| **F4 — Media**, testi statici di botola/porta | **Risolto** | Passano test dei testi derivati e della variante center. Sonda in memoria con center e porta misurata a 2 m: Y=0,175–0,625, testo “40 cm ... al centro”, porta “2,00 m (misurato)”, nessun suffisso provvisorio della porta. E2E verifica che il browser mostri i riepiloghi del manifest effettivamente caricato. |
| **F5 — Media**, schema/runtime dei cicli | **Risolto** | Matrice indipendente di 30 casi, legacy originale, CLI senza traceback, migrazione esplicita e generatore sintetico 1.1 descritti sopra. |

Risultati numerici della sonda F1:

- L001: `1ff600bc3a7b36eee701` → `28623ce848eb8dae6915` con cornice modificata;
- L900_DEMO: `274d53fea584bd3da762` → `62e442adc0fd2b92ee8b`;
- config hash invariati, directory diverse; warning esplicito anche per commit di provenienza differente.

La suite completa mantiene i controlli su coordinate di porta/botola, geometria dei fori, riapertura blend, Z-up/Y-up, scala, ID ed errori di configurazione. I build ID originali sono invariati rispetto alle revisioni precedenti.

La suite web passa su server statico nel sottopercorso `/salamai/room3d/`: caricamento, avvisi derivati, rotazione, layer, trasparenza e selezione interna, quote, misura porta **65,0 cm**, confronto per ID e camera sincronizzata. Passano gli errori manifest/GLB/WebGL e la verifica di richieste GET senza CDN. Sul telefono emulato 390×844 passano rotazione, pinch, selezione, pannello e assenza di overflow orizzontale. Non sono state osservate regressioni dovute al cambiamento del contratto dei cicli.

#### Nuovi finding

**Nessuno nel perimetro verificato.** Nessun F6 aperto. Conteggio: **0 critici, 0 alti, 0 medi, 0 bassi**.

#### Verifiche non eseguite e limiti

- Non eseguiti rilievi fisici, collegamenti a Home Assistant/dispositivi/Modbus o analisi di telemetria reale. Altezza e verso della porta, riferimento dei 40 cm e altre assunzioni restano dati da confermare. Nessuna validazione di portata o sicurezza alimentare.
- Non ripetuti Docker/Nginx e sonde HTTP/cache della revisione 2: template, sync-data, frontend e generatore geometrico sono invariati nel diff corrente. Le precedenti evidenze restano pertinenti a quei file; il presente report non le presenta come nuovi test runtime di Nginx.
- Non rigenerata e ispezionata nuovamente una variante center nel PNG e nel browser: questa volta center/porta misurata sono verificati da test e sonda mirata Python; il browser verifica i testi del manifest del layout di default. Il controllo PNG/browser della variante center era stato riprodotto nella revisione 2.
- Gli otto PNG originali sono stati rigenerati dalla build, ma non ispezionati tutti manualmente in questa riverifica. È stato ispezionato lo screenshot mobile corrente; nessun controllo in Blender GUI o via MCP. Motore di build Workbench, Cycles non riprovato.
- Chrome headless/SwiftShader con touch emulato; non dispositivi fisici, Safari/iOS, Firefox o ogni viewport. Non ripetuta su mobile l'intera sequenza desktop di misure/confronto/errori. Accessibilità e pan non verificati con prove dedicate.
- Le sonde schema/runtime coprono i casi elencati; non eseguiti fuzzing o verifica esaustiva di ogni campo, timestamp, fuso e possibile struttura JSON. Il validatore schema delle sonde non attiva un controllo aggiuntivo dei formati date-time. Il confronto mirato riguarda versioni e riferimenti interessati da F5.
- Nessuna migrazione di cicli reali né recupero da archivi esterni; solo esempio sintetico e artefatti storici locali della revisione. La disponibilità di una build storica verificabile rimane necessaria.
- Nessun audit dipendenze, benchmark, pubblicazione o modifica della scena condivisa.

#### Verdetto finale

**F1–F5 chiusi sul commit `11a0d31c5f45eb3ed2c72d0d21b0f942ab08edc8`. Nessun nuovo finding rilevato.** Le evidenze riprodotte supportano l'approvazione dello snapshot nel perimetro software esaminato, con i limiti espliciti sopra. Qualsiasi revisione successiva dei sorgenti richiederà una verifica riferita al suo commit.


## Revisione 2 — report di Codex su `4337901`

### Riverifica indipendente Salamai room3d — 4337901

Data: 28 ottobre 2026. Revisore: Codex.

**Commit esaminato:** `433790103d06f5fb81c1c1052b18eb2ca239a623`, HEAD detached nel worktree `/home/marco/lab/salamai-review`.

**Esito:** F1–F4 **risolti** nelle riproduzioni descritte sotto. **Nuovo finding F5, gravità media**, sul contratto/schema dei cicli e la validazione del nuovo campo obbligatorio. **Modifiche richieste prima dell'approvazione complessiva dello snapshot.** Nessun nuovo finding critico, alto o basso.

#### Perimetro e integrità

Letti la sezione “Correzioni” di `docs/room3d/REVIEW.md`, il report precedente `CODEX_REVIEW_14b2495.md` e il diff completo `14b2495..4337901`, con successiva lettura mirata dei file modificati e dei consumatori: generatore, esportatore, schema e esempio ciclo, test, frontend, sync-data e template Nginx. Diff salvato in `/tmp/salamai-review-4337901.diff`.

Nessuna modifica all'implementazione, ai JSON autorevoli o alla scena condivisa, nessun commit e nessun accesso MCP. Tutte le mutazioni delle sonde sono su copie in `/tmp/salamai-review-4337901/`. Build e output applicativi sono nel worktree di revisione o in `/tmp`. I processi Blender sono batch indipendenti con `--factory-startup`. Non è stato utilizzato il worktree principale.

Sono stati autorizzati comandi fuori sandbox per Blender, npm, Chrome e Docker. Creati per la prova l'immagine locale `salamai-room3d-review:4337901` e il container temporaneo `salamai-review-4337901`, esposto soltanto su `127.0.0.1:18089`; il container è stato **arrestato e rimosso automaticamente** al termine. Nessun deploy su infrastrutture reali. Le immagini Docker restano nella cache locale del daemon.

Prima della scrittura del report, `git diff --exit-code`, `git diff --cached --exit-code` e `git diff --check` sono puliti; risultava non tracciato soltanto il report precedente. Il presente report è un ulteriore file non tracciato.

#### Comandi ed esiti riprodotti

Ambiente: Blender 5.2.3 LTS, Python 3.14.4, Node v24.14.0, npm 11.9.0, Chrome di sistema. Comandi dalla radice del worktree salvo diversa indicazione. Per le tre build Blender isolate sotto, il prefisso comune è:

```bash
blender --background --factory-startup --python-exit-code 1 --python <script> -- <argomenti>
```

| Comando / prova | Esito |
|---|---|
| `git rev-parse HEAD`, `git status --short`, `git diff --stat 14b2495..4337901`, `git diff 14b2495..4337901` | Commit corretto; modifiche tracciate assenti; ispezione del diff effettuata. |
| `tools/room3d/build_all.sh > /tmp/salamai-review-4337901-build.log 2>&1` | **Exit 0**: due layout, otto PNG, GLB/manifest/blend, pacchetto sintetico, **62 test passati** in 11,234 s, npm ci, build Vite e controllo sola lettura. Gli `ERRORE` nel log durante i test negativi sono attesi: la suite termina `OK`. |
| `npm run e2e -- --out /tmp/salamai-review-4337901/e2e` in `web/room3d-viewer` | **Exit 0, tutte le verifiche superate**, log `/tmp/salamai-review-4337901/e2e.log`. Server statico sotto `/salamai/room3d/`. |
| `python3 /tmp/salamai-review-4337901/variants.py` | **Exit 0**. Copia generatore e JSON in `/tmp`; cornice nel solo generatore copiato 15→20 mm; variante center nel solo JSON copiato, con riallineamento estrattore/valvola/primi due punti del tubo a Y=0,40, come nella sonda precedente. |
| Build Blender, script `/tmp/salamai-review-4337901/variants/tools/build_scene.py`, argomenti `--config /home/marco/lab/salamai-review/model/room3d/room.json --output /tmp/salamai-review-4337901/generator-change --no-render` | **Exit 0**, log `generator-change.log`: verifica F1, configurazione originale invariata. |
| Build Blender, script `tools/room3d/build_scene.py`, argomenti `--config /tmp/salamai-review-4337901/variants/model/room.json --output /tmp/salamai-review-4337901/center --layout L001` | **Exit 0**, quattro viste della variante center; log `center.log`. |
| Build Blender originale, argomenti `--config model/room3d/room.json --output /tmp/salamai-review-4337901/repeat --no-render` | **Exit 0**, log `repeat.log`; confronto indipendente di hash/ID con la build completa in `repro.log`. |
| `python3 /tmp/salamai-review-4337901/probes.py` | **Exit 0**, sonde CSV missing/invalid, provenienza e rifiuto generatore modificato. Risultati in `probes.log`. |
| `python3 /tmp/salamai-review-4337901/contracts.py` | **Exit 0**, verifica archiviazione della build originale accanto a quella modificata, intervalli layout, hash dei file, sync-data valido e rifiuto di immagini/manifest/GLB corrotti, schema legacy e nuovo campo numerico. Risultati in `contracts.log`. Usa `jsonschema` già disponibile, senza installazioni aggiuntive. |
| Sonda `ea.main(...)` con `build_id=123` nel solo ciclo copiato | Riprodotta **TypeError non gestita**; lo script di sonda la intercetta e la stampa in `schema-runtime.log`. Dettaglio F5. |
| `node /tmp/salamai-review-4337901/browser-probe.mjs` | **Exit 0**, bundle originale servito con asset center da `/tmp`; lettura di manifest e testo UI in `browser-probe.log`, screenshot `center-browser.png`. |
| `docker image inspect nginx:1.30.5-alpine` | Prima prova nel sandbox: accesso socket negato; riesecuzione autorizzata: base non presente. Non attribuiti come difetti dello snapshot. |
| `docker build -f deploy/Dockerfile -t salamai-room3d-review:4337901 .` da `web/room3d-viewer` | **Exit 0**, base scaricata, log `docker-build.log`. |
| `docker run -d --rm --name salamai-review-4337901 -p 127.0.0.1:18089:8080 salamai-room3d-review:4337901` | **Exit 0**, istanza locale isolata. |
| `npm run e2e -- --url http://127.0.0.1:18089/salamai/room3d/ --out /tmp/salamai-review-4337901/e2e-nginx` | **Exit 0, tutte le verifiche superate**, log `e2e-nginx.log`. |
| `python3 /tmp/salamai-review-4337901/http_probe.py` | **Exit 0** della prova HTTP riuscita: cache, regex, tipi MIME, 304 e 405; log `http.log`. Un primo script chiamato `http.py` interferiva con l'import del modulo standard: rinominato prima della riesecuzione; errore della sonda, non dell'implementazione. |
| `docker exec salamai-review-4337901 nginx -t`, `docker stop salamai-review-4337901` | Sintassi Nginx **valida**; arresto riuscito. |
| `view_image` | Ispezionati la sezione A center, lo screenshot browser center, la pianta L001 rigenerata e gli screenshot confronto desktop/pannello mobile della suite Nginx. |

Tutti i log con nomi relativi nella tabella sono in `/tmp/salamai-review-4337901/`.

#### Stato dei finding precedenti

| Finding | Stato | Evidenza decisiva |
|---|---|---|
| **F1 — Alta**, identità revisioni/generatore e cache | **Risolto** | La cornice modificata cambia build ID e directory; il ciclo originale è rifiutato con codice 2 se la build originale manca. Recupero archivio originale riuscito; nomi asset verificati tramite SHA e cache Nginx verificata sul container. |
| **F2 — Media**, zona osservata senza dati | **Risolto** | Tutti missing: `measured_by:[]`, zona “NON OSSERVATA”, zero campioni validi, sonde elencate senza dati. Due intervalli: copertura separata correttamente. |
| **F3 — Media**, invalidi nell'istantanea “ok” | **Risolto** | NaN/testo/stato invalido diventano null con qualità “non valida” e `raw`; inf conteggiato invalido negli aggregati. Suite specifica passata. |
| **F4 — Media**, testi fissati per botola/porta | **Risolto** | Center: coordinate Y=0,175–0,625, cartiglio e browser riportano “40 cm ... al centro”; quota al bordo 17,5 cm. Test porta misurata passato. |

##### F1: prove di identità, recupero e cache

Le revisioni originali mantengono build ID **L001 `1ff600bc3a7b36eee701`**, **L900_DEMO `274d53fea584bd3da762`**. Directory ora `layouts/<id>/<build_id>`. La seconda build originale mantiene config hash, semantic hash, build ID, SHA GLB e tutti gli ID/hash delle entità: rispettivamente **35 e 34 oggetti**. Il manifest cambia hash per metadati/immagini della build: ciò è compatibile con la nuova policy `no-cache`.

Sonda indipendente cornice 15→20 mm nella copia del generatore:

| Layout | Config hash | Build ID originale → modificato |
|---|---|---|
| L001 | Invariato | `1ff600bc3a7b36eee701` → `28623ce848eb8dae6915` |
| L900_DEMO | Invariato | `274d53fea584bd3da762` → `62e442adc0fd2b92ee8b` |

Per L001 il semantic hash cambia da `1556fc63c52529de0cf0ff8675cd526d12efda987958b010763bbc032fc8b769` a `13b6b084dc8040a89f1a463d640a6e7a80c81125cd81ffe68e8d8ddc44fb0e29`. `resolve_build` sul riferimento originale contro la sola build modificata produce **AnalysisError codice 2**, senza usare il layout corrente. Copiando la revisione originale nell'archivio che contiene quella modificata, viene recuperato il build ID originale anche se non è nel catalogo corrente. Il test aggiunto sul semantic hash discordante passa nella suite completa.

Il diverso commit dei sorgenti è ora segnalato in `provenance_warnings`, riprodotto con un commit deliberatamente inesistente: la geometria vincolata dal build ID viene accettata ma la provenienza diversa è esplicita. Questo è un comportamento ragionevole e documentato; non equivale a una verifica dell'esistenza del commit.

SHA verificati per tutti gli otto PNG rispetto a manifest e suffisso del nome. Esempi di asset originali:

- `layouts/L001/1ff600bc3a7b36eee701/model-9404e99e8abf72ad.glb`;
- `layouts/L001/1ff600bc3a7b36eee701/views/pianta-3d487e7ee11b0e14.png`.

Sul container reale:

| Risorsa / richiesta | HTTP | Cache-Control |
|---|---:|---|
| Index, catalogo, manifest | 200 | `no-cache` |
| GLB con SHA16 | 200 | `public, max-age=31536000, immutable` |
| PNG con SHA16 | 200 | `public, max-age=31536000, immutable` |
| Vecchio nome `model.glb` | 404 | `no-cache` |
| Nome con `X` invece del punto prima dell'estensione | 404 | `no-cache` |
| Nome con soli 15 caratteri hash | 404 | `no-cache` |
| Manifest con `If-None-Match` usando ETag ricevuto | 304 | `no-cache` |
| POST, PUT, DELETE sul catalogo | 405 | — |

La regex quotata funziona nella configurazione risultante di Nginx: non ho riprodotto errori di sintassi o un punto interpretato come carattere jolly. I tipi MIME GLB/PNG/JSON sono corretti. Non è stato riprodotto un rollout concorrente completo: qui sono verificati identità, header, riconvalida e caricamento dal container.

##### F2: missing e disponibilità per intervallo

Nel CSV copiato, `temperatura` e `umidita` tutte `unknown` producono per `zone_salami`:

```json
{
  "measured_by": [],
  "quantities": [],
  "sensors_without_valid_data": ["sensor_b1_sth01"],
  "observation": "NON OSSERVATA: sonda presente ma nessun dato valido nell'intervallo"
}
```

Con `peso_g` tutto `unknown`, B2 ha `valid_samples:0`, `coverage_pct:0.0` e `data:"NESSUN DATO VALIDO nell'intervallo"`. La sua presenza nel catalogo dei punti di misura è ora esplicitamente distinta dalla disponibilità dei campioni. Il messaggio globale non dichiara più la sonda B1 osservante in assenza di dati.

Prova supplementare di cambio layout a `2026-01-11T14:00:00`: L001 contiene **360 righe**, di cui **348** valide per ciascuna T/UR; L900_DEMO contiene **495 righe** con T/UR mancanti e **0 campioni validi**. `zone_salami.measured_by` è `[sensor_b1_sth01]` soltanto nel primo intervallo ed è vuoto nel secondo. Nessun trasferimento della copertura globale al layout privo di dati.

##### F3: classificazione coerente degli invalidi

Nella prima riga copiata: `temperatura=NaN`, `umidita=nonsense`, `stufa=forse`; nella seconda `temperatura=inf`. L'istantanea al primo timestamp restituisce per NaN e testo **`value:null`, `quality:"non valida"`**, con il valore originale in `raw`. Gli aggregati temperatura contano **2 invalidi**, non li usano nella media. La suite aggiunta verifica anche lo stato invalido, `fase` valida e i valori numerici validi esportati come numeri. L'implementazione usa lo stesso `classify` per aggregati e istantanea.

##### F4: cartiglio e browser center

Variante renderizzata con il generatore originale: build ID `093d0ffdf3b8c2765b57`; botola **Y=0,175–0,625**, centro **Y=0,40**. Il cartiglio della sezione A recita:

> Botola: 40 cm dalla parete porta al centro (Y 0,175–0,625 m); riferimento al centro = ASSUNZIONE NON CONFERMATA.

La quota al bordo è **17,5 cm ASSUNTO**. In pianta la label derivata è `17,5 cm ASSUNTO: 40 cm al centro`. La nota dell'entità e quella del soffitto seguono i dati. L'immagine ispezionata è `center/layouts/L001/093d0ffdf3b8c2765b57/views/sezione_A_x-358d50e8ed95d991.png` sotto la directory di prova.

La sonda Chrome carica i reali asset center e legge dal pannello esattamente il riepilogo center del manifest, senza la precedente frase errata sul bordo vicino. Screenshot `/tmp/salamai-review-4337901/center-browser.png`. La porta resta sconosciuta con valore provvisorio 1,90 m in questa variante; il test `test_opening_texts_follow_data`, eseguito nella suite, verifica separatamente altezza misurata 2,00 m, testo “misurato” e quota 200 cm senza suffisso provvisorio.

#### Regressioni e controlli aggiuntivi

- **sync-data:** eseguita una copia dello script, così anche la sua `public/data` di destinazione è in `/tmp`. Input valido accettato con exit 0. Corruzione indipendente di un PNG, del manifest e del GLB produce exit 1 con errore specifico. Il worktree servito non è stato alterato da queste sonde. Copia ed errori del nuovo controllo SHA immagini funzionano.
- **Compatibilità cicli:** l'esempio aggiornato contiene build ID e semantic hash e funziona. Un ciclo legacy senza build ID viene rifiutato, senza attribuzione silenziosa alla build corrente; questa scelta è sicura, ma schema e gestione dei tipi presentano F5. Non è stata eseguita una migrazione automatica di dati storici reali.
- **Suite web su due server:** entrambe passano il nuovo controllo degli avvisi dal manifest, selezione, layer, trasparenza, 15 quote, misura porta **65,0 cm**, confronto per ID e camera sincronizzata, gestione errori e assenza di richieste di scrittura/CDN. Mobile emulato 390×844: rotazione, pinch, selezione, pannello e nessun overflow orizzontale. La nuova route di intercettazione `model-*.glb` esercita correttamente il caso GLB errato.
- **Geometria originale:** i 62 test comprendono riapertura blend, fori reali di porta/botola, coordinate, Z-up/Y-up e scala, riproducibilità, cambio parametro senza duplicati e invalidi. I build ID e gli hash semantici originali sono rimasti quelli della revisione precedente: le correzioni non hanno modificato la geometria di default.
- **Test aggiunti:** passano sia la mutazione reale del generatore nella copia temporanea sia i casi sintetici di disaccordo degli hash, provenienza diversa, intervalli e invalidi. Non sostituiscono le sonde indipendenti sopra, che sono state ripetute esplicitamente. Manca una verifica di coerenza schema/runtime per i nuovi campi, come dimostra F5.

#### Nuovi finding

##### F5 — Media — Il contratto JSON dei cicli non descrive il nuovo build_id obbligatorio; il runtime non ne valida il tipo

**File:** `model/room3d/cycles/cycle.schema.json:23`, `tools/room3d/export_analysis.py:72`, `tools/room3d/export_analysis.py:112`.

**Evidenza riprodotta:** il diff non aggiorna lo schema dei cicli. Lo schema, sempre versione 1.0, richiede solo `layout_id`, `config_hash`, `valid_from` e non definisce `build_id` né `semantic_hash`. Invece `load_cycle` richiede ora `build_id` e `resolve_build` lo passa direttamente a `os.path.join`.

1. Estratto con `git show 14b2495:model/room3d/cycles/examples/SINTETICO_2026-01-10_0800/cycle.json` il ciclo precedente in una copia `/tmp`. `jsonschema.Draft202012Validator(schema).validate(...)` lo **accetta**, ma `load_cycle` lo rifiuta con **AnalysisError codice 1: `layout_refs[0]: 'build_id' mancante`**.
2. Nel ciclo nuovo copiato imposto `build_id:123`. Lo schema lo **accetta**, poiché il campo non è descritto e le proprietà aggiuntive sono ammesse. `load_cycle` supera il solo controllo di presenza; `ea.main(...)` arriva a un'eccezione **TypeError non gestita: `join() argument must be str, bytes, or os.PathLike object, not 'int'`**, invece di un errore di configurazione leggibile. La sonda la intercetta soltanto per registrarla; il comando CLI normale produrrebbe traceback.

Log: `/tmp/salamai-review-4337901/contracts.log` e `schema-runtime.log`. Il runtime Python è dichiarato autorevole, ma lo schema è comunque il contratto pubblicato e non dovrebbe accettare documenti incompatibili con la nuova identità delle revisioni.

**Impatto:** produttori/editor/validatori che usano lo schema possono continuare a generare cicli formalmente validi ma non esportabili; un nuovo campo mal tipizzato causa un errore non gestito. I vecchi cicli 1.0 richiedono integrazione esplicita dei riferimenti da artefatti storici, senza che la stessa versione dello schema renda visibile il cambiamento. Non è dimostrata una perdita di dati o un'associazione silenziosa al layout errato: il problema è interoperabilità e diagnosi degli errori.

**Correzione proposta:** allineare lo schema a `build_id` obbligatorio, stringa con formato definito, e `semantic_hash` opzionale con formato SHA256; validare questi campi nel runtime prima di costruire percorsi, restituendo `AnalysisError` con percorso del campo. Rendere esplicita la compatibilità/versione del contratto e documentare come integrare un ciclo legacy usando la sua build storica verificata, senza fallback alla build corrente. Aggiungere test schema/runtime per campo mancante, intero, stringa vuota/formato invalido e semantic hash malformato, oltre all'esempio aggiornato.

#### Verifiche non eseguite e limiti

- Non eseguiti rilievi fisici, accessi a Home Assistant/dispositivi/Modbus, telemetria reale o verifica del trattamento alimentare. Nessuna assunzione di progetto viene promossa a misura reale.
- Rendering Workbench; non riprovato Cycles o Blender GUI/MCP. Le due build isolate e i test batch verificano file derivati senza usare la scena condivisa.
- Ispezione visiva mirata al cartiglio center, pianta originale e screenshot citati; non ripetuta manualmente l'ispezione di tutte le otto viste rigenerate, già controllate sul precedente snapshot. Le otto viste sono comunque rigenerate e i relativi SHA verificati.
- Chrome headless/SwiftShader e touch emulato; non telefoni fisici, Safari/iOS, Firefox o tutte le viewport. Non ripetuta su mobile tutta la sequenza desktop di misura, confronto ed errori; pan e accessibilità tastiera/screen reader non verificati con sonde dedicate.
- Nginx verificato sul sottopercorso di default. Non provati altri SUBPATH, reverse proxy reali, rollout concorrenti o cache persistenti attraverso pubblicazioni successive. La prova 304 riguarda un manifest invariato; non è una simulazione di tutte le race di deploy.
- Porta misurata verificata dal test Python eseguito; non costruita una seconda variante render/browser con altezza 2,00 m. La variante center con porta ignota è stata invece verificata nel PNG e nel browser reali.
- Nessun fuzzing esaustivo, audit dipendenze o benchmark. F5 non implica che gli altri campi del contratto siano stati sottoposti a validazione esaustiva.

#### Verdetto

**Le correzioni di F1–F4 sono confermate da evidenza riprodotta e i quattro finding sono chiusi.** Build completa, 62 test e suite browser passano, anche sul container Nginx. **Lo snapshot 4337901 richiede ancora la correzione di F5 prima dell'approvazione complessiva**, con nuova verifica della coerenza schema/runtime e del comportamento sui cicli legacy/malformati. Nessuna approvazione della scena condivisa o dell'impianto reale è implicita.


## Revisione 1 — report di Codex su `14b2495`

### Revisione indipendente Salamai room3d — 14b2495

Data: 28 ottobre 2026. Revisore: Codex.

**Commit esaminato:** `14b2495136eea9c2583a1e8b5f695a95ce7ca470`, HEAD detached nel worktree `/home/marco/lab/salamai-review`, snapshot indicato di `feat/room3d`.

**Verdetto: modifiche richieste; snapshot non approvato.** La build completa, i 54 test Python e la suite browser passano, ma restano **4 finding: 1 alta, 3 media, 0 bassa, 0 critica**. In particolare l'identità usata per conservare e recuperare le revisioni non vincola la geometria prodotta dal generatore.

#### Perimetro e integrità

Letti prima `docs/room3d/REVIEW.md`, la sezione 2 di `documentazione/Salamai_Blender_Claude_Herdr_Codex.md`, `docs/room3d/README.md` e `docs/room3d/ASSUMPTIONS.md`. Ispezionati configurazioni stanza/layout, mapping e contratto ciclo, validatore, generatore, esportatore analisi, test, frontend Three.js, sincronizzazione asset, lockfile e configurazione Docker/Nginx. Confrontati i mapping principali con `homeassistant/salumi_log.py`, `homeassistant/salumi.yaml` e i firmware ESPHome presenti.

Nessuna modifica ai file tracciati, nessun commit, nessun collegamento alla scena Blender condivisa o al socket MCP. Non usato il worktree principale per build o modifiche. Blender è stato avviato in processi batch separati con `--factory-startup`; gli output sono in questo worktree e in `/tmp`. Le mutazioni sperimentali descritte sotto riguardano esclusivamente copie in `/tmp`. `git diff --exit-code` e `git diff --cached --exit-code` risultano puliti prima della scrittura del report.

Un comando iniziale di ricerca `find .. -name AGENTS.md -print`, troppo ampio, è stato interrotto: ha elencato percorsi di repository adiacenti e ricevuto alcuni errori di permesso. Nessun file d'implementazione esterno è stato modificato o usato come input della revisione. Il controllo mirato successivo dei file AGENTS negli antenati e nel worktree non ha trovato istruzioni applicabili.

#### Ambiente e comandi eseguiti

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

#### Controlli positivi sullo snapshot

##### Coordinate, quote e geometria

- Stanza interna **3,03 × 1,60 × 2,10 m**; volume lordo **10,1808 m³**, distinto esplicitamente dal volume libero.
- Porta sulla parete Y=0, **X=1,04–1,69**, centro **1,365 m**, luce **0,65 m**. Altezza `unknown` con `value:null`, disegno a **1,90 m**, marcato provvisorio.
- Botola **X=1,205–1,525**, **Y=0,40–0,85**, centro **(1,365; 0,625)**, **Z=2,10 m**, dimensioni **0,32 × 0,45 m**. Interpretazione dei 40 cm al bordo vicino esplicitamente assunta e non confermata.
- Il parametro center produce correttamente **Y=0,175–0,625**, centro Y=0,40; la geometria funziona, la comunicazione presenta F4.
- Tolleranza configurata **0,0005 m**; i test sulle aperture usano anche tolleranze più strette per i valori derivati. Il test d'integrazione sul GLB usa **0,0001 m** sugli ingombri trasformati.
- La suite riapre il `.blend` e verifica con raggi la luce libera di porta e botola, oltre a parete e soffitto pieni. Quindi le aperture non sono semplici rettangoli sovrapposti.
- Spessori convenzionali esterni al volume interno; tre ventole di ricircolo distinte dall'estrattore, frecce nominali non simulate; placeholder prodotto e geometrie provvisorie riconoscibili.
- Il percorso del tubo contiene tratti e raccordi con ID e raggi; la lunghezza deriva da tratti + archi, non da una dichiarazione di acquisto. Lo scarto rispetto ai 3 m acquistati è documentato. Non sono inventati coefficienti di perdita o portate da PWM/RPM.

##### Z-up/Y-up, ID e riproducibilità

Trasformazione canonica → glTF **(x,y,z) → (x,z,−y)**, inversa **(xg,yg,zg) → (xg,−zg,yg)**. Esportazione Y-up esplicita; test su soffitto, parete di fondo, ventola, tubo, anta ed estrattore verificano orientamento e scala. Nel browser `FrameTransform` è condiviso da quote, hit test convertito e misure; lo snap applica prima la `matrixWorld` del vertice.

Due build originali indipendenti hanno gli stessi ID, config hash, semantic hash, build ID e SHA256 GLB, per entrambi i layout. Non è stata richiesta identità binaria del `.blend`. I manifest hanno SHA diversi per metadati/immagini di build, come atteso dai due invocamenti; il problema degli URL immutabili è discusso in F1.

| Layout | Oggetti | Config hash | Semantic hash | Build ID |
|---|---:|---|---|---|
| L001 | 35 | `e6524a05288a297be4751cb6faff4af62fb90e8a7a84e4615c82b6bc341de87d` | `1556fc63c52529de0cf0ff8675cd526d12efda987958b010763bbc032fc8b769` | `1ff600bc3a7b36eee701` |
| L900_DEMO | 34 | `9787bd0a77d91e8a53127eb1805f8cdd160a4492c0a3812f7bf4a40ecf9cfdbe` | `f1d6990a44465513db60e33dbfb7afcb13054668663a2e6a57cd8f1fe828574f` | `274d53fea584bd3da762` |

Testata l'uguaglianza fra nomi/ID dei nodi GLB e manifest, extras degli oggetti e build ID della scena. Cambio parametro senza duplicazione degli ID verificato dalla suite. Validazione negativa coperta per dimensioni negative, duplicati, assi nulli/non normalizzati, aperture fuori stanza, NaN/Inf nella configurazione, unknown con valore e componenti esterni non motivati.

##### Associazione cicli, provenienza e immagini

L'esempio è inequivocabilmente sintetico: cartella, `synthetic:true`, avviso e README del pacchetto. Il test verifica che il suo config hash coincida con L001. Superati test di cambio layout durante ciclo, intervalli sovrapposti, letture fuori validità e revisione assente: quest'ultima restituisce codice 2 invece di applicare il layout corrente. F1 riguarda il caso diverso di stessa configurazione con generatore cambiato.

Mapping corrente T/UR/stufa/umidificatore coerente con le stringhe del logger; firmware con due soli ingressi giri, terza ventola non risolta; canale umidificatore non attribuito arbitrariamente a M2/M3. Identificativi futuri sono marcati non verificati. Non verificata l'esistenza effettiva di questi ID su un'installazione HA attiva.

Carichi e rimozioni sono eventi; non si dichiara vuoto il lato sinistro dopo tre giorni. Osservazioni, inferenze e ipotesi sono sezioni separate e non compaiono campi di velocità o conclusioni automatiche di sicurezza alimentare. Restano i difetti di qualità F2/F3.

Gli otto PNG sono leggibili alla risoluzione prodotta, con cartiglio, quote esterne, richiami e assi. I due layout sono distinguibili e il demo è esplicitamente un'ipotesi, non uno storico. In alcune proiezioni componenti si sovrappongono geometricamente, ma i richiami permettono di identificarli; non ho rilevato un difetto bloccante nella leggibilità delle viste di default. La griglia disegnata in posizione di porta chiusa mentre l'anta è aperta è una convenzione esplicitamente annotata nel layout, non una misura in opera.

##### Visualizzatore web

Verificati runtime con Chrome headless e server statico nel sottopercorso `/salamai/room3d/`, con asset locali e senza dipendenze runtime da Blender/MCP. La suite effettua soltanto GET e non richiede risorse esterne; 33 richieste GET/HEAD complessive registrate dal server. Lettura del codice e controllo statico del bundle non mostrano percorsi per salvare configurazioni o comandare dispositivi.

Su desktop: caricamento, rotazione mouse, layer nascosti non selezionabili, parete opaca/trasparente con selezione della sonda interna, pannello componente e assunzioni, 15 quote, misura della luce porta **65,0 cm** con coordinate canoniche, confronto e sincronizzazione camera. Nel confronto risultano correttamente spostamento fan_02, orientamento fan_03, aggiunte/rimozioni e percorso tubo modificato; demo etichettato. Gestiti layout inesistente, manifest 404, GLB incompatibile/non corrispondente e WebGL assente. Nessun errore JavaScript nel percorso nominale testato.

Su viewport mobile **390×844**, touch emulato: rotazione a un dito, pinch a due dita, selezione della stufa e apertura pannello, assenza di overflow orizzontale della pagina. Screenshot ispezionati: comandi distribuiti su più righe, modello visibile, pannello scorrevole. Questo non equivale a certificazione su dispositivi fisici o su ogni dimensione schermo.

Coerenza asset: `sync-data.mjs` verifica SHA manifest/GLB del catalogo prima della copia; caricamento browser verifica versione, layout/build ID, SHA GLB quando Web Crypto è disponibile, extras della scena e corrispondenza completa degli ID. Questi controlli rilevano diverse mescolanze, ma non correggono la collisione di percorsi fra build differenti di F1.

#### Finding

##### F1 — Alta — La revisione identificata dal ciclo e dagli URL non include il generatore

**File:** `tools/room3d/room3d_core.py:115`, `tools/room3d/build_scene.py:648`, `tools/room3d/build_scene.py:653`, `tools/room3d/export_analysis.py:99`; rilevante anche `web/room3d-viewer/deploy/nginx.conf.template` (cache immutable).

**Evidenza:** `config_hash` include soltanto JSON stanza + layout. `build_id` include anche l'hash semantico, ma la directory continua a essere `layouts/<layout_id>/<config_hash[:12]>`. `resolve_build` controlla il config hash, senza vincolare semantic/build ID o verificare `source_commit` del riferimento.

Riproduzione eseguita: nella sola copia `/tmp/salamai-review-variants/tools/room3d_core.py`, cambio della cornice generata da 15 a 20 mm, poi build sugli stessi JSON originali. Entrambi i layout mantengono **stesso config hash e stesso percorso**, ma hanno **semantic hash e build ID diversi**. Per L001 il semantic hash diventa `13b6b084dc8040a89f1a463d640a6e7a80c81125cd81ffe68e8d8ddc44fb0e29`. Passando all'esportatore il riferimento del ciclo sintetico originale e questa nuova build, `resolve_build` la accetta. Un ulteriore probe con `source_commit` deliberatamente diverso viene ugualmente accettato.

**Impatto:** una correzione legittima al generatore può sovrascrivere la geometria associata a cicli pregressi senza cambiare il riferimento registrato. Gli URL dichiarati immutabili possono cambiare contenuto: cache vecchie possono mostrare una vecchia revisione o provocare errori di incompatibilità con il nuovo catalogo. Anche il manifest cambia per timestamp/metadata sotto lo stesso URL tra rigenerazioni originali.

**Correzione proposta:** distinguere hash configurazione e identità completa dell'artefatto. Conservare revisioni con chiave che includa geometria/generatore e pin del ciclo a build/semantic hash o equivalente verificabile; controllare la provenienza dichiarata. Per file con cache immutable usare URL basati sul contenuto effettivo, oppure non riscrivere un artefatto già pubblicato e spostare metadata variabili fuori dalla revisione. Aggiungere test che cambino solo il generatore e provino sia il recupero storico sia la pubblicazione con cache.

##### F2 — Media — Una zona viene dichiarata osservata anche senza alcuna misura valida

**File:** `tools/room3d/export_analysis.py:236`, `tools/room3d/export_analysis.py:253`, `tools/room3d/export_analysis.py:259`.

**Evidenza:** `measurement_points` viene popolato dalla presenza del mapping, non dalla disponibilità di letture valide. `sensors_in` controlla colonna e posizione ma non la copertura; `sensors_without_data` esclude quindi anche sonde mappate senza dati.

Riproduzione `/tmp/salamai-review-probes.py`: nella sola copia CSV, tutte le letture `temperatura` e `umidita` diventano `unknown`. Il pacchetto continua a riportare per `zone_salami`:

```json
{"measured_by":["sensor_b1_sth01"],"observation":"osservata da una sola sonda puntuale"}
```

Il probe con `peso_g=unknown` per l'intero ciclo mostra analogamente B2 tra i punti misurati con copertura **0,0%**. La disponibilità non viene inoltre ricalcolata nell'intervallo di ciascun layout quando un ciclo ne contiene più di uno.

**Impatto:** il pacchetto AI comunica una zona come osservata anche quando contiene solo missing; la distinzione fra collocazione di progetto di una sonda e osservazione effettiva risulta ambigua proprio nei cicli incompleti.

**Correzione proposta:** separare sonde previste/mappate da sonde con campioni validi, calcolare copertura per quantità e intervallo di layout e dichiarare esplicitamente `nessun dato valido` quando è zero. Derivare `measured_by` e `sensors_without_data` dalla disponibilità effettiva, mantenendo comunque l'incertezza della posizione. Testare colonna assente, tutti missing/invalid e dati disponibili solo prima/dopo un cambio layout.

##### F3 — Media — Il dettaglio per istante assegna qualità “ok” a valori numerici invalidi

**File:** `tools/room3d/export_analysis.py:292`.

**Evidenza:** `column_stats` riconosce stringhe non numeriche e valori non finiti, ma il ramo `--at` verifica soltanto i sentinel mancanti e l'età del record. Nella copia CSV il primo campione contiene `temperatura=NaN` e `umidita=nonsense`; esportando esattamente il timestamp della prima riga si ottiene:

```json
"temperatura": {"value":"NaN","unit":"°C","quality":"ok"},
"umidita": {"value":"nonsense","unit":"%","quality":"ok"}
```

Nello stesso pacchetto l'aggregato temperatura conta correttamente un campione `invalid`. Riproduzione e risultati in `/tmp/salamai-review-probes.py` e `.log`.

**Impatto:** un consumatore dell'istantanea può trattare come misura valida un errore del logger o un valore non finito; contraddizione con la qualità dichiarata negli aggregati.

**Correzione proposta:** condividere parsing e classificazione dei campioni tra aggregati e istantanee. Per le grandezze numeriche validare numero finito, esportare un numero o null e qualità `non valida`; conservare il dato grezzo separatamente se utile. Validare anche gli stati previsti invece di considerare qualsiasi stringa recente “ok”. Testare NaN, Inf e testo non numerico con `--at`.

##### F4 — Media — Testi di botola/porta fissati nel codice contraddicono varianti valide

**File:** `web/room3d-viewer/src/main.js:251`, `tools/room3d/build_scene.py:520`, `tools/room3d/room3d_core.py:935` (nota botola).

**Evidenza:** UI, cartiglio PNG e nota dell'entità mantengono letteralmente «40 cm ... al bordo vicino»; la UI mantiene anche «altezza porta sconosciuta (1,90 m)». Questi testi non sono derivati dai dati della revisione caricata.

Riproduzione eseguita sulla variante documentata `offset_reference=center`: manifest **Ymin=0,175, Ymax=0,625**, centro Y=0,40. La sezione A renderizzata mostra correttamente la quota **17,5 cm ASSUNTO** al bordo, mentre il cartiglio dice ancora **40 cm al bordo vicino**. Immagine: `/tmp/salamai-review-center/layouts/L001/9f81e6b518be/views/sezione_A_x.png`.

Con il bundle originale e questi asset, Chrome carica senza errori la build `093d0ffdf3b8c2765b57`; il probe legge `offset_reference:'center'` dal manifest ma trova nel pannello «Botola: 40 cm dalla parete porta al bordo vicino». Screenshot `/tmp/salamai-review-center-browser.png`, log `/tmp/salamai-review-browser-probe.log`.

**Impatto:** la procedura documentata per cambiare riferimento produce una vista tecnica e un visualizzatore contraddittori; analogamente il testo porta resterebbe obsoleto dopo un rilievo. Un utente può riportare in opera la distanza riferita al punto sbagliato.

**Correzione proposta:** generare cartiglio, note e avvisi dai valori e dagli stati effettivi di `openings` nel JSON/manifest; includere il riferimento bordo/centro corrente e l'altezza effettiva/provvisoria. Aggiornare coerentemente le descrizioni delle assunzioni. Testare il testo renderizzato e la UI con variante center e porta misurata, oltre ai soli numeri geometrici.

#### Verifiche non eseguite e limiti

- Nessun rilievo fisico: non confermati bordo/centro dei 40 cm, altezza/verso porta, spessori, posizioni, ingombri e supporti delle apparecchiature/prodotti. Le assunzioni dichiarate non diventano misure reali per effetto dei test.
- Nessuna connessione a Home Assistant, dispositivi, Modbus o telemetria reale; mapping verificato solo rispetto ai sorgenti disponibili, non contro un impianto attivo. Nessuna validazione del processo alimentare, della portata o del dimensionamento impiantistico.
- Non eseguiti Docker build/run e test HTTP su Nginx effettivo: configurazione ispezionata staticamente. Non verificati runtime CSP, cache e rifiuto metodi del container; il server statico della suite è un'altra implementazione. Nessuna pubblicazione su infrastrutture reali.
- Browser verificato su Chrome headless/SwiftShader; non su telefono fisico, Safari/iOS, Firefox, GPU hardware o tutte le viewport. Su mobile i test eseguiti coprono rotazione, pinch, selezione e pannello; non è stata ripetuta su telefono l'intera sequenza desktop di layer, misura nota, confronto ed errori. Pan e accessibilità tastiera/screen reader non sono stati verificati con prove dedicate.
- Rendering verificato con Workbench, non con Cycles. Nessuna prova interattiva nella GUI Blender né uso di MCP; riapertura `.blend` verificata dai test batch.
- Verifica degli hash/ID e delle aperture non equivale a prova esaustiva di ogni faccia della mesh o di tutte le configurazioni accettate. Non eseguito fuzzing completo dello schema/validatore, benchmark o audit di sicurezza delle dipendenze. Non serviva una consultazione di servizi esterni per verificare lo snapshot locale.
- Non testata direttamente una cache browser persistente durante deploy successivi: F1 è dimostrato tramite collisione del percorso e accettazione della geometria cambiata nel recupero storico, non tramite simulazione completa di rollout.
- I primi blocchi audio/thumbnail e i divieti di bind/network sono limiti del sandbox; la riesecuzione autorizzata risolve gli impedimenti e consente l'esito positivo completo. Non sono attribuiti come finding all'implementazione.

#### Verdetto finale

**Richieste correzioni prima dell'approvazione**, in particolare F1 per l'integrità della correlazione storica. Coordinate e aperture dello snapshot, trasformazioni, ID, build originale e principali funzioni browser sono sostenuti da verifiche riprodotte; questo non annulla i quattro difetti dimostrati. Dopo le correzioni occorre una nuova revisione su commit preciso, con prove mirate per ciascun finding. Nessuna approvazione della scena condivisa o dell'impianto reale è implicita nel presente report.
