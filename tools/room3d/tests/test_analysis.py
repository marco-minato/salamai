"""Test del collegamento ciclo ↔ layout e del pacchetto di analisi (usa Blender per la build)."""

import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import export_analysis as ea  # noqa: E402
import room3d_core as core  # noqa: E402
from test_build import BLENDER, MODEL, REPO, run_build  # noqa: E402

CYCLE = os.path.join(MODEL, "cycles", "examples", "SINTETICO_2026-01-10_0800")
MAPPING = os.path.join(MODEL, "mapping.json")


@unittest.skipUnless(shutil.which(BLENDER), "Blender non disponibile")
class TestAnalysis(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="room3d_analysis_")
        cls.build = os.path.join(cls.tmp, "build")
        r = run_build(os.path.join(MODEL, "room.json"), cls.build, "--no-render")
        assert r.returncode == 0, r.stderr[-2000:]

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def export(self, cycle_dir, *extra):
        out = os.path.join(self.tmp, "out")
        code = ea.main(["--cycle", cycle_dir, "--build", self.build, "--mapping", MAPPING, "--output", out, *extra])
        return code, out

    def cycle_copy(self, mutate):
        d = tempfile.mkdtemp(dir=self.tmp)
        shutil.copy(os.path.join(CYCLE, "letture.csv"), d)
        with open(os.path.join(CYCLE, "cycle.json")) as f:
            c = json.load(f)
        mutate(c)
        with open(os.path.join(d, "cycle.json"), "w") as f:
            json.dump(c, f)
        return d

    def test_example_hash_matches_current_layout(self):
        with open(os.path.join(CYCLE, "cycle.json")) as f:
            c = json.load(f)
        room, _, lays = core.load_model(os.path.join(MODEL, "room.json"), "L001")
        self.assertEqual(c["layout_refs"][0]["config_hash"], core.config_hash(room, lays[0]),
                         "rigenerare l'esempio con tools/room3d/make_synthetic_cycle.py")

    def test_synthetic_package(self):
        code, out = self.export(CYCLE, "--at", "2026-01-11T12:02:00")
        self.assertEqual(code, 0)
        pdir = os.path.join(out, "SINTETICO_2026-01-10_0800")
        with open(os.path.join(pdir, "package.json")) as f:
            p = json.load(f)
        self.assertTrue(p["synthetic"])
        with open(os.path.join(pdir, "README.md")) as f:
            self.assertTrue(f.read().startswith("> **DATI SINTETICI**"))
        self.assertEqual(p["readings"]["columns"]["temperatura"]["missing"], 12)
        self.assertEqual(len(p["readings"]["gaps"]), 1)
        lay = p["layouts"][0]
        self.assertEqual(lay["layout_id"], "L001")
        zones = {z["id"]: z for z in lay["product_zones"]}
        self.assertEqual(zones["zone_salami"]["measured_by"], ["sensor_b1_sth01"])
        self.assertIn("NON OSSERVATA", zones["zone_cacciatorini"]["observation"])
        self.assertNotIn("heater_e1", {m["component"] for m in lay["measurement_points"]})
        self.assertEqual(p["instant"]["reading_time"], "2026-01-11T12:00:00")
        self.assertEqual(p["inferences"], [])
        self.assertTrue(any("sicurezza alimentare" in x for x in p["limits"]))

    def test_unknown_revision_is_not_replaced_by_current(self):
        def mutate(c):
            c["layout_refs"][0]["config_hash"] = "0" * 64
            c["layout_refs"][0]["source_commit"] = "abc1234"
        d = self.cycle_copy(mutate)
        code, _ = self.export(d)
        self.assertEqual(code, 2)

    def test_layout_change_during_cycle(self):
        room, _, lays = core.load_model(os.path.join(MODEL, "room.json"))
        demo = next(l for l in lays if l["layout_id"] == "L900_DEMO")

        def mutate(c):
            c["layout_refs"][0]["valid_to"] = "2026-01-11T14:00:00"
            c["layout_refs"].append({"layout_id": "L900_DEMO", "config_hash": core.config_hash(room, demo),
                                     "valid_from": "2026-01-11T14:00:00", "valid_to": None})
        d = self.cycle_copy(mutate)
        code, out = self.export(d, "--at", "2026-01-12T09:00:00")
        self.assertEqual(code, 0)
        with open(os.path.join(out, "SINTETICO_2026-01-10_0800", "package.json")) as f:
            p = json.load(f)
        self.assertEqual([l["layout_id"] for l in p["layouts"]], ["L001", "L900_DEMO"])
        self.assertEqual(p["instant"]["layout_id"], "L900_DEMO")

    def test_overlapping_refs_rejected(self):
        def mutate(c):
            c["layout_refs"][0]["valid_to"] = "2026-01-11T14:00:00"
            c["layout_refs"].append(dict(c["layout_refs"][0], valid_from="2026-01-11T10:00:00", valid_to=None))
        code, _ = self.export(self.cycle_copy(mutate))
        self.assertEqual(code, 1)

    def test_readings_outside_layout_validity_rejected(self):
        def mutate(c):
            c["layout_refs"][0]["valid_from"] = "2026-01-11T00:00:00"
        code, _ = self.export(self.cycle_copy(mutate))
        self.assertEqual(code, 1)

    def test_bad_event_type(self):
        def mutate(c):
            c["events"].append({"t": "2026-01-11T10:00:00", "type": "magia"})
        code, _ = self.export(self.cycle_copy(mutate))
        self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
