from __future__ import annotations

import importlib.util
import math
import pathlib
import sys
import unittest

MODULE_PATH = (
    pathlib.Path(__file__).resolve().parents[2]
    / "data"
    / "pipelines"
    / "strong_gravity"
    / "spiral_plasma_thermal_bridge.py"
)
SPEC = importlib.util.spec_from_file_location("spiral_plasma_thermal_bridge", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class SpiralPlasmaThermalBridgeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.state = MODULE.PlasmaState(
            electron_density_m3=1.0e18,
            electron_temperature_k=2.0e4,
            effective_collision_hz=2.0e6,
            magnetic_field_t=2.0e-3,
            ionization_fraction=0.35,
        )
        self.fundamental = MODULE.DriveComponent(
            frequency_hz=MODULE.FUNDAMENTAL_HZ,
            electric_field_v_m=120.0,
        )
        self.harmonic = MODULE.DriveComponent(
            frequency_hz=MODULE.SECOND_HARMONIC_HZ,
            electric_field_v_m=60.0,
            phase_rad=math.pi / 4.0,
        )

    def test_frequency_pair_is_exact_harmonic(self) -> None:
        self.assertEqual(MODULE.SECOND_HARMONIC_HZ, 2.0 * MODULE.FUNDAMENTAL_HZ)
        self.assertAlmostEqual(
            MODULE.harmonic_drive_value(0.0, self.fundamental, self.harmonic),
            120.0 + 60.0 / math.sqrt(2.0),
            places=12,
        )

    def test_photon_energy_is_not_atomic_scale(self) -> None:
        self.assertLess(MODULE.photon_energy_ev(MODULE.SECOND_HARMONIC_HZ), 2.0e-9)

    def test_article_modes_convert_to_terahertz(self) -> None:
        self.assertAlmostEqual(MODULE.mev_to_hz(3.2) / 1.0e12, 0.7737566, places=6)
        self.assertAlmostEqual(MODULE.mev_to_hz(5.1) / 1.0e12, 1.2331745, places=6)

    def test_spiral_contracts_one_sector(self) -> None:
        radius = MODULE.spiral_radius(10.0, MODULE.SPIRAL_SECTOR_RAD)
        self.assertAlmostEqual(radius, 10.0 * MODULE.SPIRAL_RATIO, places=12)

    def test_higher_frequency_reduces_dissipative_conductivity_for_fixed_nu(self) -> None:
        sigma_144 = MODULE.drude_conductivity_real_s_m(
            self.state, MODULE.FUNDAMENTAL_HZ
        )
        sigma_288 = MODULE.drude_conductivity_real_s_m(
            self.state, MODULE.SECOND_HARMONIC_HZ
        )
        self.assertGreater(sigma_144, sigma_288)
        self.assertGreater(sigma_288, 0.0)

    def test_magnetic_field_makes_transport_anisotropic(self) -> None:
        tensor = MODULE.conductivity_tensor(self.state)
        self.assertGreater(tensor.parallel_s_m, tensor.pedersen_s_m)
        self.assertGreater(tensor.hall_s_m, 0.0)
        self.assertGreater(tensor.magnetization_beta, 0.0)

    def test_rf_heating_is_nonnegative(self) -> None:
        self.assertGreater(MODULE.rf_heating_w_m3(self.state, self.fundamental), 0.0)

    def test_biermann_source_vanishes_for_parallel_gradients(self) -> None:
        source = MODULE.biermann_source_t_s(
            1.0e18,
            (1.0e20, 0.0, 0.0),
            (1.0e3, 0.0, 0.0),
        )
        self.assertEqual(source, 0.0)

    def test_biermann_source_exists_for_crossed_gradients(self) -> None:
        source = MODULE.biermann_source_t_s(
            1.0e18,
            (1.0e20, 0.0, 0.0),
            (0.0, 1.0e3, 0.0),
        )
        self.assertGreater(source, 0.0)

    def test_temperature_rate_respects_losses(self) -> None:
        hot = MODULE.ThermalBudget(
            heat_capacity_j_m3_k=10.0,
            compression_w_m3=100.0,
            reconnection_w_m3=20.0,
            cooling_w_m3=5.0,
        )
        cold = MODULE.ThermalBudget(
            heat_capacity_j_m3_k=10.0,
            compression_w_m3=100.0,
            reconnection_w_m3=20.0,
            cooling_w_m3=500.0,
        )
        self.assertGreater(
            MODULE.temperature_rate_k_s(self.state, (), hot), 0.0
        )
        self.assertLess(
            MODULE.temperature_rate_k_s(self.state, (), cold), 0.0
        )

    def test_canonical_result_keeps_claim_gate_closed(self) -> None:
        budget = MODULE.ThermalBudget(
            heat_capacity_j_m3_k=20.0,
            compression_w_m3=75.0,
            reconnection_w_m3=25.0,
            radiation_absorption_w_m3=10.0,
            cooling_w_m3=30.0,
            outflow_w_m3=5.0,
        )
        result = MODULE.evaluate_bridge(
            state=self.state,
            fundamental=self.fundamental,
            second_harmonic=self.harmonic,
            budget=budget,
            radius0_m=2.0,
            phi_rad=MODULE.SPIRAL_SECTOR_RAD,
            grad_density_m4=(1.0e20, 0.0, 0.0),
            grad_temperature_k_m=(0.0, 1.0e3, 0.0),
        )
        self.assertFalse(result.claim_allowed)
        self.assertIn("claim_boundary", result.to_dict())

    def test_invalid_ionization_fraction_is_rejected(self) -> None:
        invalid = MODULE.PlasmaState(1.0e18, 1.0e4, 1.0e6, 0.0, 1.1)
        with self.assertRaises(ValueError):
            invalid.validate()


if __name__ == "__main__":
    unittest.main()
