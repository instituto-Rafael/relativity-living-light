#!/usr/bin/env python3
from __future__ import annotations

"""Fail-closed saturation gate for the current RLL open TOKEN_VAZIO set.

The gate does not resolve scientific gaps. It guarantees that every currently
open token has a concrete operational mechanism, urgency, attention state,
deliverable, verification rule, falsifier and objective close conditions.
"""

import argparse
import json
from collections import Counter
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

from tools.rll_token_vazio_reconcile_v2 import build_current_view

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY = Path("data/governance/RLL_OPEN_WORK_MECHANISM_REGISTRY_20260808_V1.json")
DEFAULT_OUTPUT = Path("artifacts/governance/RLL_OPEN_WORK_MECHANISM_GATE_V1.json")
SCHEMA = "rll.open_work_mechanism_registry.v1"
RECEIPT_SCHEMA = "rll.open_work_mechanism_gate.v1"

ALLOWED_PRIORITIES = {"P0", "P1", "P2"}
ALLOWED_ATTENTION = {
    "ACTIVE",
    "BLOCKED_EXTERNAL",
    "BLOCKED_DEPENDENCY",
    "NEEDS_HUMAN",
    "PHYSICAL_REQUIRED",
}
FORBIDDEN_ATTENTION = {
    "IGNORED",
    "LEFT",
    "ABANDONED",
    "CENSORED",
    "ABORTED",
    "UNKNOWN",
}
REPO_PATH_PREFIXES = (
    ".github/",
    "artifacts/",
    "data/",
    "docs/",
    "products/",
    "scripts/",
    "src/",
    "tests/",
    "tools/",
)


@dataclass(frozen=True)
class ValidationResult:
    schema: str
    decision: str
    claim_allowed: bool
    publication_effect: str
    source_view: str
    current_open_count: int
    registry_count: int
    priority_counts: dict[str, int]
    expected_priority_counts: dict[str, int]
    missing_tokens: list[str]
    extra_tokens: list[str]
    content_errors: list[str]
    ignored_tokens: list[str]
    urgent_queue: list[dict[str, str]]


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: top-level JSON must be an object")
    return value


def nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def current_open_tokens(repo_root: Path) -> tuple[set[str], str]:
    receipt = build_current_view(
        repo_root,
        generated_at="2026-08-08T05:37:00Z",
    )
    tokens = {
        row["token"]
        for row in receipt["results"]
        if isinstance(row.get("state"), str) and row["state"].startswith("OPEN_")
    }
    return tokens, str(receipt.get("view", "TOKEN_VAZIO_CURRENT_VIEW"))


