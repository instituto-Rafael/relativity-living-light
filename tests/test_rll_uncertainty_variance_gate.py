from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "rll_uncertainty_variance_gate.py"
spec = importlib.util.spec_from_file_location("rll_uncertainty_variance_gate", MODULE_PATH)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

REPO = Path(__file__).resolve().parents[1]
LEDGER_PATH = REPO / "data" / "governance" / "RLL_UNCERTAINTY_VARIANCE_LEDGER_20260807_V1.json"


def load_ledger() -> dict:
    return json.loads(LEDGER_PATH.read_text(encoding="utf-8"))


def test_canonical_ledger_is_valid_and_fail_closed() -> None:
    ledger = load_ledger()
    module.validate_ledger(ledger)
    receipt = module.build_receipt(ledger)
    assert receipt["claim_allowed"] is False
    assert receipt["publication_ready"] is False
    assert receipt["scientific_gate"] == "BLOCKED_P0_TOKEN_VAZIO"
    assert receipt["priority_counts"]["P0"] >= 1
    assert receipt["file_count"] == len(ledger["file_states"])
    assert receipt["paper_count"] == len(ledger["paper_adjustments"])
    assert receipt["next_action"] == "DESI_DR2_OFFICIAL_REPRODUCTION"


def test_claim_promotion_is_rejected() -> None:
    ledger = load_ledger()
    ledger["claim_allowed"] = True
    try:
        module.validate_ledger(ledger)
    except ValueError as exc:
        assert "claim_allowed=false" in str(exc)
    else:
        raise AssertionError("claim_allowed=true must be rejected")


def test_unknown_variance_axis_is_rejected() -> None:
    ledger = load_ledger()
    ledger["file_states"][0]["variance_axes"] = ["made_up_axis"]
    try:
        module.validate_ledger(ledger)
    except ValueError as exc:
        assert "unknown variance axes" in str(exc)
    else:
        raise AssertionError("unknown variance axis must be rejected")


def test_open_paper_requires_explicit_token_vazio() -> None:
    ledger = load_ledger()
    ledger["paper_adjustments"][0]["token_vazio"] = "unknown"
    try:
        module.validate_ledger(ledger)
    except ValueError as exc:
        assert "TOKEN_VAZIO" in str(exc)
    else:
        raise AssertionError("paper without explicit TOKEN_VAZIO must be rejected")


def test_queue_cannot_hide_missing_next_test() -> None:
    ledger = load_ledger()
    ledger["urgency_queue"][0]["next_test"] = ""
    try:
        module.validate_ledger(ledger)
    except ValueError as exc:
        assert "next_test is required" in str(exc)
    else:
        raise AssertionError("queue item without falsifiable next test must be rejected")


def test_queue_priority_cannot_return_from_p1_to_p0() -> None:
    ledger = load_ledger()
    changed = copy.deepcopy(ledger)
    changed["urgency_queue"][6]["priority"] = "P1"
    changed["urgency_queue"][7]["priority"] = "P0"
    try:
        module.validate_ledger(changed)
    except ValueError as exc:
        assert "higher priority" in str(exc)
    else:
        raise AssertionError("priority inversion must be rejected")


def test_stale_registry_is_exposed_not_deleted() -> None:
    receipt = module.build_receipt(load_ledger())
    stale = receipt["stale_or_superseded_files"]
    assert "data/governance/RLL_MODERN_VALIDATION_GAPS_20260807_V1.json" in stale
    assert "docs/science/RLL_MODERN_VALIDATION_GAPS_20260807_V1.md" in stale


def test_urgency_score_is_explicitly_non_scientific() -> None:
    receipt = module.build_receipt(load_ledger())
    assert "not scientific significance" in receipt["triage_note"]
