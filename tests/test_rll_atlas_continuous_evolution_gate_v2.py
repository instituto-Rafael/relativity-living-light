from __future__ import annotations

import copy
import unittest

from tools.rll_atlas_continuous_evolution_gate_v2 import (
    DEFAULT_ENVELOPE,
    DEFAULT_PREDECESSOR,
    DEFAULT_TRACE,
    build_receipt,
    load_json,
    load_jsonl,
    validate_envelope,
)


class RllAtlasContinuousEvolutionOmega6V2Tests(unittest.TestCase):
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
        self.assertFalse(receipt["publication_ready"])
        self.assertEqual(receipt["omega6_active_count"], 6)
        self.assertEqual(receipt["scientific_promotion_gate_fraction"], 0.190476)

    def test_exactly_six_complementary_guardrails_are_required(self):
        candidate = copy.deepcopy(self.envelope)
        candidate["omega6_guardrails"].pop()
        self.assertTrue(any("exact complementary Ω6" in e for e in self.validate(candidate)))

    def test_session_mesh_is_consumed_and_not_duplicated(self):
        candidate = copy.deepcopy(self.envelope)
        candidate["omega6_guardrails"][0]["id"] = "FENCE-01-AUTHORITY"
        errors = self.validate(candidate)
        self.assertTrue(any("Ω6" in e for e in errors))

    def test_urgency_cannot_lower_truth_or_evidence_thresholds(self):
        candidate = copy.deepcopy(self.envelope)
        candidate["urgency_policy"]["truth_threshold_mutable"] = True
        candidate["urgency_policy"]["evidence_threshold_mutable"] = True
        errors = self.validate(candidate)
        self.assertTrue(any("truth threshold" in e for e in errors))
        self.assertTrue(any("evidence threshold" in e for e in errors))

    def test_custody_cycle_is_rejected(self):
        candidate = copy.deepcopy(self.envelope)
        candidate["custody_graph"]["edges"].append(
            {"from": "N_RECEIPT", "to": "N_PREDECESSOR", "relation": "forbidden_cycle"}
        )
        self.assertTrue(any("acyclic" in e for e in self.validate(candidate)))

    def test_missing_evidence_digest_is_rejected(self):
        candidate = copy.deepcopy(self.envelope)
        evidence_node = next(n for n in candidate["custody_graph"]["nodes"] if n["id"] == "N_BAYES")
        evidence_node.pop("git_blob_sha1")
        self.assertTrue(any("immutable git_blob_sha1" in e for e in self.validate(candidate)))

    def test_maturity_regression_is_rejected(self):
        candidate = copy.deepcopy(self.envelope)
        gate = candidate["atlas_gate_projection"][0]
        gate["status"] = "TOKEN_VAZIO"
        gate["maturity"] = 0
        self.assertTrue(any("maturity regression" in e for e in self.validate(candidate)))

    def test_internal_replay_cannot_resolve_independent_replication(self):
        candidate = copy.deepcopy(self.envelope)
        next(g for g in candidate["gap_reconciliation"] if g["token"] == "TOKEN_VAZIO_INDEPENDENT_REPLICATION")["state"] = "RESOLVED"
        self.assertTrue(any("INDEPENDENT_REPLICATION" in e or "independent replication" in e for e in self.validate(candidate)))

    def test_generic_bayes_gap_cannot_be_falsely_closed(self):
        candidate = copy.deepcopy(self.envelope)
        next(g for g in candidate["gap_reconciliation"] if g["token"] == "TOKEN_VAZIO_REAL_BAYES_INFERENCE")["state"] = "RESOLVED"
        self.assertTrue(any("generic Bayes token" in e for e in self.validate(candidate)))

    def test_auto_merge_cannot_be_enabled(self):
        candidate = copy.deepcopy(self.envelope)
        candidate["continuous_execution"]["auto_merge"] = True
        self.assertTrue(any("auto_merge" in e for e in self.validate(candidate)))

    def test_evidence_preserving_maturity_increase_is_allowed(self):
        candidate = copy.deepcopy(self.envelope)
        gate = candidate["atlas_gate_projection"][2]
        gate["status"] = "PARTIAL"
        gate["maturity"] = 1
        gate["evidence"].append({"path": "artifacts/science/example_covariance.json", "git_blob_sha1": "1" * 40})
        errors = self.validate(candidate)
        self.assertFalse(any("G2_FULL_COVARIANCE" in e and "maturity regression" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
