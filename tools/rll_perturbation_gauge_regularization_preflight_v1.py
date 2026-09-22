#!/usr/bin/env python3
from __future__ import annotations

"""Regular-variable preflight for RLL A1.1 perturbation candidate.

This gate does not derive or solve the full perturbation system.
It checks the background identities needed to justify using
(delta_rho_s, q_s=(rho_s+p_s) theta_s) as primary candidate variables
when 1+w_s becomes small.
"""

import argparse
import json
import math
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Sequence

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.rll_perturbation_a1_restframe_candidate_v1 import (
    CASES,
    TOL,
    drho_factor_dlna,
    p_conserved_factor,
    rho_factor,
    z_grid,
)

SCHEMA = "rll.perturbation_gauge_regularization_preflight.v1"
CROSSING_TOL = 1.0e-10
DEGENERACY_THRESHOLDS = (1.0e-8, 1.0e-12)


def normalized_identity_residual(
    enthalpy: np.ndarray,
    drho_dlna: np.ndarray,
) -> np.ndarray:
    residual = enthalpy + drho_dlna / 3.0
    scale = np.maximum(1.0, np.abs(enthalpy) + np.abs(drho_dlna) / 3.0)
    return np.abs(residual) / scale


def evaluate_case(zt: float, wt: float) -> dict[str, Any]:
    z = z_grid()
    rho = rho_factor(z, zt, wt)
    pressure = p_conserved_factor(z, zt, wt)
    drho = drho_factor_dlna(z, zt, wt)
    enthalpy = rho + pressure
    one_plus_w = enthalpy / rho
    identity = normalized_identity_residual(enthalpy, drho)

    theta_trial = np.sin(np.log1p(z + 1.0))
    q_trial = enthalpy * theta_trial

    conditioned = np.abs(one_plus_w) > DEGENERACY_THRESHOLDS[0]
    if np.any(conditioned):
        theta_reconstructed = q_trial[conditioned] / enthalpy[conditioned]
        roundtrip_error = float(
            np.max(np.abs(theta_reconstructed - theta_trial[conditioned]))
        )
    else:
        roundtrip_error = math.inf

    finite = (
        np.isfinite(rho)
        & np.isfinite(pressure)
        & np.isfinite(enthalpy)
        & np.isfinite(one_plus_w)
        & np.isfinite(q_trial)
        & np.isfinite(identity)
    )

    min_one_plus_w = float(np.min(one_plus_w[finite])) if np.any(finite) else -math.inf
    max_identity = float(np.max(identity[finite])) if np.any(finite) else math.inf

    degeneracy_counts = {
        f"abs_1_plus_w_le_{threshold:.0e}": int(
            np.sum(np.abs(one_plus_w) <= threshold)
        )
        for threshold in DEGENERACY_THRESHOLDS
    }

    gates = {
        "finite_background_and_regular_momentum": bool(np.all(finite)),
        "no_negative_crossing": bool(min_one_plus_w >= -CROSSING_TOL),
        "enthalpy_identity_closed": bool(max_identity <= TOL),
        "theta_roundtrip_where_conditioned": bool(roundtrip_error <= 1.0e-12),
        "no_epsilon_clipping_used": True,
    }

    return {
        "zt": float(zt),
        "wt": float(wt),
        "pass": all(gates.values()),
        "gates": gates,
        "one_plus_w_min": min_one_plus_w,
        "one_plus_w_max": float(np.max(one_plus_w[finite])) if np.any(finite) else math.inf,
        "enthalpy_min": float(np.min(enthalpy[finite])) if np.any(finite) else -math.inf,
        "enthalpy_max": float(np.max(enthalpy[finite])) if np.any(finite) else math.inf,
        "max_normalized_enthalpy_identity_residual": max_identity,
        "theta_roundtrip_max_abs_error_conditioned": roundtrip_error,
        "degeneracy_counts": degeneracy_counts,
        "samples": int(z.size),
    }


def build() -> dict[str, Any]:
    cases = [evaluate_case(zt, wt) for zt, wt in CASES]
    passed = all(row["pass"] for row in cases)
    observed_degeneracy = any(
        any(count > 0 for count in row["degeneracy_counts"].values())
        for row in cases
    )

    return {
        "schema": SCHEMA,
        "state": (
            "C07_C08_REGULAR_VARIABLE_PREFLIGHT_PASS_IC_EQUATIONS_OPEN"
            if passed
            else "C07_C08_REGULAR_VARIABLE_PREFLIGHT_FAIL"
        ),
        "claim_allowed": False,
        "publication_ready": False,
        "candidate_id": "A1_1_CONSERVED_CS2REST_1_Q0_SIGMA0",
        "contract": "data/science/perturbations/RLL_PERTURBATION_GAUGE_REGULARIZATION_CONTRACT_20260922_V1.json",
        "reference_gauge": "synchronous",
        "primary_candidate_variables": ["delta_rho_s", "q_s"],
        "q_definition": "q_s=(rho_s+p_s)*theta_s",
        "theta_policy": "derived diagnostic only where enthalpy is conditioned",
        "sweep": {
            "passing_cases": sum(bool(row["pass"]) for row in cases),
            "total_cases": len(cases),
            "observed_enthalpy_degeneracy": observed_degeneracy,
            "cases": cases,
        },
        "hard_blockers": [
            "C01_DELTA_RHO_EVOLUTION_IN_REFERENCE_GAUGE",
            "C02_Q_MOMENTUM_EVOLUTION_IN_REFERENCE_GAUGE",
            "C07_CLASS_CAMB_GAUGE_MAPPING",
            "C07_SUPERHORIZON_INITIAL_CONDITIONS",
            "C08_ANALYTIC_ENTHALPY_DEGENERACY_LIMIT",
            "C08_PERTURBED_BIANCHI_CONSTRAINT_RESIDUAL",
        ],
        "token_resolution": "NOT_RESOLVED",
        "class_camb_unlock": False,
        "next_gate": (
            "derive the full conservation equations directly in (delta_rho_s,q_s), "
            "prove the enthalpy-degenerate limit, then derive super-horizon IC and "
            "independent CLASS/CAMB mappings"
        ),
        "scientific_boundary": (
            "PASS verifies only regular-variable suitability at the background-identity "
            "and algebraic conditioning level. It does not define the missing dynamics, "
            "initial conditions, gauge mapping, perturbation stability, or observational validity."
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
    print(json.dumps({
        "state": payload["state"],
        "passing_cases": payload["sweep"]["passing_cases"],
        "total_cases": payload["sweep"]["total_cases"],
        "observed_enthalpy_degeneracy": payload["sweep"]["observed_enthalpy_degeneracy"],
        "token_resolution": payload["token_resolution"],
        "class_camb_unlock": payload["class_camb_unlock"],
        "claim_allowed": False,
    }, sort_keys=True))
    return 0 if payload["state"].endswith("_PASS_IC_EQUATIONS_OPEN") else 2


if __name__ == "__main__":
    raise SystemExit(main())
