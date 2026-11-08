#!/usr/bin/env python3
"""RLL exact multibase complementary arithmetic reference; stdlib and no floats."""
import json
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
CONTRACT = HERE / "data/contracts/rll_multibase_complement_falsification.v1.json"

def digits(n, base):
    if n < 0 or base < 2:
        raise ValueError("nonnegative integer and base >=2 required")
    out = []
    while True:
        n, rem = divmod(n, base)
        out.append(rem)
        if not n:
            return tuple(reversed(out))

def value_from_digits(digits_tuple, base):
    if base < 2 or not digits_tuple:
        raise ValueError("invalid digits")
    n = 0
    for d in digits_tuple:
        if not isinstance(d, int) or not 0 <= d < base:
            raise ValueError("digit outside base")
        n = n * base + d
    return n

def angle_fraction(n, base):
    """Exact turn fraction, not physical angular momentum or trig result."""
    if base < 2:
        raise ValueError("invalid base")
    return n % base, base

def compensating_product(a, b, loan):
    return (a + loan) * b - loan * b

class BaseComplementChecks(unittest.TestCase):
    def test_7_in_base7(self):
        self.assertEqual(digits(7, 7), (1, 0))
    def test_07_invalid_in_base7(self):
        with self.assertRaises(ValueError):
            value_from_digits((0, 7), 7)
    def test_zero_is_known_remainder(self):
        self.assertEqual(divmod(7,7), (1,0))
        self.assertNotEqual(divmod(7,7), (0,0))
    def test_remainder_alone_not_injective(self):
        self.assertEqual(7%7,14%7)
        self.assertNotEqual(7,14)
    def test_scale_and_complement(self):
        self.assertEqual(7*10+3*10, 100)
    def test_different_types_scaled_vs_represented(self):
        self.assertEqual(digits(7,100), (7,))
        self.assertEqual(digits(70,100), (70,))
        self.assertNotEqual(7,70)
    def test_base100_carry(self):
        self.assertEqual(digits(70+30,100),(1,0))
    def test_base100_07(self):
        self.assertEqual(value_from_digits((0,7),100),7)
        self.assertEqual(value_from_digits((7,0),100),700)
    def test_product_representations(self):
        self.assertEqual(7*70,490)
        self.assertEqual(digits(490,100),(4,90))
        self.assertEqual(digits(490,7),(1,3,0,0))
    def test_complement_multiplication(self):
        self.assertEqual(compensating_product(7,70,3),490)
    def test_signed_polynomial_area(self):
        a,b,c,d = 7,70,3,30
        self.assertEqual((a+c)*(b+d)-a*d-c*b-c*d,a*b)
    def test_integer_sweep(self):
        for b in (7,10,14,100):
            for n in range(0,1001):
                self.assertEqual(value_from_digits(digits(n,b),b),n)
                self.assertEqual(b*(n//b)+n%b,n)
    def test_complement_sweep(self):
        for a in range(-25,26):
            for b in (-10,0,1,7,70):
                for loan in (-30,-3,0,3,30):
                    self.assertEqual(compensating_product(a,b,loan),a*b)
    def test_angular_not_universal(self):
        nums=(7,35,50,70)
        actual={b:tuple(n%b for n in nums) for b in (7,10,14)}
        self.assertEqual(actual,{7:(0,0,1,0),10:(7,5,0,0),14:(7,7,8,0)})
    def test_angle_not_physical_L(self):
        # Same angular residue cannot fix r×p: Lz=1 vs 2.
        r=(1,0,0)
        p1=(0,1,0)
        p2=(0,2,0)
        self.assertNotEqual(r[0]*p1[1]-r[1]*p1[0],
                            r[0]*p2[1]-r[1]*p2[0])
    def test_representation_keeps_prime_property(self):
        for base in (7,10,14,100):
            self.assertEqual(value_from_digits(digits(7,base),base),7)
        self.assertTrue(all(7%d for d in range(2,7)))
        self.assertFalse(all(70%d for d in range(2,70)))
    def test_repetend_base10(self):
        r=1; observed=[]
        for _ in range(6):
            r*=10;digit,r=divmod(r,7);observed.append(digit)
        self.assertEqual(observed,[1,4,2,8,5,7])
        self.assertEqual(r,1)
    def test_one_seventh_base7_terminates(self):
        self.assertEqual(divmod(7,7),(1,0))
    def test_digit_sum_congruence(self):
        for b in (7,10,14):
            for n in range(0,501):
                self.assertEqual(sum(digits(n,b))%(b-1),n%(b-1))
    def test_contract_no_physical_promotion(self):
        obj=json.loads(CONTRACT.read_text(encoding="utf-8"))
        self.assertFalse(obj["claim_allowed"])
        self.assertFalse(obj["merge_allowed"])
        self.assertEqual(len(obj["propositions"]),20)
        self.assertEqual(len({x["id"] for x in obj["propositions"]}),20)
        self.assertTrue(all(x["claim_allowed"] is False for x in obj["propositions"]))
        self.assertEqual(obj["geometry_physical_claim"],
                         "TOKEN_VAZIO_UNLESS_DIMENSIONAL_MODEL")

if __name__ == "__main__":
    unittest.main(verbosity=2)
