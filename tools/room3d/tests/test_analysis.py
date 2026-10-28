"""Test del collegamento ciclo ↔ layout e del pacchetto di analisi (usa Blender per la build)."""

import copy
import csv
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

    def entry(self, layout_id):
        with open(os.path.join(self.build, "catalog.json")) as f:
            return next(e for e in json.load(f)["layouts"] if e["layout_id"] == layout_id)

    def package(self, out):
        with open(os.path.join(out, "SINTETICO_2026-01-10_0800", "package.json")) as f:
            return json.load(f)

    def cycle_copy(self, mutate, mutate_rows=None):
        d = tempfile.mkdtemp(dir=self.tmp)
        shutil.copy(os.path.join(CYCLE, "letture.csv"), d)
        if mutate_rows:
            with open(os.path.join(d, "letture.csv"), newline="") as f:
                rows = list(csv.DictReader(f))
            fields = list(rows[0])
            mutate_rows(rows)
            with open(os.path.join(d, "letture.csv"), "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=fields)
                w.writeheader()
                w.writerows(rows)
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
        self.assertEqual(c["layout_refs"][0]["build_id"], self.entry("L001")["build_id"],
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
            c["layout_refs"][0]["build_id"] = "0" * 20
            c["layout_refs"][0]["source_commit"] = "abc1234"
        d = self.cycle_copy(mutate)
        code, _ = self.export(d)
        self.assertEqual(code, 2)

    def test_changed_geometry_same_config_rejected(self):
        """Stessa configurazione ma geometria diversa (es. generatore cambiato): non si accetta."""
        e = self.entry("L001")
        fake = "f" * 20
        src = os.path.join(self.build, e["path"])
        dst = os.path.join(os.path.dirname(src), fake)
        shutil.copytree(src, dst)
        self.addCleanup(shutil.rmtree, dst, True)
        man_path = os.path.join(dst, "manifest.json")
        with open(man_path) as f:
            m = json.load(f)
        m["build"]["build_id"], m["build"]["semantic_hash"] = fake, "e" * 64
        with open(man_path, "w") as f:
            json.dump(m, f)
        # il ciclo registra la build originale: la copia con geometria diversa non viene usata
        code, out = self.export(CYCLE)
        self.assertEqual(code, 0)
        self.assertEqual(self.package(out)["layouts"][0]["build_id"], e["build_id"])
        # un ciclo che punta alla cartella ma con il semantic_hash originale viene rifiutato
        def mutate(c):
            c["layout_refs"][0]["build_id"] = fake
        self.assertEqual(self.export(self.cycle_copy(mutate))[0], 2)

    def test_source_commit_mismatch_is_reported(self):
        def mutate(c):
            c["layout_refs"][0]["source_commit"] = "0000000deadbeef"
        code, out = self.export(self.cycle_copy(mutate))
        self.assertEqual(code, 0)
        warns = self.package(out)["layouts"][0]["provenance_warnings"]
        self.assertTrue(any("0000000deadbeef" in w for w in warns), warns)

    def test_zone_without_valid_data_is_not_observed(self):
        def rows(rs):
            for r in rs:
                r["temperatura"] = r["umidita"] = "unavailable"
                r["peso_g"] = "unknown"
        code, out = self.export(self.cycle_copy(lambda c: None, rows))
        self.assertEqual(code, 0)
        lay = self.package(out)["layouts"][0]
        zones = {z["id"]: z for z in lay["product_zones"]}
        self.assertEqual(zones["zone_salami"]["measured_by"], [])
        self.assertIn("nessun dato valido", zones["zone_salami"]["observation"])
        self.assertIn("sensor_b1_sth01", zones["zone_salami"]["sensors_without_valid_data"])
        self.assertIn("sensor_b1_sth01", lay["sensors_without_data"])
        for p in lay["measurement_points"]:
            if p["column"] in ("temperatura", "umidita", "peso_g"):
                self.assertEqual(p["valid_samples"], 0)
                self.assertIn("NESSUN DATO VALIDO", p["data"])

    def test_coverage_is_per_layout_interval(self):
        room, _, lays = core.load_model(os.path.join(MODEL, "room.json"))
        demo = self.entry("L900_DEMO")

        def mutate(c):
            c["layout_refs"][0]["valid_to"] = "2026-01-11T14:00:00"
            c["layout_refs"].append({"layout_id": "L900_DEMO", "config_hash": demo["config_hash"],
                                     "build_id": demo["build_id"], "valid_from": "2026-01-11T14:00:00", "valid_to": None})

        def rows(rs):  # dati della sonda solo prima del cambio di layout
            for r in rs:
                if r["ora"] >= "2026-01-11T14:00:00":
                    r["temperatura"] = r["umidita"] = "unavailable"
        code, out = self.export(self.cycle_copy(mutate, rows))
        self.assertEqual(code, 0)
        l1, l2 = self.package(out)["layouts"]
        z1 = {z["id"]: z for z in l1["product_zones"]}
        z2 = {z["id"]: z for z in l2["product_zones"]}
        self.assertEqual(z1["zone_salami"]["measured_by"], ["sensor_b1_sth01"])
        self.assertNotIn("sensor_b1_sth01", z2.get("zone_salami", {"measured_by": []})["measured_by"])
        self.assertTrue(all(p["valid_samples"] == 0 for p in l2["measurement_points"] if p["column"] == "temperatura"))

    def test_instant_flags_invalid_values(self):
        def rows(rs):
            rs[0]["temperatura"], rs[0]["umidita"], rs[0]["stufa"] = "NaN", "nonsense", "forse"
            rs[1]["temperatura"] = "inf"
        code, out = self.export(self.cycle_copy(lambda c: None, rows), "--at", "2026-01-10T08:00:00")
        self.assertEqual(code, 0)
        p = self.package(out)
        v = p["instant"]["values"]
        for col, raw in (("temperatura", "NaN"), ("umidita", "nonsense"), ("stufa", "forse")):
            self.assertEqual(v[col]["quality"], "non valida", col)
            self.assertIsNone(v[col]["value"], col)
            self.assertEqual(v[col]["raw"], raw)
        self.assertEqual(v["fase"]["quality"], "ok")
        self.assertIsInstance(v["temp_obiettivo"]["value"], float)
        self.assertEqual(p["readings"]["columns"]["temperatura"]["invalid"], 2)

    def test_layout_change_during_cycle(self):
        room, _, lays = core.load_model(os.path.join(MODEL, "room.json"))
        demo = next(l for l in lays if l["layout_id"] == "L900_DEMO")

        def mutate(c):
            c["layout_refs"][0]["valid_to"] = "2026-01-11T14:00:00"
            c["layout_refs"].append({"layout_id": "L900_DEMO", "config_hash": core.config_hash(room, demo),
                                     "build_id": self.entry("L900_DEMO")["build_id"],
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


try:
    import jsonschema
except ImportError:  # lo schema si controlla solo se la libreria c'è; il runtime sempre
    jsonschema = None


class TestCycleContract(unittest.TestCase):
    """Schema JSON e runtime devono accettare e rifiutare gli stessi riferimenti."""

    def setUp(self):
        with open(os.path.join(CYCLE, "cycle.json")) as f:
            self.base = json.load(f)
        with open(os.path.join(MODEL, "cycles", "cycle.schema.json")) as f:
            self.schema = json.load(f)
        self.tmp = tempfile.mkdtemp(prefix="room3d_contract_")
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def check(self, mutate):
        c = copy.deepcopy(self.base)
        mutate(c)
        with open(os.path.join(self.tmp, "cycle.json"), "w") as f:
            json.dump(c, f)
        try:
            ea.load_cycle(self.tmp)
            runtime = None
        except ea.AnalysisError as e:
            runtime = e
        schema_ok = None
        if jsonschema is not None:
            schema_ok = jsonschema.Draft202012Validator(self.schema).is_valid(c)
        return runtime, schema_ok

    def test_example_valid_for_both(self):
        runtime, schema_ok = self.check(lambda c: None)
        self.assertIsNone(runtime)
        self.assertIn(schema_ok, (True, None))

    def test_malformed_refs_rejected_by_both(self):
        def set_ref(k, v):
            def m(c):
                if v is ...:
                    del c["layout_refs"][0][k]
                else:
                    c["layout_refs"][0][k] = v
            return m
        cases = {
            "build_id mancante": set_ref("build_id", ...),
            "build_id intero": set_ref("build_id", 123),
            "build_id vuoto": set_ref("build_id", ""),
            "build_id formato": set_ref("build_id", "../../etc"),
            "semantic_hash malformato": set_ref("semantic_hash", "xyz"),
            "layout_id con percorso": set_ref("layout_id", "../L001"),
            "config_hash corto": set_ref("config_hash", "abc"),
            "source_commit non esadecimale": set_ref("source_commit", "main"),
            "contratto 1.0": lambda c: c.update(schema_version="1.0"),
        }
        for name, mutate in cases.items():
            with self.subTest(name):
                runtime, schema_ok = self.check(mutate)
                self.assertIsInstance(runtime, ea.AnalysisError, name)
                self.assertEqual(runtime.code, 1)
                self.assertIn(schema_ok, (False, None), name)

    def test_legacy_message_explains_migration(self):
        runtime, _ = self.check(lambda c: c.update(schema_version="1.0"))
        self.assertIn("build_id", str(runtime))
        self.assertIn("build storica", str(runtime))


if __name__ == "__main__":
    unittest.main()
