#!/usr/bin/env python3
from __future__ import annotations

"""Build TOKEN_VAZIO V5 by surfacing the orphan Modern Validation SN P0.

V1-V4 remain immutable history. V5 adds one still-open validation obligation;
there is no evidence-based closure in this transition.
"""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from tools.rll_token_vazio_reconcile_v2 import (
    DEFAULT_INPUT,
    DEFAULT_INPUT_DELTAS,
    DEFAULT_OVERRIDE_DELTAS,
    DEFAULT_OVERRIDES,
    DEFAULT_RULES,
    ROOT,
    build_current_view as build_v2_view,
)
from tools.rll_token_vazio_reconcile_v3 import V3_OVERRIDE
from tools.rll_token_vazio_reconcile_v4 import V4_INPUT_DELTA, V4_OVERRIDE

V5_INPUT_DELTA = Path("data/governance/RLL_GAP_CLOSURE_INPUT_DELTA_20260808_V5.json")
V5_OVERRIDE = Path("data/governance/RLL_TOKEN_VAZIO_CLOSURE_OVERRIDES_20260808_V5.json")


def build_current_view(
    repo_root: Path,
    *,
    input_path: Path = DEFAULT_INPUT,
    input_delta_paths: Iterable[Path] | None = None,
    rules_path: Path = DEFAULT_RULES,
    override_paths: Iterable[Path] | None = None,
    generated_at: str = "2026-08-08T07:10:00Z",
) -> dict[str, Any]:
    inputs = list(input_delta_paths) if input_delta_paths is not None else [
        *DEFAULT_INPUT_DELTAS,
        V4_INPUT_DELTA,
        V5_INPUT_DELTA,
    ]
    overrides = list(override_paths) if override_paths is not None else [
        DEFAULT_OVERRIDES,
        *DEFAULT_OVERRIDE_DELTAS,
        V3_OVERRIDE,
        V4_OVERRIDE,
        V5_OVERRIDE,
    ]
    receipt = build_v2_view(
        repo_root,
        input_path=input_path,
        input_delta_paths=inputs,
        rules_path=rules_path,
        override_paths=overrides,
        generated_at=generated_at,
    )
    receipt["view"] = "RLL_TOKEN_VAZIO_RECONCILIATION_V5_APPEND_ONLY"
    receipt["policy"]["v1_v2_v3_v4_history_preserved"] = True
    receipt["policy"]["legacy_modern_validation_gap_cannot_disappear_by_rename"] = True
    receipt["policy"]["newly_surfaced_gap_is_not_a_regression"] = True
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--generated-at", default=None)
    args = parser.parse_args()
    receipt = build_current_view(
        args.repo_root,
        generated_at=args.generated_at or datetime.now(timezone.utc).isoformat(),
    )
    root = args.repo_root.resolve()
    output = args.output if args.output.is_absolute() else root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt["summary"], sort_keys=True))
    invalid = any(row["state"] == "OPEN_EVIDENCE_MISSING" for row in receipt["results"])
    return 2 if invalid else 0


if __name__ == "__main__":
    raise SystemExit(main())
