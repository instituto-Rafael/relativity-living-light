import csv
import json
import tempfile
import unittest
from pathlib import Path

from tools.ci_scientific_skills import (
    anomaly_diagnostic,
    bayes_proxy_diagnostic,
    fourier_torus_diagnostic,
    robust_anomaly_scores,
    run,
)


class CIScientificSkillsTests(unittest.TestCase):
    def test_robust_anomaly_detects_large_outlier(self):
        scores = robust_anomaly_scores([1.0, 1.1, 0.9, 1.05, 40.0])
        index = max(range(len(scores)), key=lambda i: abs(scores[i]))
        self.assertEqual(index, 4)
        self.assertGreater(abs(scores[4]), 3.5)

    def test_anomaly_diagnostic_records_input_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "observations.csv"
            with path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=["value"])
                writer.writeheader()
                for value in [1.0, 1.1, 0.9, 1.05, 40.0]:
                    writer.writerow({"value": value})
            report = anomaly_diagnostic(path)
            self.assertEqual(report["status"], "EVIDENCED_ON_REPOSITORY_DATA")
            self.assertEqual(report["anomaly_indices"], [4])
            self.assertEqual(len(report["input_sha256"]), 64)

    def test_fourier_torus_method_is_deterministic_and_precise(self):
        report = fourier_torus_diagnostic(samples=2048, max_mode=32)
        self.assertEqual(report["status"], "VERIFIED_METHOD")
        self.assertLess(report["rmse"], 1e-12)
        self.assertLess(report["tail_energy_after_mode_5"], 1e-24)
        self.assertEqual(report["space"], "T^1")

    def test_bayes_proxy_prefers_lower_bic(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "comparison.csv"
            with path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=["model", "BIC"])
                writer.writeheader()
                writer.writerows(
                    [
                        {"model": "lcdm", "BIC": 110.0},
                        {"model": "rll", "BIC": 116.0},
                    ]
                )
            report = bayes_proxy_diagnostic(path)
            self.assertEqual(report["preferred_by_bic"], "lcdm")
            self.assertEqual(report["delta_bic_alternative_minus_preferred"], 6.0)
            self.assertEqual(report["log_bayes_proxy_preferred_vs_alternative"], 3.0)

    def test_run_preserves_missing_evidence_as_token_vazio(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = root / "artifact" / "report.json"
            payload = run(root, output, strict=False)
            self.assertEqual(payload["overall_status"], "TOKEN_VAZIO")
            self.assertEqual(payload["skills"]["C1_anomaly_diagnostic"]["status"], "TOKEN_VAZIO")
            self.assertEqual(payload["skills"]["D1_bayes_proxy"]["status"], "TOKEN_VAZIO")
            self.assertTrue(output.is_file())
            self.assertEqual(json.loads(output.read_text(encoding="utf-8"))["schema"], payload["schema"])


if __name__ == "__main__":
    unittest.main()
