#!/usr/bin/env python3
"""Audit the repository against a GitHub Actions professional capability model.

The gate distinguishes repository-local evidence from GitHub settings that must
be verified through repository/organization configuration. It never promotes a
scientific claim and preserves unknown external state as TOKEN_VAZIO.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml

SCHEMA = "rll.github_actions_capability.audit.v1"
DEFAULT_MATRIX = Path(".github/workflow-architecture/github-actions-capabilities.v1.yml")
DEFAULT_WORKFLOW_CONTRACT = Path(".github/workflow-contract.yml")
WORKFLOW_ROOT = Path(".github/workflows")
ASSURANCE_WORKFLOW = ".github/workflows/github-platform-assurance.yml"
FULL_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
EXTERNAL_USE_RE = re.compile(r"^(?!\./)([^/\s]+/[^@\s]+)@(.+)$")

REQUIRED_CAPABILITIES = {
    "workflow_syntax_and_events",
    "least_privilege_token",
    "immutable_action_pinning",
    "concurrency_and_timeouts",
    "reusable_workflows",
    "artifacts_and_receipts",
    "dependency_review",
    "codeql_actions_python",
    "dependabot_actions",
    "code_ownership",
    "security_policy",
    "branch_rulesets",
    "required_status_checks",
    "protected_environments",
    "secret_scanning_push_protection",
    "artifact_attestations",
    "oidc_boundary",
    "audit_log_and_settings_evidence",
}
ALLOWED_STATES = {
    "IMPLEMENTED_REPOSITORY",
    "IMPLEMENTED_WORKFLOW",
    "PARTIAL",
    "TOKEN_VAZIO_EXTERNAL_SETTING",
    "NOT_APPLICABLE_UNTIL_USED",
}


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    path: str
    message: str


def _load_yaml(path: Path, *, base_loader: bool = False) -> Any:
    text = path.read_text(encoding="utf-8")
    loader = yaml.BaseLoader if base_loader else yaml.SafeLoader
    return yaml.load(text, Loader=loader)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _workflow_paths(root: Path) -> list[Path]:
    base = root / WORKFLOW_ROOT
    return sorted({*base.glob("*.yml"), *base.glob("*.yaml")}) if base.exists() else []


def _add(findings: list[Finding], severity: str, code: str, path: str, message: str) -> None:
    findings.append(Finding(severity, code, path, message))


def audit(root: Path, matrix_path: Path, contract_path: Path) -> tuple[list[Finding], dict[str, Any]]:
    findings: list[Finding] = []
    matrix_file = root / matrix_path
    contract_file = root / contract_path

    for required in (matrix_file, contract_file):
        if not required.is_file():
            _add(findings, "ERROR", "REQUIRED_FILE_MISSING", required.relative_to(root).as_posix(), "required contract is absent")
    if findings:
        return findings, _payload(root, matrix_path, contract_path, findings, [], {})

    matrix = _load_yaml(matrix_file)
    contract = _load_yaml(contract_file)
    if not isinstance(matrix, dict) or matrix.get("schema") != "rll.github_actions_capabilities.v1":
        _add(findings, "ERROR", "MATRIX_SCHEMA", matrix_path.as_posix(), "unexpected capability matrix schema")
        matrix = {}
    if matrix.get("claim_allowed") is not False:
        _add(findings, "ERROR", "CLAIM_BOUNDARY", matrix_path.as_posix(), "capability matrix must keep claim_allowed=false")
    if not isinstance(contract, dict):
        _add(findings, "ERROR", "WORKFLOW_CONTRACT", contract_path.as_posix(), "workflow contract must be a mapping")
        contract = {}

    workflows = _workflow_paths(root)
    expected_count = (((contract.get("inventory") or {}).get("active_workflows")) if isinstance(contract, dict) else None)
    if expected_count != len(workflows):
        _add(
            findings,
            "ERROR",
            "WORKFLOW_COUNT_MISMATCH",
            contract_path.as_posix(),
            f"contract expects {expected_count}; discovered {len(workflows)}",
        )

    capabilities = matrix.get("capabilities") if isinstance(matrix, dict) else []
    if not isinstance(capabilities, list):
        _add(findings, "ERROR", "CAPABILITIES_TYPE", matrix_path.as_posix(), "capabilities must be a list")
        capabilities = []

    seen: set[str] = set()
    for index, raw in enumerate(capabilities):
        path = f"{matrix_path.as_posix()}#capabilities[{index}]"
        if not isinstance(raw, dict):
            _add(findings, "ERROR", "CAPABILITY_TYPE", path, "capability must be a mapping")
            continue
        capability_id = str(raw.get("id", "")).strip()
        state = str(raw.get("state", "")).strip()
        if not capability_id:
            _add(findings, "ERROR", "CAPABILITY_ID", path, "capability id is required")
            continue
        if capability_id in seen:
            _add(findings, "ERROR", "CAPABILITY_DUPLICATE", path, f"duplicate capability id: {capability_id}")
        seen.add(capability_id)
        if state not in ALLOWED_STATES:
            _add(findings, "ERROR", "CAPABILITY_STATE", path, f"unsupported state: {state}")
        evidence = raw.get("evidence", [])
        if not isinstance(evidence, list):
            _add(findings, "ERROR", "EVIDENCE_TYPE", path, "evidence must be a list")
            evidence = []
        if state in {"IMPLEMENTED_REPOSITORY", "IMPLEMENTED_WORKFLOW"}:
            if not evidence:
                _add(findings, "ERROR", "IMPLEMENTED_WITHOUT_EVIDENCE", path, "implemented capability needs repository evidence")
            for item in evidence:
                evidence_path = root / str(item)
                if not evidence_path.exists():
                    _add(findings, "ERROR", "EVIDENCE_MISSING", str(item), f"evidence for {capability_id} does not exist")
        if state == "TOKEN_VAZIO_EXTERNAL_SETTING":
            if raw.get("setting_scope") not in {"repository", "organization", "enterprise"}:
                _add(findings, "ERROR", "EXTERNAL_SCOPE", path, "external setting needs repository/organization/enterprise scope")
            if not str(raw.get("f_next", "")).strip():
                _add(findings, "ERROR", "EXTERNAL_NEXT_STEP", path, "TOKEN_VAZIO external state needs a verifiable F_next")
            if raw.get("verified") is True:
                _add(findings, "ERROR", "FALSE_EXTERNAL_VERIFICATION", path, "external setting cannot be marked verified without settings evidence")

    missing_ids = sorted(REQUIRED_CAPABILITIES - seen)
    if missing_ids:
        _add(findings, "ERROR", "REQUIRED_CAPABILITIES_MISSING", matrix_path.as_posix(), ", ".join(missing_ids))

    mutable_refs: list[dict[str, str]] = []
    forbidden_triggers: list[str] = []
    for workflow in workflows:
        rel = workflow.relative_to(root).as_posix()
        try:
            doc = _load_yaml(workflow, base_loader=True)
        except Exception as exc:  # noqa: BLE001
            _add(findings, "ERROR", "WORKFLOW_PARSE", rel, str(exc).replace("\n", " "))
            continue
        if not isinstance(doc, dict):
            _add(findings, "ERROR", "WORKFLOW_DOCUMENT", rel, "workflow must be a mapping")
            continue
        triggers = doc.get("on")
        if isinstance(triggers, dict) and "pull_request_target" in triggers:
            forbidden_triggers.append(rel)
            _add(findings, "ERROR", "PULL_REQUEST_TARGET_FORBIDDEN", rel, "untrusted PR target execution is forbidden")
        for job in (doc.get("jobs") or {}).values():
            if not isinstance(job, dict):
                continue
            for step in job.get("steps") or []:
                if not isinstance(step, dict) or not step.get("uses"):
                    continue
                uses = str(step["uses"])
                match = EXTERNAL_USE_RE.match(uses)
                if match and not FULL_SHA_RE.fullmatch(match.group(2)):
                    mutable_refs.append({"workflow": rel, "uses": uses})
                    severity = "ERROR" if rel == ASSURANCE_WORKFLOW else "WARNING"
                    _add(findings, severity, "MUTABLE_ACTION_REFERENCE", rel, uses)

    assurance = root / ASSURANCE_WORKFLOW
    if not assurance.is_file():
        _add(findings, "ERROR", "ASSURANCE_WORKFLOW_MISSING", ASSURANCE_WORKFLOW, "professional assurance workflow is absent")
    else:
        doc = _load_yaml(assurance, base_loader=True)
        jobs = doc.get("jobs") if isinstance(doc, dict) else {}
        required_jobs = {"platform-capability-contract", "dependency-review", "codeql"}
        missing_jobs = sorted(required_jobs - set(jobs or {}))
        if missing_jobs:
            _add(findings, "ERROR", "ASSURANCE_JOBS_MISSING", ASSURANCE_WORKFLOW, ", ".join(missing_jobs))

    return findings, _payload(root, matrix_path, contract_path, findings, workflows, {
        "capability_count": len(seen),
        "missing_capabilities": missing_ids,
        "mutable_action_references": mutable_refs,
        "forbidden_triggers": forbidden_triggers,
    })


def _payload(
    root: Path,
    matrix_path: Path,
    contract_path: Path,
    findings: list[Finding],
    workflows: list[Path],
    extra: dict[str, Any],
) -> dict[str, Any]:
    errors = [item for item in findings if item.severity == "ERROR"]
    warnings = [item for item in findings if item.severity == "WARNING"]
    matrix_file = root / matrix_path
    contract_file = root / contract_path
    return {
        "schema": SCHEMA,
        "claim_allowed": False,
        "publication_effect": "NONE",
        "matrix": matrix_path.as_posix(),
        "matrix_sha256": _sha256(matrix_file) if matrix_file.is_file() else "TOKEN_VAZIO",
        "workflow_contract": contract_path.as_posix(),
        "workflow_contract_sha256": _sha256(contract_file) if contract_file.is_file() else "TOKEN_VAZIO",
        "workflow_count": len(workflows),
        "errors": len(errors),
        "warnings": len(warnings),
        "decision": "FAIL" if errors else "PASS",
        "residual_state": "TOKEN_VAZIO_EXTERNAL_SETTINGS" if not errors else "BLOCKED",
        "findings": [asdict(item) for item in findings],
        **extra,
    }


def write_reports(payload: dict[str, Any], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "github_actions_capability_report.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    lines = [
        "# GitHub Platform Assurance Report",
        "",
        f"- decision: `{payload['decision']}`",
        f"- workflows: `{payload['workflow_count']}`",
        f"- errors: `{payload['errors']}`",
        f"- warnings: `{payload['warnings']}`",
        f"- residual_state: `{payload['residual_state']}`",
        "- claim_allowed: `false`",
        "- publication_effect: `NONE`",
        "",
        "| severity | code | path | message |",
        "|---|---|---|---|",
    ]
    for item in payload["findings"]:
        message = str(item["message"]).replace("|", "\\|")
        lines.append(f"| {item['severity']} | `{item['code']}` | `{item['path']}` | {message} |")
    (output_dir / "GITHUB_PLATFORM_ASSURANCE_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--matrix", type=Path, default=DEFAULT_MATRIX)
    parser.add_argument("--workflow-contract", type=Path, default=DEFAULT_WORKFLOW_CONTRACT)
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/github-platform-assurance"))
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--write-report", action="store_true")
    args = parser.parse_args()

    root = args.repo_root.resolve()
    findings, payload = audit(root, args.matrix, args.workflow_contract)
    if args.write_report:
        write_reports(payload, root / args.output_dir)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 1 if args.strict and payload["decision"] != "PASS" else 0


if __name__ == "__main__":
    sys.exit(main())
