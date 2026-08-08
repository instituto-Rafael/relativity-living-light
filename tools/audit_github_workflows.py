#!/usr/bin/env python3
"""Audit GitHub Actions workflow files and RLL validation YAML placement.

The GitHub workflow directory should contain only executable workflow YAML files.
Scientific/data YAML contracts belong in repository data/docs directories where
pipeline scripts can load them without making GitHub Actions parse them as jobs.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Iterable

import yaml

REPO = Path(__file__).resolve().parents[1]
WORKFLOWS = REPO / ".github" / "workflows"
VALIDATION_BUNDLE = REPO / "validacao_real"
VALIDATION_PATHS = REPO / "docs" / "pipelines" / "validation_paths"

NON_WORKFLOW_EXTENSIONS = {
    ".md",
    ".pdf",
    ".png",
    ".py",
    ".zip",
    ".json",
    ".csv",
    ".txt",
}

CANONICAL_REAL_DATA_WORKFLOW = ".github/workflows/real-data-complete-execution.yml"
SYNTHETIC_BOUNDARY_TERMS = ("synthetic", "mock", "fixture", "placeholder", "demo", "example")
REAL_DATA_IDENTITY_MARKERS = (
    "real-data",
    "real_data",
    "real data",
    "validacao_real",
    "validação real",
)
_ACTION_LINE_RE = re.compile(
    r"(?m)^\s*(?:-\s*)?uses:\s*actions/(?P<action>[A-Za-z0-9_.-]+)@(?P<ref>v\d+|[0-9a-fA-F]{40})\s*(?:#.*)?$"
)


def action_majors(text: str, action: str) -> list[int]:
    """Return explicit major versions used for one first-party GitHub action."""
    majors: list[int] = []
    for match in _ACTION_LINE_RE.finditer(text):
        if match.group("action") != action:
            continue
        ref = match.group("ref")
        if ref.startswith("v"):
            majors.append(int(ref[1:]))
    return majors


def _has_immutable_action_ref(text: str, action: str) -> bool:
    for match in _ACTION_LINE_RE.finditer(text):
        if match.group("action") == action and not match.group("ref").startswith("v"):
            return True
    return False


def has_supported_upload_artifact(text: str) -> bool:
    """Accept upload-artifact v4+ or a full immutable 40-hex SHA; reject v3."""
    return any(major >= 4 for major in action_majors(text, "upload-artifact")) or _has_immutable_action_ref(
        text, "upload-artifact"
    )


def has_checkout_action(text: str) -> bool:
    """Detect an explicit checkout action independently of its supported major."""
    return bool(action_majors(text, "checkout")) or _has_immutable_action_ref(text, "checkout")


def workflow_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def is_real_data_workflow(path: Path, doc: dict, text: str) -> bool:
    del text
    rel = path.relative_to(REPO).as_posix().lower()
    name = str(doc.get("name", "")).lower()
    identity = f"{rel}\n{name}"
    return any(marker in identity for marker in REAL_DATA_IDENTITY_MARKERS)


def audit_real_workflow_policy() -> list[str]:
    errors: list[str] = []
    for path in iter_workflow_yaml():
        try:
            doc = parse_yaml(path)
            text = workflow_text(path)
        except Exception:
            continue
        if not is_real_data_workflow(path, doc, text):
            continue
        rel = path.relative_to(REPO).as_posix()
        permissions = doc.get("permissions") or {}
        if not isinstance(permissions, dict) or permissions.get("contents") != "read":
            errors.append(f"{rel}: real workflow must declare top-level permissions.contents: read")
        if has_checkout_action(text) and "persist-credentials: false" not in text:
            errors.append(f"{rel}: real workflow checkout must set persist-credentials: false")
        if not has_supported_upload_artifact(text):
            errors.append(
                f"{rel}: real workflow must upload artifacts with actions/upload-artifact v4+ "
                "or a full immutable SHA"
            )
        if "rll_real_data_write_checksums" not in text and (
            "CHECKSUMS.sha256" not in text or "sha256sum" not in text
        ):
            errors.append(f"{rel}: real workflow must build a final CHECKSUMS.sha256 with sha256sum")
        if "CLAIM_BOUNDARY" not in text and "claim_boundary" not in text and "Claim Boundary" not in text:
            errors.append(f"{rel}: real workflow must declare an explicit claim boundary")
        lower = text.lower()
        if not any(term in lower for term in SYNTHETIC_BOUNDARY_TERMS):
            errors.append(f"{rel}: real workflow must declare boundary against synthetic/mock/fixture data")
        if rel != CANONICAL_REAL_DATA_WORKFLOW:
            canonical_env = f"CANONICAL_REAL_DATA_WORKFLOW: {CANONICAL_REAL_DATA_WORKFLOW}"
            canonical_shell = f"CANONICAL_REAL_DATA_WORKFLOW={CANONICAL_REAL_DATA_WORKFLOW}"
            if canonical_env not in text and canonical_shell not in text:
                errors.append(f"{rel}: non-canonical real workflow must point to {CANONICAL_REAL_DATA_WORKFLOW}")
    return errors


REQUIRED_VALIDATION_FILES = [
    VALIDATION_BUNDLE / "sources.yml",
    VALIDATION_BUNDLE / "data" / "desi_dr2_bao.yml",
    VALIDATION_BUNDLE / "data" / "hz_cosmic_chronometers.yml",
    VALIDATION_BUNDLE / "fetch_real_data.py",
    VALIDATION_BUNDLE / "compute_validation.py",
    VALIDATION_BUNDLE / "make_figures.py",
    VALIDATION_BUNDLE / "render_report.py",
    VALIDATION_PATHS / "CAMINHOS_VALIDACAO_NOVOS.yml",
]


def parse_yaml(path: Path) -> dict:
    loaded = yaml.load(path.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
    if not isinstance(loaded, dict):
        raise ValueError("top-level YAML document must be a mapping")
    return loaded


def iter_workflow_yaml() -> Iterable[Path]:
    yield from sorted(WORKFLOWS.glob("*.yml"))
    yield from sorted(WORKFLOWS.glob("*.yaml"))


def audit_workflow_contracts() -> list[str]:
    errors: list[str] = []
    for path in iter_workflow_yaml():
        try:
            doc = parse_yaml(path)
        except Exception as exc:
            errors.append(f"{path.relative_to(REPO)}: YAML parse/shape error: {exc}")
            continue

        for required in ("name", "on", "jobs"):
            if required not in doc:
                errors.append(f"{path.relative_to(REPO)}: missing required workflow key '{required}'")
        jobs = doc.get("jobs") or {}
        if not isinstance(jobs, dict) or not jobs:
            errors.append(f"{path.relative_to(REPO)}: jobs must be a non-empty mapping")
            continue
        for job_name, job in jobs.items():
            if not isinstance(job, dict):
                errors.append(f"{path.relative_to(REPO)}: job '{job_name}' must be a mapping")
                continue
            if "uses" not in job and "runs-on" not in job:
                errors.append(f"{path.relative_to(REPO)}: job '{job_name}' missing runs-on/uses")
            if "uses" not in job:
                steps = job.get("steps")
                if not isinstance(steps, list) or not steps:
                    errors.append(f"{path.relative_to(REPO)}: job '{job_name}' needs non-empty steps")
    return errors


def audit_workflow_directory_hygiene() -> list[str]:
    errors: list[str] = []
    for path in sorted(WORKFLOWS.iterdir()):
        if path.is_dir():
            errors.append(f"{path.relative_to(REPO)}: directories are not allowed inside workflow root")
            continue
        if path.suffix.lower() in NON_WORKFLOW_EXTENSIONS:
            errors.append(f"{path.relative_to(REPO)}: non-workflow artifact/script belongs outside .github/workflows")
    return errors


def audit_validation_bundle() -> list[str]:
    errors: list[str] = []
    for path in REQUIRED_VALIDATION_FILES:
        if not path.exists():
            errors.append(f"missing validation bundle file: {path.relative_to(REPO)}")
    for path in [p for p in REQUIRED_VALIDATION_FILES if p.suffix in {'.yml', '.yaml'} and p.exists()]:
        try:
            parse_yaml(path)
        except Exception as exc:
            errors.append(f"{path.relative_to(REPO)}: YAML parse/shape error: {exc}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit GitHub workflow hygiene and validation YAML placement.")
    parser.add_argument("--strict", action="store_true", help="Fail with exit 1 on any warning/error.")
    args = parser.parse_args()

    errors = []
    errors.extend(audit_workflow_contracts())
    errors.extend(audit_workflow_directory_hygiene())
    errors.extend(audit_validation_bundle())
    errors.extend(audit_real_workflow_policy())

    if errors:
        print("Workflow audit found issues:")
        for error in errors:
            print(f"- {error}")
        return 1 if args.strict else 0

    print("Workflow audit OK: executable workflows are isolated and validation data is externalized.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
