from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tools.rll_open_work_mechanism_gate_v2 import DELTA, ROOT, validate


class OpenWorkMechanismGateV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_delta = json.loads((ROOT / DELTA).read_text(encoding="utf-8"))

    def validate_mutation(self, payload: dict):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "delta.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            return validate(ROOT, path)

    def test_effective_queue_is_exactly_12_open_tokens(self):
        result = validate(ROOT, DELTA)
        self.assertEqual(result.decision, "PASS")
        self.assertEqual(result.historical_registry_count, 14)
        self.assertEqual(result.current_open_count, 12)
        self.assertEqual(result.effective_registry_count, 12)
        self.assertEqual(result.priority_counts, {"P0": 4, "P1": 6, "P2": 2})
        self.assertEqual(result.missing_tokens, [])
        self.assertEqual(result.extra_tokens, [])
        self.assertEqual(result.errors, [])
        self.assertFalse(result.claim_allowed)

    def test_only_two_evidence_backed_closures_leave_queue(self):
        result = validate(ROOT, DELTA)
        self.assertEqual(
            set(result.resolved_by_evidence),
            {
                "TOKEN_VAZIO_DIVERGED_OR_DESCENDANT_REF_SEMANTIC_REVIEW",
                "TOKEN_VAZIO_H0_PRIOR_PRIMARY_SOURCE_PROVENANCE",
            },
        )

    def test_external_availability_sharpens_attention_without_closing_tokens(self):
        result = validate(ROOT, DELTA)
        self.assertEqual(
            result.attention_overrides["TOKEN_VAZIO_DESI_DR2_OFFICIAL_JOINT_CROSSBLOCK_REPRODUCTION"],
            "ACTIVE_EXTERNAL_AVAILABLE",
        )
        self.assertEqual(
            result.attention_overrides["TOKEN_VAZIO_DES_Y6_3X2PT_LIKELIHOOD"],
            "ACTIVE_EXTERNAL_PARTIAL",
        )
        queue = {row["token"]: row for row in result.urgent_queue}
        self.assertEqual(
            queue["TOKEN_VAZIO_DESI_DR2_OFFICIAL_JOINT_CROSSBLOCK_REPRODUCTION"]["attention_state"],
            "ACTIVE_EXTERNAL_AVAILABLE",
        )
        self.assertEqual(
            queue["TOKEN_VAZIO_DES_Y6_3X2PT_LIKELIHOOD"]["attention_state"],
            "ACTIVE_EXTERNAL_PARTIAL",
        )

    def test_invalid_attention_override_fails_closed(self):
        payload = json.loads(json.dumps(self.base_delta))
        payload["attention_overrides"][0]["attention_state"] = "IGNORED"
        result = self.validate_mutation(payload)
        self.assertEqual(result.decision, "BLOCKED")
        self.assertTrue(any("unsupported attention override" in error for error in result.errors))

    def test_attention_override_requires_evidence(self):
        payload = json.loads(json.dumps(self.base_delta))
        payload["attention_overrides"][0]["evidence_path"] = "artifacts/science/external/DOES_NOT_EXIST.json"
        result = self.validate_mutation(payload)
        self.assertEqual(result.decision, "BLOCKED")
        self.assertTrue(any("attention evidence_path does not exist" in error for error in result.errors))

    def test_cannot_drop_an_open_token_by_listing_it_resolved(self):
        payload = json.loads(json.dumps(self.base_delta))
        payload["resolved_by_evidence"].append(
            {
                "token": "TOKEN_VAZIO_PHYSICAL_EXECUTION",
                "classification": "FAKE",
                "evidence_path": "data/results/utm185_void_mask_local_receipt.json",
                "closure_override_path": "data/governance/RLL_TOKEN_VAZIO_CLOSURE_OVERRIDES_20260808_V3.json",
            }
        )
        payload["expected_open_denominator"] = 11
        payload["expected_priority_counts"]["P0"] = 3
        result = self.validate_mutation(payload)
        self.assertEqual(result.decision, "BLOCKED")
        self.assertTrue(any("still OPEN in V3" in error for error in result.errors))

    def test_missing_closure_evidence_path_fails(self):
        payload = json.loads(json.dumps(self.base_delta))
        payload["resolved_by_evidence"][0]["evidence_path"] = "data/DOES_NOT_EXIST.json"
        result = self.validate_mutation(payload)
        self.assertEqual(result.decision, "BLOCKED")
        self.assertTrue(any("does not exist" in error for error in result.errors))

    def test_missing_mechanism_spec_fails(self):
        payload = json.loads(json.dumps(self.base_delta))
        payload["mechanism_enrichments"][0]["spec_path"] = "data/science/DOES_NOT_EXIST.json"
        result = self.validate_mutation(payload)
        self.assertEqual(result.decision, "BLOCKED")
        self.assertTrue(any("spec_path does not exist" in error for error in result.errors))

    def test_enrichment_cannot_target_resolved_token(self):
        payload = json.loads(json.dumps(self.base_delta))
        payload["mechanism_enrichments"][0]["token"] = "TOKEN_VAZIO_H0_PRIOR_PRIMARY_SOURCE_PROVENANCE"
        result = self.validate_mutation(payload)
        self.assertEqual(result.decision, "BLOCKED")
        self.assertTrue(any("currently open" in error for error in result.errors))


if __name__ == "__main__":
    unittest.main()
