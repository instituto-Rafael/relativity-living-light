#!/usr/bin/env python3
"""Freeze current Rx source bytes/provenance without inventing missing authority."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

from rx.kernel import dump_json, load_json

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "data/governance/RLL_CURRENT_RX_SOURCE_FREEZE_SPEC_V1.json"
OUT = ROOT / "artifacts/science/provenance/RLL_G0_SOURCE_FREEZE_RECEIPT.json"


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def csv_info(path, provenance_fields):
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        fields = list(reader.fieldnames or [])
    missing = [field for field in provenance_fields if field not in fields]
    nonempty = {
        field: sum(1 for row in rows if str(row.get(field, "")).strip())
        for field in provenance_fields if field in fields
    }
    return {
        "rows": len(rows),
        "columns": fields,
        "missing_provenance_fields": missing,
        "nonempty_provenance_counts": nonempty,
    }


def json_info(path, provenance_fields):
    payload = load_json(path)
    missing = [field for field in provenance_fields if field not in payload]
    return {
        "top_level_keys": sorted(payload),
        "missing_provenance_fields": missing,
    }


def runtime_materialization_info(item):
    binding = item.get("runtime_materialization")
    if not isinstance(binding, dict):
        return None

    receipt_rel = str(binding.get("receipt_path", ""))
    file_key = str(binding.get("file_key", ""))
    if not receipt_rel or not file_key:
        return {"valid": False, "reason": "incomplete_runtime_materialization_binding"}

    receipt_path = ROOT / receipt_rel
    if not receipt_path.is_file():
        return {
            "valid": False,
            "reason": "materialization_receipt_missing",
            "receipt_path": receipt_rel,
        }

    receipt = load_json(receipt_path)
    expected_schema = binding.get("receipt_schema")
    if expected_schema and receipt.get("schema") != expected_schema:
        return {
            "valid": False,
            "reason": "materialization_receipt_schema_mismatch",
            "receipt_path": receipt_rel,
        }

    ready_field = str(binding.get("ready_field", ""))
    if ready_field and receipt.get(ready_field) is not True:
        return {
            "valid": False,
            "reason": "materialization_receipt_not_ready",
            "receipt_path": receipt_rel,
        }

    file_info = (receipt.get("files", {}) or {}).get(file_key)
    if not isinstance(file_info, dict):
        return {
            "valid": False,
            "reason": "materialization_file_key_missing",
            "receipt_path": receipt_rel,
        }

    digest = str(file_info.get("sha256", ""))
    if len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
        return {
            "valid": False,
            "reason": "materialization_sha256_invalid",
            "receipt_path": receipt_rel,
        }

    return {
        "valid": True,
        "receipt_path": receipt_rel,
        "receipt_sha256": sha256(receipt_path),
        "source_file_key": file_key,
        "source_sha256": digest,
        "bytes": file_info.get("bytes"),
        "source_status": file_info.get("status"),
        "source_commit": receipt.get("source_commit"),
        "provider": receipt.get("provider"),
    }


def build(spec_path=SPEC):
    spec = load_json(spec_path)
    if spec.get("schema") != "rll.current_rx_source_freeze_spec.v1":
        raise ValueError("unsupported source freeze spec")
    if spec.get("claim_allowed") is not False:
        raise ValueError("source freeze spec must preserve claim_allowed=false")

    records = []
    blockers = []
    for item in spec.get("inputs", []):
        rel = str(item["path"])
        path = ROOT / rel
        authority = str(item.get("primary_authority_state", "TOKEN_VAZIO"))
        rights = str(item.get("rights_state", "TOKEN_VAZIO"))
        if authority.startswith("TOKEN_VAZIO"):
            blockers.append(item["id"] + ":primary_authority")
        if rights.startswith("TOKEN_VAZIO"):
            blockers.append(item["id"] + ":rights")

        if not path.is_file():
            materialized = runtime_materialization_info(item)
            if materialized and materialized.get("valid"):
                records.append({
                    "id": item["id"],
                    "path": rel,
                    "role": item.get("role"),
                    "local_present": False,
                    "bytes": materialized.get("bytes"),
                    "sha256": materialized["source_sha256"],
                    "expected_rows": item.get("expected_rows"),
                    "observed": {
                        "runtime_materialization": materialized,
                        "missing_provenance_fields": [],
                    },
                    "row_count_matches": True,
                    "primary_authority_state": authority,
                    "rights_state": rights,
                    "state": "RUNTIME_MATERIALIZATION_FROZEN_AUTHORITY_PARTIAL"
                    if any(x.startswith(item["id"] + ":") for x in blockers)
                    else "SOURCE_FROZEN_BY_MATERIALIZATION_RECEIPT",
                })
                continue

            records.append({
                "id": item["id"],
                "path": rel,
                "local_present": False,
                "runtime_materialization": materialized,
                "state": "TOKEN_VAZIO_MISSING_LOCAL_INPUT",
            })
            blockers.append(item["id"] + ":missing_local_input")
            if materialized is not None:
                blockers.append(item["id"] + ":runtime_materialization_invalid")
            continue

        suffix = path.suffix.lower()
        if suffix == ".csv":
            info = csv_info(path, list(item.get("provenance_fields", [])))
            expected_rows = item.get("expected_rows")
            row_match = expected_rows is None or info["rows"] == int(expected_rows)
        elif suffix == ".json":
            info = json_info(path, list(item.get("provenance_fields", [])))
            row_match = True
        else:
            info = {"missing_provenance_fields": []}
            row_match = True

        if info.get("missing_provenance_fields"):
            blockers.append(item["id"] + ":missing_provenance_fields")
        if not row_match:
            blockers.append(item["id"] + ":row_count_mismatch")

        records.append({
            "id": item["id"],
            "path": rel,
            "role": item.get("role"),
            "local_present": True,
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
            "expected_rows": item.get("expected_rows"),
            "observed": info,
            "row_count_matches": row_match,
            "primary_authority_state": authority,
            "rights_state": rights,
            "state": "BYTES_FROZEN_AUTHORITY_PARTIAL" if any(
                x.startswith(item["id"] + ":") for x in blockers
            ) else "SOURCE_FROZEN",
        })

    execution = []
    for rel in spec.get("execution_sources", []):
        path = ROOT / str(rel)
        execution.append({
            "path": str(rel),
            "present": path.is_file(),
            "sha256": sha256(path) if path.is_file() else "TOKEN_VAZIO",
        })
        if not path.is_file():
            blockers.append(str(rel) + ":missing_execution_source")

    return {
        "schema": "rll.g0.source_freeze_receipt.v1",
        "scope": spec.get("scope"),
        "state": "SCI_GATE_G0_PARTIAL_FREEZE" if blockers else "SCI_GATE_G0_SOURCE_FREEZE_READY_FOR_PASS_REVIEW",
        "inputs": records,
        "execution_sources": execution,
        "blockers": sorted(set(blockers)),
        "scientific_gate": "SCI_GATE:G0",
        "scientific_gate_closed": False,
        "claim_allowed": False,
        "boundary": "Local byte custody is evidence of exactly what the program consumes; it does not substitute for missing primary-source or rights authority.",
    }


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--spec", type=Path, default=SPEC)
    parser.add_argument("--output", type=Path, default=OUT)
    args = parser.parse_args(argv)
    spec_path = args.spec if args.spec.is_absolute() else ROOT / args.spec
    output = args.output if args.output.is_absolute() else ROOT / args.output
    payload = build(spec_path)
    if args.write:
        dump_json(output, payload)
    print(json.dumps({
        "state": payload["state"],
        "blocker_count": len(payload["blockers"]),
        "scientific_gate_closed": False,
        "claim_allowed": False,
    }, ensure_ascii=False, indent=2))
    if args.write:
        print("wrote", output.relative_to(ROOT) if output.is_relative_to(ROOT) else output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
