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
    with pytest.raises(ValueError, match="CONTRADICTED_EXTERNAL_2PLUS requires"):
        mod.validate_graph(data)


def test_negative_edge_cannot_disappear_in_next_snapshot():
    old = graph()
    new = copy.deepcopy(old)
    new["edges"] = [e for e in new["edges"] if e["edge_id"] != "EDGE-H15-ACT-LENS"]
    # New snapshot is locally coherent only after downgrading H15; append-only check must still reject deletion.
    formula_state(new, "H15")["state"] = "TOKEN_VAZIO_EXACT_TEST"
    formula_state(new, "H15")["evidence_vector"]["contradiction_strength"] = "SINGLE_PATH"
    formula_state(new, "H15")["token_vazio"] = [{
        "id": "TOKEN_VAZIO_TEST",
        "cause": "fixture",
        "evidence_needed": "fixture",
        "falsifier": "fixture",
        "F_next": "fixture",
    }]
    with pytest.raises(ValueError, match="evidence edge removed"):
        mod.assert_non_regression(old, new)


def test_gap_cannot_disappear_without_receipt():
    old = graph()
    new = copy.deepcopy(old)
    removed = new["open_gaps"].pop()
    assert removed["id"]
    with pytest.raises(ValueError, match="gaps disappeared without receipt"):
        mod.assert_non_regression(old, new)


def test_gap_can_close_only_with_explicit_receipt():
    old = graph()
    new = copy.deepcopy(old)
    removed = new["open_gaps"].pop()
    new["gap_closures"] = [{"gap_id": removed["id"], "receipt": "RUN-or-immutable-artifact-required"}]
    mod.assert_non_regression(old, new)
