from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
ADAPTER_PATH = ROOT / "tools/rll_studio_receipt_adapter.py"
SPEC = importlib.util.spec_from_file_location("rll_studio_receipt_adapter", ADAPTER_PATH)
assert SPEC and SPEC.loader
adapter = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(adapter)


def base_receipt(state: str = "VERIFIED_LIMITED") -> dict:
    return {
        "schema": "rll_evidence_receipt_v1",
        "created_utc": "2026-08-08T20:00:00+00:00",
        "experiment_id": "RLL-EVIDENCE-TEST-001",
        "experiment_title": "Joint test",
        "experiment_path": "products/rll-evidence-runner/experiments/test.yml",
        "experiment_sha256": "1" * 64,
        "commit_sha": "2" * 40,
        "runtime": {"platform": "Linux-test"},
        "inputs": [
            {
                "id": "data",
                "path": "data/test.csv",
                "required": True,
                "exists": True,
                "bytes": 10,
                "sha256": "3" * 64,
                "state": "VERIFIED",
            }
        ],
        "steps": [
            {
                "id": "run",
                "argv": ["python", "run.py"],
                "required": True,
                "exit_code": 0,
                "timed_out": False,
                "duration_seconds": 0.25,
                "state": "PASS",
                "outputs": [],
            }
        ],
        "extractions": [
            {
                "id": "rows",
                "path": "results/test.json",
                "state": "VERIFIED_LIMITED",
                "models": {
                    "LCDM": {"chi2": 10.0, "AIC": 14.0},
                    "RLL": {"chi2": 11.0, "AIC": 17.0},
                },
                "errors": [],
            }
        ],
        "comparisons": [
            {
                "baseline": "LCDM",
                "candidate": "RLL",
                "state": "VERIFIED_LIMITED",
                "candidate_minus_baseline": {"chi2": 1.0, "AIC": 3.0},
                "claim_allowed": False,
            }
        ],
        "decision": {
            "state": state,
            "claim_allowed": False,
            "publication_effect": "NONE",
            "F_ok": ["receipt materialized"],
            "F_gap": ["independent replication"],
            "F_next": ["external reproduction"],
        },
        "semantic_sha256": "4" * 64,
        "receipt_sha256": "5" * 64,
        "claim_allowed": False,
    }


class StudioReceiptAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        schema = json.loads((ROOT / "schemas/rll-experiment-manifest.v1.schema.json").read_text(encoding="utf-8"))
        cls.validator = Draft202012Validator(schema)

    def adapt(self, state: str = "VERIFIED_LIMITED") -> dict:
        manifest = adapter.adapt_receipt_document(
            base_receipt(state), source_receipt="artifacts/test/receipt.json", verification_state="PASS"
        )
        errors = list(self.validator.iter_errors(manifest))
        self.assertEqual(errors, [], [error.message for error in errors])
        return manifest

    def test_verified_limited_is_observed_limited_not_claim_pass(self) -> None:
        manifest = self.adapt("VERIFIED_LIMITED")
        self.assertEqual(manifest["manifest_state"], "OBSERVED_LIMITED")
        self.assertEqual(manifest["execution"]["state"], "PASS")
        self.assertFalse(manifest["claim"]["allowed"])
        self.assertEqual(manifest["claim"]["state"], "BLOCKED")
        self.assertEqual(manifest["provenance"]["verification_state"], "PASS")

    def test_required_input_gap_remains_token_vazio(self) -> None:
        receipt = base_receipt("TOKEN_VAZIO_REQUIRED_INPUT")
        receipt["inputs"][0]["exists"] = False
        receipt["inputs"][0]["sha256"] = None
        receipt["inputs"][0]["state"] = "TOKEN_VAZIO_INPUT_MISSING"
        receipt["steps"] = []
        manifest = adapter.adapt_receipt_document(
            receipt, source_receipt="artifacts/test/receipt.json", verification_state="PASS"
        )
        self.assertEqual(manifest["manifest_state"], "TOKEN_VAZIO")
        self.assertEqual(manifest["execution"]["state"], "BLOCKED")
        self.assertIn("TOKEN_VAZIO", {item["state"] for item in manifest["evidence"]})

    def test_result_gap_preserves_successful_execution_without_promoting_claim(self) -> None:
        manifest = self.adapt("TOKEN_VAZIO_RESULT")
        self.assertEqual(manifest["manifest_state"], "TOKEN_VAZIO")
        self.assertEqual(manifest["execution"]["state"], "PASS")
        self.assertFalse(manifest["claim"]["allowed"])

    def test_blocked_execution_maps_to_fail(self) -> None:
        manifest = self.adapt("BLOCKED_EXECUTION")
        self.assertEqual(manifest["manifest_state"], "BLOCKED")
        self.assertEqual(manifest["execution"]["state"], "FAIL")

    def test_verification_failure_is_rejected(self) -> None:
        with self.assertRaises(adapter.AdapterError):
            adapter.adapt_receipt_document(
                base_receipt(), source_receipt="receipt.json", verification_state="FAIL"
            )

    def test_claim_allowed_true_is_rejected(self) -> None:
        receipt = base_receipt()
        receipt["claim_allowed"] = True
        with self.assertRaises(adapter.AdapterError):
            adapter.adapt_receipt_document(receipt, source_receipt="receipt.json", verification_state="PASS")

    def test_decision_claim_boundary_is_rejected_if_mutated(self) -> None:
        receipt = base_receipt()
        receipt["decision"]["publication_effect"] = "PUBLISH"
        with self.assertRaises(adapter.AdapterError):
            adapter.adapt_receipt_document(receipt, source_receipt="receipt.json", verification_state="PASS")


if __name__ == "__main__":
    unittest.main()