def validate_registry(repo_root: Path, registry_path: Path) -> ValidationResult:
    full = registry_path if registry_path.is_absolute() else repo_root / registry_path
    payload = load_json(full)
    errors: list[str] = []
    ignored: list[str] = []

    if payload.get("schema") != SCHEMA:
        errors.append(f"schema must be {SCHEMA}")
    if payload.get("claim_allowed") is not False:
        errors.append("claim_allowed must remain false")
    if payload.get("publication_ready") is not False:
        errors.append("publication_ready must remain false")

    current_open, source_view = current_open_tokens(repo_root)
    items = payload.get("tokens")
    if not isinstance(items, list):
        items = []
        errors.append("tokens must be a list")

    seen: set[str] = set()
    registry_tokens: set[str] = set()
    priority_counter: Counter[str] = Counter()
    mechanism_ids: set[str] = set()
    queue: list[dict[str, str]] = []

    required_text = ("token", "priority", "domain", "state", "urgency", "attention_state", "claim_boundary")
    mechanism_text = ("id", "class", "driver", "trigger", "deliverable", "verification", "falsifier")

    for index, item in enumerate(items):
        prefix = f"tokens[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix}: must be object")
            continue

        for field in required_text:
            if not nonempty_text(item.get(field)):
                errors.append(f"{prefix}.{field}: non-empty text required")

        token = item.get("token")
        if not isinstance(token, str):
            continue
        if not token.startswith("TOKEN_VAZIO_"):
            errors.append(f"{token}: invalid token prefix")
        if token in seen:
            errors.append(f"{token}: duplicate token")
        seen.add(token)
        registry_tokens.add(token)

        priority = item.get("priority")
        if priority not in ALLOWED_PRIORITIES:
            errors.append(f"{token}: invalid priority {priority!r}")
        else:
            priority_counter[priority] += 1

        state = item.get("state")
        if not (isinstance(state, str) and state.startswith("OPEN_")):
            errors.append(f"{token}: registry is for open tokens only")

        attention = item.get("attention_state")
        if attention in FORBIDDEN_ATTENTION or attention not in ALLOWED_ATTENTION:
            ignored.append(token)
            errors.append(f"{token}: attention_state {attention!r} is forbidden/unknown")

        dependencies = item.get("dependencies")
        if not isinstance(dependencies, list):
            errors.append(f"{token}: dependencies must be a list")
        else:
            for dep in dependencies:
                if not isinstance(dep, str) or not dep.startswith("TOKEN_VAZIO_"):
                    errors.append(f"{token}: invalid dependency {dep!r}")
                elif dep == token:
                    errors.append(f"{token}: self-dependency is forbidden")

        mechanism = item.get("mechanism")
        if not isinstance(mechanism, dict):
            errors.append(f"{token}: mechanism object required")
        else:
            for field in mechanism_text:
                if not nonempty_text(mechanism.get(field)):
                    errors.append(f"{token}.mechanism.{field}: non-empty text required")
            mid = mechanism.get("id")
            if isinstance(mid, str):
                if mid in mechanism_ids:
                    errors.append(f"{token}: duplicate mechanism id {mid}")
                mechanism_ids.add(mid)
            driver = mechanism.get("driver")
            if isinstance(driver, str) and driver.startswith(REPO_PATH_PREFIXES):
                if not (repo_root / driver).is_file():
                    errors.append(f"{token}: mechanism driver path does not exist: {driver}")

        close_when = item.get("close_when")
        if not isinstance(close_when, list) or not close_when:
            errors.append(f"{token}: close_when must be a non-empty list")
        elif any(not nonempty_text(entry) for entry in close_when):
            errors.append(f"{token}: every close_when entry must be non-empty text")

        queue.append(
            {
                "priority": str(priority),
                "token": token,
                "urgency": str(item.get("urgency", "")),
                "attention_state": str(attention),
                "mechanism_id": str((mechanism or {}).get("id", "")),
            }
        )

    missing = sorted(current_open - registry_tokens)
    extra = sorted(registry_tokens - current_open)
    if missing:
        errors.append("missing current open tokens: " + ", ".join(missing))
    if extra:
        errors.append("registry contains non-current tokens: " + ", ".join(extra))

    expected_denominator = payload.get("expected_open_denominator")
    if expected_denominator != len(current_open):
        errors.append(
            f"expected_open_denominator={expected_denominator!r} current_open={len(current_open)}"
        )

    expected_counts = payload.get("expected_priority_counts")
    if not isinstance(expected_counts, dict):
        expected_counts = {}
        errors.append("expected_priority_counts must be object")
    actual_counts = {p: priority_counter.get(p, 0) for p in ("P0", "P1", "P2")}
    normalized_expected = {p: int(expected_counts.get(p, -1)) for p in ("P0", "P1", "P2")}
    if actual_counts != normalized_expected:
        errors.append(
            f"priority distribution mismatch actual={actual_counts} expected={normalized_expected}"
        )

    priority_rank = {"P0": 0, "P1": 1, "P2": 2}
    queue.sort(key=lambda row: (priority_rank.get(row["priority"], 99), row["token"]))

    return ValidationResult(
        schema=RECEIPT_SCHEMA,
        decision="PASS" if not errors else "BLOCKED",
        claim_allowed=False,
        publication_effect="NONE",
        source_view=source_view,
        current_open_count=len(current_open),
        registry_count=len(registry_tokens),
        priority_counts=actual_counts,
        expected_priority_counts=normalized_expected,
        missing_tokens=missing,
        extra_tokens=extra,
        content_errors=errors,
        ignored_tokens=sorted(set(ignored)),
        urgent_queue=queue,
    )


def write_receipt(result: ValidationResult, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(asdict(result), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    root = args.repo_root.resolve()
    result = validate_registry(root, args.registry)
    output = args.output if args.output.is_absolute() else root / args.output
    write_receipt(result, output)

    print(
        json.dumps(
            {
                "decision": result.decision,
                "current_open_count": result.current_open_count,
                "registry_count": result.registry_count,
                "priority_counts": result.priority_counts,
                "missing_tokens": result.missing_tokens,
                "extra_tokens": result.extra_tokens,
                "ignored_tokens": result.ignored_tokens,
                "content_error_count": len(result.content_errors),
            },
            sort_keys=True,
        )
    )
    if result.content_errors:
        for error in result.content_errors:
            print(f"ERROR: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
