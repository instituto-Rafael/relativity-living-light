from __future__ import annotations

import importlib.util
import json
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "rll_modern_validation_gate.py"
spec = importlib.util.spec_from_file_location("rll_modern_validation_gate", MODULE_PATH)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

REPO = Path(__file__).resolve().parents[1]
REGISTRY_PATH = REPO / "data" / "governance" / "RLL_MODERN_VALIDATION_GAPS_20260807_V1.json"


def _registry(path: str = "artifacts/test/receipt.json") -> dict:
    return {
        "schema": module.REGISTRY_SCHEMA,
        "claim_allowed": False,
        "publication_ready": False,
        "policy": {
            "token_vazio_is_auditable_state": True,
            "paper_is_context_not_materialized_evidence": True,
            "bic_proxy_is_not_bayesian_evidence": True,
            "backend_import_is_not_perturbation_validation": True,
            "dataset_name_is_not_likelihood_provenance": True,
            "all_models_must_share_data_priors_and_nuisance_policy": True,
            "negative_results_must_be_preserved": True,
        },
        "gates": [
            {
                "id": "RLL-TEST-P0",
                "priority": "P0",
                "token_vazio": "TOKEN_VAZIO_TEST_EVIDENCE",
                "required_artifacts": [
                    {
                        "id": "test_receipt",
                        "path": path,
                        "expected_state": "VERIFIED",
                        "required_keys": ["source_sha256", "result"],
                    }
                ],
            }
        ],
    }


def test_missing_receipt_remains_token_vazio(tmp_path: Path) -> None:
    receipt = module.evaluate_registry(_registry(), tmp_path)
    assert receipt["scientific_gate"] == "BLOCKED_P0_TOKEN_VAZIO"
    assert receipt["claim_allowed"] is False
    assert receipt["publication_ready"] is False
    assert receipt["token_vazio"] == ["TOKEN_VAZIO_TEST_EVIDENCE"]
    assert receipt["gates"][0]["artifacts"][0]["reasons"] == ["missing_receipt"]


def test_verified_materialized_receipt_closes_only_the_declared_gap(tmp_path: Path) -> None:
    rel = Path("artifacts/test/receipt.json")
    path = tmp_path / rel
    path.parent.mkdir(parents=True)
    path.write_text(
        json.dumps(
            {
                "state": "VERIFIED",
                "claim_allowed": False,
                "source_sha256": "a" * 64,
                "result": {"chi2": 12.5},
            }
        ),
        encoding="utf-8",
    )
    receipt = module.evaluate_registry(_registry(rel.as_posix()), tmp_path)
    assert receipt["all_gates_verified"] is True
    assert receipt["scientific_gate"] == "READY_FOR_INDEPENDENT_HUMAN_REVIEW"
    assert receipt["token_vazio"] == []
    assert receipt["claim_allowed"] is False


def test_claim_allowed_true_is_rejected_even_if_state_verified(tmp_path: Path) -> None:
    rel = Path("artifacts/test/receipt.json")
    path = tmp_path / rel
    path.parent.mkdir(parents=True)
    path.write_text(
        json.dumps(
            {
                "state": "VERIFIED",
                "claim_allowed": True,
                "source_sha256": "b" * 64,
                "result": 1.0,
            }
        ),
        encoding="utf-8",
    )
    receipt = module.evaluate_registry(_registry(rel.as_posix()), tmp_path)
    reasons = receipt["gates"][0]["artifacts"][0]["reasons"]
    assert "claim_allowed_must_be_false" in reasons
    assert receipt["all_gates_verified"] is False


def test_bayes_receipt_requires_independent_replication_true(tmp_path: Path) -> None:
    contract = {
        "expected_state": "VERIFIED",
        "required_keys": ["logz", "logz_error", "independent_replication"],
    }
    path = tmp_path / "bayes.json"
    path.write_text(
        json.dumps(
            {
                "state": "VERIFIED",
                "claim_allowed": False,
                "logz": {"LCDM": -100.0, "RLL": -105.0},
                "logz_error": {"LCDM": 0.2, "RLL": 0.3},
                "independent_replication": False,
            }
        ),
        encoding="utf-8",
    )
    verified, reasons, _ = module.validate_materialized_receipt(path, contract)
    assert verified is False
    assert "independent_replication_not_true" in reasons


def test_canonical_registry_is_fail_closed_and_has_modern_observation_gates() -> None:
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    module.validate_registry(registry)
    gate_ids = {gate["id"] for gate in registry["gates"]}
    assert {
        "RLL-MOD-P0-SN-CALIBRATION-COVARIANCE",
        "RLL-MOD-P0-REAL-BAYES",
        "RLL-MOD-P0-DESI-DR2-REPRODUCTION",
        "RLL-MOD-P1-CMB-ACT-DR6",
        "RLL-MOD-P1-DES-Y6-WEAK-LENSING",
        "RLL-MOD-P1-CLASS-CAMB-PERTURBATIONS",
        "RLL-MOD-P1-H0-DISTANCE-LADDER",
    }.issubset(gate_ids)
    assert registry["claim_allowed"] is False
    assert registry["publication_ready"] is False
    assert all(str(gate["token_vazio"]).startswith("TOKEN_VAZIO_") for gate in registry["gates"])
