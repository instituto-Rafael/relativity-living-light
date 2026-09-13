from __future__ import annotations

from tools import rll_gap_retrofeedback_v2 as retro


def test_retrofeedback_ledger_is_structurally_valid() -> None:
    report = retro.build_report()
    assert report["pass"] is True
    assert report["claim_allowed"] is False
    assert report["item_count"] == 28


def test_best_next_step_is_growth_sound_speed_policy() -> None:
    report = retro.build_report()
    assert report["best_next_step"]["id"] == "GROWTH-CS2-001"
    assert report["critical_path"][0] == "GROWTH-CS2-001"


def test_cmb_chain_is_promoted_only_to_bounded_evidence() -> None:
    ledger = retro.load(retro.LEDGER)
    by_id = {row["id"]: row for row in ledger["items"]}
    for rid in (
        "CMB-RADIATION-001",
        "CMB-ZSTAR-001",
        "CMB-CS-001",
        "CMB-RS-001",
        "CMB-BENCH-001",
    ):
        assert by_id[rid]["state"] == "EVIDENCED_FOCUSED"
        assert by_id[rid]["claim_allowed"] is False
    assert "does not validate growth" in by_id["CMB-BENCH-001"]["exclusive_boundary"]


def test_growth_negative_evidence_is_not_erased() -> None:
    ledger = retro.load(retro.LEDGER)
    growth = next(row for row in ledger["items"] if row["id"] == "GROWTH-THEORY-001")
    assert growth["state"] == "NEGATIVE_EVIDENCE_TOKEN_DECOMPOSED"
    assert any("0 of 9" in item for item in growth["evidence"])
    assert growth["claim_allowed"] is False


def test_logarithmic_priority_is_governance_only() -> None:
    ledger = retro.load(retro.LEDGER)
    policy = ledger["logarithmic_priority_policy"]
    assert policy["purpose"] == "operational triage only; never scientific evidence"
    assert ledger["multilevel_permutation_policy"]["blind_cartesian_product"] == "FORBIDDEN"
