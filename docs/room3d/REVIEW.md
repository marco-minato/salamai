# Revisione indipendente — room3d

Stato: **revisione Codex non eseguita.** Nessuna approvazione è stata dichiarata.

L'implementazione è stata fatta in una sessione di Claude Code non avviata dentro Herdr (`HERDR_ENV` assente). Come richiesto dalle specifiche:

- nessuna sessione o pannello estraneo è stato controllato;
- nessuna revisione è stata simulata.

Il report reale va scritto qui sotto, sostituendo questa sezione di consegna.

## Consegna per la revisione

- Commit da esaminare: `b4c5520` sul branch `feat/room3d`, o successivo, da indicare nel report.
- Build: `tools/room3d/build_all.sh` in una copia separata del repository. Esempio: `git worktree add ../salamai-review feat/room3d`, così la scena e gli output condivisi non vengono toccati.

Avvio previsto:

1. Entrare nel clone.
2. Avviare `herdr`.
3. In un pannello avviare `claude`.
4. Chiedere a Claude di leggere `herdr --skill` e di aprire, o riutilizzare, un pannello Codex con la consegna qui sotto.

Testo della consegna (dalle specifiche, sezione 2):

> Revisiona il commit/snapshot indicato del modello Salamai. Leggi le specifiche, ispeziona codice e configurazione, riproduci la build in output separati, controlla le immagini se il tuo ambiente lo permette. Verifica coordinate botola/porta, quote, assunzioni, Z-up/Y-up, riproducibilità, ID e associazione layout/cicli. Revisiona anche il visualizzatore web in sola lettura, trasformazioni delle misure, layer/selezione, confronto configurazioni, coerenza degli asset e fruibilità mobile; distingui i controlli eseguiti da quelli non verificabili. Riporta finding con gravità, file, evidenza e correzione proposta. Non modificare l'implementazione né la scena condivisa. Dichiara verifiche non eseguite e limiti. Non approvare senza evidenza.

Specifiche: `documentazione/Salamai_Blender_Claude_Herdr_Codex.md`, sezione 2. Documentazione: `docs/room3d/README.md` e `ASSUMPTIONS.md`.

## Verifiche già eseguite dall'implementatore (non sono una revisione)

- `python3 -m unittest discover -s tools/room3d/tests`: 54 test superati.
- `npm run check` e `npm run e2e` in `web/room3d-viewer`: tutte le verifiche superate, sia con il server statico in un sottopercorso sia sul container `nginx:1.30.5-alpine`.
- Clone pulito di `b4c5520` più `tools/room3d/build_all.sh`: exit code 0. `config_hash`, `semantic_hash` e `build_id` sono identici alla build locale.
- Controllo visivo delle quattro viste PNG di L001 e degli screenshot del visualizzatore su desktop e telefono.
