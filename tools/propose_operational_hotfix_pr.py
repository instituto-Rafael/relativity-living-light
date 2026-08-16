#!/usr/bin/env python3
"""Create or refresh a draft PR for bounded operational hotfixes.

Only repository-local deterministic diffs already produced in the workspace are
eligible. This tool never auto-merges and never edits scientific content.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Sequence

SCHEMA = "rll.operational_hotfix_proposal.v1"
DEFAULT_RECEIPT = Path("artifacts/operational-auto-hotfix/proposal-receipt.json")
APPROVED_PATHS = [".github/workflow-contract.yml"]


def run(argv: Sequence[str], env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(list(argv), check=True, text=True, capture_output=True, env=env)


def write_receipt(path: Path, **payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = {
        "schema": SCHEMA,
        "claim_allowed": False,
        "publication_effect": "NONE",
        "direct_main_commit": False,
        "auto_merge": False,
        **payload,
    }
    path.write_text(json.dumps(body, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="main")
    parser.add_argument("--branch", default="automation/operational-hotfix-main")
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN", "")
    repository = os.environ.get("GITHUB_REPOSITORY", "")
    env = os.environ.copy()
    env["GH_TOKEN"] = token

    if not token or not repository:
        write_receipt(args.receipt, decision="TOKEN_VAZIO_EXTERNAL_SETTING", residual="GITHUB_TOKEN_OR_REPOSITORY_MISSING")
        return 2

    changed = []
    for path in APPROVED_PATHS:
        result = subprocess.run(["git", "diff", "--quiet", "--", path], check=False)
        if result.returncode != 0:
            changed.append(path)
    if not changed:
        write_receipt(args.receipt, decision="NO_CHANGE", base=args.base, branch=args.branch, changed_paths=[])
        print("No approved operational change to propose.")
        return 0

    try:
        run(["git", "config", "user.name", "github-actions[bot]"], env)
        run(["git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com"], env)
        run(["git", "checkout", "-B", args.branch], env)
        run(["git", "add", "--", *changed], env)
        run(["git", "commit", "-m", "hotfix(ci): reconcile bounded operational contract drift"], env)
        run(["gh", "auth", "setup-git"], env)
        subprocess.run(["git", "fetch", "origin", args.branch], check=False, text=True, capture_output=True, env=env)
        run(["git", "push", "--force-with-lease", "origin", f"HEAD:refs/heads/{args.branch}"], env)

        existing = run([
            "gh", "pr", "list", "--repo", repository, "--state", "open",
            "--head", args.branch, "--json", "number,url", "--limit", "1"
        ], env)
        items = json.loads(existing.stdout or "[]")
        if items:
            decision = "PR_UPDATED"
            url = items[0]["url"]
        else:
            created = run([
                "gh", "pr", "create", "--repo", repository,
                "--base", args.base, "--head", args.branch, "--draft",
                "--title", "hotfix(ci): reconcile operational contract drift",
                "--body",
                "Automatic bounded proposal after deterministic CI/governance drift detection. "
                "Scope is restricted to approved structural contract fields. Human review required; "
                "auto-merge=false; claim_allowed=false; publication_effect=NONE."
            ], env)
            decision = "DRAFT_PR_OPENED"
            url = created.stdout.strip()
    except (subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        detail = getattr(exc, "stderr", "") or getattr(exc, "stdout", "") or str(exc)
        print(detail, file=sys.stderr)
        write_receipt(args.receipt, decision="TOKEN_VAZIO_EXTERNAL_SETTING", base=args.base, branch=args.branch, changed_paths=changed, residual="PR_CREATION_OR_WRITE_PERMISSION_UNAVAILABLE")
        return 1

    write_receipt(args.receipt, decision=decision, base=args.base, branch=args.branch, changed_paths=changed, pr_url=url, residual="NONE")
    print(url)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
