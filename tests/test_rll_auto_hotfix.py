from __future__ import annotations

import json
from pathlib import Path

from tools.rll_auto_hotfix import apply_safe, build_vector, read_expected, scan, write_products


def make_repo(tmp_path: Path, expected: int = 1, actual: int = 1) -> Path:
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)
    (tmp_path / ".github" / "workflow-contract.yml").write_text(
        "schema: test\ninventory:\n  active_workflows: " + str(expected) + "\n",
        encoding="utf-8",
    )
    for index in range(actual):
        (workflows / f"w{index}.yml").write_text(
            "name: W\non: workflow_dispatch\npermissions:\n  contents: read\njobs: {}\n",
            encoding="utf-8",
        )
    return tmp_path


def test_inventory_drift_is_p0_and_safe_fixable(tmp_path: Path) -> None:
    root = make_repo(tmp_path, expected=1, actual=2)
    observations, metadata = scan(root)
    drift = [o for o in observations if o.kind == "WORKFLOW_INVENTORY_DRIFT"]
    assert len(drift) == 1
    assert drift[0].urgency == "P0"
    assert drift[0].auto_fixable is True
    assert metadata["actual_workflows"] == 2


def test_safe_fix_changes_only_contract_count(tmp_path: Path) -> None:
    root = make_repo(tmp_path, expected=1, actual=3)
    workflows_before = {
        p.name: p.read_bytes() for p in (root / ".github" / "workflows").iterdir()
    }
    observations, metadata = scan(root)
    assert apply_safe(root, observations, metadata) is True
    assert read_expected((root / ".github" / "workflow-contract.yml").read_text()) == 3
    workflows_after = {
        p.name: p.read_bytes() for p in (root / ".github" / "workflows").iterdir()
    }
    assert workflows_before == workflows_after


def test_safe_fix_is_idempotent(tmp_path: Path) -> None:
    root = make_repo(tmp_path, expected=1, actual=2)
    observations, metadata = scan(root)
    assert apply_safe(root, observations, metadata) is True
    observations2, metadata2 = scan(root)
    assert not [o for o in observations2 if o.kind == "WORKFLOW_INVENTORY_DRIFT"]
    assert apply_safe(root, observations2, metadata2) is False


def test_floating_action_is_observed_but_not_auto_fixed(tmp_path: Path) -> None:
    root = make_repo(tmp_path)
    workflow = root / ".github" / "workflows" / "w0.yml"
    workflow.write_text(
        "name: W\non: workflow_dispatch\njobs:\n  x:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v4\n",
        encoding="utf-8",
    )
    observations, _ = scan(root)
    floating = [o for o in observations if o.kind == "FLOATING_ACTION_REF"]
    assert len(floating) == 1
    assert floating[0].urgency == "P1"
    assert floating[0].auto_fixable is False


def test_missing_local_dependency_is_fail_visible(tmp_path: Path) -> None:
    root = make_repo(tmp_path)
    workflow = root / ".github" / "workflows" / "w0.yml"
    workflow.write_text(
        "name: W\non: workflow_dispatch\njobs:\n  x:\n    runs-on: ubuntu-latest\n    steps:\n      - run: python 'scripts/missing.py'\n",
        encoding="utf-8",
    )
    observations, _ = scan(root)
    missing = [o for o in observations if o.kind == "MISSING_LOCAL_WORKFLOW_DEPENDENCY"]
    assert len(missing) == 1
    assert missing[0].auto_fixable is False


def test_token_vazio_is_navigable_not_closed(tmp_path: Path) -> None:
    root = make_repo(tmp_path)
    governance = root / "data" / "governance"
    governance.mkdir(parents=True)
    (governance / "x.json").write_text('{"state":"TOKEN_VAZIO_TEST"}\n', encoding="utf-8")
    observations, _ = scan(root)
    tokens = [o for o in observations if o.kind == "EPISTEMIC_TOKEN"]
    assert len(tokens) == 1
    assert tokens[0].state == "TOKEN_VAZIO_TEST"
    assert tokens[0].auto_fixable is False


def test_products_are_machine_auditable(tmp_path: Path) -> None:
    root = make_repo(tmp_path)
    observations, metadata = scan(root)
    write_products(root, Path("artifacts/hotfix"), observations, metadata, False)
    out = root / "artifacts" / "hotfix"
    receipt = json.loads((out / "receipt.json").read_text())
    vector = json.loads((out / "state_vector.json").read_text())
    assert receipt["claim_allowed"] is False
    assert receipt["auto_merge"] is False
    assert vector["claim_allowed"] is False
    assert (out / "observations.jsonl").is_file()
    assert (out / "SUMMARY.md").is_file()


def test_state_vector_keeps_blocked_items_visible(tmp_path: Path) -> None:
    root = make_repo(tmp_path)
    workflow = root / ".github" / "workflows" / "w0.yml"
    workflow.write_text(
        "name: W\non: workflow_dispatch\njobs:\n  x:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v4\n",
        encoding="utf-8",
    )
    observations, _ = scan(root)
    vector = build_vector(observations, False)
    assert vector.blocked_from_automation >= 1
    assert vector.claim_allowed is False
    assert vector.publication_effect == "NONE"
