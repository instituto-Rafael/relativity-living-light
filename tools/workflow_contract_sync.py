#!/usr/bin/env python3
"""Check or synchronize the executable GitHub workflow inventory contract.

The tool edits only ``inventory.active_workflows``. It never commits, pushes,
opens a pull request, changes branch settings, or promotes a scientific claim.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable

SCHEMA = "rll.workflow_contract_sync.v1"
DEFAULT_CONTRACT = Path(".github/workflow-contract.yml")
DEFAULT_OUTPUT = Path("artifacts/workflow-contract-sync")
ACTIVE_RE = re.compile(r"^(?P<indent>\s*)active_workflows:\s*(?P<count>\d+)\s*$", re.MULTILINE)


@dataclass(frozen=True)
class Result:
    schema: str
    contract: str
    expected: int
    actual: int
    changed: bool
    decision: str
    claim_allowed: bool
    publication_effect: str
    commit_sha: str
    inputs_sha256: str
    workflow_paths: list[str]
    residuals: list[str]


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def workflow_paths(repo_root: Path) -> list[Path]:
    root = repo_root / ".github" / "workflows"
    if not root.is_dir():
        raise ValueError(f"workflow directory not found: {root}")
    paths = [*root.glob("*.yml"), *root.glob("*.yaml")]
    return sorted(set(path for path in paths if path.is_file()))


def read_expected(text: str) -> int:
    matches = list(ACTIVE_RE.finditer(text))
    if len(matches) != 1:
        raise ValueError(
            "contract must contain exactly one inventory.active_workflows scalar"
        )
    match = matches[0]
    if match.group("indent") != "  ":
        raise ValueError("active_workflows must use two-space inventory indentation")
    return int(match.group("count"))


def replace_expected(text: str, actual: int) -> str:
    read_expected(text)
    return ACTIVE_RE.sub(f"  active_workflows: {actual}", text, count=1)


def evaluate(repo_root: Path, contract: Path, write: bool = False) -> Result:
    contract_path = contract if contract.is_absolute() else repo_root / contract
    if not contract_path.is_file():
        raise ValueError(f"contract not found: {contract_path}")

    before = contract_path.read_bytes()
    text = before.decode("utf-8")
    expected = read_expected(text)
    workflows = workflow_paths(repo_root)
    actual = len(workflows)
    changed = expected != actual

    if write and changed:
        updated = replace_expected(text, actual)
        contract_path.write_text(updated, encoding="utf-8")
        decision = "UPDATED"
        residuals: list[str] = []
    elif changed:
        decision = "MISMATCH"
        residuals = ["WORKFLOW_INVENTORY_DRIFT"]
    else:
        decision = "PASS"
        residuals = []

    rel_contract = contract_path.relative_to(repo_root).as_posix()
    rel_workflows = [path.relative_to(repo_root).as_posix() for path in workflows]
    input_material = before + "\n".join(rel_workflows).encode("utf-8")
    return Result(
        schema=SCHEMA,
        contract=rel_contract,
        expected=expected,
        actual=actual,
        changed=changed,
        decision=decision,
        claim_allowed=False,
        publication_effect="NONE",
        commit_sha=os.environ.get("GITHUB_SHA", "TOKEN_VAZIO_LOCAL_COMMIT"),
        inputs_sha256=sha256_bytes(input_material),
        workflow_paths=rel_workflows,
        residuals=residuals,
    )


def write_reports(result: Result, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = asdict(result)
    (output_dir / "receipt.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    lines = [
        "# Workflow Contract Reconciliation",
        "",
        f"- decision: `{result.decision}`",
        f"- expected: `{result.expected}`",
        f"- actual: `{result.actual}`",
        f"- changed: `{str(result.changed).lower()}`",
        "- claim_allowed: `false`",
        "- publication_effect: `NONE`",
        f"- inputs_sha256: `{result.inputs_sha256}`",
        "",
        "## Residuals",
        "",
    ]
    lines.extend(f"- `{item}`" for item in result.residuals)
    if not result.residuals:
        lines.append("- `NONE`")
    lines.extend(["", "## Workflows", ""])
    lines.extend(f"- `{path}`" for path in result.workflow_paths)
    (output_dir / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(list(argv) if argv is not None else None)

    root = args.repo_root.resolve()
    try:
        result = evaluate(root, args.contract, write=args.write)
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"ERROR WORKFLOW_CONTRACT_SYNC: {exc}", file=sys.stderr)
        return 2

    if args.write_report:
        output = args.output_dir if args.output_dir.is_absolute() else root / args.output_dir
        write_reports(result, output)

    print(
        f"workflow contract: expected={result.expected} actual={result.actual} "
        f"decision={result.decision}"
    )
    if result.decision == "MISMATCH":
        print("Run with --write on a review branch, then submit the diff by PR.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
