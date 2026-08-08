from __future__ import annotations

import unittest

from tools.main_promotion_route_gate import evaluate


class MainPromotionRouteGateTests(unittest.TestCase):
    def test_release_to_main_passes(self):
        receipt = evaluate("rll/release", "main")
        self.assertEqual(receipt["decision"], "PASS")
        self.assertEqual(receipt["residuals"], [])
        self.assertIs(receipt["claim_allowed"], False)

    def test_lab_to_main_is_blocked(self):
        receipt = evaluate("rll/lab", "main")
        self.assertEqual(receipt["decision"], "BLOCKED")
        self.assertIn("MAIN_REQUIRES_RLL_RELEASE_HEAD:rll/lab", receipt["residuals"])

    def test_feature_to_main_is_blocked(self):
        receipt = evaluate("feature/example", "main")
        self.assertEqual(receipt["decision"], "BLOCKED")
        self.assertIn("MAIN_REQUIRES_RLL_RELEASE_HEAD:feature/example", receipt["residuals"])

    def test_prefixed_release_ref_is_normalized(self):
        receipt = evaluate("refs/heads/rll/release", "refs/heads/main")
        self.assertEqual(receipt["decision"], "PASS")

    def test_non_main_base_fails_closed(self):
        receipt = evaluate("rll/release", "rll/integration")
        self.assertEqual(receipt["decision"], "BLOCKED")
        self.assertIn("UNSUPPORTED_BASE:rll/integration", receipt["residuals"])


if __name__ == "__main__":
    unittest.main()
