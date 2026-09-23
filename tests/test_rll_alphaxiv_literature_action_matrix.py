from __future__ import annotations

import unittest

from tools.validate_rll_alphaxiv_literature_action_matrix import build


class RllAlphaXivLiteratureActionMatrixTests(unittest.TestCase):
    def test_literature_actions_are_fail_closed(self):
        payload = build()
        self.assertEqual(payload["state"], "PASS_FAIL_CLOSED_LITERATURE_ACTIONS")
        self.assertFalse(payload["claim_allowed"])
        self.assertEqual(payload["failed_checks"], [])

    def test_core_solver_and_growth_guards_are_present(self):
        payload = build()
        checks = payload["checks"]
        self.assertTrue(checks["rll_tolerance_not_silently_inherited"])
        self.assertTrue(checks["perturbation_token_unresolved"])
        self.assertTrue(checks["required_papers_present"])
        self.assertTrue(checks["required_gates_present"])

if __name__ == "__main__":
    unittest.main()
