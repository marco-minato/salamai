"""Test di integrazione: esegue Blender in background (senza GUI né MCP).

    python3 -m unittest discover -s tools/room3d/tests -p 'test_build.py' -v

Variabile BLENDER per scegliere l'eseguibile (default: 'blender' nel PATH).
"""

import copy
import json
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import room3d_core as core  # noqa: E402

REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
MODEL = os.path.join(REPO, "model", "room3d")
BUILD = os.path.join(REPO, "tools", "room3d", "build_scene.py")
BLENDER = os.environ.get("BLENDER", "blender")


def run_build(config, out, *extra):
    cmd = [BLENDER, "--background", "--factory-startup", "--python-exit-code", "1", "--python", BUILD, "--",
           "--config", config, "--output", out, *extra]
    return subprocess.run(cmd, capture_output=True, text=True, timeout=600)


def read_glb(path):
    """Ritorna (json, bin) di un file GLB."""
    with open(path, "rb") as f:
        data = f.read()
    magic, version, length = struct.unpack_from("<III", data, 0)
    assert magic == 0x46546C67 and version == 2 and length == len(data)
    off, js, binary = 12, None, None
    while off < len(data):
        clen, ctype = struct.unpack_from("<II", data, off)
        chunk = data[off + 8: off + 8 + clen]
        if ctype == 0x4E4F534A:
            js = json.loads(chunk)
        elif ctype == 0x004E4942:
            binary = chunk
        off += 8 + clen
    return js, binary


def node_position_bounds(gltf, node):
    mesh = gltf["meshes"][node["mesh"]]
    lo, hi = [1e9] * 3, [-1e9] * 3
    for prim in mesh["primitives"]:
        acc = gltf["accessors"][prim["attributes"]["POSITION"]]
        lo = [min(a, b) for a, b in zip(lo, acc["min"])]
        hi = [max(a, b) for a, b in zip(hi, acc["max"])]
    t = node.get("translation", [0, 0, 0])
    return [a + b for a, b in zip(lo, t)], [a + b for a, b in zip(hi, t)]


def copy_model(tmp):
    dst = os.path.join(tmp, "model")
    shutil.copytree(MODEL, dst)
    return os.path.join(dst, "room.json")


