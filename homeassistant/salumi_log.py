#!/usr/bin/env python3
"""Archivio della camera salumi: letture CSV, note, avvisi e diario giornaliero.

Chiamato da shell_command.salumi_log:
    salumi_log.py <modo> <cartella> <dati base64(JSON)>

modi:
    csv        aggiunge una riga a letture.csv (colonne = chiavi di dati)
    nota       aggiunge una nota a note.csv          dati: {testo}
    avviso     aggiunge un avviso ad avvisi.csv      dati: {titolo, messaggio}
    diario     scrive la voce di una fase in diario.md
               dati: {fase, da, a, temp_target, ur_target, inizio_ciclo}
    riepilogo  scrive il riepilogo finale in diario.md
               dati: {da, a, esito, inizio_ciclo}

Le statistiche del diario sono calcolate dallo storico di Home Assistant
(database del recorder, letto in sola lettura).
"""
import base64
import csv
import json
import os
import re
import sqlite3
import sys
from datetime import datetime

BASE = "/share/salumi"
DB_PATHS = ("/config/home-assistant_v2.db", "/homeassistant/home-assistant_v2.db")

# Entità usate nel diario. Quelle che non esistono ancora (hardware non
# installato) compaiono come "non disponibile".
TEMP = "sensor.sonda_th_temperatura"
UR = "sensor.sonda_th_umidita"
STUFA = "switch.sonoff_1001f24fe4_2"
UMIDIFICATORE = "switch.sonoff_1001f24fe4_1"
ASPIRATORE = "switch.salumi_aspiratore"
ENERGIA_STUFA = "sensor.salumi_energia_stufa"
ENERGIA_UMIDIFICATORE = "sensor.salumi_energia_umidificatore"
PESO = "sensor.salumi_peso"
TEMP_CUORE = "sensor.salumi_temperatura_cuore"

NON_VALIDI = ("unavailable", "unknown", "", None)


# --- utilità ------------------------------------------------------------------
def num(x, dec=1):
    return f"{x:.{dec}f}".replace(".", ",")


def ora(ts, fmt="%d/%m %H:%M"):
    return datetime.fromtimestamp(ts).strftime(fmt)


def durata(sec):
    h, m = divmod(int(round(sec / 60)), 60)
    return f"{h} h {m:02d} min"


def leggi_righe(path):
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.reader(f))


def aggiungi_riga(path, riga, intestazione=None):
    nuovo = not os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if nuovo and intestazione:
            w.writerow(intestazione)
        w.writerow(riga)


# --- storico ------------------------------------------------------------------
class Storico:
    def __init__(self):
        db = next((p for p in DB_PATHS if os.path.exists(p)), None)
        self.con = sqlite3.connect(f"file:{db}?mode=ro", uri=True, timeout=30) if db else None

    def serie(self, entity_id, t0, t1):
        """Lista di (inizio, fine, stato) che copre [t0, t1], o None se l'entità non ha storico."""
        if not self.con:
            return None
        r = self.con.execute(
            "SELECT metadata_id FROM states_meta WHERE entity_id = ?", (entity_id,)
        ).fetchone()
        if not r:
            return None
        mid = r[0]
        prima = self.con.execute(
            "SELECT state FROM states WHERE metadata_id = ? AND last_updated_ts <= ? "
            "ORDER BY last_updated_ts DESC LIMIT 1",
            (mid, t0),
        ).fetchone()
        righe = self.con.execute(
            "SELECT last_updated_ts, state FROM states WHERE metadata_id = ? "
            "AND last_updated_ts > ? AND last_updated_ts <= ? ORDER BY last_updated_ts",
            (mid, t0, t1),
        ).fetchall()
        punti = ([(t0, prima[0])] if prima else []) + list(righe)
        if not punti:
            return None
        return [
            (ts, punti[i + 1][0] if i + 1 < len(punti) else t1, stato)
            for i, (ts, stato) in enumerate(punti)
        ]

    def numerica(self, entity_id, t0, t1):
        """Media pesata nel tempo, minimo, massimo e tempo non disponibile."""
        s = self.serie(entity_id, t0, t1)
        if not s:
            return None
        somma = durata_valida = 0.0
        valori = []
        assente = 0.0
        for a, b, stato in s:
            try:
                v = float(stato)
            except (TypeError, ValueError):
                assente += b - a
                continue
            valori.append(v)
            somma += v * (b - a)
            durata_valida += b - a
        if not valori or durata_valida <= 0:
            return None
        return {
            "media": somma / durata_valida,
            "min": min(valori),
            "max": max(valori),
            "assente": assente,
        }

    def accensioni(self, entity_id, t0, t1):
        """Tempo acceso e numero di accensioni."""
        s = self.serie(entity_id, t0, t1)
        if not s:
            return None
        acceso = sum(b - a for a, b, stato in s if stato == "on")
        n = sum(
            1 for i, (_, _, stato) in enumerate(s)
            if stato == "on" and (i == 0 or s[i - 1][2] != "on") and s[i][0] > t0
        )
        return {"acceso": acceso, "n": n}

    def valore(self, entity_id, t):
        """Ultimo valore numerico valido fino all'istante t."""
        if not self.con:
            return None
        r = self.con.execute(
            "SELECT s.state FROM states s JOIN states_meta m ON s.metadata_id = m.metadata_id "
            "WHERE m.entity_id = ? AND s.last_updated_ts <= ? "
            "AND s.state NOT IN ('unavailable', 'unknown', '') "
            "ORDER BY s.last_updated_ts DESC LIMIT 1",
            (entity_id, t),
        ).fetchone()
        try:
            return float(r[0]) if r else None
        except ValueError:
            return None


