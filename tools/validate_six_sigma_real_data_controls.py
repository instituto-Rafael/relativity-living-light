#!/usr/bin/env python3
"""Validate lightweight Six Sigma / DMAIC real-data control coverage.

The gate verifies the operational control spine and semantic controls. It does
not run scientific validation and never promotes an RLL claim.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

REQUIRED_FILES = [
    Path("docs/operations/SIX_SIGMA_REAL_DATA_OPERATING_SYSTEM.md"),
    Path("docs/real_data/REAL_DATA_REQUIRED_INPUTS.md"),
    Path(".github/workflows/real-data-complete-execution.yml"),
    Path("docs/RLL_TRACEABILITY_MAP.md"),
]

# A control may be expressed by an equivalent current term. This avoids a
# false CI failure when a workflow field is renamed but the control remains.
REQUIRED_CONTROL_GROUPS: dict[str, tuple[str, ...]] = {
    "DMAIC": ("DMAIC",),
    "claim boundary": ("claim boundary", "claim_boundary"),
    "checksum": ("checksum", "checksums"),
    "strict real-data mode": ("strict_real_data",),
    "reviewed artifact-only commit policy": (
        "artifact_only_reviewed_pr_required",
        "commit_light_artifacts",
        "commit artifacts through a reviewed pr",
        "reviewed pull request",
    ),
    "baseline": ("baseline",),
    "artifact": ("artifact",),
    "no-superiority boundary": (
        "No superiority claim unless real-data metrics pass predefined thresholds",
    ),
}


def missing_controls(corpus: str, groups: dict[str, Iterable[str]] = REQUIRED_CONTROL_GROUPS) -> list[str]:
    folded = corpus.casefold()
    return [
        name
        for name, alternatives in groups.items()
        if not any(term.casefold() in folded for term in alternatives)
    ]


def main() -> int:
    missing_files = [str(path) for path in REQUIRED_FILES if not path.is_file()]
    if missing_files:
        print("Six Sigma real-data control check FAILED: missing required files")
        for path in missing_files:
            print(f"- {path}")
        return 1

    corpus = "\n".join(path.read_text(encoding="utf-8", errors="replace") for path in REQUIRED_FILES)
    missing = missing_controls(corpus)
    if missing:
        print("Six Sigma real-data control check FAILED: missing semantic controls")
        for control in missing:
            print(f"- {control}")
        return 1

    print("OK: Six Sigma / DMAIC real-data control files and semantic controls are present.")
    print("claim_allowed=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
