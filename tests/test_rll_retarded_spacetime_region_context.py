import yaml
from pathlib import Path

from tools.validate_rll_retarded_spacetime_region_context import validate_contract

CONTRACT = Path("data/contracts/rll_retarded_spacetime_region_context.v1.yaml")


def load():
    return yaml.safe_load(CONTRACT.read_text(encoding="utf-8"))


def test_contract_valid_and_claim_blocked():
    result = validate_contract(load())
    assert result["valid"], result["errors"]
    assert result["claim_allowed"] is False
    assert result["scientific_confirmation"] is False


def test_light_and_matter_paths_are_separate():
    data = load()
    invariants = set(data["core_invariants"])
    assert "SIGNAL_NULL_PATH != MATTER_TIMELIKE_PATH" in invariants
    assert "OBSERVED_EMISSION_STATE != CURRENT_MATTER_STATE_INFERENCE" in invariants


def test_region_state_is_evaluated_at_crossing_event():
    data = load()
    logic = data["crossing_logic"]
    assert "photon-crossing event" in logic["moving_region_rule"]
    assert "after the photon left" in logic["before_after_rule"]


def test_plasma_is_not_promoted_to_new_gravity_force():
    data = load()
    blocked = set(data["physics_boundary"]["plasma_components"]["blocked_claims"])
    assert "plasma_gravity_as_new_fundamental_force" in blocked


def test_global_parameters_cannot_be_selected_post_hoc_per_datum():
    data = load()
    assert data["parameter_model"]["global_theta"]["post_hoc_per_datum_adaptation_allowed"] is False


def test_seven_statistics_are_orthogonal_to_seven_guards():
    data = load()
    assert data["statistics"]["seven_guards_are_separate"] is True
    assert len(data["statistics"]["S7_observation"]) == 7
    assert len(data["statistics"]["S7_model"]) == 7


def test_scientific_gate_remains_blocked():
    data = load()
    assert data["gates"]["scientific_claim"] == "BLOCKED"
