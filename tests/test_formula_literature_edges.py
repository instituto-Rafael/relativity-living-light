import copy
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "tools" / "validate_formula_literature_edges.py"
GRAPH_PATH = ROOT / "data" / "science" / "rll_formula_literature_edges.v1.json"

spec = importlib.util.spec_from_file_location("lit_edges_validator", VALIDATOR_PATH)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(mod)


def graph():
    return json.loads(GRAPH_PATH.read_text(encoding="utf-8"))


def formula_state(data, fid):
    return next(x for x in data["formula_states"] if x["formula_id"] == fid)


def closure(gap_id, *, kind="EVIDENCE_RECEIPT", total=None):
    receipt = {
        "schema": "rll.gap_closure_receipt.v1",
        "event_id": f"TEST-CLOSURE-{gap_id}",
        "gap_id": gap_id,
        "artifact_path": f"artifacts/test/{gap_id}.json",
        "artifact_sha256": "a" * 64,
        "immutable_event": True,
    }
    if total is not None:
        receipt["deduplicated_total"] = total
    return {"gap_id": gap_id, "closure_kind": kind, "receipt": receipt}


def test_seed_graph_passes_fail_closed_validator():
    mod.validate_graph(graph())


def test_claim_promotion_is_rejected():
    data = graph()
    data["claim_allowed"] = True
    with pytest.raises(ValueError, match="claim_allowed"):
        mod.validate_graph(data)


def test_pair_a_with_one_independence_group_fails():
    data = graph()
    h01 = formula_state(data, "H01")
    h01["state"] = "PAIR_A"
    h01["token_vazio"] = []
    h01["evidence_vector"]["external_concordance"] = "SUPPORT"
    data["edges"].append({
        "edge_id": "EDGE-H01-FAKE-SUPPORT",
        "formula_id": "H01",
        "reference_id": "REF_DESI_DR2_BAO_2503.14738",
        "relation": "SUPPORTS_EXACT",
        "independence_group": "IG_DESI_DR2_BAO",
        "scope": "adversarial fixture",
        "provenance": "test_fixture",
        "immutable_event": True,
    })
    with pytest.raises(ValueError, match="PAIR_A requires"):
        mod.validate_graph(data)


def test_pair_b_requires_multiple_exact_author_groups():
    data = graph()
    h01 = formula_state(data, "H01")
    h01["state"] = "PAIR_B"
    h01["token_vazio"] = []
    with pytest.raises(ValueError, match="PAIR_B requires"):
        mod.validate_graph(data)


def test_class_match_state_requires_class_match_edge():
    data = graph()
    h01 = formula_state(data, "H01")
    h01["state"] = "CLASS_MATCH"
    h01["token_vazio"] = []
    data["edges"] = [e for e in data["edges"] if e["formula_id"] != "H01"]
    h01["evidence_vector"]["independent_groups"] = 0
    h01["evidence_vector"]["false_positive_controls"] = 0
    with pytest.raises(ValueError, match="CLASS_MATCH state requires"):
        mod.validate_graph(data)


def test_class_match_cannot_close_exact_formula_gap():
    data = graph()
    h01 = formula_state(data, "H01")
    assert h01["state"] == "TOKEN_VAZIO_EXACT_TEST"
    assert any(e["formula_id"] == "H01" and e["relation"] == "CLASS_MATCH" for e in data["edges"])
    mod.validate_graph(data)


def test_token_vazio_without_cause_fails():
    data = graph()
    formula_state(data, "H01")["token_vazio"][0]["cause"] = ""
    with pytest.raises(ValueError, match="cause"):
        mod.validate_graph(data)


def test_external_two_plus_needs_two_independent_groups():
    data = graph()
    data["edges"] = [
        e for e in data["edges"]
        if not (e["formula_id"] == "H25" and e["independence_group"] == "IG_PULSAR_TIMING")
    ]
    h25 = formula_state(data, "H25")
    h25["evidence_vector"]["independent_groups"] = 1
    h25["evidence_vector"]["false_positive_controls"] = 2
    h25["evidence_vector"]["contradiction_strength"] = "SINGLE_PATH"
    with pytest.raises(ValueError, match="CONTRADICTED_EXTERNAL_2PLUS requires"):
        mod.validate_graph(data)


def test_duplicate_persistent_id_cannot_fake_independence():
    data = graph()
    alias = copy.deepcopy(data["references"][0])
    alias["reference_id"] = "REF_ALIAS_FAKE_INDEPENDENCE"
    alias["independence_group"] = "IG_FAKE_SECOND_GROUP"
    data["references"].append(alias)
    with pytest.raises(ValueError, match="duplicate persistent_id"):
        mod.validate_graph(data)


