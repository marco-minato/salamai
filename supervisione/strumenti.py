#!/usr/bin/env python3
"""Strumenti della supervisione salumi (usati dal runner e da Claude Code).

  turno                     il runner chiede se è ora di un controllo
  fine_turno ESITO          il runner registra la fine di un controllo
  stato                     situazione attuale della camera (JSON)
  storia ORE [PASSO_MIN]    andamento aggregato delle ultime ORE (JSON)
  foto                      archivia le foto nuove e le elenca (JSON)
  avviso TITOLO TESTO [P]   avviso Pushover (non richiede un'altra analisi)
  proposta TESTO            proposta in attesa di approvazione in dashboard
  proposta_chiudi           cancella proposta e risposta
  imposta ENTITA VALORE MOTIVO
                            cambia un parametro consentito (solo modalità attiva)
"""
import json
import os
import re
import shutil
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

DIR = os.path.dirname(os.path.abspath(__file__))
STATO = os.path.join(DIR, "stato")
SHARE = "/share/salumi"
FOTO = "/media/salumi"
RICHIESTA = os.path.join(SHARE, "richiesta_analisi")
API = "http://supervisor/core/api"
H = {"Authorization": "Bearer " + os.environ.get("SUPERVISOR_TOKEN", ""),
     "Content-Type": "application/json"}

# Parametri che Claude può cambiare, con i limiti assoluti. I limiti sulla
# correzione dell'UR (±5 avviso, ±10 permesso) li applica Claude secondo le
# regole; qui c'è solo il limite fisico.
CONSENTITI = {
    "input_number.salumi_correzione_ur": (-15, 15),
}


def api(path, data=None):
    req = urllib.request.Request(API + path, headers=H,
                                 data=None if data is None else json.dumps(data).encode())
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read() or "null")


def st(e):
    try:
        return api("/states/" + e)
    except Exception:
        return None


def servizio(dom, svc, data):
    return api(f"/services/{dom}/{svc}", data)


def eta_min(s):
    try:
        t = datetime.fromisoformat(s.get("last_reported") or s["last_updated"])
        return round((datetime.now(timezone.utc) - t).total_seconds() / 60, 1)
    except Exception:
        return None


def val(e, attr=None):
    s = st(e)
    if s is None:
        return None
    return s["attributes"].get(attr) if attr else s["state"]


def leggi(nome, default=None):
    try:
        with open(os.path.join(STATO, nome)) as f:
            return json.load(f)
    except Exception:
        return default


def scrivi(nome, dati):
    os.makedirs(STATO, exist_ok=True)
    with open(os.path.join(STATO, nome), "w") as f:
        json.dump(dati, f, indent=1, ensure_ascii=False)


def cartella_ciclo():
    c = (val("input_text.salumi_cartella_ciclo") or "").strip()
    return c if c and c not in ("unknown", "unavailable") else "senza_ciclo"


# --- runner -----------------------------------------------------------------

def turno():
    """Stampa 'esegui MOTIVO' oppure 'attendi MOTIVO'."""
    modo = val("input_select.salumi_supervisione")
    if modo == "sospesa":
        return print("attendi supervisione sospesa")
    if os.path.exists(RICHIESTA):
        return print("esegui richiesta di Home Assistant")
    attivo = val("input_boolean.salumi_ciclo_attivo") == "on"
    prep = val("input_boolean.salumi_preparazione") == "on"
    if not (attivo or prep):
        return print("attendi ciclo non attivo")
    step = int(float(val("sensor.salumi_fase", "step") or -1))
    opg = float(val("input_number.salumi_ore_per_giorno") or 24)
    base = 60 if step <= 3 else 120
    intervallo = max(10, base * opg / 24)  # scalato nel test accelerato
    ultimo = leggi("ultimo_turno.json", {}).get("ts", 0)
    trascorsi = (time.time() - ultimo) / 60
    if trascorsi >= intervallo:
        return print(f"esegui controllo periodico (fase {step}, ogni {intervallo:.0f} min)")
    print(f"attendi prossimo controllo tra {intervallo - trascorsi:.0f} min")


def fine_turno(esito):
    scrivi("ultimo_turno.json", {"ts": time.time(), "quando": datetime.now().isoformat(timespec="seconds"),
                                 "esito": esito})


# --- dati -------------------------------------------------------------------

