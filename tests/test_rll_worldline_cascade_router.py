from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "data/governance/RLL_WORLDLINE_CASCADE_FORMULA_ROUTER_V1.json"
INDEX = ROOT / "data/formulas/FORMULA_INDEX_CONTRACT.json"
DOC = ROOT / "docs/canonicos/34_RMRCTI_OMEGA_WORLDLINE_CASCADE_ROUTER.md"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_router_is_fail_closed() -> None:
    d = load(CONTRACT)
    assert d["claim_allowed"] is False
    assert d["status"] == "CONTRACT_CANDIDATE"
    assert "TOKEN_VAZIO != ZERO" in d["invariants"]


def test_rmrcti_semantics_do_not_collapse() -> None:
    d = load(CONTRACT)
    s = d["source_bridge"]
    assert s["delta_p_state"] == "STABILITY_CANDIDATE"
    assert s["delta_p_value_target"] == 0.18
    assert s["R"] == 2.0
    assert s["r"] == 0.7
    assert s["unresolved_index_around_70"] == "SUPERSEDED_BY_SOURCE_OBSERVED_CV_MEAN_0_700000"
    history = s["reconciliation_history"]
    assert history[-1]["previous"] == "TOKEN_VAZIO_INDEX_AROUND_70"
    assert history[-1]["corrected_to"] == "SOURCE_OBSERVED_CV_MEAN_0_700000"
    assert s["stability_related_CV_mean_0_70"]["value"] == 0.7
    assert s["stability_related_CV_mean_0_70"]["boundary"] == "not stable_any rate; not DeltaP; not a physical constant"


def test_permutation_is_bounded_and_reproducible() -> None:
    d = load(CONTRACT)
    p = d["multilevel_permutation"]
    assert p["mode"] == "SEEDED_STOCHASTIC_PRUNED"
    assert p["exhaustive_cartesian"] is False
    assert len(p["stop_rule"]) >= 4


def test_formula_index_points_to_router() -> None:
    d = load(INDEX)
    ext = d["routing_extensions"]
    assert ext["worldline_cascade_router"] == "data/governance/RLL_WORLDLINE_CASCADE_FORMULA_ROUTER_V1.json"
    assert "DeltaP remains an operational stability/routing metric" in ext["boundary"]


def test_document_preserves_core_boundaries() -> None:
    text = DOC.read_text(encoding="utf-8")
    assert "DISTANT_COORDINATE_SLOWING != PROPER_TIME_STOPS" in text
    assert "MAGNETIC_DYNAMICS != MODIFIED_G" in text
    assert "DeltaP ~= 0.18" in text
    assert "STABILITY_CANDIDATE" in text
