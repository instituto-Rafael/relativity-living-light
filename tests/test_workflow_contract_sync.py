from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.workflow_contract_sync import evaluate, read_expected, write_reports


def make_repo(tmp_path: Path, expected: int, workflow_count: int) -> Path:
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)
    (tmp_path / ".github" / "workflow-contract.yml").write_text(
        "schema: test\ninventory:\n  active_workflows: " + str(expected) + "\n",
        encoding="utf-8",
    )
    for index in range(workflow_count):
        suffix = "yml" if index % 2 == 0 else "yaml"
        (workflows / f"w{index}.{suffix}").write_text(
            f"name: W{index}\non: workflow_dispatch\njobs: {{}}\n", encoding="utf-8"
        )
    (workflows / "README.md").write_text("not a workflow\n", encoding="utf-8")
    return tmp_path


def test_matching_contract_passes(tmp_path: Path) -> None:
    root = make_repo(tmp_path, expected=2, workflow_count=2)
    result = evaluate(root, Path(".github/workflow-contract.yml"))
    assert result.decision == "PASS"
    assert result.expected == result.actual == 2
    assert result.claim_allowed is False


def test_mismatch_is_fail_closed(tmp_path: Path) -> None:
    root = make_repo(tmp_path, expected=1, workflow_count=2)
    result = evaluate(root, Path(".github/workflow-contract.yml"))
    assert result.decision == "MISMATCH"
    assert result.residuals == ["WORKFLOW_INVENTORY_DRIFT"]


def test_write_updates_only_inventory_and_is_idempotent(tmp_path: Path) -> None:
    root = make_repo(tmp_path, expected=1, workflow_count=3)
    contract = root / ".github" / "workflow-contract.yml"
    result = evaluate(root, Path(".github/workflow-contract.yml"), write=True)
    assert result.decision == "UPDATED"
    assert read_expected(contract.read_text(encoding="utf-8")) == 3
    second = evaluate(root, Path(".github/workflow-contract.yml"), write=True)
    assert second.decision == "PASS"
    assert second.changed is False


def test_reports_are_machine_and_human_readable(tmp_path: Path) -> None:
    root = make_repo(tmp_path, expected=2, workflow_count=2)
    result = evaluate(root, Path(".github/workflow-contract.yml"))
    output = root / "artifacts"
    write_reports(result, output)
    payload = json.loads((output / "receipt.json").read_text(encoding="utf-8"))
    assert payload["decision"] == "PASS"
    assert payload["publication_effect"] == "NONE"
    assert "Workflow Contract Reconciliation" in (output / "REPORT.md").read_text(
        encoding="utf-8"
    )


def test_duplicate_active_workflows_is_rejected(tmp_path: Path) -> None:
    root = make_repo(tmp_path, expected=1, workflow_count=1)
    contract = root / ".github" / "workflow-contract.yml"
    contract.write_text(
        "inventory:\n  active_workflows: 1\nother:\n  active_workflows: 1\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="exactly one"):
        evaluate(root, Path(".github/workflow-contract.yml"))


def test_wrong_indentation_is_rejected(tmp_path: Path) -> None:
    root = make_repo(tmp_path, expected=1, workflow_count=1)
    contract = root / ".github" / "workflow-contract.yml"
    contract.write_text("inventory:\n    active_workflows: 1\n", encoding="utf-8")
    with pytest.raises(ValueError, match="two-space"):
        evaluate(root, Path(".github/workflow-contract.yml"))
