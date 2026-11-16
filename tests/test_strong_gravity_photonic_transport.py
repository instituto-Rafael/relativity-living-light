import math

import pytest

from rll.strong_gravity_photonic_transport import (
    adiabatic_radiation_energy_density,
    adiabatic_radiation_temperature,
    compose_frequency_gains,
    convergent_compression_number,
    damkohler_number,
    electron_cyclotron_angular_frequency,
    electron_plasma_angular_frequency,
    epistemic_contract,
    first_order_completion,
    invariant_transfer_constant_coeff,
    logistic_midpoint_slope,
    logistic_transition,
    log_hardening,
    ram_pressure_ratio,
    spiral_radial_wavelength,
    upside_down_hammer_number,
)


def test_compression_number_is_dimensionless_nonnegative():
    assert convergent_compression_number(-2.0, 0.25) == pytest.approx(0.5)
    assert convergent_compression_number(+2.0, 0.25) == 0.0


def test_hammer_number_fixes_previous_dimensional_error():
    value = upside_down_hammer_number(
        expansion_scalar=-4.0,
        flow_time_s=0.5,
        fast_mach=2.0,
        ram_pressure=30.0,
        thermal_pressure=5.0,
        magnetic_pressure=3.0,
        radiation_pressure=2.0,
    )
    # C_down=2, M_f=2, R_ram=3 -> H_down=12.
    assert value == pytest.approx(12.0)


def test_ram_pressure_ratio_requires_supporting_pressure():
    assert ram_pressure_ratio(30, 5, 3, 2) == pytest.approx(3.0)
    with pytest.raises(ValueError):
        ram_pressure_ratio(1, 0, 0, 0)


def test_damkohler_first_order_completion_is_monotonic():
    assert damkohler_number(2, 1) == pytest.approx(2.0)
    x1 = first_order_completion(0.1, 1.0)
    x2 = first_order_completion(1.0, 1.0)
    x3 = first_order_completion(10.0, 1.0)
    assert 0 < x1 < x2 < x3 < 1
    assert x2 == pytest.approx(1.0 - math.exp(-1.0))


def test_frequency_gains_multiply_and_log_hardening_adds():
    gains = [2.0, 0.5, 3.0]
    assert compose_frequency_gains(gains) == pytest.approx(3.0)
    assert log_hardening(gains) == pytest.approx(math.log(3.0))
    with pytest.raises(ValueError):
        compose_frequency_gains([1.0, 0.0])


def test_spiral_wavelength_contracts_as_wavenumber_grows():
    assert spiral_radial_wavelength(4.0) < spiral_radial_wavelength(2.0)
    with pytest.raises(ValueError):
        spiral_radial_wavelength(0.0)


def test_logistic_exact_midpoint_and_slope():
    assert logistic_transition(7.0, 7.0, 2.0) == pytest.approx(0.5)
    assert logistic_midpoint_slope(2.0) == pytest.approx(-0.125)
    assert logistic_transition(8.0, 7.0, 2.0) < 0.5


def test_invariant_transfer_constant_coeff_exact_solution():
    # Pure emission limit.
    assert invariant_transfer_constant_coeff(2.0, 3.0, 0.0, 4.0) == pytest.approx(14.0)
    # Pure absorption.
    assert invariant_transfer_constant_coeff(2.0, 0.0, 0.5, 2.0) == pytest.approx(2.0 / math.e)
    # Non-negative source/opacity preserves non-negative intensity.
    assert invariant_transfer_constant_coeff(0.0, 1.0, 2.0, 3.0) >= 0.0


def test_adiabatic_radiation_compression_scaling():
    assert adiabatic_radiation_energy_density(1.0, 8.0, 1.0) == pytest.approx(16.0)
    assert adiabatic_radiation_temperature(1.0, 8.0, 1.0) == pytest.approx(2.0)


def test_plasma_and_cyclotron_frequencies_are_physical():
    assert electron_plasma_angular_frequency(0.0) == 0.0
    assert electron_plasma_angular_frequency(1e18) > 0.0
    assert electron_cyclotron_angular_frequency(-1.0) > 0.0


def test_epistemic_contract_never_promotes_claim():
    contract = epistemic_contract()
    assert contract["claim_allowed"] is False
    assert contract["exclusive_RLL_observable"] == "TOKEN_VAZIO"
    assert contract["calibrated_transport_solution"] == "TOKEN_VAZIO"
