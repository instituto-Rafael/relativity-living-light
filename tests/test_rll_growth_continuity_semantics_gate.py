from __future__ import annotations

import math

from tools import rll_growth_continuity_semantics_gate as gate


def test_documented_residual_matches_exact_formula() -> None:
    for zt in (0.1, 1.0, 10.0):
        for wt in (0.05, 0.3, 2.0):
            for z in (0.0, zt, max(2.0 * zt, 0.2), 10.0):
                residual = gate.continuity_residual(
                    z, zt, wt, gate.p_documented_factor(z, zt, wt)
                )
                exact = gate.exact_documented_residual(z, zt, wt)
                assert math.isclose(residual, exact, rel_tol=1e-10, abs_tol=1e-10)


def test_documented_pair_fails_separate_conservation_in_transition() -> None:
    report = gate.build_report()
    assert report["documented_pair_separate_conservation"] == "FAIL"
    assert any(
        abs(row["documented_residual"]) > 1e-8
        for case in report["cases"]
        for row in case["points"]
        if row["z"] > 0.0
    )


def test_conserved_pressure_candidate_closes_algebraically() -> None:
    report = gate.build_report()
    assert report["conserved_candidate_algebraic_closure"] == "MATH_PASS"
    for case in report["cases"]:
        for row in case["points"]:
            assert row["conserved_candidate_closes"] is True


def test_cs2_remains_blocked_until_semantics_selected() -> None:
    report = gate.build_report()
    assert report["state"] == "BLOCKED_UNRESOLVED_PHYSICAL_SEMANTICS"
    assert report["physical_semantics_selected"] is False
    assert report["growth_cs2_state"] == "BLOCKED_BY_CONTINUITY_SEMANTICS"
    assert report["claim_allowed"] is False


def test_gate_does_not_claim_conserved_semantics() -> None:
    report = gate.build_report()
    assert "does not select that semantics" in report["boundary"]
    assert "does not define a physical rest-frame sound speed" in report["boundary"]
