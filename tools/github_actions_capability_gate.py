#!/usr/bin/env python3
"""Audit repository-local GitHub Actions capabilities without inventing external state."""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any

import yaml

SCHEMA = "rll.github_actions_capability.audit.v2"
MATRIX = Path(".github/workflow-architecture/github-actions-capabilities.v2.yml")
CONTRACT = Path(".github/workflow-contract.yml")
ASSURANCE = Path(".github/workflows/github-platform-assurance-v2.yml")
FULL_SHA = re.compile(r"^[0-9a-f]{40}$")
EXTERNAL_USE = re.compile(r"^(?!\./)([^/\s]+/[^@\s]+)@(.+)$")
REQUIRED = {
    "workflow_syntax_and_events", "least_privilege_token", "immutable_action_pinning",
    "concurrency_and_timeouts", "reusable_workflows", "artifacts_and_receipts",
    "dependency_review", "codeql_actions_python", "dependabot_actions", "code_ownership",
    "security_policy", "branch_rulesets", "required_status_checks", "protected_environments",
    "secret_scanning_push_protection", "artifact_attestations", "oidc_boundary",
    "audit_log_and_settings_evidence",
}
LOCAL_STATES = {"IMPLEMENTED_REPOSITORY", "IMPLEMENTED_WORKFLOW", "PARTIAL"}
EXTERNAL_STATE = "TOKEN_VAZIO_EXTERNAL_SETTING"
ALLOWED = LOCAL_STATES | {EXTERNAL_STATE, "NOT_APPLICABLE_UNTIL_USED"}


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    path: str
    message: str


def load_yaml(path: Path, base: bool = False) -> Any:
    return yaml.load(path.read_text(encoding="utf-8"), Loader=yaml.BaseLoader if base else yaml.SafeLoader)


def workflow_paths(root: Path) -> list[Path]:
    return sorted({*(root / ".github/workflows").glob("*.yml"), *(root / ".github/workflows").glob("*.yaml")})


def audit(root: Path) -> tuple[list[Finding], dict[str, Any]]:
    findings: list[Finding] = []
    matrix_path, contract_path, assurance_path = root / MATRIX, root / CONTRACT, root / ASSURANCE
    for path in (matrix_path, contract_path, assurance_path):
        if not path.is_file():
            findings.append(Finding("ERROR", "REQUIRED_FILE_MISSING", path.relative_to(root).as_posix(), "required capability surface is absent"))
    if findings:
        return findings, payload(root, findings, [])

    matrix = load_yaml(matrix_path)
    contract = load_yaml(contract_path)
    workflows = workflow_paths(root)
    if matrix.get("schema") != "rll.github_actions_capabilities.v2" or matrix.get("claim_allowed") is not False:
        findings.append(Finding("ERROR", "MATRIX_BOUNDARY", MATRIX.as_posix(), "unexpected schema or claim boundary"))
    expected = int((contract.get("inventory") or {}).get("active_workflows", 0))
    if expected != len(workflows):
        findings.append(Finding("ERROR", "WORKFLOW_COUNT_MISMATCH", CONTRACT.as_posix(), f"expected {expected}; discovered {len(workflows)}"))

    seen: set[str] = set()
    for index, cap in enumerate(matrix.get("capabilities") or []):
        loc = f"{MATRIX.as_posix()}#capabilities[{index}]"
        if not isinstance(cap, dict):
            findings.append(Finding("ERROR", "CAPABILITY_TYPE", loc, "capability must be a mapping")); continue
        cid = str(cap.get("id", "")); state = str(cap.get("state", "")); seen.add(cid)
        if state not in ALLOWED:
            findings.append(Finding("ERROR", "CAPABILITY_STATE", loc, state))
        evidence = cap.get("evidence") or []
        if state in {"IMPLEMENTED_REPOSITORY", "IMPLEMENTED_WORKFLOW"}:
            if not evidence:
                findings.append(Finding("ERROR", "IMPLEMENTED_WITHOUT_EVIDENCE", loc, cid))
            for item in evidence:
                if not (root / str(item)).exists():
                    findings.append(Finding("ERROR", "EVIDENCE_MISSING", str(item), cid))
        if state == EXTERNAL_STATE:
            if cap.get("verified") is True:
                findings.append(Finding("ERROR", "FALSE_EXTERNAL_VERIFICATION", loc, cid))
            if cap.get("setting_scope") not in {"repository", "organization", "enterprise"}:
                findings.append(Finding("ERROR", "EXTERNAL_SCOPE", loc, cid))
            if not str(cap.get("f_next", "")).strip():
                findings.append(Finding("ERROR", "EXTERNAL_NEXT_STEP", loc, cid))
    missing = sorted(REQUIRED - seen)
    if missing:
        findings.append(Finding("ERROR", "REQUIRED_CAPABILITIES_MISSING", MATRIX.as_posix(), ", ".join(missing)))

    assurance = load_yaml(assurance_path, base=True)
    jobs = assurance.get("jobs") or {}
    for job_id in ("platform-capability-contract", "dependency-review", "codeql"):
        if job_id not in jobs:
            findings.append(Finding("ERROR", "ASSURANCE_JOB_MISSING", ASSURANCE.as_posix(), job_id))
    for job in jobs.values():
        if not isinstance(job, dict): continue
        for step in job.get("steps") or []:
            if not isinstance(step, dict) or not step.get("uses"): continue
            uses = str(step["uses"]); match = EXTERNAL_USE.match(uses)
            if match and not FULL_SHA.fullmatch(match.group(2)):
                findings.append(Finding("ERROR", "MUTABLE_ACTION_REFERENCE", ASSURANCE.as_posix(), uses))
    return findings, payload(root, findings, workflows)


def payload(root: Path, findings: list[Finding], workflows: list[Path]) -> dict[str, Any]:
    errors = [x for x in findings if x.severity == "ERROR"]
    return {
        "schema": SCHEMA,
        "claim_allowed": False,
        "publication_effect": "NONE",
        "workflow_count": len(workflows),
        "decision": "FAIL" if errors else "PASS",
        "residual_state": "BLOCKED" if errors else "TOKEN_VAZIO_EXTERNAL_SETTINGS",
        "findings": [asdict(x) for x in findings],
        "inputs_sha256": hashlib.sha256("\n".join(p.as_posix() for p in workflows).encode()).hexdigest(),
    }


def write_reports(data: dict[str, Any], out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    (out / "receipt.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    lines = ["# GitHub Platform Assurance V2", "", f"- decision: `{data['decision']}`", f"- workflows: `{data['workflow_count']}`", f"- residual_state: `{data['residual_state']}`", "- claim_allowed: `false`"]
    for item in data["findings"]:
        lines.append(f"- {item['severity']} `{item['code']}` `{item['path']}` — {item['message']}")
    (out / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    p = argparse.ArgumentParser(); p.add_argument("--repo-root", type=Path, default=Path(".")); p.add_argument("--strict", action="store_true"); p.add_argument("--write-report", action="store_true"); p.add_argument("--output-dir", type=Path, default=Path("artifacts/github-platform-assurance-v2")); args = p.parse_args()
    root = args.repo_root.resolve(); findings, data = audit(root)
    if args.write_report: write_reports(data, root / args.output_dir)
    print(json.dumps(data, indent=2, ensure_ascii=False))
    return 1 if args.strict and data["decision"] != "PASS" else 0


if __name__ == "__main__": sys.exit(main())
