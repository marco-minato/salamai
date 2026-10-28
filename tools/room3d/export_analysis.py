#!/usr/bin/env python3
"""Esporta un pacchetto di analisi per AI: ciclo + layout valido + dati.

Il pacchetto funziona anche senza un modello multimodale: tutto è in
package.json (strutturato) e README.md (testo); le immagini sono un di più.

Uso:
  python3 tools/room3d/export_analysis.py --cycle model/room3d/cycles/examples/SINTETICO_2026-01-10_0800 \
      [--build build/room3d] [--mapping model/room3d/mapping.json] [--output build/room3d/analysis] \
      [--at 2026-01-11T12:00:00]

Regole: il layout si prende dal riferimento registrato nel ciclo (layout_id +
build_id, che vincola configurazione e geometria generata), mai quello
corrente; se quella revisione non è nella build si esce con errore. Nessuna interpolazione spaziale, nessun campo
di velocità, nessuna conclusione di sicurezza alimentare.
Exit code: 0 ok, 1 dati non validi, 2 revisione del layout non disponibile.
"""

import argparse
import csv
import datetime as dt
import json
import math
import os
import re
import shutil
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import room3d_core as core  # noqa: E402

PACKAGE_VERSION = "1.0"
CYCLE_SCHEMA_VERSION = "1.1"
# formati dei riferimenti di layout: gli stessi di model/room3d/cycles/cycle.schema.json
REF_FORMATS = {
    "layout_id": (r"[A-Za-z0-9_-]+", True),
    "config_hash": (r"[0-9a-f]{64}", True),
    "build_id": (r"[0-9a-f]{20}", True),
    "semantic_hash": (r"[0-9a-f]{64}", False),
    "source_commit": (r"[0-9a-f]{7,40}", False),
}
NUMERIC = ["temp_obiettivo", "ur_obiettivo", "temperatura", "umidita", "temperatura_cantina", "umidita_cantina",
           "peso_g", "calo_reale_pct", "calo_atteso_pct", "potenza_stufa_w", "potenza_umidificatore_w",
           "energia_ciclo_stufa_kwh", "energia_ciclo_umidificatore_kwh"]
STATES = ["stufa", "umidificatore"]
AIR_COLUMNS = {"temperatura", "umidita"}


class AnalysisError(Exception):
    def __init__(self, msg, code=1):
        super().__init__(msg)
        self.code = code


def parse_ts(s, what):
    try:
        return dt.datetime.fromisoformat(s)
    except (TypeError, ValueError):
        raise AnalysisError(f"{what}: timestamp non valido {s!r}")


