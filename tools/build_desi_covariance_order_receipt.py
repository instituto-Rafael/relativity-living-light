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
G3_PRIMARY_SOURCE = ROOT / "data/contracts/rll_g3_dataset_compatibility.v1.json"
COBAYA_MEAN = ROOT / "data/real/cosmology/desi_bao_dr2_cobaya/desi_gaussian_bao_ALL_GCcomb_mean.tsv"
COBAYA_COV = ROOT / "data/real/cosmology/desi_bao_dr2_cobaya/desi_gaussian_bao_ALL_GCcomb_cov.tsv"
COBAYA_MANIFEST = ROOT / "data/real/cosmology/desi_bao_dr2_cobaya/MANIFEST.json"
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



def verify_primary_source_order(
    points: list[dict[str, str]], contract_path: Path = G3_PRIMARY_SOURCE
) -> dict[str, Any]:
    """Fail closed on row permutation, DM/DH reversal or numeric sign drift.

    Contract G3 is a separate, frozen source-table transcription. This validates
    repository custody, not independent external covariance-order provenance.
    """
    with contract_path.open(encoding="utf-8") as handle:
        contract = json.load(handle)
    if contract.get("claim_allowed") is not False:
        raise ValueError("G3 primary-source authority must remain claim_allowed=false")
    entries = contract["sources"]["desi_dr2"]["table4_primary_rows"]
    expected: list[tuple[str, float, str, float, float, str, float | None]] = []
    for item in entries:
        tracer = str(item["tracer"])
        redshift = float(item["z_eff"])
        if item.get("observable") == "DV_over_rd":
            expected.append((tracer, redshift, "DV_over_rd", float(item["value"]), float(item["sigma"]), "", None))
        else:
            correlation = float(item["correlation"])
            expected.append((tracer, redshift, "DM_over_rd", float(item["dm_over_rd"]), float(item["dm_sigma"]), "DH_over_rd", correlation))
            expected.append((tracer, redshift, "DH_over_rd", float(item["dh_over_rd"]), float(item["dh_sigma"]), "DM_over_rd", correlation))
    if len(expected) != EXPECTED_ROWS or len(points) != EXPECTED_ROWS:
        raise ValueError("G3 primary-source vector and DESI rows must have exactly 13 entries")
    for index, (row, record) in enumerate(zip(points, expected)):
        tracer, redshift, observable, value, sigma, paired, correlation = record
        if row["tracer"] != tracer or row["observable"] != observable:
            raise ValueError(f"DESI primary source/order mismatch at index {index}: tracer/observable")
        if row.get("paired_observable", "").strip() != paired:
            raise ValueError(f"DESI primary source/order mismatch at index {index}: paired_observable")
        for field, reference in (("z_eff", redshift), ("value", value), ("sigma", sigma)):
            observed = float(row[field])
            if not math.isfinite(observed) or not math.isclose(
                observed, reference, rel_tol=0.0, abs_tol=1e-12
            ):
                raise ValueError(f"DESI primary source/order mismatch at index {index}: {field}")
        raw_corr = row.get("correlation_coefficient", "").strip()
        if correlation is None:
            if raw_corr:
                raise ValueError(f"DESI primary source/order mismatch at index {index}: isotropic correlation")
        else:
            observed_corr = float(raw_corr)
            if not math.isfinite(observed_corr) or not math.isclose(
                observed_corr, correlation, rel_tol=0.0, abs_tol=1e-12
            ):
                raise ValueError(f"DESI primary source/order mismatch at index {index}: correlation sign/value")
    return {
        "status": "G3_TABLE4_ORDER_VALUE_SIGMA_CORRELATION_CHECKED",
        "contract_path": str(contract_path),
        "contract_sha256": sha256_file(contract_path),
        "checked_rows": EXPECTED_ROWS,
    }


def _repo_path(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)

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




