#!/usr/bin/env python3
from __future__ import annotations

"""A1.2 gauge-variable regularity diagnostic for the RLL perturbation candidate."""

import argparse
import json
import math
import os
import tempfile
import sys
from pathlib import Path
from typing import Any, Sequence

import numpy as np

if __package__ in {None, ""}:
    # Direct CLI execution sets sys.path[0] to tools/. Add the repository root
    # so the same canonical tools.* import works in both CLI and pytest/module modes.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.rll_perturbation_a1_restframe_candidate_v1 import (
    CASES,
    CS2_REST,
    TOL,
    dfdlna,
    drho_factor_dlna,
    rho_factor,
    transition_f,
    w_conserved,
    z_grid,
)

SCHEMA = "rll.perturbation_a1_gauge_regularity_gate.v1"
ACTIVE_FLOOR = 1.0e-12


def d2fdlna2(z: np.ndarray, zt: float, wt: float) -> np.ndarray:
    z = np.asarray(z, dtype=float)
    f = transition_f(z, zt, wt)
    g = dfdlna(z, zt, wt)
    return g * (-1.0 + (1.0 + z) * (1.0 - 2.0 * f) / float(wt))


def d2rho_factor_dlna2(z: np.ndarray, zt: float, wt: float) -> np.ndarray:
    z = np.asarray(z, dtype=float)
    f = transition_f(z, zt, wt)
    g = dfdlna(z, zt, wt)
    dg = d2fdlna2(z, zt, wt)
    a3inv = (1.0 + z) ** 3
    return dg * (1.0 - a3inv) + 6.0 * g * a3inv + 9.0 * (1.0 - f) * a3inv


def q_log_one_plus_w(z: np.ndarray, zt: float, wt: float) -> np.ndarray:
    rho = rho_factor(z, zt, wt)
    drho = drho_factor_dlna(z, zt, wt)
    d2rho = d2rho_factor_dlna2(z, zt, wt)
    return d2rho / drho - drho / rho


def ca2_from_background(z: np.ndarray, zt: float, wt: float) -> np.ndarray:
    w = w_conserved(z, zt, wt)
    return w - q_log_one_plus_w(z, zt, wt) / 3.0


def regularized_u_coefficient(z: np.ndarray, zt: float, wt: float) -> np.ndarray:
    q = q_log_one_plus_w(z, zt, wt)
    return q - (1.0 - 3.0 * CS2_REST)


def stiffness(max_abs_q: float) -> str:
    if max_abs_q <= 10.0:
        return "LOW"
    if max_abs_q <= 50.0:
        return "MODERATE"
    return "HIGH"


def algebraic_equivalence_probe(
    w: float,
    q: float,
    ca2: float,
    *,
    H: float = 0.73,
    k: float = 0.19,
    delta: float = 0.023,
    theta: float = -0.017,
    phi_prime: float = 0.004,
    psi: float = -0.006,
) -> dict[str, float | bool]:
    one = 1.0 + w
    if one <= ACTIVE_FLOOR:
        raise ValueError("equivalence probe requires active 1+w")
    U = one * theta

    delta_theta = (
        -one * (theta - 3.0 * phi_prime)
        - 3.0 * H * (CS2_REST - w) * delta
        - 9.0 * H * H * one * (CS2_REST - ca2) * theta / (k * k)
    )
    delta_u = (
        -U
        + 3.0 * one * phi_prime
        - 3.0 * H * (CS2_REST - w) * delta
        - 9.0 * H * H * (CS2_REST - ca2) * U / (k * k)
    )

    theta_prime = (
        -H * (1.0 - 3.0 * CS2_REST) * theta
        + CS2_REST * k * k * delta / one
        + k * k * psi
    )
    w_prime = H * one * q
    u_from_theta = one * theta_prime + w_prime * theta
    u_direct = (
        H * (q - (1.0 - 3.0 * CS2_REST)) * U
        + CS2_REST * k * k * delta
        + one * k * k * psi
    )

    scale_d = max(1.0, abs(delta_theta), abs(delta_u))
    scale_u = max(1.0, abs(u_from_theta), abs(u_direct))
    return {
        "delta_theta_form": delta_theta,
        "delta_u_form": delta_u,
        "u_from_theta": u_from_theta,
        "u_direct": u_direct,
        "delta_equivalent": abs(delta_theta - delta_u) <= 1.0e-12 * scale_d,
        "u_equivalent": abs(u_from_theta - u_direct) <= 1.0e-12 * scale_u,
    }


