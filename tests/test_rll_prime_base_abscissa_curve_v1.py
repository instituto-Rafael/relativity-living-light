from __future__ import annotations

import unittest

from tools import rll_prime_base_abscissa_curve_v1 as curve


class RLLPrimeBaseAbscissaCurveV1Tests(unittest.TestCase):
    def test_selected_prime_carriers_have_exact_periods(self) -> None:
        receipt = curve.base_prime_receipt()
        self.assertEqual(receipt["selected_primes"], (2, 3, 5, 7, 11, 13, 37))
        self.assertEqual(receipt["all_prime_crt_period"], 1111110)
        self.assertEqual(receipt["all_prime_product"], 1111110)
        self.assertEqual(receipt["base10_unit_primes"], (3, 7, 11, 13, 37))
        self.assertEqual(receipt["base10_unit_prime_period"], 111111)
        self.assertEqual(receipt["repunit6"], 111111)
        self.assertTrue(receipt["exact_relations"]["base10_unit_period_equals_repunit6"])
        self.assertTrue(receipt["exact_relations"]["all_prime_period_equals_10_times_repunit6"])

    def test_base_dependent_nonunits_are_explicit(self) -> None:
        receipt = curve.base_prime_receipt()
        self.assertEqual(receipt["exact_relations"]["base10_excluded_nonunits"], (2, 5))
        self.assertEqual(receipt["exact_relations"]["base7_excluded_nonunits"], (7,))
        self.assertEqual(receipt["base7_unit_primes"], (2, 3, 5, 11, 13, 37))
        self.assertEqual(receipt["base7_unit_prime_period"], 158730)

    def test_zero_abscissa_has_real_zero_residue_coordinates(self) -> None:
        point = curve.abscissa_point(0, (3, 7, 11, 13))
        self.assertEqual(point["x"], 0)
        self.assertEqual(point["residue_signature"], (0, 0, 0, 0))
        for axis in point["axes"].values():
            self.assertEqual(axis["residue"], 0)
            self.assertEqual(axis["zero_state"], "RESIDUE_ZERO")
            self.assertAlmostEqual(axis["cos"], 1.0)
            self.assertAlmostEqual(axis["sin"], 0.0)

    def test_abscissa_is_not_erased_when_one_or_more_axes_hit_zero(self) -> None:
        point = curve.abscissa_point(21, (3, 7, 11, 13))
        self.assertEqual(point["x"], 21)
        self.assertEqual(point["axes"]["3"]["zero_state"], "RESIDUE_ZERO")
        self.assertEqual(point["axes"]["7"]["zero_state"], "RESIDUE_ZERO")
        self.assertEqual(point["axes"]["11"]["residue"], 10)
        self.assertEqual(point["axes"]["13"]["residue"], 8)

    def test_residue_signature_repeats_at_declared_joint_period(self) -> None:
        moduli = (3, 7, 11, 13, 37)
        period = curve.prime_carrier_period(moduli)
        self.assertEqual(period, 111111)
        for n in (0, 1, 7, 21, 42, 999, 1001):
            self.assertEqual(
                curve.abscissa_point(n, moduli)["residue_signature"],
                curve.abscissa_point(n + period, moduli)["residue_signature"],
            )

    def test_curve_preserves_explicit_integer_abscissa(self) -> None:
        points = curve.abscissa_curve(0, 5, (3, 7))
        self.assertEqual(tuple(p["x"] for p in points), (0, 1, 2, 3, 4))
        self.assertEqual(len(points), 5)
        self.assertEqual(points[0]["joint_period"], 21)
        self.assertFalse(curve.CLAIM_ALLOWED)


if __name__ == "__main__":
    unittest.main()
