from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRODUCT = ROOT / "products/rll-evidence-runner"
sys.path.insert(0, str(PRODUCT / "src"))

from rll_evidence.core import compare_receipt, run_experiment, validate_experiment, verify_receipt  # noqa: E402


class EvidenceRunnerV1Tests(unittest.TestCase):
    def _fixture(self, root: Path) -> Path:
        (root / "products/rll-evidence-runner/schemas").mkdir(parents=True)
        schema = json.loads((PRODUCT / "schemas/experiment.schema.json").read_text())
        (root / "products/rll-evidence-runner/schemas/experiment.schema.json").write_text(json.dumps(schema))
        (root / "data").mkdir()
        (root / "data/input.txt").write_text("evidence\n")
        (root / "results").mkdir()
        (root / "results/models.json").write_text(json.dumps({"rows": [
            {"model": "LCDM", "chi2": 10.0, "AIC": 14.0, "AICc": 15.0, "BIC": 16.0},
            {"model": "RLL", "chi2": 9.0, "AIC": 17.0, "AICc": 18.0, "BIC": 20.0}
        ]}))
        experiment = root / "experiment.yml"
        experiment.write_text("""schema: rll_evidence_experiment_v1
experiment_id: TEST-EVIDENCE-001
title: Deterministic fixture
repository_root: .
claim_allowed: false
publication_effect: NONE
inputs:
  - id: input
    path: data/input.txt
    required: true
steps:
  - id: check
    argv: [python, -c, \"from pathlib import Path; assert Path('data/input.txt').stat().st_size == 9\"]
    outputs:
      - path: results/models.json
result_extractors:
  - id: models
    path: results/models.json
    rows_path: [rows]
    include_models: [LCDM, RLL]
comparisons:
  - baseline: LCDM
    candidate: RLL
receipt:
  path: artifacts/receipt.json
F_ok: [fixture]
F_gap: []
F_next: [external reproduction]
""")
        return experiment

    def test_run_verify_compare(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            experiment = self._fixture(root)
            validation = validate_experiment(experiment, root)
            self.assertEqual(validation["state"], "VALID")
            receipt = run_experiment(experiment, root)
            self.assertEqual(receipt["decision"]["state"], "VERIFIED_LIMITED")
            self.assertFalse(receipt["claim_allowed"])
            receipt_path = root / "artifacts/receipt.json"
            self.assertEqual(verify_receipt(receipt_path, root)["state"], "PASS")
            comparison = compare_receipt(receipt_path, "LCDM", "RLL")
            self.assertEqual(comparison["candidate_minus_baseline"]["chi2"], -1.0)
            self.assertEqual(comparison["candidate_minus_baseline"]["BIC"], 4.0)

    def test_missing_required_input_is_token_vazio(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            experiment = self._fixture(root)
            (root / "data/input.txt").unlink()
            validation = validate_experiment(experiment, root)
            self.assertEqual(validation["state"], "VALID_WITH_TOKEN_VAZIO")
            receipt = run_experiment(experiment, root)
            self.assertEqual(receipt["decision"]["state"], "TOKEN_VAZIO_REQUIRED_INPUT")
            self.assertEqual(receipt["steps"], [])

    def test_claim_promotion_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            experiment = self._fixture(root)
            experiment.write_text(experiment.read_text().replace("claim_allowed: false", "claim_allowed: true"))
            validation = validate_experiment(experiment, root)
            self.assertEqual(validation["state"], "INVALID")
            self.assertTrue(any("claim_allowed" in item for item in validation["schema_errors"] + validation["policy_errors"]))

    def test_receipt_tamper_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            experiment = self._fixture(root)
            run_experiment(experiment, root)
            receipt_path = root / "artifacts/receipt.json"
            receipt = json.loads(receipt_path.read_text())
            receipt["experiment_id"] = "TAMPERED"
            receipt_path.write_text(json.dumps(receipt))
            verified = verify_receipt(receipt_path, root)
            self.assertEqual(verified["state"], "FAIL")
            self.assertIn("receipt SHA-256 mismatch", verified["errors"])


if __name__ == "__main__":
    unittest.main()
