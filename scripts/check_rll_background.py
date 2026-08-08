#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def exp_clip(x: float) -> float:
    return math.exp(max(-700.0, min(700.0, x)))


def f_transition(z: float, zt: float, wt: float) -> float:
    if wt <= 0:
        raise ValueError("wt must be positive")
    return 1.0 / (1.0 + exp_clip((z - zt) / wt))


def df_dlna(z: float, zt: float, wt: float) -> float:
    """Exact df/dln(a) for a=(1+z)^-1."""
    f = f_transition(z, zt, wt)
    return f * (1.0 - f) * (1.0 + z) / wt


def rho_factor(z: float, zt: float, wt: float) -> float:
    f = f_transition(z, zt, wt)
    return f + (1.0 - f) * (1.0 + z) ** 3


def drho_factor_dlna(z: float, zt: float, wt: float) -> float:
    """d/dln(a) of R=f+(1-f)a^-3, with a=(1+z)^-1."""
    a = 1.0 / (1.0 + z)
    a_m3 = a ** -3
    f = f_transition(z, zt, wt)
    fp = df_dlna(z, zt, wt)
    return fp * (1.0 - a_m3) - 3.0 * (1.0 - f) * a_m3


def e2(z: float, om: float, os0: float, zt: float, wt: float) -> float:
    ol = 1.0 - om - os0
    return om * (1.0 + z) ** 3 + ol + os0 * rho_factor(z, zt, wt)


def w_eff(z: float, zt: float, wt: float) -> float:
    """Documented p/rho ratio for p/(Omega_s0 rho_c0)=-f.

    This is an algebraic ratio. It is not a separately-conserved-fluid closure
    while f varies; see continuity_residual_documented().
    """
    return -f_transition(z, zt, wt) / rho_factor(z, zt, wt)


def pressure_conserved_factor(z: float, zt: float, wt: float) -> float:
    """Pressure/(Omega_s0 rho_c0) required by separate FLRW conservation."""
    rf = rho_factor(z, zt, wt)
    drf = drho_factor_dlna(z, zt, wt)
    return -rf - drf / 3.0


def w_conserved(z: float, zt: float, wt: float) -> float:
    """Equation of state implied by rho_s(a) if the RLL sector conserves separately."""
    return pressure_conserved_factor(z, zt, wt) / rho_factor(z, zt, wt)


def continuity_residual_documented(z: float, zt: float, wt: float) -> float:
    """Dimensionless residual C/[Omega_s0 rho_c0] for documented p=-f.

    C = d rho/dln(a) + 3(rho+p).
    Exact symbolic form: df/dln(a) * (1-a^-3).
    """
    rf = rho_factor(z, zt, wt)
    drf = drho_factor_dlna(z, zt, wt)
    p_factor = -f_transition(z, zt, wt)
    return drf + 3.0 * (rf + p_factor)


def continuity_residual_conserved(z: float, zt: float, wt: float) -> float:
    """Numerical identity check for the pressure reconstructed from continuity."""
    rf = rho_factor(z, zt, wt)
    drf = drho_factor_dlna(z, zt, wt)
    p_factor = pressure_conserved_factor(z, zt, wt)
    return drf + 3.0 * (rf + p_factor)


def omega_s(z: float, om: float, os0: float, zt: float, wt: float) -> float:
    return os0 * rho_factor(z, zt, wt) / e2(z, om, os0, zt, wt)


def kinetic_gate(z: float, om: float, os0: float, zt: float, wt: float) -> float:
    """Legacy/documented kinetic proxy using w_eff=p_documented/rho."""
    return (1.0 + w_eff(z, zt, wt)) * omega_s(z, om, os0, zt, wt)


def kinetic_gate_conserved(z: float, om: float, os0: float, zt: float, wt: float) -> float:
    """Canonical kinetic gate after imposing separate conservation on rho_s(a)."""
    return (1.0 + w_conserved(z, zt, wt)) * omega_s(z, om, os0, zt, wt)


