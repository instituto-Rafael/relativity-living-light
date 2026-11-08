"""Structural test only. No scientific model evidence or simulation."""
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILE = ROOT / "tools/ci/rll_warmstart_preflight_v1.py"
spec = importlib.util.spec_from_file_location("warm", FILE)
warm = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(warm)


class WarmstartPreflight(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = warm.preflight(ROOT)

    def test_archive_blob_identity(self):
        n, e = warm.archive_gate(ROOT)
        self.assertEqual((n, e), (133, []))

    def test_real_input_metadata(self):
        self.assertEqual(self.r["state"], "PASS_SCOPED_DATA_PREFLIGHT")
        self.assertEqual(self.r["errors"], [])

    def test_seven_not_computed_from_background(self):
        self.assertEqual(len(self.r["seven_parameter_names"]), 7)
        self.assertEqual(self.r["seven_parameter_fit"], "NOT_RUN_REQUIRES_FULL_CMB")
        self.assertFalse(self.r["claim_allowed"])

    def test_six_baseline_models(self):
        self.assertEqual(self.r["models"], list(warm.SIX))

    def test_covariance_positive_definite(self):
        good = [[float(i == j) for j in range(13)] for i in range(13)]
        warm.check_covariance(good)
        bad = [[0.0] * 13 for _ in range(13)]
        with self.assertRaises(ValueError):
            warm.check_covariance(bad)

    def test_materialization_required_if_not_present(self):
        if not (ROOT / warm.COV).is_file():
            bad = warm.preflight(ROOT, require_materialized=True)
            self.assertIn("PANTHEON_FULL_COVARIANCE_RECEIPT_REQUIRED", bad["errors"])

    def test_no_archived_yaml_executable_path(self):
        x = warm.load(ROOT, warm.INDEX)
        self.assertTrue(all(not e["archive_path"].startswith(".github/workflows/")
                            for e in x["entries"]))

    def test_manual_entrypoints_preserve_engine(self):
        for p in ("RLL-CI.yml", "RLL_SCIENTIFIC.yml", "bayes_analysis.yml"):
            s = (ROOT / ".github/workflows" / p).read_text()
            self.assertIn("workflow_dispatch:", s)
            self.assertIn("canonical-science:", s)
            self.assertIn("uses: ./.github/workflows/rll-pipeline-linear-completo.yml", s)
            self.assertIn("modo: apenas_ciencia", s)


if __name__ == "__main__":
    unittest.main()
