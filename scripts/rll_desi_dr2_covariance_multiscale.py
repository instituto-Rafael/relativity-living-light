#!/usr/bin/env python3
"""DESI DR2 full-covariance residual diagnostic for RLL.

SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM
TOKEN_VAZIO != 0
FIBONACCI_WINDOW != LIKELIHOOD_WEIGHT
GEOMETRY_MATRIX != COVARIANCE_MATRIX
WHITENED_RESIDUAL != CAUSE
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
POINTS = ROOT / "data/real/cosmology/desi_dr2_bao_primary_points.csv"
COV = ROOT / "data/real/desi_dr2_bao_covariance.csv"
REPRO = ROOT / "results/RLL_G4_DESI_GEOMETRY_LCDM_RLL_REPRODUCTION_V1.json"
OUTPUT_SCHEMA = "rll.desi_dr2.covariance_whitened_multiscale.receipt.v1"


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


def load_points(path: Path) -> list[dict[str, Any]]:
    out = []
    with path.open(newline="", encoding="utf-8") as f:
        rd = csv.DictReader(f)
        need = {"tracer", "z_eff", "observable", "value", "sigma", "covariance_block"}
        if not need.issubset(set(rd.fieldnames or [])):
            raise ValueError("DESI points missing required fields")
        for i, r in enumerate(rd):
            out.append({
                "index": i,
                "tracer": r["tracer"],
                "z": finite(r["z_eff"], f"z[{i}]"),
                "observable": r["observable"],
                "observed": finite(r["value"], f"value[{i}]"),
                "sigma": finite(r["sigma"], f"sigma[{i}]"),
                "block": r["covariance_block"],
            })
    if not out:
        raise ValueError("empty DESI vector")
    return out


def load_cov(path: Path) -> list[list[float]]:
    out = []
    with path.open(newline="", encoding="utf-8") as f:
        rd = csv.reader(f)
        head = next(rd, None)
        if head is None or len(head) < 2:
            raise ValueError("covariance header missing")
        n = len(head) - 1
        for i, r in enumerate(rd):
            if len(r) != n + 1 or r[0] != str(i):
                raise ValueError(f"covariance row {i} malformed")
            out.append([finite(x, f"C[{i}]") for x in r[1:]])
    if len(out) != n:
        raise ValueError("covariance is not square")
    return out


def cholesky(a: list[list[float]]) -> list[list[float]]:
    n = len(a)
    if n == 0 or any(len(r) != n for r in a):
        raise ValueError("matrix must be square")
    for i in range(n):
        if a[i][i] <= 0:
            raise ValueError(f"non-positive covariance diagonal {i}")
        for j in range(i + 1, n):
            if not math.isclose(a[i][j], a[j][i], rel_tol=1e-12, abs_tol=1e-12):
                raise ValueError(f"covariance asymmetric at {i},{j}")
    L = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1):
            s = sum(L[i][k] * L[j][k] for k in range(j))
            if i == j:
                p = a[i][i] - s
                if p <= 0:
                    raise ValueError(f"covariance not positive definite at {i}")
                L[i][j] = math.sqrt(p)
            else:
                L[i][j] = (a[i][j] - s) / L[j][j]
    return L


def forward(L: list[list[float]], b: list[float]) -> list[float]:
    if len(L) != len(b):
        raise ValueError("matrix/vector size mismatch")
    x = [0.0] * len(b)
    for i in range(len(b)):
        x[i] = (b[i] - sum(L[i][j] * x[j] for j in range(i))) / L[i][i]
    return x


def fib_sizes(n: int) -> list[int]:
    if n < 2:
        return []
    out, a, b = [2], 2, 3
    while b <= n:
        out.append(b)
        a, b = b, a + b
    return out


def windows(xs: list[float], k: int) -> list[dict[str, Any]]:
    out = []
    for i in range(len(xs) - k + 1):
        w = xs[i:i+k]
        out.append({
            "start": i,
            "end_exclusive": i + k,
            "mean": mean(w),
            "population_variance": popvar(w),
            "mean_square": sum(x*x for x in w) / k,
            "sum_squares": sum(x*x for x in w),
        })
    return out


def validate_order(points: list[dict[str, Any]], preds: list[dict[str, Any]]) -> None:
    if len(points) != len(preds):
        raise ValueError("prediction length mismatch")
    for i, (p, q) in enumerate(zip(points, preds)):
        if p["tracer"] != q.get("tracer") or p["observable"] != q.get("observable"):
            raise ValueError(f"prediction order mismatch at {i}")
        if not math.isclose(p["z"], finite(q.get("z"), f"pred.z[{i}]"), abs_tol=1e-12):
            raise ValueError(f"redshift mismatch at {i}")
        if not math.isclose(p["observed"], finite(q.get("observed"), f"pred.obs[{i}]"), abs_tol=1e-12):
            raise ValueError(f"observed mismatch at {i}")


def diagnose(name: str, points: list[dict[str, Any]], C: list[list[float]], model: dict[str, Any]) -> dict[str, Any]:
    preds = model["predictions"]
    validate_order(points, preds)
    r = [p["observed"] - finite(q["predicted"], f"{name}.pred[{i}]")
         for i, (p, q) in enumerate(zip(points, preds))]
    z = forward(cholesky(C), r)
    chi2 = sum(x*x for x in z)
    recorded = finite(model["chi2_DESI_recomputed"], f"{name}.chi2")
    blocks: dict[str, list[int]] = {}
    for p in points:
        blocks.setdefault(p["block"], []).append(p["index"])

    cross = 0.0
    owner = {i: b for b, ids in blocks.items() for i in ids}
    for i in range(len(C)):
        for j in range(len(C)):
            if owner[i] != owner[j]:
                cross = max(cross, abs(C[i][j]))

    block_rows = []
    for b, ids in blocks.items():
        cb = [[C[i][j] for j in ids] for i in ids]
        rb = [r[i] for i in ids]
        zb = forward(cholesky(cb), rb)
        block_rows.append({
            "block": b,
            "indices": ids,
            "n": len(ids),
            "chi2": sum(x*x for x in zb),
            "mean_whitened_residual": mean(zb),
            "max_abs_whitened_residual": max(abs(x) for x in zb),
        })
    block_sum = sum(x["chi2"] for x in block_rows)
    block_applicable = cross <= 1e-15

    return {
        "model": name,
        "parameters": model.get("parameters", {}),
        "residuals_observed_minus_model": r,
        "whitened_residuals": z,
        "chi2_from_whitened": chi2,
        "chi2_recorded_reproduction": recorded,
        "chi2_reproduction_error": chi2 - recorded,
        "chi2_reproduction_match": math.isclose(chi2, recorded, rel_tol=1e-9, abs_tol=1e-9),
        "chi2_per_observation": chi2 / len(points),
        "block_diagnostics": {
            "covariance_is_block_diagonal_observed": block_applicable,
            "cross_block_max_abs_covariance": cross,
            "blocks": block_rows,
            "block_chi2_sum": block_sum,
            "block_closure_error": chi2 - block_sum,
            "block_closure_pass": block_applicable and math.isclose(chi2, block_sum, rel_tol=1e-12, abs_tol=1e-12),
        },
        "fibonacci_multiscale": {
            "state": "MEASURED_NUMERIC",
            "window_family": "CLASSICAL_FIBONACCI_SIZES",
            "values": "CHOLESKY_WHITENED_RESIDUALS",
            "weights_likelihood": False,
            "scales": [{"size": k, "windows": windows(z, k)} for k in fib_sizes(len(z))],
        },
    }


def evaluate(points_path: Path = POINTS, covariance_path: Path = COV, reproduction_path: Path = REPRO) -> dict[str, Any]:
    points = load_points(points_path)
    C = load_cov(covariance_path)
    if len(C) != len(points):
        raise ValueError("covariance dimension does not match DESI vector")
    repro = json.loads(reproduction_path.read_text(encoding="utf-8"))
    if repro.get("schema") != "rll.g4.desi_geometry_lcdm_rll_reproduction.v1":
        raise ValueError("unexpected G4 reproduction schema")
    outputs = repro["outputs"]
    lcdm = diagnose("LCDM", points, C, outputs["LCDM"])
    rll = diagnose("RLL", points, C, outputs["RLL"])
    os0 = outputs["RLL"].get("parameters", {}).get("Os0")
    null = os0 is not None and math.isclose(finite(os0, "RLL.Os0"), 0.0, abs_tol=1e-15)

    return {
        "schema": OUTPUT_SCHEMA,
        "state": "MEASURED_NUMERIC_LOCAL_OR_CI",
        "claim_allowed": False,
        "source_files": {
            "points": str(points_path.relative_to(ROOT)),
            "covariance": str(covariance_path.relative_to(ROOT)),
            "reproduction": str(reproduction_path.relative_to(ROOT)),
        },
        "n_observations": len(points),
        "covariance": {
            "dimension": [len(C), len(C)],
            "validated_symmetric": True,
            "validated_positive_definite_by_cholesky": True,
            "role": "LIKELIHOOD_AND_WHITENING_AUTHORITY",
        },
        "models": {"LCDM": lcdm, "RLL": rll},
        "cross_model": {
            "rll_minus_lcdm_chi2": rll["chi2_from_whitened"] - lcdm["chi2_from_whitened"],
            "rll_on_lcdm_null_submanifold": null,
            "interpretation": (
                "Frozen G4 RLL has Os0=0; this reproduces covariance geometry, not model separation."
                if null else
                "Models remain separate; no superiority claim is made."
            ),
        },
        "geometry_bindings": {
            "fibonacci": {"state": "ACTIVE_DIAGNOSTIC_ONLY", "role": "window sizes on whitened residuals", "changes_likelihood": False},
            "sqrt3_over_2": {"state": "REFERENCE_ONLY", "role": "Euclidean/projective kernel; not sigma", "changes_likelihood": False},
            "poincare": {"state": "INACTIVE_IN_THIS_LIKELIHOOD", "role": "typed manifold/metric or return-map adapter", "changes_likelihood": False},
            "venturi": {"state": "INACTIVE_IN_THIS_LIKELIHOOD", "role": "fluid adapter only after units/boundaries/falsifier", "changes_likelihood": False},
            "calendar": {"state": "INACTIVE_IN_THIS_LIKELIHOOD", "role": "temporal comparator only", "changes_likelihood": False},
        },
        "hard_boundaries": [
            "FULL_COVARIANCE_PRECEDES_DIAGONAL_APPROXIMATION_WHEN_AVAILABLE",
            "WHITENED_RESIDUAL != CAUSE",
            "FIBONACCI_WINDOW != LIKELIHOOD_WEIGHT",
            "GEOMETRY_MATRIX != COVARIANCE_MATRIX",
            "SQRT3_OVER_2 != SIGMA",
            "POINCARE_BALL != POINCARE_RETURN_MAP != POINCARE_CONJECTURE",
            "VENTURI_PHYSICAL != VENTURI_COMPUTATIONAL",
            "CALENDAR_PERIODICITY != ASTROPHYSICAL_MECHANISM",
        ],
        "F_ok": "full covariance consumed; whitening reproduces committed G4 chi2 and exposes block/multiscale residual diagnostics",
        "F_gap": "G4 RLL point is on LCDM null submanifold; held-out/non-null discrimination and independent reproduction remain separate",
        "F_next": "run CI, then apply the same frozen diagnostic to a preregistered non-null or held-out RLL profile without retuning",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--points", type=Path, default=POINTS)
    ap.add_argument("--covariance", type=Path, default=COV)
    ap.add_argument("--reproduction", type=Path, default=REPRO)
    ap.add_argument("--output", default="-")
    a = ap.parse_args()
    try:
        out = evaluate(a.points, a.covariance, a.reproduction)
        rc = 0
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as e:
        out = {"schema": OUTPUT_SCHEMA, "state": "FAIL_CLOSED", "error": str(e), "claim_allowed": False}
        rc = 2
    text_out = json.dumps(out, indent=2, ensure_ascii=False) + "\n"
    if a.output == "-":
        print(text_out, end="")
    else:
        Path(a.output).write_text(text_out, encoding="utf-8")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
