from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tools.rll_modern_validation_reconcile_v2 import RECONCILIATION, ROOT, validate


class ModernValidationReconcileV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = json.loads((ROOT / RECONCILIATION).read_text(encoding="utf-8"))

    def validate_mutation(self, payload: dict):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "reconciliation.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            return validate(ROOT, path)

    def test_all_seven_legacy_gates_reconcile_to_v4_without_duplicate_work(self):
        result = validate(ROOT, RECONCILIATION)
        self.assertEqual(result.decision, "PASS")
        self.assertEqual(result.current_token_view, "RLL_TOKEN_VAZIO_RECONCILIATION_V4_APPEND_ONLY")
        self.assertEqual(result.legacy_gate_count, 7)
        self.assertEqual(result.mapped_gate_count, 7)
        self.assertEqual(result.current_target_count, 8)
        self.assertEqual(
            result.no_open_successor_legacy_gates,
            ["RLL-MOD-P0-SN-CALIBRATION-COVARIANCE"],
        )
        self.assertEqual(result.unmapped_legacy_gates, [])
        self.assertEqual(result.duplicate_legacy_mappings, [])
        self.assertEqual(result.missing_current_targets, [])
        self.assertEqual(result.nonopen_current_targets, [])
        self.assertTrue(result.modern_sn_chain_closed)
        self.assertEqual(result.errors, [])
        self.assertFalse(result.claim_allowed)

    def test_dropping_legacy_gate_fails_closed(self):
        payload = json.loads(json.dumps(self.base))
        payload["mappings"] = payload["mappings"][:-1]
        result = self.validate_mutation(payload)
        self.assertEqual(result.decision, "BLOCKED")
        self.assertTrue(result.unmapped_legacy_gates)

    def test_renaming_open_target_to_noncanonical_token_fails(self):
        payload = json.loads(json.dumps(self.base))
        desi = next(row for row in payload["mappings"] if row["legacy_gate_id"] == "RLL-MOD-P0-DESI-DR2-REPRODUCTION")
        desi["current_tokens"] = ["TOKEN_VAZIO_FAKE_DESI"]
        result = self.validate_mutation(payload)
        self.assertEqual(result.decision, "BLOCKED")
        self.assertIn("TOKEN_VAZIO_FAKE_DESI", result.missing_current_targets)

    def test_reduced_runtime_mapping_requires_custody(self):
        payload = json.loads(json.dumps(self.base))
        desi = next(row for row in payload["mappings"] if row["legacy_gate_id"] == "RLL-MOD-P0-DESI-DR2-REPRODUCTION")
        desi["evidence"] = []
        result = self.validate_mutation(payload)
        self.assertEqual(result.decision, "BLOCKED")
        self.assertIn("RLL-MOD-P0-DESI-DR2-REPRODUCTION", result.reduced_mappings_without_evidence)

    def test_duplicate_legacy_mapping_fails_closed(self):
        payload = json.loads(json.dumps(self.base))
        payload["mappings"].append(json.loads(json.dumps(payload["mappings"][0])))
        result = self.validate_mutation(payload)
        self.assertEqual(result.decision, "BLOCKED")
        self.assertTrue(result.duplicate_legacy_mappings)

    def test_sn_gate_cannot_be_reopened_by_rename(self):
        payload = json.loads(json.dumps(self.base))
        sn = next(row for row in payload["mappings"] if row["legacy_gate_id"] == "RLL-MOD-P0-SN-CALIBRATION-COVARIANCE")
        sn["current_tokens"] = ["TOKEN_VAZIO_DESI_DR2_OFFICIAL_JOINT_CROSSBLOCK_REPRODUCTION"]
        result = self.validate_mutation(payload)
        self.assertEqual(result.decision, "BLOCKED")
        self.assertTrue(any("terminal successor relation" in error for error in result.errors))

    def test_sn_historical_chain_state_mismatch_fails(self):
        payload = json.loads(json.dumps(self.base))
        sn = next(row for row in payload["mappings"] if row["legacy_gate_id"] == "RLL-MOD-P0-SN-CALIBRATION-COVARIANCE")
        sn["historical_chain"][-1]["expected_state"] = "OPEN_MIXED"
        result = self.validate_mutation(payload)
        self.assertEqual(result.decision, "BLOCKED")
        self.assertIn("RLL-MOD-P0-SN-CALIBRATION-COVARIANCE", result.invalid_historical_chain_entries)
        self.assertFalse(result.modern_sn_chain_closed)


if __name__ == "__main__":
    unittest.main()
