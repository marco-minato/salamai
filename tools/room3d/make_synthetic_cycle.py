#!/usr/bin/env python3
"""Genera un ciclo di ESEMPIO con dati SINTETICI (non misure reali).

Serve solo a provare il contratto ciclo ↔ layout e il pacchetto di analisi.
Stesso formato di letture.csv scritto da homeassistant/salumi_log.py, con
valori mancanti e una lacuna volute. Deterministico (seme fisso).

Uso: python3 tools/room3d/make_synthetic_cycle.py [--build build/room3d]
     [--output model/room3d/cycles/examples]
"""

import argparse
import csv
import datetime as dt
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import room3d_core as core  # noqa: E402

CYCLE_ID = "SINTETICO_2026-01-10_0800"
COLUMNS = ["ora", "fase", "temp_obiettivo", "ur_obiettivo", "temperatura", "umidita", "temperatura_cantina",
           "umidita_cantina", "peso_g", "calo_reale_pct", "calo_atteso_pct", "stufa", "umidificatore",
           "potenza_stufa_w", "potenza_umidificatore_w", "energia_ciclo_stufa_kwh", "energia_ciclo_umidificatore_kwh"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="model/room3d/room.json")
    ap.add_argument("--output", default="model/room3d/cycles/examples")
    ap.add_argument("--build", default="build/room3d",
                    help="build Blender da cui leggere build_id e semantic_hash di L001")
    args = ap.parse_args()
    room, _, layouts = core.load_model(args.config, "L001")
    lay = layouts[0]
    cfg_hash = core.config_hash(room, lay)
    cat_path = os.path.join(args.build, "catalog.json")
    if not os.path.isfile(cat_path):
        sys.exit(f"catalogo mancante: {cat_path}. Eseguire prima la build Blender (tools/room3d/build_all.sh).")
    entry = next((e for e in core.load_json(cat_path)["layouts"] if e["layout_id"] == "L001"), None)
    if entry is None or entry["config_hash"] != cfg_hash:
        sys.exit(f"la build in {args.build} non corrisponde alla configurazione corrente di L001: rigenerarla.")

    rnd = random.Random(20260110)
    start = dt.datetime(2026, 1, 10, 8, 0, 0)
    rows = []
    e_heat = e_hum = 0.0
    peso0 = 1450.0
    for i in range(3 * 24 * 12):  # 3 giorni a 5 minuti
        t = start + dt.timedelta(minutes=5 * i)
        h = i / 12
        if h < 6:
            fase, tt, ur = "Sgocciolamento", 22.0, 75.0
        else:
            day = int((h - 6) // 24) + 1
            fase, tt, ur = f"Giorno {day}", 22.0 - 1.5 * (day - 1), 80.0 + 2.0 * (day - 1)
        temp = tt + 0.6 * math.sin(i / 7) + rnd.gauss(0, 0.15)
        umid = ur + 3.0 * math.sin(i / 11) + rnd.gauss(0, 0.8)
        stufa = "on" if temp < tt else "off"
        umidif = "on" if umid < ur - 1 else "off"
        p_heat = 1180.0 + rnd.gauss(0, 10) if stufa == "on" else 0.0
        p_hum = 24.0 + rnd.gauss(0, 1) if umidif == "on" else 0.0
        e_heat += p_heat * 5 / 60 / 1000
        e_hum += p_hum * 5 / 60 / 1000
        g = max(h / 24, 0.0)
        calo_att = 2.9 * g ** 0.631 if g > 0 else 0.0
        calo = calo_att * (0.9 + 0.1 * math.sin(i / 50))
        peso = peso0 * (1 - calo / 100)
        row = {
            "ora": t.isoformat(timespec="seconds"), "fase": fase, "temp_obiettivo": f"{tt:.1f}",
            "ur_obiettivo": f"{ur:.0f}", "temperatura": f"{temp:.2f}", "umidita": f"{umid:.1f}",
            "temperatura_cantina": f"{7.0 + 0.4 * math.sin(i / 90):.2f}", "umidita_cantina": f"{82 + 2 * math.sin(i / 70):.1f}",
            "peso_g": f"{peso:.1f}", "calo_reale_pct": f"{calo:.2f}", "calo_atteso_pct": f"{calo_att:.2f}",
            "stufa": stufa, "umidificatore": umidif, "potenza_stufa_w": f"{p_heat:.0f}",
            "potenza_umidificatore_w": f"{p_hum:.0f}", "energia_ciclo_stufa_kwh": f"{e_heat:.3f}",
            "energia_ciclo_umidificatore_kwh": f"{e_hum:.3f}",
        }
        # valori mancanti voluti, come in HA ('unavailable')
        if 300 <= i < 312:
            row["temperatura"] = row["umidita"] = "unavailable"
        if i % 97 == 0:
            row["temperatura_cantina"] = "unavailable"
        rows.append(row)
    # lacuna voluta di 45 minuti (righe assenti)
    rows = [r for k, r in enumerate(rows) if not (500 <= k < 509)]

    out = os.path.join(args.output, CYCLE_ID)
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "letture.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)

    cycle = {
        "schema_version": "1.1",
        "cycle_id": CYCLE_ID,
        "synthetic": True,
        "synthetic_notice": "DATI SINTETICI DI ESEMPIO generati da tools/room3d/make_synthetic_cycle.py: NON sono misure reali e non descrivono nessun ciclo avvenuto.",
        "archive_folder": None,
        "timezone": "Europe/Rome",
        "timezone_note": "letture.csv usa ora locale senza fuso: il fuso è un'assunzione del contratto",
        "started_at": rows[0]["ora"],
        "ended_at": rows[-1]["ora"],
        "layout_refs": [
            {"layout_id": "L001", "config_hash": cfg_hash, "build_id": entry["build_id"],
             "semantic_hash": entry["semantic_hash"], "source_commit": None,
             "valid_from": rows[0]["ora"], "valid_to": None,
             "note": "per un ciclo reale indicare anche il commit dei sorgenti del modello"}
        ],
        "telemetry": {"file": "letture.csv", "format": "salumi_log.py/letture.csv", "mapping": "model/room3d/mapping.json"},
        "events": [
            {"t": "2026-01-10T07:40:00", "type": "load", "zone": "zone_salami", "product": "salami", "quantity": {"value": 30, "unit": "kg"}, "note": "esempio sintetico"},
            {"t": "2026-01-10T07:45:00", "type": "load", "zone": "zone_tagli_interi", "product": "coppa, lonzino", "quantity": {"value": 8, "unit": "kg"}, "note": "esempio sintetico"},
            {"t": "2026-01-10T07:50:00", "type": "load", "zone": "zone_cacciatorini", "product": "cacciatorini", "quantity": {"value": 2, "unit": "kg"}, "note": "esempio sintetico; permanenza non specificata"},
            {"t": "2026-01-11T14:00:00", "type": "load", "zone": "zone_tagli_interi", "product": "guanciale", "quantity": {"value": 1.5, "unit": "kg"}, "note": "esempio sintetico (Giorno 1)"},
            {"t": "2026-01-12T10:00:00", "type": "removal", "zone": "zone_tagli_interi", "product": "coppa, lonzino", "quantity": {"value": 7.6, "unit": "kg"}, "note": "esempio sintetico: rimozione registrata, la zona NON è considerata vuota"},
            {"t": "2026-01-11T09:00:00", "type": "note", "text": "esempio di nota sintetica"}
        ]
    }
    cycle["events"].sort(key=lambda e: e["t"])
    with open(os.path.join(out, "cycle.json"), "w", encoding="utf-8") as f:
        json.dump(cycle, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"Ciclo sintetico scritto in {out} ({len(rows)} righe), layout L001 {cfg_hash[:12]}")


if __name__ == "__main__":
    main()
