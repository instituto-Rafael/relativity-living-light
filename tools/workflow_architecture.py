#!/usr/bin/env python3
"""Validate YAML syntax and GitHub Actions architecture invariants.

YAML remains a declarative orchestration layer. Scientific algorithms and long
programs belong in tested repository modules, scripts, composite actions, or
reusable workflows. This auditor emits machine-readable receipts and never
promotes a scientific claim.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Iterable

import yaml

SCHEMA = "rll.github_actions_architecture.audit.v1"
DEFAULT_CONTRACT = Path(".github/workflow-architecture/invariants.v1.yml")
WORKFLOW_ROOT = Path(".github/workflows")
EXTERNAL_ACTION_RE = re.compile(r"^(?!\./)([^/\s]+/[^@\s]+)@(.+)$")
FULL_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
UNTRUSTED_CONTEXT_RE = re.compile(
    r"\$\{\{\s*github\.(?:event\.)?(?:"
    r".*(?:title|body|head_ref|message|email|label|name|ref)"
    r")\s*\}\}",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    path: str
    message: str
    job: str | None = None
    step: str | None = None


@dataclass(frozen=True)
class ParsedYaml:
    path: str
    status: str
    documents: int
    sha256: str
    error: str


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def iter_yaml(repo_root: Path) -> Iterable[Path]:
    files = [*repo_root.rglob("*.yml"), *repo_root.rglob("*.yaml")]
    for path in sorted(set(files)):
        if ".git" not in path.parts:
            yield path


def iter_workflows(repo_root: Path) -> Iterable[Path]:
    root = repo_root / WORKFLOW_ROOT
    if not root.exists():
        return
    yield from sorted(root.glob("*.yml"))
    yield from sorted(root.glob("*.yaml"))


def parse_all_yaml(repo_root: Path) -> list[ParsedYaml]:
    rows: list[ParsedYaml] = []
    for path in iter_yaml(repo_root):
        raw = path.read_bytes()
        rel = path.relative_to(repo_root).as_posix()
        try:
            documents = len(list(yaml.safe_load_all(raw.decode("utf-8"))))
            rows.append(ParsedYaml(rel, "OK", documents, sha256_bytes(raw), ""))
        except Exception as exc:  # noqa: BLE001 - receipt must preserve parser failure.
            rows.append(
                ParsedYaml(
                    rel,
                    "FAIL",
                    0,
                    sha256_bytes(raw),
                    str(exc).replace("\n", " "),
                )
            )
    return rows


def parse_workflow(path: Path) -> dict[str, Any]:
    """Use BaseLoader so the GitHub Actions key ``on`` remains a string."""
    loaded = yaml.load(path.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
    if not isinstance(loaded, dict):
        raise ValueError("top-level workflow document must be a mapping")
    return loaded


def load_contract(repo_root: Path, contract_path: Path) -> dict[str, Any]:
    path = repo_root / contract_path
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("workflow architecture contract must be a mapping")
    if payload.get("schema") != "rll.github_actions_architecture.v1":
        raise ValueError("unexpected workflow architecture contract schema")
    if payload.get("claim_allowed") is not False:
        raise ValueError("workflow architecture contract must remain claim_allowed=false")
    return payload


def _mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _is_true(value: Any) -> bool:
    return str(value).strip().lower() == "true"


def _run_line_count(value: Any) -> int:
    if value is None:
        return 0
    return len(str(value).splitlines())


def _workflow_managed_policy(contract: dict[str, Any], rel: str) -> dict[str, Any] | None:
    managed = _mapping(contract.get("managed_workflows"))
    raw = managed.get(rel)
    return raw if isinstance(raw, dict) else None


def _finding(
    findings: list[Finding],
    severity: str,
    code: str,
    rel: str,
    message: str,
    job: str | None = None,
    step: str | None = None,
) -> None:
    findings.append(Finding(severity, code, rel, message, job, step))


def audit_workflow(
    repo_root: Path,
    path: Path,
    contract: dict[str, Any],
) -> list[Finding]:
    findings: list[Finding] = []
    rel = path.relative_to(repo_root).as_posix()
    managed = _workflow_managed_policy(contract, rel)
    managed_requirements = set(_list(managed.get("require"))) if managed else set()
    thresholds = _mapping(_mapping(contract.get("policy")).get("thresholds"))
    managed_limit = int(thresholds.get("max_inline_run_lines_managed", 24))
    legacy_limit = int(thresholds.get("max_inline_run_lines_legacy_warning", 50))

    try:
        doc = parse_workflow(path)
    except Exception as exc:  # noqa: BLE001
        _finding(findings, "ERROR", "WORKFLOW_PARSE", rel, str(exc))
        return findings

    for key in ("name", "on", "jobs"):
        if key not in doc:
            _finding(findings, "ERROR", "MISSING_REQUIRED_KEY", rel, f"missing top-level key: {key}")

    triggers = doc.get("on")
    if isinstance(triggers, dict) and "pull_request_target" in triggers:
        _finding(
            findings,
            "ERROR",
            "PULL_REQUEST_TARGET_FORBIDDEN",
            rel,
            "pull_request_target is forbidden without a versioned exception contract",
        )

    permissions = doc.get("permissions")
    if managed and "permissions" in managed_requirements:
        if not isinstance(permissions, dict) or not permissions:
            _finding(
                findings,
                "ERROR",
                "MANAGED_PERMISSIONS_MISSING",
                rel,
                "managed workflow must declare non-empty top-level permissions",
            )

    concurrency = doc.get("concurrency")
    if managed and "concurrency" in managed_requirements:
        if not isinstance(concurrency, dict) or not concurrency.get("group"):
            _finding(
                findings,
                "ERROR",
                "MANAGED_CONCURRENCY_MISSING",
                rel,
                "managed workflow must declare concurrency.group",
            )
    elif not concurrency:
        _finding(
            findings,
            "WARNING",
            "LEGACY_CONCURRENCY_MISSING",
            rel,
            "workflow has no concurrency policy; migration is incremental",
        )

    jobs = _mapping(doc.get("jobs"))
    if not jobs:
        _finding(findings, "ERROR", "JOBS_EMPTY", rel, "jobs must be a non-empty mapping")
        return findings

    for job_id, raw_job in jobs.items():
        if not isinstance(raw_job, dict):
            _finding(findings, "ERROR", "JOB_NOT_MAPPING", rel, "job must be a mapping", str(job_id))
            continue
        if "uses" in raw_job:
            continue
        if "runs-on" not in raw_job:
            _finding(findings, "ERROR", "JOB_RUNNER_MISSING", rel, "job lacks runs-on or uses", str(job_id))
        timeout = raw_job.get("timeout-minutes")
        if managed and "job_timeout" in managed_requirements and timeout is None:
            _finding(
                findings,
                "ERROR",
                "MANAGED_TIMEOUT_MISSING",
                rel,
                "managed runner job must declare timeout-minutes",
                str(job_id),
            )
        elif not managed and timeout is None:
            _finding(
                findings,
                "WARNING",
                "LEGACY_TIMEOUT_MISSING",
                rel,
                "runner job has no timeout-minutes",
                str(job_id),
            )

        steps = _list(raw_job.get("steps"))
        if not steps:
            _finding(findings, "ERROR", "JOB_STEPS_EMPTY", rel, "runner job needs steps", str(job_id))
            continue
        for index, raw_step in enumerate(steps):
            if not isinstance(raw_step, dict):
                _finding(
                    findings,
                    "ERROR",
                    "STEP_NOT_MAPPING",
                    rel,
                    f"step {index} must be a mapping",
                    str(job_id),
                )
                continue
            step_name = str(raw_step.get("name", f"step-{index}"))
            uses = raw_step.get("uses")
            if uses:
                match = EXTERNAL_ACTION_RE.match(str(uses))
                if match and not FULL_SHA_RE.fullmatch(match.group(2)):
                    _finding(
                        findings,
                        "WARNING",
                        "MUTABLE_ACTION_REFERENCE",
                        rel,
                        f"external action is not pinned to a full commit SHA: {uses}",
                        str(job_id),
                        step_name,
                    )
                if str(uses).startswith("actions/checkout@"):
                    persist = _mapping(raw_step.get("with")).get("persist-credentials")
                    if managed and "checkout_without_persistent_credentials" in managed_requirements:
                        if persist is None or _is_true(persist):
                            _finding(
                                findings,
                                "ERROR",
                                "CHECKOUT_CREDENTIALS_PERSIST",
                                rel,
                                "managed checkout must set persist-credentials: false",
                                str(job_id),
                                step_name,
                            )

            run = raw_step.get("run")
            if run is not None:
                run_text = str(run)
                lines = _run_line_count(run)
                if UNTRUSTED_CONTEXT_RE.search(run_text):
                    _finding(
                        findings,
                        "ERROR",
                        "UNTRUSTED_CONTEXT_IN_RUN",
                        rel,
                        "potentially attacker-controlled github context is interpolated into run",
                        str(job_id),
                        step_name,
                    )
                if managed and "externalized_algorithm" in managed_requirements and lines > managed_limit:
                    _finding(
                        findings,
                        "ERROR",
                        "OVERSIZED_INLINE_PROGRAM",
                        rel,
                        f"inline run block has {lines} lines; managed limit is {managed_limit}",
                        str(job_id),
                        step_name,
                    )
                elif not managed and lines > legacy_limit:
                    _finding(
                        findings,
                        "WARNING",
                        "LEGACY_INLINE_PROGRAM",
                        rel,
                        f"inline run block has {lines} lines; externalize algorithmic logic",
                        str(job_id),
                        step_name,
                    )
                if raw_step.get("continue-on-error") is not None:
                    _finding(
                        findings,
                        "WARNING",
                        "CONTINUE_ON_ERROR_REVIEW",
                        rel,
                        "continue-on-error requires an explicit residual/receipt path",
                        str(job_id),
                        step_name,
                    )

    if managed and "always_upload_receipt" in managed_requirements:
        text = path.read_text(encoding="utf-8")
        if "actions/upload-artifact@" not in text or "if: always()" not in text:
            _finding(
                findings,
                "ERROR",
                "RECEIPT_UPLOAD_MISSING",
                rel,
                "managed validation workflow must always upload an artifact receipt",
            )
    if managed and "claim_boundary" in managed_requirements:
        text = path.read_text(encoding="utf-8").lower()
        if "claim_allowed" not in text and "claim_boundary" not in text:
            _finding(
                findings,
                "ERROR",
                "CLAIM_BOUNDARY_MISSING",
                rel,
                "managed scientific/orchestrator workflow needs an explicit claim boundary",
            )

    return findings


def audit_repository(repo_root: Path, contract: dict[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    for path in iter_workflows(repo_root):
        findings.extend(audit_workflow(repo_root, path, contract))
    return sorted(
        findings,
        key=lambda item: (item.severity != "ERROR", item.path, item.job or "", item.step or "", item.code),
    )


def write_reports(
    output_dir: Path,
    repo_root: Path,
    contract_path: Path,
    yaml_rows: list[ParsedYaml],
    findings: list[Finding],
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    errors = [item for item in findings if item.severity == "ERROR"]
    warnings = [item for item in findings if item.severity == "WARNING"]
    yaml_failures = [row for row in yaml_rows if row.status == "FAIL"]
    workflow_count = sum(1 for _ in iter_workflows(repo_root))
    payload = {
        "schema": SCHEMA,
        "contract": contract_path.as_posix(),
        "contract_sha256": sha256_bytes((repo_root / contract_path).read_bytes()),
        "claim_allowed": False,
        "publication_effect": "NONE",
        "workflow_count": workflow_count,
        "yaml_files": len(yaml_rows),
        "yaml_failures": len(yaml_failures),
        "architecture_errors": len(errors),
        "architecture_warnings": len(warnings),
        "decision": "FAIL" if yaml_failures or errors else "PASS",
        "residuals": {
            "warnings": len(warnings),
            "action_sha_pinning": "TRANSITIONAL_WARNING",
            "legacy_normalization": "INCREMENTAL",
        },
        "findings": [asdict(item) for item in findings],
    }
    (output_dir / "workflow_architecture_report.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    with (output_dir / "yaml_parse_report.tsv").open("w", encoding="utf-8") as handle:
        handle.write("path\tstatus\tdocuments\tsha256\terror\n")
        for row in yaml_rows:
            handle.write(
                f"{row.path}\t{row.status}\t{row.documents}\t{row.sha256}\t{row.error}\n"
            )
    yaml_summary = {
        "schema": "rll.yml_syntax_validation_artifacts.v2",
        "total_yaml_files": len(yaml_rows),
        "failed_yaml_files": len(yaml_failures),
        "passed_yaml_files": len(yaml_rows) - len(yaml_failures),
        "claim_allowed": False,
        "claim_boundary": "YAML parseability and workflow hygiene are structural evidence only.",
    }
    (output_dir / "yaml_parse_summary.json").write_text(
        json.dumps(yaml_summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    md = [
        "# Workflow Architecture Ω Report",
        "",
        f"- decision: `{payload['decision']}`",
        f"- workflows: `{workflow_count}`",
        f"- YAML files: `{len(yaml_rows)}`",
        f"- YAML failures: `{len(yaml_failures)}`",
        f"- architecture errors: `{len(errors)}`",
        f"- architecture warnings: `{len(warnings)}`",
        "- claim_allowed: `false`",
        "- publication_effect: `NONE`",
        "",
        "| severity | code | path | job | step | message |",
        "|---|---|---|---|---|---|",
    ]
    for item in findings:
        message = item.message.replace("|", "\\|")
        md.append(
            f"| {item.severity} | `{item.code}` | `{item.path}` | "
            f"`{item.job or ''}` | `{item.step or ''}` | {message} |"
        )
    (output_dir / "WORKFLOW_ARCHITECTURE_REPORT.md").write_text(
        "\n".join(md) + "\n", encoding="utf-8"
    )
    return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/yml-syntax-validation"))
    parser.add_argument("--strict", action="store_true", help="Fail on YAML failures or architecture errors.")
    parser.add_argument(
        "--warnings-as-errors",
        action="store_true",
        help="Also fail on migration warnings; not enabled by the canonical gate yet.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    repo_root = args.repo_root.resolve()
    contract = load_contract(repo_root, args.contract)
    yaml_rows = parse_all_yaml(repo_root)
    findings = audit_repository(repo_root, contract)
    payload = write_reports(args.output_dir, repo_root, args.contract, yaml_rows, findings)
    print(json.dumps({key: payload[key] for key in (
        "decision",
        "workflow_count",
        "yaml_files",
        "yaml_failures",
        "architecture_errors",
        "architecture_warnings",
    )}, ensure_ascii=False, indent=2))
    failed = payload["decision"] == "FAIL"
    warning_failure = args.warnings_as_errors and payload["architecture_warnings"] > 0
    return 1 if args.strict and (failed or warning_failure) else 0


if __name__ == "__main__":
    sys.exit(main())
