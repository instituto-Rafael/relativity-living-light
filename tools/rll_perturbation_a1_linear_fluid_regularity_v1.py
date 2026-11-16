#!/usr/bin/env python3
"""Numerical regularity audit for the A1.1 standard-fluid perturbation form.

The A1.1 background candidate is evaluated twice:
1) with the legacy/direct logistic representation that forms (1-f) by subtraction;
2) with a cancellation-resistant logistic representation.

No hidden epsilon is inserted into 1+w.  This tool therefore distinguishes a
physical/sign failure from a floating-point representation failure and blocks
CLASS/CAMB handoff when the direct C02 term 1/(1+w) is not numerically credible.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

from rx.kernel import dump_json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts/science/perturbations/RLL_A1_LINEAR_FLUID_REGULARITY_RECEIPT.json"
CASES = tuple((zt, wt) for zt in (0.1, 1.0, 10.0) for wt in (0.05, 0.3, 2.0))
MACHINE_EPSILON = 2.220446049250313e-16


def _logistic_pair_stable(z: float, zt: float, wt: float) -> tuple[float, float]:
    x = (float(z) - float(zt)) / float(wt)
    if x >= 0.0:
        e = math.exp(-x) if x < 746.0 else 0.0
        f = e / (1.0 + e)
        one_minus_f = 1.0 / (1.0 + e)
    else:
        e = math.exp(x) if x > -746.0 else 0.0
        f = 1.0 / (1.0 + e)
        one_minus_f = e / (1.0 + e)
    return f, one_minus_f


def _logistic_naive(z: float, zt: float, wt: float) -> float:
    x = max(-700.0, min(700.0, (float(z) - float(zt)) / float(wt)))
    return 1.0 / (1.0 + math.exp(x))


def _one_plus_w(z: float, zt: float, wt: float, *, stable: bool) -> float:
    if stable:
        f, one_minus_f = _logistic_pair_stable(z, zt, wt)
    else:
        f = _logistic_naive(z, zt, wt)
        one_minus_f = 1.0 - f

    zp1 = 1.0 + float(z)
    cube = zp1 * zp1 * zp1
    rho = f + one_minus_f * cube
    dfdlna = zp1 * f * one_minus_f / float(wt)
    drho_dlna = dfdlna * (1.0 - cube) - 3.0 * one_minus_f * cube
    return -drho_dlna / (3.0 * rho)


def _z_grid() -> list[float]:
    low = [12.0 * i / 2400.0 for i in range(2401)]
    lo = math.log10(12.01)
    hi = 4.0
    high = [10.0 ** (lo + (hi - lo) * i / 1199.0) for i in range(1200)]
    return low + high


def evaluate_case(zt: float, wt: float) -> dict[str, Any]:
    min_stable = math.inf
    min_z = None
    naive_zero_count = 0
    sign_fail_count = 0
    below_unit_roundoff_count = 0
    max_inverse = 0.0

    for z in _z_grid():
        stable = _one_plus_w(z, zt, wt, stable=True)
        naive = _one_plus_w(z, zt, wt, stable=False)

        if stable < min_stable:
            min_stable = stable
            min_z = z
        if stable <= 0.0 or not math.isfinite(stable):
            sign_fail_count += 1
        else:
            inverse = 1.0 / stable
            if math.isfinite(inverse):
                max_inverse = max(max_inverse, inverse)
            else:
                max_inverse = math.inf
            if stable < MACHINE_EPSILON:
                below_unit_roundoff_count += 1

        if naive == 0.0 and stable > 0.0:
            naive_zero_count += 1

    direct_form_representable = sign_fail_count == 0 and naive_zero_count == 0
    state = (
        "PASS_DIRECT_STANDARD_FLUID_REPRESENTATION"
        if direct_form_representable
        else "BLOCKED_DIRECT_STANDARD_FLUID_REPRESENTATION"
    )

    return {
        "zt": zt,
        "wt": wt,
        "state": state,
        "min_stable_1_plus_w": min_stable,
        "min_at_z": min_z,
        "max_abs_inverse_1_plus_w": max_inverse,
        "naive_subtraction_zero_count": naive_zero_count,
        "stable_sign_or_finite_fail_count": sign_fail_count,
        "below_unit_roundoff_count": below_unit_roundoff_count,
        "machine_epsilon": MACHINE_EPSILON,
    }


def build() -> dict[str, Any]:
    cases = [evaluate_case(zt, wt) for zt, wt in CASES]
    blocked = [row for row in cases if row["state"].startswith("BLOCKED")]
    extreme = [row for row in cases if row["below_unit_roundoff_count"] > 0]

    state = (
        "BLOCKED_DIRECT_STANDARD_FLUID_DOUBLE_PRECISION_REGULARITY"
        if blocked
        else "PASS_REPRESENTATION_ONLY_CONDITIONING_REMAINS_DIAGNOSTIC"
    )

    return {
        "schema": "rll.perturbation_a1_linear_fluid_regularity.v1",
        "candidate_id": "A1_1_CONSERVED_CS2REST_1_Q0_SIGMA0",
        "equation_contract": "data/science/perturbations/RLL_PERTURBATION_A1_LINEAR_FLUID_EQUATION_FAMILY_20260924_V1.json",
        "state": state,
        "cases": cases,
        "blocked_case_count": len(blocked),
        "below_unit_roundoff_case_count": len(extreme),
        "class_camb_unlock": False,
        "c08_resolution": "NOT_RESOLVED",
        "token_resolution": "NOT_RESOLVED",
        "claim_allowed": False,
        "interpretation": (
            "The standard-fluid equation family contains 1/(1+w). The audit inserts no hidden epsilon. "
            "A blocked case means the current direct double-precision background representation loses "
            "the small positive 1+w needed by the momentum equation. It blocks naive solver handoff, "
            "not every mathematically equivalent stable representation or PPF alternative."
        ),
        "F_ok": [
            "stable logistic evaluation preserves positive 1+w where direct subtraction can lose it",
            "conditioning is measured over the already preregistered 9-case A1.1 sweep",
            "no perturbative observable or solver is promoted"
        ],
        "F_gap": [
            "freeze a numerically stable representation or a justified PPF/regularized route",
            "C07 gauge and model-consistent super-horizon initial conditions",
            "constraint/Bianchi residual gate",
            "independent CLASS and CAMB implementations"
        ],
        "F_next": "treat the regularity result as a C08 input; do not implement CLASS/CAMB until a stable solver-neutral equation/IC contract passes",
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--output", type=Path, default=OUT)
    args = parser.parse_args(argv)
    payload = build()
    output = args.output if args.output.is_absolute() else ROOT / args.output
    if args.write:
        dump_json(output, payload)
    print(json.dumps({
        "state": payload["state"],
        "blocked_case_count": payload["blocked_case_count"],
        "below_unit_roundoff_case_count": payload["below_unit_roundoff_case_count"],
        "class_camb_unlock": False,
        "claim_allowed": False,
    }, indent=2))
    if args.write:
        print("wrote", output.relative_to(ROOT) if output.is_relative_to(ROOT) else output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
