# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Camera di asciugatura salumi: vasca in cemento di ~10 m³ in cantina. La gestisce Home Assistant;
in futuro la gestirà una Waveshare ESP32-S3-Relay-6CH nel quadro, con un nodo XIAO ESP32C3 in camera
(scatola X6) e la supervisione periodica di Claude Code. L'utente scrive in italiano: rispondi in
italiano semplice, spiega i collegamenti elettrici senza gergo.

La mappa delle cartelle e la loro corrispondenza con Home Assistant sono in `README.md`.

## Dove stanno i file veri

Il repo è clonato anche nell'add-on Claude Code di Home Assistant, in `/share/salamai`.

- **File di HA** (`homeassistant/`, `esphome/`, `supervisione/`): gli originali stanno in `/homeassistant/...`. Il repo ne è una copia da riallineare a mano.
- **`documentazione/`**: si lavora qui e poi si ricopia in `/homeassistant/salumi/` (lì non c'è la distinta HTML).
- **Commit e push:** solo su richiesta esplicita dell'utente.

## Pagine generate (non modificarle a mano)

| Uscita | Comando (dalla radice del repo) |
|---|---|
| `documentazione/schema-quadro.html`, `quadro-disposizione.drawio` | `sh documentazione/sorgenti/quadro/build.sh` |
| `documentazione/scatola-x6.html`, `scatola-x6.drawio` | `sh documentazione/sorgenti/x6/build.sh` |

- **Come sono fatti i generatori:**
  - `gen_*.py` disegnano in mm (in draw.io si moltiplica per `S=3`) e calcolano le reti con union-find sui nomi dei capi;
  - la pagina è `page_*tpl.html` con i dati JSON al posto di `__DATA__`, più l'involucro `<!doctype html>…<body>`.
- **Controlli dopo una modifica:**
  - **quadro:** sovrapposizioni ed estremi senza nome devono restare vuoti;
  - **X6:** le reti stampate devono restare le stesse;
  - in tutte e due, il JavaScript estratto dalla pagina deve passare `node --check`;
  - i nomi di rete usati nella checklist (`STEPS`) devono esistere in `nets`.
- **Funzioni della pagina da conservare:** zoom, selezione di una rete, livelli, legenda e checklist.
  - Le spunte della checklist sono in `localStorage` per indice: aggiungere passi sposta quelle già messe.
- **Anteprima PNG:** `render.py` produce un'immagine senza testi, utile solo per la geometria.
- **Allineamento dei documenti:** `documentazione/distinta_base.md`, `distinta-camera-salumi.html` e `prompt_schema_qelectrotech.md` devono restare coerenti con gli schemi: sigle, numerazione dei morsetti, cavi.

## Firmware

- **ESPHome:** si valida e si flasha solo dal Device Builder di HA. Non si compila nell'add-on.
- **`sonda-th.yaml`:** attivo oggi.
- **`salumi-nodo.yaml`:** si flasha solo alla migrazione. Registri Modbus in `documentazione/specifiche_firmware.md`.

## Vincoli dell'utente

- In supervisione Claude **non tocca mai le temperature**, lavora solo sull'umidità.
- **Termostato meccanico di sicurezza:** niente, è una scelta consapevole. Non riproporlo.
- **Quadro:** tutto su guida DIN.
- **Saldature:** qualcuna è accettata.
- **Scatola X6 (150×110×70):** è già comprata.
- **Scelte fissate:**
  - contattori con soppressione integrata, senza diodi;
  - stufa collegata direttamente, senza presa CEE;
  - Cat5e UTP senza schermi.
- **Fusibile:** F1 1 A T (ritardato), dalla misura al banco del 30/10/2026. Niente sonda cantina B5 né F2: la cantina la misura lo Shelly H&T.
- **Acquisti:** prima di proporli, controlla nella distinta cosa è "già in possesso" (P).
- **Amazon:** blocca lo scraping con curl. Usa la ricerca web.
- **Segreti:** `esphome/secrets.yaml` e `supervisione/stato/` non sono versionati.
