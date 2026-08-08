from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.rll_token_vazio_reconcile import apply_rule_overrides, load_json, reconcile
from tools.rll_token_vazio_reconcile_v2 import (
    DEFAULT_INPUT,
    DEFAULT_INPUT_DELTAS,
    DEFAULT_OVERRIDE_DELTAS,
    DEFAULT_OVERRIDES,
    DEFAULT_RULES,
    build_current_view,
    merge_input_delta,
)

ROOT = Path(__file__).resolve().parents[1]


def v1_view():
    base = load_json(ROOT / DEFAULT_RULES)
    v1 = apply_rule_overrides(base, load_json(ROOT / DEFAULT_OVERRIDES))
    return reconcile(ROOT, load_json(ROOT / DEFAULT_INPUT), v1, "2026-08-08T00:15:00Z")


def v2_view():
    return build_current_view(ROOT, generated_at="2026-08-08T04:30:00Z")


def test_v1_historical_view_is_unchanged():
    receipt = v1_view()
    assert receipt["summary"]["input_tokens"] == 30
    assert receipt["summary"]["terminal_resolved"] == 9
    assert receipt["summary"]["reduced_generic"] == 7
    assert receipt["summary"]["open"] == 14
    assert "TOKEN_VAZIO_ACT_DR6_CMBONLY_MATERIALIZATION_REPRODUCTION" in receipt["canonical_open_tokens"]
    assert "TOKEN_VAZIO_H0_RD_FULL_BOLTZMANN_REPRODUCTION" in receipt["canonical_open_tokens"]
    assert "TOKEN_VAZIO_NOT_YET_CLASSIFIED_ALL_582_REFS" in receipt["canonical_open_tokens"]


def test_v2_adds_three_successors_without_hiding_open_work():
    receipt = v2_view()
    assert receipt["claim_allowed"] is False
    assert receipt["publication_ready"] is False
    assert receipt["summary"]["input_tokens"] == 33
    assert receipt["summary"]["terminal_resolved"] == 10
    assert receipt["summary"]["reduced_generic"] == 9
    assert receipt["summary"]["open"] == 14
    assert not any(row["state"] == "OPEN_EVIDENCE_MISSING" for row in receipt["results"])


def test_act_materialization_resolves_only_to_posterior_successor():
    rows = {row["token"]: row for row in v2_view()["results"]}
    materialization = rows["TOKEN_VAZIO_ACT_DR6_CMBONLY_MATERIALIZATION_REPRODUCTION"]
    posterior = rows["TOKEN_VAZIO_ACT_DR6_LCDM_POSTERIOR_CHAIN_REPRODUCTION"]
    assert materialization["state"] == "RESOLVED"
    assert materialization["evidence_verified"] is True
    assert posterior["state"] == "OPEN_INTERNAL"
    assert "posterior" in posterior["next_action"].lower()


def test_h0_rd_is_reduced_not_falsely_resolved():
    rows = {row["token"]: row for row in v2_view()["results"]}
    crosscheck = rows["TOKEN_VAZIO_H0_RD_FULL_BOLTZMANN_REPRODUCTION"]
    integration = rows["TOKEN_VAZIO_H0_RD_FULL_BOLTZMANN_INFERENCE_INTEGRATION"]
    assert crosscheck["state"] == "REDUCED"
    assert crosscheck["evidence_verified"] is True
    assert "0.596-0.599%" in crosscheck["resolved_fact"]
    assert integration["state"] == "OPEN_INTERNAL"
    assert "24" in integration["next_action"]


def test_582_label_is_reduced_to_current_35_ref_semantic_review():
    rows = {row["token"]: row for row in v2_view()["results"]}
    historical = rows["TOKEN_VAZIO_NOT_YET_CLASSIFIED_ALL_582_REFS"]
    successor = rows["TOKEN_VAZIO_DIVERGED_OR_DESCENDANT_REF_SEMANTIC_REVIEW"]
    assert historical["state"] == "REDUCED"
    assert historical["evidence_verified"] is True
    assert "599" in historical["resolved_fact"]
    assert "35" in historical["resolved_fact"]
    assert successor["state"] == "OPEN_INTERNAL"
    assert "35" in successor["next_action"]


def test_input_delta_rejects_duplicate_existing_token():
    base = load_json(ROOT / DEFAULT_INPUT)
    delta = {
        "schema": "rll.gap_closure_input_delta.v1",
        "claim_allowed": False,
        "tokens": [dict(base["tokens"][0])],
    }
    with pytest.raises(ValueError, match="duplicate input delta token"):
        merge_input_delta(base, delta)


def test_v2_chain_metadata_is_explicit_and_ordered():
    receipt = v2_view()
    assert receipt["view"] == "RLL_TOKEN_VAZIO_RECONCILIATION_V2_APPEND_ONLY"
    assert [row["ordinal"] for row in receipt["override_chain"]] == [1, 2]
    assert receipt["override_chain"][0]["path"].endswith("RLL_TOKEN_VAZIO_CLOSURE_OVERRIDES_20260807_V1.json")
    assert receipt["override_chain"][1]["path"].endswith("RLL_TOKEN_VAZIO_CLOSURE_OVERRIDES_20260808_V2.json")
    assert len(receipt["input_deltas"]) == 1
    assert receipt["policy"]["input_deltas_preserve_prior_denominator_history"] is True
    assert receipt["policy"]["override_order_is_explicit"] is True
