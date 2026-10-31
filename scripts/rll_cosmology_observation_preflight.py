#!/usr/bin/env python3
"""Fail-closed, read-only checks before RLL cosmological comparison.

SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM
No retuning, covariance replacement or observational stacking here.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POINTS = "data/real/cosmology/desi_dr2_bao_primary_points.csv"
COV = "data/real/desi_dr2_bao_covariance.csv"
JOINT = "results/structure_d/joint_real_likelihood.json"
ORAD = 9.0e-5
MODELS = ("LCDM_joint_real", "wCDM_joint_real", "CPL_w0waCDM_joint_real", "RLL_joint_real")


def read_points(path):
    with path.open(encoding="utf-8", newline="") as fd:
        return list(csv.DictReader(fd))


def read_covariance(path):
    with path.open(encoding="utf-8", newline="") as fd:
        rows = list(csv.reader(fd))
    if len(rows) < 2:
        raise ValueError("empty covariance")
    size = len(rows[0]) - 1
    matrix = []
    for i, row in enumerate(rows[1:]):
        if len(row) != size + 1 or row[0] != str(i):
            raise ValueError("covariance index/width mismatch")
        matrix.append([float(v) for v in row[1:]])
    if len(matrix) != size:
        raise ValueError("covariance not square")
    return matrix


def covariance_gate(points, matrix, tolerance=0.10):
    n = len(points)
    if len(matrix) != n or any(len(r) != n for r in matrix):
        return {"state": "BLOCKED_DIMENSION", "expected": n, "actual": len(matrix)}
    failures = []
    ratios = []
    for i in range(n):
        variance = matrix[i][i]
        sigma = float(points[i]["sigma"])
        if not math.isfinite(variance) or variance <= 0 or not math.isfinite(sigma) or sigma <= 0:
            failures.append({"index": i, "reason": "invalid_variance_or_sigma"})
            continue
        cs = math.sqrt(variance)
        ratio = cs / sigma
        ratios.append({"index": i, "tracer": points[i]["tracer"],
                       "observable": points[i]["observable"],
                       "sigma_csv": sigma, "sqrt_cov_ii": cs, "ratio": ratio})
        if abs(ratio - 1) > tolerance:
            failures.append({"index": i, "reason": "sigma_covariance_mismatch", "ratio": ratio})
        for j in range(i):
            if not math.isfinite(matrix[i][j]) or not math.isclose(matrix[i][j], matrix[j][i], rel_tol=1e-10, abs_tol=1e-12):
                failures.append({"index": i, "other": j, "reason": "asymmetric_or_nonfinite"})
    # A diagonal consistency gate does not establish positive definiteness or official row ordering.
    return {"state": "BLOCKED_COVARIANCE_ALIGNMENT" if failures else "PASS_DIAGONAL_SYMMETRY_ONLY",
            "failures": failures, "ratios": ratios,
            "official_order_verified": "TOKEN_VAZIO",
            "positive_definite_verified": "TOKEN_VAZIO"}


def normalization_gate(joint, tolerance=1e-5):
    results = []
    for row in joint.get("rows", []):
        model = row.get("model")
        if model not in MODELS:
            continue
        om = float(row["Om"])
        ol = float(row["OL"])
        os0 = float(row.get("Os0") or 0)
        e2_zero = om + ol + ORAD + os0
        h0 = float(row["H0"])
        results.append({
            "model": model, "E2_at_z0": e2_zero,
            "H_at_z0": h0 * math.sqrt(e2_zero) if e2_zero > 0 else None,
            "parameter_H0": h0,
            "state": "PASS" if abs(e2_zero - 1) <= tolerance else "BLOCKED_E0_NOT_UNITY",
        })
    return {"state": "BLOCKED_NORMALIZATION" if len(results) != 4 or any(r["state"] != "PASS" for r in results) else "PASS",
            "rows": results, "convention": "E(z)=H(z)/H0 physical; no parameter refit performed"}


def evaluate(root):
    points = read_points(root / POINTS)
    matrix = read_covariance(root / COV)
    joint = json.loads((root / JOINT).read_text(encoding="utf-8"))
    cov = covariance_gate(points, matrix)
    norm = normalization_gate(joint)
    ok = cov["state"].startswith("PASS") and norm["state"] == "PASS"
    return {
        "schema": "rll.cosmology.observation_preflight.v1",
        "read_only": True, "parameters_changed": False,
        "data_modified": False, "likelihood_modified": False,
        "claim_allowed": False,
        "route_state": "PRECHECK_ONLY" if ok else "BLOCKED",
        "source": {"points": POINTS, "covariance": COV, "joint": JOINT},
        "covariance": cov, "normalization": norm,
        "external_2026_observations": {
            "state": "REFERENCE_ONLY_NOT_IN_LIKELIHOOD",
            "lyalpha_2026": {"redshift": 2.33, "DM_over_rd": 39.32, "DM_sigma": 0.33,
                            "DH_over_rd": 8.600, "DH_sigma": 0.066,
                            "source": "DESI 2026 Lyman-alpha BAO/AP publication",
                            "joint_covariance_with_2025": "TOKEN_VAZIO",
                            "independent_sample": False}
        },
        "geometry_7d": "TOKEN_VAZIO_PENDING_ALIGNMENT",
        "toroidal_physical_binding": "TOKEN_VAZIO",
        "next": "Verify DESI covariance official ordering; reconcile H0/E0 convention before non-null model comparisons."
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    report = evaluate(args.root)
    print(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False))
    return 0 if report["route_state"] == "PRECHECK_ONLY" else 2


if __name__ == "__main__":
    raise SystemExit(main())
