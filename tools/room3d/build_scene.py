"""Genera la scena Blender del modello 3D Salamai dalla configurazione JSON.

Si esegue con il Python incluso in Blender, senza GUI e senza MCP:

    blender --background --factory-startup --python-exit-code 1 \
        --python tools/room3d/build_scene.py -- \
        --config model/room3d/room.json --output build/room3d

Opzioni dopo "--":
    --layout ID        costruisce solo questo layout (default: tutto il catalogo)
    --engine NOME      workbench (default) oppure cycles (solo CPU)
    --no-render        salta le immagini PNG
    --resolution N     larghezza delle immagini in pixel (default 2400)

Per ogni layout scrive in <output>/layouts/<layout_id>/<hash12>/:
model.blend, model.glb, manifest.json e views/*.png; poi <output>/catalog.json.
Errori di configurazione o di build: messaggio chiaro ed exit code 1.
"""

import argparse
import datetime
import math
import os
import subprocess
import sys

import bpy
import mathutils

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import room3d_core as core  # noqa: E402

GENERATOR_VERSION = "1.0.0"
MANIFEST_VERSION = "1.0"

LAYER_COLORS = {
    "struttura": (0.78, 0.78, 0.76, 1.0),
    "aperture": (0.55, 0.38, 0.22, 1.0),
    "estrazione_ingresso": (0.20, 0.45, 0.85, 1.0),
    "ricircolo": (0.10, 0.62, 0.55, 1.0),
    "riscaldamento_umidificazione": (0.88, 0.35, 0.18, 1.0),
    "supporti_prodotto": (0.85, 0.65, 0.20, 0.28),
    "sensori": (0.62, 0.22, 0.70, 1.0),
    "quote_annotazioni": (0.10, 0.10, 0.10, 1.0),
    "analisi_temporale": (0.30, 0.30, 0.30, 1.0),
}
ARROW_COLOR = (0.95, 0.15, 0.15, 1.0)
INK = (0.08, 0.08, 0.08, 1.0)
INK_ASSUMED = (0.85, 0.35, 0.0, 1.0)
CUT_FILL = (0.25, 0.25, 0.25, 1.0)
PAPER = (1.0, 1.0, 1.0, 1.0)

VIEW_TITLES = {
    "plan": "Pianta quotata (vista dall'alto, soffitto nascosto)",
    "section_x": "Sezione A-A sul piano X = {cut} m (porta e botola), vista verso -X",
    "section_y": "Sezione B-B sul piano Y = {cut} m (centro botola), vista verso +Y",
    "axon": "Assonometria aperta (soffitto, parete sinistra e parete di fondo nascosti)",
}


class BuildError(Exception):
    pass


# --------------------------------------------------------------------------
# Argomenti e utilità


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser(prog="build_scene.py")
    ap.add_argument("--config", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--layout", default=None)
    ap.add_argument("--engine", choices=("workbench", "cycles"), default="workbench")
    ap.add_argument("--no-render", action="store_true")
    ap.add_argument("--resolution", type=int, default=2400)
    return ap.parse_args(argv)


def git_info(path):
    def run(*cmd):
        try:
            return subprocess.run(cmd, cwd=path, capture_output=True, text=True, timeout=10).stdout.strip()
        except (OSError, subprocess.SubprocessError):
            return ""
    root = run("git", "rev-parse", "--show-toplevel")
    if not root:
        return {"commit": None, "dirty": None}
    commit = run("git", "rev-parse", "HEAD") or None
    dirty = bool(run("git", "status", "--porcelain", "--", "model/room3d", "tools/room3d"))
    return {"commit": commit, "dirty": dirty}


def r6(v):
    return [round(c, 6) + 0.0 for c in v]


# --------------------------------------------------------------------------
# Scena


def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.unit_settings.system = "METRIC"
    sc.unit_settings.scale_length = 1.0
    sc.unit_settings.length_unit = "CENTIMETERS"
    return sc


def make_collections(sc):
    cols = {}
    for i, (lid, label) in enumerate(core.LAYERS):
        col = bpy.data.collections.new(f"{i + 1:02d}_{lid}")
        col["salamai_layer"] = lid
        col["salamai_label"] = label
        sc.collection.children.link(col)
        cols[lid] = col
    return cols


_materials = {}


def material(name, rgba):
    key = (name, tuple(round(c, 4) for c in rgba))
    if key in _materials:
        return _materials[key]
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = rgba
    if getattr(mat, "node_tree", None) is None:
        mat.use_nodes = True
    bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (rgba[0], rgba[1], rgba[2], 1.0)
    bsdf.inputs["Alpha"].default_value = rgba[3]
    bsdf.inputs["Roughness"].default_value = 0.8
    if rgba[3] < 1.0:
        mat.surface_render_method = "BLENDED"
        mat.use_backface_culling = False
    _materials[key] = mat
    return mat


def flat_material(name, rgba):
    """Materiale per testi e quote: colore piatto anche in Cycles."""
    key = ("flat_" + name, tuple(rgba))
    if key in _materials:
        return _materials[key]
    mat = bpy.data.materials.new("ann_" + name)
    mat.diffuse_color = rgba
    if getattr(mat, "node_tree", None) is None:
        mat.use_nodes = True
    nt = mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = rgba
    em.inputs["Strength"].default_value = 1.0
    nt.links.new(em.outputs[0], out.inputs[0])
    _materials[key] = mat
    return mat


def mesh_object(name, verts, faces, col, mat):
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], [tuple(f) for f in faces])
    if me.validate(verbose=False):
        raise BuildError(f"mesh '{name}' non valida (corretta da Blender): controllare la geometria")
    me.update()
    me.materials.append(mat)
    ob = bpy.data.objects.new(name, me)
    col.objects.link(ob)
    if ob.name != name:
        raise BuildError(f"nome oggetto duplicato: '{name}' diventato '{ob.name}'")
    return ob


