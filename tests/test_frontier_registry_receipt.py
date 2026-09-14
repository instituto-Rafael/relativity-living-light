import json
from pathlib import Path

from tools.frontier_registry_receipt import build_receipt, render_text


CONTRACT = Path("data/contracts/cosmology_model_family_shadow.v1.json")


def test_registry_receipt_is_non_promotional_and_complete():
    payload = build_receipt(CONTRACT)
    assert payload["schema"] == "rll.frontier_model_registry_receipt.v1"
    assert payload["model_count"] == 15
    assert payload["core_model_count"] == 10
    assert payload["composition_model_count"] == 5
    assert payload["claim_allowed"] is False
    assert payload["publication_effect"] == "NONE"
    assert payload["canonical_outputs_modified"] is False
    assert len(payload["contract_sha256"]) == 64


def test_registry_receipt_preserves_explicit_residuals():
    payload = build_receipt(CONTRACT)
    assert "TOKEN_VAZIO_ROBUST_MULTI_SEED_RECEIPT" in payload["residuals"]
    assert "TOKEN_VAZIO_PERTURBATION_BACKEND" in payload["residuals"]
    assert "TOKEN_VAZIO_INDEPENDENT_REPLICATION" in payload["residuals"]


def test_text_render_is_deterministic_and_machine_readable():
    payload = build_receipt(CONTRACT)
    first = render_text(payload)
    second = render_text(json.loads(json.dumps(payload)))
    assert first == second
    assert "claim_allowed=false" in first
    assert "model_ids=" in first
