from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tools.rll_open_work_mechanism_gate_v4 import DELTA, ROOT, validate


class OpenWorkMechanismGateV4Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = json.loads((ROOT / DELTA).read_text(encoding="utf-8"))

    def validate_mutation(self, payload: dict):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "delta.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            return validate(ROOT, path)

    def test_effective_queue_adds_modern_sn_without_dropping_prior_work(self):
        result = validate(ROOT, DELTA)
        self.assertEqual(result.decision, "PASS")
        self.assertEqual(result.predecessor_open_count, 12)
        self.assertEqual(result.current_open_count, 13)
        self.assertEqual(result.effective_registry_count, 13)
        self.assertEqual(result.priority_counts, {"P0": 6, "P1": 5, "P2": 2})
        self.assertEqual(result.added_open, ["TOKEN_VAZIO_MODERN_SN_FULL_LIKELIHOOD"])
        self.assertEqual(result.missing_tokens, [])
        self.assertEqual(result.extra_tokens, [])
        self.assertFalse(result.claim_allowed)

    def test_modern_sn_cannot_be_marked_ignored(self):
        payload = json.loads(json.dumps(self.base))
        payload["added_open_mechanisms"][0]["attention_state"] = "IGNORED"
        result = self.validate_mutation(payload)
        self.assertEqual(result.decision, "BLOCKED")
        self.assertTrue(any("forbidden" in error for error in result.errors))

    def test_modern_sn_mechanism_requires_falsifier(self):
        payload = json.loads(json.dumps(self.base))
        payload["added_open_mechanisms"][0]["mechanism"]["falsifier"] = ""
        result = self.validate_mutation(payload)
        self.assertEqual(result.decision, "BLOCKED")
        self.assertTrue(any("falsifier" in error for error in result.errors))

    def test_fake_extra_token_fails_closed(self):
        payload = json.loads(json.dumps(self.base))
        fake = json.loads(json.dumps(payload["added_open_mechanisms"][0]))
        fake["token"] = "TOKEN_VAZIO_FAKE_SN_GAP"
        fake["mechanism"]["id"] = "M_FAKE"
        payload["added_open_mechanisms"].append(fake)
        payload["expected_open_denominator"] = 14
        payload["expected_priority_counts"]["P0"] = 7
        result = self.validate_mutation(payload)
        self.assertEqual(result.decision, "BLOCKED")
        self.assertTrue(any("must be OPEN in V5" in error for error in result.errors))


if __name__ == "__main__":
    unittest.main()
