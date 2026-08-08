#!/usr/bin/env python3
from __future__ import annotations

"""Build TOKEN_VAZIO V4 without rewriting V1/V2/V3 custody.

V4 closes the uncertainty about live GitHub external settings as a negative fact
and adds the observed missing platform enforcement as an explicit P0 successor.
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

V4_INPUT_DELTA = Path("data/governance/RLL_GAP_CLOSURE_INPUT_DELTA_20260808_V4.json")
V4_OVERRIDE = Path("data/governance/RLL_TOKEN_VAZIO_CLOSURE_OVERRIDES_20260808_V4.json")


def build_current_view(
    repo_root: Path,
    *,
    input_path: Path = DEFAULT_INPUT,
    input_delta_paths: Iterable[Path] | None = None,
    rules_path: Path = DEFAULT_RULES,
    override_paths: Iterable[Path] | None = None,
    generated_at: str = "2026-08-08T06:50:00Z",
) -> dict[str, Any]:
    input_chain = list(input_delta_paths) if input_delta_paths is not None else [*DEFAULT_INPUT_DELTAS, V4_INPUT_DELTA]
    override_chain = list(override_paths) if override_paths is not None else [
        DEFAULT_OVERRIDES,
        *DEFAULT_OVERRIDE_DELTAS,
        V3_OVERRIDE,
        V4_OVERRIDE,
    ]
    receipt = build_v2_view(
        repo_root,
        input_path=input_path,
        input_delta_paths=input_chain,
        rules_path=rules_path,
        override_paths=override_chain,
        generated_at=generated_at,
    )
    receipt["view"] = "RLL_TOKEN_VAZIO_RECONCILIATION_V4_APPEND_ONLY"
    receipt["policy"]["v1_v2_v3_history_preserved"] = True
    receipt["policy"]["external_settings_negative_result_creates_enforcement_successor"] = True
    receipt["policy"]["platform_absence_is_not_governance_success"] = True
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
