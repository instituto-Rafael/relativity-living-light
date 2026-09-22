#!/usr/bin/env python3
"""Fail-closed execution-quality monitor for CI cost/latency telemetry.

Phase 1 is advisory only:
- counts changed paths and classifies risk;
- records JUnit test counts/time when available;
- exposes a TTL policy state but never authorizes skipping the canonical full suite;
- never reads changed file contents or secret/environment values.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Iterable

DEFAULT_TTL_SECONDS = 21600  # 6h candidate policy; not enforced in V1.

CRITICAL_PREFIXES = (
    ".github/workflows/",
    "scripts/validation/",
    "data/governance/",
    "data/schemas/",
)
CRITICAL_EXACT = {
    "tools/rll_real_data_evidence_bridge.py",
    "tools/rll_cosmology_e0_preflight.py",
    "tools/ci/real_data_workflow_policy.sh",
}
FOCUSED_BOUNDARY_TESTS = {
    "tests/test_real_seed_utils.py",
    "tests/test_orbital_outputs.py",
}
SENSITIVE_PREFIXES = (
    ".github/",
    "data/",
    "scripts/",
    "src/",
    "tools/",
    "tests/",
)
ALLOWED_WORKFLOWS = {"python-tests", "claim-boundary"}


def _git(*args: str) -> str:
    p = subprocess.run(
        ["git", *args],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return p.stdout.strip()


def changed_files(base_sha: str | None, head_sha: str | None) -> list[str]:
    base = (base_sha or "").strip()
    head = (head_sha or "").strip()
    candidates: list[tuple[str, str]] = []
    if base and head and set(base) != {"0"}:
        candidates.append((base, head))
    candidates.extend([("HEAD^", "HEAD"), ("HEAD~1", "HEAD")])
    for left, right in candidates:
        try:
            out = _git("diff", "--name-only", left, right)
            return sorted({x.strip() for x in out.splitlines() if x.strip()})
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    return []


def classify(paths: Iterable[str]) -> dict[str, object]:
    paths = sorted(set(paths))
    critical = [
        p for p in paths
        if p in CRITICAL_EXACT or p.startswith(CRITICAL_PREFIXES)
    ]
    focused = [p for p in paths if p in FOCUSED_BOUNDARY_TESTS]
    sensitive = [p for p in paths if p.startswith(SENSITIVE_PREFIXES)]
    docs_only = bool(paths) and all(
        p.startswith(("docs/", "README", "LICENSE", "CITATION"))
        for p in paths
    )

    if critical:
        risk = "HIGH"
    elif sensitive:
        risk = "MEDIUM"
    elif docs_only:
        risk = "LOW"
    else:
        risk = "LOW" if paths else "TOKEN_VAZIO_CHANGESET"

    return {
        "changed_file_count": len(paths),
        "critical_file_count": len(critical),
        "focused_boundary_test_file_count": len(focused),
        "sensitive_file_count": len(sensitive),
        "docs_only": docs_only,
        "risk_class": risk,
        "changed_files": paths,
        "critical_files": critical,
        "focused_boundary_test_files": focused,
    }


def parse_junit(path: Path | None) -> dict[str, object]:
    if path is None or not path.exists():
        return {
            "state": "TOKEN_VAZIO_JUNIT",
            "tests": None,
            "failures": None,
            "errors": None,
            "skipped": None,
            "time_seconds": None,
        }
    root = ET.parse(path).getroot()
    suites = [root] if root.tag == "testsuite" else list(root.findall("testsuite"))
    attrs = {"tests": 0, "failures": 0, "errors": 0, "skipped": 0}
    total_time = 0.0
    for suite in suites:
        for key in attrs:
            attrs[key] += int(float(suite.attrib.get(key, "0") or 0))
        total_time += float(suite.attrib.get("time", "0") or 0.0)
    return {
        "state": "OBSERVED",
        **attrs,
        "time_seconds": total_time,
    }


def ttl_state(last_full_pass_epoch: int | None, now_epoch: int | None, ttl_seconds: int) -> dict[str, object]:
    if last_full_pass_epoch is None or now_epoch is None:
        return {
            "state": "TOKEN_VAZIO_LAST_FULL_PASS",
            "ttl_seconds": ttl_seconds,
            "age_seconds": None,
            "fresh": None,
            "enforced": False,
        }
    age = max(0, now_epoch - last_full_pass_epoch)
    return {
        "state": "OBSERVED",
        "ttl_seconds": ttl_seconds,
        "age_seconds": age,
        "fresh": age <= ttl_seconds,
        "enforced": False,
    }


def build_report(
    *,
    workflow: str,
    paths: list[str],
    junit: Path | None,
    last_full_pass_epoch: int | None,
    now_epoch: int | None,
    ttl_seconds: int,
) -> dict[str, object]:
    if workflow not in ALLOWED_WORKFLOWS:
        raise ValueError(f"unsupported workflow: {workflow}")
    counts = classify(paths)
    junit_report = parse_junit(junit)
    ttl = ttl_state(last_full_pass_epoch, now_epoch, ttl_seconds)

    if workflow == "python-tests":
        decision = "FULL_CANONICAL_REQUIRED"
        authority = "canonical_full_suite"
    else:
        decision = "FOCUSED_BOUNDARY_REQUIRED"
        authority = "focused_claim_boundary_gate"

    return {
        "schema": "rll.quality_execution_monitor.v1",
        "mode": "SHADOW_ADVISORY",
        "workflow": workflow,
        "authority": authority,
        "decision": decision,
        "skip_full_suite_allowed": False,
        "claim_allowed": False,
        "path_metrics": counts,
        "test_metrics": junit_report,
        "ttl": ttl,
        "privacy_security": {
            "changed_file_contents_read": False,
            "secret_values_read": False,
            "environment_dumped": False,
            "paths_only": True,
        },
        "non_regression": [
            "python-tests remains the canonical full-suite authority",
            "claim-boundary keeps its direct validation scripts and focused regressions",
            "TTL cannot skip the canonical full suite in V1",
            "TOKEN_VAZIO is never interpreted as freshness or PASS",
        ],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workflow", required=True, choices=sorted(ALLOWED_WORKFLOWS))
    ap.add_argument("--base-sha")
    ap.add_argument("--head-sha")
    ap.add_argument("--junitxml", type=Path)
    ap.add_argument("--last-full-pass-epoch", type=int)
    ap.add_argument("--now-epoch", type=int)
    ap.add_argument("--ttl-seconds", type=int, default=DEFAULT_TTL_SECONDS)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    paths = changed_files(args.base_sha, args.head_sha)
    report = build_report(
        workflow=args.workflow,
        paths=paths,
        junit=args.junitxml,
        last_full_pass_epoch=args.last_full_pass_epoch,
        now_epoch=args.now_epoch,
        ttl_seconds=args.ttl_seconds,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
