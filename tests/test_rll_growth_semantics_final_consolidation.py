from __future__ import annotations

from tools import rll_growth_semantics_final_consolidation as final

def test_final_consolidation_is_fail_closed() -> None:
    report = final.build_report()
    assert report["state"] == "CONSOLIDATED_FAIL_CLOSED"
    assert report["claim_allowed"] is False
    assert report["publication_ready"] is False

def test_a0_negative_evidence_is_preserved() -> None:
    report = final.build_report()
    assert report["A0"]["state"] == "FALSIFIED_AS_GLOBAL_DEFAULT"
    assert report["A0"]["cases"] == 9
    assert report["A0"]["passing_cases"] == 0

def test_a1_is_not_promoted_to_exact_perturbations() -> None:
    report = final.build_report()
    assert report["A1"]["state"] == "OPEN_BOUNDED_NECESSARY_CONDITIONS_PASS"
    assert report["A1"]["continuity_math"] == "PASS"
    assert report["A1"]["exact_perturbations"] == "TOKEN_VAZIO"

def test_b_remains_formal_not_physical() -> None:
    report = final.build_report()
    assert report["B"]["state"] == "FORMAL_Q_PASS_PHYSICS_BLOCKED"
    assert report["B"]["receiver_sector_implemented"] is False
    assert report["B"]["covariant_Q_mu_implemented"] is False

def test_c_is_operational_not_physical_selection() -> None:
    report = final.build_report()
    assert report["C"]["state"] == "SURVIVES_AS_OPERATIONAL_BASELINE"
    assert report["operational_baseline"] == "C_PHENOMENOLOGICAL_BACKGROUND"
    assert report["physical_semantics_selected"] is False
    assert report["selected_semantics"] == "TOKEN_VAZIO"

def test_downstream_science_remains_blocked() -> None:
    report = final.build_report()
    assert report["downstream"]["GROWTH_CS2_001"].startswith("BLOCKED")
    assert report["downstream"]["GROWTH_CONSERVATION_001"].startswith("BLOCKED")
    assert report["downstream"]["FIT_MODELSEL_001"] == "BLOCKED_BY_DEPENDENCY"

def test_validator_accepts_only_the_fail_closed_state() -> None:
    report = final.build_report()
    assert final.validate(report) == []
