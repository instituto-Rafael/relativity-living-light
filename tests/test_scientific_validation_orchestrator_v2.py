from __future__ import annotations

import csv
import json
from copy import deepcopy
from pathlib import Path

from tools.validate_scientific_validation_orchestrator_v2 import (
    READY_G2,
    ROOT,
    build_readiness,
    load_json,
    validate_contract_data,
    validate_desi_covariance,
    validate_urgency_data,
)


def test_contract_is_fail_closed_and_acyclic() -> None:
    contract = load_json(ROOT / "data/contracts/rll_scientific_validation_orchestrator.v1.json")
    assert contract["claim_allowed"] is False
    assert contract["publication_effect"] == "NONE"
    assert contract["execution_effect"] == "NONE_UNTIL_EXPLICITLY_WIRED"
    assert validate_contract_data(contract) == []


def test_contract_rejects_unknown_dependency_and_claim_promotion() -> None:
    contract = load_json(ROOT / "data/contracts/rll_scientific_validation_orchestrator.v1.json")
    bad = deepcopy(contract)
    bad["claim_allowed"] = True
    bad["gates"][1]["requires"] = ["G_DOES_NOT_EXIST"]
    errors = validate_contract_data(bad)
    assert any("claim_allowed" in error for error in errors)
    assert any("unknown dependencies" in error for error in errors)


def test_urgency_ledger_scores_and_receipt_fields_are_self_consistent() -> None:
    ledger = load_json(ROOT / "data/governance/RLL_SCIENTIFIC_VALIDATION_URGENCY_20260819_V1.json")
    assert ledger["claim_allowed"] is False
    assert validate_urgency_data(ledger) == []
    ids = {entry["id"] for entry in ledger["entries"]}
    assert "RLL-SV-P0-001" in ids
    assert "RLL-SV-P0-002" in ids


def test_current_desi_covariance_is_structurally_13x13() -> None:
    report = validate_desi_covariance(ROOT / "data/real/desi_dr2_bao_covariance.csv")
    assert report["status"] == "READY_DESI_13X13_MATRIX"
    assert report["rows"] == 13
    assert report["columns"] == 13
    assert report["symmetric"] is True
    assert report["positive_diagonal"] is True
    assert report["claim_allowed"] is False


def test_desi_covariance_rejects_asymmetry(tmp_path: Path) -> None:
    path = tmp_path / "desi.csv"
    matrix = [[0.0 for _ in range(13)] for _ in range(13)]
    for i in range(13):
        matrix[i][i] = 1.0
    matrix[0][1] = 0.25
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow([""] + [str(i) for i in range(13)])
        for i, row in enumerate(matrix):
            writer.writerow([str(i)] + row)
    report = validate_desi_covariance(path)
    assert report["status"] == "BLOCKED_DESI_COVARIANCE_ASYMMETRY"
    assert report["claim_allowed"] is False


def test_dependency_closure_never_bypasses_g2() -> None:
    report = build_readiness(ROOT)
    assert report["claim_allowed"] is False
    assert report["scientific_confirmation"] is False
    assert report["contract"]["valid"] is True
    assert report["urgency_ledger"]["valid"] is True
    g2 = report["gate_states"]["G2"]
    if g2 != READY_G2:
        assert report["gate_states"]["G3"] == "BLOCKED_BY_G2"
        assert report["gate_states"]["G5"] == "BLOCKED_BY_G2"
        assert report["gate_states"]["G6"] == "BLOCKED_BY_G5"
        assert "RLL-SV-P0-001" in report["current_frontier"]
    else:
        assert report["gate_states"]["G3"] == "READY_TO_EXECUTE_COMPATIBILITY_NOT_PASSED"
        assert report["gate_states"]["G5"] == "READY_TO_BUILD_AFTER_G3_G4"


def test_readiness_receipt_keeps_scientific_boundaries_explicit() -> None:
    report = build_readiness(ROOT)
    boundaries = report["boundaries"]
    assert boundaries["readiness_is_scientific_pass"] is False
    assert boundaries["desi_matrix_presence_proves_point_order"] is False
    assert boundaries["pantheon_diagonal_diagnostic_is_full_likelihood"] is False
    assert boundaries["downstream_gate_can_bypass_failed_prerequisite"] is False
    assert boundaries["negative_result_can_be_discarded"] is False


def test_report_is_json_serializable() -> None:
    report = build_readiness(ROOT)
    payload = json.dumps(report, sort_keys=True)
    assert "rll.scientific_validation_readiness.v2" in payload
