"""Adversarial synthetic-only tests for the isolated LPT operator."""
import importlib.util
import math
from pathlib import Path
import tempfile
import unittest

MODULE = Path(__file__).resolve().parents[1] / "src/rll/lpt_j0715_1141.py"
spec = importlib.util.spec_from_file_location("lpt_j0715_1141", MODULE)
lpt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lpt)


class LPTSyntheticTests(unittest.TestCase):
    def test_spin_clock_zero_residual(self):
        rows = [{"pulse_number": str(i), "toa_seconds": str(100 + i * 474)} for i in range(8)]
        result = lpt.pulse_timing_residuals(rows, 474)
        self.assertEqual(result["rms_seconds"], 0)
        self.assertFalse(result["claim_allowed"])

    def test_missing_pulses_use_explicit_index(self):
        rows = [{"pulse_number": "10", "toa_seconds": "0"},
                {"pulse_number": "13", "toa_seconds": "1422"}]
        self.assertEqual(lpt.pulse_timing_residuals(rows, 474)["residual_seconds"], [0, 0])

    def test_clock_drift_visible(self):
        rows = [{"pulse_number": str(i), "toa_seconds": str(i * 475)} for i in range(6)]
        self.assertEqual(lpt.pulse_timing_residuals(rows, 474)["residual_seconds"][-1], 5)

    def test_clock_rejects_bad_inputs(self):
        bad = [{"pulse_number": "1", "toa_seconds": "1"},
               {"pulse_number": "1", "toa_seconds": "475"}]
        with self.assertRaises(ValueError):
            lpt.pulse_timing_residuals(bad, 474)
        with self.assertRaises(ValueError):
            lpt.pulse_timing_residuals(bad, -1)
        with self.assertRaises(ValueError):
            lpt.pulse_timing_residuals([{"pulse_number": "1.5", "toa_seconds": "0"},
                                       {"pulse_number": "2", "toa_seconds": "1"}], 474)

    def test_faraday_null(self):
        rows = [{"orbital_phase": i / 12, "rm_rad_m2": 5, "rm_sigma_rad_m2": 1}
                for i in range(12)]
        result = lpt.faraday_phase_diagnostic(rows)
        self.assertAlmostEqual(result["delta_chi2"], 0, places=9)
        self.assertEqual(result["significance"], "NOT_ASSESSED")

    def test_faraday_harmonic_detected_in_synthetic_data(self):
        rows = [{"orbital_phase": i / 12, "rm_rad_m2": 5 + 3 * math.sin(2 * math.pi * i / 12),
                 "rm_sigma_rad_m2": 1} for i in range(12)]
        result = lpt.faraday_phase_diagnostic(rows)
        self.assertAlmostEqual(result["fit_coefficients"]["sin"], 3, places=9)
        self.assertAlmostEqual(result["chi2_first_harmonic"], 0, places=9)
        self.assertGreater(result["delta_chi2"], 0)
        self.assertFalse(result["claim_allowed"])

    def test_faraday_rejects_singular_or_invalid(self):
        rows = [{"orbital_phase": 0, "rm_rad_m2": 2, "rm_sigma_rad_m2": 1} for _ in range(10)]
        with self.assertRaises(ValueError):
            lpt.faraday_phase_diagnostic(rows)
        rows = [{"orbital_phase": i / 10, "rm_rad_m2": 2, "rm_sigma_rad_m2": 1} for i in range(10)]
        rows[0]["rm_sigma_rad_m2"] = 0
        with self.assertRaises(ValueError):
            lpt.faraday_phase_diagnostic(rows)

    def test_csv_integrity_and_missing_columns(self):
        with tempfile.TemporaryDirectory() as td:
            source = Path(td) / "input.csv"
            source.write_text("pulse_number,toa_seconds\n0,0\n1,474\n", encoding="utf-8")
            result = lpt.analyze_csv(str(source), "toa", 474)
            self.assertEqual(len(result["input_sha256"]), 64)
            self.assertFalse(result["source_identity_verified"])
            with self.assertRaises(ValueError):
                lpt.analyze_csv(str(source), "rm")


if __name__ == "__main__":
    unittest.main()
