from __future__ import annotations

import math

import pytest

from rll.cosmology_radiation import (
    NEFF_STANDARD,
    OMEGA_GAMMA_H2_REF,
    RadiationContract,
    omega_gamma_h2,
    omega_r_from_h0,
    omega_r_h2,
    relativistic_neutrino_factor,
)


def test_reference_photon_density_matches_contract() -> None:
    assert omega_gamma_h2() == OMEGA_GAMMA_H2_REF


def test_photon_density_scales_as_temperature_fourth_power() -> None:
    ratio = omega_gamma_h2(2.0 * 2.7255) / omega_gamma_h2(2.7255)
    assert math.isclose(ratio, 16.0, rel_tol=0.0, abs_tol=1e-12)


def test_relativistic_neutrino_factor_is_standard_thermal_ratio() -> None:
    assert math.isclose(relativistic_neutrino_factor(), 0.22710731766, rel_tol=0.0, abs_tol=1e-11)


def test_total_radiation_exceeds_photon_density() -> None:
    assert omega_r_h2(neff=NEFF_STANDARD) > omega_gamma_h2()


def test_reference_h0_yields_order_9e_minus_5_radiation_fraction() -> None:
    observed = omega_r_from_h0(67.4)
    assert 9.0e-5 < observed < 9.5e-5


def test_contract_is_explicitly_unwired_and_non_claim_bearing() -> None:
    report = RadiationContract(h0_km_s_mpc=67.4).as_dict()
    assert report["wired_into_joint_successor"] is False
    assert report["massive_neutrino_transition_modelled"] is False
    assert report["claim_allowed"] is False


@pytest.mark.parametrize(
    "fn,args",
    [
        (omega_gamma_h2, (0.0,)),
        (omega_r_h2, (2.7255, -1.0)),
        (omega_r_from_h0, (0.0,)),
    ],
)
def test_invalid_inputs_fail_closed(fn, args) -> None:
    with pytest.raises(ValueError):
        fn(*args)
