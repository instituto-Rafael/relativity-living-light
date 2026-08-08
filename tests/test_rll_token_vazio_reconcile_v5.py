from __future__ import annotations

import unittest

from tools.rll_token_vazio_reconcile_v2 import ROOT
from tools.rll_token_vazio_reconcile_v5 import build_current_view


class TokenVazioReconcileV5Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = build_current_view(ROOT, generated_at="2026-08-08T07:10:00Z")
        cls.by_token = {row["token"]: row for row in cls.receipt["results"]}

    def test_v5_adds_one_open_gap_without_rewriting_prior_history(self):
        summary = self.receipt["summary"]
        self.assertEqual(summary["input_tokens"], 35)
        self.assertEqual(summary["terminal_resolved"], 13)
        self.assertEqual(summary["reduced_generic"], 9)
        self.assertEqual(summary["open"], 13)
        self.assertFalse(self.receipt["claim_allowed"])
        self.assertFalse(self.receipt["publication_ready"])
        self.assertEqual(self.receipt["view"], "RLL_TOKEN_VAZIO_RECONCILIATION_V5_APPEND_ONLY")
        self.assertTrue(self.receipt["policy"]["v1_v2_v3_v4_history_preserved"])

    def test_modern_sn_gap_is_explicit_p0_mixed_work(self):
        row = self.by_token["TOKEN_VAZIO_MODERN_SN_FULL_LIKELIHOOD"]
        self.assertEqual(row["priority"], "P0")
        self.assertEqual(row["state"], "OPEN_MIXED")
        self.assertEqual(row["classification"], "MODERN_SN_FULL_COVARIANCE_CALIBRATION_NOT_MATERIALIZED")
        self.assertIn("pantheon", row["next_action"].lower())
        self.assertIn("covariance", row["next_action"].lower())

    def test_prior_external_settings_transition_remains_negative_with_p0_successor(self):
        old = self.by_token["TOKEN_VAZIO_EXTERNAL_SETTINGS"]
        successor = self.by_token["TOKEN_VAZIO_GITHUB_PLATFORM_ENFORCEMENT"]
        self.assertEqual(old["state"], "RESOLVED_NEGATIVE")
        self.assertEqual(successor["state"], "OPEN_GOVERNANCE")
        self.assertEqual(successor["priority"], "P0")

    def test_no_open_evidence_missing(self):
        self.assertFalse(any(row["state"] == "OPEN_EVIDENCE_MISSING" for row in self.receipt["results"]))


if __name__ == "__main__":
    unittest.main()
