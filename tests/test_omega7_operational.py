import json
from pathlib import Path

from tools.validate_omega7_operational import (
    ASSESSMENT_PATH,
    SCHEMA_PATH,
    expected_decision,
    load_json,
    validate_assessment,
    write_reports,
)


def write_assessment(tmp_path: Path, payload: dict) -> Path:
    path = tmp_path / "assessment.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def test_canonical_omega7_assessment_matches_contract() -> None:
    findings, payload = validate_assessment()

    assert not [item for item in findings if item.severity == "error"]
    assert payload["passed"] is True
    assert payload["direction_count"] == 7
    assert payload["decision"] == "BLOCKED"
    assert payload["omega_g"] == 0.479867804894
    assert payload["omega_min"] == 0.25
    assert payload["weakest_directions"] == ["D3", "D7"]
    assert payload["hard_gate_open"] == ["I1", "I4", "I5", "I6", "I7"]
    assert payload["claim_allowed"] is False


def test_declared_decision_is_fail_closed() -> None:
    assessment = load_json(ASSESSMENT_PATH)
    metrics = assessment["omega_metrics"]

    assert expected_decision(
        metrics["omega_g"],
        metrics["omega_min"],
        metrics["hard_gate_open"],
    ) == "BLOCKED"


def test_claim_promotion_is_rejected(tmp_path: Path) -> None:
    assessment = load_json(ASSESSMENT_PATH)
    assessment["claim_allowed"] = True

    findings, payload = validate_assessment(write_assessment(tmp_path, assessment), SCHEMA_PATH)

    assert payload["passed"] is False
    codes = {item.code for item in findings}
    assert "OMEGA7_SCHEMA" in codes
    assert "OMEGA7_CLAIM_BOUNDARY" in codes


def test_duplicate_direction_is_rejected(tmp_path: Path) -> None:
    assessment = load_json(ASSESSMENT_PATH)
    assessment["directions"][1]["direction_id"] = "D1"

    findings, payload = validate_assessment(write_assessment(tmp_path, assessment), SCHEMA_PATH)

    assert payload["passed"] is False
    codes = {item.code for item in findings}
    assert "OMEGA7_DUPLICATE_DIRECTION" in codes
    assert "OMEGA7_DIRECTION_SET" in codes


def test_score_tampering_is_rejected(tmp_path: Path) -> None:
    assessment = load_json(ASSESSMENT_PATH)
    assessment["directions"][0]["normalized_score"] = 0.9

    findings, payload = validate_assessment(write_assessment(tmp_path, assessment), SCHEMA_PATH)

    assert payload["passed"] is False
    codes = {item.code for item in findings}
    assert "OMEGA7_NORMALIZATION" in codes
    assert "OMEGA7_GEOMETRIC_MEAN" in codes


def test_open_hard_gate_cannot_declare_coherent(tmp_path: Path) -> None:
    assessment = load_json(ASSESSMENT_PATH)
    assessment["state"] = "COHERENT"
    assessment["omega_metrics"]["decision"] = "COHERENT"

    findings, payload = validate_assessment(write_assessment(tmp_path, assessment), SCHEMA_PATH)

    assert payload["passed"] is False
    codes = {item.code for item in findings}
    assert "OMEGA7_DECISION" in codes
    assert "OMEGA7_STATE" in codes


def test_reports_are_materialized_with_checksums(tmp_path: Path) -> None:
    findings, payload = validate_assessment()
    assert not findings

    write_reports(payload, tmp_path)

    report_json = tmp_path / "omega7_operational_report.json"
    report_md = tmp_path / "OMEGA7_OPERATIONAL_REPORT.md"
    checksums = tmp_path / "CHECKSUMS.sha256"

    assert report_json.is_file()
    assert report_md.is_file()
    assert checksums.is_file()
    assert "decision: `BLOCKED`" in report_md.read_text(encoding="utf-8")
    assert "does not validate RLL" in report_json.read_text(encoding="utf-8")
    checksum_text = checksums.read_text(encoding="utf-8")
    assert "omega7_operational_report.json" in checksum_text
    assert "OMEGA7_OPERATIONAL_REPORT.md" in checksum_text
