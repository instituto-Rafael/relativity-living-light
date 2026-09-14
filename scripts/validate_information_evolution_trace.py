#!/usr/bin/env python3
"""Validate the claim-bounded information evolution trace contract and fixture.

The validator performs two independent checks:

1. full JSON Schema Draft 2020-12 validation, including RFC 3339 date-time formats;
2. repository-specific semantic invariants that JSON Schema cannot express,
   such as contiguous state transitions and a pending external-validity gate.

Passing this validator establishes structural conformance only. It does not
establish scientific truth, historical provenance or external validity.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    import rfc3339_validator  # noqa: F401 - proves date-time validation support exists
    from jsonschema import Draft202012Validator, FormatChecker
    from jsonschema.exceptions import SchemaError
except ModuleNotFoundError as exc:  # pragma: no cover - deployment guard
    raise SystemExit(
        "information evolution trace validation failed: missing JSON Schema format "
        "dependencies; install them with \"pip install 'jsonschema[format]'\""
    ) from exc

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "information_evolution_trace.schema.json"
EXAMPLE_PATH = ROOT / "schemas" / "examples" / "information_evolution_trace.example.json"

EXPECTED_REQUIRED = {
    "trace_id",
    "schema_version",
    "artifact_type",
    "origin_status",
    "first_observable_state",
    "current_state",
    "transformations",
    "epistemic_status",
    "claim_allowed",
    "next_gate",
}


def fail(message: str) -> None:
    raise SystemExit(f"information evolution trace validation failed: {message}")


def load_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"missing file: {path.relative_to(ROOT)}")
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path.relative_to(ROOT)}: {exc}")
    if not isinstance(payload, dict):
        fail(f"top-level JSON must be an object: {path.relative_to(ROOT)}")
    return payload


def validate_schema(schema: dict[str, Any]) -> None:
    for key in ("$schema", "$id", "title", "description", "type", "required", "properties"):
        if key not in schema:
            fail(f"schema missing {key}")

    if schema["type"] != "object":
        fail("schema top-level type must be object")

    required = schema.get("required")
    if not isinstance(required, list):
        fail("schema required must be a list")

    missing = EXPECTED_REQUIRED - set(required)
    if missing:
        fail(f"schema missing required fields: {sorted(missing)}")

    properties = schema.get("properties")
    if not isinstance(properties, dict):
        fail("schema properties must be an object")

    claim_gate = properties.get("claim_allowed")
    if not isinstance(claim_gate, dict) or claim_gate.get("const") is not False:
        fail("claim_allowed must be const false")

    origin_status = properties.get("origin_status")
    if not isinstance(origin_status, dict):
        fail("origin_status property is missing")
    origin_enum = origin_status.get("enum")
    if not isinstance(origin_enum, list) or "TOKEN_VAZIO" not in origin_enum:
        fail("origin_status must preserve TOKEN_VAZIO")

    description = str(schema.get("description", "")).lower()
    for marker in ("structural contract", "does not establish"):
        if marker not in description:
            fail(f"schema description missing boundary marker: {marker}")

    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as exc:
        fail(f"invalid Draft 2020-12 schema: {exc.message}")


def format_json_path(parts: list[Any]) -> str:
    if not parts:
        return "$"
    return "$" + "".join(
        f"[{part}]" if isinstance(part, int) else f".{part}"
        for part in parts
    )


def validate_instance_against_schema(
    schema: dict[str, Any],
    instance: dict[str, Any],
) -> None:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(
        validator.iter_errors(instance),
        key=lambda error: tuple(str(part) for part in error.absolute_path),
    )
    if not errors:
        return

    first = errors[0]
    path = format_json_path(list(first.absolute_path))
    fail(f"fixture violates JSON Schema at {path}: {first.message}")


def repository_references(payload: Any) -> list[str]:
    found: list[str] = []
    if isinstance(payload, dict):
        if payload.get("kind") == "repository_path":
            locator = payload.get("locator")
            if isinstance(locator, str):
                found.append(locator)
        for value in payload.values():
            found.extend(repository_references(value))
    elif isinstance(payload, list):
        for value in payload:
            found.extend(repository_references(value))
    return found


def validate_example(example: dict[str, Any]) -> None:
    missing = EXPECTED_REQUIRED - set(example)
    if missing:
        fail(f"example missing fields: {sorted(missing)}")

    if example.get("claim_allowed") is not False:
        fail("example claim_allowed must be false")

    if example.get("origin_status") != "TOKEN_VAZIO":
        fail("didactic example must preserve unknown origin as TOKEN_VAZIO")

    first = example.get("first_observable_state")
    current = example.get("current_state")
    transformations = example.get("transformations")

    if not isinstance(first, dict) or not isinstance(current, dict):
        fail("first_observable_state and current_state must be objects")
    if not isinstance(transformations, list) or not transformations:
        fail("example must contain at least one transformation")

    cursor = first.get("state_id")
    if not isinstance(cursor, str) or not cursor:
        fail("first observable state has no state_id")

    saw_passed_internal = False
    saw_pending_external = False

    for index, transformation in enumerate(transformations):
        if not isinstance(transformation, dict):
            fail(f"transformation {index} must be an object")
        if transformation.get("from_state") != cursor:
            fail(
                f"transformation {index} breaks chain: "
                f"expected from_state={cursor!r}, found {transformation.get('from_state')!r}"
            )

        to_state = transformation.get("to_state")
        if not isinstance(to_state, str) or not to_state or to_state == cursor:
            fail(f"transformation {index} has invalid to_state")

        decision = transformation.get("decision")
        if decision not in {"retain", "revise", "reject", "rollback"}:
            fail(f"transformation {index} has unsupported decision: {decision!r}")

        tests = transformation.get("tests")
        if not isinstance(tests, list):
            fail(f"transformation {index} tests must be a list")

        for test in tests:
            if not isinstance(test, dict):
                fail(f"transformation {index} contains a non-object test")
            result = test.get("result")
            external = test.get("external_baseline")
            reproducible = test.get("reproducible")
            if external is False and result == "passed" and reproducible is True:
                saw_passed_internal = True
            if external is True and result in {"not_run", "inconclusive"}:
                saw_pending_external = True

        cursor = to_state

    if cursor != current.get("state_id"):
        fail(
            "transformation chain does not terminate at current_state: "
            f"ended at {cursor!r}, current is {current.get('state_id')!r}"
        )

    if example.get("epistemic_status") != "internally_traceable":
        fail("example must remain at internally_traceable status")

    if not saw_passed_internal:
        fail("example must include a passed reproducible internal structural test")
    if not saw_pending_external:
        fail("example must keep an external validity gate pending")

    blocked_claims = example.get("blocked_claims")
    if not isinstance(blocked_claims, list) or not blocked_claims:
        fail("example must declare blocked claims")

    next_gate = example.get("next_gate")
    if not isinstance(next_gate, str) or not next_gate.strip():
        fail("example must declare a non-empty next_gate")

    for locator in repository_references(example):
        path = ROOT / locator
        if not path.exists():
            fail(f"repository_path reference does not exist: {locator}")


def main() -> int:
    schema = load_object(SCHEMA_PATH)
    example = load_object(EXAMPLE_PATH)
    validate_schema(schema)
    validate_instance_against_schema(schema, example)
    validate_example(example)
    print(
        "OK: information evolution trace is Draft 2020-12 valid, "
        "contiguous and claim-bounded"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
