from __future__ import annotations

import math
import unittest
from fractions import Fraction

from tools import rll_geometric_dispersion_false_positive_gate as gate


class GeometricDispersionFalsePositiveGateTests(unittest.TestCase):
    def test_sample_population_and_mean_variance_are_distinct(self) -> None:
        xs = [1.0, 2.0, 3.0]
        self.assertAlmostEqual(gate.population_variance(xs), 2.0 / 3.0)
        self.assertAlmostEqual(gate.sample_variance(xs), 1.0)
        self.assertAlmostEqual(gate.variance_of_sample_mean(xs), 1.0 / 3.0)

    def test_independent_difference_of_means_variance(self) -> None:
        value = gate.variance_of_independent_mean_difference(
            [1.0, 2.0, 3.0], [2.0, 3.0, 4.0]
        )
        self.assertAlmostEqual(value, 2.0 / 3.0)

    def test_ols_line_is_diagnostic_and_exact_on_linear_fixture(self) -> None:
        intercept, slope = gate.ols_line([0, 1, 2], [1, 3, 5])
        self.assertAlmostEqual(intercept, 1.0)
        self.assertAlmostEqual(slope, 2.0)

    def test_pbip_discriminant_classifies_cut_tangent_and_miss(self) -> None:
        self.assertAlmostEqual(gate.pbip_discriminant(5.0, 3.0), 64.0)
        self.assertEqual(gate.pbip_intersection_class(5.0, 3.0), "TWO_REAL_INTERSECTIONS")
        self.assertEqual(gate.pbip_intersection_class(5.0, 5.0), "TANGENCY")
        self.assertEqual(gate.pbip_intersection_class(5.0, 6.0), "NO_REAL_INTERSECTION")

    def test_isosceles_30_degree_gate_keeps_two_height_namespaces_distinct(self) -> None:
        base, height = gate.isosceles_gate(1.0, 30.0)
        self.assertAlmostEqual(base, 1.0)
        self.assertAlmostEqual(height, math.sqrt(3.0) / 2.0)
        self.assertNotAlmostEqual(height, 3.0 / 2.0)

    def test_leg_difference_identity_preserves_negative_cross_term_information(self) -> None:
        lhs, rhs, delta = gate.right_leg_difference_identity(3.0, 4.0)
        self.assertAlmostEqual(lhs, rhs)
        self.assertAlmostEqual(lhs, 25.0)
        self.assertAlmostEqual(delta, 1.0)

    def test_canonical_spiral_contracts_but_three_over_two_control_expands(self) -> None:
        self.assertLess(gate.canonical_spiral_point(4)[2], gate.canonical_spiral_point(0)[2])
        self.assertGreater(gate.adversarial_three_over_two_radius(4), 1.0)
        self.assertAlmostEqual(gate.SQRT3_OVER_2, math.sqrt(3.0) / 2.0)
        self.assertAlmostEqual(gate.THREE_OVER_2, 1.5)
        self.assertAlmostEqual(gate.SQRT_THREE_OVER_TWO, math.sqrt(1.5))
        self.assertNotAlmostEqual(gate.SQRT3_OVER_2, gate.THREE_OVER_2)
        self.assertNotAlmostEqual(gate.SQRT3_OVER_2, gate.SQRT_THREE_OVER_TWO)

    def test_modular_family_has_exact_1050_joint_period(self) -> None:
        self.assertEqual(gate.JOINT_MOD_PERIOD, 1050)
        for n in (0, 1, 7, 14, 77, 999, 1050, 14000):
            self.assertEqual(gate.modular_signature(n), gate.modular_signature(n + 1050))

    def test_ratio_encoding_does_not_create_a_missing_eleven(self) -> None:
        receipt = gate.ratio_reduction_receipt()
        self.assertEqual(gate.reduced_ratio(77, 33), Fraction(7, 3))
        self.assertEqual(gate.reduced_ratio(777, 333), Fraction(7, 3))
        self.assertEqual(receipt["gcd_77_33"], 11)
        self.assertEqual(receipt["gcd_777_333"], 111)
        self.assertTrue(receipt["representation_invariant"])

    def test_void_is_not_numeric_zero(self) -> None:
        self.assertIsNone(gate.square_area(None))
        self.assertEqual(gate.square_area(0.0), 0.0)

    def test_log_log_999_requires_explicit_base_and_base_changes_value(self) -> None:
        natural = gate.nested_log_999(math.e)
        decimal = gate.nested_log_999(10.0)
        self.assertAlmostEqual(natural, 1.932499886168131, places=12)
        self.assertAlmostEqual(decimal, 0.4770583481420184, places=12)
        self.assertNotAlmostEqual(natural, decimal)
        with self.assertRaises(ValueError):
            gate.nested_log_999(1.0)

    def test_contract_is_fail_closed_for_physical_claims(self) -> None:
        receipt = gate.contract_receipt()
        self.assertFalse(receipt["claim_allowed"])
        self.assertEqual(receipt["physical_mapping_state"], "TOKEN_VAZIO_PHYSICAL_MAPPING")
        self.assertEqual(receipt["log_base_state"], "TOKEN_VAZIO_LOG_BASE")
        self.assertEqual(receipt["joint_mod_period"], 1050)


if __name__ == "__main__":
    unittest.main()
