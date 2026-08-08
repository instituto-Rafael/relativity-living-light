#!/usr/bin/env python3
from __future__ import annotations

"""Falsifiability test for the minimal background-derived RLL fluid closure.

This does NOT define the final RLL perturbation theory.  It asks a narrower
question: if the effective RLL background component is separately conserved,
barotropic/adiabatic, non-interacting (Q_mu=0), and shear-free, does the sound
speed implied by the versioned background remain finite and in [0,1] over the
declared transition box?  Failure rules out this minimal closure as a global
default; it does not rule out other non-adiabatic or interacting closures.
"""

import argparse
import json
import math
import os
import tempfile
from pathlib import Path
from typing import Any, Sequence

import numpy as np

SCHEMA = "rll.perturbation_barotropic_candidate.v1"


def transition_f(z: np.ndarray, zt: float, wt: float) -> np.ndarray:
    width = max(float(wt), 1.0e-12)
    x = np.clip((np.asarray(z, dtype=float) - float(zt)) / width, -700.0, 700.0)
    return 1.0 / (1.0 + np.exp(x))


def rho_factor(z: np.ndarray, zt: float, wt: float) -> np.ndarray:
    z = np.asarray(z, dtype=float)
    f = transition_f(z, zt, wt)
    return f + (1.0 - f) * (1.0 + z) ** 3


def w_effective(z: np.ndarray, zt: float, wt: float) -> np.ndarray:
    """Background w(z) implied by separate conservation of rho_s(z)."""
    z = np.asarray(z, dtype=float)
    f = transition_f(z, zt, wt)
    df_dz = -(f * (1.0 - f)) / max(float(wt), 1.0e-12)
    zp1 = 1.0 + z
    rho = f + (1.0 - f) * zp1**3
    drho_dz = df_dz * (1.0 - zp1**3) + 3.0 * (1.0 - f) * zp1**2
    return -1.0 + zp1 * drho_dz / (3.0 * rho)


def ca2_adiabatic(z: np.ndarray, zt: float, wt: float) -> tuple[np.ndarray, np.ndarray]:
    """Return c_a^2=dp/drho and a validity mask away from w=-1 singular form."""
    z = np.asarray(z, dtype=float)
    w = w_effective(z, zt, wt)
    dw_dz = np.gradient(w, z, edge_order=2)
    denom = 3.0 * (1.0 + w)
    valid = np.isfinite(w) & np.isfinite(dw_dz) & (np.abs(denom) > 1.0e-7)
    ca2 = np.full_like(w, np.nan)
    ca2[valid] = w[valid] + (1.0 + z[valid]) * dw_dz[valid] / denom[valid]
    return ca2, valid


def z_grid() -> np.ndarray:
    low = np.linspace(0.0, 12.0, 2401)
    high = np.logspace(math.log10(12.01), 4.0, 1200)
    return np.concatenate([low, high])


def evaluate_case(zt: float, wt: float) -> dict[str, Any]:
    z = z_grid()
    rho = rho_factor(z, zt, wt)
    w = w_effective(z, zt, wt)
    ca2, valid = ca2_adiabatic(z, zt, wt)
    finite = valid & np.isfinite(ca2) & np.isfinite(rho) & (rho > 0.0)
    if not np.any(finite):
        return {
            "zt": zt,
            "wt": wt,
            "pass": False,
            "reason": "no_finite_domain",
        }
    values = ca2[finite]
    stable_causal = (values >= 0.0) & (values <= 1.0)
    singular_fraction = float(1.0 - np.mean(valid))
    pass_case = bool(np.all(stable_causal) and singular_fraction == 0.0)
    first_bad = None
    bad_indices = np.flatnonzero(finite & ((ca2 < 0.0) | (ca2 > 1.0)))
    if bad_indices.size:
        i = int(bad_indices[0])
        first_bad = {"z": float(z[i]), "w": float(w[i]), "ca2": float(ca2[i])}
    return {
        "zt": float(zt),
        "wt": float(wt),
        "pass": pass_case,
        "rho_positive": bool(np.all(rho > 0.0)),
        "w_min": float(np.nanmin(w)),
        "w_max": float(np.nanmax(w)),
        "ca2_min": float(np.nanmin(values)),
        "ca2_max": float(np.nanmax(values)),
        "stable_causal_fraction": float(np.mean(stable_causal)),
        "singular_or_undefined_fraction": singular_fraction,
        "first_stability_or_causality_violation": first_bad,
    }


def build() -> dict[str, Any]:
    cases = [
        evaluate_case(zt, wt)
        for zt in (0.1, 1.0, 10.0)
        for wt in (0.05, 0.3, 2.0)
    ]
    all_pass = all(row["pass"] for row in cases)
    return {
        "schema": SCHEMA,
        "state": "CANDIDATE_SURVIVES_DECLARED_SWEEP" if all_pass else "FALSIFIED_AS_GLOBAL_DEFAULT",
        "claim_allowed": False,
        "publication_ready": False,
        "token": "TOKEN_VAZIO_RLL_PERTURBATION_CLOSURE_RELATIONS",
        "candidate": {
            "separate_conservation": True,
            "Q_mu": "0",
            "anisotropic_stress_sigma_s": "0",
            "pressure_closure": "barotropic_adiabatic",
            "rest_frame_sound_speed_policy": "c_s^2 = c_a^2 = dp_s/d rho_s derived from the versioned RLL background",
            "background_density_factor": "f(z) + (1-f(z))*(1+z)^3",
        },
        "sweep": {
            "zt": [0.1, 1.0, 10.0],
            "wt": [0.05, 0.3, 2.0],
            "z_domain": [0.0, 10000.0],
            "stability_causality_acceptance": "finite and 0 <= c_a^2 <= 1 at every evaluated point",
            "cases": cases,
        },
        "interpretation": (
            "This minimal barotropic/adiabatic, non-interacting, shear-free closure is not admissible as a global RLL default over the declared transition sweep. "
            "The background alone therefore does not determine a stable perturbation closure; a versioned non-adiabatic/rest-frame sound-speed and/or interaction prescription remains necessary."
            if not all_pass
            else
            "The candidate survived this numerical sweep only; gauge, initial-condition, conservation-residual and independent-solver gates remain open."
        ),
        "resolved_token": None,
        "reduces_token": "TOKEN_VAZIO_RLL_PERTURBATION_CLOSURE_RELATIONS",
        "next_required_decisions": [
            "choose and justify an independent rest-frame sound-speed/entropy prescription instead of silently setting c_s^2=c_a^2",
            "freeze gauge and super-horizon initial conditions",
            "freeze Q_mu and anisotropic-stress policies consistently at background and perturbation level",
            "rerun conservation, transition-regularity and gauge-mapping tests before CLASS/CAMB implementation",
        ],
        "scientific_boundary": "Negative evidence for one minimal closure candidate is not validation or falsification of the broader RLL background model.",
    }


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        tmp = Path(handle.name)
        json.dump(payload, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    try:
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    payload = build()
    atomic_json(args.output, payload)
    print(json.dumps({
        "state": payload["state"],
        "cases": len(payload["sweep"]["cases"]),
        "passing_cases": sum(bool(row["pass"]) for row in payload["sweep"]["cases"]),
        "claim_allowed": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
