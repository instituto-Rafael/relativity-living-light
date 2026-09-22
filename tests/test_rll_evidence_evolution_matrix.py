import copy
import json
import unittest
from pathlib import Path

from tools.validate_rll_evidence_evolution_matrix import validate_matrix

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "data/governance/RLL_EVIDENCE_EVOLUTION_MATRIX_V1.json"

class EvidenceEvolutionMatrixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = json.loads(MATRIX.read_text(encoding="utf-8"))

    def test_canonical_matrix_passes(self):
        self.assertEqual(validate_matrix(copy.deepcopy(self.base)), [])

    def test_missing_provenance_fails(self):
        data = copy.deepcopy(self.base)
        data["workstreams"][0]["provenance"]["sources"] = []
        self.assertIn("workstreams[0]:provenance_sources_empty", validate_matrix(data))

    def test_missing_context_boundary_fails(self):
        data = copy.deepcopy(self.base)
        data["workstreams"][0]["context"]["boundary"] = ""
        self.assertIn("workstreams[0]:context_boundary_missing", validate_matrix(data))

    def test_rollback_must_be_ready(self):
        data = copy.deepcopy(self.base)
        data["workstreams"][0]["rollback"]["state"] = "TOKEN_VAZIO"
        self.assertIn("workstreams[0]:rollback_not_ready", validate_matrix(data))

    def test_claim_promotion_is_refused(self):
        data = copy.deepcopy(self.base)
        data["workstreams"][2]["claim_allowed"] = True
        self.assertIn("workstreams[2]:claim_allowed_must_be_false", validate_matrix(data))

    def test_all_seven_domains_are_required(self):
        data = copy.deepcopy(self.base)
        data["workstreams"] = [x for x in data["workstreams"] if x["domain"] != "literature"]
        errors = validate_matrix(data)
        self.assertTrue(any(e.startswith("matrix:missing_domains:") for e in errors))

if __name__ == "__main__":
    unittest.main()
