#!/usr/bin/env python3
"""Create or refresh a draft PR for bounded operational hotfixes.

Only repository-local deterministic diffs already produced in the workspace are
eligible. This tool never auto-merges and never edits scientific content.
A proposal is emitted only when the governance policy names a verified base
branch.  Missing/contradictory maturity routing is a valid TOKEN_VAZIO product,
not permission to bypass the branch-maturity gate.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Sequence

SCHEMA = "rll.operational_hotfix_proposal.v2"
DEFAULT_RECEIPT = Path("artifacts/operational-auto-hotfix/proposal-receipt.json")
DEFAULT_POLICY = Path("data/governance/RLL_OPERATIONAL_AUTO_HOTFIX_POLICY_V1.json")
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


def load_policy(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("operational hotfix policy must be a JSON object")
    return payload


def maturity_route_decision(policy: dict[str, Any], requested_base: str) -> tuple[bool, str, str]:
    route = policy.get("main_hotfix_route", {})
    if not isinstance(route, dict):
        return False, "TOKEN_VAZIO_MATURITY_ROUTE", "HOTFIX_ROUTE_POLICY_INVALID"
    allowed = route.get("allowed") is True
    verified_base = route.get("verified_proposal_base")
    state = str(route.get("state", "TOKEN_VAZIO_MATURITY_ROUTE"))
    if not allowed:
        return False, state, "HOTFIX_ROUTE_NOT_AUTHORIZED"
    if not isinstance(verified_base, str) or not verified_base or verified_base.startswith("TOKEN_VAZIO"):
        return False, "TOKEN_VAZIO_MATURITY_ROUTE", "VERIFIED_PROPOSAL_BASE_MISSING"
    if requested_base != verified_base:
        return False, "TOKEN_VAZIO_MATURITY_ROUTE", f"REQUESTED_BASE_{requested_base}_DIFFERS_FROM_VERIFIED_{verified_base}"
    return True, state, "NONE"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="main")
    parser.add_argument("--branch", default="automation/operational-hotfix-main")
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN", "")
    repository = os.environ.get("GITHUB_REPOSITORY", "")
    env = os.environ.copy()
    env["GH_TOKEN"] = token

    changed: list[str] = []
    for path in APPROVED_PATHS:
        result = subprocess.run(["git", "diff", "--quiet", "--", path], check=False)
        if result.returncode != 0:
            changed.append(path)
    if not changed:
        write_receipt(args.receipt, decision="NO_CHANGE", base=args.base, branch=args.branch, changed_paths=[])
        print("No approved operational change to propose.")
        return 0

    try:
        policy = load_policy(args.policy)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        write_receipt(
            args.receipt,
            decision="TOKEN_VAZIO_MATURITY_ROUTE",
            base=args.base,
            branch=args.branch,
            changed_paths=changed,
            residual=f"POLICY_UNREADABLE:{type(exc).__name__}",
        )
        print("Maturity route policy unavailable; proposal blocked fail-closed.")
        return 0

    route_allowed, route_state, route_residual = maturity_route_decision(policy, args.base)
    if not route_allowed:
        write_receipt(
            args.receipt,
            decision="TOKEN_VAZIO_MATURITY_ROUTE",
            maturity_route_state=route_state,
            base=args.base,
            branch=args.branch,
            changed_paths=changed,
            residual=route_residual,
            proposed_action=(
                "reconcile main/rll-lab divergence and approve an explicit proposal base through the branch-maturity contract"
            ),
            falsifier="policy names an allowed verified_proposal_base that passes branch_maturity_gate.py",
        )
        print(f"Operational hotfix proposal blocked by maturity route: {route_residual}")
        return 0

    if not token or not repository:
        write_receipt(
            args.receipt,
            decision="TOKEN_VAZIO_EXTERNAL_SETTING",
            maturity_route_state=route_state,
            base=args.base,
            branch=args.branch,
            changed_paths=changed,
            residual="GITHUB_TOKEN_OR_REPOSITORY_MISSING",
        )
        return 2

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
        write_receipt(
            args.receipt,
            decision="TOKEN_VAZIO_EXTERNAL_SETTING",
            maturity_route_state=route_state,
            base=args.base,
            branch=args.branch,
            changed_paths=changed,
            residual="PR_CREATION_OR_WRITE_PERMISSION_UNAVAILABLE",
        )
        return 1

    write_receipt(
        args.receipt,
        decision=decision,
        maturity_route_state=route_state,
        base=args.base,
        branch=args.branch,
        changed_paths=changed,
        pr_url=url,
        residual="NONE",
    )
    print(url)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
