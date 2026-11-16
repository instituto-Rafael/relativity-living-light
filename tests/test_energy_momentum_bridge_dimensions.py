from __future__ import annotations

import unittest

from tools.validate_energy_momentum_bridge_dimensions import build


class EnergyMomentumBridgeDimensionTests(unittest.TestCase):
    def test_typed_executor_closes_silent_mixing_only(self):
        result = build()
        self.assertEqual(
            result["state"],
            "TYPED_EXECUTOR_READY_SCIENTIFIC_SELECTION_REQUIRED",
        )
        self.assertFalse(result["claim_allowed"])
        self.assertEqual(
            result["closed_gap"],
            "SILENT_DIMENSIONAL_MIXING_FOR_NONZERO_PRESSURE",
        )
        self.assertEqual(
            result["open_gap"],
            "SCIENTIFIC_STRESS_ENERGY_SEMANTICS_SELECTION",
        )

    def test_both_coherent_representations_exist_without_selection(self):
        result = build()
        self.assertIn("ENERGY_DENSITY_CONVENTION", result["available_options"])
        self.assertIn("MASS_DENSITY_CONVENTION", result["available_options"])
        self.assertTrue(result["selected_convention"].startswith("TOKEN_VAZIO"))
        self.assertTrue(all(result["typed_executor"].values()))

    def test_dimensional_identities_remain_explicit(self):
        result = build()
        dimensional = result["dimensional_analysis"]
        self.assertEqual(dimensional["Pa"], "kg m^-1 s^-2 = J/m^3")
        self.assertEqual(dimensional["Pa_over_c2"], "kg/m^3")
        self.assertTrue(dimensional["energy_density_convention_consistent"])
        self.assertTrue(dimensional["mass_density_convention_consistent"])


if __name__ == "__main__":
    unittest.main()
