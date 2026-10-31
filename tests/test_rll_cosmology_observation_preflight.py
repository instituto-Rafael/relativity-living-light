"""Isolated stdlib tests; no external dataset, API, fit, or write."""
import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/rll_cosmology_observation_preflight.py"
spec = importlib.util.spec_from_file_location("rll_observation_preflight", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PreflightTests(unittest.TestCase):
    def test_consistent_diagonal(self):
        rows = [{"sigma": "2", "tracer": "A", "observable": "DM_over_rd"},
                {"sigma": "3", "tracer": "B", "observable": "DH_over_rd"}]
        self.assertEqual(module.covariance_gate(rows, [[4, 0], [0, 9]])["state"], "PASS_DIAGONAL_SYMMETRY_ONLY")

    def test_swapped_sigma_blocked(self):
        rows = [{"sigma": "2", "tracer": "A", "observable": "DM_over_rd"},
                {"sigma": "3", "tracer": "B", "observable": "DH_over_rd"}]
        got = module.covariance_gate(rows, [[9, 0], [0, 4]])
        self.assertEqual(got["state"], "BLOCKED_COVARIANCE_ALIGNMENT")
        self.assertEqual({f["index"] for f in got["failures"]}, {0, 1})

    def test_shape_fail_closed(self):
        rows = [{"sigma": "1", "tracer": "A", "observable": "DV_over_rd"}]
        self.assertEqual(module.covariance_gate(rows, [[1, 0], [0, 1]])["state"], "BLOCKED_DIMENSION")

    def test_normalization_fail(self):
        joint = {"rows": [{"model": m, "Om": .35, "OL": .91,
                           "H0": 60, "Os0": 0} for m in module.MODELS]}
        got = module.normalization_gate(joint)
        self.assertEqual(got["state"], "BLOCKED_NORMALIZATION")
        self.assertTrue(all(x["state"] == "BLOCKED_E0_NOT_UNITY" for x in got["rows"]))

    def test_normalization_pass(self):
        joint = {"rows": [{"model": m, "Om": .3,
                           "OL": 1 - .3 - module.ORAD,
                           "H0": 70, "Os0": 0} for m in module.MODELS]}
        self.assertEqual(module.normalization_gate(joint)["state"], "PASS")

    def test_not_a_claim(self):
        from tempfile import TemporaryDirectory
        import csv
        import json
        with TemporaryDirectory() as d:
            root = Path(d)
            for p in (module.POINTS, module.COV, module.JOINT):
                (root / p).parent.mkdir(parents=True, exist_ok=True)
            with (root / module.POINTS).open("w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=["tracer", "observable", "sigma"])
                w.writeheader()
                w.writerow({"tracer": "BGS", "observable": "DV_over_rd", "sigma": 1})
            (root / module.COV).write_text(",0\n0,1\n")
            (root / module.JOINT).write_text(json.dumps({"rows": [
                {"model": m, "Om": .3, "OL": .7 - module.ORAD,
                 "H0": 70, "Os0": None} for m in module.MODELS]}))
            report = module.evaluate(root)
            self.assertFalse(report["claim_allowed"])
            self.assertFalse(report["parameters_changed"])
            self.assertEqual(report["external_2026_observations"]["lyalpha_2026"]["joint_covariance_with_2025"], "TOKEN_VAZIO")


if __name__ == "__main__":
    unittest.main()
