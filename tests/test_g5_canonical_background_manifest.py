import copy
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools/build_g5_canonical_background_manifest.py"


def load_module():
    spec = importlib.util.spec_from_file_location("g5", MODULE_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def minimal_passing_receipt():
    return {
        "schema": "rll.g4_background_tournament_receipt.v1",
        "state": "PASS_LIMITED_G4_BACKGROUND_TOURNAMENT",
        "claim_allowed": False,
        "scientific_confirmation": False,
        "negative_results_preserved": True,
        "null_limits": {"passed": True},
        "datasets": {"growth_CMB_policy": "DEFER_TO_G8_G9_NO_PROXY_PROMOTION"},
        "input_sha256": {"x": "a" * 64},
        "rows": [
            {"model": model, "chi2": 1.0, "AIC": 2.0, "AICc": 2.1, "BIC": 3.0, "N": 10, "k": 1, "dof": 9}
            for model in ["LCDM", "wCDM", "CPL", "GEDE", "IDE_QrhoLambda", "RLL"]
        ],
        "deltas_vs_LCDM": {},
        "created_utc": "2026-08-19T00:00:00Z",
    }


def test_g5_rejects_nonpass_g4():
    mod = load_module()
    receipt = minimal_passing_receipt()
    receipt["state"] = "BLOCKED_G4_BACKGROUND_TOURNAMENT"
    errors = mod.validate_g4_receipt(receipt)
    assert any("not PASS_LIMITED" in error for error in errors)


def test_g5_rejects_claim_promotion_and_missing_model():
    mod = load_module()
    receipt = minimal_passing_receipt()
    receipt["claim_allowed"] = True
    receipt["rows"].pop()
    errors = mod.validate_g4_receipt(receipt)
    assert "G4 claim_allowed must be false" in errors
    assert any("mandatory model order mismatch" in error for error in errors)


def test_g5_rejects_malformed_input_hash_and_growth_proxy_drift():
    mod = load_module()
    receipt = minimal_passing_receipt()
    receipt["input_sha256"] = {"x": "1234"}
    receipt["datasets"]["growth_CMB_policy"] = "USED_APPROXIMATE_GROWTH"
    errors = mod.validate_g4_receipt(receipt)
    assert any("invalid input hash" in error for error in errors)
    assert "growth/CMB deferral boundary changed" in errors


def test_g5_contract_never_allows_claim():
    contract = json.loads((ROOT / "data/contracts/rll_g5_canonical_background_likelihood.v1.json").read_text())
    assert contract["claim_allowed"] is False
    assert contract["scientific_confirmation"] is False
    assert "READY_G5_CANONICAL_BACKGROUND_LIKELIHOOD != Bayesian evidence" in contract["boundary"]
