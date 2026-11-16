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


def _strip_plain_yaml_comment(value: str) -> str:
    """Strip a YAML plain-scalar comment while preserving quoted # characters."""
    quote = ""
    escaped = False
    for index, char in enumerate(value):
        if quote == '"':
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = ""
            continue
        if quote == "'":
            if char == quote:
                if index + 1 < len(value) and value[index + 1] == quote:
                    continue
                quote = ""
            continue
        if char in ("'", '"'):
            quote = char
        elif char == "#" and (index == 0 or value[index - 1].isspace()):
            return value[:index].rstrip()
    return value.rstrip()


def _load_yaml(path: Path) -> dict[str, Any]:
    """Fail-closed, dependency-free scanner for the narrow credential audit.

    Extract only workflow triggers, job boundaries, job-level guards and raw
    job text. This is NOT a general YAML parser; unsupported layouts fail.
    """
    source = path.read_text(encoding="utf-8")
    events: list[str] = []
    jobs: dict[str, dict[str, str]] = {}
    section = ""
    active: str | None = None
    lines: list[str] = []
    guard = ""
    folded = False
    trigger_indent: int | None = None
    credential = re.compile(r"secrets\.(?:GITPAT|CLIMA)\b", re.IGNORECASE)

    def finish() -> None:
        if active is not None:
            if active in jobs:
                raise ValueError("duplicate workflow job")
            jobs[active] = {"if": guard, "_raw": "\n".join(lines)}

    for raw in source.splitlines():
        stripped = raw.strip()
        if "\t" in raw[:len(raw) - len(raw.lstrip())]:
            raise ValueError("tab indentation in credential workflow")
        if not stripped or stripped.startswith("#"):
            if section == "jobs" and active is not None:
                lines.append(raw)
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        if indent == 0:
            if section == "jobs":
                finish()
            active, guard, folded, section = None, "", False, ""
            trigger_indent = None
            event = re.fullmatch(r"""(?:on|'on'|"on"):\s*(.*)""", stripped)
            if event is not None:
                section = "on"
                val = event.group(1).split("#", 1)[0].strip()
                if val.startswith("[") and val.endswith("]"):
                    events.extend(
                        item.strip().strip("'\"")
                        for item in val[1:-1].split(",") if item.strip()
                    )
                elif re.fullmatch(r"[A-Za-z_][\w-]*", val):
                    events.append(val)
                elif val:
                    raise ValueError("unsupported workflow trigger syntax")
            elif stripped == "jobs:":
                section = "jobs"
            elif credential.search(raw):
                raise ValueError("credential outside explicit job")
            continue
        if section == "on":
            if trigger_indent is None:
                trigger_indent = indent
            if indent < trigger_indent:
                raise ValueError("unsupported workflow trigger indentation")
            if indent == trigger_indent:
                event = re.match(
                    r"""^(?:'([^']+)'|"([^"]+)"|([A-Za-z_][\w-]*)):(?:\s|$)""",
                    stripped,
                )
                if event:
                    events.append(next(group for group in event.groups() if group is not None))
                elif stripped.startswith("- "):
                    item = _strip_plain_yaml_comment(stripped[2:]).strip().strip("'\\\"")
                    if not re.fullmatch(r"[A-Za-z_][\w-]*", item):
                        raise ValueError("unsupported workflow trigger list item")
                    events.append(item)
                else:
                    raise ValueError("unsupported workflow trigger declaration")
            elif credential.search(raw):
                raise ValueError("credential inside trigger")
            continue
        if section != "jobs":
            if credential.search(raw):
                raise ValueError("credential outside explicit job")
            continue
        if indent == 2:
            finish()
            job = re.fullmatch(r"([A-Za-z_][\w-]*):(?:\s*#.*)?", stripped)
            if job is None:
                raise ValueError("unsupported job declaration")
            active, lines, guard, folded = job.group(1), [], "", False
            continue
        if active is None:
            if credential.search(raw):
                raise ValueError("credential without explicit job")
            continue
        lines.append(raw)
        if indent == 4:
            match = re.match(r"^if:\s*(.*?)\s*$", stripped)
            if match:
                value = _strip_plain_yaml_comment(match.group(1))
                folded = value in (">", ">-", "|", "|-")
                guard = "" if folded else value
            else:
                folded = False
        elif folded and indent > 4:
            guard += " " + stripped
    if section == "jobs":
        finish()
    if not jobs:
        raise ValueError("no explicit jobs detected")
    return {"on": events, "jobs": jobs}


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
    return bool(re.search(r"""\bgithub\.event_name\s*==\s*(['"])workflow_dispatch\1""", expr))


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
