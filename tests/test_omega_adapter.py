import importlib.util
import sys
import unittest
from pathlib import Path

MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "rll_photonic"
    / "omega_adapter.py"
)
SPEC = importlib.util.spec_from_file_location(
    "rll_omega_adapter",
    MODULE_PATH,
)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class OmegaAdapterTests(unittest.TestCase):
    def complete_checks(self, **overrides):
        values = dict(
            provenance_complete=True,
            uncertainty_known=True,
            in_domain=True,
            numerical_check_passed=True,
            calibration_check_passed=True,
            instrument_check_passed=True,
            transport_check_passed=True,
            matter_field_check_passed=True,
            physics_candidate=False,
        )
        values.update(overrides)
        return MODULE.ResidualChecks(**values)

    def test_normalized_residual(self):
        value = MODULE.normalized_residual(12.0, 10.0, 1.0, 1.0)
        self.assertAlmostEqual(value, 2.0 / (2.0**0.5))

    def test_missing_provenance_abstains(self):
        result = MODULE.classify_residual(
            self.complete_checks(provenance_complete=False)
        )
        self.assertEqual(result.value, "R_TOKEN_VAZIO")

    def test_out_of_domain_precedes_physics(self):
        result = MODULE.classify_residual(
            self.complete_checks(
                in_domain=False,
                physics_candidate=True,
            )
        )
        self.assertEqual(result.value, "R_OUT_OF_DOMAIN")

    def test_numerical_failure_precedes_physics(self):
        result = MODULE.classify_residual(
            self.complete_checks(
                numerical_check_passed=False,
                physics_candidate=True,
            )
        )
        self.assertEqual(result.value, "R_NUMERICAL")

    def test_physics_requires_all_prior_checks(self):
        result = MODULE.classify_residual(
            self.complete_checks(physics_candidate=True)
        )
        self.assertEqual(result.value, "R_PHYSICS")

    def test_large_residual_does_not_auto_promote_physics(self):
        screen = MODULE.screen_residuals(
            [8.0, -7.0],
            threshold=5.0,
            checks=self.complete_checks(),
        )
        self.assertEqual(screen.classification, "R_TOKEN_VAZIO")
        self.assertEqual(screen.exceedance_count, 2)

    def test_scope_split_gate(self):
        gate = MODULE.opposition_gate(
            support_weight=1.0,
            refutation_weight=1.0,
            scope_overlap=0.2,
            evidence_complete=True,
        )
        self.assertEqual(gate.state, "SCOPE_SPLIT")

    def test_photonic_invariants(self):
        self.assertEqual(
            MODULE.photonic_invariant_errors(
                intensity=1.0,
                q=0.2,
                u=0.2,
                v=0.2,
            ),
            [],
        )
        self.assertTrue(
            MODULE.photonic_invariant_errors(intensity=1.0, q=2.0)
        )


if __name__ == "__main__":
    unittest.main()
