from pathlib import Path

from tools.validate_workflow_docs import DEFAULT_CONTRACT, REPO, validate_contract, write_reports


def test_workflow_documentation_contract_matches_repository() -> None:
    findings, payload = validate_contract(REPO, DEFAULT_CONTRACT)

    errors = [item for item in findings if item.severity == "error"]
    assert not errors, "\n".join(f"{item.code}: {item.path}: {item.message}" for item in errors)
    assert payload["passed"] is True
    assert payload["active_workflows"] == 44
    assert payload["canonical_pipeline"] == ".github/workflows/rll-pipeline-linear-completo.yml"


def test_workflow_documentation_report_is_consultable(tmp_path: Path) -> None:
    findings, payload = validate_contract(REPO, DEFAULT_CONTRACT)
    assert not [item for item in findings if item.severity == "error"]

    write_reports(payload, tmp_path)

    registry = tmp_path / "workflow_registry.json"
    report = tmp_path / "WORKFLOW_DOCS_REPORT.md"
    assert registry.is_file()
    assert report.is_file()
    assert "Workflow Documentation Consistency" in report.read_text(encoding="utf-8")
    assert "branch-protection" in registry.read_text(encoding="utf-8")
