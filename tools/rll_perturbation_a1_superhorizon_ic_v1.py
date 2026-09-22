#!/usr/bin/env python3
from __future__ import annotations

"""A1.3 component-local super-horizon IC series gate.

This verifies a regular power-series solution of the frozen A1.2 component
equations in the radiation-era reference limit. It is deliberately not a full
Einstein-Boltzmann initial-condition solver.
"""

import argparse
import json
import os
import sys
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any, Sequence

import numpy as np

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.rll_perturbation_a1_gauge_regularization_v1 import (
    ca2_from_background,
    q_log_one_plus_w,
)
from tools.rll_perturbation_a1_restframe_candidate_v1 import CASES, w_conserved

SCHEMA = "rll.perturbation_a1_superhorizon_ic_gate.v1"
Z_REFERENCE = 1.0e4

D0 = Fraction(-3, 2)
D2 = Fraction(-1, 28)
D4 = Fraction(1, 280)
V1 = Fraction(1, 2)
V3 = Fraction(-1, 28)
V5 = Fraction(1, 840)


def exact_recurrence_residuals() -> dict[str, Fraction]:
    return {
        "continuity_x^-1": -3 * D0 - 9 * V1,
        "momentum_x^0": V1 - (2 * V1 + D0 + 1),
        "continuity_x^1": 5 * D2 + V1 + 9 * V3,
        "momentum_x^2": V3 - D2,
        "continuity_x^3": 7 * D4 + V3 + 9 * V5,
        "momentum_x^4": 3 * V5 - D4,
    }


def delta_series(x: float, psi0: float = 1.0) -> float:
    return psi0 * (
        float(D0) + float(D2) * x * x + float(D4) * x**4
    )


def v_series(x: float, psi0: float = 1.0) -> float:
    return psi0 * (
        float(V1) * x + float(V3) * x**3 + float(V5) * x**5
    )


def first_omitted_continuity_residual(x: float, psi0: float = 1.0) -> float:
    # With the series truncated at d4/v5, all lower powers cancel exactly.
    return psi0 * float(V5) * x**5


def early_background_case(zt: float, wt: float) -> dict[str, Any]:
    z = np.array([Z_REFERENCE], dtype=float)
    w = float(w_conserved(z, zt, wt)[0])
    q = float(q_log_one_plus_w(z, zt, wt)[0])
    ca = float(ca2_from_background(z, zt, wt)[0])
    finite = bool(np.isfinite(w) and np.isfinite(q) and np.isfinite(ca))
    passed = finite and max(abs(w), abs(q), abs(ca)) <= 1.0e-12
    return {
        "zt": float(zt),
        "wt": float(wt),
        "z_reference": Z_REFERENCE,
        "w": w,
        "q_w": q,
        "ca2": ca,
        "pass": passed,
    }


def build() -> dict[str, Any]:
    residuals = exact_recurrence_residuals()
    exact_pass = all(value == 0 for value in residuals.values())
    background = [early_background_case(zt, wt) for zt, wt in CASES]
    background_pass = all(row["pass"] for row in background)

    # Conditional adiabatic consistency at leading order:
    # delta_gamma/Psi0 = -2 -> (3/4)delta_gamma/Psi0 = -3/2 = d0.
    adiabatic_leading_pass = D0 == Fraction(3, 4) * Fraction(-2, 1)

    x_probe = 1.0e-2
    truncation_residual = abs(first_omitted_continuity_residual(x_probe))
    truncation_pass = truncation_residual < 2.0e-13

    passed = exact_pass and background_pass and adiabatic_leading_pass and truncation_pass
    state = (
        "A1_3_COMPONENT_LOCAL_SUPERHORIZON_SERIES_PASS_COUPLED_IC_OPEN"
        if passed
        else "A1_3_COMPONENT_LOCAL_SUPERHORIZON_SERIES_FAIL"
    )
    return {
        "schema": SCHEMA,
        "state": state,
        "claim_allowed": False,
        "publication_ready": False,
        "parent": "A1_2_GAUGE_VARIABLE_REGULARIZATION_PASS_IC_OPEN",
        "reference_regime": {
            "x": "k*tau << 1",
            "conformal_H": "1/tau",
            "metric": "reduced component-local reference: Psi=Psi0 constant and Phi_prime=0 through retained order",
            "normalization": "Psi0 free",
        },
        "coefficients": {
            "d0": str(D0),
            "d2": str(D2),
            "d4": str(D4),
            "v1": str(V1),
            "v3": str(V3),
            "v5": str(V5),
        },
        "series": {
            "delta_over_Psi0": "-3/2 - x^2/28 + x^4/280 + O(x^6)",
            "U_over_kPsi0": "x/2 - x^3/28 + x^5/840 + O(x^7)",
        },
        "exact_recurrence_residuals": {k: str(v) for k, v in residuals.items()},
        "exact_recurrence_pass": exact_pass,
        "conditional_adiabatic_leading_pass": adiabatic_leading_pass,
        "background_cases": background,
        "passing_background_cases": sum(row["pass"] for row in background),
        "total_background_cases": len(background),
        "truncation_probe": {
            "x": x_probe,
            "continuity_first_omitted_abs_residual": truncation_residual,
            "threshold": 2.0e-13,
            "pass": truncation_pass,
        },
        "token_resolution": "NOT_RESOLVED",
        "class_camb_unlock": False,
        "hard_blockers": [
            "FULL_COUPLED_EINSTEIN_BOLTZMANN_INITIAL_CONDITIONS",
            "NEUTRINO_ANISOTROPIC_STRESS_CORRECTION",
            "PRIMORDIAL_NORMALIZATION",
            "CLASS_SYNCHRONOUS_GAUGE_MAP",
            "CAMB_VARIABLE_MAP",
            "PERTURBED_BIANCHI_CONSTRAINT_RESIDUAL",
            "FULL_SOLVER_CONVERGENCE",
        ],
        "next_gate": (
            "derive coupled radiation+neutrino metric series and independent "
            "CLASS/CAMB maps without changing the local A1.3 recurrence evidence"
        ),
        "scientific_boundary": (
            "PASS establishes only a regular component-local series in the declared frozen-potential "
            "reference regime. Higher-order coefficients may change in the fully coupled metric "
            "series; this is not a complete cosmological IC solution."
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
        "exact_recurrence_pass": payload["exact_recurrence_pass"],
        "passing_background_cases": payload["passing_background_cases"],
        "total_background_cases": payload["total_background_cases"],
        "token_resolution": payload["token_resolution"],
        "class_camb_unlock": payload["class_camb_unlock"],
    }, sort_keys=True))
    return 0 if payload["state"] == "A1_3_COMPONENT_LOCAL_SUPERHORIZON_SERIES_PASS_COUPLED_IC_OPEN" else 2


if __name__ == "__main__":
    raise SystemExit(main())
