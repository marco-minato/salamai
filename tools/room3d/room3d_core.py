"""Nucleo del modello 3D della camera Salamai, in Python puro.

Carica la configurazione JSON (stanza + layout), la valida, ricava la
geometria nel frame canonico (metri, destrorso, Z verso l'alto) e calcola gli
hash semantici. Lo usano sia il Python di sistema (validate_config.py, test)
sia il Python incluso in Blender (build_scene.py): niente dipendenze esterne.

Convenzione delle grandezze ("Q"): ogni dato di rilievo è un oggetto
    {"value": <numero|lista|stringa|null>, "status": <stato>, "source": <id>,
     "draw_value": <valore provvisorio per disegnare>, "note": "..."}
con stato in STATUSES. Uno stato "unknown" ha sempre value null: il disegno
usa draw_value, che resta un'assunzione e non diventa mai un dato reale.
"""

import hashlib
import json
import math
import os

SCHEMA_VERSION = "1.0"

# Ordine crescente di incertezza: lo stato complessivo di un oggetto è il
# peggiore fra quelli delle grandezze usate per disegnarlo.
STATUSES = ("measured", "declared", "derived", "assumed", "unknown")
STATES = ("existing", "installed", "planned", "placeholder")
PLACEMENTS = ("interior", "external", "through_opening")
LAYOUT_KINDS = ("real_plan", "real_as_built", "hypothetical_demo")

LAYERS = [
    ("struttura", "Struttura"),
    ("aperture", "Aperture"),
    ("estrazione_ingresso", "Estrazione e ingresso aria"),
    ("ricircolo", "Ricircolo"),
    ("riscaldamento_umidificazione", "Riscaldamento e umidificazione"),
    ("supporti_prodotto", "Supporti e prodotto"),
    ("sensori", "Sensori"),
    ("quote_annotazioni", "Quote e annotazioni"),
    ("analisi_temporale", "Analisi temporale"),
]
LAYER_IDS = [lid for lid, _ in LAYERS]

GEOMETRY_KINDS = ("box", "cylinder", "fan", "pipe", "marker", "zone")
ID_CHARS = set("abcdefghijklmnopqrstuvwxyz0123456789_")

# Z-up canonico -> Y-up glTF (convenzione dell'esportatore glTF di Blender):
# (x, y, z) -> (x, z, -y). Il visualizzatore usa l'inversa (x, -z, y).
CANONICAL_TO_GLTF = [[1, 0, 0], [0, 0, 1], [0, -1, 0]]
GLTF_TO_CANONICAL = [[1, 0, 0], [0, 0, -1], [0, 1, 0]]


class ConfigError(Exception):
    """Configurazione non valida: contiene tutti i messaggi trovati."""

    def __init__(self, errors):
        self.errors = list(errors)
        super().__init__("\n".join(self.errors))


# --------------------------------------------------------------------------
# Caricamento e hash canonico


def _reject_constant(name):
    # json accetta NaN/Infinity: li lasciamo passare come float e li
    # segnaliamo in validazione con il percorso esatto.
    return float(name.replace("Infinity", "inf"))


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f, parse_constant=_reject_constant)


