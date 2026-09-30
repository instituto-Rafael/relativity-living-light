#!/usr/bin/env python3
"""Fail-closed credential-authority audit for RLL repository secrets.

Canonical repository secrets:
- GITPAT: manual read-only GitHub authentication assurance only.
- CLIMA: manual Climate Engine provider-read jobs only.

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


SCHEMA = "rll.credential_authority.audit.v1"
DEFAULT_POLICY = Path("data/governance/RLL_CREDENTIAL_AUTHORITY_POLICY_V1.json")
WORKFLOW_ROOT = Path(".github/workflows")
GITHUB_SECRET = "GITPAT"
CLIMATE_SECRET = "CLIMA"
GITHUB_ASSURANCE_WORKFLOW = ".github/workflows/rll-repository-pat-assurance.yml"

GITHUB_SECRET_REF_RE = re.compile(rf"secrets\.{re.escape(GITHUB_SECRET)}\b", re.IGNORECASE)
LEGACY_PAT_SECRET_REF_RE = re.compile(
    r"secrets\.(?:RLL_GITHUB_AUTOMATION_PAT|RLL_GITHUB_PAT|GITHUB_PAT|GH_PAT|PAT_GIT|GIT_PAT|PATGITHUB|GIT)\b",
    re.IGNORECASE,
)
LEGACY_CLIMATE_SECRET_REF_RE = re.compile(
    r"secrets\.(?:RLL_CLIMATE_ENGINE_TRIAL_TOKEN|CLIMATE)\b",
    re.IGNORECASE,
)
CLIMATE_SECRET_REF_RE = re.compile(
    rf"secrets\.{re.escape(CLIMATE_SECRET)}\b",
    re.IGNORECASE,
)
LEGACY_CLIMATE_SECRET_REF_RE = re.compile(
    r"secrets\.(?:RLL_CLIMATE_ENGINE_TRIAL_TOKEN|CLIMATE)\b",
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


def _yaml_key_at_indent(line: str, indent: int):
    if not line.strip() or line.lstrip().startswith("#"):
        return None
    actual = len(line) - len(line.lstrip(" "))
    if actual != indent:
        return None
    stripped = line.strip()
    match = re.match(r"^(?P<q>['\"]?)(?P<key>[A-Za-z0-9_.-]+)(?P=q):(?:\s*(?P<value>.*))?$", stripped)
    if not match:
        return None
    return match.group("key"), (match.group("value") or "").strip()


def _workflow_triggers(text: str) -> set[str]:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        parsed = _yaml_key_at_indent(line, 0)
        if not parsed or parsed[0] != "on":
            continue
        inline = parsed[1]
        if inline:
            value = inline.strip()
            if value.startswith("[") and value.endswith("]"):
                return {
                    item.strip().strip("'\"")
                    for item in value[1:-1].split(",")
                    if item.strip()
                }
            return {value.strip("'\"")}
        triggers: set[str] = set()
        for child in lines[index + 1:]:
            if not child.strip() or child.lstrip().startswith("#"):
                continue
            child_indent = len(child) - len(child.lstrip(" "))
            if child_indent == 0:
                break
            parsed_child = _yaml_key_at_indent(child, 2)
            if parsed_child:
                triggers.add(parsed_child[0])
        return triggers
    return set()


def _job_blocks(text: str) -> dict[str, str]:
    lines = text.splitlines()
    jobs_start = None
    for index, line in enumerate(lines):
        parsed = _yaml_key_at_indent(line, 0)
        if parsed and parsed[0] == "jobs":
            jobs_start = index + 1
            break
    if jobs_start is None:
        return {}

    blocks: dict[str, list[str]] = {}
    current: str | None = None
    for line in lines[jobs_start:]:
        if line.strip() and not line.lstrip().startswith("#"):
            indent = len(line) - len(line.lstrip(" "))
            if indent == 0:
                break
            parsed = _yaml_key_at_indent(line, 2)
            if parsed:
                current = parsed[0]
                blocks[current] = [line]
                continue
        if current is not None:
            blocks[current].append(line)
    return {name: "\n".join(lines_) for name, lines_ in blocks.items()}


def _contains_manual_guard_text(job_text: str) -> bool:
    for line in job_text.splitlines():
        parsed = _yaml_key_at_indent(line, 4)
        if parsed and parsed[0] == "if":
            expr = parsed[1]
            return "github.event_name" in expr and "workflow_dispatch" in expr
    return False


def _audit_secret_job(
    findings: list[Finding],
    rel: str,
    workflow_text: str,
    secret_re: re.Pattern[str],
    code_prefix: str,
) -> None:
    triggers = _workflow_triggers(workflow_text)
    if "pull_request_target" in triggers:
        findings.append(Finding(
            "ERROR", "PULL_REQUEST_TARGET_SECRET", rel,
            "credential-bearing workflow cannot use pull_request_target",
        ))

    matched_job = False
    for job_id, job_text in _job_blocks(workflow_text).items():
        if not secret_re.search(job_text):
            continue
        matched_job = True
        if not _contains_manual_guard_text(job_text):
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

    if secret_re.search(workflow_text) and not matched_job:
        findings.append(Finding(
            "ERROR", f"{code_prefix}_STRUCTURE_UNPARSED", rel,
            "secret reference was found outside a structurally parsed job; fail closed",
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

    agent_surface = policy.get("agent_secret_surface") or {}
    if agent_surface.get("surface") != "COPILOT_CLOUD_AGENT_SECRETS":
        findings.append(Finding("ERROR", "AGENT_SECRET_SURFACE", policy_path.as_posix(), "Copilot agent secret surface must be explicit"))
    if agent_surface.get("repository_secrets_declared_by_owner") != ["GIT"]:
        findings.append(Finding("ERROR", "AGENT_REPOSITORY_SECRET_NAMES", policy_path.as_posix(), "owner-declared Agent repository secret set must be [GIT]"))
    if agent_surface.get("organization_secrets_declared_by_owner") != ["CLIMATE", "PATGITHUB"]:
        findings.append(Finding("ERROR", "AGENT_ORG_SECRET_NAMES", policy_path.as_posix(), "owner-declared Agent organization secret set must be [CLIMATE, PATGITHUB]"))
    if agent_surface.get("actions_repository_secrets_are_distinct") is not True:
        findings.append(Finding("ERROR", "AGENT_ACTIONS_SURFACE_COLLISION", policy_path.as_posix(), "Agent and Actions secret surfaces must remain distinct"))

    credential_workflows: list[str] = []
    for workflow in sorted((repo_root / WORKFLOW_ROOT).glob("*.y*ml")):
        rel = workflow.relative_to(repo_root).as_posix()
        text = workflow.read_text(encoding="utf-8")

        if LEGACY_PAT_SECRET_REF_RE.search(text):
            findings.append(Finding(
                "ERROR", "GITHUB_PAT_IN_ACTIONS_FORBIDDEN", rel,
                "legacy/alternate PAT secret names are forbidden; canonical repository secret is GITPAT",
            ))
        if LEGACY_CLIMATE_SECRET_REF_RE.search(text):
            findings.append(Finding(
                "ERROR", "CLIMATE_SECRET_IN_ACTIONS_FORBIDDEN", rel,
                "legacy/Agent Climate secret names are forbidden in Actions; canonical Actions secret is CLIMA",
            ))

        if LEGACY_CLIMATE_SECRET_REF_RE.search(text):
            findings.append(Finding(
                "ERROR", "CLIMATE_SECRET_SURFACE_OR_NAME", rel,
                "Actions uses CLIMA; Agents CLIMATE and the historical Actions name are not implicit fallbacks",
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
            _audit_secret_job(findings, rel, text, GITHUB_SECRET_REF_RE, "GITPAT")

        if has_climate:
            _audit_secret_job(findings, rel, text, CLIMATE_SECRET_REF_RE, "CLIMATE_TRIAL")

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
    guard_names = [
        "provenance",
        "context",
        "evidence",
        "contradiction",
        "uncertainty",
        "reproduction",
        "rollback",
    ]
    finding_codes = [item.code for item in findings]
    runtime_state = "OBSERVED_BOOLEAN_ONLY" if runtime_checked else "TOKEN_VAZIO_RUNTIME"
    uncertainty_items = list(residuals)
    if not runtime_checked:
        uncertainty_items.extend([
            "TOKEN_VAZIO_ACTIONS_RUNTIME_BINDING",
            "TOKEN_VAZIO_AGENT_RUNTIME",
            "TOKEN_VAZIO_ORGANIZATION_SECRET_INHERITANCE_SCOPE",
        ])
    return {
        "schema": SCHEMA,
        "claim_allowed": False,
        "publication_effect": "NONE",
        "decision": "FAIL" if errors or residuals else "PASS",
        "errors": len(errors),
        "runtime_binding_checked": runtime_checked,
        "canonical_repository_secrets": [GITHUB_SECRET, CLIMATE_SECRET],
        "agent_secret_surface": {
            "repository": ["GIT"],
            "organization": ["CLIMATE", "PATGITHUB"],
            "runtime_state": "TOKEN_VAZIO_AGENT_RUNTIME",
        },
        "gitpat_runtime_state": "TOKEN_VAZIO_UNTIL_GITPAT_ASSURANCE_DISPATCH",
        "climate_actions_secret_present": climate_actions_secret_present if runtime_checked else "TOKEN_VAZIO_EXTERNAL_SETTING",
        "secret_value_observed": False,
        "secret_value_hashed": False,
        "credential_workflows": sorted(set(credential_workflows)),
        "guards": guard_names,
        "provenance": {
            "authority": "instituto-Rafael/relativity-living-light",
            "policy": DEFAULT_POLICY.as_posix(),
            "credential_workflows": sorted(set(credential_workflows)),
        },
        "context": {
            "scope": "Copilot Agent and GitHub Actions credential authority separation",
            "boundary": "secret presence/authentication is not repository authority, scientific evidence, or claim promotion",
        },
        "evidence": {
            "state": runtime_state,
            "runtime_binding_checked": runtime_checked,
            "actions_climate_binding_present_boolean": climate_actions_secret_present if runtime_checked else "TOKEN_VAZIO",
            "secret_material_persisted": False,
        },
        "contradiction": {
            "state": "OPEN" if finding_codes else "NONE_DETECTED_STATIC",
            "finding_codes": finding_codes,
        },
        "uncertainty": {
            "state": "OPEN" if uncertainty_items else "BOUNDED_FOR_THIS_CHECK",
            "open_items": uncertainty_items,
        },
        "reproduction": {
            "state": "READY",
            "procedure": "python3 tools/validate_rll_credential_authority.py --strict --write-report",
        },
        "rollback": {
            "state": "READY",
            "anchor": os.environ.get("GITHUB_SHA", "TOKEN_VAZIO_GIT_ANCHOR"),
            "procedure": "revert only the credential-surface mapping change; preserve all prior receipts and findings",
        },
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