def evaluate_case(zt: float, wt: float) -> dict[str, Any]:
    z = z_grid()
    w = w_conserved(z, zt, wt)
    one = 1.0 + w
    drho = drho_factor_dlna(z, zt, wt)
    active = (
        np.isfinite(one)
        & (one > ACTIVE_FLOOR)
        & np.isfinite(drho)
        & (np.abs(drho) > np.finfo(float).tiny)
    )

    no_crossing = bool(np.nanmin(one) >= -TOL)
    active_count = int(np.count_nonzero(active))
    asymptotic_count = int(z.size - active_count)

    if active_count:
        q = q_log_one_plus_w(z[active], zt, wt)
        ca = ca2_from_background(z[active], zt, wt)
        coeff = regularized_u_coefficient(z[active], zt, wt)
        finite_coefficients = bool(
            np.all(np.isfinite(q))
            and np.all(np.isfinite(ca))
            and np.all(np.isfinite(coeff))
        )
        max_q = float(np.max(np.abs(q)))
        max_ca = float(np.max(np.abs(ca)))
        max_coeff = float(np.max(np.abs(coeff)))

        mid = active_count // 2
        eq = algebraic_equivalence_probe(
            float(w[active][mid]),
            float(q[mid]),
            float(ca[mid]),
        )
    else:
        finite_coefficients = False
        max_q = max_ca = max_coeff = math.inf
        eq = {"delta_equivalent": False, "u_equivalent": False}

    passed = (
        no_crossing
        and active_count > 0
        and finite_coefficients
        and bool(eq["delta_equivalent"])
        and bool(eq["u_equivalent"])
    )
    return {
        "zt": float(zt),
        "wt": float(wt),
        "pass": passed,
        "one_plus_w_min": float(np.nanmin(one)),
        "active_floor": ACTIVE_FLOOR,
        "active_points": active_count,
        "asymptotic_points": asymptotic_count,
        "finite_active_coefficients": finite_coefficients,
        "max_abs_q_w": max_q,
        "max_abs_ca2": max_ca,
        "max_abs_u_coefficient": max_coeff,
        "stiffness": stiffness(max_q),
        "equivalence_probe": eq,
    }


def build() -> dict[str, Any]:
    cases = [evaluate_case(zt, wt) for zt, wt in CASES]
    all_pass = all(row["pass"] for row in cases)
    return {
        "schema": SCHEMA,
        "state": (
            "A1_2_GAUGE_VARIABLE_REGULARIZATION_PASS_IC_OPEN"
            if all_pass
            else "A1_2_GAUGE_VARIABLE_REGULARIZATION_FAIL"
        ),
        "claim_allowed": False,
        "publication_ready": False,
        "parent_candidate": "A1_1_CONSERVED_CS2REST_1_Q0_SIGMA0",
        "gauge": "conformal_newtonian_reference",
        "regularized_variable": "U_s=(1+w_s)theta_s",
        "rest_frame_cs2": CS2_REST,
        "cases": cases,
        "passing_cases": sum(bool(row["pass"]) for row in cases),
        "total_cases": len(cases),
        "stiffness_counts": {
            label: sum(row["stiffness"] == label for row in cases)
            for label in ("LOW", "MODERATE", "HIGH")
        },
        "token_resolution": "NOT_RESOLVED",
        "class_camb_unlock": False,
        "hard_blockers": [
            "SUPER_HORIZON_INITIAL_CONDITIONS",
            "CLASS_GAUGE_VARIABLE_MAP",
            "CAMB_GAUGE_VARIABLE_MAP",
            "PERTURBED_BIANCHI_CONSTRAINT_RESIDUAL",
            "FULL_SOLVER_CONVERGENCE",
        ],
        "next_gate": (
            "derive super-horizon initial conditions in the frozen convention and "
            "independent CLASS/CAMB variable maps; preserve stiffness diagnostics"
        ),
        "scientific_boundary": (
            "PASS validates algebraic equivalence and coefficient finiteness only on the "
            "declared sweep/active region. It does not prove physical stability, correct ICs, "
            "solver convergence or observational validity."
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
        "passing_cases": payload["passing_cases"],
        "total_cases": payload["total_cases"],
        "stiffness_counts": payload["stiffness_counts"],
        "token_resolution": payload["token_resolution"],
        "class_camb_unlock": payload["class_camb_unlock"],
    }, sort_keys=True))
    return 0 if payload["state"] == "A1_2_GAUGE_VARIABLE_REGULARIZATION_PASS_IC_OPEN" else 2


if __name__ == "__main__":
    raise SystemExit(main())
