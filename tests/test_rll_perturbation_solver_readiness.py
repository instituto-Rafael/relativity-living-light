from __future__ import annotations

import unittest

from tools.rll_perturbation_solver_readiness import build


class RllPerturbationSolverReadinessTests(unittest.TestCase):
    def test_solver_handoff_remains_fail_closed(self):
        payload = build()
        self.assertEqual(
            payload["state"],
            "BLOCKED_AS_EXPECTED_PHYSICAL_DERIVATION_REQUIRED",
        )
        self.assertFalse(payload["class_camb_unlock"])
        self.assertFalse(payload["claim_allowed"])
        self.assertEqual(
            set(payload["open_hard_slots"]),
            {
                "C01_DELTA_S",
                "C02_THETA_S",
                "C07_GAUGE_AND_INITIAL_CONDITIONS",
                "C08_TRANSITION_REGULARIZATION",
            },
        )

    def test_class_and_camb_are_not_prematurely_implemented(self):
        payload = build()
        self.assertEqual(payload["class_state"], "NOT_IMPLEMENTED_RLL_PERTURBATIONS")
        self.assertEqual(payload["camb_state"], "NOT_IMPLEMENTED_RLL_PERTURBATIONS")
        self.assertTrue(payload["checks"]["constraint_bianchi_gate_declared"])


if __name__ == "__main__":
    unittest.main()
