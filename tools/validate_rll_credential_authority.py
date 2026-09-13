#!/usr/bin/env python3
"""Fail-closed credential-authority audit for RLL repository secrets.

Canonical repository secrets:
- GITPAT: manual read-only GitHub authentication assurance only.
- RLL_CLIMATE_ENGINE_TRIAL_TOKEN: manual Climate Engine provider-read jobs only.

Secret values are never read by this static audit, persisted, hashed, or logged.
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
GITHUB_SECRET = "GITPAT"
CLIMATE_SECRET = "RLL_CLIMATE_ENGINE_TRIAL_TOKEN"
GITHUB_ASSURANCE_WORKFLOW = ".github/workflows/rll-repository-pat-assurance.yml"

GITHUB_SECRET_REF_RE = re.compile(rf"secrets\.{re.escape(GITHUB_SECRET)}\b", re.IGNORECASE)
LEGACY_PAT_SECRET_REF_RE = re.compile(
    r"secrets\.(?:RLL_GITHUB_AUTOMATION_PAT|RLL_GITHUB_PAT|GITHUB_PAT|GH_PAT|PAT_GIT|GIT_PAT)\b",
    re.IGNORECASE,
)
CLIMATE_SECRET_REF_RE = re.compile(
    rf"secrets\.{re.escape(CLIMATE_SECRET)}\b",
    re.IGNORECASE,
)
DESTRUCTIVE_RE = re.compile(
    r"(?:\bcurl\b[^\n]*(?:-X|--request)\s*(?:POST|PUT|PATCH|DELETE)\b|"
    r"\bgh\s+api\b[^\n]*(?:-X|--method)\s*(?:POST|PUT|PATCH|DELETE)\b|"
    r"\bgit\s+push\b|"
    r"\brequests\.(?:post|put|patch|delete)\s*\(|"
    r"\bhttpx\.(?:post|put|patch|delete)\s*\()",
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


def _audit_secret_job(
    findings: list[Finding],
    rel: str,
    doc: dict[str, Any],
    secret_re: re.Pattern[str],
    code_prefix: str,
) -> None:
    if "pull_request_target" in _triggers(doc):
        findings.append(Finding(
            "ERROR", "PULL_REQUEST_TARGET_SECRET", rel,
            "credential-bearing workflow cannot use pull_request_target",
        ))

    for job_id, raw_job in (doc.get("jobs") or {}).items():
        if not isinstance(raw_job, dict):
            continue
        job_text = json.dumps(raw_job, ensure_ascii=False)
        if not secret_re.search(job_text):
            continue
        if not _contains_manual_guard(raw_job):
            findings.append(Finding(
                "ERROR", f"{code_prefix}_NON_MANUAL", rel,
                "job consuming a repository secret must be guarded by workflow_dispatch",
                str(job_id),
            ))
        if DESTRUCTIVE_RE.search(job_text):
            findings.append(Finding(
                "ERROR", "DESTRUCTIVE_OPERATION_WITH_SECRET", rel,
                "mutating remote operations are forbidden in repository-secret probe jobs",
                str(job_id),
            ))
        if SECRET_DUMP_RE.search(job_text):
            findings.append(Finding(
                "ERROR", "SECRET_DUMP_RISK", rel,
                "shell tracing or environment dumping is forbidden in a credential-bearing job",
                str(job_id),
            ))


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
    if policy.get("canonical_secret_surface") != "GITHUB_ACTIONS_REPOSITORY_SECRETS":
        findings.append(Finding("ERROR", "SECRET_SURFACE", policy_path.as_posix(), "canonical secret surface must be repository secrets"))

    secrets = policy.get("repository_secrets") or {}
    github = secrets.get("github_pat") or {}
    climate = secrets.get("climate_engine_trial") or {}
    if github.get("secret_name") != GITHUB_SECRET:
        findings.append(Finding("ERROR", "GITHUB_SECRET_NAME", policy_path.as_posix(), f"GitHub repository secret must be {GITHUB_SECRET}"))
    if github.get("allowed_workflow") != GITHUB_ASSURANCE_WORKFLOW:
        findings.append(Finding("ERROR", "GITHUB_ASSURANCE_WORKFLOW", policy_path.as_posix(), "GITPAT must be confined to the reviewed assurance workflow"))
    if github.get("actions_allowed_event") != "workflow_dispatch_only":
        findings.append(Finding("ERROR", "GITHUB_EVENT_BOUNDARY", policy_path.as_posix(), "GITPAT assurance must remain manual-only"))
    if climate.get("secret_name") != CLIMATE_SECRET:
        findings.append(Finding("ERROR", "CLIMATE_SECRET_NAME", policy_path.as_posix(), f"Climate repository secret must be {CLIMATE_SECRET}"))
    if climate.get("actions_allowed_event") != "workflow_dispatch_only":
        findings.append(Finding("ERROR", "CLIMATE_EVENT_BOUNDARY", policy_path.as_posix(), "Climate trial credential must remain manual-only"))

    credential_workflows: list[str] = []
    for workflow in sorted((repo_root / WORKFLOW_ROOT).glob("*.y*ml")):
        rel = workflow.relative_to(repo_root).as_posix()
        text = workflow.read_text(encoding="utf-8")

        if LEGACY_PAT_SECRET_REF_RE.search(text):
            findings.append(Finding(
                "ERROR", "GITHUB_PAT_IN_ACTIONS_FORBIDDEN", rel,
                "legacy/alternate PAT secret names are forbidden; canonical repository secret is GITPAT",
            ))

        has_gitpat = bool(GITHUB_SECRET_REF_RE.search(text))
        has_climate = bool(CLIMATE_SECRET_REF_RE.search(text))
        if has_gitpat or has_climate:
            credential_workflows.append(rel)

        if has_gitpat:
            if rel != GITHUB_ASSURANCE_WORKFLOW:
                findings.append(Finding(
                    "ERROR", "GITPAT_OUTSIDE_ASSURANCE_WORKFLOW", rel,
                    "GITPAT may only be consumed by the reviewed read-only assurance workflow",
                ))
            try:
                doc = _load_yaml(workflow)
            except Exception as exc:  # noqa: BLE001
                findings.append(Finding("ERROR", "WORKFLOW_PARSE", rel, str(exc)))
            else:
                _audit_secret_job(findings, rel, doc, GITHUB_SECRET_REF_RE, "GITPAT")

        if has_climate:
            try:
                doc = _load_yaml(workflow)
            except Exception as exc:  # noqa: BLE001
                findings.append(Finding("ERROR", "WORKFLOW_PARSE", rel, str(exc)))
            else:
                _audit_secret_job(findings, rel, doc, CLIMATE_SECRET_REF_RE, "CLIMATE_TRIAL")

        if has_gitpat and has_climate:
            findings.append(Finding(
                "ERROR", "CROSS_CREDENTIAL_SAME_WORKFLOW", rel,
                "GITPAT and Climate repository secret must not be consumed by the same workflow",
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
        "canonical_repository_secrets": [GITHUB_SECRET, CLIMATE_SECRET],
        "gitpat_runtime_state": "TOKEN_VAZIO_UNTIL_GITPAT_ASSURANCE_DISPATCH",
        "climate_actions_secret_present": climate_actions_secret_present if runtime_checked else "TOKEN_VAZIO_EXTERNAL_SETTING",
        "secret_value_observed": False,
        "secret_value_hashed": False,
        "credential_workflows": sorted(set(credential_workflows)),
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
        "canonical_repository_secrets": payload["canonical_repository_secrets"],
        "climate_actions_secret_present": payload["climate_actions_secret_present"],
        "secret_value_observed": False,
        "residuals": payload["residuals"],
    }, ensure_ascii=False, indent=2))

    return 1 if args.strict and payload["decision"] != "PASS" else 0


if __name__ == "__main__":
    sys.exit(main())
