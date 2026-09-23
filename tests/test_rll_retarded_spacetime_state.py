from pathlib import Path

import yaml

from tools.validate_rll_retarded_spacetime_state import validate_contract

CONTRACT = Path("data/contracts/rll_retarded_spacetime_state.v1.yml")


def test_retarded_spacetime_contract_is_structurally_valid():
    data = yaml.safe_load(CONTRACT.read_text(encoding="utf-8"))
    result = validate_contract(data)
    assert result["valid"], result["errors"]
    assert result["claim_allowed"] is False


def test_observation_and_present_state_remain_distinct():
    data = yaml.safe_load(CONTRACT.read_text(encoding="utf-8"))
    assert "OBSERVATION_EVENT != PRESENT_SOURCE_STATE" in data["invariants"]
    assert "NULL_SIGNAL_PATH != TIMELIKE_MATTER_WORLDLINE" in data["invariants"]


def test_plasma_gravity_and_geometry_boundaries_fail_closed():
    data = yaml.safe_load(CONTRACT.read_text(encoding="utf-8"))
    assert data["plasma_and_gravity"]["no_new_force_claim"] is True
    assert data["geometry_relational_layer"]["physical_metric_claim"] is False
    assert data["semantic_boundaries"]["syntropy"].startswith("TOKEN_VAZIO")