def entity_color(ent):
    if ent.get("role") == "nominal_flow_arrow":
        return ARROW_COLOR
    rgba = LAYER_COLORS[ent["layer"]]
    if ent["id"] == "floor":
        rgba = (0.52, 0.53, 0.55, 1.0)
    if ent["state"] == "placeholder" and rgba[3] == 1.0:
        rgba = (rgba[0], rgba[1], rgba[2], 0.45)
    return rgba


def build_model_objects(entities, cols):
    objs = {}
    for ent in entities:
        verts, faces = ent["mesh"]
        rgba = entity_color(ent)
        mat = material(f"{ent['layer']}_{ent['state']}_{ent['role']}" + ("_floor" if ent["id"] == "floor" else ""), rgba)
        ob = mesh_object(ent["id"], verts, faces, cols[ent["layer"]], mat)
        for k in ("entity_id", "role", "layer", "type", "state", "data_status", "placement"):
            ob["salamai_" + k] = ent[k] or ""
        ob["salamai_id"] = ent["id"]
        ob["salamai_name"] = ent["name"]
        objs[ent["id"]] = ob
    return objs


def read_back_hashes(objs, entities):
    """Hash semantici calcolati dalle mesh effettivamente presenti in Blender."""
    out = {}
    for ent in entities:
        ob = objs[ent["id"]]
        mw = ob.matrix_world
        verts = [list(mw @ v.co) for v in ob.data.vertices]
        faces = [list(p.vertices) for p in ob.data.polygons]
        mh = core.mesh_semantic_hash(verts, faces)
        out[ent["id"]] = core.entity_semantic_hash(ent, mh)
    return out


# --------------------------------------------------------------------------
# Annotazioni


