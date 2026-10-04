from __future__ import annotations

import importlib.util
import math
import unittest
from pathlib import Path

from rll.academic_false_positive_gate import (
    CONFIRMATORY_BOOLEAN_REQUIREMENTS,
    RLL_EXISTING_FIT_PARAMETERS,
    academic_false_positive_gate,
    circular_section_width,
    difference_of_means,
    dispersion_buffer,
    exploratory_spiral_geodesic_features,
    geometric_rational,
    isosceles_projection,
    leg_asymmetry,
    modular_signature,
    ols_line,
    paired_difference_stats,
    paired_existing_rll_parameter_deltas,
    pythagorean_difference,
    quadratic_discriminant,
    sample_variance,
    signed_quadratic,
    summarize_existing_rll_parameter_samples,
    variance_of_mean,
    venturi_reference,
)

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "tools" / "validate_academic_false_positive_gate.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_academic_false_positive_gate", VALIDATOR)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class AcademicFalsePositiveDiagnosticsTests(unittest.TestCase):
    def test_sample_variance_uses_n_minus_one_and_variance_of_mean_uses_n(self) -> None:
        values = [1.0, 2.0, 3.0]
        self.assertAlmostEqual(sample_variance(values) or -1.0, 1.0)
        self.assertAlmostEqual(variance_of_mean(values) or -1.0, 1.0 / 3.0)
        self.assertIsNone(sample_variance([1.0]))

    def test_difference_of_means_propagates_independent_sample_variances(self) -> None:
        out = difference_of_means([1, 2, 3], [2, 3, 4])
        self.assertAlmostEqual(float(out["mean_difference"]), -1.0)
        self.assertAlmostEqual(float(out["variance_of_difference"]), 2.0 / 3.0)
        self.assertAlmostEqual(float(out["standard_error_of_difference"]), math.sqrt(2.0 / 3.0))

    def test_paired_difference_uses_variance_of_pairwise_differences(self) -> None:
        out = paired_difference_stats([2, 5, 9, 10], [1, 3, 8, 6])
        # d=[1,2,1,4], mean=2, unbiased sample variance=2, Var(mean)=2/4.
        self.assertEqual(out["design"], "PAIRED")
        self.assertEqual(out["n_pairs"], 4)
        self.assertAlmostEqual(float(out["mean_difference"]), 2.0)
        self.assertAlmostEqual(float(out["sample_variance_of_differences"]), 2.0)
        self.assertAlmostEqual(float(out["variance_of_mean_difference"]), 0.5)
        self.assertAlmostEqual(float(out["standard_error_of_mean_difference"]), math.sqrt(0.5))
        with self.assertRaises(ValueError):
            paired_difference_stats([1, 2], [1])

    def test_existing_rll_parameter_dispersion_does_not_create_new_fit_parameters(self) -> None:
        self.assertEqual(
            RLL_EXISTING_FIT_PARAMETERS,
            frozenset({"H0", "Om", "OL", "Os0", "zt", "wt", "Ob_h2", "sigma8"}),
        )
        summary = summarize_existing_rll_parameter_samples(
            {
                "H0": [60.0, 61.0, 62.0],
                "Os0": [0.0, 0.01, 0.02],
            }
        )
        self.assertAlmostEqual(float(summary["H0"]["mean"]), 61.0)
        self.assertAlmostEqual(float(summary["H0"]["sample_variance"]), 1.0)
        self.assertAlmostEqual(float(summary["H0"]["variance_of_mean"]), 1.0 / 3.0)
        self.assertEqual(summary["H0"]["role"], "EXISTING_FIT_PARAMETER_DIAGNOSTIC_ONLY")

        with self.assertRaises(ValueError):
            summarize_existing_rll_parameter_samples({"pi_phi": [5.0, 5.1, 5.2]})
        with self.assertRaises(ValueError):
            summarize_existing_rll_parameter_samples({"mod14": [0.0, 1.0, 2.0]})

    def test_paired_existing_rll_parameter_deltas_require_same_authorized_parameter_set(self) -> None:
        out = paired_existing_rll_parameter_deltas(
            {"H0": [60.0, 61.0, 62.0], "wt": [0.2, 0.3, 0.4]},
            {"H0": [59.0, 60.0, 61.0], "wt": [0.1, 0.2, 0.3]},
        )
        self.assertAlmostEqual(float(out["H0"]["mean_difference"]), 1.0)
        self.assertAlmostEqual(float(out["wt"]["mean_difference"]), 0.1)
        self.assertEqual(out["H0"]["design"], "PAIRED")

        with self.assertRaises(ValueError):
            paired_existing_rll_parameter_deltas({"H0": [60.0]}, {"Om": [0.3]})
        with self.assertRaises(ValueError):
            paired_existing_rll_parameter_deltas({"pi_phi": [5.0, 5.1]}, {"pi_phi": [5.0, 5.1]})

    def test_ols_line_and_dispersion_buffer(self) -> None:
        fit = ols_line([1, 2, 3, 4], [2, 4, 6, 8])
        self.assertAlmostEqual(float(fit["slope"]), 2.0)
        self.assertAlmostEqual(float(fit["intercept"]), 0.0)
        self.assertAlmostEqual(float(fit["sse"]), 0.0)
        self.assertAlmostEqual(float(fit["residual_variance"]), 0.0)
        buffer = dispersion_buffer([1, 2, 3], sigma_multiplier=3.0)
        self.assertAlmostEqual(float(buffer["sample_std"]), 1.0)
        self.assertAlmostEqual(float(buffer["buffer"]), 3.0)
        self.assertEqual(buffer["state"], "STATISTICAL_ANALOGY_ONLY")

    def test_rational_scale_is_not_lost(self) -> None:
        a = geometric_rational(77, 33)
        b = geometric_rational(777, 333)
        self.assertEqual((a.primitive_p, a.primitive_q, a.scale_gcd), (7, 3, 11))
        self.assertEqual((b.primitive_p, b.primitive_q, b.scale_gcd), (7, 3, 111))
        self.assertAlmostEqual(a.ratio, b.ratio)

    def test_modular_signature_preserves_zero_as_numeric_state(self) -> None:
        sig7 = modular_signature(7)
        sig999 = modular_signature(999)
        self.assertEqual(sig7[7], 0)
        self.assertEqual(sig999[7], 5)
        self.assertEqual(sig999[14], 5)
        self.assertEqual(sig999[10], 9)
        self.assertEqual(sig999[70], 19)

    def test_pythagorean_and_quadratic_signed_relations(self) -> None:
        p = pythagorean_difference(5, 3)
        self.assertAlmostEqual(p["c2"], p["two_ab_plus_delta2"])
        self.assertEqual(p["delta"], 2.0)
        self.assertEqual(quadratic_discriminant(1, -2, 1)["state"], "TANGENT_DOUBLE_ROOT")
        self.assertEqual(quadratic_discriminant(1, 0, 1)["state"], "NO_REAL_ROOT")
        self.assertEqual(quadratic_discriminant(1, 0, -1)["state"], "TWO_REAL_ROOTS")
        self.assertAlmostEqual(signed_quadratic(1, -3, -4, 2), -6.0)

    def test_30_degree_geometric_gate_keeps_distinct_heights(self) -> None:
        iso = isosceles_projection(10.0, 30.0)
        self.assertAlmostEqual(iso["base"], 10.0)
        self.assertAlmostEqual(iso["height"], 5.0 * math.sqrt(3.0))
        self.assertAlmostEqual(circular_section_width(10.0, 30.0), 10.0)
        self.assertNotAlmostEqual(iso["height"], 15.0)

    def test_leg_asymmetry_does_not_claim_isosceles(self) -> None:
        out = leg_asymmetry(7.0, 3.0)
        self.assertEqual(out["min_abs_leg"], 3.0)
        self.assertEqual(out["max_abs_leg"], 7.0)
        self.assertEqual(out["absolute_difference"], 4.0)

    def test_venturi_is_explicit_reference_model(self) -> None:
        out = venturi_reference(area1=2.0, area2=1.0, velocity1=3.0, density=1.0)
        self.assertAlmostEqual(float(out["velocity2"]), 6.0)
        self.assertAlmostEqual(float(out["pressure_drop_p1_minus_p2"]), 13.5)
        self.assertEqual(out["state"], "REFERENCE_MODEL_ONLY")

    def test_authorial_scalars_are_features_not_equalities(self) -> None:
        out = exploratory_spiral_geodesic_features(3)
        self.assertAlmostEqual(float(out["pg_3_over_2_pow_n"]), 3.375)
        self.assertFalse(bool(out["equality_asserted"]))
        self.assertNotAlmostEqual(float(out["pg_3_over_2_pow_n"]), float(out["pi_times_phi"]))
        self.assertGreater(float(out["log_log_999_natural"]), 0.0)

    def test_academic_false_positive_gate_is_fail_closed(self) -> None:
        blocked = academic_false_positive_gate(True, {"negative_controls_passed": True})
        self.assertFalse(bool(blocked["confirmatory_ready"]))
        self.assertIn("preregistered_before_result", blocked["missing_or_failed"])

        complete = {name: True for name in CONFIRMATORY_BOOLEAN_REQUIREMENTS}
        complete["multiplicity_policy"] = "predefined_single_primary"
        ready = academic_false_positive_gate(True, complete)
        self.assertTrue(bool(ready["confirmatory_ready"]))
        self.assertEqual(ready["missing_or_failed"], [])

        no_screen = academic_false_positive_gate(False, complete)
        self.assertFalse(bool(no_screen["confirmatory_ready"]))

    def test_nested_real_claim_cannot_evade_validator(self) -> None:
        validator = load_validator()
        payload = {
            "container": [
                {
                    "dataset_type": "real_observational",
                    "interpretation_label": "rll_preferred_strong",
                    "claim_allowed": True,
                }
            ]
        }
        found = list(validator.walk_real_results(payload))
        self.assertEqual(len(found), 1)
        mapping, location = found[0]
        self.assertEqual(location, "$.container[0]")
        errors = validator.validate_real_result(ROOT / "results" / "nested_fixture.json", mapping, location)
        self.assertTrue(errors)
        self.assertIn("confirmatory evidence", errors[0])

    def test_technical_readiness_true_without_real_dataset_type_is_not_scientific_claim(self) -> None:
        validator = load_validator()
        payload = {"bao_covariance_policy": {"claim_allowed": True, "mode": "official_full"}}
        self.assertEqual(list(validator.walk_real_results(payload)), [])


if __name__ == "__main__":
    unittest.main()