ENTITA_STATO = {
    "fase": "sensor.salumi_fase",
    "temperatura": "sensor.sonda_th_temperatura",
    "umidita": "sensor.sonda_th_umidita",
    "rugiada": "sensor.sonda_th_dew_point",
    "ah_camera": "sensor.salumi_umidita_assoluta_camera",
    "ah_cantina": "sensor.salumi_umidita_assoluta_cantina",
    "t_cantina": "sensor.shelly_h_t_cantina_temperature",
    "ur_cantina": "sensor.shelly_h_t_cantina_humidity",
    "stufa": "climate.salumi_stufa",
    "umidificatore": "humidifier.salumi_umidita",
    "rele_stufa": "switch.sonoff_1001f24fe4_2",
    "rele_umidificatore": "switch.sonoff_1001f24fe4_1",
    "peso": "sensor.salumi_peso",
    "peso_iniziale": "input_number.salumi_peso_iniziale",
    "calo_reale": "sensor.salumi_calo_reale",
    "calo_atteso": "sensor.salumi_calo_atteso",
    "calo_minimo": "sensor.salumi_calo_atteso_minimo",
    "calo_massimo": "sensor.salumi_calo_atteso_massimo",
    "energia_ciclo": "sensor.salumi_energia_ciclo_totale",
    "correzione_ur": "input_number.salumi_correzione_ur",
    "ciclo_attivo": "input_boolean.salumi_ciclo_attivo",
    "preparazione": "input_boolean.salumi_preparazione",
    "sensore_fermo": "input_boolean.salumi_sensore_fermo",
    "supervisione": "input_select.salumi_supervisione",
    "proposta": "input_text.salumi_proposta",
    "risposta": "input_text.salumi_risposta",
}
ATTR = {
    "fase": ["step", "temp_target", "ur_target", "correzione_ur", "fine_fase", "ore_trascorse",
             "ur_sgocciolamento", "tabella_temp", "tabella_ur", "tabella_estrazione"],
    "stufa": ["temperature", "current_temperature", "hvac_action"],
    "umidificatore": ["humidity", "current_humidity", "action"],
}


def stato():
    out = {"ora": datetime.now().isoformat(timespec="minutes"), "cartella_ciclo": cartella_ciclo()}
    for k, e in ENTITA_STATO.items():
        s = st(e)
        if s is None:
            out[k] = None
            continue
        v = {"stato": s["state"], "eta_min": eta_min(s)}
        for a in ATTR.get(k, []):
            v[a] = s["attributes"].get(a)
        out[k] = v
    out["ultimo_turno"] = leggi("ultimo_turno.json")
    out["modifiche_recenti"] = leggi("modifiche.json", [])[-10:]
    print(json.dumps(out, ensure_ascii=False, indent=1))


