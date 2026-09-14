#!/usr/bin/env python3
"""Validate the finite, claim-bounded scientific infinity cycle contract."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    from jsonschema import Draft202012Validator
    from jsonschema.exceptions import SchemaError
except ModuleNotFoundError as exc:  # pragma: no cover
    raise SystemExit(
        "scientific infinity validation failed: install jsonschema"
    ) from exc

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "scientific_infinity_cycle.schema.json"
EXAMPLE_PATH = ROOT / "schemas" / "examples" / "scientific_infinity_cycle.example.json"


def fail(message: str) -> None:
    raise SystemExit(f"scientific infinity validation failed: {message}")


def load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"missing file: {path.relative_to(ROOT)}")
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path.relative_to(ROOT)}: {exc}")
    if not isinstance(value, dict):
        fail(f"top-level JSON must be an object: {path.relative_to(ROOT)}")
    return value


def validate_semantics(schema: dict[str, Any], example: dict[str, Any]) -> None:
    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as exc:
        fail(f"invalid Draft 2020-12 schema: {exc.message}")

    errors = sorted(
        Draft202012Validator(schema).iter_errors(example),
        key=lambda error: tuple(str(part) for part in error.absolute_path),
    )
    if errors:
        error = errors[0]
        fail(f"example violates schema at {list(error.absolute_path)}: {error.message}")

    if example.get("claim_allowed") is not False:
        fail("claim_allowed must remain false")
    scope = example.get("execution_scope", {})
    if scope.get("mode") != "finite_budgeted":
        fail("execution scope must be finite_budgeted")
    classes = example.get("infinity_classes", [])
    if "TOKEN_VAZIO" not in classes:
        fail("example must preserve TOKEN_VAZIO")
    if "infinity_physical" in classes and example.get("decision") == "converged":
        fail("structural convergence cannot close a physical-infinity claim")

    observations = example.get("observations", [])
    iterations = [item.get("iteration") for item in observations]
    if iterations != list(range(len(iterations))):
        fail("example observations must use contiguous zero-based iterations")
    digests = [item.get("state_digest") for item in observations]
    if len(digests) != len(set(digests)):
        fail("example contains a repeated state digest but does not declare cycle_detected")

    boundary = str(example.get("claim_boundary", "")).lower()
    for marker in ("does not prove", "finite"):
        if marker not in boundary:
            fail(f"claim_boundary missing marker: {marker}")


def main() -> int:
    schema = load(SCHEMA_PATH)
    example = load(EXAMPLE_PATH)
    validate_semantics(schema, example)
    print("OK: scientific infinity cycle is finite, structurally valid and claim-bounded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
