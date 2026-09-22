from __future__ import annotations

from tools.rll_perturbation_gauge_regularization_preflight_v1 import build


def test_regular_variable_preflight_passes_without_claim_promotion():
    payload = build()
    assert payload["state"] == "C07_C08_REGULAR_VARIABLE_PREFLIGHT_PASS_IC_EQUATIONS_OPEN"
    assert payload["sweep"]["passing_cases"] == 9
    assert payload["sweep"]["total_cases"] == 9
    assert payload["claim_allowed"] is False
    assert payload["token_resolution"] == "NOT_RESOLVED"
    assert payload["class_camb_unlock"] is False


def test_regular_variable_contract_preserves_open_dynamics_and_ic():
    payload = build()
    blockers = set(payload["hard_blockers"])
    assert "C01_DELTA_RHO_EVOLUTION_IN_REFERENCE_GAUGE" in blockers
    assert "C02_Q_MOMENTUM_EVOLUTION_IN_REFERENCE_GAUGE" in blockers
    assert "C07_SUPERHORIZON_INITIAL_CONDITIONS" in blockers
    assert "C08_ANALYTIC_ENTHALPY_DEGENERACY_LIMIT" in blockers
    assert payload["primary_candidate_variables"] == ["delta_rho_s", "q_s"]


def test_every_case_closes_background_enthalpy_identity_and_avoids_crossing():
    payload = build()
    for row in payload["sweep"]["cases"]:
        assert row["pass"] is True
        assert row["gates"]["no_negative_crossing"] is True
        assert row["gates"]["enthalpy_identity_closed"] is True
        assert row["gates"]["theta_roundtrip_where_conditioned"] is True
        assert row["gates"]["no_epsilon_clipping_used"] is True
        assert row["max_normalized_enthalpy_identity_residual"] <= 1.0e-10


def test_degeneracy_is_reported_not_clipped_or_silently_removed():
    payload = build()
    assert "observed_enthalpy_degeneracy" in payload["sweep"]
    assert payload["theta_policy"] == "derived diagnostic only where enthalpy is conditioned"
    assert "does not define the missing dynamics" in payload["scientific_boundary"]
