# Camera salumi

Automazione della camera di asciugatura dei salumi (vasca in cemento di ~10 m³
in cantina): scheda Waveshare ESP32-S3-Relay-6CH con ESPHome, Home Assistant
per dashboard e archivio, supervisione periodica con Claude Code.

| Cartella | Contenuto | Dove sta in Home Assistant |
|---|---|---|
| `documentazione/` | Strategia di processo, specifiche del firmware, regole della supervisione, distinta base (anche come pagina HTML), prompt per lo schema QElectroTech | `/homeassistant/salumi/` |
| `supervisione/` | Runner della supervisione (`giro.sh`, `avvia.sh`, `ferma.sh`), istruzioni per Claude (`prompt.md`), strumenti (`strumenti.py`) | `/homeassistant/salumi/supervisione/` |
| `homeassistant/` | Package `salumi.yaml`, archivio su file `salumi_log.py`, configurazione della dashboard `camera-salumi` | `/homeassistant/packages/`, `/homeassistant/salumi/`, `.storage/lovelace.camera_salumi` |
| `esphome/` | `salumi-camera.yaml` (scheda Waveshare, firmware di prova), `salumi-nodo.yaml` (nodo in camera su XIAO ESP32C3, server Modbus indirizzo 4), `sonda-th.yaml` (sonda attuale sulla stessa XIAO, fino alla migrazione) | `/homeassistant/esphome/` |
| `camera_salumi/` | Schema elettrico QElectroTech e immagini | — |
| `qet-tools/` | Strumenti per generare ed esportare gli schemi QElectroTech | — |

Non versionati: `secrets.yaml` di ESPHome e `supervisione/stato/` (contiene il
token del Supervisor e lo stato del runner).
