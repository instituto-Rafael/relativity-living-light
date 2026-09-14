import importlib.util
import sys
import unittest
from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "rll_omega_residual_audit.py"
)
SPEC = importlib.util.spec_from_file_location(
    "rll_omega_residual_audit",
    SCRIPT,
)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class ResidualAuditCliTests(unittest.TestCase):
    def payload(self):
        return {
            "observed": [10.0, 12.0],
            "predicted": [9.0, 10.0],
            "sigma_observed": [1.0, 1.0],
            "sigma_model": [0.5, 0.5],
            "threshold": 2.0,
            "checks": {
                "provenance_complete": True,
                "uncertainty_known": True,
                "in_domain": True,
                "numerical_check_passed": True,
                "calibration_check_passed": True,
                "instrument_check_passed": True,
                "transport_check_passed": True,
                "matter_field_check_passed": True,
                "physics_candidate": False
            },
            "support_weight": 1.0,
            "refutation_weight": 1.0,
            "scope_overlap": 0.8,
            "evidence_complete": True,
            "photonic_state": {
                "intensity": 1.0,
                "q": 0.2,
                "u": 0.2,
                "v": 0.2
            }
        }

    def test_report_preserves_token_vazio_without_physics_gate(self):
        report = MODULE.build_report(self.payload())
        self.assertEqual(
            report["screen"]["classification"],
            "R_TOKEN_VAZIO",
        )
        self.assertEqual(report["gate"]["state"], "BOTH")
        self.assertEqual(report["photonic_invariant_errors"], [])

    def test_invalid_lengths_fail(self):
        payload = self.payload()
        payload["predicted"] = [1.0]
        with self.assertRaises(ValueError):
            MODULE.build_report(payload)


if __name__ == "__main__":
    unittest.main()
