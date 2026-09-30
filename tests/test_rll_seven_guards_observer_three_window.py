import json
from pathlib import Path

from tools.validate_rll_seven_guards_observer_three_window import validate_contract


CONTRACT = Path("data/contracts/rll_seven_guards_observer_three_window.v1.json")


def load_contract():
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def test_contract_is_structurally_valid_and_claim_blocked():
    result = validate_contract(load_contract())
    assert result["valid"] is True, result["errors"]
    assert result["claim_allowed"] is False
    assert result["scientific_confirmation"] is False
    assert result["boundary"] == "STRUCTURAL_PASS != SCIENTIFIC_CONFIRMATION"


def test_exact_seven_guards_are_present():
    data = load_contract()
    assert set(data["guards"]) == {
        "provenance",
        "context",
        "evidence",
        "contradiction",
        "uncertainty",
        "reproduction",
        "rollback",
    }


def test_three_windows_are_predeclared_and_located():
    data = load_contract()
    assert [window["id"] for window in data["windows"]] == ["W0", "W1", "W2"]
    assert all(window["predeclared"] for window in data["windows"])
    assert all(window["required_locator"] for window in data["windows"])


def test_post_hoc_best_of_three_is_blocked():
    data = load_contract()
    assert data["selection_policy"]["best_of_three_post_hoc_allowed"] is False
    assert data["selection_policy"]["predeclared_selection_rule_required"] is True


def test_unresolved_author_phrases_remain_token_vazio():
    data = load_contract()
    tokens = set(data["unresolved_author_tokens"])
    assert "TOKEN_VAZIO_TWINS_ON_DAGGER" in tokens
    assert "TOKEN_VAZIO_4_OF_5_IN_THREE" in tokens


def test_quantum_boundary_blocks_consciousness_and_classical_orbit_overclaim():
    data = load_contract()
    observer = data["observer_model"]
    blockers = set(data["claim_blockers"])
    assert observer["consciousness_required_for_physical_claim"] is False
    assert "CLASSICAL_TRAJECTORY_ASSUMED_FOR_QUANTUM_OBSERVABLE" in blockers
    assert "METAPHOR_PROMOTED_TO_PHYSICAL_MECHANISM" in blockers


def test_rollback_requires_history_preservation():
    data = load_contract()
    assert "history_preserved" in data["guards"]["rollback"]["minimum"]
    assert "ROLLBACK_PRESERVES_CONTRADICTORY_EVIDENCE" in data["invariants"]
