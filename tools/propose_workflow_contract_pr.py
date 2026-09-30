#!/usr/bin/env python3
"""Open a review PR for a locally synchronized workflow contract.

The script is intended for ``workflow_dispatch`` only. It never targets a branch
other than the explicitly supplied base and records external permission failures
as TOKEN_VAZIO_EXTERNAL_SETTING.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Sequence

SCHEMA = "rll.workflow_contract_proposal.v1"


def run(argv: Sequence[str], env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(argv),
        check=True,
        text=True,
        capture_output=True,
        env=env,
    )


def write_receipt(path: Path, decision: str, branch: str, base: str, residual: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": SCHEMA,
        "decision": decision,
        "branch": branch,
        "base": base,
        "residual": residual,
        "claim_allowed": False,
        "publication_effect": "NONE",
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="rll/lab")
    parser.add_argument("--contract", default=".github/workflow-contract.yml")
    parser.add_argument(
        "--receipt", default="artifacts/workflow-contract-sync/proposal-receipt.json"
    )
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN", "")
    repository = os.environ.get("GITHUB_REPOSITORY", "")
    run_id = os.environ.get("GITHUB_RUN_ID", "local")
    branch = f"automation/workflow-contract-sync-{run_id}"
    receipt = Path(args.receipt)
    env = os.environ.copy()
    env["GH_TOKEN"] = token

    if not token or not repository:
        write_receipt(
            receipt,
            "TOKEN_VAZIO_EXTERNAL_SETTING",
            branch,
            args.base,
            "GITHUB_TOKEN_OR_REPOSITORY_MISSING",
        )
        return 2

    unchanged = subprocess.run(
        ["git", "diff", "--quiet", "--", args.contract], check=False
    ).returncode == 0
    if unchanged:
        write_receipt(receipt, "NO_CHANGE", branch, args.base, "NONE")
        print("No workflow contract change to propose.")
        return 0

    try:
        run(["git", "config", "user.name", "github-actions[bot]"], env)
        run(
            [
                "git",
                "config",
                "user.email",
                "41898282+github-actions[bot]@users.noreply.github.com",
            ],
            env,
        )
        run(["git", "checkout", "-b", branch], env)
        run(["git", "add", args.contract], env)
        run(["git", "commit", "-m", "chore(ci): synchronize workflow contract"], env)
        run(["gh", "auth", "setup-git"], env)
        run(["git", "push", "origin", f"HEAD:refs/heads/{branch}"], env)
        completed = run(
            [
                "gh",
                "pr",
                "create",
                "--repo",
                repository,
                "--base",
                args.base,
                "--head",
                branch,
                "--title",
                "chore(ci): sincronizar contrato de workflows",
                "--body",
                (
                    "Proposta automática gerada após detectar divergência entre "
                    "`.github/workflows` e `.github/workflow-contract.yml`. "
                    "Requer revisão humana; `claim_allowed=false`."
                ),
            ],
            env,
        )
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or "proposal command failed").strip()
        print(detail, file=sys.stderr)
        write_receipt(
            receipt,
            "TOKEN_VAZIO_EXTERNAL_SETTING",
            branch,
            args.base,
            "ACTIONS_PR_CREATION_OR_WRITE_PERMISSION_UNAVAILABLE",
        )
        return 1

    write_receipt(receipt, "PR_OPENED", branch, args.base, "NONE")
    print(completed.stdout.strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
