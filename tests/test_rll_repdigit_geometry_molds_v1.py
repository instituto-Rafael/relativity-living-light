from __future__ import annotations

import math
import unittest
from fractions import Fraction

from tools import rll_repdigit_geometry_molds_v1 as molds


class RLLRepdigitGeometryMoldsV1Tests(unittest.TestCase):
    def test_requested_seven_over_three_values(self) -> None:
        rows = molds.seven_over_three_family(3)
        self.assertEqual(rows[0]["numerator"], 7)
        self.assertEqual(rows[0]["integer_quotient_abs_divisor"], 2)
        self.assertEqual(rows[0]["remainder_abs_divisor"], 1)
        self.assertEqual(rows[1]["numerator"], 77)
        self.assertEqual(rows[1]["integer_quotient_abs_divisor"], 25)
        self.assertEqual(rows[1]["remainder_abs_divisor"], 2)
        self.assertEqual(rows[2]["numerator"], 777)
        self.assertEqual(rows[2]["integer_quotient_abs_divisor"], 259)
        self.assertEqual(rows[2]["remainder_abs_divisor"], 0)
        self.assertEqual(molds.seven_repdigit_mod3_orbit(), (1, 2, 0))

    def test_requested_three_over_seven_values(self) -> None:
        rows = molds.three_over_seven_family(3)
        self.assertEqual(rows[0]["numerator"], 3)
        self.assertEqual(rows[0]["integer_quotient_abs_divisor"], 0)
        self.assertEqual(rows[0]["remainder_abs_divisor"], 3)
        self.assertEqual(rows[1]["numerator"], 33)
        self.assertEqual(rows[1]["integer_quotient_abs_divisor"], 4)
        self.assertEqual(rows[1]["remainder_abs_divisor"], 5)
        self.assertEqual(rows[2]["numerator"], 333)
        self.assertEqual(rows[2]["integer_quotient_abs_divisor"], 47)
        self.assertEqual(rows[2]["remainder_abs_divisor"], 4)

    def test_three_repdigit_mod7_is_six_cycle_with_fixed_residue_two_outside(self) -> None:
        orbit = molds.three_repdigit_mod7_orbit()
        self.assertEqual(orbit, (3, 5, 4, 1, 6, 0))
        self.assertEqual(len(set(orbit)), 6)
        self.assertNotIn(2, orbit)
        self.assertEqual(molds.mod7_repdigit_transition(2), 2)
        for a, b in zip(orbit, orbit[1:] + orbit[:1]):
            self.assertEqual(molds.mod7_repdigit_transition(a), b)

    def test_first_six_integer_quotients_expose_prefix_cycles(self) -> None:
        seven_q = tuple(r["integer_quotient_abs_divisor"] for r in molds.seven_over_three_family(6))
        three_q = tuple(r["integer_quotient_abs_divisor"] for r in molds.three_over_seven_family(6))
        self.assertEqual(seven_q, (2, 25, 259, 2592, 25925, 259259))
        self.assertEqual(three_q, (0, 4, 47, 476, 4761, 47619))

    def test_closed_forms_for_repdigit_division(self) -> None:
        for n in range(1, 7):
            seven = Fraction(molds.repdigit(7, n), 3)
            three = Fraction(molds.repdigit(3, n), 7)
            self.assertEqual(seven, Fraction(7 * (10**n - 1), 27))
            self.assertEqual(three, Fraction(10**n - 1, 21))

    def test_factor_molds_are_exact(self) -> None:
        fm = molds.factor_molds()
        self.assertEqual(fm[18], (2, 3, 3))
        self.assertEqual(fm[21], (3, 7))
        self.assertEqual(fm[42], (2, 3, 7))
        self.assertEqual(fm["1001=7*11*13"], 1001)

    def test_regular_polygon_molds_cover_requested_integer_family(self) -> None:
        family = molds.integer_polygon_molds()
        self.assertEqual(set(family), {11, 18, 13, 21, 42})
        for n, mold in family.items():
            self.assertAlmostEqual(mold["central_angle"], 2.0 * math.pi / n)
            self.assertAlmostEqual(mold["half_central_angle"], math.pi / n)
            self.assertAlmostEqual(mold["sector_area"], math.pi / n)

    def test_21_to_42_is_exact_half_step_refinement(self) -> None:
        m21 = molds.regular_polygon_mold(21)
        m42 = molds.regular_polygon_mold(42)
        self.assertAlmostEqual(m42["central_angle"], m21["central_angle"] / 2.0)
        self.assertAlmostEqual(m42["central_angle"], m21["half_central_angle"])

    def test_pentagram_ratio_is_phi(self) -> None:
        p = molds.pentagram_mold()
        self.assertTrue(p["star_5_2"]["connected_single_cycle"])
        self.assertAlmostEqual(p["diagonal_over_side"], molds.PHI)
        self.assertAlmostEqual(2.0 * molds.PHI - 1.0, math.sqrt(5.0))

    def test_dodeca_keeps_base_and_dodecagram_distinct(self) -> None:
        d = molds.dodeca_mold()
        base = d["base_12_gon"]
        star = d["dodecagram_12_5"]
        self.assertAlmostEqual(base["central_angle"], math.pi / 6.0)
        self.assertAlmostEqual(base["half_central_angle"], math.pi / 12.0)
        self.assertEqual(star["step"], 5)
        self.assertTrue(star["connected_single_cycle"])
        self.assertAlmostEqual(star["step_angle"], 5.0 * math.pi / 6.0)
        self.assertNotAlmostEqual(star["half_chord_angle"], base["half_central_angle"])

    def test_area_root_molds_match_existing_crown_identities(self) -> None:
        a = molds.area_root_molds()
        self.assertAlmostEqual(a["s5_squared"], math.pi / 5.0)
        self.assertAlmostEqual(a["s12_squared"], math.pi / 12.0)
        self.assertAlmostEqual(a["s5_over_s12"], math.sqrt(12.0 / 5.0))
        self.assertAlmostEqual(a["crown_bridge"], math.sqrt(5.0) / 2.0)
        self.assertAlmostEqual(a["pentagon_half_central_angle"], math.pi / 5.0)
        self.assertAlmostEqual(a["dodecagon_half_central_angle"], math.pi / 12.0)
        self.assertEqual(a["physical_role"], "TOKEN_VAZIO_PHYSICAL_ROLE")

    def test_sqrt5_over_pi_is_numeric_scalar_only(self) -> None:
        self.assertAlmostEqual(molds.SQRT5_OVER_PI, math.sqrt(5.0) / math.pi)
        self.assertFalse(molds.CLAIM_ALLOWED)


if __name__ == "__main__":
    unittest.main()