@unittest.skipUnless(shutil.which(BLENDER), "Blender non disponibile")
class TestBuild(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="room3d_test_")
        cls.out1 = os.path.join(cls.tmp, "build1")
        cls.out2 = os.path.join(cls.tmp, "build2")
        cls.r1 = run_build(os.path.join(MODEL, "room.json"), cls.out1)
        cls.r2 = run_build(os.path.join(MODEL, "room.json"), cls.out2, "--no-render")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def catalog(self, out):
        with open(os.path.join(out, "catalog.json")) as f:
            return json.load(f)

    def manifest(self, out, layout_id="L001"):
        cat = self.catalog(out)
        e = next(x for x in cat["layouts"] if x["layout_id"] == layout_id)
        with open(os.path.join(out, e["manifest"])) as f:
            return json.load(f), e

    def test_build_succeeds(self):
        self.assertEqual(self.r1.returncode, 0, self.r1.stderr[-2000:])
        self.assertEqual(self.r2.returncode, 0, self.r2.stderr[-2000:])

    def test_outputs_exist(self):
        for e in self.catalog(self.out1)["layouts"]:
            d = os.path.join(self.out1, e["path"])
            for fn in ("model.blend", "model.glb", "manifest.json"):
                self.assertTrue(os.path.getsize(os.path.join(d, fn)) > 0, fn)
            self.assertEqual(set(e["images"]), {"plan", "section_x", "section_y", "axon"})
            for rel in e["images"].values():
                self.assertTrue(os.path.getsize(os.path.join(self.out1, rel)) > 10000, rel)

    def test_reproducible_semantics(self):
        c1, c2 = self.catalog(self.out1), self.catalog(self.out2)
        for a, b in zip(c1["layouts"], c2["layouts"]):
            self.assertEqual(a["layout_id"], b["layout_id"])
            self.assertEqual(a["config_hash"], b["config_hash"])
            self.assertEqual(a["semantic_hash"], b["semantic_hash"])
            self.assertEqual(a["build_id"], b["build_id"])
            self.assertEqual(a["path"], b["path"])
        m1, _ = self.manifest(self.out1)
        m2, _ = self.manifest(self.out2)
        h1 = {e["id"]: e["semantic_hash"] for e in m1["entities"]}
        h2 = {e["id"]: e["semantic_hash"] for e in m2["entities"]}
        self.assertEqual(h1, h2)

    def test_manifest_matches_glb(self):
        for e in self.catalog(self.out1)["layouts"]:
            d = os.path.join(self.out1, e["path"])
            with open(os.path.join(d, "manifest.json")) as f:
                m = json.load(f)
            glb = os.path.join(d, "model.glb")
            self.assertEqual(core.sha256_file(glb), m["gltf"]["sha256"])
            self.assertEqual(e["glb_sha256"], m["gltf"]["sha256"])
            self.assertEqual(core.sha256_file(os.path.join(d, "manifest.json")), e["manifest_sha256"])
            gltf, _ = read_glb(glb)
            scene = gltf["scenes"][gltf.get("scene", 0)]
            self.assertEqual(scene["extras"]["salamai_build_id"], m["build"]["build_id"])
            nodes = {n["name"]: n for n in gltf["nodes"]}
            ids = {x["id"] for x in m["entities"]}
            self.assertEqual(set(nodes), ids, "nodi glTF e ID del manifest devono coincidere")
            for name, n in nodes.items():
                self.assertEqual(n["extras"]["salamai_id"], name)
                self.assertNotRegex(name, r"\.\d{3}$")

    def test_gltf_orientation_and_scale(self):
        m, e = self.manifest(self.out1)
        gltf, _ = read_glb(os.path.join(self.out1, e["glb"]))
        nodes = {n["name"]: n for n in gltf["nodes"]}
        ents = {x["id"]: x for x in m["entities"]}
        conv = m["gltf"]["gltf_to_canonical"]
        for oid in ("wall_y1", "ceiling", "fan_01", "exhaust_duct_01", "door_01_leaf", "extractor_m4"):
            lo, hi = node_position_bounds(gltf, nodes[oid])
            corners = [[x, y, z] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])]
            can = [[sum(conv[r][c] * p[c] for c in range(3)) for r in range(3)] for p in corners]
            clo = [min(p[i] for p in can) for i in range(3)]
            chi = [max(p[i] for p in can) for i in range(3)]
            for i in range(3):
                self.assertAlmostEqual(clo[i], ents[oid]["bbox_min"][i], delta=1e-4, msg=f"{oid} min[{i}]")
                self.assertAlmostEqual(chi[i], ents[oid]["bbox_max"][i], delta=1e-4, msg=f"{oid} max[{i}]")
        # in glTF il soffitto sta in alto lungo +Y, a 2,10 m (metri, non centimetri)
        lo, hi = node_position_bounds(gltf, nodes["ceiling"])
        self.assertAlmostEqual(lo[1], 2.10, delta=1e-4)
        # la parete di fondo (Y canonico 1,60) va su -Z in glTF
        lo, hi = node_position_bounds(gltf, nodes["wall_y1"])
        self.assertAlmostEqual(hi[2], -1.60, delta=1e-4)

    def test_manifest_openings_and_assumptions(self):
        m, _ = self.manifest(self.out1)
        h = m["openings"]["hatch"]
        d = m["openings"]["door"]
        self.assertAlmostEqual(h["x_min"], 1.205, delta=1e-9)
        self.assertAlmostEqual(h["y_min"], 0.40, delta=1e-9)
        self.assertAlmostEqual(h["y_max"], 0.85, delta=1e-9)
        self.assertEqual(h["status"]["offset_reference"], "assumed")
        self.assertAlmostEqual(d["x_min"], 1.04, delta=1e-9)
        self.assertAlmostEqual(d["x_max"], 1.69, delta=1e-9)
        self.assertEqual(d["status"]["height"], "unknown")
        self.assertAlmostEqual(m["room"]["volume_gross_m3"], 10.1808, delta=1e-9)
        self.assertTrue(any(a["id"] == "a01_hatch_offset_reference" for a in m["assumptions"]))
        paths = {u["path"] for u in m["unknowns"]}
        self.assertIn("room.openings.door.height", paths)
        fans = [x for x in m["entities"] if x["type"] == "recirculation_fan" and x["role"] == "body"]
        self.assertEqual(len(fans), 3)
        arrows = [x for x in m["entities"] if x["role"] == "nominal_flow_arrow"]
        self.assertEqual(len(arrows), 3)
        for a in arrows:
            self.assertIn("non simulata", a["name"])

    def test_blend_reopens_and_openings_are_free(self):
        _, e = self.manifest(self.out1)
        blend = os.path.join(self.out1, e["path"], "model.blend")
        script = r"""
import bpy, json
from mathutils import Vector
sc = bpy.context.scene
dg = bpy.context.evaluated_depsgraph_get()
def hit(o, d):
    r = sc.ray_cast(dg, Vector(o), Vector(d))
    return r[4].name if r[0] else None
res = {
  "objects": len([o for o in bpy.data.objects if "salamai_id" in o]),
  "door_ray": hit((1.365, 0.5, 1.0), (0, -1, 0)),
  "wall_ray": hit((0.10, 0.10, 0.30), (0, -1, 0)),
  "hatch_ray": hit((1.23, 0.43, 1.0), (0, 0, 1)),
  "ceiling_ray": hit((1.80, 0.10, 1.95), (0, 0, 1)),
  "build_id": sc.get("salamai_build_id"),
  "collections": sorted(c.name for c in sc.collection.children),
}
print("RESULT" + json.dumps(res))
"""
        r = subprocess.run([BLENDER, "--background", blend, "--python-expr", script],
                           capture_output=True, text=True, timeout=300)
        line = next(l for l in r.stdout.splitlines() if l.startswith("RESULT"))
        res = json.loads(line[6:])
        self.assertIsNone(res["door_ray"], "la luce della porta deve essere libera")
        self.assertEqual(res["wall_ray"], "wall_y0")
        self.assertIsNone(res["hatch_ray"], "la botola deve essere un foro reale")
        self.assertEqual(res["ceiling_ray"], "ceiling")
        self.assertEqual(len(res["collections"]), len(core.LAYERS))
        m, _ = self.manifest(self.out1)
        self.assertEqual(res["objects"], len(m["entities"]))
        self.assertEqual(res["build_id"], m["build"]["build_id"])

    def test_parameter_change_moves_without_duplicates(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg = copy_model(tmp)
            with open(cfg) as f:
                room = json.load(f)
            room["openings"]["hatch"]["offset_reference"]["value"] = "center"
            with open(cfg, "w") as f:
                json.dump(room, f)
            lpath = os.path.join(os.path.dirname(cfg), "layouts", "L001_progetto.json")
            with open(lpath) as f:
                lay = json.load(f)
            # i componenti nella botola seguono la botola
            for c in lay["components"]:
                if c["id"] in ("extractor_m4", "check_valve_y1"):
                    c["geometry"]["center"]["y"]["value"] = 0.40
                if c["id"] == "exhaust_duct_01":
                    for p in c["geometry"]["points"][:2]:
                        p["value"][1] = 0.40
            with open(lpath, "w") as f:
                json.dump(lay, f)
            out = os.path.join(tmp, "out")
            r = run_build(cfg, out, "--no-render", "--layout", "L001")
            self.assertEqual(r.returncode, 0, r.stderr[-2000:])
            with open(os.path.join(out, "catalog.json")) as f:
                e = json.load(f)["layouts"][0]
            with open(os.path.join(out, e["manifest"])) as f:
                m2 = json.load(f)
        m1, e1 = self.manifest(self.out1)
        self.assertNotEqual(e["config_hash"], e1["config_hash"])
        self.assertNotEqual(e["path"], e1["path"])
        self.assertAlmostEqual(m2["openings"]["hatch"]["y_min"], 0.175, delta=1e-9)
        self.assertEqual([x["id"] for x in m1["entities"]], [x["id"] for x in m2["entities"]])
        ceil1 = next(x for x in m1["entities"] if x["id"] == "ceiling")
        ceil2 = next(x for x in m2["entities"] if x["id"] == "ceiling")
        self.assertNotEqual(ceil1["semantic_hash"], ceil2["semantic_hash"])
        wall1 = next(x for x in m1["entities"] if x["id"] == "wall_x0")
        wall2 = next(x for x in m2["entities"] if x["id"] == "wall_x0")
        self.assertEqual(wall1["semantic_hash"], wall2["semantic_hash"])

    def test_invalid_config_fails_with_exit_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg = copy_model(tmp)
            with open(cfg) as f:
                room = json.load(f)
            room["openings"]["door"]["x_min"]["value"] = 2.9
            with open(cfg, "w") as f:
                json.dump(room, f)
            out = os.path.join(tmp, "out")
            r = run_build(cfg, out, "--no-render")
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("porta fuori dalla parete", r.stderr)
            self.assertFalse(os.path.exists(os.path.join(out, "catalog.json")))

    def test_missing_config_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = run_build(os.path.join(tmp, "nope.json"), os.path.join(tmp, "out"), "--no-render")
            self.assertNotEqual(r.returncode, 0)


if __name__ == "__main__":
    unittest.main()
