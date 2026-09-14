from __future__ import annotations

import unittest

from tools.rll_perturbation_barotropic_candidate_v1 import build, evaluate_case


class BarotropicClosureCandidateTests(unittest.TestCase):
    def test_background_derived_candidate_is_fail_closed(self):
        payload = build()
        self.assertFalse(payload["claim_allowed"])
        self.assertFalse(payload["publication_ready"])
        self.assertEqual(payload["token"], "TOKEN_VAZIO_RLL_PERTURBATION_CLOSURE_RELATIONS")
        self.assertEqual(payload["resolved_token"], None)
        self.assertEqual(payload["reduces_token"], "TOKEN_VAZIO_RLL_PERTURBATION_CLOSURE_RELATIONS")
        self.assertEqual(len(payload["sweep"]["cases"]), 9)

    def test_canonical_transition_exposes_nontrivial_sound_speed_problem(self):
        row = evaluate_case(1.0, 0.3)
        self.assertTrue(row["rho_positive"])
        self.assertFalse(row["pass"])
        self.assertLess(row["stable_causal_fraction"], 1.0)
        self.assertIsNotNone(row["first_stability_or_causality_violation"])

    def test_negative_candidate_result_does_not_resolve_theory_token(self):
        payload = build()
        self.assertEqual(payload["state"], "FALSIFIED_AS_GLOBAL_DEFAULT")
        self.assertIn("rest-frame sound-speed", " ".join(payload["next_required_decisions"]))
        self.assertIn("not validation or falsification", payload["scientific_boundary"])


if __name__ == "__main__":
    unittest.main()
