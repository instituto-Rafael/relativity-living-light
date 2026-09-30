import copy
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts/validate_desi_50_hypothesis_intake.py"
spec = importlib.util.spec_from_file_location("desi_intake_validator", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class Desi50HypothesisIntakeTests(unittest.TestCase):
    def setUp(self):
        self.rows = mod.load_rows()
        import json
        self.meta = json.loads(mod.META.read_text(encoding="utf-8"))

    def test_canonical_intake_passes(self):
        self.assertEqual([], mod.validate(self.rows, self.meta))

    def test_exactly_50_unique_ids(self):
        self.assertEqual(50, len(self.rows))
        self.assertEqual(mod.EXPECTED_IDS, {r["id"] for r in self.rows})

    def test_no_evidence_gate_promoted(self):
        self.assertTrue(all(r["E"] == "TOKEN_VAZIO" for r in self.rows))
        self.assertFalse(self.meta["claim_allowed"])
        self.assertFalse(self.meta["promotion_allowed"])

    def test_direct_desi_has_observable_gate(self):
        direct = [r for r in self.rows if r["desi_relevance"] == "DIRECT_DESI"]
        self.assertEqual(17, len(direct))
        self.assertTrue(all(r["O"] == "PASS" for r in direct))

    def test_known_formula_defects_are_preserved(self):
        by_id = {r["id"]: r for r in self.rows}
        self.assertEqual("FAIL", by_id["H15"]["P"])
        self.assertEqual("FAIL", by_id["H35"]["P"])
        self.assertEqual("FAIL", by_id["H44"]["D"])
        self.assertEqual("R", by_id["H50"]["state"])
        self.assertEqual("FAIL", by_id["H50"]["F"])

    def test_mutation_duplicate_id_fails(self):
        rows = copy.deepcopy(self.rows)
        rows[1]["id"] = rows[0]["id"]
        self.assertTrue(mod.validate(rows, self.meta))

    def test_mutation_fake_evidence_fails(self):
        rows = copy.deepcopy(self.rows)
        rows[0]["E"] = "PASS"
        self.assertTrue(any("E may not be PASS" in e for e in mod.validate(rows, self.meta)))

    def test_mutation_absolute_certainty_promotion_fails(self):
        rows = copy.deepcopy(self.rows)
        by_id = {r["id"]: r for r in rows}
        by_id["H50"]["state"] = "H"
        by_id["H50"]["F"] = "PASS"
        self.assertTrue(mod.validate(rows, self.meta))

    def test_mutation_claim_allowed_fails(self):
        meta = dict(self.meta)
        meta["claim_allowed"] = True
        self.assertTrue(any("fail-closed" in e for e in mod.validate(self.rows, meta)))


if __name__ == "__main__":
    unittest.main()
