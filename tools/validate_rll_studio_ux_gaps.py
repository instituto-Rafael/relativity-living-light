#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "data/governance/RLL_STUDIO_UX_GAPS_V1.json"
ALLOWED_PRIORITIES = {"P0", "P1", "P2"}
ALLOWED_STATES = {"PASS", "READY_FOR_CI", "OBSERVED_LIMITED", "TOKEN_VAZIO", "BLOCKED"}


def validate() -> list[str]:
    errors: list[str] = []
    data = json.loads(LEDGER.read_text(encoding="utf-8"))
    if data.get("schema") != "rll_studio_ux_gap_ledger_v1":
        errors.append("schema mismatch")
    if data.get("claim_allowed") is not False:
        errors.append("claim_allowed must be false")
    if data.get("automatic_promotion") is not False:
        errors.append("automatic_promotion must be false")
    seen: set[str] = set()
    for item in data.get("items", []):
        item_id = item.get("id")
        if not item_id or item_id in seen:
            errors.append(f"duplicate/missing id: {item_id}")
        seen.add(item_id)
        if item.get("priority") not in ALLOWED_PRIORITIES:
            errors.append(f"invalid priority: {item_id}")
        if item.get("state") not in ALLOWED_STATES:
            errors.append(f"invalid state: {item_id}")
        if not item.get("authority"):
            errors.append(f"missing authority: {item_id}")
        if not item.get("closure_test"):
            errors.append(f"missing closure_test: {item_id}")
        if not item.get("next_producer"):
            errors.append(f"missing next_producer: {item_id}")
        state = item.get("state")
        token = str(item.get("token", ""))
        if state in {"TOKEN_VAZIO", "READY_FOR_CI", "BLOCKED"} and not token.startswith("TOKEN_VAZIO"):
            errors.append(f"open state must retain TOKEN_VAZIO: {item_id}")
        if state == "PASS" and not item.get("evidence"):
            errors.append(f"PASS requires evidence: {item_id}")
    if not any(item.get("priority") == "P0" for item in data.get("items", [])):
        errors.append("at least one P0 required")
    return errors


if __name__ == "__main__":
    issues = validate()
    if issues:
        print(json.dumps({"state": "FAIL", "claim_allowed": False, "errors": issues}, indent=2))
        raise SystemExit(1)
    print(json.dumps({"state": "PASS", "claim_allowed": False, "ledger": str(LEDGER.relative_to(ROOT))}, indent=2))
