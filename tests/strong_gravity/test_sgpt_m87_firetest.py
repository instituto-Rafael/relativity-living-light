from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "tools" / "validate_sgpt_m87_firetest.py"
SPEC = importlib.util.spec_from_file_location("validate_sgpt_m87_firetest", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class SGPTM87FiretestTests(unittest.TestCase):
    def test_preregistration_contract_passes_without_scientific_promotion(self):
        contract = MODULE.load()
        result = MODULE.validate(contract)
        self.assertEqual(result["status"], "PASS_PREREGISTRATION_CONTRACT_ONLY")
        self.assertFalse(result["claim_allowed"])
        self.assertEqual(result["scientific_validation"], "TOKEN_VAZIO")

    def test_illegal_mutations_are_rejected(self):
        rejected = MODULE.selftest(MODULE.load())
        self.assertGreaterEqual(len(rejected), 11)
        self.assertIn("prospective-relabel", rejected)
        self.assertIn("invent-mass", rejected)
        self.assertIn("drop-GRPIC", rejected)
        self.assertIn("G4-source-pass", rejected)
        self.assertIn("claim-promotion", rejected)

    def test_all_scientific_gates_start_token_vazio(self):
        contract = MODULE.load()
        self.assertEqual(
            list(contract["gates"]),
            MODULE.EXPECTED_GATES,
        )
        self.assertTrue(all(value == "TOKEN_VAZIO" for value in contract["gates"].values()))

    def test_public_eht_products_are_not_called_prospective(self):
        contract = MODULE.load()
        self.assertFalse(contract["prospective_claim"])
        self.assertIn(
            "not be described as a prospective blind prediction",
            contract["split"]["holdout_warning"],
        )

    def test_source_parameters_are_not_invented(self):
        contract = MODULE.load()
        self.assertTrue(
            all(value == "TOKEN_VAZIO" for value in contract["source"]["parameter_values"].values())
        )

    def test_temporal_ordering_remains_not_run(self):
        contract = MODULE.load()
        temporal = next(x for x in contract["hypotheses"] if x["id"] == "H_temporal_ordering")
        self.assertEqual(temporal["state"], "TOKEN_VAZIO_NOT_RUN")
        self.assertEqual(temporal["primary_test"], "TOKEN_VAZIO")


if __name__ == "__main__":
    unittest.main()
