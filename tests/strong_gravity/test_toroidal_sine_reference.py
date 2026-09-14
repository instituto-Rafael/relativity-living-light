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
    / "toroidal_sine_reference.py"
)
SPEC = importlib.util.spec_from_file_location("toroidal_sine_reference", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class ToroidalSineReferenceTests(unittest.TestCase):
    def state(self, **overrides):
        values = {
            "major_radius_m": 3.0,
            "minor_radius_m": 1.0,
            "inner_frequency_hz": 2.0,
            "outer_frequency_hz": 1.0,
            "reference_frequency_hz": 1.0,
            "amplitude": 1.0,
            "amplitude_unit": "normalized",
            "duration_s": 1.0,
            "sample_count": 1001,
            "observed_phase_offset_rad": 0.0,
        }
        values.update(overrides)
        return MODULE.ToroidalSineReferenceState(**values)

    def test_torus_point_lies_on_surface(self):
        point = MODULE.torus_point_m(3.0, 1.0, 0.7, 1.3)
        self.assertAlmostEqual(
            MODULE.torus_surface_residual_m(point, 3.0, 1.0), 0.0, places=12
        )

    def test_integer_inner_outer_cycles_close(self):
        result = MODULE.evaluate(self.state())
        self.assertTrue(result.cycle_closed_within_tolerance)
        self.assertLess(result.closure_residual_m, 1.0e-12)

    def test_noninteger_outer_cycle_does_not_close(self):
        result = MODULE.evaluate(self.state(outer_frequency_hz=1.25))
        self.assertFalse(result.cycle_closed_within_tolerance)
        self.assertGreater(result.closure_residual_m, 1.0)

    def test_zero_phase_offset_has_zero_error(self):
        result = MODULE.evaluate(self.state())
        self.assertAlmostEqual(result.phase_error_rad, 0.0, places=12)
        self.assertAlmostEqual(result.signal_rms_error, 0.0, places=12)
        self.assertAlmostEqual(result.phase_lock_score, 1.0, places=12)

    def test_phase_offset_produces_bounded_nonzero_error(self):
        result = MODULE.evaluate(self.state(observed_phase_offset_rad=math.pi / 2))
        self.assertAlmostEqual(result.phase_error_rad, math.pi / 2, places=12)
        self.assertGreater(result.signal_normalized_rms_error, 0.0)
        self.assertLessEqual(result.phase_lock_score, 1.0)

    def test_phase_wrap_is_principal_value(self):
        error = MODULE.wrapped_phase_error_rad(0.0, 3.0 * math.pi)
        self.assertAlmostEqual(abs(error), math.pi, places=12)

    def test_amplitude_scales_absolute_not_normalized_error(self):
        one = MODULE.evaluate(self.state(amplitude=1.0, observed_phase_offset_rad=0.3))
        two = MODULE.evaluate(self.state(amplitude=2.0, observed_phase_offset_rad=0.3))
        self.assertAlmostEqual(two.signal_rms_error / one.signal_rms_error, 2.0, places=12)
        self.assertAlmostEqual(
            two.signal_normalized_rms_error, one.signal_normalized_rms_error, places=12
        )

    def test_geometric_path_metric_is_dimensionless_and_positive(self):
        result = MODULE.evaluate(self.state())
        self.assertGreater(result.geometric_path_metric_dimensionless, 0.0)

    def test_deterministic_baseline(self):
        self.assertEqual(MODULE.baseline(), MODULE.baseline())

    def test_invalid_minor_radius_is_rejected(self):
        with self.assertRaises(ValueError):
            self.state(minor_radius_m=3.0).validate()

    def test_zero_frequency_is_rejected(self):
        with self.assertRaises(ValueError):
            self.state(reference_frequency_hz=0.0).validate()

    def test_small_sample_count_is_rejected(self):
        with self.assertRaises(ValueError):
            self.state(sample_count=2).validate()

    def test_baseline_is_reference_only_and_not_claim(self):
        baseline = MODULE.baseline()
        self.assertTrue(baseline["result"]["reference_only"])
        self.assertFalse(baseline["result"]["claim_allowed"])
        self.assertFalse(baseline["boundaries"]["pure_sine_is_universal_stabilizer"])
        self.assertFalse(baseline["boundaries"]["cosmological_background_modified"])

    def test_contract_preserves_primary_sources_and_boundaries(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        contract = json.loads(
            (root / "data" / "contracts" / "toroidal_research_cycle_adapter.v1.json").read_text()
        )
        self.assertFalse(contract["claim_allowed"])
        self.assertFalse(contract["boundaries"]["pure_sine_universal_stabilizer"])
        source_ids = {source["id"] for source in contract["primary_sources"]}
        self.assertIn("SRC-ASDEX-MOD-ECCD-2007", source_ids)
        self.assertIn("SRC-FAST-ION-2025", source_ids)

    def test_recorded_baseline_matches_runtime(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        recorded = json.loads(
            (
                root
                / "data"
                / "results"
                / "strong_gravity"
                / "toroidal_sine_reference_baseline.json"
            ).read_text()
        )
        runtime = MODULE.baseline()
        self.assertEqual(recorded["schema"], runtime["schema"])
        self.assertAlmostEqual(
            recorded["result"]["signal_normalized_rms_error"],
            runtime["result"]["signal_normalized_rms_error"],
            places=15,
        )
        self.assertFalse(recorded["result"]["claim_allowed"])


if __name__ == "__main__":
    unittest.main()
