from __future__ import annotations

import unittest

from tools.rll_token_vazio_reconcile_v2 import ROOT
from tools.rll_token_vazio_reconcile_v4 import build_current_view


class TokenVazioReconcileV4Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = build_current_view(ROOT, generated_at="2026-08-08T06:50:00Z")
        cls.by_token = {row["token"]: row for row in cls.receipt["results"]}

    def test_v4_preserves_history_and_keeps_open_count_honest(self):
        summary = self.receipt["summary"]
        self.assertEqual(summary["input_tokens"], 34)
        self.assertEqual(summary["terminal_resolved"], 13)
        self.assertEqual(summary["reduced_generic"], 9)
        self.assertEqual(summary["open"], 12)
        self.assertFalse(self.receipt["claim_allowed"])
        self.assertFalse(self.receipt["publication_ready"])
        self.assertEqual(self.receipt["view"], "RLL_TOKEN_VAZIO_RECONCILIATION_V4_APPEND_ONLY")
        self.assertTrue(self.receipt["policy"]["v1_v2_v3_history_preserved"])

    def test_unknown_settings_closes_negative_not_positive(self):
        row = self.by_token["TOKEN_VAZIO_EXTERNAL_SETTINGS"]
        self.assertEqual(row["state"], "RESOLVED_NEGATIVE")
        self.assertTrue(row["evidence_verified"])
        self.assertEqual(row["classification"], "EXTERNAL_SETTINGS_OBSERVED_NO_BRANCH_PROTECTION_OR_RULESETS")
        self.assertEqual(row["successors"], ["TOKEN_VAZIO_GITHUB_PLATFORM_ENFORCEMENT"])

    def test_platform_enforcement_successor_is_p0_and_open(self):
        row = self.by_token["TOKEN_VAZIO_GITHUB_PLATFORM_ENFORCEMENT"]
        self.assertEqual(row["priority"], "P0")
        self.assertEqual(row["state"], "OPEN_GOVERNANCE")
        self.assertEqual(row["classification"], "PLATFORM_ENFORCEMENT_ABSENT")
        self.assertIn("branch protection", row["next_action"].lower())

    def test_no_open_evidence_missing_is_created(self):
        self.assertFalse(any(row["state"] == "OPEN_EVIDENCE_MISSING" for row in self.receipt["results"]))


if __name__ == "__main__":
    unittest.main()
