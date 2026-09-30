from __future__ import annotations

import unittest

from tools.rll_branch_maturity_decision_packet import build


class BranchMaturityDecisionPacketTests(unittest.TestCase):
    def test_diverged_history_is_never_force_reset_by_packet(self):
        packet = build()
        self.assertFalse(packet["force_reset_allowed"])
        self.assertFalse(packet["claim_allowed"])
        self.assertIn("rll/lab", packet["branches_with_unique_commits"])
        self.assertIn("rll/integration", packet["branches_with_unique_commits"])
        self.assertNotIn("rll/release", packet["branches_with_unique_commits"])

    def test_policy_choice_remains_explicit_governance_decision(self):
        packet = build()
        self.assertEqual(packet["state"], "READY_FOR_GOVERNANCE_DECISION")
        self.assertTrue(packet["selected_option"].startswith("TOKEN_VAZIO"))
        self.assertEqual(len(packet["options"]), 2)


if __name__ == "__main__":
    unittest.main()
