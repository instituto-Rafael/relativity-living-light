import json
from pathlib import Path

import pytest

from tools.rll_token_vazio_reconcile import (
    evaluate_rule,
    load_json,
    reconcile,
    validate_input,
    validate_rules,
)


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data/governance/RLL_GAP_CLOSURE_INPUT_20260807_V1.json"
RULES = ROOT / "data/governance/RLL_TOKEN_VAZIO_CLOSURE_RULES_20260807_V1.json"


def test_current_reconciliation_closes_only_evidence_backed_uncertainty():
    receipt = reconcile(ROOT, load_json(INPUT), load_json(RULES), "2026-08-07T22:36:00Z")

    assert receipt["claim_allowed"] is False
    assert receipt["publication_ready"] is False
    assert receipt["summary"]["input_tokens"] == 18
    assert receipt["summary"]["terminal_resolved"] == 2
    assert receipt["summary"]["reduced_generic"] == 1
    assert receipt["summary"]["open"] == 15

    assert "TOKEN_VAZIO_MODERN_SN_FULL_LIKELIHOOD" in receipt["reduced_tokens"]
    assert "TOKEN_VAZIO_MODERN_SN_FULL_LIKELIHOOD" not in receipt["canonical_open_tokens"]

    assert "TOKEN_VAZIO_RLL_SN_ONLY_PARAMETER_IDENTIFIABILITY" in receipt["terminal_tokens"]
    assert "TOKEN_VAZIO_RLL_SN_ONLY_PARAMETER_IDENTIFIABILITY" not in receipt["canonical_open_tokens"]

    assert "TOKEN_VAZIO_EXPLICIT_REPOSITORY_LICENSE_NOT_FOUND" in receipt["terminal_tokens"]
    assert "TOKEN_VAZIO_EXPLICIT_REPOSITORY_LICENSE_NOT_FOUND" not in receipt["canonical_open_tokens"]

    assert "TOKEN_VAZIO_SN_COMMON_NUISANCE_ABLATION" in receipt["canonical_open_tokens"]
    assert "TOKEN_VAZIO_CPL_DOVEKIE_WA_BOUNDARY_SENSITIVITY" in receipt["canonical_open_tokens"]
    assert "TOKEN_VAZIO_REAL_BAYES_INFERENCE" in receipt["open_by_priority"]["P0"]

    assert not any(r["state"] == "OPEN_EVIDENCE_MISSING" for r in receipt["results"])


def test_terminal_rule_without_evidence_contract_is_rejected():
    rules = {
        "schema": "rll.token_vazio_closure_rules.v1",
        "claim_allowed": False,
        "rules": [
            {
                "token": "TOKEN_VAZIO_X",
                "priority": "P0",
                "target_state": "RESOLVED",
                "classification": "BAD"
            }
        ]
    }
    with pytest.raises(ValueError, match="requires evidence_path"):
        validate_rules(rules)


def test_missing_evidence_downgrades_resolution_to_open(tmp_path):
    item = {"token": "TOKEN_VAZIO_X", "priority": "P0", "domain": "test"}
    rule = {
        "token": "TOKEN_VAZIO_X",
        "priority": "P0",
        "target_state": "RESOLVED_NEGATIVE",
        "classification": "TEST",
        "evidence_path": "missing.json",
        "assertions": [{"path": "state", "op": "eq", "value": "VERIFIED"}],
        "resolved_fact": "negative fact",
        "successors": []
    }
    result = evaluate_rule(tmp_path, item, rule)
    assert result["state"] == "OPEN_EVIDENCE_MISSING"
    assert result["evidence_verified"] is False
    assert result["resolved_fact"] is None


def test_failed_assertion_cannot_close_token(tmp_path):
    evidence = tmp_path / "evidence.json"
    evidence.write_text(json.dumps({"state": "NOT_VERIFIED"}), encoding="utf-8")
    item = {"token": "TOKEN_VAZIO_X", "priority": "P0", "domain": "test"}
    rule = {
        "token": "TOKEN_VAZIO_X",
        "priority": "P0",
        "target_state": "RESOLVED",
        "classification": "TEST",
        "evidence_path": "evidence.json",
        "assertions": [{"path": "state", "op": "eq", "value": "VERIFIED"}],
        "resolved_fact": "should not close",
        "successors": []
    }
    result = evaluate_rule(tmp_path, item, rule)
    assert result["state"] == "OPEN_EVIDENCE_MISSING"
    assert result["evidence_verified"] is False
    assert result["assertions"][0]["ok"] is False


def test_duplicate_input_token_is_rejected():
    payload = {
        "schema": "rll.gap_closure_input.v1",
        "claim_allowed": False,
        "tokens": [
            {"token": "TOKEN_VAZIO_X", "priority": "P0"},
            {"token": "TOKEN_VAZIO_X", "priority": "P1"}
        ]
    }
    with pytest.raises(ValueError, match="duplicate input token"):
        validate_input(payload)


def test_negative_resolution_is_not_positive_claim():
    receipt = reconcile(ROOT, load_json(INPUT), load_json(RULES), "2026-08-07T22:36:00Z")
    rows = {row["token"]: row for row in receipt["results"]}
    ident = rows["TOKEN_VAZIO_RLL_SN_ONLY_PARAMETER_IDENTIFIABILITY"]
    license_row = rows["TOKEN_VAZIO_EXPLICIT_REPOSITORY_LICENSE_NOT_FOUND"]

    assert ident["state"] == "RESOLVED_NEGATIVE"
    assert "not identifiable" in ident["resolved_fact"]
    assert license_row["state"] == "RESOLVED_NEGATIVE"
    assert "redistribution is blocked" in license_row["resolved_fact"]
    assert receipt["claim_allowed"] is False
