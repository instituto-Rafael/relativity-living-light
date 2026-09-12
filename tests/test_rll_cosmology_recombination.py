from __future__ import annotations

import math

import pytest

from rll.cosmology_radiation import omega_r_from_h0
from rll.cosmology_recombination import (
    C_KM_S,
    baryon_photon_ratio_R,
    reference_planck_like_sanity,
    sound_horizon_mpc,
    sound_speed_km_s,
    z_star_hu_sugiyama,
)


def test_hu_sugiyama_planck_like_zstar_is_near_expected_range() -> None:
    h = 0.674
    zstar = z_star_hu_sugiyama(0.02237, 0.315 * h * h)
    assert 1085.0 < zstar < 1098.0


def test_baryon_photon_ratio_scales_linearly_with_a() -> None:
    r1 = baryon_photon_ratio_R(1.0e-4, 0.02237)
    r2 = baryon_photon_ratio_R(2.0e-4, 0.02237)
    assert math.isclose(r2 / r1, 2.0, rel_tol=0.0, abs_tol=1e-12)


def test_sound_speed_is_positive_and_below_radiation_limit() -> None:
    cs = sound_speed_km_s(1.0 / 1090.0, 0.02237)
    assert 0.0 < cs < C_KM_S / math.sqrt(3.0)


def test_planck_like_reference_sound_horizon_is_close_to_pdg_reference() -> None:
    omega_r = omega_r_from_h0(67.4)
    report = reference_planck_like_sanity(omega_r=omega_r)
    assert report["claim_allowed"] is False
    assert report["class_camb_benchmark_complete"] is False
    assert abs(report["r_s_zstar_mpc"] - 144.43) < 0.6


def test_sound_horizon_rejects_invalid_integration_contract() -> None:
    with pytest.raises(ValueError):
        sound_horizon_mpc(
            z_star=1090.0,
            h0_km_s_mpc=67.4,
            e_of_a=lambda a: 1.0,
            omega_b_h2=0.02237,
            intervals=3,
        )


def test_sound_horizon_rejects_nonpositive_background() -> None:
    with pytest.raises(ValueError):
        sound_horizon_mpc(
            z_star=1090.0,
            h0_km_s_mpc=67.4,
            e_of_a=lambda a: 0.0,
            omega_b_h2=0.02237,
        )
