from __future__ import annotations

import copy
import unittest

from tools.rll_atlas_evolution_gate import (
    DEFAULT_REGISTRY,
    compare_no_regression,
    load_json,
    validate_record,
)


class RllAtlasEvolutionGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = load_json(DEFAULT_REGISTRY)

    def test_current_record_is_fail_closed_and_structurally_valid(self):
        self.assertEqual(validate_record(self.record), [])
        self.assertFalse(self.record["claim_allowed"])
        self.assertFalse(self.record["publication_ready"])
        states = {gate["id"]: gate["status"] for gate in self.record["gates"]}
        self.assertEqual(states["G0_SOURCE_RIGHTS_FREEZE"], "PARTIAL")
        self.assertEqual(states["G1_OBSERVABLE_SCHEMA"], "PARTIAL")
        self.assertEqual(states["G7_CLAIM_DECISION"], "BLOCKED")

    def test_cannot_turn_claim_on_while_prerequisites_are_open(self):
        candidate = copy.deepcopy(self.record)
        candidate["claim_allowed"] = True
        errors = validate_record(candidate)
        self.assertTrue(any("claim_allowed=true" in error for error in errors))

    def test_status_and_maturity_must_agree(self):
        candidate = copy.deepcopy(self.record)
        candidate["gates"][2]["maturity"] = 2
        errors = validate_record(candidate)
        self.assertTrue(any("G2_FULL_COVARIANCE" in error and "maturity" in error for error in errors))

    def test_no_regression_rejects_maturity_drop_and_evidence_removal(self):
        previous = copy.deepcopy(self.record)
        previous["record_id"] = "PREVIOUS"
        previous["revision"] = 1
        previous["gates"][0]["status"] = "VERIFIED_LIMITED"
        previous["gates"][0]["maturity"] = 2

        candidate = copy.deepcopy(previous)
        candidate["record_id"] = "CANDIDATE"
        candidate["revision"] = 2
        candidate["predecessor"] = "PREVIOUS"
        candidate["gates"][0]["status"] = "PARTIAL"
        candidate["gates"][0]["maturity"] = 1
        candidate["gates"][0]["evidence"] = []

        errors = compare_no_regression(previous, candidate)
        self.assertTrue(any("maturity regression" in error for error in errors))
        self.assertTrue(any("evidence custody shrank" in error for error in errors))

    def test_evidence_preserving_maturity_increase_is_allowed(self):
        previous = copy.deepcopy(self.record)
        previous["record_id"] = "PREVIOUS"
        previous["revision"] = 1

        candidate = copy.deepcopy(previous)
        candidate["record_id"] = "CANDIDATE"
        candidate["revision"] = 2
        candidate["predecessor"] = "PREVIOUS"
        candidate["gates"][2]["status"] = "PARTIAL"
        candidate["gates"][2]["maturity"] = 1
        candidate["gates"][2]["evidence"].append(
            {"path": "artifacts/science/example.json", "git_blob_sha1": "1" * 40}
        )

        self.assertEqual(compare_no_regression(previous, candidate), [])


if __name__ == "__main__":
    unittest.main()
