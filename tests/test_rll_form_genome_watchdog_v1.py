from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT=Path(__file__).resolve().parents[1]
MOD=ROOT/"tools"/"rll_form_genome_watchdog_v1.py"
SPEC=importlib.util.spec_from_file_location("form_genome",MOD)
m=importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name]=m
SPEC.loader.exec_module(m)

SEED={
 "schema":"test",
 "invariants":["TOKEN_VAZIO != 0","SEARCH_SCORE != EVIDENCE != CLAIM"],
 "directions":["N","NE","E","SE","S","SW","W","NW"],
 "antipodal_pairs":[["N","S"],["E","W"],["NE","SW"],["NW","SE"]],
 "center":"O",
 "mandala":{"observed_sectors":8,"key_mapping":"TOKEN_VAZIO_42_KEY_SEMANTICS"},
}


def test_trigram_and_hexagram_counts():
    assert len(m.trigram_states())==8
    assert len(m.hexagram_states())==64
    assert len(m.epistemic_states())==27


def test_complement_preserves_token_vazio():
    assert m.complement_state((0,1,None))==(1,0,None)


def test_d8_orbit_is_bounded_by_16():
    x=tuple(range(8))
    orbit=m.d8_orbit(x)
    assert len(orbit)<=16
    assert len(orbit)>0


def test_form_genome_counts():
    g=m.form_genome(SEED)
    assert g["counts"]["trigrams"]==8
    assert g["counts"]["epistemic_trigrams"]==27
    assert g["counts"]["hexagrams"]==64
    assert g["claim_allowed"] is False


def test_watchdogs_are_independent_ids_and_meta_passes():
    r=m.simulate_watch(SEED)
    assert r["watchdog_A"]["implementation_id"] != r["watchdog_B"]["implementation_id"]
    assert r["meta"]["decision"]=="CONSENSUS_PASS"


def test_meta_detects_silence_fail_closed():
    t=m.Tick(0,"i","s","o",("x",),False)
    a=m.validate_tick("A",t,None,peer_prev=None,meta_prev=None,implementation_id="A")
    meta=m.meta_compare(a,None,0)
    assert meta.decision=="DIVERGENCE_FAIL_CLOSED"


def test_same_implementation_marks_common_mode_gap():
    t=m.Tick(0,"i","s","o",("x",),False)
    a=m.validate_tick("A",t,None,peer_prev=None,meta_prev=None,implementation_id="same")
    b=m.validate_tick("B",t,None,peer_prev=None,meta_prev=None,implementation_id="same")
    meta=m.meta_compare(a,b,0)
    assert meta.decision=="CONSENSUS_PASS_WITH_COMMON_MODE_GAP"
    assert "COMMON_MODE_UNRESOLVED" in meta.reasons


def test_bounded_select_is_deterministic():
    items=list(range(20))
    a=m.bounded_select(items,4,ordered=True,exhaustive_cap=100,sample_budget=25,seed=42)
    b=m.bounded_select(items,4,ordered=True,exhaustive_cap=100,sample_budget=25,seed=42)
    assert a==b
    assert a["mode"]=="BOUNDED_RANDOM_SAMPLE"
    assert a["returned"]==25


def test_small_space_is_exhaustive():
    r=m.bounded_select(list(range(4)),2,ordered=False,exhaustive_cap=100,sample_budget=2,seed=1)
    assert r["mode"]=="EXHAUSTIVE"
    assert r["total_space"]==6
    assert r["returned"]==6


def test_delayed_reciprocal_watchdog_of_watchdog():
    r=m.simulate_two_ticks(SEED)
    assert all(r["cross_check"].values())
    assert r["M"][0]["decision"]=="CONSENSUS_PASS"
    assert r["M"][1]["decision"]=="CONSENSUS_PASS"


def test_mandala_sample_d8_dedup_and_bounded():
    seed={**SEED,"search":{"sample_budget":64,"random_seed":42}}
    a=m.sample_mandala_assignments(seed)
    b=m.sample_mandala_assignments(seed)
    assert a==b
    assert a["raw_total_space"]==40320
    assert a["d8_equivalence_classes_exact"]==2520
    assert a["returned"]==64
    canons=[tuple(x["canonical_d8"]) for x in a["candidates"]]
    assert len(canons)==len(set(canons))
    assert all(x["semantic_state"]=="TOKEN_VAZIO_HISTORICAL_ORDER" for x in a["candidates"])
