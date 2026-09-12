"""Recombination and sound-horizon helpers for bounded successor paths.

This module is additive and non-claim-bearing. It does not replace the
historical CMB approximation until a dedicated successor likelihood is wired
and benchmarked.

SOURCE != ARTEFACT != EXECUTION != EVIDENCE != CLAIM.
"""

from __future__ import annotations

from collections.abc import Callable
import math

from rll.cosmology_radiation import (
    OMEGA_GAMMA_H2_REF,
    TCMB_REF_K,
    omega_gamma_h2,
)

C_KM_S = 299792.458


def _positive(name: str, value: float) -> float:
    value = float(value)
    if not math.isfinite(value) or value <= 0.0:
        raise ValueError(f"{name} must be finite and > 0")
    return value


def z_star_hu_sugiyama(omega_b_h2: float, omega_m_h2: float) -> float:
    """Approximate photon-decoupling redshift z_*.

    Uses the Hu-Sugiyama fitting form used in standard compressed-CMB
    calculations. It is an approximation and remains separately benchmarked
    from a recombination solver.
    """

    ob = _positive("omega_b_h2", omega_b_h2)
    om = _positive("omega_m_h2", omega_m_h2)
    g1 = 0.0783 * ob ** (-0.238) / (1.0 + 39.5 * ob ** 0.763)
    g2 = 0.560 / (1.0 + 21.1 * ob ** 1.81)
    return 1048.0 * (1.0 + 0.00124 * ob ** (-0.738)) * (1.0 + g1 * om ** g2)


def baryon_photon_ratio_R(
    a: float,
    omega_b_h2: float,
    tcmb_k: float = TCMB_REF_K,
) -> float:
    """Return R_b(a)=3 rho_b/(4 rho_gamma) for the tightly-coupled plasma."""

    a = _positive("a", a)
    ob = _positive("omega_b_h2", omega_b_h2)
    og = omega_gamma_h2(tcmb_k)
    return (3.0 * ob / (4.0 * og)) * a


def sound_speed_km_s(
    a: float,
    omega_b_h2: float,
    tcmb_k: float = TCMB_REF_K,
) -> float:
    """Photon-baryon sound speed c/sqrt(3(1+R_b))."""

    rb = baryon_photon_ratio_R(a, omega_b_h2, tcmb_k)
    return C_KM_S / math.sqrt(3.0 * (1.0 + rb))


def sound_horizon_mpc(
    *,
    z_star: float,
    h0_km_s_mpc: float,
    e_of_a: Callable[[float], float],
    omega_b_h2: float,
    tcmb_k: float = TCMB_REF_K,
    intervals: int = 4096,
    a_min: float = 1.0e-8,
) -> float:
    """Integrate the comoving sound horizon to a*=1/(1+z_star).

    r_s(a*) = integral[c_s(a)/(a^2 H0 E(a)) da].

    Simpson integration is deterministic and intentionally dependency-light.
    The supplied E(a) makes the background model explicit instead of silently
    assuming LCDM inside this function.
    """

    z_star = _positive("z_star", z_star)
    h0 = _positive("h0_km_s_mpc", h0_km_s_mpc)
    _positive("omega_b_h2", omega_b_h2)
    a0 = _positive("a_min", a_min)
    if intervals < 2 or intervals % 2 != 0:
        raise ValueError("intervals must be an even integer >= 2")

    a1 = 1.0 / (1.0 + z_star)
    if not a0 < a1:
        raise ValueError("a_min must be smaller than a_star")

    def f(a: float) -> float:
        e = float(e_of_a(a))
        if not math.isfinite(e) or e <= 0.0:
            raise ValueError("e_of_a(a) must be finite and > 0")
        cs = sound_speed_km_s(a, omega_b_h2, tcmb_k)
        return cs / (a * a * h0 * e)

    step = (a1 - a0) / intervals
    acc = f(a0) + f(a1)
    acc += 4.0 * sum(f(a0 + i * step) for i in range(1, intervals, 2))
    acc += 2.0 * sum(f(a0 + i * step) for i in range(2, intervals, 2))
    return acc * step / 3.0


def flat_lcdm_e_of_a(
    *,
    omega_m: float,
    omega_r: float,
) -> Callable[[float], float]:
    """Build a flat LCDM E(a) reference function for sanity benchmarks."""

    om = _positive("omega_m", omega_m)
    orad = _positive("omega_r", omega_r)
    ol = 1.0 - om - orad
    if ol <= 0.0:
        raise ValueError("flat closure requires positive Omega_Lambda")

    def e(a: float) -> float:
        a = _positive("a", a)
        return math.sqrt(orad / a**4 + om / a**3 + ol)

    return e


def reference_planck_like_sanity(
    *,
    h0_km_s_mpc: float = 67.4,
    omega_m: float = 0.315,
    omega_b_h2: float = 0.02237,
    omega_r: float,
) -> dict[str, float | str | bool]:
    """Return a bounded Planck-like sanity calculation.

    This is not a CLASS/CAMB benchmark and not an RLL claim.
    """

    h = _positive("h0_km_s_mpc", h0_km_s_mpc) / 100.0
    zstar = z_star_hu_sugiyama(omega_b_h2, omega_m * h * h)
    rs = sound_horizon_mpc(
        z_star=zstar,
        h0_km_s_mpc=h0_km_s_mpc,
        e_of_a=flat_lcdm_e_of_a(omega_m=omega_m, omega_r=omega_r),
        omega_b_h2=omega_b_h2,
    )
    return {
        "schema": "rll.cmb_reference_sanity.v1",
        "z_star_fit": zstar,
        "r_s_zstar_mpc": rs,
        "reference_r_s_zstar_mpc": 144.43,
        "class_camb_benchmark_complete": False,
        "claim_allowed": False,
        "status": "REFERENCE_SANITY_ONLY",
    }
