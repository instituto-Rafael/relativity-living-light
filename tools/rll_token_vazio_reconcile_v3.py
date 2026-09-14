#!/usr/bin/env python3
from __future__ import annotations

"""Build the current TOKEN_VAZIO V3 view without rewriting V1/V2 custody.

V3 adds only the 2026-08-08 late evidence delta that closes the frozen-ref
semantic review and H0 primary numeric provenance. The input denominator stays
33; only evidence-backed states change. claim_allowed remains false.
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

V3_OVERRIDE = Path("data/governance/RLL_TOKEN_VAZIO_CLOSURE_OVERRIDES_20260808_V3.json")


def build_current_view(
    repo_root: Path,
    *,
    input_path: Path = DEFAULT_INPUT,
    input_delta_paths: Iterable[Path] = DEFAULT_INPUT_DELTAS,
    rules_path: Path = DEFAULT_RULES,
    override_paths: Iterable[Path] | None = None,
    generated_at: str = "2026-08-08T05:44:00Z",
) -> dict[str, Any]:
    chain = list(override_paths) if override_paths is not None else [
        DEFAULT_OVERRIDES,
        *DEFAULT_OVERRIDE_DELTAS,
        V3_OVERRIDE,
    ]
    receipt = build_v2_view(
        repo_root,
        input_path=input_path,
        input_delta_paths=input_delta_paths,
        rules_path=rules_path,
        override_paths=chain,
        generated_at=generated_at,
    )
    receipt["view"] = "RLL_TOKEN_VAZIO_RECONCILIATION_V3_APPEND_ONLY"
    receipt["policy"]["v1_v2_history_preserved"] = True
    receipt["policy"]["v3_closures_require_asserted_evidence"] = True
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--input-delta", type=Path, action="append", default=None)
    parser.add_argument("--rules", type=Path, default=DEFAULT_RULES)
    parser.add_argument("--overrides", type=Path, action="append", default=None)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--generated-at", default=None)
    args = parser.parse_args()

    input_deltas = args.input_delta if args.input_delta is not None else list(DEFAULT_INPUT_DELTAS)
    override_chain = args.overrides if args.overrides is not None else [
        DEFAULT_OVERRIDES,
        *DEFAULT_OVERRIDE_DELTAS,
        V3_OVERRIDE,
    ]
    generated_at = args.generated_at or datetime.now(timezone.utc).isoformat()
    receipt = build_current_view(
        args.repo_root,
        input_path=args.input,
        input_delta_paths=input_deltas,
        rules_path=args.rules,
        override_paths=override_chain,
        generated_at=generated_at,
    )

    root = args.repo_root.resolve()
    output = args.output if args.output.is_absolute() else root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(receipt["summary"], sort_keys=True))
    invalid = any(row["state"] == "OPEN_EVIDENCE_MISSING" for row in receipt["results"])
    return 2 if invalid else 0


if __name__ == "__main__":
    raise SystemExit(main())
