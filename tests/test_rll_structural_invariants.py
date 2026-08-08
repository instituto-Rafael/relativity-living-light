from __future__ import annotations

import math
import unittest

from rll_core.structural_invariants import (
    RLLParameters,
    dh_over_rd,
    dm_over_rd,
    dv_over_rd,
    e2,
    e2_prime,
    finite_difference_first,
    jerk_j,
    kretschmann_bar,
    linspace,
    ricci_bar,
    scan_invariants,
    transition_f,
    transition_f_prime,
)


class StructuralInvariantTests(unittest.TestCase):
    def setUp(self) -> None:
        self.p = RLLParameters()

    def test_normalization(self) -> None:
        self.assertAlmostEqual(e2(0.0, self.p), 1.0, places=14)

    def test_null_limit_is_lcdm(self) -> None:
        p = self.p.null_limit()
        for z in (0.0, 0.1, 1.0, 2.4, 5.0):
            u = 1.0 + z
            expected = p.Om * u**3 + p.Or * u**4 + 1.0 - p.Om - p.Or
            self.assertAlmostEqual(e2(z, p), expected, places=13)

    def test_logistic_derivative(self) -> None:
        for z in (0.0, 0.5, 1.0, 2.0):
            numeric = finite_difference_first(lambda x: transition_f(x, self.p), z)
            self.assertAlmostEqual(transition_f_prime(z, self.p), numeric, places=8)

    def test_e2_derivative(self) -> None:
        for z in (0.0, 0.5, 1.0, 2.0):
            numeric = finite_difference_first(lambda x: e2(x, self.p), z)
            self.assertAlmostEqual(e2_prime(z, self.p), numeric, places=7)

    def test_lcdm_jerk_is_one_without_radiation(self) -> None:
        p = RLLParameters(Or=0.0, Os0=0.0)
        for z in (0.0, 0.5, 1.0, 3.0):
            self.assertAlmostEqual(jerk_j(z, p), 1.0, places=12)

    def test_flat_flrw_curvature_scalars_are_finite(self) -> None:
        for z in (0.0, 1.0, 2.4):
            self.assertTrue(math.isfinite(ricci_bar(z, self.p)))
            self.assertGreater(kretschmann_bar(z, self.p), 0.0)

    def test_distance_relations(self) -> None:
        z = 0.8
        self.assertGreater(dh_over_rd(z, self.p), 0.0)
        self.assertGreater(dm_over_rd(z, self.p), 0.0)
        self.assertGreater(dv_over_rd(z, self.p), 0.0)
        self.assertEqual(dv_over_rd(0.0, self.p), 0.0)

    def test_scan_passes(self) -> None:
        result = scan_invariants(self.p, linspace(0.0, 3.0, 301))
        self.assertTrue(result["passed"], result)

    def test_invalid_width(self) -> None:
        with self.assertRaises(ValueError):
            transition_f(0.0, RLLParameters(wt=0.0))


if __name__ == "__main__":
    unittest.main()
