#!/usr/bin/env python3
"""Validate the machine-readable RLL claim authority export."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPORT = ROOT / "docs" / "audits" / "RLL_CLAIM_AUTHORITY_EXPORT.json"
ALLOWED = {
    "VERIFIED",
    "VERIFIED_LIMITED",
    "DECLARED_BY_AUTHOR",
    "HYPOTHESIS",
    "TOKEN_VAZIO",
    "CONTRADICTION",
    "CLAIM_BLOCKED",
}
REQUIRED = {
    "claim_id",
    "statement",
    "state",
    "scope",
    "source_path",
    "source_ref",
    "source_blob_sha",
    "not_claimed",
    "claim_allowed",
}


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    try:
        data = json.loads(EXPORT.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot read export: {exc}")

    if data.get("producer") != "rafaelmeloreisnovo/relativity-living-light":
        fail("unexpected producer")
    if data.get("canonical_domain") != "rll_scientific_validation":
        fail("unexpected canonical domain")
    if data.get("claim_allowed") is not False:
        fail("top-level claim_allowed must be false")

    claims = data.get("claims")
    if not isinstance(claims, list) or not claims:
        fail("claims must be a non-empty list")

    seen: set[str] = set()
    for index, claim in enumerate(claims):
        if not isinstance(claim, dict):
            fail(f"claim {index} must be an object")
        missing = REQUIRED - claim.keys()
        if missing:
            fail(f"claim {index} missing {sorted(missing)}")
        claim_id = claim["claim_id"]
        if claim_id in seen:
            fail(f"duplicate claim_id: {claim_id}")
        seen.add(claim_id)
        if claim["state"] not in ALLOWED:
            fail(f"invalid state for {claim_id}: {claim['state']}")
        if claim["claim_allowed"] is not False:
            fail(f"{claim_id} must remain claim_allowed=false")
        if not isinstance(claim["not_claimed"], list) or not claim["not_claimed"]:
            fail(f"{claim_id}.not_claimed must be non-empty")
        source = ROOT / claim["source_path"]
        if not source.is_file():
            fail(f"source_path not found for {claim_id}: {claim['source_path']}")
        blob_sha = claim["source_blob_sha"]
        if not isinstance(blob_sha, str) or len(blob_sha) != 40:
            fail(f"invalid source_blob_sha for {claim_id}")

    print(
        json.dumps(
            {
                "status": "PASS",
                "producer": data["producer"],
                "claims": len(claims),
                "claim_allowed": False,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
