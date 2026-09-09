import importlib.util
import json
import sys
from pathlib import Path
import unittest
import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SCRIPT = ROOT / "scripts" / "run_nibiguiri_self_critique.py"
CONFIG = ROOT / "nibiguiri_self_critique_engine_20260905.v1.yml"
REGISTRY = ROOT / "math_research_program_48_20260905.v1.json"

spec = importlib.util.spec_from_file_location("nibiguiri_self_critique", SCRIPT)
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
assert spec.loader is not None
spec.loader.exec_module(mod)


class NibiguiriSelfCritiqueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
        cls.registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        cls.matrix, cls.candidates, cls.receipt = mod.build_report(cls.config, cls.registry)

    def test_config_has_12_lenses(self):
        self.assertEqual(len(self.config["lenses"]), 12)

    def test_angles_are_isogonic(self):
        self.assertEqual([x["angle_deg"] for x in self.config["lenses"]], list(range(0, 360, 30)))

    def test_opposites_are_180_and_involutive(self):
        by_id = {x["id"]: x for x in self.config["lenses"]}
        for lens in self.config["lenses"]:
            opp = by_id[lens["opposite"]]
            self.assertEqual((opp["angle_deg"] - lens["angle_deg"]) % 360, 180)
            self.assertEqual(opp["opposite"], lens["id"])

    def test_six_antagonistic_pairs(self):
        self.assertEqual(len(self.candidates["pair_tensions"]), 6)

    def test_research_registry_is_48(self):
        self.assertEqual(len(self.registry["research_units"]), 48)

    def test_matrix_is_48_by_12(self):
        self.assertEqual(self.matrix["cells_count"], 576)

    def test_matrix_starts_token_vazio(self):
        self.assertTrue(all(c["state"] == "TOKEN_VAZIO_NOT_AUDITED" for c in self.matrix["cells"]))

    def test_exactly_12_seed_candidates(self):
        self.assertEqual(self.candidates["count"], 12)

    def test_candidate_type_counts(self):
        self.assertEqual(
            self.candidates["counts_by_type"],
            {"HYPOTHESIS_CANDIDATE": 8, "LEMMA_CANDIDATE": 2, "THESIS_PROGRAM_CANDIDATE": 2},
        )

    def test_no_auto_promotion(self):
        self.assertFalse(self.config["auto_promote_candidates"])
        self.assertTrue(all(not c["promotion_allowed"] for c in self.candidates["candidates"]))

    def test_every_candidate_has_falsifier(self):
        self.assertTrue(all(c["falsifier"] for c in self.candidates["candidates"]))

    def test_every_candidate_has_opposite_lens(self):
        self.assertTrue(all(c["opposite_lens"] for c in self.candidates["candidates"]))

    def test_candidate_hashes_unique(self):
        hashes = [c["sha256"] for c in self.candidates["candidates"]]
        self.assertEqual(len(hashes), len(set(hashes)))

    def test_candidate_merkle_root_format(self):
        root = self.candidates["candidate_merkle_root"]
        self.assertEqual(len(root), 64)
        int(root, 16)

    def test_method_audits_itself(self):
        self.assertTrue(self.config["self_critique_of_method"]["audit_method_as_subject"])
        self.assertGreaterEqual(len(self.config["self_critique_of_method"]["questions"]), 8)

    def test_structural_receipt_passes(self):
        self.assertEqual(self.receipt["structural_validation"], "PASS")
        self.assertTrue(all(self.receipt["structural_checks"].values()))

    def test_hash_is_not_proof_gate(self):
        self.assertTrue(self.config["global_rules"]["hash_is_provenance_not_proof"])

    def test_token_vazio_is_not_zero_gate(self):
        self.assertFalse(self.config["global_rules"]["token_vazio_is_zero"])


if __name__ == "__main__":
    unittest.main()