def grid(a: float, b: float, n: int) -> list[float]:
    if n < 2:
        return [a]
    h = (b - a) / (n - 1)
    return [a + i * h for i in range(n)]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--omega-m", type=float, default=0.315)
    ap.add_argument("--omega-s0", type=float, default=0.059)
    ap.add_argument("--zt", type=float, default=1.164)
    ap.add_argument("--wt", type=float, default=0.405)
    ap.add_argument("--z-max", type=float, default=5.0)
    ap.add_argument("--n", type=int, default=501)
    ap.add_argument("--continuity-tol", type=float, default=1.0e-10)
    ap.add_argument("--out-json", default="results/rll_background_check.json")
    args = ap.parse_args()
    zs = grid(0.0, args.z_max, args.n)
    rows = [
        {
            "z": z,
            "f": f_transition(z, args.zt, args.wt),
            "w_documented": w_eff(z, args.zt, args.wt),
            "w_conserved": w_conserved(z, args.zt, args.wt),
            "omega_s": omega_s(z, args.omega_m, args.omega_s0, args.zt, args.wt),
            "kinetic_gate_documented": kinetic_gate(
                z, args.omega_m, args.omega_s0, args.zt, args.wt
            ),
            "kinetic_gate_conserved": kinetic_gate_conserved(
                z, args.omega_m, args.omega_s0, args.zt, args.wt
            ),
            "continuity_residual_documented": continuity_residual_documented(
                z, args.zt, args.wt
            ),
            "continuity_residual_conserved": continuity_residual_conserved(
                z, args.zt, args.wt
            ),
            "cs2_proxy": f_transition(z, args.zt, args.wt),
        }
        for z in zs
    ]
    summary = {
        "params": vars(args),
        "semantics": {
            "w_documented": "p_documented/rho; not a separately conserved closure while f varies",
            "w_conserved": "equation of state implied by rho_s(a) under separate FLRW conservation",
            "cs2_proxy": "bounded diagnostic only; canonical scalar rest-frame cs2 is 1",
        },
        "ranges": {
            "f": [min(r["f"] for r in rows), max(r["f"] for r in rows)],
            "w_documented": [
                min(r["w_documented"] for r in rows),
                max(r["w_documented"] for r in rows),
            ],
            "w_conserved": [
                min(r["w_conserved"] for r in rows),
                max(r["w_conserved"] for r in rows),
            ],
            "kinetic_gate_documented": [
                min(r["kinetic_gate_documented"] for r in rows),
                max(r["kinetic_gate_documented"] for r in rows),
            ],
            "kinetic_gate_conserved": [
                min(r["kinetic_gate_conserved"] for r in rows),
                max(r["kinetic_gate_conserved"] for r in rows),
            ],
            "continuity_residual_documented": [
                min(r["continuity_residual_documented"] for r in rows),
                max(r["continuity_residual_documented"] for r in rows),
            ],
            "continuity_residual_conserved": [
                min(r["continuity_residual_conserved"] for r in rows),
                max(r["continuity_residual_conserved"] for r in rows),
            ],
            "cs2_proxy": [
                min(r["cs2_proxy"] for r in rows),
                max(r["cs2_proxy"] for r in rows),
            ],
        },
        "checks": {
            "documented_continuity_closed": all(
                abs(r["continuity_residual_documented"]) <= args.continuity_tol
                for r in rows
            ),
            "conserved_reconstruction_continuity_closed": all(
                abs(r["continuity_residual_conserved"]) <= args.continuity_tol
                for r in rows
            ),
            "kinetic_gate_documented_non_negative": all(
                r["kinetic_gate_documented"] >= -1e-10 for r in rows
            ),
            "kinetic_gate_conserved_non_negative": all(
                r["kinetic_gate_conserved"] >= -1e-10 for r in rows
            ),
            "w_documented_above_minus_one": all(
                r["w_documented"] >= -1.0 - 1e-10 for r in rows
            ),
            "w_conserved_above_minus_one": all(
                r["w_conserved"] >= -1.0 - 1e-10 for r in rows
            ),
            "cs2_proxy_bounded": all(
                -1e-10 <= r["cs2_proxy"] <= 1.0 + 1e-10 for r in rows
            ),
            "linear_growth_background_response": "AVAILABLE_SEPARATE_SOLVER",
            "exact_rll_perturbations": "TOKEN_VAZIO",
            "canonical_eft_closure": "BLOCKED_UNTIL_CONSERVATION_OR_INTERACTION_SEMANTICS_SELECTED",
        },
    }
    out = Path(args.out_json)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary["checks"], indent=2))


if __name__ == "__main__":
    main()
