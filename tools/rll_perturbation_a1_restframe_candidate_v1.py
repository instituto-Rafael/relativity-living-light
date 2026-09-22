#!/usr/bin/env python3
from __future__ import annotations

"""Bounded falsifiability gate for RLL perturbation candidate A1.1.

This does not implement full RLL perturbations. It evaluates only necessary
background/closure conditions for the explicitly versioned candidate:
- separately conserved effective fluid,
- c_s,rest^2 = 1 as a research-candidate assumption,
- Q_mu = 0,
- sigma_s = 0.

Gauge, full delta/theta evolution, super-horizon ICs and perturbative transition
regularity remain open and block CLASS/CAMB promotion.
"""

import argparse
import json
import math
import os
import tempfile
from pathlib import Path
from typing import Any, Sequence

import numpy as np

SCHEMA = "rll.perturbation_a1_restframe_gate.v1"
CASES = tuple(
    (zt, wt)
    for zt in (0.1, 1.0, 10.0)
    for wt in (0.05, 0.3, 2.0)
)
TOL = 1.0e-10
CS2_REST = 1.0


def transition_f(z: np.ndarray, zt: float, wt: float) -> np.ndarray:
    if wt <= 0.0:
        raise ValueError("wt must be positive")
    x = np.clip((np.asarray(z, dtype=float) - float(zt)) / float(wt), -700.0, 700.0)
    return 1.0 / (1.0 + np.exp(x))


def dfdlna(z: np.ndarray, zt: float, wt: float) -> np.ndarray:
    z = np.asarray(z, dtype=float)
    f = transition_f(z, zt, wt)
    return (1.0 + z) * f * (1.0 - f) / float(wt)


def rho_factor(z: np.ndarray, zt: float, wt: float) -> np.ndarray:
    z = np.asarray(z, dtype=float)
    f = transition_f(z, zt, wt)
    return f + (1.0 - f) * (1.0 + z) ** 3


def drho_factor_dlna(z: np.ndarray, zt: float, wt: float) -> np.ndarray:
    z = np.asarray(z, dtype=float)
    f = transition_f(z, zt, wt)
    return dfdlna(z, zt, wt) * (1.0 - (1.0 + z) ** 3) - 3.0 * (1.0 - f) * (1.0 + z) ** 3


def p_conserved_factor(z: np.ndarray, zt: float, wt: float) -> np.ndarray:
    rho = rho_factor(z, zt, wt)
    return -rho - drho_factor_dlna(z, zt, wt) / 3.0


def w_conserved(z: np.ndarray, zt: float, wt: float) -> np.ndarray:
    rho = rho_factor(z, zt, wt)
    return p_conserved_factor(z, zt, wt) / rho


def continuity_residual(z: np.ndarray, zt: float, wt: float) -> np.ndarray:
    rho = rho_factor(z, zt, wt)
    pressure = p_conserved_factor(z, zt, wt)
    return drho_factor_dlna(z, zt, wt) + 3.0 * (rho + pressure)


def z_grid() -> np.ndarray:
    low = np.linspace(0.0, 12.0, 2401)
    high = np.logspace(math.log10(12.01), 4.0, 1200)
    return np.concatenate([low, high])


def evaluate_case(zt: float, wt: float) -> dict[str, Any]:
    z = z_grid()
    rho = rho_factor(z, zt, wt)
    pressure = p_conserved_factor(z, zt, wt)
    w = pressure / rho
    residual = continuity_residual(z, zt, wt)

    finite = (
        np.isfinite(rho)
        & np.isfinite(pressure)
        & np.isfinite(w)
        & np.isfinite(residual)
    )

    max_abs_residual = float(np.max(np.abs(residual[finite]))) if np.any(finite) else math.inf
    min_rho = float(np.min(rho[finite])) if np.any(finite) else -math.inf
    min_one_plus_w = float(np.min(1.0 + w[finite])) if np.any(finite) else -math.inf
    max_abs_w = float(np.max(np.abs(w[finite]))) if np.any(finite) else math.inf

    gates = {
        "finite_everywhere": bool(np.all(finite)),
        "rho_positive": bool(np.all(rho > 0.0)),
        "continuity_closed": bool(max_abs_residual <= TOL),
        "canonical_kinetic_sign_necessary": bool(min_one_plus_w >= -TOL),
        "cs2_rest_bounded": bool(0.0 <= CS2_REST <= 1.0),
    }
    passed = all(gates.values())

    return {
        "zt": float(zt),
        "wt": float(wt),
        "pass": passed,
        "gates": gates,
        "rho_min": min_rho,
        "one_plus_w_min": min_one_plus_w,
        "max_abs_w": max_abs_w,
        "max_abs_continuity_residual": max_abs_residual,
        "cs2_rest": CS2_REST,
        "z_domain": [float(z[0]), float(z[-1])],
        "samples": int(z.size),
    }


