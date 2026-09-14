from __future__ import annotations

import json
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rll.mathematics_registry_adapter import (  # noqa: E402
    classify_artifact,
    summarize_registry,
    validate_envelope,
    validate_registry,
)

PIN = "34b7c638bd17997572b1fd6736b54c91b6d076f2"
BLOB = "3063fb66016b54081f202f3b8b6e0df212f7f269"
FIXTURE = ROOT / "tests" / "fixtures" / "mathematics_registry_emulation.json"


def load_registry():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


class MathematicsRegistryAdapterTests(unittest.TestCase):
    def test_valid_emulated_contract_passes(self):
        registry = load_registry()
        self.assertEqual(validate_registry(registry), [])
        summary = summarize_registry(registry)
        self.assertEqual(summary["status"], "PASS_EMULATED_CONTRACT")
        self.assertFalse(summary["claim_allowed"])
        self.assertFalse(summary["physical_promotion_performed"])

    def test_envelope_pins_repository_commit_and_blob(self):
        envelope = {
            "producer_repo": "rafaelmeloreisnovo/Matem-tica-",
            "producer_commit": PIN,
            "registry_blob_sha": BLOB,
            "payload": load_registry(),
        }
        self.assertEqual(
            validate_envelope(envelope, expected_commit=PIN, expected_blob_sha=BLOB), []
        )

    def test_token_vazio_cannot_be_zero_vector(self):
        registry = load_registry()
        registry["artifacts"][0]["vector"]["value"] = [0.0, 0.0, 0.0]
        errors = validate_registry(registry)
        self.assertTrue(any("TOKEN_VAZIO vector value must be null" in error for error in errors))

    def test_synthetic_data_cannot_be_observational(self):
        registry = load_registry()
        bridge = registry["artifacts"][2]
        bridge["data"]["real_world_observation"] = True
        errors = validate_registry(registry)
        self.assertTrue(any("REAL_OBSERVATIONAL_DATA_PIPELINE" in error for error in errors))

    def test_coupled_vector_requires_labels_and_source(self):
        registry = load_registry()
        model = registry["artifacts"][3]
        model["vector"].pop("source")
        model["vector"]["labels"] = ["H0"]
        errors = validate_registry(registry)
        self.assertTrue(any("labels must match" in error for error in errors))
        self.assertTrue(any("requires a source" in error for error in errors))

    def test_global_claim_gate_is_fail_closed(self):
        registry = load_registry()
        registry["claim_allowed"] = True
        self.assertIn("claim_allowed must remain false", validate_registry(registry))

    def test_physical_token_vazio_is_context_only(self):
        registry = load_registry()
        self.assertEqual(
            classify_artifact(registry["artifacts"][1]),
            "CONTEXT_ONLY_TOKEN_VAZIO",
        )

    def test_real_rll_posterior_is_inference_ready_not_physical_truth(self):
        registry = load_registry()
        self.assertEqual(
            classify_artifact(registry["artifacts"][3]),
            "OBSERVATIONAL_INFERENCE_READY",
        )
        self.assertEqual(
            registry["artifacts"][3]["claim_state"],
            "CURRENT_PARAMETRIZATION_DISFAVORED_VS_LCDM",
        )

    def test_wrong_pin_is_rejected(self):
        envelope = {
            "producer_repo": "rafaelmeloreisnovo/Matem-tica-",
            "producer_commit": "a" * 40,
            "registry_blob_sha": BLOB,
            "payload": load_registry(),
        }
        errors = validate_envelope(envelope, expected_commit=PIN, expected_blob_sha=BLOB)
        self.assertTrue(any("pinned contract" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
