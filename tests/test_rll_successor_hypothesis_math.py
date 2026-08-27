import math
import unittest

from tools.rll_successor_hypothesis_math import (
    A_CROSS,
    S_RLL,
    h03_dw_dz,
    h03_w_eff,
    h51_cpl_constraint_residual,
    h51_to_cpl,
    h51_w,
    rll_null_shape_identifiable,
    rll_superposition_term,
)


class RllSuccessorHypothesisMathTests(unittest.TestCase):
    def test_structural_constant_square_is_three_quarters(self):
        self.assertAlmostEqual(3.0 / 4.0, A_CROSS, places=15)
        self.assertAlmostEqual(math.sqrt(3.0) / 2.0, S_RLL, places=15)

    def test_h03_effective_eos_is_phantom_for_observed_nonnegative_redshift(self):
        self.assertLess(h03_w_eff(0.0), -1.0)
        self.assertLess(h03_w_eff(0.5), -1.0)
        self.assertLess(h03_w_eff(2.33), -1.0)
        self.assertLess(h03_dw_dz(), 0.0)

    def test_h03_effective_eos_has_no_finite_phantom_crossing_for_z_ge_zero(self):
        for z in (0.0, 0.1, 0.33, 0.5, 1.0, 2.33, 5.0):
            self.assertNotAlmostEqual(h03_w_eff(z), -1.0, places=12)

    def test_h51_crosses_minus_one_exactly_at_three_quarters(self):
        for amplitude in (-2.0, -0.5, 0.5, 2.0):
            self.assertAlmostEqual(-1.0, h51_w(A_CROSS, amplitude), places=15)

    def test_h51_has_exact_cpl_line(self):
        for amplitude in (-2.0, -0.25, 0.25, 2.0):
            w0, wa = h51_to_cpl(amplitude)
            self.assertAlmostEqual(0.0, h51_cpl_constraint_residual(w0, wa), places=15)
            for a in (0.4, 0.75, 1.0):
                cpl = w0 + wa * (1.0 - a)
                self.assertAlmostEqual(h51_w(a, amplitude), cpl, places=15)

    def test_rll_null_removes_shape_parameters_exactly(self):
        values = {
            rll_superposition_term(0.8, 0.0, zt, wt)
            for zt, wt in ((0.2, 0.1), (1.0, 0.5), (6.0, 0.8), (9.0, 1.8))
        }
        self.assertEqual({0.0}, values)
        self.assertFalse(rll_null_shape_identifiable(0.0))
        self.assertTrue(rll_null_shape_identifiable(1.0e-6))


if __name__ == "__main__":
    unittest.main()