def build() -> dict[str, Any]:
    cases = [evaluate_case(zt, wt) for zt, wt in CASES]
    necessary_pass = all(row["pass"] for row in cases)

    state = (
        "A1_1_NECESSARY_GATES_PASS_GAUGE_IC_OPEN"
        if necessary_pass
        else "A1_1_NECESSARY_GATES_FAIL"
    )

    return {
        "schema": SCHEMA,
        "state": state,
        "claim_allowed": False,
        "publication_ready": False,
        "candidate_id": "A1_1_CONSERVED_CS2REST_1_Q0_SIGMA0",
        "candidate_contract": "data/science/perturbations/RLL_PERTURBATION_A1_RESTFRAME_CS1_CANDIDATE_20260922_V1.json",
        "successor_contract": "data/science/perturbations/RLL_PERTURBATION_CLOSURE_SUCCESSOR_20260922_V2.json",
        "assumptions": {
            "separate_conservation": True,
            "cs2_rest": CS2_REST,
            "Q_mu": "0",
            "sigma_s": "0",
            "pressure": "p_cons=-rho_s-(1/3)d rho_s/dln(a)",
            "entropy": "nonadiabatic allowed; rest-frame delta_p = c_s_rest^2 delta_rho_rest",
        },
        "sweep": {
            "cases": cases,
            "passing_cases": sum(bool(row["pass"]) for row in cases),
            "total_cases": len(cases),
            "tolerance": TOL,
        },
        "resolved_slots": [],
        "candidate_assigned_slots": ["C03_CS2", "C04_ENTROPY", "C05_ANISOTROPIC_STRESS", "C06_Q_MU"],
        "hard_blockers": [
            "C01_DELTA_S_FULL_EVOLUTION",
            "C02_THETA_S_FULL_EVOLUTION",
            "C07_GAUGE_AND_INITIAL_CONDITIONS",
            "C08_PERTURBATION_TRANSITION_REGULARITY",
            "CONSTRAINT_BIANCHI_RESIDUAL",
        ],
        "token": "TOKEN_VAZIO_RLL_PERTURBATION_CLOSURE_RELATIONS",
        "token_resolution": "NOT_RESOLVED",
        "class_camb_unlock": False,
        "next_gate": (
            "derive and freeze C01/C02 in an explicit gauge, define super-horizon initial conditions, "
            "then run gauge-mapping, constraint/Bianchi and transition-regularity tests"
        ),
        "scientific_boundary": (
            "A necessary-gate PASS means only that the declared A1.1 assumptions are not rejected by "
            "this background/closure sweep. It is not a complete perturbation theory, not CLASS/CAMB "
            "validation, not observational support, and not evidence that c_s,rest^2=1 is a property of RLL."
        ),
    }


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False
    ) as handle:
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
    print(
        json.dumps(
            {
                "state": payload["state"],
                "passing_cases": payload["sweep"]["passing_cases"],
                "total_cases": payload["sweep"]["total_cases"],
                "token_resolution": payload["token_resolution"],
                "class_camb_unlock": payload["class_camb_unlock"],
                "claim_allowed": False,
            },
            sort_keys=True,
        )
    )
    return 0 if payload["state"] == "A1_1_NECESSARY_GATES_PASS_GAUGE_IC_OPEN" else 2


if __name__ == "__main__":
    raise SystemExit(main())
