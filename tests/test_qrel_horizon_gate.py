"""Exact falsifiers for a conditional quantum-relative-entropy/area bridge."""
import unittest
from fractions import Fraction
from tools.qrel_horizon_gate import (
    gate_witness, null_contractions_vanish_1p1, null_flux_moment,
    symbolic_area_bridge,
)


class QrelHorizonGateTests(unittest.TestCase):
    def test_exact_bump_moment(self):
        # Independently integrated analytic polynomial: integral = 1/105.
        self.assertEqual(null_flux_moment((0, 0, 1, 2, 1)), Fraction(1, 105))

    def test_amplitude_and_length_scaling(self):
        # phi_A,L = A*u^2*(u+L)^2; F = A^2 * L^8 / 105.
        for length in (1, 2, 3):
            for amplitude in (1, 2, -3):
                coeffs = (0, 0, amplitude * length**2,
                          2 * amplitude * length, amplitude)
                self.assertEqual(null_flux_moment(coeffs, length),
                                 Fraction(amplitude**2 * length**8, 105))

    def test_area_is_conditional_and_alpha_over_pi_is_eight(self):
        flux = Fraction(1, 105)
        no_area = symbolic_area_bridge(flux, coherent_state=True)
        self.assertIsNone(no_area["area_over_pi"])
        self.assertIsNone(no_area["alpha_over_pi"])
        with_area = symbolic_area_bridge(flux, coherent_state=True,
                                         assume_bh_area_law=True)
        self.assertEqual(with_area["s_rel_over_pi"], Fraction(2, 105))
        self.assertEqual(with_area["area_over_pi"], Fraction(8, 105))
        self.assertEqual(with_area["alpha_over_pi"], Fraction(8))
        self.assertFalse(with_area["physical_claim_allowed"])

    def test_zero_flux_does_not_infer_coupling(self):
        zero = symbolic_area_bridge(0, coherent_state=True,
                                    assume_bh_area_law=True)
        self.assertEqual(zero["s_rel_over_pi"], 0)
        self.assertIsNone(zero["alpha_over_pi"])

    def test_reject_noncoherent_and_negative_flux(self):
        with self.assertRaises(ValueError):
            symbolic_area_bridge(Fraction(1, 105), assume_bh_area_law=True)
        with self.assertRaises(ValueError):
            symbolic_area_bridge(-1, coherent_state=True)

    def test_reject_float_bad_endpoints_bad_domain(self):
        with self.assertRaises(TypeError):
            null_flux_moment((0, 0, 1.0, 2, 1))
        with self.assertRaises(ValueError):
            null_flux_moment((0, 1), length=1)
        with self.assertRaises(ValueError):
            null_flux_moment((0, 0, 1, 2, 1), length=-1)
        with self.assertRaises(ValueError):
            null_flux_moment(tuple(range(19)), length=1)

    def test_null_contraction_has_metric_only_kernel_in_1p1(self):
        for scalar in (-7, 0, Fraction(1, 3)):
            self.assertTrue(null_contractions_vanish_1p1(-scalar, 0, scalar))
        self.assertFalse(null_contractions_vanish_1p1(-1, 1, 1))
        self.assertFalse(null_contractions_vanish_1p1(-1, 0, 2))

    def test_cannot_promote_scientific_claim(self):
        r = gate_witness()
        self.assertEqual(r["flux_exact"], "1/105")
        self.assertEqual(r["alpha_over_pi_exact"], "8")
        self.assertFalse(r["modular_theory_proven"])
        self.assertFalse(r["four_dimensional_gravity_derived"])
        self.assertEqual(r["rll_deviation_observed"], "TOKEN_VAZIO")
        self.assertFalse(r["claim_allowed"])

    def test_independent_midpoint_flux_quadrature(self):
        # Independently integrated midpoint quadrature, not exact moment code.
        n = 20_000
        step = 1.0 / n
        value = 0.0
        for k in range(n):
            u = -1.0 + (k + 0.5) * step
            deriv = 4.0 * u**3 + 6.0 * u**2 + 2.0 * u
            value += (-u) * deriv**2 * step
        self.assertLess(abs(value - 1.0 / 105.0), 1e-8)


if __name__ == "__main__":
    unittest.main()
