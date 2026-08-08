import json
from pathlib import Path

import pytest

from tools.rll_token_vazio_reconcile import (
    apply_rule_overrides,
    evaluate_rule,
    load_json,
    reconcile,
    validate_input,
    validate_rules,
)


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data/governance/RLL_GAP_CLOSURE_INPUT_20260807_V1.json"
RULES = ROOT / "data/governance/RLL_TOKEN_VAZIO_CLOSURE_RULES_20260807_V1.json"
OVERRIDES = ROOT / "data/governance/RLL_TOKEN_VAZIO_CLOSURE_OVERRIDES_20260807_V1.json"


def effective_rules():
    return apply_rule_overrides(load_json(RULES), load_json(OVERRIDES))


def current_receipt():
    return reconcile(ROOT, load_json(INPUT), effective_rules(), "2026-08-08T00:15:00Z")


def test_current_reconciliation_closes_only_evidence_backed_uncertainty():
    receipt = current_receipt()

    assert receipt["claim_allowed"] is False
    assert receipt["publication_ready"] is False
    assert receipt["summary"]["input_tokens"] == 30
    assert receipt["summary"]["terminal_resolved"] == 8
    assert receipt["summary"]["reduced_generic"] == 7
    assert receipt["summary"]["open"] == 15

    for token in (
        "TOKEN_VAZIO_MODERN_SN_FULL_LIKELIHOOD",
        "TOKEN_VAZIO_REAL_BAYES_INFERENCE",
        "TOKEN_VAZIO_DESI_DR2_OFFICIAL_REPRODUCTION",
        "TOKEN_VAZIO_ACT_DR6_LIKELIHOOD",
        "TOKEN_VAZIO_CLASS_CAMB_PERTURBATION_BENCHMARK",
        "TOKEN_VAZIO_MODERN_H0_FORMAL_LIKELIHOOD",
        "TOKEN_VAZIO_H0_RD_ABLATION_EXECUTION_PROVENANCE",
    ):
        assert token in receipt["reduced_tokens"]
        assert token not in receipt["canonical_open_tokens"]

    for token in (
        "TOKEN_VAZIO_RLL_SN_ONLY_PARAMETER_IDENTIFIABILITY",
        "TOKEN_VAZIO_EXPLICIT_REPOSITORY_LICENSE_NOT_FOUND",
        "TOKEN_VAZIO_SN_COMMON_NUISANCE_ABLATION",
        "TOKEN_VAZIO_CPL_DOVEKIE_WA_BOUNDARY_SENSITIVITY",
        "TOKEN_VAZIO_CPL_DOVEKIE_WA_LOWER_PROFILE_CLOSURE",
        "TOKEN_VAZIO_REAL_BAYES_MODERN_3MODEL_PRIOR_LOCK",
        "TOKEN_VAZIO_H0_RD_OPTIMIZATION_CONVERGENCE",
        "TOKEN_VAZIO_PENDING_RELEASE_REFRESH",
    ):
        assert token in receipt["terminal_tokens"]
        assert token not in receipt["canonical_open_tokens"]

    for token in (
        "TOKEN_VAZIO_REAL_BAYES_JOINT_MULTI_PROBE",
        "TOKEN_VAZIO_INDEPENDENT_REPLICATION",
        "TOKEN_VAZIO_DESI_DR2_OFFICIAL_JOINT_CROSSBLOCK_REPRODUCTION",
        "TOKEN_VAZIO_PHYSICAL_EXECUTION",
    ):
        assert token in receipt["open_by_priority"]["P0"]

    for token in (
        "TOKEN_VAZIO_ACT_DR6_CMBONLY_MATERIALIZATION_REPRODUCTION",
        "TOKEN_VAZIO_DES_Y6_3X2PT_LIKELIHOOD",
        "TOKEN_VAZIO_LCDM_CPL_CLASS_CAMB_BASELINE_CROSSCHECK",
        "TOKEN_VAZIO_RLL_PERTURBATION_CLOSURE_RELATIONS",
        "TOKEN_VAZIO_RLL_CLASS_CAMB_IMPLEMENTATION",
        "TOKEN_VAZIO_H0_PRIOR_PRIMARY_SOURCE_PROVENANCE",
        "TOKEN_VAZIO_H0_RD_FULL_BOLTZMANN_REPRODUCTION",
        "TOKEN_VAZIO_EXTERNAL_SETTINGS",
    ):
        assert token in receipt["open_by_priority"]["P1"]

    for token in (
        "TOKEN_VAZIO_NOT_YET_CLASSIFIED_ALL_582_REFS",
        "TOKEN_VAZIO_UTM185_TERMUX_EXECUTION",
        "TOKEN_VAZIO_UTM185_REAL_MODEL_TRAINING",
    ):
        assert token in receipt["open_by_priority"]["P2"]

    assert not any(r["state"] == "OPEN_EVIDENCE_MISSING" for r in receipt["results"])


