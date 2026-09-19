import unittest

from scripts.rll_dual_observation_window import evaluate, spectral_entropy


def base_doc():
    return {
        "schema": "rll.dual_observation_window.input.v1",
        "observable": {"name": "normalized_flux", "unit": "1", "time_scale": "demo"},
        "observed": [1.0, 2.0, 3.0, 4.0],
        "baseline": [0.0, 1.0, 2.0, 3.0],
        "candidate": [1.0, 2.0, 3.0, 4.0],
        "uncertainty": [1.0, 1.0, 1.0, 1.0],
        "context_covariates": {"pressure_proxy": [0.0, 1.0, 2.0, 3.0]},
        "preregistration": {
            "delta_loss_tolerance": 0.0,
            "hard_falsifiers": [{"id": "F1", "state": "PASS"}],
        },
    }


class DualObservationWindowTests(unittest.TestCase):
    def test_support_channel(self):
        out = evaluate(base_doc())
        self.assertEqual(out["relative_fit"]["state"], "RELATIVE_SUPPORT")
        self.assertGreater(out["relative_fit"]["support_channel"], 0.0)
        self.assertEqual(out["relative_fit"]["opposition_channel"], 0.0)
        self.assertFalse(out["claim_allowed"])
        self.assertFalse(out["new_physics_detected"])

    def test_opposition_channel(self):
        doc = base_doc()
        doc["baseline"] = doc["observed"][:]
        doc["candidate"] = [0.0, 1.0, 2.0, 3.0]
        out = evaluate(doc)
        self.assertEqual(out["relative_fit"]["state"], "RELATIVE_OPPOSITION")
        self.assertGreater(out["relative_fit"]["opposition_channel"], 0.0)

    def test_hard_fail_does_not_erase_support(self):
        doc = base_doc()
        doc["preregistration"]["hard_falsifiers"] = [{"id": "F1", "state": "FAIL"}]
        out = evaluate(doc)
        self.assertEqual(out["relative_fit"]["state"], "BLOCKED_HARD_FALSIFIER")
        self.assertGreater(out["relative_fit"]["support_channel"], 0.0)
        self.assertTrue(out["hard_falsifiers"]["noncompensatory_block"])

    def test_unknown_uncertainty_is_not_zero(self):
        doc = base_doc()
        doc["uncertainty"][0] = 0.0
        with self.assertRaises(ValueError):
            evaluate(doc)

    def test_entropy_bounds(self):
        h = spectral_entropy([1.0, 0.0, -1.0, 0.0] * 4)
        self.assertIsNotNone(h)
        self.assertGreaterEqual(h, 0.0)
        self.assertLessEqual(h, 1.0)


if __name__ == "__main__":
    unittest.main()
