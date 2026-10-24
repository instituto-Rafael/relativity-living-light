# RAFAELIA / RLL, 2026-10-24. Independent local fixtures.
# No external dependencies, physical-data assumptions, or upstream implementation.
import importlib.util
import math
from decimal import Decimal, localcontext
from pathlib import Path
import unittest

ORACLE = Path(__file__).resolve().parents[1] / "tools" / "rll_exact_quantized_orbit.py"
spec = importlib.util.spec_from_file_location("rll_exact_quantized_orbit", ORACLE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class TestExactQuantizedOrbit(unittest.TestCase):
    def test_boundary_fixtures(self):
        self.assertEqual(module.quantized_step(100, 2), 75)
        self.assertEqual(module.quantized_step(16, 4), 9)
        self.assertTrue(module.is_integer_boundary(100, 2))
        self.assertTrue(module.is_integer_boundary(16, 4))
        self.assertFalse(module.is_integer_boundary(100, 3))

    def test_topological_jump_of_one_integer(self):
        self.assertEqual(module.orbit_signature(100, 75)["cycles"], 25)
        self.assertEqual(module.orbit_signature(100, 75)["permutation_sign"], -1)
        self.assertEqual(module.orbit_signature(100, 74)["cycles"], 2)
        self.assertEqual(module.orbit_signature(100, 74)["permutation_sign"], 1)

    def test_no_mutation_of_numeric_meaning(self):
        self.assertEqual(module.quantized_step(100, 0), 100)
        self.assertEqual(module.orbit_signature(7, 7)["cycles"], 7)
        self.assertEqual(module.orbit_signature(7, 1)["permutation_sign"], 1)
        self.assertFalse(module.audit(100, 2)["claim_allowed"])

    def test_exact_integer_inequality_certificate(self):
        for base in (6, 7, 8, 13, 16, 100):
            for exponent in range(64):
                q = module.quantized_step(base, exponent)
                m, odd = divmod(exponent, 2)
                a = base * 3 ** m
                d = 4 ** m
                if odd:
                    self.assertLessEqual((2*d*q)**2, 3*a*a)
                    self.assertLess(3*a*a, (2*d*(q+1))**2)
                else:
                    self.assertLessEqual(q*d, a)
                    self.assertLess(a, (q+1)*d)

    def test_decimal_independent_odd_power_oracle(self):
        # Odd exponents irrational, so equality with an integer is impossible.
        with localcontext() as ctx:
            ctx.prec = 130
            alpha = Decimal(3).sqrt() / Decimal(2)
            for base in (6, 7, 8, 13, 16, 100):
                for exponent in range(1, 60, 2):
                    reference = int(Decimal(base) * alpha ** exponent)
                    self.assertEqual(module.quantized_step(base, exponent), reference)

    def test_float_near_integer_is_not_certificate(self):
        # nextafter models a representational perturbation at the exact boundary.
        lower = math.nextafter(75.0, -math.inf)
        self.assertEqual(math.floor(lower), 74)
        self.assertEqual(module.quantized_step(100, 2), 75)

    def test_invalid_inputs_fail_closed(self):
        for b, n in ((0, 1), (-1, 0), (6, -1)):
            with self.assertRaises(ValueError):
                module.quantized_step(b, n)
        with self.assertRaises(TypeError):
            module.quantized_step(True, 2)


if __name__ == "__main__":
    unittest.main()