class Annotator:
    """Crea testi, quote e richiami per una vista, in una sottocollezione."""

    def __init__(self, parent_col, view, rot, toward_cam, size):
        self.col = bpy.data.collections.new(f"ann_{view}")
        parent_col.children.link(self.col)
        self.view = view
        self.rot = rot
        self.toward = toward_cam  # spostamento verso la camera (non cambia la proiezione)
        self.size = size
        self.n = 0

    def _name(self, kind):
        self.n += 1
        return f"ann_{self.view}_{kind}_{self.n:03d}"

    def bar(self, p1, p2, w, rgba):
        d = mathutils.Vector(p2) - mathutils.Vector(p1)
        if d.length < 1e-9:
            return None
        verts, faces = core.mesh_cylinder(list(p1), list(d.normalized()), w / 2, d.length, segs=6)
        return mesh_object(self._name("line"), verts, faces, self.col, flat_material("ink%d" % int(rgba[0] * 100), rgba))

    def text(self, body, loc, rgba=INK, size=None, align="CENTER", plate=None):
        cu = bpy.data.curves.new(self._name("txt"), "FONT")
        cu.body = body
        cu.size = size or self.size
        cu.align_x = align
        cu.align_y = "CENTER"
        ob = bpy.data.objects.new(cu.name, cu)
        ob.location = loc
        ob.rotation_euler = self.rot
        ob.data.materials.append(flat_material("ink%d" % int(rgba[0] * 100), rgba))
        self.col.objects.link(ob)
        if plate is None:
            plate = self.view != "axon"  # in assonometria i fondi risultano ombreggiati
        if plate:
            bpy.context.view_layer.update()
            w, h = ob.dimensions.x, ob.dimensions.y
            pad = (size or self.size) * 0.25
            off = {"CENTER": 0.0, "LEFT": w / 2, "RIGHT": -w / 2}[align]
            rot = self.rot.to_matrix()
            right, up, nrm = rot.col[0], rot.col[1], rot.col[2]
            c = mathutils.Vector(loc) + right * off - nrm * 0.0004
            hw, hh = w / 2 + pad, h / 2 + pad * 0.6
            verts = [list(c - right * hw - up * hh), list(c + right * hw - up * hh),
                     list(c + right * hw + up * hh), list(c - right * hw + up * hh)]
            mesh_object(self._name("plate"), verts, [(0, 1, 2, 3)], self.col, flat_material("paper", PAPER))
        return ob

    def dimension(self, p1, p2, offset, label, rgba):
        p1, p2, o = mathutils.Vector(p1), mathutils.Vector(p2), mathutils.Vector(offset)
        w = self.size * 0.08
        a, b = p1 + o, p2 + o
        on = o.normalized() if o.length > 1e-9 else mathutils.Vector((0, 0, 0))
        self.bar(p1 + on * 0.03, a + on * 0.05, w * 0.6, rgba)
        self.bar(p2 + on * 0.03, b + on * 0.05, w * 0.6, rgba)
        self.bar(a, b, w, rgba)
        d = (b - a).normalized()
        for p in (a, b):
            tick = (d + on).normalized() * self.size * 0.35
            self.bar(p - tick, p + tick, w * 1.6, rgba)
        mid = (a + b) / 2 + on * self.size * 0.9
        self.text(label, mid, rgba)


def project(v, cam_rot):
    m = cam_rot.to_matrix()
    v = mathutils.Vector(v)
    return v.dot(m.col[0]), v.dot(m.col[1]), v.dot(m.col[2])


def place_callouts(ann, items, cam_rot, bounds_uv, depth_point):
    """Etichette su due colonne ai lati della stanza, con linee di richiamo.

    items: lista di (testo, punto 3D, colore). Le etichette non si
    sovrappongono e restano fuori dal disegno della stanza.
    """
    m = cam_rot.to_matrix()
    right, up, nrm = m.col[0], m.col[1], m.col[2]
    umin, umax, vmin, vmax = bounds_uv
    ucen = (umin + umax) / 2
    gap = ann.size * 2.0
    sides = {"L": [], "R": []}
    for text, p, rgba in items:
        u, v, _ = project(p, cam_rot)
        sides["R" if u >= ucen else "L"].append((v, u, text, p, rgba))
    dp = mathutils.Vector(depth_point)
    used = [vmin, vmax]
    for side, lst in sides.items():
        lst.sort(key=lambda t: -t[0])
        n = len(lst)
        if not n:
            continue
        ucol = umax + 0.75 if side == "R" else umin - 0.75
        # posizioni verticali: ordine conservato, spaziatura minima "gap"
        vs = []
        for v, *_rest in lst:
            vs.append(v if not vs or vs[-1] - v >= gap else vs[-1] - gap)
        # se la colonna esce sotto la stanza, la si alza mantenendo la spaziatura
        overflow = (vmin - gap) - vs[-1]
        if overflow > 0:
            vs = [x + overflow for x in vs]
        used = [min(used[0], vs[-1] - gap), max(used[1], vs[0] + gap)]
        for (v, u, text, p, rgba), vv in zip(lst, vs):
            # punto nel piano delle annotazioni: componente lungo nrm presa da depth_point
            base = right * ucol + up * vv + nrm * dp.dot(nrm)
            anchor = mathutils.Vector(p)
            anchor = anchor - nrm * anchor.dot(nrm) + nrm * dp.dot(nrm)
            elbow = right * (ucol - (0.06 if side == "R" else -0.06)) + up * vv + nrm * dp.dot(nrm)
            ann.bar(anchor, elbow, ann.size * 0.05, rgba)
            ann.bar(elbow, base, ann.size * 0.05, rgba)
            dot = core.mesh_uv_sphere(list(anchor), ann.size * 0.18, segs=8, rings=4)
            mesh_object(ann._name("dot"), dot[0], dot[1], ann.col, flat_material("dot%d" % int(rgba[0] * 100), rgba))
            ann.text(text, base + right * (0.03 if side == "R" else -0.03),
                     rgba, align="LEFT" if side == "R" else "RIGHT")
    return used


