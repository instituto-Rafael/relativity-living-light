import math

import pytest

from data.pipelines.geomagnetism.pole_dynamics_gate import (
    SQRT3_OVER_2,
    baseline,
    fixed_ratio_log_rms,
    frozen_flux_residual,
    implicit_zero_acceleration,
    implicit_zero_velocity,
    phase_passage_period_years,
    scan_zero_mean_sinusoid_periods,
    source_amplitude_sensitivity,
)


def test_chaos8_m13_phase_period_cross_derivation():
    period = phase_passage_period_years(3485.0, 13, 200.0)
    assert period == pytest.approx(8.421884921354176, rel=1e-12)
    assert 8.0 < period < 9.0


def test_implicit_moving_zero_velocity_and_acceleration():
    jacobian = ((1.0, 0.0), (0.0, 1.0))
    velocity = implicit_zero_velocity(jacobian, (-3.0, -1.6))
    assert velocity == pytest.approx((3.0, 1.6))

    acceleration = implicit_zero_acceleration(
        jacobian,
        (0.0, -0.8),
        ((0.0, 0.0), (0.0, 0.0)),
        (((0.0, 0.0), (0.0, 0.0)), ((0.0, 0.0), (0.0, 0.0))),
        velocity,
    )
    assert acceleration == pytest.approx((0.0, 0.8))


def test_source_sensitivity_is_negative_inverse_j_source():
    jacobian = ((1.0, 0.0), (0.0, 1.0))
    sensitivity = source_amplitude_sensitivity(jacobian, (2.0, -1.0))
    assert sensitivity == pytest.approx((-2.0, 1.0))


def test_frozen_flux_synthetic_closure():
    residual = frozen_flux_residual(-7.0, 3.0, 2.0, 2.0)
    assert residual == pytest.approx(0.0, abs=1e-15)


def test_sinusoidal_period_scan_recovers_synthetic_8p4_year_signal():
    times = [0.25 * i for i in range(49)]
    true_period = 8.4
    values = [
        1.7 * math.sin(2.0 * math.pi * t / true_period)
        - 0.4 * math.cos(2.0 * math.pi * t / true_period)
        for t in times
    ]
    result = scan_zero_mean_sinusoid_periods(times, values)
    assert result["best"]["period_year"] == pytest.approx(8.4, abs=1e-12)
    assert result["best"]["rmse"] < 1e-12


def test_pre_registered_sqrt3_ratio_gate_is_zero_only_for_exact_fixture():
    values = [SQRT3_OVER_2 ** i for i in range(8)]
    assert fixed_ratio_log_rms(values) < 1e-15

    perturbed = list(values)
    perturbed[-1] *= 1.02
    assert fixed_ratio_log_rms(perturbed) > 0.0


def test_baseline_keeps_real_data_and_cosmological_claims_closed():
    receipt = baseline()
    assert receipt["epistemic_state"] == "SYNTHETIC_AND_LITERATURE_DERIVED_ONLY"
    assert receipt["result"]["claim_allowed"] is False
    assert receipt["result"]["boundaries"]["RLL_cosmology_supported_by_geomagnetism"] is False
    assert receipt["real_data_gates"]["WMM2025_coefficients_bound"] == "TOKEN_VAZIO"
    assert receipt["real_data_gates"]["real_sqrt3_ratio_test"] == "TOKEN_VAZIO"
