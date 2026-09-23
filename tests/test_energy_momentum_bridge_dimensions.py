from __future__ import annotations

import unittest

from tools.validate_energy_momentum_bridge_dimensions import build


class EnergyMomentumBridgeDimensionTests(unittest.TestCase):
    def test_current_legacy_bridge_is_explicitly_blocked(self):
        result = build()
        self.assertEqual(result["state"], "BLOCKED_DIMENSIONAL_AUTHORITY_REQUIRED")
        self.assertFalse(result["claim_allowed"])
        self.assertTrue(result["observed"]["rho_declared_j_per_m3"])
        self.assertTrue(result["observed"]["pressure_declared_pa"])
        self.assertTrue(result["observed"]["pressure_divided_by_c2"])
        self.assertFalse(result["dimensional_analysis"]["current_sum_consistent"])

    def test_both_coherent_conventions_are_exposed_without_selection(self):
        result = build()
        self.assertIn("ENERGY_DENSITY_CONVENTION", result["available_options"])
        self.assertIn("MASS_DENSITY_CONVENTION", result["available_options"])
        self.assertTrue(result["selected_convention"].startswith("TOKEN_VAZIO"))


if __name__ == "__main__":
    unittest.main()