def verify_observation_vector_matches_primary(
    observed_rows: list[dict[str, Any]], primary_rows: list[dict[str, str]]
) -> None:
    """Check external JSON/derived observations against canonical primary row axes."""
    if len(observed_rows) != len(primary_rows) or len(primary_rows) != EXPECTED_ROWS:
        raise ValueError("DESI observation vector cardinality/order mismatch")
    for index, (actual, reference) in enumerate(zip(observed_rows, primary_rows)):
        for field in ("tracer", "observable", "paired_observable", "covariance_block"):
            if field == "covariance_block" and field not in actual:
                continue  # JSON fallback predates the block identifier; identity still pinned.
            if str(actual.get(field, "") or "") != str(reference.get(field, "") or ""):
                raise ValueError(f"DESI derived observation identity mismatch at index {index}: {field}")
        for field in ("z_eff", "value", "sigma", "correlation_coefficient"):
            source_value = reference.get(field, "")
            input_value = actual.get(field)
            if source_value is None or str(source_value).strip() == "":
                if input_value is not None and str(input_value).strip() != "":
                    raise ValueError(f"DESI derived observation spurious value at {index}: {field}")
                continue
            if input_value is None:
                raise ValueError(f"DESI derived observation missing value at {index}: {field}")
            number = float(input_value)
            if not math.isfinite(number) or not math.isclose(
                number, float(source_value), rel_tol=0.0, abs_tol=1e-10
            ):
                raise ValueError(f"DESI derived observation value/sign mismatch at {index}: {field}")


def bind_native_covariance_order(
    points: list[dict[str, str]], matrix: list[list[float]], root: Path = ROOT
) -> dict[str, Any]:
    """Bind the Cobaya covariance's native row order to primary DESI row identities.

    The public DESI/Cobaya ALL mean places Lya DH before DM, whereas the
    repository's Table-IV primary vector places DM before DH. Never infer the
    covariance axis from a bare 13x13 shape; do not edit the immutable input.
    """
    mean_path = root / COBAYA_MEAN.relative_to(ROOT)
    cov_path = root / COBAYA_COV.relative_to(ROOT)
    manifest_path = root / COBAYA_MANIFEST.relative_to(ROOT)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("claim_boundary", {}).get("claim_allowed") is not False:
        raise ValueError("DESI upstream-custody manifest must remain claim_allowed=false")
    records = {item["local_file"]: item for item in manifest["files"]}
    for source_path in (mean_path, cov_path):
        identifier = _repo_path(source_path, root)
        record = records.get(identifier)
        if record is None or sha256_file(source_path) != record.get("local_sha256"):
            raise ValueError(f"DESI source custody missing or hash mismatch for {identifier}")
    with mean_path.open(newline="", encoding="utf-8") as handle:
        native = list(csv.DictReader(handle, delimiter="\t"))
    if len(native) != EXPECTED_ROWS:
        raise ValueError("DESI native Cobaya mean must contain 13 indexed observables")
    native_cov = [
        [float(value) for value in line.split()]
        for line in cov_path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]
    if len(native_cov) != EXPECTED_ROWS or any(len(row) != EXPECTED_ROWS for row in native_cov):
        raise ValueError("DESI native Cobaya covariance must be 13x13")
    if any(
        not math.isclose(matrix[i][j], native_cov[i][j], rel_tol=0.0, abs_tol=1e-12)
        for i in range(EXPECTED_ROWS) for j in range(EXPECTED_ROWS)
    ):
        raise ValueError("DESI repository covariance differs from pinned Cobaya native matrix")
    permutation: list[int] = []
    used: set[int] = set()
    deviations: list[float] = []
    for index, point in enumerate(points):
        matches = [
            native_index for native_index, item in enumerate(native)
            if math.isclose(float(item["z"]), float(point["z_eff"]), rel_tol=0.0, abs_tol=1e-9)
            and item["quantity"].replace("_over_rs", "_over_rd") == point["observable"]
        ]
        if len(matches) != 1 or matches[0] in used:
            raise ValueError(f"DESI native covariance has ambiguous/missing axis for primary row {index}")
        native_index = matches[0]
        used.add(native_index)
        permutation.append(native_index)
        if abs(float(native[native_index]["value"]) - float(point["value"])) > 0.002:
            raise ValueError(f"DESI native mean/Table-IV value disagreement at row {index}")
        sigma_native = math.sqrt(matrix[native_index][native_index])
        sigma_table = float(point["sigma"])
        drift = abs(sigma_native / sigma_table - 1.0)
        deviations.append(drift)
        # An operational diagnostic tolerance, not a scientific source-error bar.
        if not math.isfinite(drift) or drift > 0.10:
            raise ValueError(f"DESI native covariance sigma inconsistent with primary row {index}")
    if sorted(permutation) != list(range(EXPECTED_ROWS)):
        raise ValueError("DESI native covariance mapping is not bijective")
    return {
        "status": "LOCAL_COBAYA_CUSTODY_AND_PERMUTATION_CHECKED",
        "covariance_index_for_primary_row": permutation,
        "native_mean_path": _repo_path(mean_path, root),
        "native_mean_sha256": sha256_file(mean_path),
        "native_covariance_path": _repo_path(cov_path, root),
        "native_covariance_sha256": sha256_file(cov_path),
        "native_manifest_sha256": sha256_file(manifest_path),
        "max_sigma_relative_drift": max(deviations),
        "sigma_drift_operational_limit": 0.10,
        "external_independent_reanalysis": "TOKEN_VAZIO",
    }


