from __future__ import annotations

import unittest

from tools.rll_perturbation_a1_linear_fluid_regularity_v1 import (
    MACHINE_EPSILON,
    _one_plus_w,
    build,
    evaluate_case,
)


class A1LinearFluidRegularityTests(unittest.TestCase):
    def test_stable_representation_recovers_small_positive_one_plus_w(self):
        stable = _one_plus_w(0.0, 10.0, 0.05, stable=True)
        naive = _one_plus_w(0.0, 10.0, 0.05, stable=False)
        self.assertGreater(stable, 0.0)
        self.assertLess(stable, 1e-80)
        self.assertEqual(naive, 0.0)

    def test_extreme_case_blocks_direct_double_precision_handoff(self):
        result = evaluate_case(10.0, 0.05)
        self.assertEqual(result["state"], "BLOCKED_DIRECT_STANDARD_FLUID_REPRESENTATION")
        self.assertGreater(result["naive_subtraction_zero_count"], 0)
        self.assertGreater(result["below_unit_roundoff_count"], 0)
        self.assertLess(result["min_stable_1_plus_w"], MACHINE_EPSILON)

    def test_mild_case_remains_directly_representable(self):
        result = evaluate_case(0.1, 2.0)
        self.assertEqual(result["state"], "PASS_DIRECT_STANDARD_FLUID_REPRESENTATION")
        self.assertEqual(result["naive_subtraction_zero_count"], 0)
        self.assertGreater(result["min_stable_1_plus_w"], 0.0)

    def test_global_audit_fails_closed_without_claim_promotion(self):
        receipt = build()
        self.assertEqual(
            receipt["state"],
            "BLOCKED_DIRECT_STANDARD_FLUID_DOUBLE_PRECISION_REGULARITY",
        )
        self.assertGreater(receipt["blocked_case_count"], 0)
        self.assertFalse(receipt["class_camb_unlock"])
        self.assertEqual(receipt["c08_resolution"], "NOT_RESOLVED")
        self.assertFalse(receipt["claim_allowed"])


if __name__ == "__main__":
    unittest.main()
