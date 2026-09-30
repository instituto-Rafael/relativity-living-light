import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
P = ROOT / "scripts" / "rll_stratified_reservoir_aurora_bridge.py"
SPEC = importlib.util.spec_from_file_location("rll_reservoir_aurora", P)
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


class ReservoirAuroraBridgeTests(unittest.TestCase):
    def test_hydrostatic_pressure_increases_with_depth(self):
        self.assertGreater(M.hydrostatic_pressure(200), M.hydrostatic_pressure(100))

    def test_invalid_hydrostatic_inputs_fail_closed(self):
        with self.assertRaises(ValueError):
            M.hydrostatic_pressure(-1)

    def test_saturation_threshold_is_explicit(self):
        self.assertLess(M.saturation_ratio(0.9, 1.0), 1.0)
        self.assertGreater(M.saturation_ratio(1.1, 1.0), 1.0)

    def test_positive_n2_is_stable_under_declared_sign_convention(self):
        self.assertTrue(M.stable_stratification(1e-4))
        self.assertFalse(M.stable_stratification(-1e-4))

    def test_photon_energy_orders_known_oxygen_lines(self):
        self.assertGreater(M.photon_energy_ev(557.7), M.photon_energy_ev(630.0))

    def test_receipt_is_fail_closed(self):
        r = M.synthetic_receipt()
        self.assertFalse(r["claim_allowed"])
        self.assertEqual(r["input_class"], "SYNTHETIC_REFERENCE_ONLY")
        self.assertIn("STRUCTURAL_ANALOGY != MECHANISM_EQUIVALENCE", r["boundaries"])
        self.assertGreaterEqual(len(r["gaps"]), 4)


if __name__ == "__main__":
    unittest.main()
