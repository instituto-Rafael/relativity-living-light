#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

POLICY = Path("data/governance/RLL_REPOSITORY_PAT_ASSURANCE_EXCEPTION_V1.json")
WORKFLOW = Path(".github/workflows/rll-repository-pat-assurance.yml")
SECRET_NAME = "GITPAT"
API = "https://api.github.com"


def static_validate(root: Path) -> list[str]:
    errors: list[str] = []
    policy_path = root / POLICY
    workflow_path = root / WORKFLOW
    if not policy_path.is_file():
        return ["POLICY_MISSING"]
    if not workflow_path.is_file():
        return ["WORKFLOW_MISSING"]
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    workflow = workflow_path.read_text(encoding="utf-8")
    if policy.get("repository_secret_name") != SECRET_NAME:
        errors.append("SECRET_NAME_MISMATCH")
    if policy.get("allowed_event") != "workflow_dispatch_only_for_secret_consumption":
        errors.append("MANUAL_ONLY_REQUIRED")
    if policy.get("workflow_permissions", {}).get("contents") != "read":
        errors.append("CONTENTS_READ_REQUIRED")
    if "secrets.GITPAT" not in workflow:
        errors.append("GITPAT_BINDING_MISSING")
    if "github.event_name == 'workflow_dispatch'" not in workflow:
        errors.append("MANUAL_JOB_GUARD_MISSING")
    forbidden = ["curl -X POST", "curl -X PUT", "curl -X PATCH", "curl -X DELETE", "git push", "gh pr merge", "printenv", "set -x"]
    lower = workflow.lower()
    for token in forbidden:
        if token.lower() in lower:
            errors.append(f"FORBIDDEN_PATTERN:{token}")
    return errors


def get_json(path: str, token: str) -> tuple[int, dict[str, Any]]:
    req = urllib.request.Request(
        f"{API}{path}",
        method="GET",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "RLL-repository-PAT-assurance/1"
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            raw = response.read(1024 * 1024)
            return int(response.status), json.loads(raw.decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return int(exc.code), {"message": f"HTTP_{exc.code}"}
    except urllib.error.URLError:
        return 0, {"message": "NETWORK_ERROR"}


def runtime_probe(repository: str) -> dict[str, Any]:
    token = os.environ.get(SECRET_NAME, "")
    receipt: dict[str, Any] = {
        "schema": "rll.repository_pat_assurance.receipt.v1",
        "repository": repository,
        "secret_name": SECRET_NAME,
        "secret_binding_present": bool(token),
        "secret_value_observed": False,
        "secret_value_hashed": False,
        "methods_used": ["GET"],
        "endpoints_used": ["/user", f"/repos/{repository}"],
        "claim_allowed": False,
        "publication_effect": "NONE",
        "authenticated_user": False,
        "repository_read": False,
        "repository_permission_metadata": "TOKEN_VAZIO_NOT_USED_AS_SCOPE_PROOF",
        "decision": "TOKEN_VAZIO_SECRET_BINDING",
        "residuals": []
    }
    if not token:
        receipt["residuals"].append("TOKEN_VAZIO_GITPAT_REPOSITORY_SECRET")
        return receipt

    user_status, user = get_json("/user", token)
    receipt["user_http_status"] = user_status
    receipt["authenticated_user"] = user_status == 200 and bool(user.get("login"))

    repo_status, repo = get_json(f"/repos/{repository}", token)
    receipt["repository_http_status"] = repo_status
    receipt["repository_read"] = repo_status == 200 and bool(repo.get("full_name"))

    if receipt["authenticated_user"] and receipt["repository_read"]:
        receipt["decision"] = "PASS_READ_ONLY_AUTHENTICATION"
        receipt["residuals"].extend([
            "TOKEN_VAZIO_WRITE_PERMISSION_NOT_TESTED",
            "TOKEN_VAZIO_DELETE_ABSENCE_NOT_PROVEN",
            "TOKEN_VAZIO_FINE_GRAINED_SCOPES_NOT_FULLY_INTROSPECTED"
        ])
    else:
        receipt["decision"] = "FAIL_AUTHENTICATION_OR_REPOSITORY_READ"
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--runtime", action="store_true")
    parser.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY", "instituto-Rafael/relativity-living-light"))
    parser.add_argument("--output", type=Path, default=Path("artifacts/governance/RLL_REPOSITORY_PAT_ASSURANCE_RECEIPT.json"))
    args = parser.parse_args()

    errors = static_validate(args.repo_root.resolve())
    if errors:
        print(json.dumps({"decision": "FAIL_STATIC", "errors": errors}, indent=2))
        return 1
    if not args.runtime:
        print(json.dumps({"decision": "PASS_STATIC", "claim_allowed": False}, indent=2))
        return 0

    receipt = runtime_probe(args.repository)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"decision": receipt["decision"], "residuals": receipt["residuals"]}, indent=2))
    return 0 if receipt["decision"].startswith("PASS") else 2


if __name__ == "__main__":
    raise SystemExit(main())
