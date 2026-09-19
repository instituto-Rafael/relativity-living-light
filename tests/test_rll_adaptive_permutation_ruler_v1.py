from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MOD_PATH = ROOT / "tools" / "rll_adaptive_permutation_ruler_v1.py"
SPEC = importlib.util.spec_from_file_location("ruler", MOD_PATH)
ruler = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(ruler)


def sample_fragments():
    rows = [
        {"id":"A","name":"a","layer":"x","impact":8,"uncertainty_reduction":8,"effort":2,"undercoverage":1,"recurrence":1,"testability":1,"novelty":0.5,"provenance":1,"claim_gate":"SUPPORTED"},
        {"id":"B","name":"b","layer":"y","impact":4,"uncertainty_reduction":8,"effort":2,"undercoverage":0.8,"recurrence":0.8,"testability":1,"novelty":0.6,"provenance":0.9,"claim_gate":"TOKEN_VAZIO"},
        {"id":"C","name":"c","layer":"z","impact":2,"uncertainty_reduction":4,"effort":4,"undercoverage":0.5,"recurrence":0.6,"testability":0.7,"novelty":0.7,"provenance":0.8,"claim_gate":"METHOD"},
        {"id":"D","name":"d","layer":"x","impact":1,"uncertainty_reduction":2,"effort":8,"undercoverage":0.3,"recurrence":0.3,"testability":0.5,"novelty":0.2,"provenance":0.7,"claim_gate":"SUPPORTED"},
    ]
    return [ruler.Fragment.from_dict(x) for x in rows]


def test_deterministic_same_seed():
    fs = sample_fragments()
    weights = {"undercoverage":1,"recurrence":1,"testability":1,"cross_layer":1,"novelty":0.75,"provenance":1.25,"redundancy_penalty":1}
    a = ruler.search(fs, weights, seed=42, sample_budget=50, max_size=3, beam_width=10, epsilon=0.0, patience=50, require_cross_layer=True)
    b = ruler.search(fs, weights, seed=42, sample_budget=50, max_size=3, beam_width=10, epsilon=0.0, patience=50, require_cross_layer=True)
    assert a["candidates"] == b["candidates"]


def test_bounded_not_cartesian_execution():
    fs = sample_fragments()
    result = ruler.search(fs, {}, seed=1, sample_budget=7, max_size=3, beam_width=5, epsilon=0.0, patience=20, require_cross_layer=True)
    assert result["samples_attempted"] <= 7
    assert result["policy"]["blind_cartesian_product"] == "FORBIDDEN"


def test_no_duplicate_fragment_ids_inside_candidate():
    fs = sample_fragments()
    result = ruler.search(fs, {}, seed=2, sample_budget=30, max_size=4, beam_width=10, epsilon=0.0, patience=30, require_cross_layer=False)
    for c in result["candidates"]:
        assert len(c["ids"]) == len(set(c["ids"]))


def test_token_vazio_blocks_promotion_not_exploration():
    fs = sample_fragments()
    b = next(x for x in fs if x.id == "B")
    a = next(x for x in fs if x.id == "A")
    assert ruler.promotion_allowed((a,b)) is False


def test_weight_update_positive_and_normalized():
    w = {"undercoverage":1,"recurrence":1,"testability":1,"cross_layer":1,"novelty":1,"provenance":1}
    f = {"undercoverage":1,"recurrence":0.5,"testability":1,"cross_layer":1,"novelty":0.2,"provenance":1}
    out = ruler.update_weights(w, f, reward=1.0, eta=0.1)
    vals = [out[k] for k in w]
    assert all(v > 0 for v in vals)
    assert abs(sum(vals) - len(vals)) < 1e-9
