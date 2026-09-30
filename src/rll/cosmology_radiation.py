"""Early-universe radiation helpers for successor cosmology paths.

This module is additive. It does not change the legacy joint likelihood and does
not by itself validate the CMB acoustic-scale implementation.

Provenance:
- PDG astrophysical constants gives Omega_gamma h^2 =
  2.473e-5 * (T_CMB / 2.7255 K)^4.
- The relativistic-neutrino factor is derived from
  (7/8) * (4/11)^(4/3).
- A Standard-Model N_eff reference of 3.044 is used as an explicit default.

SOURCE != ARTEFACT != EXECUTION != EVIDENCE != CLAIM.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

TCMB_REF_K = 2.7255
OMEGA_GAMMA_H2_REF = 2.473e-5
NEFF_STANDARD = 3.044


def _require_positive(name: str, value: float) -> float:
    value = float(value)
    if not math.isfinite(value) or value <= 0.0:
        raise ValueError(f"{name} must be finite and > 0")
    return value


def _require_nonnegative(name: str, value: float) -> float:
    value = float(value)
    if not math.isfinite(value) or value < 0.0:
        raise ValueError(f"{name} must be finite and >= 0")
    return value


def relativistic_neutrino_factor() -> float:
    """Return rho_nu / (N_eff * rho_gamma) for relativistic neutrinos."""

    return (7.0 / 8.0) * (4.0 / 11.0) ** (4.0 / 3.0)


def omega_gamma_h2(tcmb_k: float = TCMB_REF_K) -> float:
    """Return the physical photon density Omega_gamma h^2."""

    tcmb_k = _require_positive("tcmb_k", tcmb_k)
    return OMEGA_GAMMA_H2_REF * (tcmb_k / TCMB_REF_K) ** 4


def omega_r_h2(
    tcmb_k: float = TCMB_REF_K,
    neff: float = NEFF_STANDARD,
) -> float:
    """Return physical total radiation density under a relativistic-N_eff model.

    This treats the N_eff contribution as relativistic. Massive-neutrino
    transition effects are outside this bounded helper.
    """

    neff = _require_nonnegative("neff", neff)
    photon = omega_gamma_h2(tcmb_k)
    return photon * (1.0 + relativistic_neutrino_factor() * neff)


def omega_r_from_h0(
    h0_km_s_mpc: float,
    tcmb_k: float = TCMB_REF_K,
    neff: float = NEFF_STANDARD,
) -> float:
    """Return Omega_r from H0, T_CMB and N_eff."""

    h0_km_s_mpc = _require_positive("h0_km_s_mpc", h0_km_s_mpc)
    h = h0_km_s_mpc / 100.0
    return omega_r_h2(tcmb_k=tcmb_k, neff=neff) / (h * h)


@dataclass(frozen=True)
class RadiationContract:
    h0_km_s_mpc: float
    tcmb_k: float = TCMB_REF_K
    neff: float = NEFF_STANDARD

    def as_dict(self) -> dict[str, float | str | bool]:
        photon_h2 = omega_gamma_h2(self.tcmb_k)
        radiation_h2 = omega_r_h2(self.tcmb_k, self.neff)
        radiation = omega_r_from_h0(self.h0_km_s_mpc, self.tcmb_k, self.neff)
        return {
            "schema": "rll.cosmology_radiation_contract.v1",
            "h0_km_s_mpc": float(self.h0_km_s_mpc),
            "tcmb_k": float(self.tcmb_k),
            "neff": float(self.neff),
            "omega_gamma_h2": photon_h2,
            "omega_r_h2": radiation_h2,
            "omega_r": radiation,
            "massive_neutrino_transition_modelled": False,
            "wired_into_joint_successor": False,
            "claim_allowed": False,
            "status": "IMPLEMENTED_HELPER_NOT_YET_BENCHMARKED_OR_WIRED",
        }