# --- diario -------------------------------------------------------------------
def eventi(cartella, nome, t0, t1):
    out = []
    for riga in leggi_righe(os.path.join(cartella, nome))[1:]:
        try:
            ts = datetime.fromisoformat(riga[0]).timestamp()
        except (ValueError, IndexError):
            continue
        if t0 <= ts <= t1:
            out.append((ts, riga[1:]))
    return out


def energia(st, entity_id, t0, t1):
    a, b = st.valore(entity_id, t0), st.valore(entity_id, t1)
    return None if a is None or b is None else max(b - a, 0)


def righe_statistiche(st, cartella, t0, t1, inizio_ciclo):
    dur = max(t1 - t0, 1)
    out = []

    for nome, eid, unita in (("Temperatura", TEMP, "°C"), ("Umidità", UR, "%")):
        s = st.numerica(eid, t0, t1)
        if s:
            riga = (f"{nome + ':':<15}media {num(s['media'])} {unita} "
                    f"(min {num(s['min'])} – max {num(s['max'])})")
            if s["assente"] > 600:
                riga += f"  ⚠ sensore assente {durata(s['assente'])}"
        else:
            riga = f"{nome + ':':<15}non disponibile"
        out.append(riga)

    for nome, eid, eid_kwh in (
        ("Stufa", STUFA, ENERGIA_STUFA),
        ("Umidificatore", UMIDIFICATORE, ENERGIA_UMIDIFICATORE),
        ("Aspiratore", ASPIRATORE, None),
    ):
        a = st.accensioni(eid, t0, t1)
        if a is None:
            out.append(f"{nome + ':':<15}non disponibile")
            continue
        riga = (f"{nome + ':':<15}acceso {durata(a['acceso'])} "
                f"({round(100 * a['acceso'] / dur)}% del tempo, {a['n']} accensioni)")
        kwh = energia(st, eid_kwh, t0, t1) if eid_kwh else None
        if kwh is not None:
            riga += f" – {num(kwh, 2)} kWh"
        out.append(riga)

    p0, p1 = st.valore(PESO, t0), st.valore(PESO, t1)
    if p0 is not None and p1 is not None:
        giorni = dur / 86400
        riga = f"{'Peso campione:':<15}{p0:.0f} g → {p1:.0f} g ({p1 - p0:+.0f} g"
        if p0 > 0:
            riga += f", {num(100 * (p1 - p0) / p0 / giorni)}% al giorno"
        pi = st.valore(PESO, inizio_ciclo + 600) if inizio_ciclo else None
        if pi:
            riga += f"; totale {num(100 * (p1 - pi) / pi)}%"
        out.append(riga + ")")
    else:
        out.append(f"{'Peso campione:':<15}non disponibile")

    c = st.numerica(TEMP_CUORE, t0, t1)
    out.append(f"{'Cuore salame:':<15}"
               + (f"media {num(c['media'])} °C (min {num(c['min'])} – max {num(c['max'])})"
                  if c else "non disponibile"))

    avvisi = eventi(cartella, "avvisi.csv", t0, t1)
    if avvisi:
        out.append(f"{'Avvisi:':<15}{len(avvisi)}")
        out += [f"{'':<15}[{ora(ts)}] {r[0]}" for ts, r in avvisi]
    else:
        out.append(f"{'Avvisi:':<15}nessuno")

    note = eventi(cartella, "note.csv", t0, t1)
    if note:
        out.append(f"{'Note:':<15}[{ora(note[0][0])}] \"{note[0][1][0]}\"")
        out += [f"{'':<15}[{ora(ts)}] \"{r[0]}\"" for ts, r in note[1:]]
    else:
        out.append(f"{'Note:':<15}nessuna")
    return out


