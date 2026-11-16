from __future__ import annotations

import math
import unittest
from fractions import Fraction

from tools import rll_full_permutation_void_census_v1 as census


class FullPermutationVoidCensusTests(unittest.TestCase):
    def test_zero_is_not_empty_null_or_token_vazio(self) -> None:
        self.assertEqual(census.void_relation(census.VoidKind.NUMERIC_ZERO, census.VoidKind.NUMERIC_ZERO), "SAME_TYPED_STATE")
        self.assertEqual(census.void_relation(census.VoidKind.NUMERIC_ZERO, census.VoidKind.APPROX_ZERO), "APPROX_NEAR_NOT_EQUAL")
        self.assertEqual(census.void_relation(census.VoidKind.NUMERIC_ZERO, census.VoidKind.RESIDUE_ZERO), "CONTEXT_RELATED_NOT_IDENTICAL")
        for other in (
            census.VoidKind.EMPTY_SET,
            census.VoidKind.NULL_VALUE,
            census.VoidKind.TOKEN_VAZIO,
            census.VoidKind.UNDEFINED,
            census.VoidKind.NO_REAL_SOLUTION,
            census.VoidKind.MISSING_OBSERVATION,
        ):
            self.assertEqual(census.void_relation(census.VoidKind.NUMERIC_ZERO, other), "DISTINCT_OR_NOT_COMPARABLE")

    def test_digit_string_10_depends_on_base(self) -> None:
        self.assertEqual(census.positional_value_10(10), 10)
        self.assertEqual(census.positional_value_10(7), 7)

    def test_repdigit_divisions_and_orbits(self) -> None:
        self.assertEqual(census.repdigit_division(7, 1, 3)["fraction"], "7/3")
        self.assertEqual(census.repdigit_division(7, 2, 3)["q"], 25)
        self.assertEqual(census.repdigit_division(7, 3, 3)["q"], 259)
        self.assertEqual(census.repdigit_division(3, 1, 7)["fraction"], "3/7")
        self.assertEqual(census.repdigit_division(3, 2, 7)["q"], 4)
        self.assertEqual(census.repdigit_division(3, 3, 7)["q"], 47)
        self.assertEqual(census.repdigit_remainder_orbit(7, 3), [1, 2, 0])
        self.assertEqual(census.repdigit_remainder_orbit(3, 7), [3, 5, 4, 1, 6, 0])

    def test_exact_ratio_representation_invariance(self) -> None:
        self.assertEqual(Fraction(77, 33), Fraction(7, 3))
        self.assertEqual(Fraction(777, 333), Fraction(7, 3))

    def test_prime_composite_factor_invariants(self) -> None:
        inv = census.exact_invariants()
        self.assertEqual(inv["factor_1001"], 1001)
        self.assertEqual(inv["factor_21"], 21)
        self.assertEqual(inv["factor_42"], 42)
        self.assertEqual(inv["repunit6_factorization_check"], inv["repunit6"])

    def test_radical_identities(self) -> None:
        inv = census.exact_invariants()
        self.assertTrue(inv["sqrt_pi_over_pi_equals_inverse_sqrt_pi"])
        self.assertAlmostEqual(inv["sqrt_phi_pi_reciprocal_product"], 1.0)
        self.assertAlmostEqual(inv["sqrt_pi5_square"], math.pi / 5.0)
        self.assertAlmostEqual(inv["sqrt_pi12_square"], math.pi / 12.0)
        self.assertAlmostEqual(inv["crown_bridge"], math.sqrt(5.0) / 2.0)

    def test_bounded_permutation_grammar_is_exhaustive_within_declared_atoms(self) -> None:
        n = len(census.ATOMS)
        self.assertEqual(len(census.ordered_binary_permutations()), 4*n*(n-1))
        self.assertEqual(len(census.unary_permutations()), 3*n)

    def test_integer_mod_census_count(self) -> None:
        integer_atoms = [a for a in census.ATOMS if float(a.value).is_integer()]
        self.assertEqual(
            len(census.integer_mod_permutations()),
            len(integer_atoms) * len(census.MODULI),
        )
        self.assertEqual(census.MASTER_MOD_PERIOD, 900900)

    def test_geometry_molds_keep_polygon_and_star_step_distinct(self) -> None:
        pentagon = census.regular_mold(5, 1)
        pentagram = census.regular_mold(5, 2)
        dodecagon = census.regular_mold(12, 1)
        dodecagram = census.regular_mold(12, 5)
        self.assertNotEqual(pentagon["step_angle_rad"], pentagram["step_angle_rad"])
        self.assertNotEqual(dodecagon["step_angle_rad"], dodecagram["step_angle_rad"])
        self.assertEqual(pentagram["cycle_length"], 5)
        self.assertEqual(dodecagram["cycle_length"], 12)

    def test_near_is_not_equal(self) -> None:
        pairs = census.near_pairs(0.01)
        target = {
            tuple(sorted((p["a"], p["b"])))
            for p in pairs
        }
        self.assertIn(
            tuple(sorted(("sqrt5_over_pi", "sqrt_phi_over_sqrt_pi"))),
            target,
        )
        self.assertNotAlmostEqual(
            math.sqrt(5.0) / math.pi,
            math.sqrt(census.PHI / math.pi),
        )

    def test_receipt_remains_fail_closed(self) -> None:
        receipt = census.receipt()
        self.assertFalse(receipt["claim_allowed"])
        self.assertEqual(receipt["scope"], "bounded_current_thread_plus_source_anchors")
        self.assertEqual(receipt["void_state_count"], len(census.VoidKind))
        self.assertEqual(receipt["void_relation_count"], len(census.VoidKind) ** 2)


if __name__ == "__main__":
    unittest.main()
