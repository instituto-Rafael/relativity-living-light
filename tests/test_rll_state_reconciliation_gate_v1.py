import copy
import json
import tempfile
import unittest
from pathlib import Path

from tools.ci.rll_state_reconciliation_gate_v1 import audit

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/governance/rll_state_reconciliation_20261115.v1.json"

class StateReconciliationGate(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(SOURCE.read_text())

    def run_mutation(self, mutate):
        candidate = copy.deepcopy(self.data)
        mutate(candidate)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "candidate.json"
            path.write_text(json.dumps(candidate))
            return audit(path)

    def test_canonical_contract_passes_scoped(self):
        report = audit(SOURCE)
        self.assertEqual(report["status"], "PASS_SCOPED_STATE_RECONCILIATION")
        self.assertFalse(report["claim_allowed"])
        self.assertEqual(report["merged_prs"], [1172, 1173])

    def test_claim_promotion_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "CLAIM_PROMOTION_BLOCKED"):
            self.run_mutation(lambda d: d.__setitem__("claim_allowed", True))

    def test_state_downgrade_is_detected(self):
        with self.assertRaisesRegex(ValueError, "PR_1172_STATE_MISMATCH"):
            self.run_mutation(lambda d: d["pull_requests"][0].__setitem__("state", "DRAFT/HOLD"))

    def test_head_sha_drift_is_detected(self):
        with self.assertRaisesRegex(ValueError, "PR_1173_SHA_MISMATCH"):
            self.run_mutation(lambda d: d["pull_requests"][1].__setitem__("head_sha", "0" * 40))

    def test_missing_falsifier_is_detected(self):
        with self.assertRaisesRegex(ValueError, "SCIENTIFIC_GATE_SET_MISMATCH"):
            self.run_mutation(lambda d: d["scientific_gates"].pop("independent_reproduction"))

    def test_unearned_gate_promotion_is_detected(self):
        with self.assertRaisesRegex(ValueError, "UNSUPPORTED_GATE_PROMOTION"):
            self.run_mutation(lambda d: d["scientific_gates"].__setitem__("nonlinear_pk", "PASS"))

    def test_source_reference_drift_is_detected(self):
        with self.assertRaisesRegex(ValueError, "PR_1172_SOURCE_MISMATCH"):
            self.run_mutation(lambda d: d["pull_requests"][0].__setitem__("source_ref", "TOKEN_VAZIO"))

if __name__ == "__main__":
    unittest.main(verbosity=2)