def component_label(ent):
    c = ent.get("component") or {}
    tag = c.get("tag") or ent["id"]
    name = c.get("name") or ent.get("name")
    flag = ""
    if ent["state"] == "placeholder":
        flag = " [P]"
    elif ent["data_status"] in ("assumed", "unknown"):
        flag = " [A]"
    return f"{tag} — {name}{flag}", (INK_ASSUMED if flag else INK)


# --------------------------------------------------------------------------
# Viste


def setup_render(sc, engine, res_x, res_y):
    sc.render.resolution_x = res_x
    sc.render.resolution_y = res_y
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = False
    sc.view_settings.view_transform = "Standard"
    sc.render.image_settings.file_format = "PNG"
    world = bpy.data.worlds.new("paper")
    world.color = PAPER[:3]
    sc.world = world
    if engine == "cycles":
        sc.render.engine = "CYCLES"
        sc.cycles.device = "CPU"
        sc.cycles.samples = 32
        world.use_nodes = True if getattr(world, "node_tree", None) is None else world.use_nodes
        bg = next(n for n in world.node_tree.nodes if n.type == "BACKGROUND")
        bg.inputs["Color"].default_value = PAPER
        bg.inputs["Strength"].default_value = 1.0
    else:
        sc.render.engine = "BLENDER_WORKBENCH"
        sh = sc.display.shading
        sh.light = "STUDIO"
        sh.color_type = "MATERIAL"
        sh.show_object_outline = True
        sh.object_outline_color = (0.15, 0.15, 0.15)
        sh.show_cavity = False
        sh.show_shadows = False
        sc.display.render_aa = "16"


def view_camera(view, room, door, hatch):
    sx, sy, sz = core.room_dims(room)
    if view == "plan":
        rot = mathutils.Euler((0.0, 0.0, 0.0))
        return rot, None
    if view == "section_x":
        return mathutils.Euler((math.pi / 2, 0.0, math.pi / 2)), ("x", door["center_x"])
    if view == "section_y":
        return mathutils.Euler((math.pi / 2, 0.0, 0.0)), ("y", hatch["center_y"])
    d = mathutils.Vector((-0.62, 0.78, 0.72)).normalized()
    rot = (-d).to_track_quat("-Z", "Y").to_euler()
    return rot, None


