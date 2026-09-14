from __future__ import annotations

import copy
import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "docs" / "contracts" / "intent_ir.schema.json"


def _valid_intent() -> dict:
    return {
        "schema": "rafaelia.intent.v1",
        "intent_id": "intent-001",
        "action": "readonly.repo.audit",
        "target": {"repo": "instituto-Rafael/relativity-living-light"},
        "inputs": [],
        "constraints": ["read_only"],
        "evidence_refs": ["chunk-001"],
        "requested_capabilities": ["git.read", "git.diff"],
        "risk": "low",
        "execution_gate": "allow",
    }


def test_intent_ir_valid_payload_passes() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    payload = _valid_intent()
    Draft202012Validator(schema).validate(payload)


def test_intent_ir_invalid_risk_fails() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    payload = copy.deepcopy(_valid_intent())
    payload["risk"] = "extreme"
    errors = list(Draft202012Validator(schema).iter_errors(payload))
    assert errors
    assert any("is not one of" in error.message for error in errors)