def test_terminal_rule_without_evidence_contract_is_rejected():
    rules = {
        "schema": "rll.token_vazio_closure_rules.v1",
        "claim_allowed": False,
        "rules": [{"token": "TOKEN_VAZIO_X", "priority": "P0", "target_state": "RESOLVED", "classification": "BAD"}],
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
        "successors": [],
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
        "successors": [],
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
            {"token": "TOKEN_VAZIO_X", "priority": "P1"},
        ],
    }
    with pytest.raises(ValueError, match="duplicate input token"):
        validate_input(payload)


def test_duplicate_override_token_is_rejected():
    base = {"schema": "rll.token_vazio_closure_rules.v1", "claim_allowed": False, "rules": []}
    override = {
        "schema": "rll.token_vazio_closure_overrides.v1",
        "claim_allowed": False,
        "overrides": [
            {"token": "TOKEN_VAZIO_X", "priority": "P0", "target_state": "OPEN_INTERNAL"},
            {"token": "TOKEN_VAZIO_X", "priority": "P0", "target_state": "OPEN_INTERNAL"},
        ],
    }
    with pytest.raises(ValueError, match="duplicate override token"):
        apply_rule_overrides(base, override)


def test_negative_resolution_is_not_positive_claim():
    receipt = current_receipt()
    rows = {row["token"]: row for row in receipt["results"]}
    ident = rows["TOKEN_VAZIO_RLL_SN_ONLY_PARAMETER_IDENTIFIABILITY"]
    boundary = rows["TOKEN_VAZIO_CPL_DOVEKIE_WA_BOUNDARY_SENSITIVITY"]
    license_row = rows["TOKEN_VAZIO_EXPLICIT_REPOSITORY_LICENSE_NOT_FOUND"]

    assert ident["state"] == "RESOLVED_NEGATIVE"
    assert "not identifiable" in ident["resolved_fact"]
    assert boundary["state"] == "RESOLVED_NEGATIVE"
    assert "boundary-sensitive" in boundary["resolved_fact"]
    assert license_row["state"] == "RESOLVED_NEGATIVE"
    assert "redistribution is blocked" in license_row["resolved_fact"]
    assert receipt["claim_allowed"] is False


def test_common_nuisance_ablation_is_positive_operational_resolution_only():
    receipt = current_receipt()
    rows = {row["token"]: row for row in receipt["results"]}
    ablation = rows["TOKEN_VAZIO_SN_COMMON_NUISANCE_ABLATION"]
    assert ablation["state"] == "RESOLVED"
    assert ablation["evidence_verified"] is True
    assert "RLL remained effectively LCDM-like" in ablation["resolved_fact"]
    assert receipt["claim_allowed"] is False


def test_legacy_real_bayes_reduces_and_modern_dovekie_gate_is_closed():
    receipt = current_receipt()
    rows = {row["token"]: row for row in receipt["results"]}
    bayes = rows["TOKEN_VAZIO_REAL_BAYES_INFERENCE"]
    modern = rows["TOKEN_VAZIO_REAL_BAYES_MODERN_3MODEL_PRIOR_LOCK"]
    joint = rows["TOKEN_VAZIO_REAL_BAYES_JOINT_MULTI_PROBE"]

    assert bayes["state"] == "REDUCED"
    assert bayes["evidence_verified"] is True
    assert modern["state"] == "RESOLVED"
    assert modern["evidence_verified"] is True
    assert "lnB(CPL/LCDM)=-0.1107" in modern["resolved_fact"]
    assert joint["state"] == "OPEN_MIXED"
    assert receipt["claim_allowed"] is False


def test_finite_wa_lower_profile_token_is_closed_by_bracketed_receipt():
    receipt = current_receipt()
    rows = {row["token"]: row for row in receipt["results"]}
    lower = rows["TOKEN_VAZIO_CPL_DOVEKIE_WA_LOWER_PROFILE_CLOSURE"]

    assert lower["state"] == "RESOLVED"
    assert lower["evidence_verified"] is True
    assert "wa≈-12.60645" in lower["resolved_fact"]
    assert lower["successors"] == []


