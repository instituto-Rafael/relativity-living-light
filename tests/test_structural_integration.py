import json
import math
from pathlib import Path

import pytest

from rll.structural_integration import (
    EpistemicStatus,
    ExecutionDecision,
    TransitionParameters,
    alcock_paczynski_ratio,
    bulk_viscous_pressure,
    distance_duality_eta,
    evaluate_branch_readiness,
    frb_delay_residual,
    interaction_source,
    logistic_transition_z,
    stable_payload_hash,
    transition_density_factor_z,
    transition_density_fraction_z,
    transition_w_eff_z,
    validate_integration_registry,
    validate_source_registry,
)

ROOT = Path(__file__).resolve().parents[1]


def test_logistic_transition_is_bounded_and_centered():
    assert logistic_transition_z(1.0, 1.0, 0.2) == pytest.approx(0.5)
    assert 0.0 < logistic_transition_z(50.0, 1.0, 0.2) < 1e-10
    assert 0.999 < logistic_transition_z(0.0, 5.0, 0.2) <= 1.0


def test_transition_density_has_expected_limits():
    params = TransitionParameters(omega_s0=0.02, z_t=1.0, w_t=0.1)
    assert transition_density_fraction_z(0.0, params) == pytest.approx(0.02)
    z = 5.0
    assert transition_density_factor_z(z, 1.0, 0.1) == pytest.approx((1 + z) ** 3, rel=1e-8)


def test_effective_eos_is_finite():
    for z in (0.0, 0.5, 1.0, 2.0, 10.0):
        assert math.isfinite(transition_w_eff_z(z, 1.0, 0.3))


def test_dissipative_and_interaction_operators():
    assert bulk_viscous_pressure(2.0, 3.0, 0.5) == pytest.approx(-2.5)
    assert interaction_source(-0.1, 70.0, 0.3) == pytest.approx(-2.1)


def test_distance_operators():
    z = 1.0
    d_a = 1000.0
    d_l = (1 + z) ** 2 * d_a
    assert distance_duality_eta(d_l, d_a, z) == pytest.approx(1.0)
    assert alcock_paczynski_ratio(20.0, 10.0) == pytest.approx(2.0)


def test_frb_residual_does_not_assume_new_physics():
    assert frb_delay_residual(12.0, 2.0, 1.0, 5.0) == pytest.approx(2.0)


def test_hash_is_order_invariant():
    assert stable_payload_hash({"a": 1, "b": 2}) == stable_payload_hash({"b": 2, "a": 1})


def test_source_registry_is_claim_bounded():
    payload = json.loads((ROOT / "data/registries/rll_recent_primary_sources_2026.json").read_text())
    assert validate_source_registry(payload) == []
    assert payload["claim_allowed"] is False


def test_source_registry_keeps_legacy_sources_and_bounded_c11_sources():
    payload = json.loads((ROOT / "data/registries/rll_recent_primary_sources_2026.json").read_text())
    sources = {item["source_id"]: item for item in payload["sources"]}
    legacy = {
        "DESI-DR2-BAO-2025",
        "GEDE-DESI-DR2-2025",
        "BULK-VISCOSITY-DESI-2026",
        "INTERACTING-DARK-SECTOR-2025",
        "ANTON-SCHMIDT-DESI-2026",
        "DESI-SN-DISTANCE-CROSSCHECK-2026",
        "CDDR-PANTHEON-BAO-2026",
        "FRB-GALAXY-CROSSCORRELATION-2025",
        "FRB-COSMOLOGY-REVIEW-2026",
        "ACT-DR6-BIREFRINGENCE-2025",
        "BIREFRINGENCE-DM-DE-2026",
    }
    assert legacy <= set(sources)
    c11 = {
        "BH-THERMODYNAMICS-REVIEW-2026",
        "MPEMBA-PRX-2026",
        "MPEMBA-THERMOMAJORIZATION-2025",
        "UNRUH-MPEMBA-2026",
        "HOLOGRAPHIC-MPEMBA-2026",
        "EHT-M87-VARIABILITY-2025",
        "EHT-M87-JET-BASE-2026",
        "EHT-2026-D01-01",
    }
    assert c11 <= set(sources)
    assert sources["HOLOGRAPHIC-MPEMBA-2026"]["verification_status"] == "metadata_verified"
    assert "preprint" in sources["HOLOGRAPHIC-MPEMBA-2026"]["safe_use"].lower()
    assert "TOKEN_VAZIO" in sources["EHT-2026-D01-01"]["safe_use"]


