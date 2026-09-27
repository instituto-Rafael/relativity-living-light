from __future__ import annotations

import unittest

from tools.validate_energy_momentum_bridge_dimensions import build


class EnergyMomentumBridgeDimensionTests(unittest.TestCase):
    def test_legacy_mixing_is_guarded_by_typed_executor(self):
        result = build()
        self.assertEqual(
            result["state"],
            "TYPED_EXECUTOR_READY_SCIENTIFIC_SELECTION_REQUIRED",
        )
        self.assertFalse(result["claim_allowed"])
        self.assertTrue(result["legacy_observed"]["rho_declared_j_per_m3"])
        self.assertTrue(result["legacy_observed"]["pressure_declared_pa"])
        self.assertTrue(
            result["legacy_observed"]["pressure_divided_by_c2_helper_retained"]
        )
        self.assertEqual(
            result["dimensional_analysis"]["legacy_nonzero_pressure_sum"],
            "BLOCKED_BY_TYPED_EXECUTOR",
        )
        self.assertEqual(
            result["closed_gap"],
            "SILENT_DIMENSIONAL_MIXING_FOR_NONZERO_PRESSURE",
        )

    def test_both_coherent_conventions_are_exposed_without_selection(self):
        result = build()
        self.assertIn(
            "ENERGY_DENSITY_CONVENTION",
            result["available_options"],
        )
        self.assertIn(
            "MASS_DENSITY_CONVENTION",
            result["available_options"],
        )
        self.assertTrue(result["selected_convention"].startswith("TOKEN_VAZIO"))
        self.assertEqual(
            result["open_gap"],
            "SCIENTIFIC_STRESS_ENERGY_SEMANTICS_SELECTION",
        )

    def test_typed_executor_markers_are_complete(self):
        result = build()
        self.assertTrue(all(result["typed_executor"].values()))
        self.assertTrue(
            result["dimensional_analysis"][
                "energy_density_convention_consistent"
            ]
        )
        self.assertTrue(
            result["dimensional_analysis"][
                "mass_density_convention_consistent"
            ]
        )


if __name__ == "__main__":
    unittest.main()
