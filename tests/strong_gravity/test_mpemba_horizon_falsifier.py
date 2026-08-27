from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest

MODULE_PATH = Path(__file__).resolve().parents[2] / "data" / "pipelines" / "strong_gravity" / "mpemba_horizon_falsifier.py"
SPEC = importlib.util.spec_from_file_location("mpemba_horizon_falsifier", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class MpembaHorizonFalsifierTests(unittest.TestCase):
    def test_hawking_temperature_inverse_mass(self):
        mass = 10.0 * MODULE.SOLAR_MASS_KG
        self.assertAlmostEqual(MODULE.hawking_temperature_k(2.0 * mass) / MODULE.hawking_temperature_k(mass), 0.5, places=12)

    def test_entropy_scales_as_mass_squared(self):
        mass = 10.0 * MODULE.SOLAR_MASS_KG
        self.assertAlmostEqual(MODULE.bekenstein_hawking_entropy_j_k(2.0 * mass) / MODULE.bekenstein_hawking_entropy_j_k(mass), 4.0, places=12)

    def test_heat_capacity_and_temperature_derivative_are_negative(self):
        mass = 10.0 * MODULE.SOLAR_MASS_KG
        self.assertLess(MODULE.schwarzschild_heat_capacity_j_k(mass), 0.0)
        self.assertLess(MODULE.d_hawking_temperature_d_mass_k_kg(mass), 0.0)

    def test_static_observer_rejects_horizon_and_interior(self):
        mass = 10.0 * MODULE.SOLAR_MASS_KG
        rs = MODULE.schwarzschild_radius_m(mass)
        with self.assertRaises(ValueError):
            MODULE.static_redshift_factor(mass, rs)
        with self.assertRaises(ValueError):
            MODULE.static_redshift_factor(mass, 0.99 * rs)

    def test_tolman_temperature_increases_for_static_observer_near_horizon(self):
        mass = 10.0 * MODULE.SOLAR_MASS_KG
        rs = MODULE.schwarzschild_radius_m(mass)
        self.assertGreater(MODULE.tolman_local_temperature_k(1.0, mass, 1.01 * rs), MODULE.tolman_local_temperature_k(1.0, mass, 10.0 * rs))

    def test_mpemba_witness_requires_crossing_and_faster_first_passage(self):
        result = MODULE.mpemba_witness([0.0, 1.0, 2.0, 3.0, 4.0], [1.0, 0.50, 0.18, 0.06, 0.02], [0.70, 0.55, 0.40, 0.20, 0.05], 0.10)
        self.assertTrue(result.initial_farther)
        self.assertTrue(result.crossing_observed)
        self.assertLess(result.tau_far, result.tau_near)
        self.assertTrue(result.witness)

    def test_no_crossing_means_no_witness(self):
        result = MODULE.mpemba_witness([0.0, 1.0, 2.0], [1.0, 0.8, 0.6], [0.5, 0.4, 0.3], 0.2)
        self.assertFalse(result.crossing_observed)
        self.assertFalse(result.witness)

    def test_slow_mode_probe(self):
        self.assertLess(MODULE.slow_mode_suppression_ratio(0.1, 1.0), 1.0)

    def test_astrophysical_claims_remain_token_vazio(self):
        states = {item["id"]: item["state"] for item in MODULE.claim_ledger()}
        self.assertEqual(states["BH-MP-06"], MODULE.TOKEN_VAZIO)
        self.assertEqual(states["BH-MP-08"], MODULE.TOKEN_VAZIO)

    def test_inside_horizon_jet_claim_is_falsified(self):
        states = {item["id"]: item["state"] for item in MODULE.claim_ledger()}
        self.assertEqual(states["BH-MP-04"], "FALSIFIED_BY_CAUSAL_BOUNDARY")

    def test_baseline_is_bounded_not_global_claim(self):
        result = MODULE.baseline()
        self.assertEqual(result["decision"], "BOUNDED_PASS")
        self.assertFalse(result["global_scientific_claim_allowed"])
        self.assertFalse(result["synthetic_relaxation"]["astrophysical_evidence"])

    def test_invalid_relaxation_axis_rejected(self):
        with self.assertRaises(ValueError):
            MODULE.mpemba_witness([0.0, 1.0, 1.0], [1.0, 0.5, 0.1], [0.8, 0.4, 0.2], 0.2)


if __name__ == "__main__":
    unittest.main()