def read_summary(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def build_receipt(
    root: Path = ROOT, *, points_override: Path | None = None, covariance_override: Path | None = None
) -> dict[str, Any]:
    points_path = Path(points_override) if points_override is not None else root / POINTS_PATH.relative_to(ROOT)
    covariance_path = Path(covariance_override) if covariance_override is not None else root / COVARIANCE_PATH.relative_to(ROOT)
    summary_path = root / SUMMARY_PATH.relative_to(ROOT)
    points = read_points(points_path)
    source_binding = verify_primary_source_order(points)
    matrix_native = read_covariance(covariance_path)
    native_binding = bind_native_covariance_order(points, matrix_native, root)
    permutation = native_binding["covariance_index_for_primary_row"]
    matrix = [[matrix_native[i][j] for j in permutation] for i in permutation]
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
        if (points[i]["tracer"] != block["tracer"] or points[j]["tracer"] != block["tracer"]
                or not math.isclose(float(points[i]["z_eff"]), float(block["z_eff"]), rel_tol=0.0, abs_tol=1e-12)
                or not math.isclose(float(points[j]["z_eff"]), float(block["z_eff"]), rel_tol=0.0, abs_tol=1e-12)
                or points[i]["observable"] != block["observable_a"]
                or points[j]["observable"] != block["observable_b"]):
            raise ValueError(f"covariance block {block_name} source/observable orientation mismatch")
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
        "primary_source_binding": source_binding,
        "native_covariance_binding": native_binding,
        "covariance_index_for_primary_row": permutation,
        "points_path": _repo_path(points_path, root),
        "points_sha256": sha256_file(points_path),
        "covariance_path": _repo_path(covariance_path, root),
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
            "path": "tools/run_g4_background_tournament.py",
            "behavior": "G4 consumes this custody receipt and permutes source covariance axes before likelihood construction",
            "status": "VERIFIED_G4_ALIGNMENT_ONLY",
        },
        "provenance_boundary": {
            "repo_order_binding": "VERIFIED",
            "external_primary_covariance_order_metadata": "BOUNDED_BY_REPO_DOCUMENTATION_NOT_INDEPENDENT_PRIMARY_ORDER_RECEIPT",
            "interpretation": "This receipt proves deterministic repository wiring, not independent external-source authorship of the matrix ordering.",
        },
        "F_ok": "13 primary rows are G3-bound and the native Cobaya covariance is aligned by a verified permutation; six canonical pairs are checked",
        "F_gap": "non-G4 consumers of the raw matrix remain unaudited; no independent DESI catalog reconstruction or physical cosmology claim",
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
