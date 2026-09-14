from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "validate_semantic_governance_schemas.py"
spec = importlib.util.spec_from_file_location("semantic_validator", MODULE_PATH)
assert spec and spec.loader
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


def test_current_contracts_and_examples_pass() -> None:
    validator.validate_schema_contracts()
    validator.validate_examples()


def test_token_vazio_requires_missing_variables() -> None:
    payload = copy.deepcopy(validator.load_json(validator.SEMANTIC_EXAMPLE))
    payload["views_7d"]["d6_epistemic_gap"]["missing_variables"] = []
    try:
        validator.validate_semantic_example(payload)
    except ValueError as exc:
        assert "requires missing variables" in str(exc)
    else:
        raise AssertionError("empty TOKEN_VAZIO variables should fail")


def test_explicit_training_requires_explicit_training_purpose() -> None:
    payload = copy.deepcopy(validator.load_json(validator.SEMANTIC_EXAMPLE))
    payload["use_policy"]["training_eligibility"] = "yes_explicit"
    try:
        validator.validate_semantic_example(payload)
    except ValueError as exc:
        assert "requires purpose=training_explicit" in str(exc)
    else:
        raise AssertionError("mismatched training policy should fail")


def test_formal_token_vazio_cannot_execute_directly() -> None:
    payload = copy.deepcopy(validator.load_json(validator.FORMAL_EXAMPLE))
    payload["execution_gate"] = "allow"
    try:
        validator.validate_formal_example(payload)
    except ValueError as exc:
        assert "cannot execute directly" in str(exc)
    else:
        raise AssertionError("TOKEN_VAZIO direct execution should fail")
