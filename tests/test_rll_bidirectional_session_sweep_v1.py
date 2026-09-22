from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MOD_PATH = ROOT / "tools" / "rll_bidirectional_session_sweep_v1.py"
SPEC = importlib.util.spec_from_file_location("rll_bidir", MOD_PATH)
mod = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = mod
SPEC.loader.exec_module(mod)


def ledger():
    return {
        "schema":"test.ledger.v1",
        "fragments":[
            {"id":"F0","name":"a","layer":"nutrition_causal_design","impact":8,"uncertainty_reduction":8,"effort":2,"undercoverage":1,"recurrence":1,"testability":1,"novelty":0.5,"provenance":1,"claim_gate":"METHOD_RULE"},
            {"id":"F1","name":"b","layer":"physical_chemistry","impact":8,"uncertainty_reduction":8,"effort":2,"undercoverage":1,"recurrence":1,"testability":1,"novelty":0.5,"provenance":1,"claim_gate":"SUPPORTED"},
            {"id":"F2","name":"c","layer":"bioenergetics","impact":4,"uncertainty_reduction":8,"effort":2,"undercoverage":0.8,"recurrence":0.8,"testability":1,"novelty":0.6,"provenance":0.9,"claim_gate":"SUPPORTED"},
            {"id":"F3","name":"d","layer":"replication","impact":4,"uncertainty_reduction":4,"effort":4,"undercoverage":0.7,"recurrence":0.7,"testability":0.8,"novelty":0.7,"provenance":0.8,"claim_gate":"SUPPORTED"},
        ],
        "candidate_crosslinks":[
            {"id":"X","fragments":["F0","F1"],"state":"HYPOTHESIS"}
        ]
    }


def test_deterministic_replay():
    a=mod.run(ledger(),seed=42,max_cycles=4,fanout=3,second_order_budget=8)
    b=mod.run(ledger(),seed=42,max_cycles=4,fanout=3,second_order_budget=8)
    assert a==b


def test_forward_and_reverse_present():
    r=mod.run(ledger(),seed=1,max_cycles=1,fanout=2,second_order_budget=4)
    c=r["cycles"][0]
    assert c["direction_counts"]["FORWARD"] > 0
    assert c["direction_counts"]["REVERSE"] > 0


def test_never_claims_complete():
    r=mod.run(ledger(),seed=2,max_cycles=2,fanout=2,second_order_budget=4)
    assert r["complete"] is False
    assert r["claim_allowed"] is False
    assert r["rule"] == "SATURATED_UNDER_CURRENT_RULER != COMPLETE"


def test_structural_gaps_are_explicit():
    r=mod.run(ledger(),seed=3,max_cycles=1,fanout=2,second_order_budget=4)
    kinds={x["kind"] for x in r["structural_metadata_gaps"]}
    assert "TOKEN_VAZIO_UNITS" in kinds
    assert "TOKEN_VAZIO_TIME_AXIS" in kinds
    assert "TOKEN_VAZIO_COMPARTMENT" in kinds


def test_second_order_bounded():
    r=mod.run(ledger(),seed=4,max_cycles=1,fanout=3,second_order_budget=2)
    assert r["cycles"][0]["second_order_probes"] <= 2


def test_representation_changes_after_cycle():
    r=mod.run(ledger(),seed=5,max_cycles=1,fanout=3,second_order_budget=4)
    c=r["cycles"][0]
    assert c["representation_in"] != c["representation_out"]
