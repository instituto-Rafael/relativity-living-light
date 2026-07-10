#!/usr/bin/env python3
"""Validate RAFAELIA semantic-governance schema contracts.

Uses only the Python standard library. It checks schema structure and the
invariants that JSON Schema alone does not express clearly in this repository's
lightweight CI contract.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "schemas"
EXAMPLE_DIR = SCHEMA_DIR / "examples"
SEMANTIC_SCHEMA = SCHEMA_DIR / "semantic_token_unit.schema.json"
FORMAL_SCHEMA = SCHEMA_DIR / "formal_treatment_record.schema.json"
SEMANTIC_EXAMPLE = EXAMPLE_DIR / "semantic_token_unit.pulley_ramp.example.json"
FORMAL_EXAMPLE = EXAMPLE_DIR / "formal_treatment_record.token_vazio.example.json"

SEVEN_VIEWS = (
    "d1_lexical_structure",
    "d2_entity_domain",
    "d3_relational_isogonic",
    "d4_antagonic_constraints",
    "d5_causal_temporal",
    "d6_epistemic_gap",
    "d7_operational_governance",
)
USE_POLICY_FIELDS = {"privacy", "training_eligibility", "retention", "purpose", "owner"}
SEMANTIC_REQUIRED = {"unit_id", "raw_span", "lexical_tokens", "views_7d", "evidence_refs", "uncertainty", "epistemic_status", "use_policy", "created_at"}
FORMAL_REQUIRED = {"record_id", "name", "family", "artifact_type", "nature", "status", "origin", "evidence", "risk", "relations", "next_action", "execution_gate", "created_at", "updated_at"}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: top-level JSON value must be an object")
    return payload


def assert_schema_header(path: Path, payload: dict[str, Any]) -> None:
    for field in ("$schema", "$id", "title", "description", "type"):
        if field not in payload:
            raise ValueError(f"{path.name}: missing schema header {field}")
    if payload["type"] != "object":
        raise ValueError(f"{path.name}: top-level schema type must be object")


def assert_required_fields(name: str, actual: set[str], expected: set[str]) -> None:
    missing = expected - actual
    if missing:
        raise ValueError(f"{name}: missing required fields: {sorted(missing)}")


def validate_schema_contracts() -> None:
    semantic = load_json(SEMANTIC_SCHEMA)
    formal = load_json(FORMAL_SCHEMA)
    assert_schema_header(SEMANTIC_SCHEMA, semantic)
    assert_schema_header(FORMAL_SCHEMA, formal)
    assert_required_fields(SEMANTIC_SCHEMA.name, set(semantic.get("required", [])), SEMANTIC_REQUIRED)
    assert_required_fields(FORMAL_SCHEMA.name, set(formal.get("required", [])), FORMAL_REQUIRED)

    view_schema = semantic["properties"]["views_7d"]
    actual_views = tuple(view_schema.get("required", []))
    if actual_views != SEVEN_VIEWS:
        raise ValueError("semantic_token_unit.schema.json: views_7d must contain the canonical ordered seven directions")
    if set(view_schema.get("properties", {})) != set(SEVEN_VIEWS):
        raise ValueError("semantic_token_unit.schema.json: views_7d properties must be exactly the canonical seven directions")

    policy_required = set(semantic["properties"]["use_policy"].get("required", []))
    assert_required_fields("semantic_token_unit.schema.json use_policy", policy_required, USE_POLICY_FIELDS)


def validate_use_policy(name: str, policy: dict[str, Any]) -> None:
    assert_required_fields(name, set(policy), USE_POLICY_FIELDS)
    training = policy["training_eligibility"]
    purpose = policy["purpose"]
    if training == "yes_explicit" and purpose != "training_explicit":
        raise ValueError(f"{name}: yes_explicit training requires purpose=training_explicit")
    if purpose == "training_explicit" and training != "yes_explicit":
        raise ValueError(f"{name}: purpose=training_explicit requires yes_explicit training")


def validate_semantic_example(payload: dict[str, Any]) -> None:
    assert_required_fields(SEMANTIC_EXAMPLE.name, set(payload), SEMANTIC_REQUIRED)
    views = payload["views_7d"]
    if tuple(views) != SEVEN_VIEWS:
        raise ValueError(f"{SEMANTIC_EXAMPLE.name}: expected ordered seven directions, found {tuple(views)}")
    gap = views["d6_epistemic_gap"]
    if gap["token_vazio"]:
        if payload["epistemic_status"] != "gap":
            raise ValueError(f"{SEMANTIC_EXAMPLE.name}: TOKEN_VAZIO requires status=gap")
        if not gap["missing_variables"]:
            raise ValueError(f"{SEMANTIC_EXAMPLE.name}: TOKEN_VAZIO requires missing variables")
    if not 0 <= payload["uncertainty"] <= 1:
        raise ValueError(f"{SEMANTIC_EXAMPLE.name}: uncertainty must be between 0 and 1")
    validate_use_policy(f"{SEMANTIC_EXAMPLE.name} use_policy", payload["use_policy"])


def validate_formal_example(payload: dict[str, Any]) -> None:
    assert_required_fields(FORMAL_EXAMPLE.name, set(payload), FORMAL_REQUIRED)
    validate_use_policy(f"{FORMAL_EXAMPLE.name} use_policy", payload["use_policy"])
    if payload["artifact_type"] == "token_vazio":
        if payload["status"] != "gap":
            raise ValueError(f"{FORMAL_EXAMPLE.name}: token_vazio requires status=gap")
        if payload["execution_gate"] not in {"blocked", "human_review"}:
            raise ValueError(f"{FORMAL_EXAMPLE.name}: token_vazio cannot execute directly")
        if not payload.get("token_vazio_reason"):
            raise ValueError(f"{FORMAL_EXAMPLE.name}: token_vazio requires a reason")


def validate_examples() -> None:
    validate_semantic_example(load_json(SEMANTIC_EXAMPLE))
    validate_formal_example(load_json(FORMAL_EXAMPLE))


def main() -> int:
    validate_schema_contracts()
    validate_examples()
    for path in (SEMANTIC_SCHEMA, FORMAL_SCHEMA, SEMANTIC_EXAMPLE, FORMAL_EXAMPLE):
        print(f"OK: {path.relative_to(ROOT)}")
    print("OK: semantic-governance 7D schema layer passed validation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
