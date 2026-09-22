from __future__ import annotations

from tools.rll_perturbation_a1_restframe_candidate_v1 import (
    CS2_REST,
    build,
    evaluate_case,
)


def test_a1_candidate_is_fail_closed_and_does_not_resolve_theory_token():
    payload = build()
    assert payload["claim_allowed"] is False
    assert payload["publication_ready"] is False
    assert payload["token_resolution"] == "NOT_RESOLVED"
    assert payload["class_camb_unlock"] is False
    assert payload["resolved_slots"] == []
    assert "C07_GAUGE_AND_INITIAL_CONDITIONS" in payload["hard_blockers"]


def test_a1_declared_sweep_passes_only_necessary_background_closure_gates():
    payload = build()
    assert payload["state"] == "A1_1_NECESSARY_GATES_PASS_GAUGE_IC_OPEN"
    assert payload["sweep"]["total_cases"] == 9
    assert payload["sweep"]["passing_cases"] == 9
    for row in payload["sweep"]["cases"]:
        assert row["pass"] is True
        assert row["gates"]["finite_everywhere"] is True
        assert row["gates"]["rho_positive"] is True
        assert row["gates"]["continuity_closed"] is True
        assert row["gates"]["canonical_kinetic_sign_necessary"] is True
        assert row["gates"]["cs2_rest_bounded"] is True


def test_cs2_rest_one_is_explicit_candidate_assumption_not_background_derivation():
    payload = build()
    assert CS2_REST == 1.0
    assert payload["assumptions"]["cs2_rest"] == 1.0
    assert "not evidence that c_s,rest^2=1 is a property of RLL" in payload["scientific_boundary"]


def test_canonical_mid_sweep_case_is_regular():
    row = evaluate_case(1.0, 0.3)
    assert row["pass"] is True
    assert row["rho_min"] > 0.0
    assert row["one_plus_w_min"] >= -1.0e-10
    assert row["max_abs_continuity_residual"] <= 1.0e-10