def load_cycle(cycle_dir):
    path = os.path.join(cycle_dir, "cycle.json")
    if not os.path.isfile(path):
        raise AnalysisError(f"cycle.json mancante in {cycle_dir}")
    c = core.load_json(path)
    errs = []
    for k in ("schema_version", "cycle_id", "synthetic", "layout_refs", "telemetry", "events"):
        if k not in c:
            errs.append(f"campo '{k}' mancante")
    if errs:
        raise AnalysisError("cycle.json non valido: " + "; ".join(errs))
    if c["schema_version"] == "1.0":
        raise AnalysisError("cycle.json: contratto 1.0 non più accettato. Aggiungere a ogni layout_refs il build_id "
                            "(e semantic_hash) della build storica verificata e impostare schema_version "
                            f"'{CYCLE_SCHEMA_VERSION}'; non si usa mai la build corrente al suo posto.")
    if c["schema_version"] != CYCLE_SCHEMA_VERSION:
        raise AnalysisError(f"cycle.json: schema_version {c['schema_version']!r} non supportata (attesa '{CYCLE_SCHEMA_VERSION}')")
    if not isinstance(c["synthetic"], bool):
        raise AnalysisError("cycle.json: 'synthetic' deve essere true/false")
    refs = c["layout_refs"]
    if not isinstance(refs, list) or not refs:
        raise AnalysisError("cycle.json: nessun riferimento di layout")
    prev_end = None
    for i, r in enumerate(refs):
        if not isinstance(r, dict):
            raise AnalysisError(f"layout_refs[{i}]: deve essere un oggetto")
        if not r.get("valid_from"):
            raise AnalysisError(f"layout_refs[{i}].valid_from: mancante")
        # validati prima di costruire percorsi (layout_id e build_id finiscono nel percorso)
        for k, (pattern, required) in REF_FORMATS.items():
            v = r.get(k)
            if v is None:
                if required:
                    raise AnalysisError(f"layout_refs[{i}].{k}: mancante")
                continue
            if not isinstance(v, str) or not re.fullmatch(pattern, v):
                raise AnalysisError(f"layout_refs[{i}].{k}: valore {v!r} non valido (formato atteso {pattern})")
        r["_from"] = parse_ts(r["valid_from"], f"layout_refs[{i}].valid_from")
        r["_to"] = parse_ts(r["valid_to"], f"layout_refs[{i}].valid_to") if r.get("valid_to") else None
        if r["_to"] and r["_to"] <= r["_from"]:
            raise AnalysisError(f"layout_refs[{i}]: valid_to non successivo a valid_from")
        if prev_end is not None and r["_from"] < prev_end:
            raise AnalysisError(f"layout_refs[{i}]: intervallo sovrapposto al precedente")
        if i < len(refs) - 1 and not r["_to"]:
            raise AnalysisError(f"layout_refs[{i}]: solo l'ultimo intervallo può essere aperto")
        prev_end = r["_to"] or dt.datetime.max
    for i, e in enumerate(c["events"]):
        parse_ts(e.get("t"), f"events[{i}].t")
        if e.get("type") not in ("load", "removal", "layout_change", "note", "maintenance"):
            raise AnalysisError(f"events[{i}]: tipo '{e.get('type')}' non ammesso")
    return c


def layout_at(cycle, t):
    for r in cycle["layout_refs"]:
        if r["_from"] <= t and (r["_to"] is None or t < r["_to"]):
            return r
    return None


def resolve_build(build_dir, ref):
    """Trova la revisione registrata nel ciclo; mai il layout corrente al suo posto.

    La cartella è layouts/<layout_id>/<build_id>: il build_id deriva da
    configurazione + geometria generata, quindi una modifica del generatore che
    cambia la geometria produce un'altra revisione e non viene accettata.
    Ritorna (percorso, manifest, avvisi di provenienza).
    """
    cat_path = os.path.join(build_dir, "catalog.json")
    if not os.path.isfile(cat_path):
        raise AnalysisError(f"catalogo della build mancante: {cat_path}", 2)
    with open(cat_path, encoding="utf-8") as f:
        cat = json.load(f)
    # anche revisioni archiviate non più nel catalogo
    path = os.path.join(build_dir, "layouts", ref["layout_id"], ref["build_id"])
    man_path = os.path.join(path, "manifest.json")
    if not os.path.isfile(man_path):
        current = [e["build_id"] for e in cat["layouts"] if e["layout_id"] == ref["layout_id"]]
        raise AnalysisError(
            f"revisione {ref['layout_id']} build {ref['build_id']} non presente nella build "
            f"(build corrente: {current or 'nessuna'}). Non si applica il layout corrente al ciclo: "
            f"rigenerare quella revisione dal commit dei sorgenti "
            f"({ref.get('source_commit') or 'commit non registrato nel ciclo'}).", 2)
    with open(man_path, encoding="utf-8") as f:
        man = json.load(f)
    b = man["build"]
    for k in ("build_id", "config_hash", "semantic_hash"):
        if k in ref and ref[k] is not None and b.get(k) != ref[k]:
            raise AnalysisError(f"manifest in {path}: {k} {b.get(k)} diverso da quello del ciclo ({ref[k]})", 2)
    warnings = []
    if ref.get("source_commit") and b.get("source_commit") and not b["source_commit"].startswith(ref["source_commit"]):
        warnings.append(f"commit dei sorgenti diverso: ciclo {ref['source_commit']}, build {b['source_commit']}. "
                        f"La geometria coincide (stesso build_id), la provenienza no.")
    if ref.get("source_commit") and not b.get("source_commit"):
        warnings.append("la build non registra il commit dei sorgenti: provenienza non verificabile")
    if b.get("source_dirty"):
        warnings.append("build generata da sorgenti con modifiche non registrate")
    return path, man, warnings


