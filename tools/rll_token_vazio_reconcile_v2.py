#!/usr/bin/env python3
from __future__ import annotations

"""Build the 2026-08-08 TOKEN_VAZIO view without rewriting V1 custody.

V2 composes two append-only chains:
  * base 30-token input + successor-token input deltas;
  * base rules + V1 overrides + later override deltas.

The V1 reconciler remains untouched and can reproduce its historical 30-token
view. V2 only produces a derived current view; claim_allowed stays false.
"""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from tools.rll_token_vazio_reconcile import (
    apply_rule_overrides,
    load_json,
    reconcile,
    sha256_file,
    validate_input,
)

INPUT_DELTA_SCHEMA = "rll.gap_closure_input_delta.v1"
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = Path("data/governance/RLL_GAP_CLOSURE_INPUT_20260807_V1.json")
DEFAULT_INPUT_DELTAS = [Path("data/governance/RLL_GAP_CLOSURE_INPUT_DELTA_20260808_V2.json")]
DEFAULT_RULES = Path("data/governance/RLL_TOKEN_VAZIO_CLOSURE_RULES_20260807_V1.json")
DEFAULT_OVERRIDES = Path("data/governance/RLL_TOKEN_VAZIO_CLOSURE_OVERRIDES_20260807_V1.json")
DEFAULT_OVERRIDE_DELTAS = [Path("data/governance/RLL_TOKEN_VAZIO_CLOSURE_OVERRIDES_20260808_V2.json")]


def clone(payload: Any) -> Any:
    return json.loads(json.dumps(payload))


def merge_input_delta(base_payload: dict[str, Any], delta_payload: dict[str, Any]) -> dict[str, Any]:
    """Append new token objects while preserving the base input verbatim."""
    validate_input(base_payload)
    if delta_payload.get("schema") != INPUT_DELTA_SCHEMA:
        raise ValueError(f"input delta schema must be {INPUT_DELTA_SCHEMA}")
    if delta_payload.get("claim_allowed") is not False:
        raise ValueError("input delta must preserve claim_allowed=false")
    additions = delta_payload.get("tokens")
    if not isinstance(additions, list) or not additions:
        raise ValueError("input delta requires non-empty tokens")

    merged = clone(base_payload)
    existing = {item["token"] for item in merged["tokens"]}
    seen: set[str] = set()
    for item in additions:
        if not isinstance(item, dict):
            raise ValueError("input delta token must be object")
        token = item.get("token")
        if not isinstance(token, str) or not token.startswith("TOKEN_VAZIO_"):
            raise ValueError(f"invalid input delta token: {token!r}")
        if token in existing or token in seen:
            raise ValueError(f"duplicate input delta token: {token}")
        if item.get("priority") not in {"P0", "P1", "P2"}:
            raise ValueError(f"{token}: invalid priority")
        seen.add(token)
        merged["tokens"].append(clone(item))
    validate_input(merged)
    return merged


def merge_input_chain(base_payload: dict[str, Any], deltas: Iterable[dict[str, Any]]) -> dict[str, Any]:
    merged = clone(base_payload)
    for delta in deltas:
        merged = merge_input_delta(merged, delta)
    return merged


def apply_override_chain(base_rules: dict[str, Any], override_payloads: Iterable[dict[str, Any]]) -> dict[str, Any]:
    effective = clone(base_rules)
    for override in override_payloads:
        effective = apply_rule_overrides(effective, override)
    return effective


def resolve(root: Path, path: Path) -> Path:
    return path if path.is_absolute() else root / path


def load_existing_chain(root: Path, paths: Iterable[Path]) -> tuple[list[dict[str, Any]], list[Path]]:
    payloads: list[dict[str, Any]] = []
    actual_paths: list[Path] = []
    for path in paths:
        full = resolve(root, path)
        if not full.is_file():
            raise FileNotFoundError(full)
        payloads.append(load_json(full))
        actual_paths.append(full)
    return payloads, actual_paths


def build_current_view(
    repo_root: Path,
    *,
    input_path: Path = DEFAULT_INPUT,
    input_delta_paths: Iterable[Path] = DEFAULT_INPUT_DELTAS,
    rules_path: Path = DEFAULT_RULES,
    override_paths: Iterable[Path] = (DEFAULT_OVERRIDES, *DEFAULT_OVERRIDE_DELTAS),
    generated_at: str = "2026-08-08T04:30:00Z",
) -> dict[str, Any]:
    root = repo_root.resolve()
    full_input = resolve(root, input_path)
    full_rules = resolve(root, rules_path)
    input_deltas, input_delta_actual = load_existing_chain(root, input_delta_paths)
    overrides, override_actual = load_existing_chain(root, override_paths)

    merged_input = merge_input_chain(load_json(full_input), input_deltas)
    effective_rules = apply_override_chain(load_json(full_rules), overrides)
    receipt = reconcile(root, merged_input, effective_rules, generated_at)
    receipt["view"] = "RLL_TOKEN_VAZIO_RECONCILIATION_V2_APPEND_ONLY"
    receipt["base_input"] = {"path": str(full_input.relative_to(root)), "sha256": sha256_file(full_input)}
    receipt["input_deltas"] = [
        {"path": str(path.relative_to(root)), "sha256": sha256_file(path)} for path in input_delta_actual
    ]
    receipt["base_rules"] = {"path": str(full_rules.relative_to(root)), "sha256": sha256_file(full_rules)}
    receipt["override_chain"] = [
        {"ordinal": index, "path": str(path.relative_to(root)), "sha256": sha256_file(path)}
        for index, path in enumerate(override_actual, start=1)
    ]
    receipt["policy"]["input_deltas_preserve_prior_denominator_history"] = True
    receipt["policy"]["override_order_is_explicit"] = True
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
    override_chain = args.overrides if args.overrides is not None else [DEFAULT_OVERRIDES, *DEFAULT_OVERRIDE_DELTAS]
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
    output = resolve(root, args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt["summary"], sort_keys=True))
    invalid = any(row["state"] == "OPEN_EVIDENCE_MISSING" for row in receipt["results"])
    return 2 if invalid else 0


if __name__ == "__main__":
    raise SystemExit(main())
