from __future__ import annotations

import copy

import pytest

from tools import validate_session_reality_science_claims as validator


def test_session_reality_science_ledger_is_valid() -> None:
    data = validator.load_ledger()
    report = validator.validate_ledger(data)
    assert report["valid"] is True
    assert report["claim_allowed"] is False
    assert report["claim_count"] >= 17
    assert report["contradiction_count"] >= 4
    assert report["analogy_count"] >= 2


def test_autonomous_background_claim_cannot_be_promoted() -> None:
    data = copy.deepcopy(validator.load_ledger())
    claim = next(item for item in data["claims"] if item["id"] == "AI-BACKGROUND-001")
    claim["state"] = "VERIFIED_STANDARD"
    with pytest.raises(ValueError, match="state promotion blocked"):
        validator.validate_ledger(data)


def test_water_memory_claim_remains_analogy_only() -> None:
    data = copy.deepcopy(validator.load_ledger())
    claim = next(item for item in data["claims"] if item["id"] == "WATER-MEMORY-011")
    claim["state"] = "HYPOTHESIS"
    with pytest.raises(ValueError, match="state promotion blocked"):
        validator.validate_ledger(data)


def test_hypercube_does_not_become_physical_claim() -> None:
    data = copy.deepcopy(validator.load_ledger())
    claim = next(item for item in data["claims"] if item["id"] == "HYPERCUBE-013")
    claim["state"] = "VERIFIED_STANDARD"
    with pytest.raises(ValueError, match="state promotion blocked"):
        validator.validate_ledger(data)


def test_complete_2026_session_cannot_be_claimed_from_historical_export() -> None:
    data = copy.deepcopy(validator.load_ledger())
    data["source_scope"]["historical_export"]["current_2026_session_complete_in_export"] = True
    with pytest.raises(ValueError, match="complete 2026 session"):
        validator.validate_ledger(data)


def test_negative_results_invariant_is_mandatory() -> None:
    data = copy.deepcopy(validator.load_ledger())
    data["mandatory_invariants"]["negative_results_preserved"] = False
    with pytest.raises(ValueError, match="mandatory invariants changed"):
        validator.validate_ledger(data)
