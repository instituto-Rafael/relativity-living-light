from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_information_evolution_trace.py"


def load_validator():
    spec = importlib.util.spec_from_file_location(
        "validate_information_evolution_trace",
        VALIDATOR,
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_contract(module):
    schema = module.load_object(module.SCHEMA_PATH)
    example = module.load_object(module.EXAMPLE_PATH)
    return schema, example


def test_information_evolution_trace_validator_passes() -> None:
    module = load_validator()
    assert module.main() == 0


def test_schema_rejects_claim_promotion() -> None:
    module = load_validator()
    schema, example = load_contract(module)
    promoted = copy.deepcopy(example)
    promoted["claim_allowed"] = True

    with pytest.raises(SystemExit, match="fixture violates JSON Schema"):
        module.validate_instance_against_schema(schema, promoted)


def test_schema_rejects_invalid_datetime_format() -> None:
    module = load_validator()
    schema, example = load_contract(module)
    malformed = copy.deepcopy(example)
    malformed["current_state"]["timestamp"] = "11/07/2026 13:00"

    with pytest.raises(SystemExit, match="date-time"):
        module.validate_instance_against_schema(schema, malformed)


def test_semantic_validator_rejects_broken_state_chain() -> None:
    module = load_validator()
    _, example = load_contract(module)
    broken = copy.deepcopy(example)
    broken["transformations"][0]["from_state"] = "state-does-not-exist"

    with pytest.raises(SystemExit, match="breaks chain"):
        module.validate_example(broken)


def test_semantic_validator_requires_pending_external_gate() -> None:
    module = load_validator()
    _, example = load_contract(module)
    closed_too_early = copy.deepcopy(example)
    external_test = closed_too_early["transformations"][0]["tests"][1]
    external_test["result"] = "passed"
    external_test["reproducible"] = True

    with pytest.raises(SystemExit, match="external validity gate pending"):
        module.validate_example(closed_too_early)