def is_missing(v, missing):
    return v is None or v.strip() in missing


STATE_VALUES = {"on", "off"}


def classify(col, v, missing):
    """Classificazione unica di un campione, usata da aggregati e istantanee.

    Ritorna (qualità, valore): qualità 'missing' | 'invalid' | 'ok'; il valore è
    float per le colonne numeriche, la stringa per stati e fase, None se non ok.
    """
    if is_missing(v, missing):
        return "missing", None
    v = v.strip()
    if col in STATES:
        return ("ok", v) if v in STATE_VALUES else ("invalid", None)
    if col in NUMERIC:
        try:
            x = float(v)
        except ValueError:
            return "invalid", None
        return ("ok", x) if math.isfinite(x) else ("invalid", None)
    return "ok", v


def read_readings(path, missing, interval_s):
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise AnalysisError(f"{path}: nessuna lettura")
    for i, r in enumerate(rows):
        r["_t"] = parse_ts(r.get("ora"), f"letture.csv riga {i + 2}")
    rows.sort(key=lambda r: r["_t"])
    gaps = []
    for a, b in zip(rows, rows[1:]):
        d = (b["_t"] - a["_t"]).total_seconds()
        if d > 2 * interval_s:
            gaps.append({"from": a["ora"], "to": b["ora"], "minutes": round(d / 60, 1)})
    return rows, gaps


def column_stats(rows, col, missing):
    vals, n_missing, n_bad = [], 0, 0
    for r in rows:
        q, x = classify(col, r.get(col), missing)
        if q == "missing":
            n_missing += 1
        elif q == "invalid":
            n_bad += 1
        else:
            vals.append(x)
    out = {"n": len(rows), "valid": len(vals), "missing": n_missing, "invalid": n_bad,
           "coverage_pct": round(100 * len(vals) / len(rows), 1) if rows else 0.0}
    if vals and col in NUMERIC:
        out.update({"min": round(min(vals), 3), "max": round(max(vals), 3),
                    "mean": round(statistics.fmean(vals), 3), "first": vals[0], "last": vals[-1]})
    return out


def phase_aggregates(rows, missing):
    phases = {}
    for r in rows:
        phases.setdefault(r.get("fase") or "(vuota)", []).append(r)
    out = []
    for name, rs in phases.items():
        agg = {"phase": name, "from": rs[0]["ora"], "to": rs[-1]["ora"], "rows": len(rs), "columns": {}}
        for col in ("temperatura", "umidita", "temperatura_cantina", "umidita_cantina", "peso_g", "calo_reale_pct"):
            agg["columns"][col] = column_stats(rs, col, missing)
        for col in STATES:
            on = sum(1 for r in rs if (r.get(col) or "").strip() == "on")
            known = sum(1 for r in rs if (r.get(col) or "").strip() in ("on", "off"))
            agg["columns"][col] = {"on_fraction_of_known": round(on / known, 3) if known else None, "known": known}
        out.append(agg)
    out.sort(key=lambda a: a["from"])
    return out


def inside(p, lo, hi):
    return all(lo[i] <= p[i] <= hi[i] for i in range(3))


