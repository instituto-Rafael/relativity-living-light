import copy
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "tools/validate_ethics_license_complexity_sustainment.py"
REGISTRY = ROOT / "governance/ethics_license_complexity_sustainment.v1.json"

spec = importlib.util.spec_from_file_location("ethics_license_validator", VALIDATOR)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(mod)


def registry():
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def test_registry_passes_fail_closed_validator():
    data = registry()
    mod.validate_graph(data, ROOT)
    text = mod.summary(data)
    assert "nodes=9" in text
    assert "edges=6" in text
    assert "tokens=8" in text
    assert "P0=3" in text
    assert "claim_allowed=false" in text
    assert "legal_effect_claim=false" in text


def test_claim_promotion_is_rejected():
    data = registry()
    data["claim_allowed"] = True
    with pytest.raises(ValueError, match="claim_allowed"):
        mod.validate_graph(data, ROOT)


def test_legal_effect_promotion_is_rejected():
    data = registry()
    data["legal_effect_claim"] = True
    with pytest.raises(ValueError, match="legal_effect_claim"):
        mod.validate_graph(data, ROOT)


def test_standard_spdx_equivalence_is_not_invented():
    data = registry()
    data["license_interoperability"]["spdx_standard_identifier"] = True
    with pytest.raises(ValueError, match="SPDX"):
        mod.validate_graph(data, ROOT)


def test_unknown_third_party_rights_fail_closed():
    data = registry()
    data["license_interoperability"]["third_party_redistribution_default"] = "ALLOW"
    with pytest.raises(ValueError, match="redistribution"):
        mod.validate_graph(data, ROOT)


def test_dangling_complex_network_edge_is_rejected():
    data = registry()
    data["complex_network"]["edges"][0]["target"] = "NODE-DOES-NOT-EXIST"
    with pytest.raises(ValueError, match="dangling edge"):
        mod.validate_graph(data, ROOT)


def test_duplicate_token_id_is_rejected():
    data = registry()
    data["open_tokens"].append(copy.deepcopy(data["open_tokens"][0]))
    with pytest.raises(ValueError, match="duplicate TOKEN_VAZIO"):
        mod.validate_graph(data, ROOT)


def test_token_cannot_disappear_without_receipt():
    old = registry()
    new = copy.deepcopy(old)
    new["open_tokens"] = new["open_tokens"][:-1]
    with pytest.raises(ValueError, match="disappeared without receipt"):
        mod.assert_non_regression(old, new, ROOT)


def test_token_can_close_with_structured_hash_bound_receipt():
    old = registry()
    new = copy.deepcopy(old)
    removed = new["open_tokens"].pop()
    new["closure_receipts"].append({
        "schema": "rll.token_vazio_closure_receipt.v1",
        "gap_id": removed["id"],
        "artifact_path": "artifacts/governance/example_closure_receipt.json",
        "sha256": "a" * 64,
        "commit_sha": "b" * 40,
        "result": "CLOSED_BY_EVIDENCE",
        "claim_allowed": False,
    })
    mod.assert_non_regression(old, new, ROOT)


def test_text_only_fake_receipt_is_rejected():
    old = registry()
    new = copy.deepcopy(old)
    removed = new["open_tokens"].pop()
    new["closure_receipts"].append({"gap_id": removed["id"], "receipt": "done"})
    with pytest.raises(ValueError, match="closure receipt schema"):
        mod.assert_non_regression(old, new, ROOT)


def test_historical_edge_cannot_be_rewritten():
    old = registry()
    new = copy.deepcopy(old)
    new["complex_network"]["edges"][0]["claim_boundary"] = "PROMOTED"
    with pytest.raises(ValueError, match="historical edge mutated"):
        mod.assert_non_regression(old, new, ROOT)


def test_parable_cannot_be_promoted_to_runtime_proof():
    data = registry()
    data["parable_router"]["epistemic_status"] = "PROVADO"
    with pytest.raises(ValueError, match="PARABOLA"):
        mod.validate_graph(data, ROOT)


def test_no_limit_phrase_keeps_measurable_runtime_boundary():
    data = registry()
    data["parable_router"]["runtime_boundary"] = "no boundaries exist"
    with pytest.raises(ValueError, match="operational limits"):
        mod.validate_graph(data, ROOT)


def test_ethics_physical_field_cannot_silently_become_evidence():
    data = registry()
    data["ethics_by_design"]["physical_field_status"] = "EVIDENCIADO"
    with pytest.raises(ValueError, match="physical_field_status"):
        mod.validate_graph(data, ROOT)
