#!/usr/bin/env python3
"""Validate that RLL workflow documentation matches executable GitHub Actions YAML.

This tool is intentionally structural. It verifies repository-local facts such as
workflow count, triggers, reusable-workflow delegation, job identifiers and the
language used in the human guide. It cannot inspect GitHub branch-protection
rules, so required-check statements remain explicitly classified as documented
recommendations unless external API evidence is attached.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

import yaml

REPO = Path(__file__).resolve().parents[1]
DEFAULT_CONTRACT = REPO / ".github" / "workflow-contract.yml"
DEFAULT_REPORT_DIR = REPO / "artifacts" / "workflow-docs"


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    message: str
    path: str | None = None


def load_yaml(path: Path) -> dict[str, Any]:
    """Load YAML with BaseLoader so the GitHub Actions key `on` stays a string."""
    loaded = yaml.load(path.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
    if not isinstance(loaded, dict):
        raise ValueError(f"{path}: top-level YAML must be a mapping")
    return loaded


def workflow_paths(repo: Path) -> list[Path]:
    root = repo / ".github" / "workflows"
    return sorted([*root.glob("*.yml"), *root.glob("*.yaml")])


def rel(path: Path, repo: Path) -> str:
    return path.relative_to(repo).as_posix()


def mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def sequence(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def scalar(value: Any) -> str:
    return "" if value is None else str(value)


def workflow_registry(repo: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in workflow_paths(repo):
        doc = load_yaml(path)
        on = mapping(doc.get("on"))
        jobs = mapping(doc.get("jobs"))
        rows.append(
            {
                "path": rel(path, repo),
                "name": scalar(doc.get("name")),
                "triggers": sorted(str(k) for k in on),
                "jobs": sorted(str(k) for k in jobs),
                "physical_steps": sum(
                    len(sequence(job.get("steps")))
                    for job in jobs.values()
                    if isinstance(job, dict) and "uses" not in job
                ),
                "reusable_jobs": sorted(
                    str(job_id)
                    for job_id, job in jobs.items()
                    if isinstance(job, dict) and "uses" in job
                ),
            }
        )
    return rows


def find_job(doc: dict[str, Any], job_id: str) -> dict[str, Any] | None:
    job = mapping(doc.get("jobs")).get(job_id)
    return job if isinstance(job, dict) else None


def validate_contract(repo: Path, contract_path: Path) -> tuple[list[Finding], dict[str, Any]]:
    findings: list[Finding] = []
    contract = load_yaml(contract_path)
    registry = workflow_registry(repo)
    by_path = {row["path"]: row for row in registry}

    expected_count = int(scalar(mapping(contract.get("inventory")).get("active_workflows")) or 0)
    if expected_count and len(registry) != expected_count:
        findings.append(
            Finding(
                "error",
                "WF_COUNT_MISMATCH",
                f"contract expects {expected_count} active workflows, discovered {len(registry)}",
                rel(contract_path, repo),
            )
        )

    canonical = mapping(contract.get("canonical_pipeline"))
    canonical_path = scalar(canonical.get("path"))
    pipeline_file = repo / canonical_path
    if not pipeline_file.exists():
        findings.append(Finding("error", "WF_CANONICAL_MISSING", "canonical pipeline file does not exist", canonical_path))
    else:
        pipeline = load_yaml(pipeline_file)
        actual_triggers = set(mapping(pipeline.get("on")))
        expected_triggers = {str(x) for x in sequence(canonical.get("triggers"))}
        missing_triggers = sorted(expected_triggers - actual_triggers)
        if missing_triggers:
            findings.append(
                Finding(
                    "error",
                    "WF_TRIGGER_MISSING",
                    f"canonical pipeline is missing triggers: {', '.join(missing_triggers)}",
                    canonical_path,
                )
            )

        job_id = scalar(canonical.get("job_id"))
        job = find_job(pipeline, job_id)
        if job is None:
            findings.append(Finding("error", "WF_JOB_MISSING", f"canonical job '{job_id}' not found", canonical_path))
        else:
            actual_steps = len(sequence(job.get("steps")))
            expected_steps = int(scalar(canonical.get("github_actions_steps")) or 0)
            if expected_steps and actual_steps != expected_steps:
                findings.append(
                    Finding(
                        "error",
                        "WF_PHYSICAL_STEPS_MISMATCH",
                        f"canonical job has {actual_steps} physical GitHub Actions steps; contract expects {expected_steps}",
                        canonical_path,
                    )
                )
            logical_steps = int(scalar(canonical.get("logical_steps")) or 0)
            job_name = scalar(job.get("name"))
            if logical_steps and f"01–{logical_steps}" not in job_name and f"01-{logical_steps}" not in job_name:
                findings.append(
                    Finding(
                        "error",
                        "WF_LOGICAL_STEPS_UNANCHORED",
                        f"canonical job name does not anchor logical range 01–{logical_steps}",
                        canonical_path,
                    )
                )

    for alias in sequence(contract.get("aliases")):
        if not isinstance(alias, dict):
            continue
        alias_path = scalar(alias.get("path"))
        alias_file = repo / alias_path
        if not alias_file.exists():
            findings.append(Finding("error", "WF_ALIAS_MISSING", "alias workflow does not exist", alias_path))
            continue
        alias_doc = load_yaml(alias_file)
        job_id = scalar(alias.get("job_id"))
        job = find_job(alias_doc, job_id)
        if job is None:
            findings.append(Finding("error", "WF_ALIAS_JOB_MISSING", f"alias job '{job_id}' not found", alias_path))
            continue
        expected_uses = scalar(alias.get("uses"))
        if scalar(job.get("uses")) != expected_uses:
            findings.append(
                Finding(
                    "error",
                    "WF_ALIAS_TARGET_MISMATCH",
                    f"alias uses '{scalar(job.get('uses'))}', expected '{expected_uses}'",
                    alias_path,
                )
            )
        expected_mode = scalar(alias.get("modo"))
        actual_mode = scalar(mapping(job.get("with")).get("modo"))
        if expected_mode and actual_mode != expected_mode:
            findings.append(
                Finding(
                    "error",
                    "WF_ALIAS_MODE_MISMATCH",
                    f"alias mode is '{actual_mode}', expected '{expected_mode}'",
                    alias_path,
                )
            )

    checks_contract = mapping(contract.get("documented_checks"))
    for check in sequence(checks_contract.get("checks")):
        if not isinstance(check, dict):
            continue
        path = scalar(check.get("workflow"))
        job_id = scalar(check.get("job_id"))
        row = by_path.get(path)
        if row is None:
            findings.append(Finding("error", "WF_CHECK_WORKFLOW_MISSING", "documented check workflow not found", path))
        elif job_id and job_id not in row["jobs"]:
            findings.append(
                Finding(
                    "error",
                    "WF_CHECK_JOB_MISSING",
                    f"documented check job '{job_id}' not found; actual jobs: {', '.join(row['jobs'])}",
                    path,
                )
            )

    docs = mapping(contract.get("documentation"))
    for path, markers in mapping(docs.get("required_markers")).items():
        target = repo / str(path)
        if not target.exists():
            findings.append(Finding("error", "WF_DOC_MISSING", "required workflow document is missing", str(path)))
            continue
        text = target.read_text(encoding="utf-8")
        for marker in sequence(markers):
            marker_text = str(marker)
            if marker_text not in text:
                findings.append(
                    Finding(
                        "error",
                        "WF_DOC_MARKER_MISSING",
                        f"required marker not found: {marker_text!r}",
                        str(path),
                    )
                )

    payload = {
        "schema": "rll.workflow_documentation_validation.v1",
        "contract": rel(contract_path, repo),
        "active_workflows": len(registry),
        "canonical_pipeline": canonical_path,
        "findings": [asdict(item) for item in findings],
        "passed": not any(item.severity == "error" for item in findings),
        "claim_boundary": (
            "This validator proves repository-local structural consistency only. "
            "It does not inspect GitHub branch-protection settings and does not validate scientific claims."
        ),
        "registry": registry,
    }
    return findings, payload


def write_reports(payload: dict[str, Any], report_dir: Path) -> None:
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / "workflow_registry.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    lines = [
        "# Workflow Documentation Consistency",
        "",
        f"- passed: `{str(payload['passed']).lower()}`",
        f"- active_workflows: `{payload['active_workflows']}`",
        f"- canonical_pipeline: `{payload['canonical_pipeline']}`",
        f"- claim_boundary: {payload['claim_boundary']}",
        "",
        "## Findings",
        "",
    ]
    if not payload["findings"]:
        lines.append("No inconsistencies found.")
    else:
        lines.extend(["| severity | code | path | message |", "|---|---|---|---|"])
        for item in payload["findings"]:
            lines.append(
                f"| {item['severity']} | `{item['code']}` | `{item.get('path') or ''}` | {item['message']} |"
            )
    lines.extend(["", "## Registry", "", "| workflow | triggers | jobs | physical steps |", "|---|---|---|---:|"])
    for row in payload["registry"]:
        lines.append(
            f"| `{row['path']}` | {', '.join(row['triggers'])} | {', '.join(row['jobs'])} | {row['physical_steps']} |"
        )
    (report_dir / "WORKFLOW_DOCS_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    parser.add_argument("--strict", action="store_true", help="Return non-zero when any error is found.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    contract_path = args.contract if args.contract.is_absolute() else REPO / args.contract
    findings, payload = validate_contract(REPO, contract_path)
    if args.write_report:
        report_dir = args.report_dir if args.report_dir.is_absolute() else REPO / args.report_dir
        write_reports(payload, report_dir)

    for item in findings:
        print(f"{item.severity.upper()} {item.code}: {item.path or '-'}: {item.message}")
    if not findings:
        print(f"Workflow documentation contract OK: {payload['active_workflows']} active workflows.")

    has_errors = any(item.severity == "error" for item in findings)
    return 1 if args.strict and has_errors else 0


if __name__ == "__main__":
    sys.exit(main())
