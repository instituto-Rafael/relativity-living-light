#!/usr/bin/env python3
"""Validate the discrete-ontology factor-11 claim ledger.

The validator is executable directly from the repository root. It validates the
JSON Schema contract, semantic invariants, and the runtime factor-11 claim gate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rll.discrete_ontology import ClaimState, evaluate_factor11_gate  # noqa: E402


DEFAULT_LEDGER = ROOT / "data/epistemic_void/factor11_discrete_ontology.json"
DEFAULT_SCHEMA = ROOT / "schemas/discrete_ontology_claim.schema.json"
DEFAULT_REPORT = ROOT / "artifacts/discrete-ontology/discrete_ontology_report.json"


class ValidationError(ValueError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    _require(isinstance(payload, dict), f"{path} must contain a JSON object")
    return payload


def _validate_schema(payload: dict[str, Any], schema: dict[str, Any]) -> None:
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(payload), key=lambda error: list(error.absolute_path))
    if errors:
        details = "; ".join(
            f"/{'/'.join(str(part) for part in error.absolute_path)}: {error.message}"
            for error in errors
        )
        raise ValidationError(f"JSON Schema validation failed: {details}")


def validate_payload(payload: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    checks: list[str] = []

    _validate_schema(payload, schema)
    checks.append("json_schema_draft_2020_12")

    _require(payload.get("schema_version") == "1.0", "schema_version must be 1.0")
    checks.append("schema_version")
    _require(payload.get("id") == "EV-ONTOLOGY-FACTOR11-001", "unexpected ledger id")
    checks.append("stable_id")
    _require(payload.get("state") == ClaimState.TOKEN_VAZIO.value, "state must remain TOKEN_VAZIO")
    checks.append("token_vazio_state")
    _require(payload.get("claim_allowed") is False, "claim_allowed must remain false")
    checks.append("claim_block")

    exact_claims = payload.get("exact_claims")
    _require(isinstance(exact_claims, list) and len(exact_claims) >= 3, "exact_claims must contain at least 3 items")
    ids = [item.get("id") for item in exact_claims if isinstance(item, dict)]
    _require(len(ids) == len(set(ids)), "exact claim ids must be unique")
    _require(all(item.get("state") == ClaimState.PASS_EXACT.value for item in exact_claims), "all exact claims must be PASS_EXACT")
    checks.extend(["exact_claim_count", "exact_claim_unique_ids", "exact_claim_states"])

    physical_bridge = payload.get("physical_bridge")
    _require(isinstance(physical_bridge, dict), "physical_bridge must be an object")
    _require(physical_bridge.get("state") == ClaimState.TOKEN_VAZIO.value, "physical bridge must remain TOKEN_VAZIO")
    prohibited = physical_bridge.get("prohibited_claims")
    unknowns = physical_bridge.get("unknowns")
    _require(isinstance(prohibited, list) and prohibited, "prohibited_claims must be non-empty")
    _require(isinstance(unknowns, list) and unknowns, "unknowns must be non-empty")
    checks.extend(["physical_bridge_state", "prohibited_claims", "unknowns"])

    exit_conditions = payload.get("exit_conditions")
    _require(isinstance(exit_conditions, list) and len(exit_conditions) >= 6, "at least 6 exit conditions are required")
    for index, item in enumerate(exit_conditions):
        _require(isinstance(item, dict), f"exit_conditions[{index}] must be an object")
        _require(bool(item.get("evidence_required")), f"exit_conditions[{index}] missing evidence_required")
        _require(bool(item.get("acceptance_criterion")), f"exit_conditions[{index}] missing acceptance_criterion")
    checks.append("exit_conditions")

    gate = evaluate_factor11_gate()
    _require(gate.mathematical_state is ClaimState.PASS_EXACT, "arithmetic gate must pass exactly")
    _require(gate.physical_coupling_state is ClaimState.TOKEN_VAZIO, "physical gate must remain TOKEN_VAZIO")
    _require(gate.claim_allowed is False, "runtime gate must block claim promotion")
    checks.extend(["runtime_arithmetic_gate", "runtime_physical_gate", "runtime_claim_block"])

    return checks


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    _require(args.ledger.is_file(), f"ledger not found: {args.ledger}")
    _require(args.schema.is_file(), f"schema not found: {args.schema}")
    payload = _load_json(args.ledger)
    schema = _load_json(args.schema)

    checks = validate_payload(payload, schema)
    ledger_bytes = args.ledger.read_bytes()
    report = {
        "status": "PASS",
        "claim_allowed": False,
        "state": ClaimState.TOKEN_VAZIO.value,
        "checks_total": len(checks),
        "checks": checks,
        "ledger": str(args.ledger.relative_to(ROOT)),
        "schema": str(args.schema.relative_to(ROOT)),
        "ledger_sha256": hashlib.sha256(ledger_bytes).hexdigest(),
        "factor11_gate": evaluate_factor11_gate().to_dict(),
    }

    if args.write_report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