def render_view(sc, view, ctx, out_png):
    room, layout, entities, objs, ann_parent, dims, res = (
        ctx["room"], ctx["layout"], ctx["entities"], ctx["objs"], ctx["ann_parent"], ctx["dims"], ctx["res"])
    sx, sy, sz = core.room_dims(room)
    t = core.num(room["room"]["wall_thickness"])
    door, hatch = core.derive_openings(room)
    rot, cut = view_camera(view, room, door, hatch)
    m = rot.to_matrix()
    right, up, nrm = m.col[0], m.col[1], m.col[2]

    hidden = {"plan": {"ceiling"}, "section_x": set(), "section_y": set(),
              "axon": {"ceiling", "wall_x0", "wall_y1"}}[view]
    for oid, ob in objs.items():
        ob.hide_render = oid in hidden

    # punti della stanza per inquadrare
    corners = [mathutils.Vector((x, y, z)) for x in (-t, sx + t) for y in (-t, sy + t) for z in (-t, sz + t)]
    if cut:
        ax = 0 if cut[0] == "x" else 1
        corners = [c for c in corners]
    us = [c.dot(right) for c in corners]
    vs = [c.dot(up) for c in corners]
    bounds = (min(us), max(us), min(vs), max(vs))
    size = 0.055 if view != "axon" else 0.05

    ann = Annotator(ann_parent, view, rot, nrm, size)
    room_center = mathutils.Vector((sx / 2, sy / 2, sz / 2))
    if cut:
        axis, coord = cut
        ai = 0 if axis == "x" else 1
        # camera fuori dalla stanza; il piano di taglio coincide con clip_start
        cam_dist = 8.0
        sign = 1.0 if axis == "x" else -1.0
        cam_loc = room_center.copy()
        cam_loc[ai] = coord + sign * cam_dist
        clip_start = cam_dist
        depth_point = room_center.copy()
        depth_point[ai] = coord - sign * 0.0006
        fill_point = coord - sign * 0.0012
        # campitura delle parti tagliate della struttura
        for (a0, a1), (b0, b1) in core.section_rects(core.structure_section_boxes(room), ai, coord):
            if axis == "x":
                verts = [[fill_point, a0, b0], [fill_point, a1, b0], [fill_point, a1, b1], [fill_point, a0, b1]]
            else:
                verts = [[a0, fill_point, b0], [a1, fill_point, b0], [a1, fill_point, b1], [a0, fill_point, b1]]
            mesh_object(ann._name("cut"), verts, [(0, 1, 2, 3)], ann.col, flat_material("cut", CUT_FILL))
    else:
        cam_loc = room_center + nrm * 12.0
        clip_start = 0.1
        depth_point = room_center + nrm * 3.0

    def on_plane(p):
        p = mathutils.Vector(p)
        return p - nrm * p.dot(nrm) + nrm * depth_point.dot(nrm)

    # quote
    for d in dims:
        if d["view"] != view and not (view == "axon" and False):
            continue
        rgba = INK if d["status"] in ("measured", "declared", "derived") else INK_ASSUMED
        ann.dimension(on_plane(d["p1"]), on_plane(d["p2"]), d["offset"], d["label"], rgba)

    # richiami dei componenti visibili
    items = []
    seen = set()
    for ent in entities:
        if ent["role"] != "body" or ent["layer"] == "struttura" or ent["id"] in hidden:
            continue
        lo, hi = core.bbox_of(ent["mesh"][0])
        center = [(a + b) / 2 for a, b in zip(lo, hi)]
        if cut:
            ai = 0 if cut[0] == "x" else 1
            visible = lo[ai] < cut[1] if cut[0] == "x" else hi[ai] > cut[1]
            if not visible:
                continue
            center[ai] = min(max(center[ai], lo[ai]), hi[ai])
        if ent["entity_id"] in seen:
            continue
        seen.add(ent["entity_id"])
        label, rgba = component_label(ent)
        items.append((label, center, rgba))
    v_lo, v_hi = place_callouts(ann, items, rot, bounds, depth_point)

    # assi
    origin = mathutils.Vector((-t - 0.35, -t - 0.35, 0.0)) if view in ("plan", "axon") else (
        mathutils.Vector((cut[1], -t - 0.35, -t - 0.15)) if cut[0] == "x" else mathutils.Vector((-t - 0.35, cut[1], -t - 0.15)))
    origin = on_plane(origin)
    for vec, name, col in (((1, 0, 0), "X", (0.85, 0.1, 0.1, 1)), ((0, 1, 0), "Y", (0.1, 0.6, 0.1, 1)),
                           ((0, 0, 1), "Z", (0.1, 0.25, 0.9, 1))):
        v = mathutils.Vector(vec)
        if abs(v.dot(nrm)) > 0.99:
            continue
        verts, faces = core._arrow(list(origin), list(v), 0.25, 0.006)
        mesh_object(ann._name("axis"), verts, faces, ann.col, flat_material("axis" + name, col))
        ann.text(name, origin + v * 0.32, col, plate=False)

    # cartiglio
    # cornice: stanza + quote (0,6 m) + colonne di richiami, cartiglio sopra
    us = [c.dot(right) for c in corners]
    title_h = size * 9.5
    top = max(v_hi, max(vs) + 0.7) + 0.1
    bottom = min(v_lo, min(vs) - 0.7)
    width = (max(us) - min(us)) + 2 * 2.75
    height = (top + title_h) - bottom
    aspect = min(max(width / height, 1.2), 2.4)
    sc.render.resolution_y = int(res[0] / aspect)
    scale = max(width, height * aspect)
    cu, cv = (max(us) + min(us)) / 2, (top + title_h + bottom) / 2
    tl = right * (cu - scale / 2 + 0.12) + up * (top + title_h - size * 1.2) + nrm * depth_point.dot(nrm)
    cut_txt = f"{cut[1]:.3f}".replace(".", ",") if cut else ""
    lines = [
        ("SALAMAI · " + VIEW_TITLES[view].format(cut=cut_txt), INK, size * 1.5),
        (f"Layout {layout['layout_id']} rev {layout['revision']} — {layout['kind']} — {layout['title']}",
         INK_ASSUMED if layout["kind"] == "hypothetical_demo" else INK, size),
        (f"config {ctx['config_hash'][:12]} · build {ctx['build_id']}", INK, size * 0.8),
        ("Quote in cm. Arancio / [A] = dato assunto o sconosciuto, disegnato con valore provvisorio (da rilevare). "
         "[P] = segnaposto.", INK_ASSUMED, size * 0.85),
        ("Frecce rosse = direzione NOMINALE delle ventole, non simulata. "
         "Botola: 40 cm dalla parete porta al bordo vicino = ASSUNZIONE NON CONFERMATA.", INK_ASSUMED, size * 0.85),
    ]
    off = 0.0
    for text, rgba, s in lines:
        ann.text(text, tl - up * off, rgba, size=s, align="LEFT", plate=False)
        off += s * 1.9

    cam_data = bpy.data.cameras.new(f"cam_{view}")
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = scale
    cam_data.clip_start = clip_start
    cam_data.clip_end = 60.0
    cam = bpy.data.objects.new(f"cam_{view}", cam_data)
    cam.rotation_euler = rot
    cam.location = right * cu + up * cv + nrm * cam_loc.dot(nrm)
    ann.col.objects.link(cam)
    sc.camera = cam

    # solo le annotazioni di questa vista
    if sc.render.engine == "BLENDER_WORKBENCH":
        # viste tecniche a colori piatti; l'assonometria resta ombreggiata
        sc.display.shading.light = "STUDIO" if view == "axon" else "FLAT"
    for col in ann_parent.children:
        col.hide_render = col is not ann.col
    sc.render.filepath = out_png
    bpy.ops.render.render(write_still=True)
    for ob in objs.values():
        ob.hide_render = False
    if not os.path.isfile(out_png):
        raise BuildError(f"render non scritto: {out_png}")