def build_package(args):
    cycle = load_cycle(args.cycle)
    with open(args.mapping, encoding="utf-8") as f:
        mapping = json.load(f)
    arch = mapping["cycle_archive"]
    missing = set(arch["missing_values"])
    tel = os.path.join(args.cycle, cycle["telemetry"]["file"])
    if not os.path.isfile(tel):
        raise AnalysisError(f"file di telemetria mancante: {tel}")
    rows, gaps = read_readings(tel, missing, arch["readings_interval_s"])
    t0, t1 = rows[0]["_t"], rows[-1]["_t"]

    # layout valido per ogni intervallo del ciclo (mai quello corrente)
    layouts = []
    for ref in cycle["layout_refs"]:
        if ref["_to"] is not None and ref["_to"] <= t0:
            continue
        if ref["_from"] > t1:
            continue
        path, man, warns = resolve_build(args.build, ref)
        layouts.append((ref, path, man, warns))
    if not layouts:
        raise AnalysisError("nessun layout valido nell'intervallo delle letture", 2)
    uncovered = [r["ora"] for r in rows if layout_at(cycle, r["_t"]) is None]
    if uncovered:
        raise AnalysisError(f"{len(uncovered)} letture fuori da ogni intervallo di layout (prima: {uncovered[0]})")

    out_dir = os.path.join(args.output, cycle["cycle_id"])
    if os.path.isdir(out_dir):
        shutil.rmtree(out_dir)
    os.makedirs(os.path.join(out_dir, "images"))
    os.makedirs(os.path.join(out_dir, "data"))
    shutil.copy2(tel, os.path.join(out_dir, "data", os.path.basename(tel)))

    columns = {}
    for col in NUMERIC:
        st = column_stats(rows, col, missing)
        m = mapping["csv_columns"].get(col, {})
        st.update({"unit": m.get("unit"), "quantity": m.get("quantity"), "entity_id": m.get("entity_id"),
                   "component": m.get("component"), "mapping_status": m.get("status"), "note": m.get("note")})
        columns[col] = st

    layout_pkgs = []
    observed_air_sensors = set()
    for ref, path, man, warns in layouts:
        # disponibilità calcolata solo sulle letture di questo intervallo di layout
        lrows = [r for r in rows if layout_at(cycle, r["_t"]) is ref]
        lstats = {col: column_stats(lrows, col, missing) for col in mapping["csv_columns"]}
        ents = {e["id"]: e for e in man["entities"]}
        images = {}
        for view, rel in man.get("images", {}).items():
            src = os.path.join(path, rel)
            dst_name = f"{ref['layout_id']}_{ref['build_id']}_{os.path.basename(rel)}"
            shutil.copy2(src, os.path.join(out_dir, "images", dst_name))
            images[view] = f"images/{dst_name}"
        # punti di misura: componenti collegati a colonne; "con dati" solo se ci
        # sono campioni validi nell'intervallo di questo layout
        points, actuators = [], []
        for col, m in mapping["csv_columns"].items():
            cid = m.get("component")
            if not cid or cid not in ents:
                continue
            e = ents[cid]
            st = lstats[col]
            if e["layer"] != "sensori":
                actuators.append({"column": col, "component": cid, "tag": e.get("tag"), "quantity": m.get("quantity"),
                                  "entity_id": m.get("entity_id"), "position_status": e["data_status"],
                                  "valid_samples": st["valid"], "coverage_pct": st["coverage_pct"]})
                continue
            points.append({
                "column": col, "component": cid, "tag": e.get("tag"), "position": e.get("center") or e["bbox_center"],
                "position_status": e["data_status"], "status_detail": e.get("status_detail"),
                "valid_samples": st["valid"], "coverage_pct": st["coverage_pct"],
                "data": "con dati validi" if st["valid"] else "NESSUN DATO VALIDO nell'intervallo",
                "note": "posizione di progetto, non rilevata" if e["data_status"] in ("assumed", "unknown") else None,
            })
        observed_components = {p["component"] for p in points if p["valid_samples"]}
        mapped_no_data = sorted({p["component"] for p in points} - observed_components)
        zones = []
        for e in man["entities"]:
            if e["type"] != "product_zone":
                continue
            # solo sonde dell'aria: la bilancia non osserva la zona
            air_in = [p for p in points if p["column"] in AIR_COLUMNS
                      and inside(p["position"], e["bbox_min"], e["bbox_max"])]
            sensors_in = sorted({p["component"] for p in air_in if p["valid_samples"]})
            no_data_in = sorted({p["component"] for p in air_in} - set(sensors_in))
            observed_air_sensors.update(sensors_in)
            if len(sensors_in) == 1:
                obs = "osservata da una sola sonda puntuale"
            elif sensors_in:
                obs = "osservata da più sonde"
            elif no_data_in:
                obs = "NON OSSERVATA: sonda presente ma nessun dato valido nell'intervallo"
            else:
                obs = "NON OSSERVATA: nessuna sonda"
            zones.append({"id": e["id"], "name": e["name"], "bbox_min": e["bbox_min"], "bbox_max": e["bbox_max"],
                          "status": e["data_status"], "measured_by": sensors_in,
                          "quantities": sorted({p["column"] for p in air_in if p["valid_samples"]}),
                          "sensors_without_valid_data": no_data_in, "observation": obs})
        unmapped = sorted(e["entity_id"] for e in man["entities"]
                          if e["role"] == "body" and e["layer"] == "sensori" and e["entity_id"] not in observed_components)
        layout_pkgs.append({
            "layout_id": ref["layout_id"], "config_hash": ref["config_hash"], "source_commit": ref.get("source_commit"),
            "valid_from": ref["valid_from"], "valid_to": ref.get("valid_to"), "readings_in_interval": len(lrows),
            "build_id": man["build"]["build_id"], "semantic_hash": man["build"]["semantic_hash"],
            "build_source_commit": man["build"].get("source_commit"), "provenance_warnings": warns,
            "kind": man["layout"]["kind"], "title": man["layout"]["title"],
            "frame": man["frame"], "units": man["units"], "room": man["room"], "openings": man["openings"],
            "components": [{k: e.get(k) for k in ("id", "tag", "name", "type", "layer", "state", "data_status",
                                                  "center", "size", "bbox_min", "bbox_max", "orientation", "pipe", "fan",
                                                  "properties", "notes")}
                           for e in man["entities"] if e["role"] == "body"],
            "assumptions": man["assumptions"], "unknowns": man["unknowns"],
            "measurement_points": points, "actuators_with_data": actuators, "product_zones": zones,
            "sensors_without_data": sorted(set(unmapped) | set(mapped_no_data)),
            "sensors_mapped_without_valid_data": mapped_no_data,
            "images": images,
        })

    instant = None
    if args.at:
        t = parse_ts(args.at, "--at")
        ref = layout_at(cycle, t)
        if ref is None:
            raise AnalysisError(f"--at {args.at}: nessun layout valido in quell'istante")
        before = [r for r in rows if r["_t"] <= t]
        rec = before[-1] if before else None
        age = (t - rec["_t"]).total_seconds() if rec else None
        values = {}
        stale = age is not None and age > 2 * arch["readings_interval_s"]
        for col in NUMERIC + STATES + ["fase"]:
            raw = rec.get(col) if rec else None
            q, val = classify(col, raw, missing)
            values[col] = {
                "value": val,
                "unit": mapping["csv_columns"].get(col, {}).get("unit"),
                "quality": {"missing": "mancante", "invalid": "non valida"}.get(q, "vecchia" if stale else "ok"),
                "raw": raw if q == "invalid" else None,
            }
        instant = {"t": args.at, "layout_id": ref["layout_id"], "config_hash": ref["config_hash"], "build_id": ref["build_id"],
                   "reading_time": rec["ora"] if rec else None, "reading_age_s": age, "values": values,
                   "note": "valori dell'ultima lettura non successiva all'istante; nessuna interpolazione"}

    load_events = [e for e in cycle["events"] if e["type"] in ("load", "removal")]
    pkg = {
        "package_version": PACKAGE_VERSION,
        "generated_by": "tools/room3d/export_analysis.py",
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "synthetic": cycle["synthetic"],
        "synthetic_notice": cycle.get("synthetic_notice") if cycle["synthetic"] else None,
        "cycle": {k: cycle.get(k) for k in ("cycle_id", "archive_folder", "timezone", "timezone_note", "started_at", "ended_at")},
        "readings": {
            "file": f"data/{os.path.basename(tel)}", "rows": len(rows), "first": rows[0]["ora"], "last": rows[-1]["ora"],
            "interval_s": arch["readings_interval_s"], "timestamp_format": arch["timestamp"], "gaps": gaps,
            "columns": columns,
        },
        "phases": phase_aggregates(rows, missing),
        "events": cycle["events"],
        "product_load": {
            "events": load_events,
            "note": "carichi e rimozioni come registrati; una rimozione non implica che la zona sia vuota",
        },
        "layouts": layout_pkgs,
        "instant": instant,
        "observations": [
            f"{len(rows)} letture dal {rows[0]['ora']} al {rows[-1]['ora']}, intervallo nominale {arch['readings_interval_s']} s",
            f"{len(gaps)} lacune oltre il doppio dell'intervallo" + (f" (la più lunga {max(g['minutes'] for g in gaps)} min)" if gaps else ""),
            f"copertura temperatura camera {columns['temperatura']['coverage_pct']} %, umidità camera {columns['umidita']['coverage_pct']} %",
            (f"sonde dell'aria in camera con dati validi: {', '.join(sorted(observed_air_sensors))} "
             f"({len(observed_air_sensors)}); valori puntuali, posizione di progetto" if observed_air_sensors else
             "nessuna sonda dell'aria in camera con dati validi: nessuna zona prodotto è osservata"),
        ],
        "inferences": [],
        "inference_rule": "Ogni inferenza va scritta separata dalle osservazioni, con il metodo usato e i dati da cui deriva.",
        "hypotheses": [],
        "hypothesis_rule": "Le ipotesi (es. sul flusso d'aria) vanno marcate come tali: le frecce del modello sono direzioni nominali, non misure.",
        "limits": [
            "Il layout è pianificato (real_plan), non rilevato: molte posizioni sono assunte o sconosciute (vedi unknowns/assumptions).",
            "Con una sola sonda in camera non si possono ricostruire mappe di temperatura o umidità: nessuna interpolazione spaziale.",
            "Nessun campo di velocità dell'aria: PWM e giri delle ventole non sono misure di portata; nessuna simulazione CFD.",
            "Le zone prodotto senza sonde sono NON OSSERVATE.",
            "Timestamp locali senza fuso (fuso dichiarato nel ciclo come assunzione).",
            "Nessuna conclusione automatica di sicurezza alimentare può essere tratta dal modello 3D o da questo pacchetto.",
        ],
    }
    with open(os.path.join(out_dir, "package.json"), "w", encoding="utf-8") as f:
        json.dump(pkg, f, ensure_ascii=False, indent=1)
        f.write("\n")
    with open(os.path.join(out_dir, "README.md"), "w", encoding="utf-8") as f:
        f.write(readme(pkg))
    return out_dir, pkg


