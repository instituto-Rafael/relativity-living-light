import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


REPO = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO / "schemas" / "rll_run_manifest.schema.json"
FIXTURE_PATH = REPO / "fixtures" / "rll_run_manifest.partial.example.json"


def test_partial_run_manifest_fixture_matches_schema() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(fixture), key=lambda error: list(error.path))

    assert not errors, "\n".join(
        f"{'/'.join(str(part) for part in error.path)}: {error.message}" for error in errors
    )
    assert fixture["claim_allowed"] is False
    assert fixture["completeness"] == "partial"
    assert fixture["results"][0]["status"] == "TOKEN_VAZIO"


def test_token_vazio_result_does_not_claim_supersession() -> None:
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    result = fixture["results"][0]

    assert result["status"] == "TOKEN_VAZIO"
    assert result["supersedes_result_id"] is None
    assert result["artifact_sha256"] == "TOKEN_VAZIO"
