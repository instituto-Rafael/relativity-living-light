"""Adversarial static gates for evidence-source graph. No external network."""
from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "tools/ci/rll_polymorphic_evidence_gate_v1.py"
SPEC = importlib.util.spec_from_file_location("poly_gate", P)
gate = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(gate)


class EpistemicGraphTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = gate.load_json(gate.SPEC)
        cls.g4 = gate.load_json(gate.G4)

    def check_error(self, data, signal):
        r = gate.evaluate(data, self.g4)
        self.assertNotEqual(r["state"], gate.RECEIPT_STATE)
        self.assertTrue(any(signal in x for x in r["errors"]), r)

    def test_scope_passes_without_science_claim(self):
        r = gate.evaluate(self.contract, self.g4)
        self.assertEqual(r["state"], gate.RECEIPT_STATE)
        self.assertFalse(r["claim_allowed"])
        self.assertEqual(r["network_requests"], 0)
        self.assertEqual(r["secrets_read"], 0)

    def test_news_is_not_primary_data(self):
        x = copy.deepcopy(self.contract)
        x["relations"].append({"from":"source:SCIENCE_X", "to":"hypothesis:RLL_BACKGROUND",
            "type":"ELIGIBLE_LIKELIHOOD_INPUT","scope":"COSMOLOGY_ONLY","evidence":"CLAIM"})
        self.check_error(x, "NONPRIMARY_EVIDENCE_CANNOT_BE_LIKELIHOOD_INPUT")

    def test_exploratory_xray_requires_mechanism(self):
        x = copy.deepcopy(self.contract)
        next(h for h in x["hypotheses"] if h["id"] == "TRIBO_XRAY_CELL")["state"] = "CONFIRMED"
        self.check_error(x, "TRIBO_XRAY_PROMOTED_WITHOUT_MECHANISM")

    def test_analogy_cannot_become_causal(self):
        x = copy.deepcopy(self.contract)
        next(e for e in x["relations"] if e["type"] == "ANALOGY_NOT_CAUSALITY")["evidence"] = "VERIFIED_CAUSAL"
        self.check_error(x, "ANALOGY_TO_CAUSALITY_ESCALATION")

    def test_cycles_fail(self):
        x = copy.deepcopy(self.contract)
        x["relations"].extend([
            {"from":"hypothesis:MITO_ATP","to":"hypothesis:TRIBO_XRAY_CELL",
             "type":"DEPENDS_ON","scope":"CELL","evidence":"UNPROVEN"},
            {"from":"hypothesis:TRIBO_XRAY_CELL","to":"hypothesis:MITO_ATP",
             "type":"DEPENDS_ON","scope":"CELL","evidence":"UNPROVEN"},
        ])
        self.check_error(x, "CAUSAL_DEPENDENCY_CYCLE")

    def test_bayes_blocks_empty(self):
        result = gate.bayesian_readiness({}, self.contract["sources"])
        self.assertTrue(result.startswith("BLOCKED_TOKEN_VAZIO"))

    def test_bayes_blocks_double_counting(self):
        s = "a" * 64
        payload = {"prior_h1":0.5,"prior_origin":"source:registered", "h0":"LCDM",
            "h1":"RLL", "observations_sha256":s,"likelihood_sha256":s,
            "covariance_sha256":s, "selection_sha256":s, "nuisance_sha256":s,
            "independence_groups":["DESI_DR2_BAO", "DESI_DR2_BAO"],
            "all_preregistered":True,"model_parameter_counts":{"LCDM":4,"RLL":7}}
        self.assertIn("double counting", gate.bayesian_readiness(payload, self.contract["sources"]))

    def test_secrets_denied_on_pr(self):
        x = copy.deepcopy(self.contract)
        x["security"]["pr_secrets"] = "ALL"
        self.check_error(x, "SECRET_EXPOSURE_TO_PR")

    def test_scoped_sources_and_six_models(self):
        names = {s["id"] for s in self.contract["sources"]}
        self.assertTrue({"DESI_DR2_BAO","PANTHEON_PLUS","NOAA_NCEI","NATURE",
                         "SCIELO","ZENODO","SCIENCE_X","SUPABASE_RAF"} <= names)
        self.assertEqual(tuple(self.g4["models"]), gate.MODEL_SET)


if __name__ == "__main__":
    unittest.main()