def scrivi_diario(cartella, testo):
    path = os.path.join(cartella, "diario.md")
    nuovo = not os.path.exists(path)
    with open(path, "a", encoding="utf-8") as f:
        if nuovo:
            f.write(f"# Diario camera salumi – ciclo {os.path.basename(cartella)}\n\n")
        f.write(testo + "\n")


def voce(cartella, d):
    st = Storico()
    t0, t1 = float(d["da"]), float(d["a"])
    righe = [f"## {d['fase']} · {ora(t0)} → {ora(t1)} ({durata(t1 - t0)})", "", "```"]
    if d.get("temp_target") not in NON_VALIDI:
        ur = d.get("ur_target")
        righe.append(f"{'Obiettivo:':<15}{d['temp_target']} °C"
                     + (f" / {ur}% UR" if ur not in NON_VALIDI else " (umidificatore spento)"))
    righe += righe_statistiche(st, cartella, t0, t1, d.get("inizio_ciclo"))
    righe += ["```", ""]
    scrivi_diario(cartella, "\n".join(righe))


def riepilogo(cartella, d):
    st = Storico()
    t0, t1 = float(d["da"]), float(d["a"])
    righe = [f"## Riepilogo ciclo · {ora(t0)} → {ora(t1)} ({durata(t1 - t0)})", "",
             f"Esito: {d.get('esito', '')}", "", "```"]
    righe += righe_statistiche(st, cartella, t0, t1, d.get("inizio_ciclo"))
    righe += ["```", "", "Giudizio finale sul prodotto: ", ""]
    scrivi_diario(cartella, "\n".join(righe))


# --- main ---------------------------------------------------------------------
def main():
    modo, nome = sys.argv[1], sys.argv[2]
    if not re.fullmatch(r"[\w-]+", nome):
        sys.exit(f"nome cartella non valido: {nome}")
    dati = json.loads(base64.b64decode(sys.argv[3])) if len(sys.argv) > 3 else {}
    cartella = os.path.join(BASE, nome)
    os.makedirs(cartella, exist_ok=True)
    adesso = datetime.now().isoformat(timespec="seconds")

    if modo == "csv":
        aggiungi_riga(os.path.join(cartella, "letture.csv"),
                      [adesso] + list(dati.values()), ["ora"] + list(dati.keys()))
    elif modo == "nota":
        aggiungi_riga(os.path.join(cartella, "note.csv"), [adesso, dati["testo"]], ["ora", "nota"])
    elif modo == "avviso":
        aggiungi_riga(os.path.join(cartella, "avvisi.csv"),
                      [adesso, dati.get("titolo", ""), dati.get("messaggio", "")],
                      ["ora", "titolo", "messaggio"])
    elif modo == "diario":
        voce(cartella, dati)
    elif modo == "riepilogo":
        riepilogo(cartella, dati)
    else:
        sys.exit(f"modo sconosciuto: {modo}")


if __name__ == "__main__":
    main()
