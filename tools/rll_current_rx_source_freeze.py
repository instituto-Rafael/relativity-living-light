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


def build():
    spec = load_json(SPEC)
    if spec.get("schema") != "rll.current_rx_source_freeze_spec.v1":
        raise ValueError("unsupported source freeze spec")
    if spec.get("claim_allowed") is not False:
        raise ValueError("source freeze spec must preserve claim_allowed=false")

    records = []
    blockers = []
    for item in spec.get("inputs", []):
        rel = str(item["path"])
        path = ROOT / rel
        if not path.is_file():
            records.append({
                "id": item["id"],
                "path": rel,
                "state": "TOKEN_VAZIO_MISSING_LOCAL_INPUT",
            })
            blockers.append(item["id"] + ":missing_local_input")
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

        authority = str(item.get("primary_authority_state", "TOKEN_VAZIO"))
        rights = str(item.get("rights_state", "TOKEN_VAZIO"))
        if authority.startswith("TOKEN_VAZIO"):
            blockers.append(item["id"] + ":primary_authority")
        if rights.startswith("TOKEN_VAZIO"):
            blockers.append(item["id"] + ":rights")
        if info.get("missing_provenance_fields"):
            blockers.append(item["id"] + ":missing_provenance_fields")
        if not row_match:
            blockers.append(item["id"] + ":row_count_mismatch")

        records.append({
            "id": item["id"],
            "path": rel,
            "role": item.get("role"),
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
    args = parser.parse_args(argv)
    payload = build()
    if args.write:
        dump_json(OUT, payload)
    print(json.dumps({
        "state": payload["state"],
        "blocker_count": len(payload["blockers"]),
        "scientific_gate_closed": False,
        "claim_allowed": False,
    }, ensure_ascii=False, indent=2))
    if args.write:
        print("wrote", OUT.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
