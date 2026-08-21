#!/usr/bin/env python3
"""Fail-closed validation for append-only RLL scan / proof-of-concept records."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

SCHEMA = "rll.scan_poc_coherence_registry.v1"
SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")


def fail(message: str) -> None:
    raise ValueError(message)


def present(value: Any) -> bool:
    return bool(value.strip()) if isinstance(value, str) else value is not None


def validate_record(record: Any, index: int, seen: set[str]) -> None:
    if not isinstance(record, dict):
        fail(f"records[{index}] must be an object")
    record_id = record.get("id")
    if not isinstance(record_id, str) or not record_id:
        fail(f"records[{index}].id is required")
    if record_id in seen:
        fail(f"duplicate record id: {record_id}")
    seen.add(record_id)
    if record.get("claim_allowed") is not False:
        fail(f"{record_id}: claim_allowed must remain false")
    if record.get("kind") not in {"SCAN", "POC"}:
        fail(f"{record_id}: kind must be SCAN or POC")
    for key in ("recorded_at", "scope", "epistemic_state", "next_gate"):
        if not present(record.get(key)):
            fail(f"{record_id}: {key} is required")
    source = record.get("source")
    if not isinstance(source, dict):
        fail(f"{record_id}: source must be an object")
    if not isinstance(source.get("repository"), str) or "/" not in source["repository"]:
        fail(f"{record_id}: source.repository must be owner/name")
    sha = source.get("git_sha")
    if not isinstance(sha, str) or not SHA40.fullmatch(sha):
        fail(f"{record_id}: source.git_sha must be a 40-character lowercase SHA")
    evidence = record.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        fail(f"{record_id}: evidence must be a non-empty list")
    for item in evidence:
        if not isinstance(item, dict) or not present(item.get("kind")) or not present(item.get("reference")):
            fail(f"{record_id}: each evidence item needs kind and reference")
    poc = record.get("poc")
    if not isinstance(poc, dict):
        fail(f"{record_id}: poc must be an object")
    status = poc.get("status")
    if status not in {"NOT_RUN", "EXECUTED", "BLOCKED"}:
        fail(f"{record_id}: unsupported poc.status")
    if status == "EXECUTED":
        for key in ("command", "environment", "exit_code", "output_sha256"):
            if not present(poc.get(key)):
                fail(f"{record_id}: executed POC requires poc.{key}")
        if not isinstance(poc.get("exit_code"), int):
            fail(f"{record_id}: poc.exit_code must be an integer")
        if not isinstance(poc.get("output_sha256"), str) or not SHA256.fullmatch(poc["output_sha256"]):
            fail(f"{record_id}: poc.output_sha256 must be SHA-256")
    elif not (isinstance(record.get("token_vazio"), str) and record["token_vazio"].startswith("TOKEN_VAZIO_")):
        fail(f"{record_id}: non-executed POC requires explicit TOKEN_VAZIO")


def validate_registry(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    registry = json.loads(raw.decode("utf-8"))
    if not isinstance(registry, dict) or registry.get("schema") != SCHEMA:
        fail(f"schema must be {SCHEMA}")
    if registry.get("append_only") is not True or registry.get("claim_allowed") is not False:
        fail("registry must be append_only=true and claim_allowed=false")
    records = registry.get("records")
    if not isinstance(records, list) or not records:
        fail("registry requires at least one record")
    seen: set[str] = set()
    for index, record in enumerate(records):
        validate_record(record, index, seen)
    return {"decision": "PASS", "records": len(records), "registry_sha256": hashlib.sha256(raw).hexdigest()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(validate_registry(args.registry), sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"SCAN_POC_COHERENCE_BLOCKED: {exc}")
        raise SystemExit(1)
