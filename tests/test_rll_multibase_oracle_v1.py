"""Scoped properties of RLL multibase arithmetic, not physical evidence."""
import unittest
from fractions import Fraction
from math import gcd
from tools.rll_multibase_oracle_v1 import (
    numeral_value, complement_pair, lift_additive, near_anchor_product,
    nine_via_ten, multiply_by_base_minus_one, phase_fraction,
    intersection_count, supergrid, compatible_crt, digital_root_decimal, is_prime
)


class MultibaseRegression(unittest.TestCase):
    def test_numeral_50_across_7_10_14(self):
        self.assertEqual([numeral_value('50', b) for b in (7, 10, 14)], [35, 50, 70])

    def test_numeral_10_base_7_is_seven(self):
        self.assertEqual(numeral_value('10', 7), 7)

    def test_invalid_digit_in_base_seven(self):
        with self.assertRaises(ValueError): numeral_value('70', 7)

    def test_70_plus_30(self):
        self.assertEqual(complement_pair(7, 10, 10), (70, 30, 100))

    def test_complement_properties_all_bases(self):
        for b in range(2, 31):
            for x in range(b + 1):
                for k in (1, 3, 10):
                    a, c, t = complement_pair(x, b, k)
                    self.assertEqual(a + c, t)

    def test_additive_lift_7_to_70(self):
        self.assertEqual(lift_additive(7, 10, 10), 70)

    def test_lift_well_defined_on_equivalent_reps(self):
        for b in range(2, 22):
            for k in (1, 2, 10):
                for a in range(-b, 2*b):
                    self.assertEqual(lift_additive(a, b, k), lift_additive(a + 17*b, b, k))

    def test_lift_additive_homomorphism(self):
        for b in (7, 10, 14):
            for k in (2, 10):
                for a in range(b):
                    for c in range(b):
                        target = k * b
                        self.assertEqual(lift_additive(a+c, b, k),
                                         (lift_additive(a,b,k) + lift_additive(c,b,k)) % target)

    def test_lift_injective_in_additive_classes(self):
        for b in range(2, 51):
            self.assertEqual(len({lift_additive(a,b,10) for a in range(b)}), b)

    def test_lift_not_multiplicative(self):
        self.assertNotEqual(lift_additive(2*3, 10, 10),
                            lift_additive(2,10,10) * lift_additive(3,10,10) % 100)

    def test_nine_via_ten(self):
        for n in range(-500, 501): self.assertEqual(nine_via_ten(n), 9*n)

    def test_general_base_minus_one(self):
        for b in range(2,31):
            for n in range(-10,11): self.assertEqual(multiply_by_base_minus_one(n,b), (b-1)*n)

    def test_signed_virtual_area_seven_thirteen(self):
        self.assertEqual(near_anchor_product(7,13,10),100-9)

    def test_signed_virtual_area_thirteen_seventeen(self):
        self.assertEqual(near_anchor_product(13,17,15),225-4)

    def test_anchor_product_exhaustive_small_grid(self):
        for b in (7,10,14):
            for x in range(-20,21):
                for y in range(-20,21): self.assertEqual(near_anchor_product(x,y,b), x*y)

    def test_common_grid_350(self):
        self.assertEqual(supergrid(7, 10, 14, 35, 50, 70),350)

    def test_cyclic_overlap_counts(self):
        self.assertEqual([(n,m,intersection_count(n,m)) for n,m in [(7,14),(7,50),(35,50),(50,70)]],
                         [(7,14,7),(7,50,1),(35,50,5),(50,70,10)])

    def test_phase_intersections_by_rational_sets(self):
        for n,m in ((7,14),(7,50),(35,50),(50,70)):
            set1={phase_fraction(i,n) for i in range(n)}
            set2={phase_fraction(i,m) for i in range(m)}
            self.assertEqual(len(set1 & set2),gcd(n,m))

    def test_no_common_nonzero_phase_for_7_35_50_70(self):
        shared=set.intersection(*({phase_fraction(i,n) for i in range(n)}
                                  for n in (7,35,50,70)))
        self.assertEqual(shared,{Fraction(0,1)})

    def test_crt_mod14_mod10_parity(self):
        outcomes={(n%14,n%10) for n in range(70)}
        self.assertEqual(len(outcomes),70)
        for a in range(14):
            for b in range(10): self.assertEqual((a,b) in outcomes,compatible_crt(a,b))

    def test_decimal_digital_roots_not_equal(self):
        self.assertEqual([digital_root_decimal(n) for n in (7,35,50,70)],[7,8,5,7])

    def test_primality_does_not_transfer_to_70(self):
        self.assertTrue(is_prime(7)); self.assertFalse(is_prime(70))

    def test_primes_thirteen_seventeen_exact(self):
        self.assertTrue(is_prime(13)); self.assertTrue(is_prime(17))
        self.assertEqual(near_anchor_product(13,17,15),221)

    def test_invalid_modulus(self):
        with self.assertRaises(ValueError): lift_additive(1, 1, 10)


if __name__=='__main__': unittest.main()