# --------------------------------------------------------------------------
# Manifest


def collect_unknowns(obj, path, out):
    if core.is_q(obj):
        if core.q_status(obj) == "unknown":
            out.append({"path": path, "draw_value": obj.get("draw_value"), "note": obj.get("note"),
                        "assumption": obj.get("assumption")})
        return
    if isinstance(obj, dict):
        for k, v in obj.items():
            if not k.startswith("_"):
                collect_unknowns(v, f"{path}.{k}" if path else k, out)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            collect_unknowns(v, f"{path}[{i}]", out)


def entity_record(ent, sem_hash):
    verts = ent["mesh"][0]
    lo, hi = core.bbox_of(verts)
    rec = {
        "id": ent["id"],
        "entity_id": ent["entity_id"],
        "role": ent["role"],
        "name": ent["name"],
        "type": ent["type"],
        "layer": ent["layer"],
        "state": ent["state"],
        "data_status": ent["data_status"],
        "placement": ent["placement"],
        "placement_reason": ent.get("placement_reason"),
        "gltf_node": ent["id"],
        "bbox_min": r6(lo),
        "bbox_max": r6(hi),
        "bbox_center": r6([(a + b) / 2 for a, b in zip(lo, hi)]),
        "bbox_size": r6([b - a for a, b in zip(lo, hi)]),
        "notes": ent.get("notes", []),
        "semantic_hash": sem_hash,
    }
    c = ent.get("component")
    if c:
        g = c["geometry"]
        rec["tag"] = c.get("tag")
        rec["geometry_kind"] = g["kind"]
        rec["status_detail"] = ent.get("status_detail", {})
        rec["properties"] = c.get("properties", {})
        if "center" in g:
            rec["center"] = r6(core.vec3(g["center"])[0])
        if "size" in g:
            rec["size"] = r6(core.vec3(g["size"])[0])
        if "axis" in g:
            ax = core._norm(core.vec3(g["axis"])[0])
            rec["orientation"] = {"axis": r6(ax), "meaning": "verso nominale dell'aria" if g["kind"] == "fan" else "asse"}
        if "yaw_deg" in g:
            rec["orientation"] = {"yaw_deg": core.num(g["yaw_deg"])}
        if g["kind"] == "fan":
            rec["fan"] = {"frame_size": core.num(g["frame_size"]), "depth": core.num(g["depth"]),
                          "rotor_diameter": core.num(g["rotor_diameter"]),
                          "flow_direction": "nominale, NON simulata"}
        if g["kind"] == "pipe":
            pp = core.pipe_path(g)
            rec["pipe"] = {
                "points": [r6(core.vec3(p)[0]) for p in g["points"]],
                "outer_diameter": core.num(g["outer_diameter"]),
                "inner_diameter": core.num(g["inner_diameter"]) if g.get("inner_diameter") else None,
                "bend_radius": core.num(g["bend_radius"]) if g.get("bend_radius") else None,
                "length_m": round(pp["length"], 4),
                "length_note": "lunghezza dell'asse rappresentato (tratti + archi), non una misura in opera",
                "straights": [{"id": f"{ent['entity_id']}.{s['id']}", "start": r6(s["start"]), "end": r6(s["end"]),
                               "length_m": round(s["length"], 4)} for s in pp["straights"]],
                "bends": [{"id": f"{ent['entity_id']}.{b['id']}", "at_point": b["at_point"],
                           "angle_deg": round(b["angle_deg"], 3), "radius_m": b["radius"],
                           "length_m": round(b["length"], 4)} for b in pp["bends"]],
                "loss_coefficients": None,
            }
    return rec


