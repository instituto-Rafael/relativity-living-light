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

    def test_all_seven_legacy_gates_are_mapped_without_orphan(self):
        result = validate(ROOT, RECONCILIATION)
        self.assertEqual(result.decision, "PASS")
        self.assertEqual(result.legacy_gate_count, 7)
        self.assertEqual(result.mapped_gate_count, 7)
        self.assertEqual(result.unmapped_legacy_gates, [])
        self.assertEqual(result.duplicate_legacy_mappings, [])
        self.assertEqual(result.missing_current_targets, [])
        self.assertTrue(result.modern_sn_surfaced)
        self.assertFalse(result.claim_allowed)

    def test_dropping_legacy_gate_fails_closed(self):
        payload = json.loads(json.dumps(self.base))
        payload["mappings"] = payload["mappings"][:-1]
        result = self.validate_mutation(payload)
        self.assertEqual(result.decision, "BLOCKED")
        self.assertTrue(result.unmapped_legacy_gates)

    def test_renaming_target_to_noncanonical_token_fails(self):
        payload = json.loads(json.dumps(self.base))
        payload["mappings"][0]["current_tokens"] = ["TOKEN_VAZIO_FAKE_SN"]
        result = self.validate_mutation(payload)
        self.assertEqual(result.decision, "BLOCKED")
        self.assertIn("TOKEN_VAZIO_FAKE_SN", result.missing_current_targets)

    def test_reduced_mapping_requires_runtime_evidence(self):
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


if __name__ == "__main__":
    unittest.main()
