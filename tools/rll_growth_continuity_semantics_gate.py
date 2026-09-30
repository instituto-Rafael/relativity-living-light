#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

SCHEMA = "rll.growth_continuity_semantics_gate.v1.report"


def logistic_f(z: float, zt: float, wt: float) -> float:
    if wt <= 0:
        raise ValueError("wt must be positive")
    x = (z - zt) / wt
    if x > 700:
        return 0.0
    if x < -700:
        return 1.0
    return 1.0 / (1.0 + math.exp(x))


def dfdlna(z: float, zt: float, wt: float) -> float:
    f = logistic_f(z, zt, wt)
    return (1.0 + z) * f * (1.0 - f) / wt


def rho_factor(z: float, zt: float, wt: float) -> float:
    f = logistic_f(z, zt, wt)
    a_inv3 = (1.0 + z) ** 3
    return f + (1.0 - f) * a_inv3


def drho_factor_dlna(z: float, zt: float, wt: float) -> float:
    f = logistic_f(z, zt, wt)
    fp = dfdlna(z, zt, wt)
    a_inv3 = (1.0 + z) ** 3
    return fp * (1.0 - a_inv3) - 3.0 * (1.0 - f) * a_inv3


def p_documented_factor(z: float, zt: float, wt: float) -> float:
    return -logistic_f(z, zt, wt)


def p_conserved_factor(z: float, zt: float, wt: float) -> float:
    r = rho_factor(z, zt, wt)
    dr = drho_factor_dlna(z, zt, wt)
    return -r - dr / 3.0


def continuity_residual(z: float, zt: float, wt: float, p_factor: float) -> float:
    r = rho_factor(z, zt, wt)
    dr = drho_factor_dlna(z, zt, wt)
    return dr + 3.0 * (r + p_factor)


def exact_documented_residual(z: float, zt: float, wt: float) -> float:
    a_inv3 = (1.0 + z) ** 3
    return dfdlna(z, zt, wt) * (1.0 - a_inv3)


def build_report() -> dict[str, Any]:
    cases = []
    for zt in (0.1, 1.0, 10.0):
        for wt in (0.05, 0.3, 2.0):
            points = sorted({0.0, zt, max(2.0 * zt, 0.2), 10.0})
            rows = []
            for z in points:
                doc = continuity_residual(z, zt, wt, p_documented_factor(z, zt, wt))
                exact = exact_documented_residual(z, zt, wt)
                cons = continuity_residual(z, zt, wt, p_conserved_factor(z, zt, wt))
                rows.append({
                    "z": z,
                    "documented_residual": doc,
                    "exact_formula_residual": exact,
                    "documented_formula_match": math.isclose(doc, exact, rel_tol=1e-10, abs_tol=1e-10),
                    "conserved_candidate_residual": cons,
                    "conserved_candidate_closes": math.isclose(cons, 0.0, rel_tol=0.0, abs_tol=1e-10),
                })
            cases.append({"zt": zt, "wt": wt, "points": rows})

    formula_match = all(
        row["documented_formula_match"]
        for case in cases
        for row in case["points"]
    )
    conserved_closes = all(
        row["conserved_candidate_closes"]
        for case in cases
        for row in case["points"]
    )
    transition_failure_observed = any(
        abs(row["documented_residual"]) > 1e-8
        for case in cases
        for row in case["points"]
        if row["z"] > 0.0
    )

    return {
        "schema": SCHEMA,
        "claim_allowed": False,
        "state": "BLOCKED_UNRESOLVED_PHYSICAL_SEMANTICS",
        "documented_pair_separate_conservation": "FAIL" if transition_failure_observed else "NOT_FALSIFIED",
        "exact_residual_formula_reproduced": formula_match,
        "conserved_candidate_algebraic_closure": "MATH_PASS" if conserved_closes else "FAIL",
        "physical_semantics_selected": False,
        "growth_cs2_state": "BLOCKED_BY_CONTINUITY_SEMANTICS",
        "cases": cases,
        "boundary": (
            "The conserved pressure formula is an algebraic consequence of imposing separate conservation on the versioned density. "
            "This tool does not select that semantics, does not define a physical rest-frame sound speed, and does not validate RLL perturbations."
        ),
        "next": "select one physical semantics route, version it, test conservation/regularity, then instantiate GROWTH-CS2-001",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--require-blocked", action="store_true")
    args = parser.parse_args()

    report = build_report()
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "state": report["state"],
        "documented_pair_separate_conservation": report["documented_pair_separate_conservation"],
        "exact_residual_formula_reproduced": report["exact_residual_formula_reproduced"],
        "conserved_candidate_algebraic_closure": report["conserved_candidate_algebraic_closure"],
        "growth_cs2_state": report["growth_cs2_state"],
        "claim_allowed": False,
    }, sort_keys=True))
    if args.require_blocked and report["state"] != "BLOCKED_UNRESOLVED_PHYSICAL_SEMANTICS":
        return 1
    if not report["exact_residual_formula_reproduced"]:
        return 1
    if report["documented_pair_separate_conservation"] != "FAIL":
        return 1
    if report["conserved_candidate_algebraic_closure"] != "MATH_PASS":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