def test_duplicate_formula_state_identifier_fails():
    data = graph()
    data["formula_states"].append(copy.deepcopy(formula_state(data, "H01")))
    with pytest.raises(ValueError, match="duplicate formula_id"):
        mod.validate_graph(data)


def test_edge_without_formula_state_fails():
    data = graph()
    data["edges"].append({
        "edge_id": "EDGE-H999-ORPHAN",
        "formula_id": "H999",
        "reference_id": "REF_DESI_DR2_BAO_2503.14738",
        "relation": "CLASS_MATCH",
        "independence_group": "IG_DESI_DR2_BAO",
        "scope": "adversarial orphan edge",
        "provenance": "test_fixture",
        "immutable_event": True,
    })
    with pytest.raises(ValueError, match="has no formula_state"):
        mod.validate_graph(data)


def test_evidence_vector_types_and_counts_are_derived_from_edges():
    data = graph()
    h15 = formula_state(data, "H15")
    h15["evidence_vector"]["math_defined"] = "banana"
    with pytest.raises(ValueError, match="math_defined must be boolean"):
        mod.validate_graph(data)

    data = graph()
    formula_state(data, "H15")["evidence_vector"]["independent_groups"] = 99
    with pytest.raises(ValueError, match="does not match edge-derived groups"):
        mod.validate_graph(data)

    data = graph()
    formula_state(data, "H15")["evidence_vector"]["external_concordance"] = "SUPPORT"
    with pytest.raises(ValueError, match="does not match edge/state-derived CONTRADICT"):
        mod.validate_graph(data)


def test_negative_edge_cannot_disappear_in_next_snapshot():
    old = graph()
    new = copy.deepcopy(old)
    new["edges"] = [e for e in new["edges"] if e["edge_id"] != "EDGE-H15-ACT-LENS"]
    # Keep the successor locally coherent; append-only comparison must still reject deletion.
    h15 = formula_state(new, "H15")
    h15["state"] = "TOKEN_VAZIO_EXACT_TEST"
    h15["evidence_vector"]["contradiction_strength"] = "SINGLE_PATH"
    h15["token_vazio"] = [{
        "id": "TOKEN_VAZIO_TEST",
        "cause": "fixture",
        "evidence_needed": "fixture",
        "falsifier": "fixture",
        "F_next": "fixture",
    }]
    with pytest.raises(ValueError, match="evidence edge removed"):
        mod.assert_non_regression(old, new)


def test_historical_formula_state_cannot_be_rewritten():
    old = graph()
    new = copy.deepcopy(old)
    formula_state(new, "H15")["expression"] = "silently rewritten expression"
    with pytest.raises(ValueError, match="historical formula state mutated"):
        mod.assert_non_regression(old, new)


def test_gap_cannot_disappear_without_receipt():
    old = graph()
    new = copy.deepcopy(old)
    removed = new["open_gaps"].pop()
    assert removed["id"]
    with pytest.raises(ValueError, match="gaps disappeared without structured receipt"):
        mod.assert_non_regression(old, new)


def test_truthy_string_is_not_a_closure_receipt():
    old = graph()
    new = copy.deepcopy(old)
    removed = new["open_gaps"].pop()
    new["gap_closures"] = [{"gap_id": removed["id"], "closure_kind": "EVIDENCE_RECEIPT", "receipt": "x"}]
    with pytest.raises(ValueError, match="structured object"):
        mod.assert_non_regression(old, new)


def test_gap_can_close_only_with_structured_hash_bound_receipt():
    old = graph()
    new = copy.deepcopy(old)
    removed = new["open_gaps"].pop()
    new["gap_closures"] = [closure(removed["id"])]
    mod.assert_non_regression(old, new)


def test_deduplicated_total_can_close_only_with_deterministic_receipt():
    data = graph()
    data["source_inventory"]["deduplicated_total"] = 500
    with pytest.raises(ValueError, match="DETERMINISTIC_DEDUP"):
        mod.validate_graph(data)

    data["gap_closures"] = [closure(2026 if False else "TOKEN_VAZIO_DEDUP_COUNT", kind="DETERMINISTIC_DEDUP", total=500)]
    mod.validate_graph(data)


def test_dedup_receipt_total_must_match_inventory():
    data = graph()
    data["source_inventory"]["deduplicated_total"] = 500
    data["gap_closures"] = [closure("TOKEN_VAZIO_DEDUP_COUNT", kind="DETERMINISTIC_DEDUP", total=499)]
    with pytest.raises(ValueError, match="does not match deterministic dedup receipt"):
        mod.validate_graph(data)
