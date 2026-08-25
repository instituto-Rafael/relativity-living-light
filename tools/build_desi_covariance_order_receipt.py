#!/usr/bin/env python3
"""Build a deterministic repo-local DESI BAO vector/covariance order receipt.

The receipt proves how the current repository wires the 13 ordered BAO rows to
covariance indices 0..12.  It does not prove that external primary-source
covariance metadata used the same ordering unless that primary metadata is
independently archived and hash-bound.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
POINTS_PATH = ROOT / "data/real/cosmology/desi_dr2_bao_primary_points.csv"
COVARIANCE_PATH = ROOT / "data/real/desi_dr2_bao_covariance.csv"
SUMMARY_PATH = ROOT / "data/real/cosmology/desi_dr2_bao_covariance_summary.csv"
EXPECTED_ROWS = 13


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_json(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def read_points(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != EXPECTED_ROWS:
        raise ValueError(f"DESI primary vector must have {EXPECTED_ROWS} rows, got {len(rows)}")
    required = {"release", "tracer", "z_eff", "observable", "value", "sigma", "covariance_block", "primary_likelihood"}
    if not rows or not required.issubset(rows[0]):
        raise ValueError("DESI primary vector is missing required identity fields")
    if any(str(row["primary_likelihood"]).strip().lower() != "true" for row in rows):
        raise ValueError("every canonical DESI row must be marked primary_likelihood=true")
    return rows


def read_covariance(path: Path) -> list[list[float]]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.reader(handle))
    if len(rows) != EXPECTED_ROWS + 1 or rows[0][1:] != [str(i) for i in range(EXPECTED_ROWS)]:
        raise ValueError("DESI covariance header/order must be explicit indices 0..12")
    matrix: list[list[float]] = []
    for index, row in enumerate(rows[1:]):
        if len(row) != EXPECTED_ROWS + 1 or row[0] != str(index):
            raise ValueError(f"DESI covariance row {index} is not bound to explicit index {index}")
        matrix.append([float(value) for value in row[1:]])
    for i in range(EXPECTED_ROWS):
        if matrix[i][i] <= 0.0:
            raise ValueError(f"DESI covariance diagonal at {i} is not positive")
        for j in range(EXPECTED_ROWS):
            if not math.isclose(matrix[i][j], matrix[j][i], rel_tol=0.0, abs_tol=1e-12):
                raise ValueError(f"DESI covariance is asymmetric at {i},{j}")
    return matrix


def read_summary(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def build_receipt(root: Path = ROOT) -> dict[str, Any]:
    points_path = root / POINTS_PATH.relative_to(ROOT)
    covariance_path = root / COVARIANCE_PATH.relative_to(ROOT)
    summary_path = root / SUMMARY_PATH.relative_to(ROOT)
    points = read_points(points_path)
    matrix = read_covariance(covariance_path)
    summary = read_summary(summary_path)

    mapping: list[dict[str, Any]] = []
    for index, row in enumerate(points):
        identity = {
            "index": index,
            "release": row["release"],
            "tracer": row["tracer"],
            "z_eff": row["z_eff"],
            "observable": row["observable"],
            "covariance_block": row["covariance_block"],
            "value": row["value"],
            "sigma": row["sigma"],
        }
        identity["identity_sha256"] = sha256_json(identity)
        mapping.append(identity)

    expected_nonzero_pairs: set[tuple[int, int]] = set()
    pair_checks: list[dict[str, Any]] = []
    for block in summary:
        block_name = block["covariance_block"]
        indices = [index for index, row in enumerate(points) if row["covariance_block"] == block_name]
        if len(indices) != 2:
            raise ValueError(f"covariance block {block_name} must map to exactly two primary-vector rows")
        i, j = sorted(indices)
        expected_nonzero_pairs.add((i, j))
        observed = matrix[i][j]
        correlation = float(block["correlation_coefficient"])
        if observed == 0.0:
            raise ValueError(f"covariance block {block_name} maps to zero off-diagonal covariance")
        if math.copysign(1.0, observed) != math.copysign(1.0, correlation):
            raise ValueError(f"covariance block {block_name} sign disagrees with summary correlation")
        pair_checks.append(
            {
                "covariance_block": block_name,
                "indices": [i, j],
                "observables": [points[i]["observable"], points[j]["observable"]],
                "matrix_covariance": observed,
                "summary_covariance_from_rounded_inputs": float(block["covariance"]),
                "summary_correlation": correlation,
                "sign_consistent": True,
            }
        )

    unexpected_nonzero_pairs: list[list[int]] = []
    for i in range(EXPECTED_ROWS):
        for j in range(i + 1, EXPECTED_ROWS):
            if matrix[i][j] != 0.0 and (i, j) not in expected_nonzero_pairs:
                unexpected_nonzero_pairs.append([i, j])
    if unexpected_nonzero_pairs:
        raise ValueError(f"unexpected cross-block off-diagonal covariance: {unexpected_nonzero_pairs}")

    vector_identity = [
        {
            "index": row["index"],
            "tracer": row["tracer"],
            "z_eff": row["z_eff"],
            "observable": row["observable"],
            "covariance_block": row["covariance_block"],
        }
        for row in mapping
    ]

    return {
        "schema": "rll.desi_covariance_order_receipt.v1",
        "state": "VERIFIED_REPO_ORDER_BINDING",
        "claim_allowed": False,
        "scientific_confirmation": False,
        "points_path": str(points_path.relative_to(root)),
        "points_sha256": sha256_file(points_path),
        "covariance_path": str(covariance_path.relative_to(root)),
        "covariance_sha256": sha256_file(covariance_path),
        "summary_path": str(summary_path.relative_to(root)),
        "summary_sha256": sha256_file(summary_path),
        "vector_rows": EXPECTED_ROWS,
        "covariance_shape": [EXPECTED_ROWS, EXPECTED_ROWS],
        "ordered_vector_identity_sha256": sha256_json(vector_identity),
        "matrix_index_to_vector_row": mapping,
        "pair_checks": pair_checks,
        "unexpected_nonzero_pairs": [],
        "consumer_binding": {
            "path": "data/pipelines/structure_d/joint_real_likelihood.py",
            "behavior": "pd.read_csv(primary_points) preserves file row order; covariance is read with index_col=0 and accepted only at matching shape",
            "status": "VERIFIED_REPO_WIRING",
        },
        "provenance_boundary": {
            "repo_order_binding": "VERIFIED",
            "external_primary_covariance_order_metadata": "BOUNDED_BY_REPO_DOCUMENTATION_NOT_INDEPENDENT_PRIMARY_ORDER_RECEIPT",
            "interpretation": "This receipt proves deterministic repository wiring, not independent external-source authorship of the matrix ordering.",
        },
        "F_ok": "13 primary rows are deterministically bound to covariance indices 0..12 and six anisotropic covariance blocks map to the expected row pairs",
        "F_gap": "independent primary-source covariance-order metadata is not promoted by this repo-local receipt",
        "F_next": "carry this vector identity hash into the future G2/G5 canonical likelihood manifest",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build DESI covariance/order binding receipt")
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        receipt = build_receipt(ROOT)
    except (OSError, ValueError) as exc:
        print(f"[rll] BLOCKED_DESI_ORDER_BINDING: {exc}", file=sys.stderr)
        return 2
    payload = json.dumps(receipt, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    if args.json or args.output is None:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