# --------------------------------------------------------------------------
# Build di un layout


def build_layout(room, layout, args, out_root, git):
    global _materials
    _materials = {}
    cfg_hash = core.config_hash(room, layout)
    sc = reset_scene()
    cols = make_collections(sc)
    entities = core.build_entities(room, layout)
    objs = build_model_objects(entities, cols)
    bpy.context.view_layer.update()
    ent_hashes = read_back_hashes(objs, entities)
    sem_hash = core.model_semantic_hash(ent_hashes)
    build_id = core.sha256_text(cfg_hash + sem_hash)[:20]
    sc["salamai_build_id"] = build_id
    sc["salamai_layout_id"] = layout["layout_id"]
    sc["salamai_config_hash"] = cfg_hash

    rel_dir = f"layouts/{layout['layout_id']}/{cfg_hash[:12]}"
    out_dir = os.path.join(out_root, rel_dir)
    os.makedirs(os.path.join(out_dir, "views"), exist_ok=True)

    # GLB: solo oggetti del modello (niente annotazioni, camere, testi)
    bpy.ops.object.select_all(action="DESELECT")
    for ob in objs.values():
        ob.select_set(True)
    glb = os.path.join(out_dir, "model.glb")
    bpy.ops.export_scene.gltf(filepath=glb, export_format="GLB", use_selection=True, export_extras=True,
                              export_yup=True, export_apply=False, export_materials="EXPORT",
                              export_cameras=False, export_lights=False)
    if not os.path.isfile(glb):
        raise BuildError("esportazione GLB fallita")

    dims = core.dimension_lines(room, layout)
    images = {}
    if not args.no_render:
        res = (args.resolution, int(args.resolution * 0.62))
        setup_render(sc, args.engine, *res)
        ann_parent = cols["quote_annotazioni"]
        ctx = {"room": room, "layout": layout, "entities": entities, "objs": objs, "ann_parent": ann_parent,
               "dims": dims, "res": res, "config_hash": cfg_hash, "build_id": build_id}
        for view, fname in (("plan", "pianta.png"), ("section_x", "sezione_A_x.png"),
                            ("section_y", "sezione_B_y.png"), ("axon", "assonometria_aperta.png")):
            png = os.path.join(out_dir, "views", fname)
            render_view(sc, view, ctx, png)
            images[view] = f"views/{fname}"
        for col in ann_parent.children:
            col.hide_render = False
            col.hide_viewport = col.name != "ann_plan"

    door, hatch = core.derive_openings(room)
    sx, sy, sz = core.room_dims(room)
    unknowns = []
    collect_unknowns({k: v for k, v in room.items() if k not in ("sources", "assumptions")}, "room", unknowns)
    collect_unknowns(layout.get("components", []), f"layout[{layout['layout_id']}].components", unknowns)
    layer_counts = {}
    for e in entities:
        layer_counts[e["layer"]] = layer_counts.get(e["layer"], 0) + 1
    manifest = {
        "manifest_version": MANIFEST_VERSION,
        "model_id": room["model_id"],
        "layout": {k: layout.get(k) for k in ("layout_id", "revision", "kind", "title", "status", "description",
                                              "valid_from", "valid_to", "derived_from")},
        "layout_source_file": layout["_file"],
        "build": {
            "build_id": build_id,
            "config_hash": cfg_hash,
            "semantic_hash": sem_hash,
            "source_commit": git["commit"],
            "source_dirty": git["dirty"],
            "blender_version": bpy.app.version_string,
            "generator": "tools/room3d/build_scene.py",
            "generator_version": GENERATOR_VERSION,
            "built_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
            "engine": None if args.no_render else args.engine,
        },
        "units": room["units"],
        "frame": room["frame"],
        "gltf": {
            "file": "model.glb",
            "sha256": core.sha256_file(glb),
            "up_axis": "+Y",
            "canonical_to_gltf": core.CANONICAL_TO_GLTF,
            "gltf_to_canonical": core.GLTF_TO_CANONICAL,
            "note": "glTF è Y-up: (x, y, z) canonico -> (x, z, -y) glTF. Usare gltf_to_canonical per coordinate, quote, misure e selezione.",
            "scene_extras_build_id": build_id,
        },
        "layers": [{"id": lid, "label": label, "collection": f"{i + 1:02d}_{lid}", "count": layer_counts.get(lid, 0),
                    "in_gltf": lid != "quote_annotazioni",
                    "note": ("popolato dal pacchetto di analisi per istante (export_analysis.py); vuoto nella geometria"
                             if lid == "analisi_temporale" else None)}
                   for i, (lid, label) in enumerate(core.LAYERS)],
        "room": {
            "interior_size": [sx, sy, sz],
            "interior_status": {k: core.q_status(room["room"]["interior"][k]) for k in ("size_x", "size_y", "size_z")},
            "volume_gross_m3": round(sx * sy * sz, 6),
            "volume_note": "volume geometrico interno lordo: non è il volume libero con prodotti e attrezzature",
            "wall_thickness_drawn": core.num(room["room"]["wall_thickness"]),
            "wall_thickness_status": core.q_status(room["room"]["wall_thickness"]),
        },
        "openings": {"door": {k: v for k, v in door.items()}, "hatch": hatch},
        "entities": [entity_record(e, ent_hashes[e["id"]]) for e in entities],
        "dimensions": [{k: d[k] for k in ("id", "view", "p1", "p2", "offset", "length_m", "label", "status")}
                       for d in dims],
        "assumptions": room.get("assumptions", []) + layout.get("assumptions", []),
        "unknowns": unknowns,
        "sources": room.get("sources", []),
        "images": images,
    }
    import json
    with open(os.path.join(out_dir, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
        f.write("\n")

    blend = os.path.join(out_dir, "model.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend, compress=True)
    print(f"[room3d] {layout['layout_id']}: {len(entities)} oggetti, semantic {sem_hash[:12]}, -> {rel_dir}")
    return {
        "layout_id": layout["layout_id"],
        "kind": layout["kind"],
        "title": layout["title"],
        "revision": layout["revision"],
        "status": layout.get("status"),
        "valid_from": layout.get("valid_from"),
        "valid_to": layout.get("valid_to"),
        "config_hash": cfg_hash,
        "semantic_hash": sem_hash,
        "build_id": build_id,
        "path": rel_dir,
        "manifest": f"{rel_dir}/manifest.json",
        "manifest_sha256": core.sha256_file(os.path.join(out_dir, "manifest.json")),
        "glb": f"{rel_dir}/model.glb",
        "glb_sha256": manifest["gltf"]["sha256"],
        "images": {k: f"{rel_dir}/{v}" for k, v in images.items()},
    }


def main():
    import json
    args = parse_args()
    try:
        room, catalog, layouts = core.load_model(args.config, args.layout)
        core.validate(room, layouts, catalog)
    except core.ConfigError as e:
        print(f"[room3d] CONFIGURAZIONE NON VALIDA ({len(e.errors)} errori):", file=sys.stderr)
        for m in e.errors:
            print(f"  - {m}", file=sys.stderr)
        sys.exit(1)
    except (OSError, ValueError, KeyError) as e:
        print(f"[room3d] ERRORE di lettura configurazione: {e}", file=sys.stderr)
        sys.exit(1)
    out_root = os.path.abspath(args.output)
    os.makedirs(out_root, exist_ok=True)
    git = git_info(os.path.dirname(os.path.abspath(args.config)))
    built = []
    try:
        for lay in layouts:
            built.append(build_layout(room, lay, args, out_root, git))
    except BuildError as e:
        print(f"[room3d] BUILD FALLITA: {e}", file=sys.stderr)
        sys.exit(1)
    # catalogo della build: unisce le voci già costruite (es. build di un solo layout)
    cat_path = os.path.join(out_root, "catalog.json")
    entries = {}
    if args.layout and os.path.isfile(cat_path):
        with open(cat_path, encoding="utf-8") as f:
            entries = {e["layout_id"]: e for e in json.load(f).get("layouts", [])}
    for b in built:
        entries[b["layout_id"]] = b
    order = [e["layout_id"] for e in catalog["layouts"]]
    out_cat = {
        "catalog_version": "1.0",
        "model_id": room["model_id"],
        "default_layout": catalog.get("default_layout"),
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "source_commit": git["commit"],
        "source_dirty": git["dirty"],
        "note": "Percorsi immutabili per revisione: layouts/<layout_id>/<config_hash[:12]>/. "
                "'hypothetical_demo' è un esempio, mai uno storico reale.",
        "layouts": [entries[i] for i in order if i in entries],
    }
    with open(cat_path, "w", encoding="utf-8") as f:
        json.dump(out_cat, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"[room3d] catalogo: {cat_path}")


if __name__ == "__main__":
    main()
