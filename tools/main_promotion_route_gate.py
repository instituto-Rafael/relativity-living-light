#!/usr/bin/env python3
"""Fail-closed gate for the canonical RLL promotion edge into main.

This gate validates repository branch-routing only. It does not validate scientific
claims, external branch-protection settings, or publication readiness.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


def norm(ref: str) -> str:
    value = (ref or "").strip()
    for prefix in ("refs/heads/", "origin/"):
        if value.startswith(prefix):
            return value[len(prefix):]
    return value


def evaluate(head_ref: str, base_ref: str) -> dict:
    head = norm(head_ref)
    base = norm(base_ref)
    residuals: list[str] = []

    if base != "main":
        residuals.append(f"UNSUPPORTED_BASE:{base or 'EMPTY'}")
    if head != "rll/release":
        residuals.append(f"MAIN_REQUIRES_RLL_RELEASE_HEAD:{head or 'EMPTY'}")

    return {
        "schema": "rll.main_promotion_route_gate.v1",
        "head_ref": head,
        "base_ref": base,
        "expected_edge": "rll/release -> main",
        "decision": "PASS" if not residuals else "BLOCKED",
        "residuals": residuals,
        "claim_allowed": False,
        "publication_effect": "NONE",
        "branch_protection_verified": False,
        "external_settings": "TOKEN_VAZIO_EXTERNAL_SETTINGS",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--head-ref", required=True)
    parser.add_argument("--base-ref", required=True)
    parser.add_argument(
        "--output",
        default="artifacts/main-promotion-route/receipt.json",
    )
    args = parser.parse_args()

    receipt = evaluate(args.head_ref, args.base_ref)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if receipt["decision"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
