import copy
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from tools.validate_epistemic_void import (
    DEFAULT_LEDGER,
    DEFAULT_SCHEMA,
    semantic_findings,
    validate,
    write_reports,
)


def load_fixture() -> tuple[dict, dict]:
    schema = json.loads(DEFAULT_SCHEMA.read_text(encoding="utf-8"))
    ledger = json.loads(DEFAULT_LEDGER.read_text(encoding="utf-8"))
    return schema, ledger


def schema_errors(schema: dict, ledger: dict) -> list:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return sorted(validator.iter_errors(ledger), key=lambda error: list(error.path))


def test_epistemic_void_ledger_is_valid_and_claim_bounded() -> None:
    findings, payload = validate()
    assert not findings
    assert payload["passed"] is True
    assert payload["claim_allowed"] is False
    assert payload["totals"]["records"] >= 5
    assert payload["totals"]["hypotheses"] >= 1
    assert payload["totals"]["exit_conditions"] >= payload["totals"]["records"]


def test_every_hypothesis_has_falsifier_prediction_and_gate() -> None:
    _, ledger = load_fixture()
    hypotheses = [
        possibility
        for record in ledger["records"]
        for possibility in record["possibilities"]
        if possibility["classification"] == "H"
    ]
    assert hypotheses
    for hypothesis in hypotheses:
        assert hypothesis["role"] == "testable_hypothesis"
        assert hypothesis["falsifier"]
        assert hypothesis["predicted_observation"]
        assert hypothesis["promotion_gate"]
        assert hypothesis["claim_allowed"] is False


def test_token_vazio_cannot_carry_a_conclusion() -> None:
    schema, ledger = load_fixture()
    mutated = copy.deepcopy(ledger)
    record = next(item for item in mutated["records"] if item["state"] == "TOKEN_VAZIO")
    record["conclusion"] = "Premature conclusion"
    assert schema_errors(schema, mutated)


def test_hypothesis_without_falsifier_is_rejected() -> None:
    schema, ledger = load_fixture()
    mutated = copy.deepcopy(ledger)
    hypothesis = next(
        possibility
        for record in mutated["records"]
        for possibility in record["possibilities"]
        if possibility["classification"] == "H"
    )
    hypothesis["falsifier"] = None
    assert schema_errors(schema, mutated)


def test_resolved_record_requires_hashed_resolution_evidence() -> None:
    schema, ledger = load_fixture()
    mutated = copy.deepcopy(ledger)
    record = mutated["records"][0]
    record["state"] = "RESOLVED"
    record["conclusion"] = "The structural gap is closed by auditable evidence."
    record["resolution_evidence"] = []
    assert schema_errors(schema, mutated)


def test_semantic_validator_detects_duplicate_record_ids() -> None:
    _, ledger = load_fixture()
    mutated = copy.deepcopy(ledger)
    mutated["records"][1]["id"] = mutated["records"][0]["id"]
    findings = semantic_findings(mutated)
    assert any(item["code"] == "EV_DUPLICATE_RECORD_ID" for item in findings)


def test_report_is_generated_with_metric_boundary_and_checksums(tmp_path: Path) -> None:
    findings, payload = validate()
    assert not findings
    write_reports(payload, tmp_path)
    report = (tmp_path / "EPISTEMIC_VOID_REPORT.md").read_text(encoding="utf-8")
    machine = (tmp_path / "epistemic_void_report.json").read_text(encoding="utf-8")
    checksums = (tmp_path / "CHECKSUMS.sha256").read_text(encoding="utf-8")
    assert "not thermodynamic entropy" in report
    assert "routing only" in machine
    assert "EPISTEMIC_VOID_REPORT.md" in checksums
