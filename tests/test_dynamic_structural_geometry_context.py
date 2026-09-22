import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "data/governance/RLL_DYNAMIC_STRUCTURAL_GEOMETRY_CONTEXT_V1.json"


def load():
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def test_dynamic_geometry_contract_is_fail_closed():
    c = load()
    assert c["claim_allowed"] is False
    assert c["source_bridge"]["delta_p_state"] == "STABILITY_CANDIDATE"
    assert c["source_bridge"]["unresolved_index_around_70"] == "TOKEN_VAZIO_INDEX_AROUND_70"


def test_delta_p_is_not_promoted_to_physics():
    c = load()
    forbidden = set(c["rmrcti_adapter"]["forbidden_use"])
    assert "cosmological_parameter" in forbidden
    assert "physical_pressure" in forbidden
    assert "universal_constant" in forbidden


def test_router_contains_local_relativistic_cosmological_and_observation_regimes():
    c = load()
    ids = {row["id"] for row in c["regime_router"]}
    assert {"G0", "G1", "G2", "G3", "G4", "G5", "G6"} <= ids


def test_hidden_truth_experiment_is_required_before_promotion():
    c = load()
    assert c["required_experiment"]["type"] == "SYNTHETIC_HIDDEN_TRUTH_EVENT_CHAIN"
    assert "held_out_truth" in c["controls"]
    assert "wrong_geometry" in c["controls"]
    assert "wrong_event_order" in c["controls"]
