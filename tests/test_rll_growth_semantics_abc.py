from __future__ import annotations

from tools import rll_growth_semantics_abc as abc

def test_claim_boundary_remains_closed() -> None:
    report = abc.build_report()
    assert report["claim_allowed"] is False
    assert report["selected_semantics"] == "TOKEN_VAZIO"
    assert report["comparison"]["unique_physical_winner"] is False

def test_route_a_closes_continuity() -> None:
    report = abc.build_report()
    assert report["route_A"]["continuity_math"] == "PASS"
    assert all(abs(row["continuity_residual"]) <= 1e-10 for row in report["route_A"]["rows"])

def test_route_a_canonical_kinetic_sign_sweep_is_nonnegative() -> None:
    report = abc.build_report()
    assert report["route_A"]["canonical_kinetic_sign_sweep"] == "PASS_NO_W_LT_MINUS1"
    assert report["route_A"]["min_one_plus_w"] >= -1e-10

def test_route_b_formal_q_matches_documented_residual() -> None:
    report = abc.build_report()
    assert report["route_B"]["formal_q_source"] == "PASS"
    assert report["route_B"]["formal_equal_opposite_total_accounting"] == "PASS"

def test_route_b_stays_physically_blocked() -> None:
    report = abc.build_report()
    assert report["route_B"]["receiver_sector_implemented"] is False
    assert report["route_B"]["covariant_Q_mu_implemented"] is False

def test_route_c_is_background_only() -> None:
    report = abc.build_report()
    assert report["route_C"]["background_claim_boundary"] == "PASS"
    assert report["route_C"]["physical_cs2"] == "TOKEN_VAZIO"
    assert report["route_C"]["dark_sector_perturbations"] == "BLOCKED"

def test_operational_order_is_not_physical_selection() -> None:
    report = abc.build_report()
    assert report["comparison"]["operational_order"][0] == "A_TEST_FIRST"
    assert "not evidence that A is physically true" in report["comparison"]["reason"]
