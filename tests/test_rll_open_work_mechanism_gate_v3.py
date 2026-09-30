from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tools.rll_open_work_mechanism_gate_v3 import DELTA, ROOT, validate


class OpenWorkMechanismGateV3Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = json.loads((ROOT / DELTA).read_text(encoding="utf-8"))

    def validate_mutation(self, payload: dict):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "delta.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            return validate(ROOT, path)

    def test_effective_queue_replaces_unknown_settings_with_p0_enforcement(self):
        result = validate(ROOT, DELTA)
        self.assertEqual(result.decision, "PASS")
        self.assertEqual(result.current_open_count, 12)
        self.assertEqual(result.effective_registry_count, 12)
        self.assertEqual(result.priority_counts, {"P0": 5, "P1": 5, "P2": 2})
        self.assertEqual(result.newly_resolved, ["TOKEN_VAZIO_EXTERNAL_SETTINGS"])
        self.assertEqual(result.newly_added_open, ["TOKEN_VAZIO_GITHUB_PLATFORM_ENFORCEMENT"])
        tokens = {row["token"] for row in result.urgent_queue}
        self.assertNotIn("TOKEN_VAZIO_EXTERNAL_SETTINGS", tokens)
        self.assertIn("TOKEN_VAZIO_GITHUB_PLATFORM_ENFORCEMENT", tokens)
        self.assertEqual(result.errors, [])

    def test_ignored_successor_fails_closed(self):
        payload = json.loads(json.dumps(self.base))
        payload["added_open_mechanisms"][0]["attention_state"] = "IGNORED"
        result = self.validate_mutation(payload)
        self.assertEqual(result.decision, "BLOCKED")
        self.assertTrue(any("forbidden" in error for error in result.errors))

    def test_missing_evidence_fails_closed(self):
        payload = json.loads(json.dumps(self.base))
        payload["resolved_by_evidence"][0]["evidence_path"] = "artifacts/governance/DOES_NOT_EXIST.json"
        result = self.validate_mutation(payload)
        self.assertEqual(result.decision, "BLOCKED")
        self.assertTrue(any("missing evidence_path" in error for error in result.errors))

    def test_successor_cannot_be_renamed_out_of_current_view(self):
        payload = json.loads(json.dumps(self.base))
        payload["added_open_mechanisms"][0]["token"] = "TOKEN_VAZIO_FAKE_PLATFORM_ENFORCEMENT"
        result = self.validate_mutation(payload)
        self.assertEqual(result.decision, "BLOCKED")
        self.assertTrue(any("must be OPEN in V4" in error for error in result.errors))


if __name__ == "__main__":
    unittest.main()
