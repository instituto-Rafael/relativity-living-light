from __future__ import annotations

import math

import pytest

from data.pipelines.cosmology.late_time_cascade_observables import (
    C_M_S,
    CascadeTemplate,
    cascade_transfer,
    damp_bao_wiggle,
    observed_redshift_from_peculiar_velocity,
    project_power_point,
    run_projection,
)


def test_exact_null_returns_baseline_power() -> None:
    template = CascadeTemplate(amplitude=0.0, damping_k=0.2)
    result = project_power_point(0.1, 0.5, 123.0, template)
    assert result["cascade_transfer"] == 0.0
    assert result["projected_power"] == 123.0
    assert result["delta_power"] == 0.0


def test_transfer_decays_with_k_for_positive_amplitude() -> None:
    template = CascadeTemplate(amplitude=0.1, damping_k=0.2)
    assert cascade_transfer(0.05, 0.0, template) > cascade_transfer(0.30, 0.0, template)


def test_bao_damping_never_amplifies_wiggle_magnitude() -> None:
    for wiggle in (0.04, -0.04):
        damped = damp_bao_wiggle(0.2, wiggle, 3.0)
        assert abs(damped) <= abs(wiggle)


def test_zero_bao_damping_preserves_existing_wiggle() -> None:
    assert damp_bao_wiggle(0.2, -0.03, 0.0) == -0.03


def test_peculiar_velocity_redshift_mapping_first_order() -> None:
    z_cos = 0.1
    v = 300_000.0
    observed = observed_redshift_from_peculiar_velocity(z_cos, v)
    expected = z_cos + (1.0 + z_cos) * v / C_M_S
    assert observed == pytest.approx(expected)


def test_superluminal_or_light_speed_velocity_is_rejected() -> None:
    with pytest.raises(ValueError):
        observed_redshift_from_peculiar_velocity(0.1, C_M_S)
    with pytest.raises(ValueError):
        observed_redshift_from_peculiar_velocity(0.1, -C_M_S * 1.01)


def test_projection_rejects_negative_power_multiplier() -> None:
    template = CascadeTemplate(amplitude=-2.0, damping_k=1.0)
    with pytest.raises(ValueError):
        project_power_point(0.0, 0.0, 10.0, template)


def test_receipt_preserves_claim_and_bridge_boundaries() -> None:
    receipt = run_projection(
        {
            "template": {"amplitude": 0.0, "damping_k": 0.2},
            "power_points": [{"k": 0.1, "z": 0.2, "baseline_power": 100.0}],
            "bao_wiggles": [{"k": 0.1, "wiggle": 0.02, "sigma_c": 1.0}],
            "peculiar_velocity_points": [
                {"z_cosmological": 0.05, "v_parallel_m_s": 100000.0}
            ],
        }
    )
    assert receipt["claim_allowed"] is False
    assert receipt["background_modified"] is False
    assert receipt["bao_origin_claimed"] is False
    assert "strain_to_trigger_energy" in receipt["token_vazio"]
    assert receipt["power_points"][0]["projected_power"] == 100.0
    assert len(receipt["receipt_sha256"]) == 64
    assert all(ch in "0123456789abcdef" for ch in receipt["receipt_sha256"])


def test_template_requires_positive_damping_scale() -> None:
    with pytest.raises(ValueError):
        cascade_transfer(0.1, 0.0, CascadeTemplate(amplitude=0.1, damping_k=0.0))


def test_projected_power_is_finite_for_bounded_inputs() -> None:
    result = project_power_point(
        0.1,
        1.0,
        500.0,
        CascadeTemplate(amplitude=0.05, damping_k=0.2, beta=-1.0),
    )
    assert math.isfinite(result["projected_power"])
    assert result["projected_power"] >= 0.0
