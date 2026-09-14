from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from tools.rll_open_work_mechanism_gate_v1 import (
    DEFAULT_REGISTRY,
    ROOT,
    validate_registry,
)


class OpenWorkMechanismGateTests(unittest.TestCase):
    def load_registry(self) -> dict:
        return json.loads((ROOT / DEFAULT_REGISTRY).read_text(encoding="utf-8"))

    def validate_mutation(self, payload: dict):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "registry.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            return validate_registry(ROOT, path)

    def test_current_registry_saturates_all_open_tokens(self):
        result = validate_registry(ROOT, DEFAULT_REGISTRY)
        self.assertEqual(result.decision, "PASS")
        self.assertEqual(result.current_open_count, 14)
        self.assertEqual(result.registry_count, 14)
        self.assertEqual(result.priority_counts, {"P0": 4, "P1": 7, "P2": 3})
        self.assertEqual(result.missing_tokens, [])
        self.assertEqual(result.extra_tokens, [])
        self.assertEqual(result.ignored_tokens, [])
        self.assertEqual(result.content_errors, [])
        self.assertFalse(result.claim_allowed)

    def test_ignored_attention_fails_closed(self):
        payload = self.load_registry()
        payload["tokens"][0]["attention_state"] = "IGNORED"
        result = self.validate_mutation(payload)
        self.assertEqual(result.decision, "BLOCKED")
        self.assertIn(payload["tokens"][0]["token"], result.ignored_tokens)

    def test_missing_mechanism_content_fails_closed(self):
        payload = self.load_registry()
        payload["tokens"][0]["mechanism"]["falsifier"] = ""
        result = self.validate_mutation(payload)
        self.assertEqual(result.decision, "BLOCKED")
        self.assertTrue(any("mechanism.falsifier" in err for err in result.content_errors))

    def test_missing_current_token_fails_closed(self):
        payload = self.load_registry()
        removed = payload["tokens"].pop()
        payload["expected_open_denominator"] = 13
        payload["expected_priority_counts"]["P2"] = 2
        result = self.validate_mutation(payload)
        self.assertEqual(result.decision, "BLOCKED")
        self.assertIn(removed["token"], result.missing_tokens)

    def test_extra_noncurrent_token_fails_closed(self):
        payload = self.load_registry()
        extra = copy.deepcopy(payload["tokens"][0])
        extra["token"] = "TOKEN_VAZIO_FAKE_NONCURRENT"
        extra["mechanism"]["id"] = "M99_FAKE"
        payload["tokens"].append(extra)
        payload["expected_open_denominator"] = 15
        payload["expected_priority_counts"]["P0"] = 5
        result = self.validate_mutation(payload)
        self.assertEqual(result.decision, "BLOCKED")
        self.assertIn("TOKEN_VAZIO_FAKE_NONCURRENT", result.extra_tokens)

    def test_broken_repo_driver_path_fails_closed(self):
        payload = self.load_registry()
        payload["tokens"][0]["mechanism"]["driver"] = "tools/DOES_NOT_EXIST.py"
        result = self.validate_mutation(payload)
        self.assertEqual(result.decision, "BLOCKED")
        self.assertTrue(any("driver path does not exist" in err for err in result.content_errors))

    def test_self_dependency_fails_closed(self):
        payload = self.load_registry()
        payload["tokens"][0]["dependencies"] = [payload["tokens"][0]["token"]]
        result = self.validate_mutation(payload)
        self.assertEqual(result.decision, "BLOCKED")
        self.assertTrue(any("self-dependency" in err for err in result.content_errors))


if __name__ == "__main__":
    unittest.main()
