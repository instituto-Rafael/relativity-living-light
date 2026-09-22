#!/usr/bin/env python3
"""Executable physical-profile contract for canonical RLL Omega_B0/Omega_P0.

This module resolves the sign of B/P only for their canonical physical-density
interpretation. It deliberately does not supply missing PMF/plasma perturbation
microphysics or infer an observational prior from historical blueprint ranges.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "data/inputs/qcd_primordial/rll_bp_physical_contract.v1.json"


def load_contract() -> dict:
    payload = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if payload.get("claim_allowed") is not False:
        raise ValueError("B/P contract must remain claim_allowed=false")
    return payload


def magnetic_energy_density_si(B_tesla: float, mu0: float = 4.0e-7 * math.pi) -> float:
    if not math.isfinite(B_tesla) or not math.isfinite(mu0) or mu0 <= 0.0:
        raise ValueError("finite magnetic field and positive mu0 required")
    return B_tesla * B_tesla / (2.0 * mu0)


def w_from_density_scaling_exponent(n: float) -> float:
    """For separately conserved rho proportional to a^-n, n=3(1+w)."""
    if not math.isfinite(n):
        raise ValueError("finite scaling exponent required")
    return n / 3.0 - 1.0


def validate_physical_background(omega_B0: float, omega_P0: float) -> dict:
    for name, value in (("Omega_B0", omega_B0), ("Omega_P0", omega_P0)):
        if not math.isfinite(value):
            raise ValueError(f"{name} must be finite")
        if value < 0.0:
            raise ValueError(f"{name} cannot be negative in the physical energy-density profile")
    return {
        "schema": "rll.bp_physical_background.receipt.v1",
        "claim_allowed": False,
        "Omega_B0": float(omega_B0),
        "Omega_P0": float(omega_P0),
        "Omega_BP0": float(omega_B0 + omega_P0),
        "B_sign": "NONNEGATIVE_RESOLVED_PHYSICAL_PROFILE",
        "P_sign": "NONNEGATIVE_RESOLVED_PHYSICAL_PROFILE",
        "background_scaling": "a^-4",
        "implied_w_if_separately_conserved": w_from_density_scaling_exponent(4.0),
        "B_perturbations": "TOKEN_VAZIO_PMF_SPECTRUM_HELICITY_ANISOTROPIC_STRESS",
        "P_perturbations": "TOKEN_VAZIO_PLASMA_EOS_SOUND_SPEED_VISCOSITY_INTERACTIONS",
        "statistical_prior": "TOKEN_VAZIO_NO_AUTHORITATIVE_BP_PRIOR_FOUND",
        "full_physical_CMB_likelihood": "TOKEN_VAZIO",
        "publication_effect": "NONE",
    }


def omega_bp_h2(omega_B0: float, omega_P0: float, H0_km_s_Mpc: float) -> float:
    validate_physical_background(omega_B0, omega_P0)
    if not math.isfinite(H0_km_s_Mpc) or H0_km_s_Mpc <= 0.0:
        raise ValueError("H0 must be positive and finite")
    h = H0_km_s_Mpc / 100.0
    return (omega_B0 + omega_P0) * h * h


def delta_neff_background_equivalent(
    omega_B0: float,
    omega_P0: float,
    H0_km_s_Mpc: float,
    omega_gamma_h2: float,
) -> float:
    """Background-only mapping for positive independently redshifting radiation.

    rho_extra/rho_gamma = (7/8)(4/11)^(4/3) Delta N_eff.
    This is not a PMF/plasma perturbation likelihood.
    """
    if not math.isfinite(omega_gamma_h2) or omega_gamma_h2 <= 0.0:
        raise ValueError("omega_gamma_h2 must be positive and finite")
    factor = (7.0 / 8.0) * (4.0 / 11.0) ** (4.0 / 3.0)
    return omega_bp_h2(omega_B0, omega_P0, H0_km_s_Mpc) / (factor * omega_gamma_h2)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--omega-b0", type=float, required=True)
    parser.add_argument("--omega-p0", type=float, required=True)
    parser.add_argument("--H0", type=float, default=67.4)
    parser.add_argument("--omega-gamma-h2", type=float, default=2.4728e-5)
    args = parser.parse_args()
    receipt = validate_physical_background(args.omega_b0, args.omega_p0)
    receipt["omega_BP_h2"] = omega_bp_h2(args.omega_b0, args.omega_p0, args.H0)
    receipt["delta_Neff_background_equivalent"] = delta_neff_background_equivalent(
        args.omega_b0, args.omega_p0, args.H0, args.omega_gamma_h2
    )
    receipt["mapping_guard"] = "BACKGROUND_ONLY_NOT_PMF_OR_PLASMA_PERTURBATION_LIKELIHOOD"
    print(json.dumps(receipt, indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
