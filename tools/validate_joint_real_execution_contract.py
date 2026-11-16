#!/usr/bin/env python3
"""Validate the exact input/provenance contract of the joint real likelihood.

SOURCE != DERIVED_MATERIALIZATION != EXECUTION_BYTES != EVIDENCE != CLAIM.
This validator proves only that the declared source/derivation/execution bindings
match the committed repository state. It does not validate a cosmological model.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data.pipelines.structure_d import joint_real_likelihood as joint  # noqa: E402

MANIFEST_PATH = ROOT / "data" / "inputs" / "cosmology_joint" / "joint_real_inputs_manifest.json"
CANONICAL_PATH = ROOT / "data" / "real" / "cosmology" / "observational_sources_manifest.json"

RUNTIME_PATHS = {
    "expansion_Hz": joint.HZ_PATH,
    "bao_DESI_DR2": joint.DESI_POINTS_PATH,
    "growth_fsigma8": joint.FSIGMA8_PATH,
    "cmb_shift": joint.CMB_SHIFT_PATH,
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_sources() -> dict[str, dict[str, object]]:
    payload = json.loads(CANONICAL_PATH.read_text(encoding="utf-8"))
    return {row["source_id"]: row for row in payload["canonical_local_real_sources"]}


def _csv_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def _validate_hz_derivation(entry: dict[str, object], canonical: dict[str, dict[str, object]]) -> dict[str, object]:
    derivation = entry.get("derivation")
    if not isinstance(derivation, dict):
        return {"state": "FAIL", "reason": "missing derivation object"}
    parent_id = entry.get("parent_source_id")
    parent = canonical.get(str(parent_id))
    if parent is None:
        return {"state": "FAIL", "reason": f"parent source not canonical: {parent_id}"}

    parent_path = ROOT / str(entry.get("parent_path"))
    execution_path = ROOT / str(entry.get("execution_path"))
    expected_parent = ROOT / str(parent["local_path"])
    if parent_path.resolve() != expected_parent.resolve():
        return {"state": "FAIL", "reason": "parent_path does not resolve to canonical parent source"}

    parent_fields, parent_rows = _csv_rows(parent_path)
    child_fields, child_rows = _csv_rows(execution_path)
    preserve = list(derivation.get("preserve_columns", []))
    predicate = derivation.get("predicate")
    if predicate != "source == CC_Moresco2022":
        return {"state": "FAIL", "reason": f"unsupported derivation predicate: {predicate}"}
    if preserve != parent_fields or child_fields != preserve:
        return {
            "state": "FAIL",
            "reason": "column preservation mismatch",
            "parent_fields": parent_fields,
            "child_fields": child_fields,
            "declared": preserve,
        }

    derived = [{key: row[key] for key in preserve} for row in parent_rows if row.get("source") == "CC_Moresco2022"]
    expected_rows = int(derivation.get("expected_rows", -1))
    state = "PASS" if derived == child_rows and len(derived) == expected_rows else "FAIL"
    return {
        "state": state,
        "predicate": predicate,
        "parent_rows": len(parent_rows),
        "derived_rows": len(derived),
        "execution_rows": len(child_rows),
        "expected_rows": expected_rows,
        "rows_exact_match": derived == child_rows,
        "parent_sha256": sha256(parent_path),
        "execution_sha256": sha256(execution_path),
    }


def build_receipt() -> dict[str, object]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    canonical = _canonical_sources()
    entries = manifest.get("inputs", [])
    rows: list[dict[str, object]] = []
    blocking: list[str] = []

    seen_axes: set[str] = set()
    for entry in entries:
        axis = str(entry.get("axis"))
        source_id = str(entry.get("source_id"))
        seen_axes.add(axis)
        runtime_path = RUNTIME_PATHS.get(axis)
        execution_path = ROOT / str(entry.get("execution_path"))
        declared_sha = str(entry.get("execution_sha256"))
        source = canonical.get(source_id)

        checks = {
            "canonical_source_registered": source is not None,
            "execution_file_exists": execution_path.is_file(),
            "runtime_axis_known": runtime_path is not None,
            "runtime_path_matches_manifest": runtime_path is not None and runtime_path.resolve() == execution_path.resolve(),
            "execution_sha256_matches": execution_path.is_file() and sha256(execution_path) == declared_sha,
        }

        canonical_exact = False
        if source is not None:
            source_path = ROOT / str(source["local_path"])
            canonical_exact = (
                source_path.is_file()
                and source_path.resolve() == execution_path.resolve()
                and str(source.get("sha256")) == declared_sha
                and sha256(source_path) == declared_sha
            )

        derivation_receipt = None
        if axis == "expansion_Hz":
            derivation_receipt = _validate_hz_derivation(entry, canonical)
            checks["derived_materialization_verified"] = derivation_receipt["state"] == "PASS"
        else:
            checks["canonical_execution_binding"] = canonical_exact

        if axis == "bao_DESI_DR2":
            covariance_path = ROOT / str(entry.get("covariance_path"))
            covariance_sha = str(entry.get("covariance_sha256"))
            checks["covariance_path_matches_runtime"] = covariance_path.resolve() == joint.DESI_FULL_COV_PATH.resolve()
            checks["covariance_sha256_matches"] = covariance_path.is_file() and sha256(covariance_path) == covariance_sha

        state = "PASS" if all(checks.values()) else "FAIL"
        if state == "FAIL":
            blocking.append(axis)
        rows.append(
            {
                "axis": axis,
                "source_id": source_id,
                "state": state,
                "execution_path": str(execution_path.relative_to(ROOT)),
                "execution_sha256": declared_sha,
                "canonical_exact": canonical_exact,
                "checks": checks,
                "derivation": derivation_receipt,
            }
        )

    expected_axes = set(RUNTIME_PATHS)
    axis_set_ok = seen_axes == expected_axes
    if not axis_set_ok:
        blocking.append("AXIS_SET")

    receipt = {
        "schema": "rll.cosmology_joint_execution_contract_receipt.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "state": "PASS" if not blocking else "FAIL",
        "claim_allowed": False,
        "scientific_confirmation": False,
        "source_manifest": str(MANIFEST_PATH.relative_to(ROOT)),
        "source_manifest_schema": manifest.get("schema"),
        "canonical_manifest": str(CANONICAL_PATH.relative_to(ROOT)),
        "expected_axes": sorted(expected_axes),
        "observed_axes": sorted(seen_axes),
        "axis_set_exact": axis_set_ok,
        "bindings": rows,
        "blocking": blocking,
        "F_ok": "Execution bytes, runtime constants, canonical source identities and declared H(z) derivation are mutually consistent." if not blocking else None,
        "F_gap": [] if not blocking else blocking,
        "F_next": "Use this receipt as a prerequisite for scientific fit receipts; keep model-validation claims independently gated.",
    }
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="artifacts/structure-d-falsifier-coverage/joint-input-contract.json")
    args = parser.parse_args()
    receipt = build_receipt()
    out = Path(args.output)
    if not out.is_absolute():
        out = ROOT / out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0 if receipt["state"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
