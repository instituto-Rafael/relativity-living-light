from __future__ import annotations

import copy
import unittest

from tools.rll_atlas_continuous_evolution_gate import (
    DEFAULT_ENVELOPE,
    DEFAULT_PREDECESSOR,
    DEFAULT_TRACE,
    build_receipt,
    load_json,
    load_jsonl,
    validate_envelope,
)


class RllAtlasContinuousEvolutionOmega6Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.envelope = load_json(DEFAULT_ENVELOPE)
        cls.predecessor = load_json(DEFAULT_PREDECESSOR)
        cls.trace = load_jsonl(DEFAULT_TRACE)

    def validate(self, candidate):
        return validate_envelope(candidate, self.predecessor, self.trace)

    def test_current_envelope_is_valid_and_fail_closed(self):
        errors = self.validate(self.envelope)
        self.assertEqual(errors, [])
        receipt = build_receipt(self.envelope, errors)
        self.assertTrue(receipt["valid"])
        self.assertFalse(receipt["claim_allowed"])
        self.assertEqual(receipt["omega6_active_count"], 6)
        self.assertEqual(receipt["scientific_promotion_gate_fraction"], 0.190476)

    def test_exactly_six_guardrails_are_required(self):
        candidate = copy.deepcopy(self.envelope)
        candidate["omega6_guardrails"].pop()
        errors = self.validate(candidate)
        self.assertTrue(any("exact OMEGA6 guardrail" in error for error in errors))

    def test_urgency_cannot_lower_truth_or_evidence_thresholds(self):
        candidate = copy.deepcopy(self.envelope)
        candidate["urgency_policy"]["truth_threshold_mutable"] = True
        candidate["urgency_policy"]["evidence_threshold_mutable"] = True
        errors = self.validate(candidate)
        self.assertTrue(any("truth threshold" in error for error in errors))
        self.assertTrue(any("evidence threshold" in error for error in errors))

    def test_custody_cycle_is_rejected(self):
        candidate = copy.deepcopy(self.envelope)
        candidate["custody_graph"]["edges"].append(
            {"from": "N_RECEIPT", "to": "N_PREDECESSOR", "relation": "forbidden_cycle"}
        )
        errors = self.validate(candidate)
        self.assertTrue(any("acyclic" in error for error in errors))

    def test_missing_evidence_digest_is_rejected(self):
        candidate = copy.deepcopy(self.envelope)
        candidate["custody_graph"]["nodes"][1].pop("git_blob_sha1")
        errors = self.validate(candidate)
        self.assertTrue(any("immutable git_blob_sha1" in error for error in errors))

    def test_maturity_regression_is_rejected(self):
        candidate = copy.deepcopy(self.envelope)
        gate = candidate["atlas_gate_projection"][0]
        gate["status"] = "TOKEN_VAZIO"
        gate["maturity"] = 0
        errors = self.validate(candidate)
        self.assertTrue(any("maturity regression" in error for error in errors))

    def test_internal_replay_cannot_resolve_independent_replication(self):
        candidate = copy.deepcopy(self.envelope)
        for gap in candidate["gap_reconciliation"]:
            if gap["token"] == "TOKEN_VAZIO_INDEPENDENT_REPLICATION":
                gap["state"] = "RESOLVED"
        errors = self.validate(candidate)
        self.assertTrue(any("INDEPENDENT_REPLICATION" in error for error in errors))

    def test_generic_bayes_gap_is_narrowed_not_falsely_closed(self):
        candidate = copy.deepcopy(self.envelope)
        for gap in candidate["gap_reconciliation"]:
            if gap["token"] == "TOKEN_VAZIO_REAL_BAYES_INFERENCE":
                gap["state"] = "RESOLVED"
        errors = self.validate(candidate)
        self.assertTrue(any("generic Bayes token" in error for error in errors))

    def test_workflow_surface_cannot_gain_auto_merge(self):
        candidate = copy.deepcopy(self.envelope)
        candidate["continuous_execution"]["auto_merge"] = True
        errors = self.validate(candidate)
        self.assertTrue(any("auto_merge" in error for error in errors))

    def test_evidence_preserving_maturity_increase_is_allowed(self):
        candidate = copy.deepcopy(self.envelope)
        gate = candidate["atlas_gate_projection"][2]
        gate["status"] = "PARTIAL"
        gate["maturity"] = 1
        gate["reason"] = "Synthetic successor example: evidence-backed covariance progress."
        gate["evidence"].append(
            {"path": "artifacts/science/example_covariance_receipt.json", "git_blob_sha1": "1" * 40}
        )
        errors = self.validate(candidate)
        self.assertFalse(any("G2_FULL_COVARIANCE" in error and "maturity regression" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
