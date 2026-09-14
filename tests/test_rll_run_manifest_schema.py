import copy
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


REPO = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO / "schemas" / "rll_run_manifest.schema.json"
FIXTURE_PATH = REPO / "fixtures" / "rll_run_manifest.partial.example.json"


def load_contract() -> tuple[Draft202012Validator, dict]:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    return Draft202012Validator(schema, format_checker=FormatChecker()), fixture


def validation_errors(validator: Draft202012Validator, payload: dict) -> list:
    return sorted(validator.iter_errors(payload), key=lambda error: list(error.path))


def test_partial_run_manifest_fixture_matches_schema() -> None:
    validator, fixture = load_contract()
    errors = validation_errors(validator, fixture)

    assert not errors, "\n".join(
        f"{'/'.join(str(part) for part in error.path)}: {error.message}" for error in errors
    )
    assert fixture["claim_allowed"] is False
    assert fixture["completeness"] == "partial"
    assert fixture["results"][0]["status"] == "TOKEN_VAZIO"


def test_token_vazio_cannot_supersede_historical_evidence() -> None:
    validator, fixture = load_contract()
    invalid = copy.deepcopy(fixture)
    invalid["results"][0]["supersedes_result_id"] = "historical-F-COS-04"

    errors = validation_errors(validator, invalid)

    assert errors
    assert any("supersedes_result_id" in "/".join(str(part) for part in error.path) for error in errors)


def test_pass_or_fail_requires_numeric_evidence_and_real_artifact_hash() -> None:
    validator, fixture = load_contract()
    invalid = copy.deepcopy(fixture)
    invalid["results"][0].update(
        {
            "status": "FAIL",
            "value": -6.19,
            "uncertainty": 0.691,
            "artifact_sha256": "TOKEN_VAZIO",
        }
    )

    errors = validation_errors(validator, invalid)

    assert errors
    assert any("artifact_sha256" in "/".join(str(part) for part in error.path) for error in errors)


def test_invalidated_result_requires_reason() -> None:
    validator, fixture = load_contract()
    invalid = copy.deepcopy(fixture)
    invalid["results"][0].update(
        {
            "status": "INVALIDATED",
            "value": -6.19,
            "uncertainty": 0.691,
            "artifact_sha256": "0" * 64,
            "invalidation_reason": None,
        }
    )

    errors = validation_errors(validator, invalid)

    assert errors
    assert any("invalidation_reason" in "/".join(str(part) for part in error.path) for error in errors)
