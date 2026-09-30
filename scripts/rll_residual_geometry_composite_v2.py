#!/usr/bin/env python3
"""RLL residual-geometry composite V2.

This successor AUGMENTS the frozen DESI DR2 full-covariance diagnostic.
It never replaces covariance, sigma, chi-square, or likelihood weights with
Fibonacci, geometry, Poincare, Venturi, or calendar constructions.

SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM
TOKEN_VAZIO != 0
FULL_COVARIANCE_PRECEDES_GEOMETRY_DIAGNOSTICS
FIBONACCI_WINDOW != LIKELIHOOD_WEIGHT
GEOMETRY_MATRIX != COVARIANCE_MATRIX
SQRT3_OVER_2 != SIGMA
RESIDUAL != CAUSE
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BASELINE_PATH = ROOT / "scripts" / "rll_desi_dr2_covariance_multiscale.py"
OUTPUT_SCHEMA = "rll.residual_geometry_composite.v2.receipt"


def _load_baseline():
    spec = importlib.util.spec_from_file_location("rll_desi_covariance_v1", BASELINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load frozen DESI covariance diagnostic")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASE = _load_baseline()


def finite(x: Any, name: str) -> float:
    v = float(x)
    if not math.isfinite(v):
        raise ValueError(f"{name} must be finite")
    return v


def mean(xs: list[float]) -> float:
    if not xs:
        raise ValueError("empty mean")
    return sum(xs) / len(xs)


def popvar(xs: list[float]) -> float:
    m = mean(xs)
    return sum((x - m) ** 2 for x in xs) / len(xs)


def classical_fibonacci_sizes(n: int) -> list[int]:
    """Return 2,3,5,8,... <= n."""
    if n < 2:
        return []
    out = [2]
    a, b = 2, 3
    while b <= n:
        out.append(b)
        a, b = b, a + b
    return out


def rafael_affine_sizes(n: int) -> list[int]:
    """R_(k+1)=R_k+R_(k-1)+1, seeded 1,2; keep sizes >=2."""
    if n < 2:
        return []
    out: list[int] = []
    a, b = 1, 2
    while b <= n:
        out.append(b)
        a, b = b, a + b + 1
    return out


def rafael_affine_step(state: tuple[int, int, int]) -> tuple[int, int, int]:
    """3x3 affine companion matrix [[1,1,1],[1,0,0],[0,0,1]]."""
    rn, rprev, one = state
    if one != 1:
        raise ValueError("affine homogeneous coordinate must be 1")
    return (rn + rprev + one, rn, one)


def solve3(a: list[list[float]], b: list[float]) -> list[float] | None:
    """Small deterministic Gaussian elimination with partial pivoting."""
    m = [row[:] + [rhs] for row, rhs in zip(a, b)]
    for col in range(3):
        pivot = max(range(col, 3), key=lambda r: abs(m[r][col]))
        if abs(m[pivot][col]) <= 1e-15:
            return None
        if pivot != col:
            m[col], m[pivot] = m[pivot], m[col]
        div = m[col][col]
        for j in range(col, 4):
            m[col][j] /= div
        for r in range(3):
            if r == col:
                continue
            f = m[r][col]
            for j in range(col, 4):
                m[r][j] -= f * m[col][j]
    return [m[i][3] for i in range(3)]


def quadratic_descriptor(xs: list[float]) -> dict[str, Any]:
    """Least-squares z(t)=a t^2+b t+c; discriminant is diagnostic only."""
    n = len(xs)
    if n < 3:
        return {
            "state": "TOKEN_VAZIO_INSUFFICIENT_POINTS",
            "coefficients": None,
            "discriminant": None,
        }
    ts = [float(i) for i in range(n)]
    s0 = float(n)
    s1 = sum(ts)
    s2 = sum(t*t for t in ts)
    s3 = sum(t*t*t for t in ts)
    s4 = sum(t*t*t*t for t in ts)
    y0 = sum(xs)
    y1 = sum(t*y for t, y in zip(ts, xs))
    y2 = sum(t*t*y for t, y in zip(ts, xs))
    # column order: t^2, t, 1
    coeff = solve3(
        [[s4, s3, s2], [s3, s2, s1], [s2, s1, s0]],
        [y2, y1, y0],
    )
    if coeff is None:
        return {"state": "TOKEN_VAZIO_SINGULAR_FIT", "coefficients": None, "discriminant": None}
    a, b, c = coeff
    pred = [a*t*t + b*t + c for t in ts]
    sse = sum((y-p)**2 for y, p in zip(xs, pred))
    return {
        "state": "MEASURED_NUMERIC_DIAGNOSTIC",
        "coefficients": {"a": a, "b": b, "c": c},
        "discriminant": b*b - 4.0*a*c,
        "fit_sse": sse,
        "meaning": "quadratic/Bhaskara descriptor; not a causal or physical discriminant",
    }


def triangle_descriptor(xs: list[float]) -> dict[str, Any]:
    """Triangle built from graph points (0,z0), (mid,zmid), (last,zlast)."""
    n = len(xs)
    if n < 3:
        return {"state": "TOKEN_VAZIO_INSUFFICIENT_POINTS"}
    ids = [0, (n - 1) // 2, n - 1]
    pts = [(float(i), xs[i]) for i in ids]

    def dist(p, q):
        return math.hypot(q[0]-p[0], q[1]-p[1])

    sides = [dist(pts[0], pts[1]), dist(pts[1], pts[2]), dist(pts[0], pts[2])]
    ss = sorted(sides)
    denom = max(1e-30, ss[2] * ss[2])
    pythagoras_defect = (ss[0]*ss[0] + ss[1]*ss[1] - ss[2]*ss[2]) / denom
    area2 = (
        pts[0][0]*(pts[1][1]-pts[2][1])
        + pts[1][0]*(pts[2][1]-pts[0][1])
        + pts[2][0]*(pts[0][1]-pts[1][1])
    )
    sm = mean(sides)
    equilateral_deviation = 0.0 if sm == 0 else (max(sides)-min(sides))/sm
    pairs = [abs(sides[0]-sides[1]), abs(sides[1]-sides[2]), abs(sides[0]-sides[2])]
    isosceles_deviation = min(pairs) / max(1e-30, max(sides))
    return {
        "state": "MEASURED_NUMERIC_DIAGNOSTIC",
        "point_indices": ids,
        "side_lengths": sides,
        "signed_area": area2 / 2.0,
        "pythagoras_normalized_defect": pythagoras_defect,
        "equilateral_relative_deviation": equilateral_deviation,
        "isosceles_relative_deviation": isosceles_deviation,
        "sqrt3_over_2_reference": math.sqrt(3.0)/2.0,
        "boundary": "graph-triangle descriptor only; sqrt3/2 is not statistical sigma",
    }


def poincare_lift(xs: list[float]) -> dict[str, Any]:
    """Generic nD computational lift x -> x/(1+||x||) into unit Poincare ball."""
    norm = math.sqrt(sum(x*x for x in xs))
    if norm == 0.0:
        u = [0.0 for _ in xs]
        radius = 0.0
        d0 = 0.0
    else:
        u = [x/(1.0+norm) for x in xs]
        radius = norm/(1.0+norm)
        d0 = 2.0 * math.atanh(radius)
    return {
        "state": "MEASURED_COMPUTATIONAL_EMBEDDING",
        "dimension": len(xs),
        "radius": radius,
        "origin_distance_curvature_minus_1": d0,
        "inside_unit_ball": radius < 1.0,
        "coordinates": u,
        "boundary": "Poincare-ball embedding != return map != physical spacetime metric != conjecture",
    }


def geodesic_sphere_descriptor(xs: list[float]) -> dict[str, Any]:
    """Direction on S^(n-1) and angle to uniform reference vector."""
    n = len(xs)
    norm = math.sqrt(sum(x*x for x in xs))
    if norm == 0.0:
        return {"state": "TOKEN_VAZIO_ZERO_VECTOR_DIRECTION"}
    u = [x/norm for x in xs]
    ref = 1.0/math.sqrt(n)
    dot = max(-1.0, min(1.0, sum(x*ref for x in u)))
    return {
        "state": "MEASURED_NUMERIC_DIAGNOSTIC",
        "sphere_dimension": n-1,
        "unit_direction": u,
        "great_circle_angle_to_uniform_rad": math.acos(dot),
        "boundary": "directional/geodesic descriptor only; not an astrophysical sphere claim",
    }


def finite_difference_descriptor(xs: list[float]) -> dict[str, Any]:
    d1 = [xs[i+1]-xs[i] for i in range(len(xs)-1)]
    d2 = [d1[i+1]-d1[i] for i in range(len(d1)-1)]
    return {
        "first_difference_mean": None if not d1 else mean(d1),
        "first_difference_energy": sum(x*x for x in d1),
        "second_difference_energy": sum(x*x for x in d2),
        "endpoint_tangent": None if len(xs)<2 else (xs[-1]-xs[0])/(len(xs)-1),
    }


def window_descriptor(xs: list[float], start: int, family: str) -> dict[str, Any]:
    q = quadratic_descriptor(xs)
    tri = triangle_descriptor(xs)
    p = poincare_lift(xs)
    out = {
        "start": start,
        "end_exclusive": start+len(xs),
        "size": len(xs),
        "family": family,
        "mean": mean(xs),
        "population_variance": popvar(xs),
        "sum_squares": sum(x*x for x in xs),
        "rms": math.sqrt(sum(x*x for x in xs)/len(xs)),
        "finite_difference": finite_difference_descriptor(xs),
        "quadratic": q,
        "triangle": tri,
        "poincare_nd": p,
        "geodesic_sphere": geodesic_sphere_descriptor(xs),
    }
    if len(xs) >= 7:
        out["poincare_7d_prefix"] = poincare_lift(xs[:7])
    else:
        out["poincare_7d_prefix"] = {"state": "TOKEN_VAZIO_WINDOW_LT_7"}
    return out


def family_scan(xs: list[float], sizes: list[int], family: str) -> dict[str, Any]:
    return {
        "family": family,
        "likelihood_weight": False,
        "sizes": sizes,
        "windows": [
            window_descriptor(xs[i:i+k], i, family)
            for k in sizes
            for i in range(len(xs)-k+1)
        ],
    }


def diagnose_model(model: dict[str, Any]) -> dict[str, Any]:
    z = [finite(x, "whitened_residual") for x in model["whitened_residuals"]]
    return {
        "model": model["model"],
        "n": len(z),
        "chi2_input": model["chi2_from_whitened"],
        "chi2_reconstructed": sum(x*x for x in z),
        "chi2_identity_pass": math.isclose(
            finite(model["chi2_from_whitened"], "chi2"),
            sum(x*x for x in z),
            rel_tol=1e-12,
            abs_tol=1e-12,
        ),
        "classical_fibonacci": family_scan(
            z, classical_fibonacci_sizes(len(z)), "CLASSICAL_FIBONACCI"
        ),
        "rafael_affine": family_scan(
            z, rafael_affine_sizes(len(z)), "RAFAEL_AFFINE_PLUS_ONE"
        ),
    }


def evaluate() -> dict[str, Any]:
    baseline = BASE.evaluate()
    if baseline.get("claim_allowed") is not False:
        raise ValueError("baseline claim gate unexpectedly open")
    models = baseline["models"]
    composite = {
        "LCDM": diagnose_model(models["LCDM"]),
        "RLL": diagnose_model(models["RLL"]),
    }
    for name in ("LCDM", "RLL"):
        if not math.isclose(
            composite[name]["chi2_reconstructed"],
            models[name]["chi2_from_whitened"],
            rel_tol=1e-12,
            abs_tol=1e-12,
        ):
            raise ValueError(f"{name} chi2 changed under diagnostic composition")

    return {
        "schema": OUTPUT_SCHEMA,
        "state": "MEASURED_NUMERIC_LOCAL_OR_CI",
        "claim_allowed": False,
        "baseline_schema": baseline["schema"],
        "likelihood_mutated": False,
        "n_observations": baseline["n_observations"],
        "covariance": baseline["covariance"],
        "baseline_cross_model": baseline["cross_model"],
        "diagnostics": composite,
        "matrix_families": {
            "classical_fibonacci": {
                "Q_F": [[1,1],[1,0]],
                "identity": "Q_F^n=[[F_(n+1),F_n],[F_n,F_(n-1)]] for n>=1",
            },
            "rafael_affine_plus_one": {
                "A_R": [[1,1,1],[1,0,0],[0,0,1]],
                "state_vector": "[R_n,R_(n-1),1]^T",
                "recurrence": "R_(n+1)=R_n+R_(n-1)+1",
                "closed_relation_source": "R_n=F_(n+3)-1",
            },
        },
        "typed_adapters": {
            "poincare_nd": {
                "state": "ACTIVE_COMPUTATIONAL_DIAGNOSTIC",
                "physical_binding": False,
            },
            "poincare_7d": {
                "state": "ACTIVE_PREFIX_DIAGNOSTIC_WHEN_WINDOW_GE_7",
                "physical_binding": False,
                "full_formal_namespace": "H7/hyperboloid -> B7 Poincare ball; S1 phase is separate",
            },
            "geodesic_sphere": {
                "state": "ACTIVE_DIRECTIONAL_DIAGNOSTIC",
                "physical_binding": False,
            },
            "pitagoras_bhaskara_tangent": {
                "state": "ACTIVE_DIAGNOSTIC_DESCRIPTORS",
                "physical_binding": False,
            },
            "venturi": {
                "state": "TOKEN_VAZIO_FLUID_BINDING",
                "required": [
                    "geometry","fluid","units","boundary_conditions",
                    "viscosity","temperature","covariance","falsifier"
                ],
                "changes_likelihood": False,
            },
            "calendar": {
                "state": "TOKEN_VAZIO_TEMPORAL_BINDING",
                "reason": "DESI redshift vector is not a calendar-time series",
                "changes_likelihood": False,
            },
        },
        "hard_boundaries": [
            "FULL_COVARIANCE_PRECEDES_GEOMETRY_DIAGNOSTICS",
            "STANDARD_DEVIATION_IS_NOT_REPLACED",
            "FIBONACCI_WINDOW != LIKELIHOOD_WEIGHT",
            "RAFAEL_AFFINE_WINDOW != LIKELIHOOD_WEIGHT",
            "SQRT3_OVER_2 != SIGMA",
            "GEOMETRY_MATRIX != COVARIANCE_MATRIX",
            "QUADRATIC_DISCRIMINANT != MODEL_SELECTION_SCORE",
            "POINCARE_BALL != POINCARE_RETURN_MAP != POINCARE_CONJECTURE",
            "GEODESIC_DESCRIPTOR != PHYSICAL_GEODESIC_CLAIM",
            "VENTURI_PHYSICAL != VENTURI_COMPUTATIONAL",
            "CALENDAR_PERIODICITY != ASTROPHYSICAL_MECHANISM",
            "WHITENED_RESIDUAL != CAUSE",
        ],
        "F_ok": (
            "full-covariance chi2 preserved while classical/Rafael Fibonacci scales "
            "and typed geometry diagnostics are added"
        ),
        "F_gap": (
            "held-out/non-null scientific discrimination; physical Venturi/calendar/Poincare "
            "bindings; independent reproduction"
        ),
        "F_next": (
            "run provider gate; then freeze one held-out or non-null RLL profile and compare "
            "diagnostic stability without retuning windows or covariance"
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default="-")
    args = ap.parse_args()
    try:
        out = evaluate()
        rc = 0
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        out = {
            "schema": OUTPUT_SCHEMA,
            "state": "FAIL_CLOSED",
            "error": str(exc),
            "claim_allowed": False,
        }
        rc = 2
    rendered = json.dumps(out, indent=2, ensure_ascii=False) + "\n"
    if args.output == "-":
        print(rendered, end="")
    else:
        Path(args.output).write_text(rendered, encoding="utf-8")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
