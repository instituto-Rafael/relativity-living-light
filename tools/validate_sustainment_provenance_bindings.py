#!/usr/bin/env python3
"""Verify declared provenance bindings against actual repository file bytes.

A 40-hex string is not provenance by itself. This gate recomputes Git's blob
object identity (`sha1("blob <len>\\0" + bytes)`) for every bound source and
requires exact equality with the registry. It also verifies later-evidence
bindings in the dataset-rights reconciliation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "governance/ethics_license_complexity_sustainment.v1.json"
RIGHTS = ROOT / "data/contracts/dataset_rights_reconciliation_20260822.v1.json"


def git_blob_sha1(path: Path) -> str:
    payload = path.read_bytes()
    header = f"blob {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected object")
    return value


def _verify(path_text: str, expected: str, label: str, root: Path) -> dict[str, str]:
    path = root / path_text
    if not path.is_file():
        raise ValueError(f"{label}: missing bound file {path_text}")
    actual = git_blob_sha1(path)
    if actual != expected:
        raise ValueError(
            f"{label}: Git blob provenance mismatch for {path_text}: "
            f"expected={expected} actual={actual}"
        )
    return {"path": path_text, "expected_git_blob_sha1": expected, "actual_git_blob_sha1": actual}


def build_report(root: Path = ROOT) -> dict[str, Any]:
    registry = _load(root / REGISTRY.relative_to(ROOT))
    rights = _load(root / RIGHTS.relative_to(ROOT))
    bindings: list[dict[str, str]] = []

    for item in registry["source_bindings"]:
        result = _verify(item["path"], item["git_blob_sha1"], item["artifact_id"], root)
        result["binding_id"] = item["artifact_id"]
        result["binding_class"] = "SUSTAINMENT_SOURCE"
        bindings.append(result)

    predecessor = rights["predecessor"]
    result = _verify(
        predecessor["path"], predecessor["git_blob_sha1"], "RIGHTS_PREDECESSOR", root
    )
    result["binding_id"] = "RIGHTS_PREDECESSOR"
    result["binding_class"] = "APPEND_ONLY_PREDECESSOR"
    bindings.append(result)

    for event in rights["later_evidence"]:
        result = _verify(event["path"], event["git_blob_sha1"], event["event_id"], root)
        result["binding_id"] = event["event_id"]
        result["binding_class"] = "LATER_EVIDENCE"
        bindings.append(result)

    ids = [item["binding_id"] for item in bindings]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate provenance binding ID")

    return {
        "schema": "rll.sustainment_provenance_binding_receipt.v1",
        "state": "PASS_EXACT_GIT_BLOB_BINDINGS",
        "claim_allowed": False,
        "scientific_confirmation": False,
        "legal_effect_claim": False,
        "binding_count": len(bindings),
        "bindings": sorted(bindings, key=lambda item: item["binding_id"]),
        "boundary": "exact Git blob identity proves which repository bytes were bound; it does not prove scientific truth, authorship entitlement, third-party permission or legal enforceability",
        "F_ok": [
            "all declared source bindings match actual Git blob identities",
            "rights predecessor identity is exact",
            "later rights evidence identities are exact"
        ],
        "F_gap": [],
        "F_next": "retain exact bindings in every successor; if a source changes, add/version a new binding instead of silently relabeling the historical one"
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = build_report(ROOT)
    payload = json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
