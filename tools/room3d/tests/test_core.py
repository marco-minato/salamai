"""Test del nucleo (Python di sistema, senza Blender).

    python3 -m unittest discover -s tools/room3d/tests -v
"""

import copy
import math
import re
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import room3d_core as core  # noqa: E402

REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CONFIG = os.path.join(REPO, "model", "room3d", "room.json")
TOL = 1e-9


def load():
    room, catalog, layouts = core.load_model(CONFIG)
    return room, catalog, layouts


def errors_of(room, layouts, catalog=None):
    try:
        core.validate(room, layouts, catalog)
    except core.ConfigError as e:
        return e.errors
    return []


def comp(layout, cid):
    return next(c for c in layout["components"] if c["id"] == cid)


class TestValidConfig(unittest.TestCase):
    def setUp(self):
        self.room, self.catalog, self.layouts = load()

    def test_valid(self):
        self.assertEqual(errors_of(self.room, self.layouts, self.catalog), [])

    def test_room_dimensions_and_volume(self):
        sx, sy, sz = core.room_dims(self.room)
        self.assertAlmostEqual(sx, 3.03, delta=TOL)
        self.assertAlmostEqual(sy, 1.60, delta=TOL)
        self.assertAlmostEqual(sz, 2.10, delta=TOL)
        self.assertAlmostEqual(sx * sy * sz, 10.1808, delta=1e-9)
        parts = [core.num(q) for q in self.room["room"]["interior"]["x_breakdown"]]
        self.assertAlmostEqual(sum(parts), sx, delta=TOL)

    def test_door(self):
        door, _ = core.derive_openings(self.room)
        self.assertAlmostEqual(door["x_min"], 1.04, delta=TOL)
        self.assertAlmostEqual(door["x_max"], 1.69, delta=TOL)
        self.assertAlmostEqual(door["center_x"], 1.365, delta=TOL)
        # altezza sconosciuta: il valore disegnato non diventa un dato
        self.assertEqual(door["status"]["height"], "unknown")
        self.assertIsNone(self.room["openings"]["door"]["height"]["value"])

    def test_hatch_near_edge_assumption(self):
        _, h = core.derive_openings(self.room)
        self.assertAlmostEqual(h["x_min"], 1.205, delta=TOL)
        self.assertAlmostEqual(h["x_max"], 1.525, delta=TOL)
        self.assertAlmostEqual(h["y_min"], 0.40, delta=TOL)
        self.assertAlmostEqual(h["y_max"], 0.85, delta=TOL)
        self.assertAlmostEqual(h["center_y"], 0.625, delta=TOL)
        self.assertAlmostEqual(h["z"], 2.10, delta=TOL)
        self.assertEqual(h["offset_reference"], "near_edge")
        self.assertEqual(h["status"]["offset_reference"], "assumed")
        self.assertEqual(h["status"]["y_min"], "assumed")

    def test_hatch_center_reference_changes_position(self):
        room = copy.deepcopy(self.room)
        room["openings"]["hatch"]["offset_reference"]["value"] = "center"
        _, h = core.derive_openings(room)
        self.assertAlmostEqual(h["y_min"], 0.175, delta=TOL)
        self.assertAlmostEqual(h["center_y"], 0.40, delta=TOL)

    def test_opening_texts_follow_data(self):
        door, h = core.derive_openings(self.room)
        self.assertIn("40 cm dalla parete porta al bordo vicino", h["texts"]["summary"])
        self.assertIn("ASSUNZIONE NON CONFERMATA", h["texts"]["summary"])
        self.assertIn("sconosciuta", door["texts"]["summary"])
        room = copy.deepcopy(self.room)
        room["openings"]["hatch"]["offset_reference"].update(value="center", status="measured", source="src_sketch")
        room["openings"]["door"]["height"] = {"value": 2.0, "status": "measured", "source": "src_sketch"}
        door, h = core.derive_openings(room)
        self.assertIn("al centro", h["texts"]["summary"])
        self.assertNotIn("ASSUNZIONE", h["texts"]["summary"])
        self.assertEqual(h["texts"]["dim_suffix"], "")
        self.assertEqual(door["texts"]["summary"], "Altezza porta 2,00 m (misurato).")
        dims = {d["id"]: d for d in core.dimension_lines(room, self.layouts[0])}
        self.assertEqual(dims["dim_door_height"]["label"], "200 cm")

    def test_hatch_is_hole_in_ceiling(self):
        boxes = core.structure_section_boxes(self.room)
        _, h = core.derive_openings(self.room)
        # nessuna scatola della struttura contiene il centro della botola a quota soffitto
        p = [h["center_x"], h["center_y"], h["z"] + 0.05]
        inside = [b for b in boxes if all(b[0][i] < p[i] < b[1][i] for i in range(3))]
        self.assertEqual(inside, [])

    def test_door_is_hole_in_wall(self):
        boxes = core.structure_section_boxes(self.room)
        door, _ = core.derive_openings(self.room)
        for z in (0.05, 1.0, door["z_max"] - 0.01):
            p = [door["center_x"], -0.05, z]
            inside = [b for b in boxes if all(b[0][i] < p[i] < b[1][i] for i in range(3))]
            self.assertEqual(inside, [], f"luce porta occupata a z={z}")

    def test_three_fans_separate_from_extractor(self):
        lay = self.layouts[0]
        fans = [c for c in lay["components"] if c["type"] == "recirculation_fan"]
        self.assertEqual(sorted(c["id"] for c in fans), ["fan_01", "fan_02", "fan_03"])
        self.assertEqual(comp(lay, "extractor_m4")["type"], "extractor_fan")
        for f in fans:
            ax = core.vec3(f["geometry"]["axis"])[0]
            self.assertAlmostEqual(math.sqrt(sum(a * a for a in ax)), 1.0, delta=1e-9)

    def test_pipe_length_from_geometry(self):
        lay = self.layouts[0]
        g = comp(lay, "exhaust_duct_01")["geometry"]
        pp = core.pipe_path(g)
        pts = [core.vec3(p)[0] for p in g["points"]]
        R = core.num(g["bend_radius"])
        poly = sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))
        # ogni curva sostituisce 2·R·tan(θ/2) di spigolo con un arco R·θ
        expect = poly
        for b in pp["bends"]:
            th = math.radians(b["angle_deg"])
            expect += R * th - 2 * R * math.tan(th / 2)
        self.assertAlmostEqual(pp["length"], expect, delta=1e-9)
        self.assertEqual(len(pp["straights"]), len(pts) - 1)
        self.assertEqual(len(pp["bends"]), len(pts) - 2)

    FLOW_CLAIM = re.compile(r"aspira di più|\battravers|\bripartizion|\bportat[ae]\b")
    # una nota sul flusso è accettabile se è un'ipotesi, una direzione nominale
    # o se dichiara che il dato non è noto (non misurato, sconosciuto, ...)
    FLOW_QUALIFIERS = ("ipotesi", "nominale", "non simulat", "non sono misure", "non una portata",
                       "non misurat", "non calcolat", "sconosciut", "non verificat", "da verificare")

    @classmethod
    def flow_claim_unqualified(cls, note):
        low = note.lower()
        return bool(cls.FLOW_CLAIM.search(low)) and not any(k in low for k in cls.FLOW_QUALIFIERS)

    def test_flow_claim_detector(self):
        for bad in ("Con rami di lunghezza diversa aspira di più il ramo corto.",
                    "Con l'ingresso in basso l'aria attraversa la camera dal basso verso l'alto.",
                    "Portata 120 m³/h per ramo."):
            self.assertTrue(self.flow_claim_unqualified(bad), bad)
        for ok in ("Portata non misurata: dato sconosciuto.",
                   "IPOTESI da verificare: la portata potrebbe non dividersi in parti uguali.",
                   "La lunghezza riportata nel manifest deriva dal percorso disegnato.",
                   "Flusso nominale: dalla camera verso la cantina, non simulato."):
            self.assertFalse(self.flow_claim_unqualified(ok), ok)

    def test_flow_claims_in_notes_are_marked_as_hypotheses(self):
        """Le note non presentano come accertati effetti sul flusso d'aria (portate, percorsi, ripartizioni)."""
        for lay in self.layouts:
            for c in lay["components"]:
                for n in c.get("notes", []):
                    self.assertFalse(self.flow_claim_unqualified(n),
                                     f"{lay['layout_id']}/{c['id']}: affermazione sul flusso non marcata come ipotesi: {n}")

    def test_exhaust_tee_two_branches_high_in_back_corners(self):
        """Decisione utente 28/10/2026: Ø100 → T sulla parete di fondo → due Ø80 negli angoli lontani, bocche in alto."""
        lay = self.layouts[0]
        sx, sy, sz = core.room_dims(self.room)
        main = [core.vec3(p)[0] for p in comp(lay, "exhaust_duct_01")["geometry"]["points"]]
        tee = core.vec3(comp(lay, "duct_tee_01")["geometry"]["center"])[0]
        self.assertEqual(main[-1], tee, "il tubo principale termina nel T")
        self.assertGreater(tee[1], sy / 2, "il T è verso la parete di fondo, lontano dalla porta")
        ends = []
        for cid in ("exhaust_duct_02", "exhaust_duct_03"):
            g = comp(lay, cid)["geometry"]
            pts = [core.vec3(p)[0] for p in g["points"]]
            self.assertEqual(pts[0], tee, f"{cid} parte dal T")
            self.assertAlmostEqual(core.num(g["inner_diameter"]), 0.08, delta=TOL)
            ends.append(pts[-1])
        self.assertEqual(sorted(e[0] < sx / 2 for e in ends), [False, True], "un ramo per angolo")
        for e in ends:
            self.assertGreater(e[1], sy - 0.2, "bocca vicino alla parete di fondo")
            self.assertGreater(e[2], sz * 0.75, "bocca in alto")
            self.assertLess(min(e[0], sx - e[0]), 0.2, "bocca vicino a una parete laterale")

    def test_unknown_not_zero(self):
        # nessuna grandezza 'unknown' ha valore 0 al posto di null
        found = []

        def walk(o):
            if core.is_q(o):
                if o.get("status") == "unknown":
                    found.append(o)
                    self.assertIsNone(o.get("value"))
                return
            if isinstance(o, dict):
                for v in o.values():
                    walk(v)
            elif isinstance(o, list):
                for v in o:
                    walk(v)
        walk(self.room)
        walk(self.layouts)
        self.assertGreater(len(found), 10)

    def test_demo_layout_is_marked(self):
        demo = [l for l in self.layouts if l["layout_id"] == "L900_DEMO"][0]
        self.assertEqual(demo["kind"], "hypothetical_demo")
        self.assertIn("DIMOSTRATIVA", demo["title"])
        real = [l for l in self.layouts if l["kind"].startswith("real")]
        self.assertEqual([l["layout_id"] for l in real], ["L001"])

    def test_config_hash_stable_and_sensitive(self):
        lay = self.layouts[0]
        h1 = core.config_hash(self.room, lay)
        self.assertEqual(h1, core.config_hash(copy.deepcopy(self.room), copy.deepcopy(lay)))
        lay2 = copy.deepcopy(lay)
        comp(lay2, "fan_01")["geometry"]["center"]["z"]["draw_value"] = 1.80
        self.assertNotEqual(h1, core.config_hash(self.room, lay2))

    def test_mesh_hash_deterministic(self):
        lay = self.layouts[0]
        e1 = core.build_entities(self.room, lay)
        e2 = core.build_entities(copy.deepcopy(self.room), copy.deepcopy(lay))
        h1 = [core.mesh_semantic_hash(*e["mesh"]) for e in e1]
        h2 = [core.mesh_semantic_hash(*e["mesh"]) for e in e2]
        self.assertEqual(h1, h2)
        ids = [e["id"] for e in e1]
        self.assertEqual(len(ids), len(set(ids)))