def canonical_json(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def load_model(room_path, layout_id=None):
    """Ritorna (room, catalog, [layout, ...]) con i percorsi risolti.

    Senza layout_id carica tutti i layout del catalogo.
    """
    room_path = os.path.abspath(room_path)
    room = load_json(room_path)
    base = os.path.dirname(room_path)
    catalog_path = os.path.join(base, room.get("layouts_catalog", "layouts/catalog.json"))
    catalog = load_json(catalog_path)
    entries = catalog.get("layouts", [])
    if layout_id is not None:
        entries = [e for e in entries if e.get("layout_id") == layout_id]
        if not entries:
            raise ConfigError([f"layout '{layout_id}' non presente in {catalog_path}"])
    layouts = []
    for e in entries:
        lpath = os.path.join(os.path.dirname(catalog_path), e["file"])
        layout = load_json(lpath)
        layout["_file"] = os.path.relpath(lpath, base)
        layouts.append(layout)
    room["_base_dir"] = base
    return room, catalog, layouts


def config_hash(room, layout):
    """Hash del JSON canonico (stanza + layout) che identifica la revisione."""
    clean_room = {k: v for k, v in room.items() if not k.startswith("_")}
    clean_layout = {k: v for k, v in layout.items() if not k.startswith("_")}
    return sha256_text(canonical_json({"room": clean_room, "layout": clean_layout}))


# --------------------------------------------------------------------------
# Grandezze Q


def is_q(obj):
    return isinstance(obj, dict) and "status" in obj and ("value" in obj or "draw_value" in obj)


def qv(q):
    """Valore usato per disegnare: il dato se noto, altrimenti draw_value."""
    if q.get("status") == "unknown" or q.get("value") is None:
        return q.get("draw_value")
    return q["value"]


def q_status(q):
    st = q.get("status")
    if st == "unknown" or q.get("value") is None:
        return "unknown"
    return st


def worst(statuses):
    idx = max((STATUSES.index(s) for s in statuses if s in STATUSES), default=0)
    return STATUSES[idx]


def vec3(field):
    """Vettore 3D da Q-lista oppure da {"x": Q, "y": Q, "z": Q}.

    Ritorna (valori, stato peggiore, stati per asse).
    """
    if is_q(field):
        v = qv(field)
        st = q_status(field)
        return [float(c) for c in v], st, {"x": st, "y": st, "z": st}
    vals, sts = [], {}
    for axis in "xyz":
        q = field[axis]
        vals.append(float(qv(q)))
        sts[axis] = q_status(q)
    return vals, worst(sts.values()), sts


def num(q):
    return float(qv(q))


# --------------------------------------------------------------------------
# Validazione


def _finite(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


class _V:
    def __init__(self, source_ids):
        self.errors = []
        self.warnings = []
        self.sources = source_ids

    def err(self, path, msg):
        self.errors.append(f"{path}: {msg}")

    def q(self, path, q, kind="number", positive=False, required=True):
        """Controlla una grandezza Q; ritorna il valore per disegnare o None."""
        if q is None:
            if required:
                self.err(path, "grandezza mancante")
            return None
        if not is_q(q):
            self.err(path, "attesa una grandezza {value, status, ...}")
            return None
        st = q.get("status")
        if st not in STATUSES:
            self.err(path, f"stato '{st}' non valido (ammessi: {', '.join(STATUSES)})")
            return None
        if st == "unknown":
            if q.get("value") is not None:
                self.err(path, "stato 'unknown' con value non nullo: uno sconosciuto non ha valore")
            if "draw_value" not in q:
                self.err(path, "grandezza sconosciuta senza draw_value provvisorio per il disegno")
                return None
        else:
            if q.get("value") is None:
                self.err(path, f"stato '{st}' senza value: usare status 'unknown' con draw_value")
                return None
        if st in ("measured", "declared") and q.get("source") not in self.sources:
            self.err(path, f"dato '{st}' senza source valida (source='{q.get('source')}')")
        if st == "assumed" and not q.get("note") and not q.get("assumption"):
            self.err(path, "assunzione senza note né riferimento ad assumption")
        if q.get("assumption") and q["assumption"] not in self.assumption_ids:
            self.err(path, f"assumption '{q['assumption']}' non definita")
        for key in ("value", "draw_value"):
            if key not in q or q[key] is None:
                continue
            v = q[key]
            if kind == "number":
                if not _finite(v):
                    self.err(f"{path}.{key}", f"numero non finito o non numerico: {v!r}")
                elif positive and v <= 0:
                    self.err(f"{path}.{key}", f"deve essere positivo, trovato {v}")
            elif kind == "vec3":
                if not (isinstance(v, list) and len(v) == 3 and all(_finite(c) for c in v)):
                    self.err(f"{path}.{key}", f"atteso vettore di 3 numeri finiti, trovato {v!r}")
                elif positive and any(c <= 0 for c in v):
                    self.err(f"{path}.{key}", f"tutte le componenti devono essere positive: {v}")
            elif kind == "string":
                if not isinstance(v, str):
                    self.err(f"{path}.{key}", "attesa una stringa")
            elif isinstance(kind, tuple):
                if v not in kind:
                    self.err(f"{path}.{key}", f"valore '{v}' non ammesso ({', '.join(kind)})")
        try:
            return qv(q)
        except Exception:
            return None

    def vec(self, path, field, positive=False):
        if field is None:
            self.err(path, "vettore mancante")
            return None
        if is_q(field):
            v = self.q(path, field, "vec3", positive)
            return v if isinstance(v, list) and len(v) == 3 and all(_finite(c) for c in v) else None
        if isinstance(field, dict) and set(field) >= {"x", "y", "z"}:
            out = []
            for a in "xyz":
                c = self.q(f"{path}.{a}", field[a], "number", positive)
                if not _finite(c):
                    return None
                out.append(c)
            return out
        self.err(path, "atteso vettore come Q-lista o {x, y, z}")
        return None


def _check_id(v, path, ident, seen):
    if not isinstance(ident, str) or not ident or ident[0].isdigit() or set(ident) - ID_CHARS:
        v.err(path, f"ID '{ident}' non valido: usare minuscole, cifre e _")
        return
    if ident in seen:
        v.err(path, f"ID duplicato '{ident}' (già usato in {seen[ident]})")
    else:
        seen[ident] = path


def room_dims(room):
    i = room["room"]["interior"]
    return num(i["size_x"]), num(i["size_y"]), num(i["size_z"])


def derive_openings(room):
    """Coordinate delle aperture nel frame canonico, con stati e regola usata."""
    sx, sy, sz = room_dims(room)
    d = room["openings"]["door"]
    h = room["openings"]["hatch"]
    door_x0 = num(d["x_min"])
    door_w = num(d["width"])
    door_h = num(d["height"])
    door = {
        "id": d["id"],
        "wall": "wall_y0",
        "x_min": door_x0,
        "x_max": door_x0 + door_w,
        "center_x": door_x0 + door_w / 2,
        "z_min": 0.0,
        "z_max": door_h,
        "width": door_w,
        "height": door_h,
        "status": {
            "x_min": q_status(d["x_min"]),
            "width": q_status(d["width"]),
            "height": q_status(d["height"]),
        },
        "hinge_side": qv(d["hinge_side"]),
        "hinge_status": q_status(d["hinge_side"]),
        "swing": qv(d["swing"]),
        "swing_status": q_status(d["swing"]),
    }
    hx, hy = num(h["size_x"]), num(h["size_y"])
    if h["center_x_rule"] != "door_center":
        raise ConfigError([f"openings.hatch.center_x_rule '{h['center_x_rule']}' non gestita"])
    cx = door["center_x"]
    off = num(h["offset_from_door_wall"])
    ref = qv(h["offset_reference"])
    if ref == "near_edge":
        y0 = off
    elif ref == "center":
        y0 = off - hy / 2
    elif ref == "far_edge":
        y0 = off - hy
    else:
        raise ConfigError([f"openings.hatch.offset_reference '{ref}' non gestito"])
    hatch = {
        "id": h["id"],
        "x_min": cx - hx / 2,
        "x_max": cx + hx / 2,
        "y_min": y0,
        "y_max": y0 + hy,
        "center_x": cx,
        "center_y": y0 + hy / 2,
        "z": sz,
        "size_x": hx,
        "size_y": hy,
        "offset_from_door_wall": off,
        "offset_reference": ref,
        "status": {
            "size_x": q_status(h["size_x"]),
            "size_y": q_status(h["size_y"]),
            "center_x": "derived",
            "offset_from_door_wall": q_status(h["offset_from_door_wall"]),
            "offset_reference": q_status(h["offset_reference"]),
            "y_min": worst([q_status(h["offset_from_door_wall"]), q_status(h["offset_reference"])]),
        },
    }
    door["texts"] = door_texts(door)
    hatch["texts"] = hatch_texts(hatch)
    return door, hatch


# Testi su porta e botola: derivati dai valori e dagli stati effettivi, mai
# scritti a mano, così una variante (es. offset_reference=center) o un
# rilievo aggiornano cartiglio, note, quote e visualizzatore insieme.
HATCH_REF_TEXT = {"near_edge": "al bordo vicino", "center": "al centro", "far_edge": "al bordo lontano"}
STATUS_WORD = {"measured": "misurato", "declared": "dichiarato", "derived": "derivato",
               "assumed": "ASSUNZIONE NON CONFERMATA", "unknown": "SCONOSCIUTO"}


def _m(x):
    """Metri con almeno due decimali e virgola: 0,40 · 0,175 · 1,90."""
    txt = f"{x:.3f}"
    if txt.endswith("0"):
        txt = txt[:-1]
    return txt.replace(".", ",")


def hatch_texts(h):
    ref_txt = HATCH_REF_TEXT[h["offset_reference"]]
    ref_st = h["status"]["offset_reference"]
    dist = f"{fmt_cm(h['offset_from_door_wall'])} dalla parete porta {ref_txt}"
    pos = f"Y {_m(h['y_min'])}–{_m(h['y_max'])} m"
    if ref_st in ("measured", "declared"):
        summary = f"Botola: {dist} ({pos}), riferimento {STATUS_WORD[ref_st]}."
        dim_suffix = ""
    else:
        summary = f"Botola: {dist} ({pos}); riferimento al {ref_txt[3:]} = {STATUS_WORD[ref_st]}."
        dim_suffix = f" ASSUNTO: {fmt_cm(h['offset_from_door_wall'])} {ref_txt}"
    return {"summary": summary, "dim_suffix": dim_suffix, "dim_status": h["status"]["y_min"],
            "entity_note": f"posizione Y: {dist}, riferimento {STATUS_WORD[ref_st]} ({pos})"}


def door_texts(d):
    st = d["status"]["height"]
    if st == "unknown":
        summary = f"Altezza porta sconosciuta ({_m(d['height'])} m solo per il disegno)."
        dim_suffix = " PROVVISORIO (altezza ignota)"
        note = "altezza sconosciuta: disegnata con valore provvisorio"
    elif st == "assumed":
        summary = f"Altezza porta {_m(d['height'])} m = ASSUNZIONE NON CONFERMATA."
        dim_suffix = " ASSUNTO"
        note = "altezza assunta, da rilevare"
    else:
        summary = f"Altezza porta {_m(d['height'])} m ({STATUS_WORD[st]})."
        dim_suffix = ""
        note = f"altezza {STATUS_WORD[st]}"
    return {"summary": summary, "dim_suffix": dim_suffix, "entity_note": note}


def validate(room, layouts, catalog=None):
    """Valida stanza e layout; solleva ConfigError con tutti gli errori."""
    src_ids = {s.get("id") for s in room.get("sources", []) if isinstance(s, dict)}
    v = _V(src_ids)
    v.assumption_ids = {a.get("id") for a in room.get("assumptions", []) if isinstance(a, dict)}
    for lay in layouts:
        v.assumption_ids |= {a.get("id") for a in lay.get("assumptions", []) if isinstance(a, dict)}

    if room.get("schema_version") != SCHEMA_VERSION:
        v.err("schema_version", f"atteso '{SCHEMA_VERSION}', trovato {room.get('schema_version')!r}")
    units = room.get("units", {})
    if units.get("length") != "m":
        v.err("units.length", "l'unità canonica deve essere 'm'")
    fr = room.get("frame", {})
    if fr.get("handedness") != "right" or fr.get("up") != "+Z":
        v.err("frame", "il frame canonico deve essere destrorso con up '+Z'")
    tol = room.get("tolerance_m")
    if not _finite(tol) or tol <= 0:
        v.err("tolerance_m", "tolleranza mancante o non positiva")
        tol = 0.0005

    seen_ids = {}
    for i, s in enumerate(room.get("sources", [])):
        _check_id(v, f"sources[{i}]", s.get("id"), seen_ids)
    for i, a in enumerate(room.get("assumptions", [])):
        _check_id(v, f"assumptions[{i}]", a.get("id"), seen_ids)

    rr = room.get("room", {})
    inter = rr.get("interior", {})
    sx = v.q("room.interior.size_x", inter.get("size_x"), positive=True)
    sy = v.q("room.interior.size_y", inter.get("size_y"), positive=True)
    sz = v.q("room.interior.size_z", inter.get("size_z"), positive=True)
    parts = inter.get("x_breakdown", [])
    pv = [v.q(f"room.interior.x_breakdown[{i}]", p, positive=True) for i, p in enumerate(parts)]
    if sx is not None and pv and all(_finite(p) for p in pv) and abs(sum(pv) - sx) > tol:
        v.err("room.interior.x_breakdown", f"somma {sum(pv):.4f} diversa da size_x {sx:.4f}")
    for key in ("wall_thickness", "floor_thickness", "ceiling_thickness"):
        v.q(f"room.{key}", rr.get(key), positive=True)
    if v.errors:
        raise ConfigError(v.errors)

    op = room.get("openings", {})
    d = op.get("door", {})
    h = op.get("hatch", {})
    _check_id(v, "openings.door.id", d.get("id"), seen_ids)
    _check_id(v, "openings.hatch.id", h.get("id"), seen_ids)
    v.q("openings.door.x_min", d.get("x_min"))
    v.q("openings.door.width", d.get("width"), positive=True)
    v.q("openings.door.height", d.get("height"), positive=True)
    v.q("openings.door.hinge_side", d.get("hinge_side"), ("x_min", "x_max"))
    v.q("openings.door.swing", d.get("swing"), ("inward", "outward"))
    v.q("openings.door.leaf_open_deg", d.get("leaf_open_deg"))
    v.q("openings.door.leaf_thickness", d.get("leaf_thickness"), positive=True)
    v.q("openings.hatch.size_x", h.get("size_x"), positive=True)
    v.q("openings.hatch.size_y", h.get("size_y"), positive=True)
    v.q("openings.hatch.offset_from_door_wall", h.get("offset_from_door_wall"))
    v.q("openings.hatch.offset_reference", h.get("offset_reference"), ("near_edge", "center", "far_edge"))
    if v.errors:
        raise ConfigError(v.errors)

    door, hatch = derive_openings(room)
    if door["x_min"] < -tol or door["x_max"] > sx + tol:
        v.err("openings.door", f"porta fuori dalla parete: X {door['x_min']:.3f}–{door['x_max']:.3f}, parete 0–{sx:.3f}")
    if door["z_max"] > sz + tol:
        v.err("openings.door.height", f"porta più alta della stanza ({door['z_max']:.3f} > {sz:.3f})")
    if (hatch["x_min"] < -tol or hatch["x_max"] > sx + tol or hatch["y_min"] < -tol
            or hatch["y_max"] > sy + tol):
        v.err("openings.hatch", (
            f"botola fuori dal soffitto: X {hatch['x_min']:.3f}–{hatch['x_max']:.3f}, "
            f"Y {hatch['y_min']:.3f}–{hatch['y_max']:.3f}"))

    for lay in layouts:
        _validate_layout(v, lay, room, dict(seen_ids), (sx, sy, sz), door, hatch, tol)
    if catalog is not None:
        kinds = {e.get("layout_id"): e.get("kind") for e in catalog.get("layouts", [])}
        if len(kinds) != len(catalog.get("layouts", [])):
            v.err("catalog.layouts", "layout_id duplicato nel catalogo")
        for lay in layouts:
            if kinds.get(lay.get("layout_id")) != lay.get("kind"):
                v.err(f"catalog[{lay.get('layout_id')}]", "kind del catalogo diverso da quello del layout")
    if v.errors:
        raise ConfigError(v.errors)
    return v.warnings


def _validate_layout(v, lay, room, seen_ids, dims, door, hatch, tol):
    lp = f"layout[{lay.get('layout_id')}]"
    if lay.get("schema_version") != SCHEMA_VERSION:
        v.err(f"{lp}.schema_version", f"atteso '{SCHEMA_VERSION}'")
    lid = lay.get("layout_id")
    if not isinstance(lid, str) or not lid:
        v.err(lp, "layout_id mancante")
    if lay.get("kind") not in LAYOUT_KINDS:
        v.err(f"{lp}.kind", f"tipo '{lay.get('kind')}' non ammesso ({', '.join(LAYOUT_KINDS)})")
    for i, a in enumerate(lay.get("assumptions", [])):
        _check_id(v, f"{lp}.assumptions[{i}]", a.get("id"), seen_ids)
    for i, c in enumerate(lay.get("components", [])):
        _validate_component(v, f"{lp}.components[{i}]", c, seen_ids, dims, door, hatch, tol)


def _validate_component(v, path, c, seen_ids, dims, door, hatch, tol):
    _check_id(v, f"{path}.id", c.get("id"), seen_ids)
    path = f"{path}({c.get('id')})"
    if c.get("layer") not in LAYER_IDS:
        v.err(f"{path}.layer", f"layer '{c.get('layer')}' non esistente")
    if c.get("state") not in STATES:
        v.err(f"{path}.state", f"stato '{c.get('state')}' non ammesso ({', '.join(STATES)})")
    if not c.get("type"):
        v.err(f"{path}.type", "tipo mancante")
    placement = c.get("placement", "interior")
    if placement not in PLACEMENTS:
        v.err(f"{path}.placement", f"'{placement}' non ammesso ({', '.join(PLACEMENTS)})")
    if placement in ("external", "through_opening") and not c.get("placement_reason"):
        v.err(f"{path}.placement_reason", "elemento fuori dalla stanza senza motivazione")
    g = c.get("geometry", {})
    kind = g.get("kind")
    if kind not in GEOMETRY_KINDS:
        v.err(f"{path}.geometry.kind", f"tipo geometria '{kind}' non ammesso")
        return
    n_err = len(v.errors)
    if kind in ("box", "zone"):
        v.vec(f"{path}.geometry.center", g.get("center"))
        v.vec(f"{path}.geometry.size", g.get("size"), positive=True)
        if "yaw_deg" in g:
            v.q(f"{path}.geometry.yaw_deg", g["yaw_deg"])
    elif kind == "marker":
        v.vec(f"{path}.geometry.center", g.get("center"))
        v.q(f"{path}.geometry.diameter", g.get("diameter"), positive=True)
    elif kind in ("cylinder", "fan"):
        v.vec(f"{path}.geometry.center", g.get("center"))
        ax = v.vec(f"{path}.geometry.axis", g.get("axis"))
        if ax is not None:
            n = math.sqrt(sum(a * a for a in ax))
            if n < 1e-9:
                v.err(f"{path}.geometry.axis", "asse nullo")
            elif abs(n - 1) > 1e-6:
                v.err(f"{path}.geometry.axis", f"asse non normalizzato (|a|={n:.6f}): usare un versore")
        if kind == "cylinder":
            v.q(f"{path}.geometry.diameter", g.get("diameter"), positive=True)
            v.q(f"{path}.geometry.length", g.get("length"), positive=True)
        else:
            v.q(f"{path}.geometry.frame_size", g.get("frame_size"), positive=True)
            v.q(f"{path}.geometry.depth", g.get("depth"), positive=True)
            v.q(f"{path}.geometry.rotor_diameter", g.get("rotor_diameter"), positive=True)
    elif kind == "pipe":
        pts = g.get("points", [])
        if not isinstance(pts, list) or len(pts) < 2:
            v.err(f"{path}.geometry.points", "servono almeno due punti")
        else:
            vals = [v.vec(f"{path}.geometry.points[{i}]", p) for i, p in enumerate(pts)]
            for i in range(1, len(vals)):
                a, b = vals[i - 1], vals[i]
                if a and b and _dist(a, b) < 1e-6:
                    v.err(f"{path}.geometry.points[{i}]", "punto coincidente con il precedente")
        od = v.q(f"{path}.geometry.outer_diameter", g.get("outer_diameter"), positive=True)
        if g.get("inner_diameter") is not None:
            idm = v.q(f"{path}.geometry.inner_diameter", g.get("inner_diameter"), positive=True)
            if _finite(od) and _finite(idm) and idm >= od:
                v.err(f"{path}.geometry.inner_diameter", "diametro interno non minore dell'esterno")
        needs_bend = isinstance(pts, list) and len(pts) > 2
        br = v.q(f"{path}.geometry.bend_radius", g.get("bend_radius"), positive=True, required=needs_bend)
        if len(v.errors) == n_err and isinstance(pts, list) and len(pts) >= 2 and (_finite(br) or not needs_bend):
            try:
                pipe_path(g)
            except ValueError as e:
                v.err(f"{path}.geometry", str(e))
    for key, q in (c.get("properties") or {}).items():
        if not is_q(q):
            v.err(f"{path}.properties.{key}", "proprietà senza {value, status}: indicare provenienza")
        elif q.get("status") not in STATUSES:
            v.err(f"{path}.properties.{key}", f"stato '{q.get('status')}' non valido")
        elif q.get("status") in ("measured", "declared") and q.get("source") not in v.sources:
            v.err(f"{path}.properties.{key}", "dato dichiarato/misurato senza source valida")
        elif q.get("status") == "unknown" and q.get("value") is not None:
            v.err(f"{path}.properties.{key}", "stato 'unknown' con value non nullo")
    if len(v.errors) != n_err:
        return
    bb = bbox_of(component_parts(c)[0][1])
    if placement == "interior":
        sx, sy, sz = dims
        lo, hi = bb
        if (lo[0] < -tol or lo[1] < -tol or lo[2] < -tol or hi[0] > sx + tol or hi[1] > sy + tol
                or hi[2] > sz + tol):
            v.err(path, (
                "elemento fuori dalla stanza: bbox "
                f"[{lo[0]:.3f},{lo[1]:.3f},{lo[2]:.3f}]–[{hi[0]:.3f},{hi[1]:.3f},{hi[2]:.3f}]; "
                "se è voluto usare placement 'external' o 'through_opening' con motivazione"))
    elif placement == "through_opening":
        ref = c.get("opening")
        lo, hi = bb
        if ref == hatch["id"]:
            ok = (lo[0] >= hatch["x_min"] - tol and hi[0] <= hatch["x_max"] + tol
                  and lo[1] >= hatch["y_min"] - tol and hi[1] <= hatch["y_max"] + tol)
            if not ok:
                v.err(path, "elemento 'through_opening' non contenuto nell'impronta della botola")
        elif ref == door["id"]:
            ok = (lo[0] >= door["x_min"] - tol and hi[0] <= door["x_max"] + tol
                  and lo[2] >= -tol and hi[2] <= door["z_max"] + tol)
            if not ok:
                v.err(path, "elemento 'through_opening' non contenuto nella luce della porta")
        else:
            v.err(f"{path}.opening", f"apertura '{ref}' non esistente")


# --------------------------------------------------------------------------
# Geometria


def _dist(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def _sub(a, b):
    return [x - y for x, y in zip(a, b)]


def _add(a, b):
    return [x + y for x, y in zip(a, b)]


def _mul(a, s):
    return [x * s for x in a]


def _dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def _cross(a, b):
    return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]


def _norm(a):
    n = math.sqrt(_dot(a, a))
    return [x / n for x in a]


def _perp_basis(axis):
    a = _norm(axis)
    ref = [0, 0, 1] if abs(a[2]) < 0.9 else [1, 0, 0]
    u = _norm(_cross(ref, a))
    w = _cross(a, u)
    return a, u, w


def mesh_box(center, size, yaw_deg=0.0):
    cx, cy, cz = center
    hx, hy, hz = (s / 2 for s in size)
    c, s = math.cos(math.radians(yaw_deg)), math.sin(math.radians(yaw_deg))
    verts = []
    for z in (-hz, hz):
        for x, y in ((-hx, -hy), (hx, -hy), (hx, hy), (-hx, hy)):
            verts.append([cx + x * c - y * s, cy + x * s + y * c, cz + z])
    faces = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    return verts, faces


def mesh_aabb(lo, hi):
    return mesh_box([(a + b) / 2 for a, b in zip(lo, hi)], [b - a for a, b in zip(lo, hi)])


def mesh_cylinder(base, axis, radius, length, segs=24, cap=True):
    a, u, w = _perp_basis(axis)
    verts = []
    for end in (0.0, length):
        for i in range(segs):
            t = 2 * math.pi * i / segs
            p = _add(_add(base, _mul(a, end)), _add(_mul(u, radius * math.cos(t)), _mul(w, radius * math.sin(t))))
            verts.append(p)
    faces = [(i, (i + 1) % segs, segs + (i + 1) % segs, segs + i) for i in range(segs)]
    if cap:
        faces.append(tuple(reversed(range(segs))))
        faces.append(tuple(range(segs, 2 * segs)))
    return verts, faces


def mesh_cone(base, axis, radius, length, segs=24):
    a, u, w = _perp_basis(axis)
    verts = [_add(base, _add(_mul(u, radius * math.cos(2 * math.pi * i / segs)),
                             _mul(w, radius * math.sin(2 * math.pi * i / segs)))) for i in range(segs)]
    verts.append(_add(base, _mul(a, length)))
    tip = segs
    faces = [(i, (i + 1) % segs, tip) for i in range(segs)]
    faces.append(tuple(reversed(range(segs))))
    return verts, faces


def mesh_uv_sphere(center, radius, segs=16, rings=8):
    verts = [[center[0], center[1], center[2] - radius]]
    for r in range(1, rings):
        phi = -math.pi / 2 + math.pi * r / rings
        for s in range(segs):
            t = 2 * math.pi * s / segs
            verts.append([center[0] + radius * math.cos(phi) * math.cos(t),
                          center[1] + radius * math.cos(phi) * math.sin(t),
                          center[2] + radius * math.sin(phi)])
    verts.append([center[0], center[1], center[2] + radius])
    top = len(verts) - 1
    faces = [(0, 1 + (s + 1) % segs, 1 + s) for s in range(segs)]
    for r in range(rings - 2):
        o = 1 + r * segs
        for s in range(segs):
            faces.append((o + s, o + (s + 1) % segs, o + segs + (s + 1) % segs, o + segs + s))
    o = 1 + (rings - 2) * segs
    faces += [(o + s, o + (s + 1) % segs, top) for s in range(segs)]
    return verts, faces


def mesh_prism_with_hole(outer, hole, axis, t0, t1):
    """Prisma da un rettangolo 2D (u0,u1,v0,v1) con un foro rettangolare.

    axis: 'y' -> piano XZ estruso lungo Y, 'z' -> piano XY estruso lungo Z.
    Se il foro tocca il bordo v0 (porta a filo pavimento) diventa un intaglio.
    """
    u0, u1, v0, v1 = outer
    h0, h1, k0, k1 = hole

    def P(u, v, t):
        return [u, t, v] if axis == "y" else [u, v, t]

    if abs(k0 - v0) < 1e-12:
        loop = [(u0, v0), (h0, v0), (h0, k1), (h1, k1), (h1, v0), (u1, v0), (u1, v1), (u0, v1)]
        n = len(loop)
        verts = [P(u, v, t0) for u, v in loop] + [P(u, v, t1) for u, v in loop]
        faces = [tuple(reversed(range(n))), tuple(range(n, 2 * n))]
        faces += [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
        if axis == "y":
            faces = [tuple(reversed(f)) for f in faces]
        return verts, faces
    o = [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]
    i_ = [(h0, k0), (h1, k0), (h1, k1), (h0, k1)]
    verts = []
    for t in (t0, t1):
        verts += [P(u, v, t) for u, v in o] + [P(u, v, t) for u, v in i_]
    faces = []
    for base, flip in ((0, True), (8, False)):
        for j in range(4):
            q = (base + j, base + (j + 1) % 4, base + 4 + (j + 1) % 4, base + 4 + j)
            faces.append(tuple(reversed(q)) if flip else q)
    for j in range(4):
        faces.append((j, (j + 1) % 4, 8 + (j + 1) % 4, 8 + j))
        faces.append((4 + (j + 1) % 4, 4 + j, 12 + j, 12 + (j + 1) % 4))
    if axis == "y":
        faces = [tuple(reversed(f)) for f in faces]
    return verts, faces


def merge_meshes(meshes):
    verts, faces = [], []
    for mv, mf in meshes:
        o = len(verts)
        verts += mv
        faces += [tuple(i + o for i in f) for f in mf]
    return verts, faces


def bbox_of(verts):
    lo = [min(v[i] for v in verts) for i in range(3)]
    hi = [max(v[i] for v in verts) for i in range(3)]
    return lo, hi


def pipe_path(g, arc_steps=8):
    """Asse della tubazione con raccordi ad arco di raggio bend_radius.

    Ritorna dict con polilinea campionata, tratti rettilinei e curve con
    lunghezze calcolate dalla geometria rappresentata.
    """
    pts = [vec3(p)[0] for p in g["points"]]
    R = num(g["bend_radius"]) if g.get("bend_radius") is not None else 0.0
    if len(pts) > 2 and R <= 0:
        raise ValueError("tubazione con curve senza bend_radius")
    straights, bends = [], []
    tangents_in = [None] * len(pts)
    trims = [0.0] * len(pts)
    for i in range(1, len(pts) - 1):
        d1 = _norm(_sub(pts[i], pts[i - 1]))
        d2 = _norm(_sub(pts[i + 1], pts[i]))
        cosang = max(-1.0, min(1.0, _dot(d1, d2)))
        theta = math.acos(cosang)
        if theta < 1e-6:
            continue
        if theta > math.pi - 1e-3:
            raise ValueError(f"inversione di 180° al punto {i}: impossibile raccordare")
        trims[i] = R * math.tan(theta / 2)
        tangents_in[i] = (d1, d2, theta)
    for i in range(1, len(pts)):
        seg = _dist(pts[i - 1], pts[i])
        if trims[i - 1] + trims[i] > seg + 1e-9:
            raise ValueError(
                f"tratto {i} lungo {seg:.3f} m troppo corto per i raccordi di raggio {R:.3f} m")
    samples = [pts[0]]
    for i in range(1, len(pts)):
        a, b = pts[i - 1], pts[i]
        d = _norm(_sub(b, a))
        start = _add(a, _mul(d, trims[i - 1]))
        end = _sub(b, _mul(d, trims[i]))
        straights.append({"id": f"s{i}", "start": start, "end": end, "length": _dist(start, end)})
        if _dist(samples[-1], start) > 1e-9:
            samples.append(start)
        samples.append(end)
        if i < len(pts) - 1 and tangents_in[i]:
            d1, d2, theta = tangents_in[i]
            corner = pts[i]
            p0 = _sub(corner, _mul(d1, trims[i]))
            bis = _norm(_sub(d2, d1))
            center = _add(corner, _mul(bis, R / math.cos(theta / 2)))
            r0 = _sub(p0, center)
            # rotazione di r0 attorno alla normale del piano della curva
            nrm = _norm(_cross(d1, d2))
            for k in range(1, arc_steps + 1):
                ang = theta * k / arc_steps
                rr = _add(_add(_mul(r0, math.cos(ang)), _mul(_cross(nrm, r0), math.sin(ang))),
                          _mul(nrm, _dot(nrm, r0) * (1 - math.cos(ang))))
                samples.append(_add(center, rr))
            bends.append({"id": f"b{i}", "at_point": i, "angle_deg": math.degrees(theta),
                          "radius": R, "length": R * theta, "center": center})
    total = sum(s["length"] for s in straights) + sum(b["length"] for b in bends)
    return {"samples": samples, "straights": straights, "bends": bends, "length": total}


def mesh_tube(samples, radius, segs=16):
    """Tubo lungo una polilinea con trasporto parallelo del riferimento."""
    n = len(samples)
    tangents = []
    for i in range(n):
        if i == 0:
            t = _sub(samples[1], samples[0])
        elif i == n - 1:
            t = _sub(samples[-1], samples[-2])
        else:
            t = _add(_norm(_sub(samples[i], samples[i - 1])), _norm(_sub(samples[i + 1], samples[i])))
        tangents.append(_norm(t))
    _, u, _ = _perp_basis(tangents[0])
    verts, faces = [], []
    for i in range(n):
        t = tangents[i]
        u = _norm(_sub(u, _mul(t, _dot(u, t))))
        w = _cross(t, u)
        for s in range(segs):
            ang = 2 * math.pi * s / segs
            verts.append(_add(samples[i], _add(_mul(u, radius * math.cos(ang)), _mul(w, radius * math.sin(ang)))))
    for i in range(n - 1):
        for s in range(segs):
            a, b = i * segs + s, i * segs + (s + 1) % segs
            faces.append((a, b, b + segs, a + segs))
    faces.append(tuple(reversed(range(segs))))
    faces.append(tuple(range((n - 1) * segs, n * segs)))
    return verts, faces


def _arrow(start, direction, length, radius):
    d = _norm(direction)
    shaft = length * 0.72
    m1 = mesh_cylinder(start, d, radius, shaft, segs=12)
    m2 = mesh_cone(_add(start, _mul(d, shaft)), d, radius * 2.6, length - shaft, segs=12)
    return merge_meshes([m1, m2])


def component_parts(c):
    """Parti mesh di un componente: lista di (suffisso, verts, faces, ruolo)."""
    g = c["geometry"]
    kind = g["kind"]
    if kind in ("box", "zone"):
        center, _, _ = vec3(g["center"])
        size, _, _ = vec3(g["size"])
        yaw = num(g["yaw_deg"]) if "yaw_deg" in g else 0.0
        v, f = mesh_box(center, size, yaw)
        return [("", v, f, "body")]
    if kind == "marker":
        center, _, _ = vec3(g["center"])
        v, f = mesh_uv_sphere(center, num(g["diameter"]) / 2)
        return [("", v, f, "body")]
    if kind == "cylinder":
        center, _, _ = vec3(g["center"])
        axis, _, _ = vec3(g["axis"])
        L = num(g["length"])
        base = _sub(center, _mul(_norm(axis), L / 2))
        v, f = mesh_cylinder(base, axis, num(g["diameter"]) / 2, L)
        return [("", v, f, "body")]
    if kind == "fan":
        center, _, _ = vec3(g["center"])
        axis = _norm(vec3(g["axis"])[0])
        fs, dp, rd = num(g["frame_size"]), num(g["depth"]), num(g["rotor_diameter"])
        a, u, w = _perp_basis(axis)
        back = _sub(center, _mul(a, dp / 2))
        # telaio quadrato orientato sull'asse: 4 barre
        bar = (fs - rd) / 2 if fs > rd else fs * 0.08
        bars = []
        for su, sw, lu, lw in ((0, 1, fs, bar), (0, -1, fs, bar), (1, 0, bar, fs - 2 * bar), (-1, 0, bar, fs - 2 * bar)):
            off = _add(_mul(u, su * (fs - lu) / 2), _mul(w, sw * (fs - lw) / 2))
            corners = []
            for t in (0.0, dp):
                for du, dw in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
                    corners.append(_add(_add(back, _mul(a, t)), _add(off, _add(_mul(u, du * lu / 2), _mul(w, dw * lw / 2)))))
            bars.append((corners, [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]))
        hub = mesh_cylinder(back, a, rd * 0.18, dp, segs=16)
        ring = mesh_cylinder(_add(back, _mul(a, dp * 0.2)), a, rd / 2, dp * 0.6, segs=24, cap=False)
        body = merge_meshes(bars + [hub, ring])
        arrow_len = num(g["arrow_length"]) if "arrow_length" in g else 0.30
        arr = _arrow(_add(center, _mul(a, dp / 2 + 0.01)), a, arrow_len, 0.008)
        return [("", body[0], body[1], "body"), ("__flow_arrow", arr[0], arr[1], "nominal_flow_arrow")]
    if kind == "pipe":
        pp = pipe_path(g)
        v, f = mesh_tube(pp["samples"], num(g["outer_diameter"]) / 2)
        return [("", v, f, "body")]
    raise ValueError(kind)


def component_status(c):
    """Stato complessivo dei dati geometrici e dettaglio per campo."""
    g = c["geometry"]
    detail = {}
    for key, val in g.items():
        if key == "kind":
            continue
        if key == "points":
            sts = [vec3(p)[1] for p in val]
            detail[key] = worst(sts)
        elif is_q(val):
            detail[key] = q_status(val)
        elif isinstance(val, dict) and set(val) >= {"x", "y", "z"}:
            _, st, per_axis = vec3(val)
            detail[key] = st
            detail[key + "_axes"] = per_axis
    return worst(v for k, v in detail.items() if isinstance(v, str)), detail


def structure_parts(room):
    """Pavimento, soffitto con botola e pareti (porta come foro reale)."""
    sx, sy, sz = room_dims(room)
    t = num(room["room"]["wall_thickness"])
    tf = num(room["room"]["floor_thickness"])
    tc = num(room["room"]["ceiling_thickness"])
    door, hatch = derive_openings(room)
    st_dims = worst(q_status(room["room"]["interior"][k]) for k in ("size_x", "size_y", "size_z"))
    st_thick = q_status(room["room"]["wall_thickness"])
    parts = []

    def add(eid, name, mesh, status, notes):
        parts.append({"id": eid, "name": name, "layer": "struttura", "type": "structure",
                      "state": "existing", "mesh": mesh, "data_status": status, "notes": notes,
                      "placement": "interior"})

    thick_note = "spessore convenzionale disegnato all'esterno del volume interno (spessore reale sconosciuto)"
    add("floor", "Pavimento", mesh_aabb([-t, -t, -tf], [sx + t, sy + t, 0.0]),
        worst([st_dims, q_status(room["room"]["floor_thickness"])]), [thick_note])
    add("ceiling", "Soffitto (con botola)",
        mesh_prism_with_hole((-t, sx + t, -t, sy + t),
                             (hatch["x_min"], hatch["x_max"], hatch["y_min"], hatch["y_max"]),
                             "z", sz, sz + tc),
        worst([st_dims, hatch["status"]["y_min"], q_status(room["room"]["ceiling_thickness"])]),
        [thick_note, "foro della botola: " + hatch["texts"]["entity_note"]])
    add("wall_y0", "Parete porta (Y=0)",
        mesh_prism_with_hole((-t, sx + t, 0.0, sz), (door["x_min"], door["x_max"], 0.0, door["z_max"]),
                             "y", -t, 0.0),
        worst([st_dims, st_thick, q_status(room["openings"]["door"]["height"])]),
        [thick_note, "luce porta reale nella geometria; altezza porta sconosciuta (disegnata con valore provvisorio)"])
    add("wall_y1", "Parete opposta alla porta (Y=1,60)",
        mesh_aabb([-t, sy, 0.0], [sx + t, sy + t, sz]), worst([st_dims, st_thick]), [thick_note])
    add("wall_x0", "Parete sinistra (X=0)",
        mesh_aabb([-t, 0.0, 0.0], [0.0, sy, sz]), worst([st_dims, st_thick]), [thick_note])
    add("wall_x1", "Parete destra (X=3,03)",
        mesh_aabb([sx, 0.0, 0.0], [sx + t, sy, sz]), worst([st_dims, st_thick]), [thick_note])
    return parts


def opening_parts(room):
    """Cornici di riferimento delle aperture e anta della porta (esterna)."""
    sx, sy, sz = room_dims(room)
    door, hatch = derive_openings(room)
    d = room["openings"]["door"]
    t = num(room["room"]["wall_thickness"])
    fw = 0.015  # cornice disegnata attorno alla luce, fuori dalla luce libera
    out = []
    fr = [mesh_aabb([door["x_min"] - fw, 0.0, 0.0], [door["x_min"], 0.004, door["z_max"]]),
          mesh_aabb([door["x_max"], 0.0, 0.0], [door["x_max"] + fw, 0.004, door["z_max"]]),
          mesh_aabb([door["x_min"] - fw, 0.0, door["z_max"]], [door["x_max"] + fw, 0.004, door["z_max"] + fw])]
    out.append({"id": door["id"], "name": "Porta (luce libera)", "layer": "aperture", "type": "door_opening",
                "state": "existing", "mesh": merge_meshes(fr), "placement": "interior",
                "data_status": worst(door["status"].values()),
                "notes": ["cornice di riferimento attorno alla luce; la luce è un foro reale nella parete",
                          door["texts"]["entity_note"]]})
    hf = [mesh_aabb([hatch["x_min"] - fw, hatch["y_min"] - fw, sz - 0.004], [hatch["x_max"] + fw, hatch["y_min"], sz]),
          mesh_aabb([hatch["x_min"] - fw, hatch["y_max"], sz - 0.004], [hatch["x_max"] + fw, hatch["y_max"] + fw, sz]),
          mesh_aabb([hatch["x_min"] - fw, hatch["y_min"], sz - 0.004], [hatch["x_min"], hatch["y_max"], sz]),
          mesh_aabb([hatch["x_max"], hatch["y_min"], sz - 0.004], [hatch["x_max"] + fw, hatch["y_max"], sz])]
    out.append({"id": hatch["id"], "name": "Botola a soffitto (luce libera)", "layer": "aperture",
                "type": "hatch_opening", "state": "existing", "mesh": merge_meshes(hf), "placement": "interior",
                "data_status": worst(hatch["status"].values()),
                "notes": [hatch["texts"]["entity_note"]]})
    # anta: interpretazione grafica, esterna alla stanza
    ang = math.radians(num(d["leaf_open_deg"]))
    lt = num(d["leaf_thickness"])
    hinge_x = door["x_max"] if door["hinge_side"] == "x_max" else door["x_min"]
    sign_x = -1 if door["hinge_side"] == "x_max" else 1
    outward = door["swing"] == "outward"
    y_face = -t if outward else 0.0
    sy_dir = -1 if outward else 1
    w = door["width"]
    dirv = [sign_x * math.cos(ang), sy_dir * math.sin(ang), 0.0]
    nrm = [-dirv[1], dirv[0], 0.0]
    p0 = [hinge_x, y_face, 0.0]
    corners = []
    for z in (0.0, door["z_max"]):
        for a_, b_ in ((0, 0), (w, 0), (w, lt), (0, lt)):
            p = _add(p0, _add(_mul(dirv, a_), _mul(nrm, b_ * sy_dir * sign_x)))
            corners.append([p[0], p[1], z])
    leaf = (corners, [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)])
    out.append({"id": "door_01_leaf", "name": "Anta porta (aperta, interpretazione)", "layer": "aperture",
                "type": "door_leaf", "state": "existing", "mesh": leaf,
                "placement": "external" if outward else "interior",
                "placement_reason": "anta disegnata aperta per lasciare libera la luce",
                "data_status": worst([door["hinge_status"], door["swing_status"], q_status(d["leaf_open_deg"])]),
                "notes": ["verso di apertura e cerniera NON confermati: lo schizzo sembra mostrare apertura verso "
                          "l'esterno, prompt_schema_qelectrotech.md:417 dice 'apre verso l'interno'",
                          "angolo di apertura solo per il disegno"]})
    return out


def build_entities(room, layout):
    """Tutte le entità (struttura, aperture, componenti) con le loro mesh."""
    ents = structure_parts(room) + opening_parts(room)
    for c in layout.get("components", []):
        status, detail = component_status(c)
        for suffix, verts, faces, role in component_parts(c):
            ent = {
                "id": c["id"] + suffix,
                "entity_id": c["id"],
                "role": role,
                "name": c.get("name", c["id"]) + (" — freccia direzione nominale (non simulata)" if role == "nominal_flow_arrow" else ""),
                "layer": c["layer"],
                "type": c["type"],
                "state": c["state"],
                "mesh": (verts, faces),
                "data_status": status,
                "status_detail": detail,
                "placement": c.get("placement", "interior"),
                "placement_reason": c.get("placement_reason"),
                "notes": list(c.get("notes", [])),
                "component": c,
            }
            if role == "nominal_flow_arrow":
                ent["notes"] = ["direzione nominale del soffio, NON simulata"]
            ents.append(ent)
    for e in ents:
        e.setdefault("entity_id", e["id"])
        e.setdefault("role", "body")
    return ents


# --------------------------------------------------------------------------
# Quote


def dimension_lines(room, layout):
    """Quote da disegnare: punti nel frame canonico, valore e stato."""
    sx, sy, sz = room_dims(room)
    door, hatch = derive_openings(room)
    i = room["room"]["interior"]
    xb = i.get("x_breakdown", [])
    dims = [
        {"id": "dim_room_x", "view": "plan", "p1": [0, 0, 0], "p2": [sx, 0, 0], "offset": [0, -0.45, 0],
         "status": q_status(i["size_x"])},
        {"id": "dim_room_y", "view": "plan", "p1": [sx, 0, 0], "p2": [sx, sy, 0], "offset": [0.45, 0, 0],
         "status": q_status(i["size_y"])},
        {"id": "dim_wall_left", "view": "plan", "p1": [0, 0, 0], "p2": [door["x_min"], 0, 0], "offset": [0, -0.25, 0],
         "status": q_status(xb[0]) if xb else "derived"},
        {"id": "dim_door_width", "view": "plan", "p1": [door["x_min"], 0, 0], "p2": [door["x_max"], 0, 0],
         "offset": [0, -0.25, 0], "status": door["status"]["width"]},
        {"id": "dim_wall_right", "view": "plan", "p1": [door["x_max"], 0, 0], "p2": [sx, 0, 0], "offset": [0, -0.25, 0],
         "status": q_status(xb[2]) if len(xb) > 2 else "derived"},
        {"id": "dim_hatch_x", "view": "plan", "p1": [hatch["x_min"], hatch["y_max"], 0], "p2": [hatch["x_max"], hatch["y_max"], 0],
         "offset": [0, 0.12, 0], "status": hatch["status"]["size_x"]},
        {"id": "dim_hatch_y", "view": "plan", "p1": [hatch["x_max"], hatch["y_min"], 0], "p2": [hatch["x_max"], hatch["y_max"], 0],
         "offset": [0.12, 0, 0], "status": hatch["status"]["size_y"]},
        {"id": "dim_door_to_hatch", "view": "plan", "p1": [hatch["x_min"], 0, 0], "p2": [hatch["x_min"], hatch["y_min"], 0],
         "offset": [-0.12, 0, 0], "status": hatch["texts"]["dim_status"],
         "label_suffix": hatch["texts"]["dim_suffix"]},
        {"id": "dim_room_z", "view": "section_x", "p1": [0, sy, 0], "p2": [0, sy, sz], "offset": [0, 0.35, 0],
         "status": q_status(i["size_z"])},
        {"id": "dim_door_height", "view": "section_x", "p1": [0, 0, 0], "p2": [0, 0, door["z_max"]], "offset": [0, -0.30, 0],
         "status": door["status"]["height"], "label_suffix": door["texts"]["dim_suffix"]},
        {"id": "dim_hatch_y_sec", "view": "section_x", "p1": [0, hatch["y_min"], sz], "p2": [0, hatch["y_max"], sz],
         "offset": [0, 0, 0.62], "status": hatch["status"]["size_y"]},
        {"id": "dim_door_hatch_sec", "view": "section_x", "p1": [0, 0, sz], "p2": [0, hatch["y_min"], sz],
         "offset": [0, 0, 0.62], "status": hatch["texts"]["dim_status"],
         "label_suffix": " ASSUNTO" if hatch["texts"]["dim_suffix"] else ""},
        {"id": "dim_room_z_b", "view": "section_y", "p1": [0, 0, 0], "p2": [0, 0, sz], "offset": [-0.35, 0, 0],
         "status": q_status(i["size_z"])},
        {"id": "dim_room_x_b", "view": "section_y", "p1": [0, 0, 0], "p2": [sx, 0, 0], "offset": [0, 0, -0.30],
         "status": q_status(i["size_x"])},
        {"id": "dim_hatch_x_sec", "view": "section_y", "p1": [hatch["x_min"], 0, sz], "p2": [hatch["x_max"], 0, sz],
         "offset": [0, 0, 0.62], "status": hatch["status"]["size_x"]},
    ]
    for d in dims:
        d["length_m"] = _dist(d["p1"], d["p2"])
        d["label"] = fmt_cm(d["length_m"]) + d.get("label_suffix", "")
    return dims


def fmt_cm(meters):
    """Quota in centimetri con la virgola decimale: 104 cm, 62,5 cm."""
    txt = f"{meters * 100:.1f}".rstrip("0").rstrip(".")
    return txt.replace(".", ",") + " cm"


# --------------------------------------------------------------------------
# Hash semantici


def mesh_semantic_hash(verts, faces, digits=5):
    """Hash della geometria arrotondata (indipendente dal file binario)."""
    vs = [[round(c, digits) + 0.0 for c in v] for v in verts]
    return sha256_text(canonical_json({"v": vs, "f": [list(f) for f in faces]}))


def entity_semantic_hash(ent, mesh_hash):
    meta = {k: ent.get(k) for k in ("id", "entity_id", "role", "layer", "type", "state", "data_status", "placement")}
    return sha256_text(canonical_json({"meta": meta, "mesh": mesh_hash}))


def model_semantic_hash(entity_hashes):
    return sha256_text(canonical_json(sorted(entity_hashes.items())))


def structure_section_boxes(room):
    """Scatole allineate agli assi la cui unione è la struttura.

    Servono per campire le parti tagliate nelle sezioni (stessa geometria
    di structure_parts, porta e botola comprese).
    """
    sx, sy, sz = room_dims(room)
    t = num(room["room"]["wall_thickness"])
    tf = num(room["room"]["floor_thickness"])
    tc = num(room["room"]["ceiling_thickness"])
    door, hatch = derive_openings(room)
    return [
        ([-t, -t, -tf], [sx + t, sy + t, 0.0]),
        ([-t, -t, sz], [sx + t, hatch["y_min"], sz + tc]),
        ([-t, hatch["y_max"], sz], [sx + t, sy + t, sz + tc]),
        ([-t, hatch["y_min"], sz], [hatch["x_min"], hatch["y_max"], sz + tc]),
        ([hatch["x_max"], hatch["y_min"], sz], [sx + t, hatch["y_max"], sz + tc]),
        ([-t, -t, 0.0], [door["x_min"], 0.0, sz]),
        ([door["x_max"], -t, 0.0], [sx + t, 0.0, sz]),
        ([door["x_min"], -t, door["z_max"]], [door["x_max"], 0.0, sz]),
        ([-t, sy, 0.0], [sx + t, sy + t, sz]),
        ([-t, 0.0, 0.0], [0.0, sy, sz]),
        ([sx, 0.0, 0.0], [sx + t, sy, sz]),
    ]


def section_rects(boxes, axis, coord):
    """Rettangoli 2D tagliati dal piano axis=coord (axis 0=X, 1=Y)."""
    other = [i for i in range(3) if i != axis]
    out = []
    for lo, hi in boxes:
        if lo[axis] < coord < hi[axis]:
            out.append(((lo[other[0]], hi[other[0]]), (lo[other[1]], hi[other[1]])))
    return out
