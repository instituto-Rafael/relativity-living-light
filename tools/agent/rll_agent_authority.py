#!/usr/bin/env python3
"""Governed GitHub authority bridge for the RLL Copilot Secretary.

Agents secrets/variables are runtime authority. Secret values are never
persisted, printed, hashed, or included in receipts.

SOURCE != EXECUTION != EVIDENCE != CLAIM
TOKEN_VAZIO != 0
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

API = "https://api.github.com"
ENV_NAME_RE = re.compile(r"^[A-Z_][A-Z0-9_]*$")
PAT_SELECTOR = "RLL_AGENT_GITHUB_PAT_ENV"
PAT_ALIASES = (
    "RLL_AGENT_PAT",
    "AGENT_GITHUB_PAT",
    "AGENT_PAT",
    "GH_PAT",
    "GIT_PAT",
    "PAT_GIT",
)
PROTECTED_BRANCHES = {"main", "rll/lab", "rll/integration", "rll/release"}
WORK_PREFIXES = ("agent/", "work/")
TOKEN_VAZIO = "TOKEN_VAZIO"


class AuthorityError(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def resolve_pat() -> tuple[str | None, str | None]:
    selector = os.environ.get(PAT_SELECTOR, "").strip()
    if selector:
        if not ENV_NAME_RE.fullmatch(selector):
            raise AuthorityError("TOKEN_VAZIO_INVALID_AGENT_PAT_SELECTOR")
        token = os.environ.get(selector)
        if not token:
            raise AuthorityError("TOKEN_VAZIO_SELECTED_AGENT_PAT_ABSENT")
        return selector, token

    present = [name for name in PAT_ALIASES if os.environ.get(name)]
    if not present:
        return None, None
    if len(present) > 1:
        raise AuthorityError("TOKEN_VAZIO_AMBIGUOUS_AGENT_PAT")
    return present[0], os.environ[present[0]]


def github_get(path: str, token: str, timeout: int = 20) -> tuple[int, Any]:
    req = urllib.request.Request(
        f"{API}{path}",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "RLL-Secretary-Agent/1",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            body = response.read(2 * 1024 * 1024 + 1)
            if len(body) > 2 * 1024 * 1024:
                raise AuthorityError("GitHub response exceeded 2 MiB cap")
            return int(response.status), json.loads(body.decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return int(exc.code), {"message": f"HTTP_{exc.code}"}


def probe(repository: str) -> tuple[dict[str, Any], int]:
    receipt: dict[str, Any] = {
        "schema": "rll.agent_authority_probe.v1",
        "timestamp_utc": utc_now(),
        "repository": repository,
        "auth_present": False,
        "authenticated": False,
        "actor": TOKEN_VAZIO,
        "repository_access_observed": False,
        "repository_permission_observed": TOKEN_VAZIO,
        "token_scope_claim": TOKEN_VAZIO,
        "operations_observed": [],
        "operations_not_tested": [
            "branch_write",
            "push_work_branch",
            "pull_request_write",
            "issue_write",
            "workflow_dispatch",
            "workflow_rerun"
        ],
        "forbidden_operations": [
            "delete",
            "force_push",
            "auto_merge",
            "direct_protected_branch_push",
            "secret_mutation",
            "variable_mutation",
            "repository_settings_mutation",
            "branch_protection_or_ruleset_mutation"
        ],
        "claim_allowed": False,
        "gaps": []
    }

    try:
        _source, token = resolve_pat()
    except AuthorityError as exc:
        receipt["gaps"].append(str(exc))
        return receipt, 3

    if not token:
        receipt["gaps"].append("TOKEN_VAZIO_AGENT_GITHUB_PAT")
        return receipt, 3

    receipt["auth_present"] = True
    status, user = github_get("/user", token)
    if status != 200 or not isinstance(user, dict) or not user.get("login"):
        receipt["authentication_http_status"] = status
        receipt["gaps"].append("TOKEN_VAZIO_AGENT_GITHUB_AUTHENTICATION")
        return receipt, 4

    receipt["authenticated"] = True
    receipt["actor"] = user["login"]
    receipt["operations_observed"].append("GET /user")

    status, repo = github_get(f"/repos/{repository}", token)
    receipt["repository_http_status"] = status
    if status == 200 and isinstance(repo, dict):
        receipt["repository_access_observed"] = True
        receipt["operations_observed"].append("GET /repos/{repository}")
        perms = repo.get("permissions")
        if isinstance(perms, dict):
            receipt["repository_permission_observed"] = {
                key: bool(perms.get(key))
                for key in ("pull", "triage", "push", "maintain", "admin")
                if key in perms
            }
        receipt["token_scope_claim"] = "TOKEN_VAZIO_FINE_GRAINED_SCOPE_NOT_INFERRED"
    else:
        receipt["gaps"].append("TOKEN_VAZIO_REPOSITORY_ACCESS")

    return receipt, 0 if receipt["repository_access_observed"] else 5


def current_branch() -> str:
    proc = subprocess.run(
        ["git", "branch", "--show-current"],
        check=False,
        capture_output=True,
        text=True,
    )
    return proc.stdout.strip() if proc.returncode == 0 else ""


def _has_force_flag(args: Sequence[str]) -> bool:
    force_flags = {"-f", "--force", "--force-with-lease", "--force-if-includes"}
    return any(arg in force_flags or arg.startswith("--force=") for arg in args)


def classify_command(argv: Sequence[str], branch: str | None = None) -> tuple[bool, str]:
    if not argv:
        return False, "EMPTY_COMMAND"

    root = argv[0]
    args = list(argv[1:])

    if root == "git":
        if not args or args[0] != "push":
            return False, "ONLY_GIT_PUSH_IS_GOVERNED_HERE"
        rest = args[1:]
        if _has_force_flag(rest):
            return False, "FORCE_PUSH_FORBIDDEN"
        br = branch or current_branch()
        if br in PROTECTED_BRANCHES or not br.startswith(WORK_PREFIXES):
            return False, "PUSH_REQUIRES_AGENT_OR_WORK_BRANCH"
        joined = " ".join(rest)
        if any(
            f"refs/heads/{protected}" in joined or f":{protected}" in joined
            for protected in PROTECTED_BRANCHES
        ):
            return False, "PROTECTED_BRANCH_PUSH_FORBIDDEN"
        return True, "ALLOW_WORK_BRANCH_PUSH"

    if root != "gh":
        return False, "ONLY_GH_OR_GIT_SUPPORTED"
    if not args:
        return False, "EMPTY_GH_COMMAND"

    area = args[0]
    rest = args[1:]

    if area in {"secret", "variable"}:
        return False, "SECRET_OR_VARIABLE_MUTATION_FORBIDDEN"

    if area == "api":
        method = "GET"
        for i, arg in enumerate(rest):
            if arg in {"-X", "--method"} and i + 1 < len(rest):
                method = rest[i + 1].upper()
            elif arg.startswith("--method="):
                method = arg.split("=", 1)[1].upper()
        if method != "GET":
            return False, "MUTATING_GH_API_FORBIDDEN"
        return True, "ALLOW_READONLY_GH_API"

    if not rest:
        return False, "GH_SUBCOMMAND_REQUIRED"
    sub = rest[0]

    if area == "auth":
        return (
            (True, "ALLOW_AUTH_STATUS")
            if sub == "status"
            else (False, "AUTH_MUTATION_FORBIDDEN")
        )

    if area == "repo":
        return (
            (True, "ALLOW_REPO_VIEW")
            if sub == "view"
            else (False, "REPO_MUTATION_NOT_ALLOWLISTED")
        )

    if area == "pr":
        if sub == "merge":
            return False, "PR_MERGE_FORBIDDEN"
        allowed = {"create", "edit", "comment", "view", "list", "checks", "diff", "status", "ready"}
        return (
            (True, "ALLOW_PR_OPERATION")
            if sub in allowed
            else (False, "PR_OPERATION_NOT_ALLOWLISTED")
        )

    if area == "issue":
        allowed = {"create", "edit", "comment", "view", "list", "status"}
        return (
            (True, "ALLOW_ISSUE_OPERATION")
            if sub in allowed
            else (False, "ISSUE_OPERATION_NOT_ALLOWLISTED")
        )

    if area == "workflow":
        allowed = {"run", "view", "list"}
        return (
            (True, "ALLOW_WORKFLOW_OPERATION")
            if sub in allowed
            else (False, "WORKFLOW_OPERATION_NOT_ALLOWLISTED")
        )

    if area == "run":
        if sub in {"delete", "cancel"}:
            return False, "RUN_CANCEL_DELETE_FORBIDDEN"
        allowed = {"rerun", "view", "list", "watch", "download"}
        return (
            (True, "ALLOW_RUN_OPERATION")
            if sub in allowed
            else (False, "RUN_OPERATION_NOT_ALLOWLISTED")
        )

    if area == "release":
        return (
            (True, "ALLOW_RELEASE_READ")
            if sub in {"view", "list"}
            else (False, "RELEASE_MUTATION_NOT_ALLOWLISTED")
        )

    return False, "GH_AREA_NOT_ALLOWLISTED"


def sanitized_command(argv: Sequence[str]) -> list[str]:
    out: list[str] = []
    redact_next = False
    for arg in argv:
        if redact_next:
            out.append("REDACTED")
            redact_next = False
            continue
        if arg in {"--token", "--password", "--auth-token"}:
            out.append(arg)
            redact_next = True
            continue
        lowered = arg.lower()
        if "authorization:" in lowered or "bearer " in lowered:
            out.append("REDACTED_AUTH_ARGUMENT")
            continue
        out.append(arg)
    return out


def emit(receipt: dict[str, Any], path: Path | None) -> None:
    text = json.dumps(receipt, indent=2, ensure_ascii=False) + "\n"
    if path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)


def guarded_exec(argv: Sequence[str], receipt_path: Path | None = None) -> int:
    allowed, decision = classify_command(argv)
    receipt: dict[str, Any] = {
        "schema": "rll.agent_guard_execution.v1",
        "timestamp_utc": utc_now(),
        "command": sanitized_command(argv),
        "allowed": allowed,
        "decision": decision,
        "branch": current_branch() or TOKEN_VAZIO,
        "claim_allowed": False
    }

    if not allowed:
        receipt["returncode"] = 126
        emit(receipt, receipt_path)
        return 126

    try:
        _source, token = resolve_pat()
    except AuthorityError as exc:
        receipt["returncode"] = 125
        receipt["gap"] = str(exc)
        emit(receipt, receipt_path)
        return 125

    if not token:
        receipt["returncode"] = 125
        receipt["gap"] = "TOKEN_VAZIO_AGENT_GITHUB_PAT"
        emit(receipt, receipt_path)
        return 125

    env = os.environ.copy()
    env["GH_TOKEN"] = token
    proc = subprocess.run(list(argv), env=env, check=False)
    receipt["returncode"] = proc.returncode
    receipt["execution_observed"] = True
    emit(receipt, receipt_path)
    return proc.returncode


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_probe = sub.add_parser("probe")
    p_probe.add_argument(
        "--repository",
        default=os.environ.get(
            "GITHUB_REPOSITORY",
            "instituto-Rafael/relativity-living-light"
        ),
    )
    p_probe.add_argument("--output")

    p_check = sub.add_parser("check")
    p_check.add_argument("--branch")
    p_check.add_argument("command", nargs=argparse.REMAINDER)

    p_exec = sub.add_parser("exec")
    p_exec.add_argument("--receipt")
    p_exec.add_argument("command", nargs=argparse.REMAINDER)

    args = parser.parse_args()

    if args.cmd == "probe":
        receipt, rc = probe(args.repository)
        emit(receipt, Path(args.output) if args.output else None)
        return rc

    command = list(args.command)
    if command and command[0] == "--":
        command = command[1:]

    if args.cmd == "check":
        allowed, decision = classify_command(command, branch=args.branch)
        print(
            json.dumps(
                {
                    "allowed": allowed,
                    "decision": decision,
                    "command": sanitized_command(command),
                },
                indent=2,
            )
        )
        return 0 if allowed else 126

    return guarded_exec(
        command,
        Path(args.receipt) if getattr(args, "receipt", None) else None,
    )


if __name__ == "__main__":
    raise SystemExit(main())
