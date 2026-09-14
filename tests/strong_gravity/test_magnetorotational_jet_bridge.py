from __future__ import annotations

import importlib.util
import json
import math
import pathlib
import sys
import unittest

MODULE_PATH = (
    pathlib.Path(__file__).resolve().parents[2]
    / "data"
    / "pipelines"
    / "strong_gravity"
    / "magnetorotational_jet_bridge.py"
)
SPEC = importlib.util.spec_from_file_location("magnetorotational_jet_bridge", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class MagnetorotationalJetBridgeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.rotor = MODULE.DipoleRotorState(
            volume_m3=1.0,
            density_kg_m3=7_500.0,
            magnetization_a_m=1.19e6,
            characteristic_radius_m=0.5,
            inertia_coefficient=0.4,
            spin_angular_frequency_rad_s=1_000.0,
            field_angular_frequency_rad_s=500.0,
            magnetic_field_t=1.5,
        )
        self.plasma = MODULE.KerrPlasmaState(
            central_mass_kg=10.0 * MODULE.SOLAR_MASS_KG,
            spin_dimensionless=0.9,
            magnetic_field_t=1.0e4,
            mass_density_kg_m3=1.0e-4,
            specific_enthalpy_dimensionless=2.0,
            radial_speed_m_s=0.1 * MODULE.C_M_S,
            thermal_pressure_pa=1.0e11,
            magnetic_flux_wb=1.0e4 * math.pi * (1.5e4) ** 2,
            field_angular_frequency_rad_s=500.0,
        )

    def test_cross_product_orientation(self) -> None:
        self.assertEqual(
            MODULE.cross((1.0, 0.0, 0.0), (0.0, 1.0, 0.0)),
            (0.0, 0.0, 1.0),
        )

    def test_ead_limit_is_charge_density_times_electric_field(self) -> None:
        force = MODULE.electromagnetic_force_density_n_m3(
            2.0, (3.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 1.0)
        )
        self.assertEqual(force, (6.0, 0.0, 0.0))

    def test_lorentz_term_adds_to_electric_force(self) -> None:
        force = MODULE.electromagnetic_force_density_n_m3(
            1.0, (2.0, 0.0, 0.0), (0.0, 3.0, 0.0), (0.0, 0.0, 4.0)
        )
        self.assertEqual(force, (14.0, 0.0, 0.0))

    def test_poynting_flux_follows_e_cross_b(self) -> None:
        flux = MODULE.poynting_flux_w_m2((2.0, 0.0, 0.0), (0.0, 3.0, 0.0))
        self.assertEqual(flux[0], 0.0)
        self.assertEqual(flux[1], 0.0)
        self.assertGreater(flux[2], 0.0)

    def test_rotor_mass_and_moment_are_volume_extensive(self) -> None:
        self.assertEqual(self.rotor.mass_kg, 7_500.0)
        self.assertEqual(self.rotor.magnetic_moment_a_m2, 1.19e6)

    def test_similar_body_scaling_preserves_requested_size_law(self) -> None:
        scaling = MODULE.similar_body_scaling(1.0, 10.0)
        self.assertEqual(scaling["magnetic_moment_ratio"], 10.0)
        self.assertAlmostEqual(
            scaling["moment_of_inertia_ratio"], 10.0 ** (5.0 / 3.0), places=12
        )
        self.assertAlmostEqual(
            scaling["angular_response_ratio"], 10.0 ** (-2.0 / 3.0), places=12
        )

    def test_larger_similar_body_responds_angularly_more_slowly(self) -> None:
        self.assertLess(
            MODULE.similar_body_scaling(1.0, 10.0)["angular_response_ratio"],
            1.0,
        )

    def test_rotational_lock_parameter_is_finite(self) -> None:
        value = MODULE.rotational_lock_parameter(self.rotor)
        self.assertGreater(value, 0.0)
        self.assertTrue(math.isfinite(value))

    def test_rotational_regimes_are_fail_closed_conventions(self) -> None:
        self.assertEqual(
            MODULE.rotational_regime(0.01), "angular_inertia_dominated"
        )
        self.assertEqual(MODULE.rotational_regime(1.0), "phase_lock_transition")
        self.assertEqual(MODULE.rotational_regime(100.0), "field_torque_dominated")

    def test_schwarzschild_horizon_has_zero_angular_frequency(self) -> None:
        omega = MODULE.horizon_angular_frequency_rad_s(
            10.0 * MODULE.SOLAR_MASS_KG, 0.0
        )
        self.assertEqual(omega, 0.0)

    def test_kerr_horizon_frequency_changes_sign_with_spin(self) -> None:
        positive = MODULE.horizon_angular_frequency_rad_s(
            10.0 * MODULE.SOLAR_MASS_KG, 0.9
        )
        negative = MODULE.horizon_angular_frequency_rad_s(
            10.0 * MODULE.SOLAR_MASS_KG, -0.9
        )
        self.assertAlmostEqual(positive, -negative, places=12)

    def test_light_cylinder_is_c_over_field_rotation(self) -> None:
        self.assertEqual(
            MODULE.light_cylinder_radius_m(2.0), MODULE.C_M_S / 2.0
        )

    def test_arrest_parameter_increases_with_field(self) -> None:
        weak = MODULE.arrest_parameter(1.0, 1.0, 10.0, 1.0)
        strong = MODULE.arrest_parameter(2.0, 1.0, 10.0, 1.0)
        self.assertAlmostEqual(strong / weak, 4.0, places=12)

    def test_magnetization_decreases_with_mass_loading(self) -> None:
        light = MODULE.magnetization_sigma(10.0, 1.0e-8, 2.0)
        heavy = MODULE.magnetization_sigma(10.0, 1.0e-4, 2.0)
        self.assertGreater(light, heavy)

    def test_bz_proxy_is_zero_without_spin(self) -> None:
        self.assertEqual(
            MODULE.blandford_znajek_power_proxy_w(10.0, 0.0, 0.05), 0.0
        )

    def test_bz_proxy_scales_with_flux_squared(self) -> None:
        p1 = MODULE.blandford_znajek_power_proxy_w(1.0, 2.0, 0.05)
        p2 = MODULE.blandford_znajek_power_proxy_w(2.0, 2.0, 0.05)
        self.assertAlmostEqual(p2 / p1, 4.0, places=12)

    def test_baseline_is_mad_and_poynting_candidate_but_not_claim(self) -> None:
        baseline = MODULE.baseline()
        result = baseline["result"]
        self.assertEqual(result["arrest_regime"], "mad_candidate")
        self.assertEqual(
            result["conversion_regime"], "poynting_dominated_candidate"
        )
        self.assertFalse(result["claim_allowed"])
        self.assertFalse(baseline["boundaries"]["cosmological_background_modified"])

    def test_invalid_extremal_spin_is_rejected(self) -> None:
        invalid = MODULE.KerrPlasmaState(
            central_mass_kg=1.0,
            spin_dimensionless=1.0,
            magnetic_field_t=1.0,
            mass_density_kg_m3=1.0,
            specific_enthalpy_dimensionless=1.0,
            radial_speed_m_s=0.0,
            thermal_pressure_pa=1.0,
            magnetic_flux_wb=1.0,
            field_angular_frequency_rad_s=1.0,
        )
        with self.assertRaises(ValueError):
            invalid.validate()

    def test_contract_preserves_claim_boundary_and_primary_sources(self) -> None:
        root = pathlib.Path(__file__).resolve().parents[2]
        contract = json.loads(
            (root / "data" / "contracts" / "magnetorotational_jet_bridge.v1.json").read_text()
        )
        self.assertFalse(contract["claim_allowed"])
        source_ids = {
            source["id"]
            for source in contract["modern_cosmology_and_astrophysics_sources"]
        }
        self.assertIn("SRC-BZ-1977", source_ids)
        self.assertIn("SRC-EHT-M87-VIII-2021", source_ids)

    def test_recorded_baseline_matches_runtime_baseline(self) -> None:
        root = pathlib.Path(__file__).resolve().parents[2]
        recorded = json.loads(
            (
                root
                / "data"
                / "results"
                / "strong_gravity"
                / "magnetorotational_jet_bridge_baseline.json"
            ).read_text()
        )
        runtime = MODULE.baseline()
        self.assertEqual(recorded["schema"], runtime["schema"])
        self.assertAlmostEqual(
            recorded["result"]["arrest_parameter"],
            runtime["result"]["arrest_parameter"],
            places=12,
        )
        self.assertFalse(recorded["result"]["claim_allowed"])

    def test_cosmology_route_is_explicitly_disconnected(self) -> None:
        root = pathlib.Path(__file__).resolve().parents[2]
        contract = json.loads(
            (root / "data" / "contracts" / "magnetorotational_jet_bridge.v1.json").read_text()
        )
        routes = {
            route["route"]: route["state"]
            for route in contract["observational_routes"]
        }
        self.assertEqual(
            routes["cosmological background"],
            "NOT_CONNECTED_BY_THIS_BRIDGE",
        )


if __name__ == "__main__":
    unittest.main()
