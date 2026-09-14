import copy
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools/validate_scientific_validation_orchestrator_v3.py"
RECEIPT_PATH = ROOT / "artifacts/pantheon/RLL_PANTHEON_FULL_COVARIANCE_MATERIALIZATION_RECEIPT_20260819_RUN32285275333.json"


def load_module():
    spec = importlib.util.spec_from_file_location("sv3", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_persisted_receipt_closes_g2_but_not_g3_g4_g5():
    mod = load_module()
    report = mod.build_readiness(ROOT)
    assert report["g2_ready"] is True
    assert report["gate_states"]["G2"] == mod.READY_G2_RECEIPT
    assert report["gate_states"]["G3"] == "READY_TO_EXECUTE_COMPATIBILITY_NOT_PASSED"
    assert report["gate_states"]["G4"] == "BLOCKED_BY_G3_RESULT"
    assert report["gate_states"]["G5"] == "BLOCKED_BY_G3_G4"
    assert report["claim_allowed"] is False
    assert report["scientific_confirmation"] is False
    assert "TOKEN_VAZIO_FULL_COVARIANCE" not in report["token_vazio"]


def test_receipt_exact_primary_hashes_are_required():
    mod = load_module()
    receipt = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    tampered = copy.deepcopy(receipt)
    tampered["files"]["Pantheon+SH0ES_STAT+SYS.cov"]["sha256"] = "0" * 64
    errors = mod.validate_pantheon_receipt(tampered)
    assert any("covariance SHA-256 mismatch" in error for error in errors)


def test_receipt_cannot_promote_claim_allowed():
    mod = load_module()
    receipt = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    receipt["claim_allowed"] = True
    errors = mod.validate_pantheon_receipt(receipt)
    assert "receipt claim_allowed must remain false" in errors


def test_receipt_requires_exact_matrix_value_count():
    mod = load_module()
    receipt = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    receipt["files"]["Pantheon+SH0ES_STAT+SYS.cov"]["matrix_values"] -= 1
    errors = mod.validate_pantheon_receipt(receipt)
    assert any("covariance value count mismatch" in error for error in errors)


def test_missing_receipt_fails_closed(tmp_path):
    mod = load_module()
    report = mod.build_readiness(ROOT, tmp_path / "missing.json")
    assert report["g2_ready"] is False
    assert report["gate_states"]["G2"] == "BLOCKED_BY_G2_RECEIPT_VALIDATION"
    assert "TOKEN_VAZIO_OR_BLOCKED_G2_RECEIPT" in report["token_vazio"]


def test_desi_binding_remains_repo_local_not_external_proof():
    mod = load_module()
    report = mod.build_readiness(ROOT)
    boundary = report["desi_order_binding"]["provenance_boundary"]
    assert report["desi_order_binding"]["valid"] is True
    assert boundary["repo_order_binding"] == "VERIFIED"
    assert "BOUNDED_BY_REPO_DOCUMENTATION" in boundary["external_primary_covariance_order_metadata"]
