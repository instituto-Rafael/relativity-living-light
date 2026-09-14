import pytest

from rll.strong_gravity_calibration import (
    C,
    E_CHARGE,
    M_E,
    M_P,
    CascadeRates,
    CascadeState,
    Regime,
    advance_cascade_state,
    calibration_payload,
    classify_gravitothermal,
    classify_photon_channel,
    compressive_heating_rate,
    coulomb_to_gravity_force_ratio,
    gravitational_radius,
    ideal_gas_volume_m3,
    magnetoelectric_transduction,
    oscillator_quality_factor,
    photon_energy_ev,
    reference_black_hole_sweep,
    tidal_acceleration_difference,
)


def test_gravitational_radius_positive():
    assert gravitational_radius(1.0) > 0


def test_compression_heats_with_negative_expansion():
    assert compressive_heating_rate(2.0, -3.0) == 6.0


def test_gravitothermal_classification():
    assert classify_gravitothermal(0.5) is Regime.INFALL_DOMINANT
    assert classify_gravitothermal(1.0) is Regime.TRANSITIONAL
    assert classify_gravitothermal(1.5) is Regime.EXPANSION_OUTFLOW


def test_transduction_ratio():
    assert magnetoelectric_transduction(2.0, 4.0) == pytest.approx(0.5)


def test_oscillator_quality():
    assert oscillator_quality_factor(10.0, 2.0) == pytest.approx(2.5)


def test_tidal_difference_scales_with_length():
    a = tidal_acceleration_difference(1e20, 1e6, 1.0)
    b = tidal_acceleration_difference(1e20, 1e6, 2.0)
    assert b == pytest.approx(2.0 * a)


def test_microwave_photon_below_bond_scale():
    energy = photon_energy_ev(2.45e9)
    assert energy < 1e-3
    assert classify_photon_channel(energy) == "collective_or_rotational_heating"


def test_gamma_pair_threshold_classification():
    assert classify_photon_channel(1.1e6).startswith("pair_production")


def test_electromagnetism_dominates_atomic_gravity():
    ratio = coulomb_to_gravity_force_ratio(-E_CHARGE, E_CHARGE, M_E, M_P)
    assert ratio > 1e39


def test_one_kg_steam_reference_is_about_1_7_m3():
    volume = ideal_gas_volume_m3(1.0, 0.01801528, 373.15, 101325.0)
    assert 1.6 < volume < 1.8


def test_reference_sweep_identifies_massive_disk():
    payload = reference_black_hole_sweep(10.0)
    assert payload["rows"][-1]["toomre_q_reference"] < 1.0
    assert payload["rows"][-1]["self_gravity_regime"] == "self_gravity_instability_candidate"


def test_reference_sweep_timescale_scales_with_mass():
    small = reference_black_hole_sweep(10.0)
    large = reference_black_hole_sweep(4.3e6)
    expected = 4.3e6 / 10.0
    assert large["orbital_period_s"] / small["orbital_period_s"] == pytest.approx(expected)


def test_recurrent_state_moves_in_expected_directions():
    state = CascadeState(1.0, 0.1, 0.0, 1.0)
    rates = CascadeRates(
        expansion_scalar=-0.2,
        pressure=1.0,
        photoionization_rate=0.1,
        impact_ionization_rate=0.1,
        field_ionization_rate=0.0,
        tidal_ionization_rate=0.0,
        recombination_rate=0.1,
        current_drive=2.0,
        current_relaxation_time=1.0,
        gravity_heating=0.1,
        electromagnetic_heating=0.1,
        radiation_heating=0.0,
        cooling=0.0,
        outflow_loss=0.0,
    )
    next_state = advance_cascade_state(state, rates, 0.1)
    assert next_state.density > state.density
    assert next_state.ionization_fraction > state.ionization_fraction
    assert next_state.current_density > state.current_density
    assert next_state.internal_energy_density > state.internal_energy_density


def test_state_rejects_invalid_ionization_fraction():
    with pytest.raises(ValueError):
        CascadeState(1.0, 1.1, 0.0, 1.0).validate()


def test_payload_preserves_claim_gate_and_token_vazio():
    payload = calibration_payload()
    assert payload["claim_allowed"] is False
    assert payload["raw_data_policy"] == "immutable"
    assert payload["TOKEN_VAZIO"]
    assert payload["recurrent_state_smoke_test"]["scope"].startswith("synthetic")


def test_orbital_speed_reference_is_subluminal_by_construction():
    sweep = reference_black_hole_sweep(10.0, radius_rg=20.0)
    omega = sweep["orbital_angular_frequency_rad_s"]
    speed = omega * sweep["radius_m"]
    assert speed < C
