import importlib.util
from pathlib import Path
import sys
import unittest

MODULE_PATH = (
    Path(__file__).parents[2]
    / "data/pipelines/strong_gravity/relativistic_compression_radiation_bridge.py"
)
spec = importlib.util.spec_from_file_location("compression_radiation", MODULE_PATH)
m = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = m
spec.loader.exec_module(m)


class TestRelativisticCompressionRadiationBridge(unittest.TestCase):
    def test_compression_positive_when_theta_negative(self):
        self.assertEqual(m.compression_work_w_m3(10.0, -2.0), 20.0)

    def test_expansion_is_signed_cooling_work(self):
        self.assertEqual(m.compression_work_w_m3(10.0, 2.0), -20.0)

    def test_magnetic_pressure_even_in_field_direction(self):
        self.assertEqual(m.magnetic_pressure_pa(2.0), m.magnetic_pressure_pa(-2.0))

    def test_photon_thrust_absorption(self):
        self.assertAlmostEqual(m.photon_thrust_n(m.C_M_S), 1.0)

    def test_photon_thrust_reflection(self):
        self.assertAlmostEqual(m.photon_thrust_n(m.C_M_S, 2.0), 2.0)

    def test_eddington_identity(self):
        mass = 2.0e31
        opacity = 0.04
        radius = 1.0e8
        luminosity = m.eddington_luminosity_w(mass, opacity)
        flux = m.radiation_flux_w_m2(luminosity, radius)
        self.assertAlmostEqual(
            m.radiative_acceleration_m_s2(flux, opacity),
            m.gravity_acceleration_m_s2(mass, radius),
            places=10,
        )

    def test_degeneracy_pressure_scales_as_density_five_thirds(self):
        p1 = m.electron_degeneracy_pressure_pa(1.0e30)
        p2 = m.electron_degeneracy_pressure_pa(2.0e30)
        self.assertAlmostEqual(p2 / p1, 2.0 ** (5.0 / 3.0), places=12)

    def test_field_energy_has_equivalent_mass_density(self):
        self.assertGreater(
            m.field_energy_equivalent_mass_density_kg_m3(1.0, 0.0), 0.0
        )

    def test_reference_threshold_ladder(self):
        reached = m.reached_reference_thresholds(2.0e6)
        self.assertIn("hydrogen_ionization_reference", reached)
        self.assertIn("electron_positron_rest_pair_reference", reached)
        self.assertNotIn("hadronic_resolution_reference", reached)

    def test_thresholds_do_not_claim_process_probability(self):
        reached = m.reached_reference_thresholds(20.0)
        self.assertEqual(reached, ("hydrogen_ionization_reference",))

    def test_negative_available_energy_rejected(self):
        with self.assertRaises(ValueError):
            m.reached_reference_thresholds(-1.0)

    def test_zero_luminosity_has_zero_flux(self):
        self.assertEqual(m.radiation_flux_w_m2(0.0, 1.0), 0.0)

    def test_acceleration_and_eddington_ratios_match(self):
        state = m.CompressionRadiationState(
            1.0, -1.0, 1.0e30, 1.0, 1.0e30, 1.0e7, 0.04, 2.0e31
        )
        result = m.evaluate(state, 20.0)
        self.assertAlmostEqual(
            result.eddington_ratio, result.acceleration_ratio, places=12
        )

    def test_claim_boundary_closed(self):
        state = m.CompressionRadiationState(
            1.0, -1.0, 1.0e30, 1.0, 1.0e30, 1.0e7, 0.04, 2.0e31
        )
        self.assertFalse(m.evaluate(state, 20.0).claim_allowed)

    def test_baseline_preserves_microphysics_boundaries(self):
        boundaries = m.baseline()["boundaries"]
        self.assertFalse(boundaries["compression_automatically_creates_subparticles"])
        self.assertFalse(boundaries["spin_hydrodynamics_solved"])
        self.assertFalse(boundaries["claim_allowed"])


if __name__ == "__main__":
    unittest.main()