class TestInvalidConfig(unittest.TestCase):
    """Ogni dato invalido deve produrre un errore chiaro, con il percorso."""

    def setUp(self):
        self.room, self.catalog, self.layouts = load()
        self.lay = copy.deepcopy(self.layouts[0])

    def assertError(self, room, layouts, needle):
        errs = errors_of(room, layouts)
        self.assertTrue(any(needle in e for e in errs), f"atteso '{needle}' in {errs}")

    def test_negative_dimension(self):
        room = copy.deepcopy(self.room)
        room["room"]["interior"]["size_y"]["value"] = -1.6
        self.assertError(room, [self.lay], "deve essere positivo")

    def test_negative_component_size(self):
        comp(self.lay, "junction_box_x4")["geometry"]["size"]["value"] = [0.07, -0.15, 0.11]
        self.assertError(self.room, [self.lay], "positive")

    def test_duplicate_id(self):
        comp(self.lay, "fan_02")["id"] = "fan_01"
        self.assertError(self.room, [self.lay], "ID duplicato 'fan_01'")

    def test_duplicate_id_with_structure(self):
        comp(self.lay, "fan_02")["id"] = "door_01"
        self.assertError(self.room, [self.lay], "ID duplicato 'door_01'")

    def test_null_axis(self):
        comp(self.lay, "fan_01")["geometry"]["axis"]["value"] = [0, 0, 0]
        self.assertError(self.room, [self.lay], "asse nullo")

    def test_non_unit_axis(self):
        comp(self.lay, "fan_01")["geometry"]["axis"]["value"] = [-2, 0, 0]
        self.assertError(self.room, [self.lay], "non normalizzato")

    def test_door_outside_room(self):
        room = copy.deepcopy(self.room)
        room["openings"]["door"]["x_min"]["value"] = 2.80
        self.assertError(room, [self.lay], "porta fuori dalla parete")

    def test_hatch_outside_room(self):
        room = copy.deepcopy(self.room)
        room["openings"]["hatch"]["offset_from_door_wall"]["value"] = 1.40
        self.assertError(room, [self.lay], "botola fuori dal soffitto")

    def test_non_finite(self):
        for bad in (float("nan"), float("inf")):
            lay = copy.deepcopy(self.lay)
            comp(lay, "fan_01")["geometry"]["frame_size"]["value"] = bad
            self.assertError(self.room, [lay], "non finito")

    def test_non_finite_from_json_text(self):
        import json
        bad = json.loads('{"value": NaN, "status": "declared", "source": "src_sketch"}')
        room = copy.deepcopy(self.room)
        room["room"]["interior"]["size_z"] = bad
        self.assertError(room, [self.lay], "non finito")

    def test_unknown_with_value(self):
        room = copy.deepcopy(self.room)
        room["openings"]["door"]["height"]["value"] = 1.9
        self.assertError(room, [self.lay], "stato 'unknown' con value non nullo")

    def test_unknown_without_draw_value(self):
        room = copy.deepcopy(self.room)
        del room["openings"]["door"]["height"]["draw_value"]
        self.assertError(room, [self.lay], "senza draw_value")

    def test_declared_without_source(self):
        room = copy.deepcopy(self.room)
        del room["room"]["interior"]["size_x"]["source"]
        self.assertError(room, [self.lay], "senza source valida")

    def test_component_outside_room(self):
        comp(self.lay, "sensor_b1_sth01")["geometry"]["center"]["x"]["value"] = 3.5
        self.assertError(self.room, [self.lay], "elemento fuori dalla stanza")

    def test_external_requires_reason(self):
        c = comp(self.lay, "sensor_b5_cantina")
        del c["placement_reason"]
        self.assertError(self.room, [self.lay], "senza motivazione")

    def test_external_allowed_with_reason(self):
        self.assertEqual(errors_of(self.room, [self.lay]), [])
        self.assertEqual(comp(self.lay, "sensor_b5_cantina")["placement"], "external")

    def test_through_opening_must_stay_in_footprint(self):
        comp(self.lay, "extractor_m4")["geometry"]["center"]["x"]["value"] = 1.0
        self.assertError(self.room, [self.lay], "non contenuto nell'impronta della botola")

    def test_unknown_layer(self):
        comp(self.lay, "fan_01")["layer"] = "ventole"
        self.assertError(self.room, [self.lay], "layer 'ventole' non esistente")

    def test_pipe_coincident_points(self):
        pts = comp(self.lay, "exhaust_duct_01")["geometry"]["points"]
        pts.insert(1, copy.deepcopy(pts[0]))
        self.assertError(self.room, [self.lay], "punto coincidente")

    def test_pipe_inner_not_smaller(self):
        g = comp(self.lay, "exhaust_duct_01")["geometry"]
        g["outer_diameter"] = {"value": 0.09, "status": "assumed", "note": "test"}
        self.assertError(self.room, [self.lay], "diametro interno non minore")

    def test_bad_status(self):
        comp(self.lay, "fan_01")["geometry"]["depth"]["status"] = "forse"
        self.assertError(self.room, [self.lay], "stato 'forse' non valido")

    def test_property_without_provenance(self):
        comp(self.lay, "fan_01")["properties"]["model"] = "ARCTIC"
        self.assertError(self.room, [self.lay], "proprietà senza")

    def test_catalog_kind_mismatch(self):
        cat = copy.deepcopy(self.catalog)
        cat["layouts"][1]["kind"] = "real_plan"
        errs = errors_of(self.room, self.layouts, cat)
        self.assertTrue(any("kind del catalogo" in e for e in errs), errs)

    def test_cli_exit_code(self):
        import json
        import subprocess
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            room = copy.deepcopy(self.room)
            room.pop("_base_dir", None)
            room["room"]["interior"]["size_x"]["value"] = -3
            os.makedirs(os.path.join(tmp, "layouts"))
            with open(os.path.join(tmp, "room.json"), "w") as f:
                json.dump(room, f)
            src = os.path.join(REPO, "model", "room3d", "layouts")
            for fn in os.listdir(src):
                with open(os.path.join(src, fn)) as a, open(os.path.join(tmp, "layouts", fn), "w") as b:
                    b.write(a.read())
            r = subprocess.run([sys.executable, os.path.join(REPO, "tools", "room3d", "validate_config.py"),
                                "--config", os.path.join(tmp, "room.json")], capture_output=True, text=True)
            self.assertEqual(r.returncode, 1)
            self.assertIn("size_x", r.stderr)


if __name__ == "__main__":
    unittest.main()
