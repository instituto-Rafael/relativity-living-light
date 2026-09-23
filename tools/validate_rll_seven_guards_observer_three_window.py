#!/usr/bin/env python3
"""Validate the public RLL seven-guard / three-window observation contract.

This validator checks structure and epistemic guardrails only. Passing it does not
promote a scientific claim.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

DEFAULT_CONTRACT = Path("data/contracts/rll_seven_guards_observer_three_window.v1.json")
REQUIRED_GUARDS = {
    "provenance",
    "context",
    "evidence",
    "contradiction",
    "uncertainty",
    "reproduction",
    "rollback",
}
REQUIRED_WINDOWS = [("W0", "entry"), ("W1", "middle"), ("W2", "exit")]
REQUIRED_STATS = {"min", "median", "max"}
REQUIRED_TOKENS = {
    "TOKEN_VAZIO_TWINS_ON_DAGGER",
    "TOKEN_VAZIO_4_OF_5_IN_THREE",
}
REQUIRED_INVARIANTS = {
    "SOURCE != ARTEFACT != EXECUTION != EVIDENCE != CLAIM",
    "TOKEN_VAZIO != 0",
    "ROLLBACK_PRESERVES_CONTRADICTORY_EVIDENCE",
}


def _require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def validate_contract(data: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []

    _require(data.get("schema") == "rll.seven_guards_observer_three_window.v1", "schema mismatch", errors)
    _require(data.get("claim_allowed") is False, "claim_allowed must remain false", errors)
    _require(data.get("scientific_confirmation") is False, "scientific_confirmation must remain false", errors)

    invariants = set(data.get("invariants", []))
    _require(REQUIRED_INVARIANTS <= invariants, "required epistemic invariants missing", errors)

    guards = data.get("guards", {})
    _require(set(guards) == REQUIRED_GUARDS, "guard set must be exactly the seven declared guards", errors)
    for name in REQUIRED_GUARDS:
        guard = guards.get(name, {})
        _require(guard.get("required") is True, f"guard {name} must be required", errors)
        minimum = guard.get("minimum", [])
        _require(isinstance(minimum, list) and len(minimum) > 0, f"guard {name} needs minimum fields", errors)

    windows = data.get("windows", [])
    _require(len(windows) == 3, "exactly three windows are required", errors)
    for index, (window_id, role_token) in enumerate(REQUIRED_WINDOWS):
        if index >= len(windows):
            break
        window = windows[index]
        _require(window.get("id") == window_id, f"window {index} must be {window_id}", errors)
        _require(role_token in str(window.get("role", "")), f"{window_id} role must include {role_token}", errors)
        _require(window.get("predeclared") is True, f"{window_id} must be predeclared", errors)
        _require(window.get("required_locator") is True, f"{window_id} must require a locator", errors)

    required_stats = set(data.get("statistics", {}).get("required", []))
    _require(REQUIRED_STATS <= required_stats, "min/median/max statistics are required", errors)

    selection = data.get("selection_policy", {})
    _require(selection.get("best_of_three_post_hoc_allowed") is False, "post-hoc best-of-three must be blocked", errors)
    _require(selection.get("predeclared_selection_rule_required") is True, "predeclared selection rule must be required", errors)

    observer = data.get("observer_model", {})
    _require(observer.get("consciousness_required_for_physical_claim") is False, "consciousness-collapse claim must remain blocked", errors)

    unresolved = set(data.get("unresolved_author_tokens", []))
    _require(REQUIRED_TOKENS <= unresolved, "unresolved author tokens must remain TOKEN_VAZIO", errors)

    rollback = guards.get("rollback", {})
    _require("history_preserved" in rollback.get("minimum", []), "rollback must preserve history", errors)

    output = set(data.get("required_round_output", []))
    _require(REQUIRED_GUARDS <= output, "round output must expose all seven guards", errors)
    _require("R3" in output and "claim_allowed" in output, "round output must include R3 and claim_allowed", errors)

    return {
        "schema": "rll.seven_guards_observer_three_window.validation.v1",
        "valid": not errors,
        "claim_allowed": False,
        "scientific_confirmation": False,
        "errors": errors,
        "checked_guards": sorted(REQUIRED_GUARDS),
        "checked_windows": [item[0] for item in REQUIRED_WINDOWS],
        "boundary": "STRUCTURAL_PASS != SCIENTIFIC_CONFIRMATION",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--json", action="store_true", help="emit JSON only")
    args = parser.parse_args()

    data = json.loads(args.contract.read_text(encoding="utf-8"))
    result = validate_contract(data)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