def test_integration_registry_preserves_raw_data():
    payload = json.loads((ROOT / "data/registries/rll_operational_integration_registry.json").read_text())
    assert validate_integration_registry(payload) == []
    assert payload["raw_data_policy"] == "immutable"
    assert payload["claim_allowed"] is False


def test_b10_mpemba_route_is_append_only_and_fail_closed():
    payload = json.loads((ROOT / "data/registries/rll_operational_integration_registry.json").read_text())
    branches = {branch["branch_id"]: branch for branch in payload["branches"]}
    for index in range(10):
        assert any(branch_id.startswith(f"B{index:02d}_") for branch_id in branches)
    b10 = branches["B10_black_hole_thermodynamics_mpemba_falsifier"]
    assert b10["status"] == EpistemicStatus.PARTIAL.value
    assert "checksum_verified_real_time_series" in b10["required_artifacts"]
    assert "independent_reproduction" in b10["required_artifacts"]
    decision, missing = evaluate_branch_readiness(b10, ["mpemba_horizon_contract"])
    assert decision is ExecutionDecision.BLOCKED
    assert "checksum_verified_real_time_series" in missing


def test_strong_gravity_successor_preserves_historical_calibration():
    payload = json.loads((ROOT / "data/registries/rll_strong_gravity_calibration_registry.json").read_text())
    assert payload["raw_data_policy"] == "immutable"
    assert payload["claim_allowed"] is False
    assert payload["generated_at"] == "2026-07-17"
    assert payload["committed_numeric_result"] == "results/strong_gravity_calibration/session_reference_sweep_20260717.json"
    assert [item["id"] for item in payload["heuristics"]] == [f"H{i}_{name}" for i, name in [
        (1, "scale_separation"),
        (2, "force_dominance"),
        (3, "phase_ladder"),
        (4, "self_gravity"),
        (5, "transduction"),
        (6, "radiative_threshold"),
        (7, "recurrence"),
        (8, "falsifier"),
    ]]
    extensions = {item["id"]: item for item in payload["successor_extensions"]}
    b10 = extensions["B10_black_hole_thermodynamics_mpemba_falsifier"]
    assert b10["claim_allowed"] is False
    for key in ("implementation", "contract", "tests", "atlas", "falsifiability_protocol"):
        assert (ROOT / b10[key]).exists(), key
    assert "independent reproduction" in b10["protected_gaps"]


def test_branch_readiness_reports_missing_artifacts():
    branch = {
        "status": EpistemicStatus.HYPOTHESIS.value,
        "required_artifacts": ["a", "b"],
    }
    decision, missing = evaluate_branch_readiness(branch, ["a"])
    assert decision is ExecutionDecision.BLOCKED
    assert missing == ["b"]


def test_token_vazio_branch_stays_token_vazio():
    branch = {
        "status": EpistemicStatus.TOKEN_VAZIO.value,
        "required_artifacts": [],
    }
    decision, reasons = evaluate_branch_readiness(branch, [])
    assert decision is ExecutionDecision.TOKEN_VAZIO
    assert reasons


@pytest.mark.parametrize(
    "call",
    [
        lambda: logistic_transition_z(-1, 1, 1),
        lambda: logistic_transition_z(1, 1, 0),
        lambda: distance_duality_eta(0, 1, 1),
        lambda: alcock_paczynski_ratio(1, 0),
        lambda: frb_delay_residual(1, -1, 1, 1),
    ],
)
def test_invalid_inputs_fail_closed(call):
    with pytest.raises(ValueError):
        call()
