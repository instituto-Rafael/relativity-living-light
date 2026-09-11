#!/usr/bin/env python3
"""Fail-closed credential-authority audit for RLL.

This module validates repository policy and workflow use of privileged
credentials without reading, hashing, logging, or persisting secret values.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml

SCHEMA = "rll.credential_authority.audit.v1"
DEFAULT_POLICY = Path("data/governance/RLL_CREDENTIAL_AUTHORITY_POLICY_V1.json")
WORKFLOW_ROOT = Path(".github/workflows")
CLIMATE_SECRET = "RLL_CLIMATE_ENGINE_TRIAL_TOKEN"

PAT_SECRET_REF_RE = re.compile(
    r"secrets\.(?:RLL_GITHUB_AUTOMATION_PAT|RLL_GITHUB_PAT|GITHUB_PAT|GH_PAT|PAT_GIT)\b",
    re.IGNORECASE,
)
CLIMATE_SECRET_REF_RE = re.compile(
    rf"secrets\.{re.escape(CLIMATE_SECRET)}\b",
    re.IGNORECASE,
)
DESTRUCTIVE_RE = re.compile(
    r"(?:\bcurl\b[^\n]*(?:-X|--request)\s*DELETE\b|"
    r"\bgh\s+api\b[^\n]*(?:-X|--method)\s*DELETE\b|"
    r"\bgit\s+push\b[^\n]*--delete\b|"
    r"\bgit\s+push\b[^\n]*:\s*refs/(?:heads|tags)/|"
    r"\brequests\.delete\s*\(|\bhttpx\.delete\s*\()",
    re.IGNORECASE,
)
SECRET_DUMP_RE = re.compile(
    r"(?:\bset\s+-x\b|\bprintenv\b|(?:^|[;&|])\s*env\s*(?:$|[;&|]))",
    re.IGNORECASE | re.MULTILINE,
)


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    path: str
    message: str
    job: str = ""


def _load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.load(path.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
    return payload if isinstance(payload, dict) else {}


def _triggers(doc: dict[str, Any]) -> set[str]:
    raw = doc.get("on")
    if isinstance(raw, str):
        return {raw}
    if isinstance(raw, list):
        return {str(item) for item in raw}
    if isinstance(raw, dict):
        return {str(item) for item in raw}
    return set()


def _contains_manual_guard(job: dict[str, Any]) -> bool:
    expr = str(job.get("if", ""))
    return "github.event_name" in expr and "workflow_dispatch" in expr


def audit(repo_root: Path, policy_path: Path = DEFAULT_POLICY) -> tuple[list[Finding], dict[str, Any]]:
    findings: list[Finding] = []
    full_policy = repo_root / policy_path
    if not full_policy.is_file():
        findings.append(Finding("ERROR", "POLICY_MISSING", policy_path.as_posix(), "credential policy is missing"))
        return findings, _payload(findings, False, False, [])

    try:
        policy = json.loads(full_policy.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        findings.append(Finding("ERROR", "POLICY_PARSE", policy_path.as_posix(), str(exc)))
        return findings, _payload(findings, False, False, [])

    if policy.get("schema") != "rll.credential_authority.v1":
        findings.append(Finding("ERROR", "POLICY_SCHEMA", policy_path.as_posix(), "unexpected policy schema"))
    if policy.get("claim_allowed") is not False:
        findings.append(Finding("ERROR", "CLAIM_BOUNDARY", policy_path.as_posix(), "claim_allowed must remain false"))
    if policy.get("canonical_repository") != "instituto-Rafael/relativity-living-light":
        findings.append(Finding("ERROR", "CANONICAL_REPOSITORY", policy_path.as_posix(), "canonical repository mismatch"))

    groups = policy.get("authority_groups") or {}
    github_pat = groups.get("github_agent_pat") or {}
    climate = groups.get("climate_engine_trial") or {}
    permissions = github_pat.get("fine_grained_permissions") or {}

    if permissions.get("administration") != "none":
        findings.append(Finding("ERROR", "PAT_ADMINISTRATION_FORBIDDEN", policy_path.as_posix(), "GitHub PAT Administration must be none"))
    if permissions.get("agent_secrets") != "none":
        findings.append(Finding("ERROR", "PAT_AGENT_SECRETS_WRITE_FORBIDDEN", policy_path.as_posix(), "runtime PAT must not manage Agent secrets"))
    if github_pat.get("actions_secret_binding") != "FORBIDDEN_BY_DEFAULT":
        findings.append(Finding("ERROR", "PAT_ACTIONS_BINDING", policy_path.as_posix(), "GitHub PAT must remain agent-only by default"))
    if climate.get("actions_secret_name") != CLIMATE_SECRET:
        findings.append(Finding("ERROR", "CLIMATE_SECRET_NAME", policy_path.as_posix(), f"Actions Climate secret must be {CLIMATE_SECRET}"))
    if climate.get("actions_allowed_event") != "workflow_dispatch_only":
        findings.append(Finding("ERROR", "CLIMATE_EVENT_BOUNDARY", policy_path.as_posix(), "trial credential must remain manual-only"))

    credential_workflows: list[str] = []
    for workflow in sorted((repo_root / WORKFLOW_ROOT).glob("*.y*ml")):
        rel = workflow.relative_to(repo_root).as_posix()
        text = workflow.read_text(encoding="utf-8")
        if PAT_SECRET_REF_RE.search(text):
            findings.append(Finding(
                "ERROR",
                "GITHUB_PAT_IN_ACTIONS_FORBIDDEN",
                rel,
                "same-repository Actions must use GITHUB_TOKEN; PAT binding requires a separate reviewed exception",
            ))

        if not CLIMATE_SECRET_REF_RE.search(text):
            continue

        credential_workflows.append(rel)
        try:
            doc = _load_yaml(workflow)
        except Exception as exc:  # noqa: BLE001
            findings.append(Finding("ERROR", "WORKFLOW_PARSE", rel, str(exc)))
            continue

        if "pull_request_target" in _triggers(doc):
            findings.append(Finding("ERROR", "PULL_REQUEST_TARGET_SECRET", rel, "trial credential cannot coexist with pull_request_target"))

        for job_id, raw_job in (doc.get("jobs") or {}).items():
            if not isinstance(raw_job, dict):
                continue
            job_text = json.dumps(raw_job, ensure_ascii=False)
            if not CLIMATE_SECRET_REF_RE.search(job_text):
                continue
            if not _contains_manual_guard(raw_job):
                findings.append(Finding(
                    "ERROR",
                    "CLIMATE_TRIAL_NON_MANUAL",
                    rel,
                    "job consuming the Climate trial secret must be guarded by workflow_dispatch",
                    str(job_id),
                ))
            if DESTRUCTIVE_RE.search(job_text):
                findings.append(Finding(
                    "ERROR",
                    "DESTRUCTIVE_OPERATION_WITH_SECRET",
                    rel,
                    "destructive remote operation is forbidden in a credential-bearing job",
                    str(job_id),
                ))
            if SECRET_DUMP_RE.search(job_text):
                findings.append(Finding(
                    "ERROR",
                    "SECRET_DUMP_RISK",
                    rel,
                    "shell tracing or environment dumping is forbidden in a credential-bearing job",
                    str(job_id),
                ))

    return findings, _payload(findings, False, False, credential_workflows)


def _payload(
    findings: list[Finding],
    runtime_checked: bool,
    climate_actions_secret_present: bool,
    credential_workflows: list[str],
) -> dict[str, Any]:
    errors = [item for item in findings if item.severity == "ERROR"]
    residuals: list[str] = []
    if runtime_checked and not climate_actions_secret_present:
        residuals.append("TOKEN_VAZIO_ACTIONS_CLIMATE_SECRET_BINDING")
    return {
        "schema": SCHEMA,
        "claim_allowed": False,
        "publication_effect": "NONE",
        "decision": "FAIL" if errors or residuals else "PASS",
        "errors": len(errors),
        "runtime_binding_checked": runtime_checked,
        "climate_actions_secret_present": climate_actions_secret_present if runtime_checked else "TOKEN_VAZIO_EXTERNAL_SETTING",
        "github_pat_actions_binding": "FORBIDDEN_BY_DEFAULT_USE_GITHUB_TOKEN",
        "secret_value_observed": False,
        "secret_value_hashed": False,
        "credential_workflows": credential_workflows,
        "residuals": residuals,
        "findings": [asdict(item) for item in findings],
    }


def write_report(payload: dict[str, Any], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--output", type=Path, default=Path("artifacts/governance/RLL_CREDENTIAL_AUTHORITY_RECEIPT.json"))
    parser.add_argument("--runtime-binding-check", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    root = args.repo_root.resolve()
    findings, payload = audit(root, args.policy)
    if args.runtime_binding_check:
        present = bool(os.environ.get(CLIMATE_SECRET))
        payload = _payload(findings, True, present, payload["credential_workflows"])

    if args.write_report:
        write_report(payload, root / args.output)

    print(json.dumps({
        "schema": payload["schema"],
        "decision": payload["decision"],
        "errors": payload["errors"],
        "runtime_binding_checked": payload["runtime_binding_checked"],
        "climate_actions_secret_present": payload["climate_actions_secret_present"],
        "secret_value_observed": False,
        "residuals": payload["residuals"],
    }, ensure_ascii=False, indent=2))

    return 1 if args.strict and payload["decision"] != "PASS" else 0


if __name__ == "__main__":
    sys.exit(main())
