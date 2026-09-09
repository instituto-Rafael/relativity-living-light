import importlib.util
import json
import sys
from pathlib import Path
import unittest
import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SCRIPT = ROOT / "scripts" / "run_nibiguiri_full_method_v2.py"
CONFIG = ROOT / "nibiguiri_full_method_8x12_20260905.v2.yml"
REGISTRY = ROOT / "math_research_program_48_20260905.v1.json"

spec = importlib.util.spec_from_file_location("fullmethod", SCRIPT)
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
assert spec.loader is not None
spec.loader.exec_module(mod)


class FullMethodTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
        cls.registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        cls.lenses = mod.build_96_lenses(cls.config)
        cls.perms = mod.ae_permutations(cls.config)
        cls.ob = mod.build_obligations(cls.config, cls.registry)
        cls.receipt = mod.build_receipt(cls.config, cls.registry, cls.ob)

    def test_eight_families(self): self.assertEqual(len(self.config["macro_families"]), 8)
    def test_twelve_directions(self): self.assertEqual(len(self.config["antagonistic_directions"]), 12)
    def test_96_lenses(self): self.assertEqual(len(self.lenses), 96)
    def test_lens_ids_unique(self): self.assertEqual(len({x["id"] for x in self.lenses}), 96)
    def test_isogonic(self): self.assertEqual(sorted(x["angle_deg"] for x in self.config["antagonistic_directions"]), list(range(0, 360, 30)))

    def test_opposites(self):
        by = {x["id"]: x for x in self.config["antagonistic_directions"]}
        for x in by.values():
            y = by[x["opposite"]]
            self.assertEqual(y["opposite"], x["id"])
            self.assertEqual((y["angle_deg"] - x["angle_deg"]) % 360, 180)

    def test_five_AE(self): self.assertEqual(len(self.config["heuristic_AE"]["operators"]), 5)
    def test_120_permutations(self): self.assertEqual(len(self.perms), 120); self.assertEqual(len(set(self.perms)), 120)
    def test_permutations_include_forward_reverse(self): self.assertIn("ABCDE", self.perms); self.assertIn("EDCBA", self.perms)
    def test_relation_12(self): self.assertEqual(len(self.config["relation_calculus"]["operators"]), 12)
    def test_semantic_34(self): self.assertEqual(len(self.config["semantic_dimensions"]["slots"]), 34)
    def test_no_invented_34D_names(self): self.assertTrue(all(x["canonical_name"].startswith("TOKEN_VAZIO") for x in self.config["semantic_dimensions"]["slots"]))
    def test_48_units(self): self.assertEqual(len(self.registry["research_units"]), 48)
    def test_base_cells(self): self.assertEqual(self.ob["counts"]["base_cells"], 4608)
    def test_AE_cells(self): self.assertEqual(self.ob["counts"]["AE_cells"], 5760)
    def test_relation_cells(self): self.assertEqual(self.ob["counts"]["relation_cells"], 576)
    def test_semantic_cells(self): self.assertEqual(self.ob["counts"]["semantic_cells"], 1632)
    def test_staged_total(self): self.assertEqual(self.ob["counts"]["staged_total"], 12576)
    def test_full_cross(self): self.assertEqual(self.ob["counts"]["full_cross"], 225607680)

    def test_every_staged_cell_starts_token(self):
        for u in self.ob["units"].values():
            for key in ("base_96", "AE_120", "relation_12", "semantic_34"):
                self.assertTrue(all(v == "TOKEN_VAZIO_NOT_AUDITED" for v in u[key].values()))

    def test_random_access_roundtrip_edges(self):
        size = mod.full_cross_size(self.config, self.registry)
        for i in (0, 1, 33, 34, 1439, size // 2, size - 2, size - 1):
            point = mod.decode_full_index(i, self.config, self.registry)
            self.assertEqual(mod.encode_full_index(point, self.config, self.registry), i)

    def test_shard(self):
        rows = list(mod.iter_full_shard(100, 7, self.config, self.registry))
        self.assertEqual([r["index"] for r in rows], list(range(100, 107)))

    def test_method_self_critique(self): self.assertGreaterEqual(len(self.config["method_self_critique"]["questions"]), 12)
    def test_no_auto_promotion(self): self.assertFalse(self.config["auto_promote"])
    def test_validation_pass(self): self.assertEqual(self.receipt["structural_validation"], "PASS"); self.assertTrue(all(self.receipt["checks"].values()))
    def test_obligation_hash(self): self.assertEqual(len(self.ob["sha256"]), 64); int(self.ob["sha256"], 16)


if __name__ == "__main__":
    unittest.main()