def readme(p):
    L = []
    if p["synthetic"]:
        L += ["> **DATI SINTETICI** — " + p["synthetic_notice"], ""]
    c = p["cycle"]
    L += [f"# Pacchetto di analisi — ciclo {c['cycle_id']}", "",
          f"Letture: {p['readings']['rows']} dal {p['readings']['first']} al {p['readings']['last']} "
          f"({c['timezone']}, {c['timezone_note']}).", ""]
    L += ["## Layout valido", ""]
    for lay in p["layouts"]:
        L.append(f"- {lay['layout_id']} ({lay['kind']}) config `{lay['config_hash'][:12]}`, build `{lay['build_id']}`, "
                 f"valido dal {lay['valid_from']} al {lay['valid_to'] or 'fine ciclo'}; commit sorgenti: {lay['source_commit'] or 'non registrato'}")
        r = lay["room"]
        L.append(f"  - Stanza interna {r['interior_size'][0]:.2f} × {r['interior_size'][1]:.2f} × {r['interior_size'][2]:.2f} m "
                 f"(Z verso l'alto, origine nell'angolo sinistro della parete porta); volume lordo {r['volume_gross_m3']} m³ (non libero).")
        L.append("  - Punti misurati:")
        for m in lay["measurement_points"]:
            pos = ", ".join(f"{v:.2f}" for v in m["position"])
            L.append(f"    - `{m['column']}` ← {m['component']} ({m['tag']}) in [{pos}] m, posizione {m['position_status']}, "
                     f"{m['data']} ({m['valid_samples']} campioni, copertura {m['coverage_pct']} %)")
        L.append("  - Attuatori con dati: " + ", ".join(f"`{a['column']}` ← {a['component']}" for a in lay["actuators_with_data"]))
        L.append("  - Zone prodotto (osservazione dell'aria):")
        for z in lay["product_zones"]:
            L.append(f"    - {z['id']}: {z['observation']}" + (f" ({', '.join(z['measured_by'])})" if z["measured_by"] else ""))
        L.append(f"  - Sonde del modello senza dati validi in questo intervallo: {', '.join(lay['sensors_without_data']) or 'nessuna'}")
        for w in lay["provenance_warnings"]:
            L.append(f"  - AVVISO provenienza: {w}")
        L.append(f"  - Immagini: {', '.join(lay['images'].values())}")
    L += ["", "## Colonne", "", "| colonna | grandezza | unità | copertura | min | max | media | origine |", "|---|---|---|---|---|---|---|---|"]
    for col, s in p["readings"]["columns"].items():
        L.append(f"| {col} | {s.get('quantity') or ''} | {s.get('unit') or ''} | {s['coverage_pct']} % | {s.get('min', '')} | "
                 f"{s.get('max', '')} | {s.get('mean', '')} | {s.get('entity_id') or ''} ({s.get('mapping_status')}) |")
    L += ["", "## Fasi", ""]
    for ph in p["phases"]:
        t = ph["columns"]["temperatura"]
        u = ph["columns"]["umidita"]
        L.append(f"- {ph['phase']}: {ph['from']} → {ph['to']}, {ph['rows']} righe; T {t.get('min', '—')}–{t.get('max', '—')} °C "
                 f"(media {t.get('mean', '—')}, copertura {t['coverage_pct']} %), UR {u.get('min', '—')}–{u.get('max', '—')} %")
    L += ["", "## Lacune", ""] + ([f"- {g['from']} → {g['to']} ({g['minutes']} min)" for g in p["readings"]["gaps"]] or ["- nessuna"])
    L += ["", "## Eventi", ""] + [f"- {e['t']} {e['type']}: " + ", ".join(f"{k}={v}" for k, v in e.items() if k not in ("t", "type")) for e in p["events"]]
    if p["instant"]:
        i = p["instant"]
        L += ["", f"## Istante {i['t']}", "", f"Layout {i['layout_id']} build `{i['build_id']}`; lettura delle {i['reading_time']} ({i['note']})."]
        L += [f"- {k}: {v['value']} {v['unit'] or ''} [{v['quality']}]" + (f" (grezzo: {v['raw']!r})" if v["raw"] is not None else "")
              for k, v in i["values"].items()]
    L += ["", "## Osservazioni (dai dati)", ""] + [f"- {o}" for o in p["observations"]]
    L += ["", "## Inferenze", "", f"- nessuna registrata. Regola: {p['inference_rule']}"]
    L += ["", "## Ipotesi", "", f"- nessuna registrata. Regola: {p['hypothesis_rule']}"]
    L += ["", "## Limiti", ""] + [f"- {x}" for x in p["limits"]]
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--cycle", required=True)
    ap.add_argument("--build", default="build/room3d")
    ap.add_argument("--mapping", default="model/room3d/mapping.json")
    ap.add_argument("--output", default=None, help="default: <build>/analysis")
    ap.add_argument("--at", default=None, help="istante ISO da descrivere (layout e ultima lettura)")
    args = ap.parse_args(argv)
    args.output = args.output or os.path.join(args.build, "analysis")
    try:
        out, pkg = build_package(args)
    except AnalysisError as e:
        print(f"ERRORE: {e}", file=sys.stderr)
        return e.code
    print(f"Pacchetto scritto in {out}" + (" (DATI SINTETICI)" if pkg["synthetic"] else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