def storia(ore, passo=15):
    ore, passo = float(ore), int(passo)
    fine = datetime.now(timezone.utc)
    inizio = fine - timedelta(hours=ore)
    numeriche = {"T": "sensor.sonda_th_temperatura", "UR": "sensor.sonda_th_umidita",
                 "T_cantina": "sensor.shelly_h_t_cantina_temperature",
                 "UR_cantina": "sensor.shelly_h_t_cantina_humidity",
                 "AH_camera": "sensor.salumi_umidita_assoluta_camera",
                 "AH_cantina": "sensor.salumi_umidita_assoluta_cantina",
                 "peso": "sensor.salumi_peso"}
    onoff = {"stufa_on": "switch.sonoff_1001f24fe4_2", "umid_on": "switch.sonoff_1001f24fe4_1"}
    ids = ",".join(list(numeriche.values()) + list(onoff.values()) + ["sensor.salumi_fase"])
    q = urllib.parse.urlencode({"filter_entity_id": ids, "end_time": fine.isoformat()})
    dati = api(f"/history/period/{urllib.parse.quote(inizio.isoformat())}?{q}")
    serie = {}
    for lista in dati:
        if lista:
            serie[lista[0]["entity_id"]] = lista
    nbin = int(ore * 60 // passo) + 1

    def bin_di(ts):
        t = datetime.fromisoformat(ts)
        return int((t - inizio).total_seconds() // (passo * 60))

    righe = [{"da": (inizio + timedelta(minutes=i * passo)).astimezone().strftime("%d/%m %H:%M")}
             for i in range(nbin)]
    for nome, e in numeriche.items():
        acc = [[] for _ in range(nbin)]
        for s in serie.get(e, []):
            try:
                acc[max(0, min(nbin - 1, bin_di(s["last_changed"])))].append(float(s["state"]))
            except (ValueError, KeyError):
                pass
        ultimo = None  # valore invariato nel periodo: si ripete l'ultimo noto
        for i, a in enumerate(acc):
            if a:
                ultimo = round(sum(a) / len(a), 2)
            righe[i][nome] = ultimo
    for nome, e in onoff.items():
        stati = serie.get(e, [])
        for i in range(nbin):
            a = inizio + timedelta(minutes=i * passo)
            b = a + timedelta(minutes=passo)
            on = 0.0
            for j, s in enumerate(stati):
                t0 = max(datetime.fromisoformat(s["last_changed"]), a)
                t1 = min(datetime.fromisoformat(stati[j + 1]["last_changed"]) if j + 1 < len(stati) else fine, b)
                if s["state"] == "on" and t1 > t0:
                    on += (t1 - t0).total_seconds()
            righe[i][nome] = round(on / (passo * 60), 2)
    fasi = serie.get("sensor.salumi_fase", [])
    for i in range(nbin):
        b = inizio + timedelta(minutes=(i + 1) * passo)
        att = None
        for s in fasi:
            if datetime.fromisoformat(s["last_changed"]) <= b:
                att = s
        if att:
            righe[i]["fase"] = att["state"]
            righe[i]["T_target"] = att["attributes"].get("temp_target")
            righe[i]["UR_target"] = att["attributes"].get("ur_target")
    print(json.dumps({"passo_min": passo, "righe": righe}, ensure_ascii=False))


# --- foto -------------------------------------------------------------------

ESTENSIONI = (".jpg", ".jpeg", ".png", ".heic", ".webp")


def foto():
    os.makedirs(FOTO, exist_ok=True)
    dest = os.path.join(FOTO, cartella_ciclo())
    nuove = []
    for nome in sorted(os.listdir(FOTO)):
        p = os.path.join(FOTO, nome)
        if not (os.path.isfile(p) and nome.lower().endswith(ESTENSIONI)):
            continue
        os.makedirs(dest, exist_ok=True)
        ts = datetime.fromtimestamp(os.path.getmtime(p)).strftime("%Y%m%d_%H%M")
        ext = os.path.splitext(nome)[1].lower()
        q = os.path.join(dest, ts + ext)
        n = 2
        while os.path.exists(q):
            q = os.path.join(dest, f"{ts}_{n}{ext}")
            n += 1
        shutil.move(p, q)
        nuove.append(q)
    tutte = sorted(os.path.join(dest, f) for f in os.listdir(dest)) if os.path.isdir(dest) else []
    precedenti = [f for f in tutte if f not in nuove][-2:]
    print(json.dumps({"nuove": nuove, "precedenti_per_confronto": precedenti, "totale": len(tutte)},
                     ensure_ascii=False, indent=1))


# --- azioni -----------------------------------------------------------------

def avviso(titolo, testo, priorita=0):
    servizio("script", "salumi_avviso", {"titolo": "Salumi (Claude): " + titolo, "messaggio": testo,
                                         "priorita": int(priorita), "da_claude": True})
    print("avviso inviato")


def proposta(testo):
    servizio("input_text", "set_value", {"entity_id": "input_text.salumi_proposta", "value": testo[:255]})
    servizio("input_text", "set_value", {"entity_id": "input_text.salumi_risposta", "value": "in attesa"})
    print("proposta pubblicata in dashboard")


def proposta_chiudi():
    for e in ("input_text.salumi_proposta", "input_text.salumi_risposta"):
        servizio("input_text", "set_value", {"entity_id": e, "value": ""})
    print("proposta chiusa")


def imposta(entita, valore, motivo):
    if val("input_select.salumi_supervisione") != "attiva":
        sys.exit("RIFIUTATO: supervisione in modalità osservazione o sospesa, nessuna modifica consentita")
    if entita not in CONSENTITI:
        sys.exit(f"RIFIUTATO: {entita} non è tra i parametri modificabili: {list(CONSENTITI)}")
    lo, hi = CONSENTITI[entita]
    v = float(valore)
    if not lo <= v <= hi:
        sys.exit(f"RIFIUTATO: {v} fuori dai limiti {lo}…{hi}")
    prima = val(entita)
    servizio(entita.split(".")[0], "set_value", {"entity_id": entita, "value": v})
    mod = leggi("modifiche.json", [])
    mod.append({"quando": datetime.now().isoformat(timespec="minutes"), "entita": entita,
                "da": prima, "a": v, "motivo": motivo})
    scrivi("modifiche.json", mod[-200:])
    print(f"impostato {entita}: {prima} -> {v}")


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    cmd, args = a[0], a[1:]
    {"turno": turno, "fine_turno": fine_turno, "stato": stato, "storia": storia, "foto": foto,
     "avviso": avviso, "proposta": proposta, "proposta_chiudi": proposta_chiudi,
     "imposta": imposta}[cmd](*args)