def test_desi_generic_gap_is_reduced_not_falsely_called_official():
    receipt = current_receipt()
    rows = {row["token"]: row for row in receipt["results"]}
    generic = rows["TOKEN_VAZIO_DESI_DR2_OFFICIAL_REPRODUCTION"]
    official = rows["TOKEN_VAZIO_DESI_DR2_OFFICIAL_JOINT_CROSSBLOCK_REPRODUCTION"]

    assert generic["state"] == "REDUCED"
    assert generic["evidence_verified"] is True
    assert "13-observable" in generic["resolved_fact"]
    assert official["state"] == "OPEN_EXTERNAL"
    assert receipt["claim_allowed"] is False


def test_act_dr6_availability_reduces_to_pinned_local_reproduction():
    receipt = current_receipt()
    rows = {row["token"]: row for row in receipt["results"]}
    generic = rows["TOKEN_VAZIO_ACT_DR6_LIKELIHOOD"]
    successor = rows["TOKEN_VAZIO_ACT_DR6_CMBONLY_MATERIALIZATION_REPRODUCTION"]

    assert generic["state"] == "REDUCED"
    assert generic["evidence_verified"] is True
    assert "public executable ACT DR6 CMB-only Cobaya likelihood" in generic["resolved_fact"]
    assert successor["state"] == "OPEN_INTERNAL"
    assert receipt["claim_allowed"] is False


def test_class_camb_generic_gap_reduces_without_inventing_rll_perturbations():
    receipt = current_receipt()
    rows = {row["token"]: row for row in receipt["results"]}
    generic = rows["TOKEN_VAZIO_CLASS_CAMB_PERTURBATION_BENCHMARK"]
    baseline = rows["TOKEN_VAZIO_LCDM_CPL_CLASS_CAMB_BASELINE_CROSSCHECK"]
    closure = rows["TOKEN_VAZIO_RLL_PERTURBATION_CLOSURE_RELATIONS"]
    implementation = rows["TOKEN_VAZIO_RLL_CLASS_CAMB_IMPLEMENTATION"]

    assert generic["state"] == "REDUCED"
    assert generic["evidence_verified"] is True
    assert "internal GR matter-growth approximation" in generic["resolved_fact"]
    assert baseline["state"] == "OPEN_INTERNAL"
    assert closure["state"] == "OPEN_MIXED"
    assert implementation["state"] == "OPEN_MIXED"
    assert receipt["claim_allowed"] is False


def test_h0_generic_gap_reduces_to_converged_execution_with_two_open_successors():
    receipt = current_receipt()
    rows = {row["token"]: row for row in receipt["results"]}
    generic = rows["TOKEN_VAZIO_MODERN_H0_FORMAL_LIKELIHOOD"]
    execution = rows["TOKEN_VAZIO_H0_RD_ABLATION_EXECUTION_PROVENANCE"]
    convergence = rows["TOKEN_VAZIO_H0_RD_OPTIMIZATION_CONVERGENCE"]

    assert generic["state"] == "REDUCED"
    assert generic["evidence_verified"] is True
    assert "six-cell H0/r_d fairness matrix" in generic["resolved_fact"]

    assert execution["state"] == "REDUCED"
    assert execution["evidence_verified"] is True
    assert "all 24 selected best fits converged" in execution["resolved_fact"]
    assert "+22.51 to +34.79" in execution["resolved_fact"]
    assert set(execution["successors"]) == {
        "TOKEN_VAZIO_H0_PRIOR_PRIMARY_SOURCE_PROVENANCE",
        "TOKEN_VAZIO_H0_RD_FULL_BOLTZMANN_REPRODUCTION",
    }

    assert convergence["state"] == "RESOLVED"
    assert convergence["evidence_verified"] is True
    assert convergence["successors"] == []
    assert rows["TOKEN_VAZIO_H0_PRIOR_PRIMARY_SOURCE_PROVENANCE"]["state"] == "OPEN_EXTERNAL"
    assert rows["TOKEN_VAZIO_H0_RD_FULL_BOLTZMANN_REPRODUCTION"]["state"] == "OPEN_MIXED"
    assert receipt["claim_allowed"] is False


def test_release_refresh_requires_non_destructive_identity_receipt():
    receipt = current_receipt()
    rows = {row["token"]: row for row in receipt["results"]}
    release = rows["TOKEN_VAZIO_PENDING_RELEASE_REFRESH"]

    assert release["state"] == "RESOLVED"
    assert release["evidence_verified"] is True
    assert "force=false" in release["resolved_fact"]
    assert release["successors"] == []
    assert receipt["claim_allowed"] is False
