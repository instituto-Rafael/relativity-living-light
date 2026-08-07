from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.workflow_contract_sync import evaluate, read_expected, write_reports


def make_repo(tmp_path: Path, expected: int, workflow_count: int) -> Path:
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)
    (tmp_path / ".github" / "workflow-contract.yml").write_text(
        "schema: test\ninventory:\n  active_workflows: " + str(expected) + "\n", encoding="utf-8"
    )
    for index in range(workflow_count):
        suffix = "yml" if index % 2 == 0 else "yaml"
        (workflows / f"w{index}.{suffix}").write_text("name: W\non: workflow_dispatch\njobs: {}\n", encoding="utf-8")
    return tmp_path


def test_matching_contract_passes(tmp_path: Path):
    result = evaluate(make_repo(tmp_path, 2, 2), Path(".github/workflow-contract.yml"))
    assert result.decision == "PASS"
    assert result.claim_allowed is False


def test_mismatch_is_fail_closed(tmp_path: Path):
    result = evaluate(make_repo(tmp_path, 1, 2), Path(".github/workflow-contract.yml"))
    assert result.decision == "MISMATCH"
    assert result.residuals == ["WORKFLOW_INVENTORY_DRIFT"]


def test_write_is_narrow_and_idempotent(tmp_path: Path):
    root = make_repo(tmp_path, 1, 3)
    contract = root / ".github/workflow-contract.yml"
    assert evaluate(root, Path(".github/workflow-contract.yml"), write=True).decision == "UPDATED"
    assert read_expected(contract.read_text(encoding="utf-8")) == 3
    assert evaluate(root, Path(".github/workflow-contract.yml"), write=True).decision == "PASS"


def test_reports_preserve_boundary(tmp_path: Path):
    root = make_repo(tmp_path, 1, 1)
    result = evaluate(root, Path(".github/workflow-contract.yml"))
    write_reports(result, root / "artifacts")
    payload = json.loads((root / "artifacts/receipt.json").read_text(encoding="utf-8"))
    assert payload["claim_allowed"] is False
    assert payload["publication_effect"] == "NONE"


def test_duplicate_scalar_rejected(tmp_path: Path):
    root = make_repo(tmp_path, 1, 1)
    contract = root / ".github/workflow-contract.yml"
    contract.write_text("inventory:\n  active_workflows: 1\nother:\n  active_workflows: 1\n", encoding="utf-8")
    with pytest.raises(ValueError, match="exactly one"):
        evaluate(root, Path(".github/workflow-contract.yml"))
