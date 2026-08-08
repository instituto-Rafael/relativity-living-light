#!/usr/bin/env python3
from __future__ import annotations

"""Validate the V5 effective mechanism queue after surfacing modern SN P0."""

import argparse
import json
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from tools.rll_open_work_mechanism_gate_v1 import ROOT
from tools.rll_open_work_mechanism_gate_v3 import DELTA as PREDECESSOR_DELTA, validate as validate_v3
from tools.rll_token_vazio_reconcile_v5 import build_current_view

DELTA = Path("data/governance/RLL_OPEN_WORK_MECHANISM_REGISTRY_DELTA_20260808_V4.json")
OUTPUT = Path("artifacts/governance/RLL_OPEN_WORK_MECHANISM_GATE_V4.json")
SCHEMA = "rll.open_work_mechanism_registry_delta.v3"
FORBIDDEN_ATTENTION = {"IGNORED", "LEFT", "ABANDONED", "CENSORED", "ABORTED"}


@dataclass(frozen=True)
class Result:
    schema: str
    decision: str
    claim_allowed: bool
    publication_effect: str
    source_view: str
    predecessor_decision: str
    predecessor_open_count: int
    current_open_count: int
    effective_registry_count: int
    priority_counts: dict[str, int]
    expected_priority_counts: dict[str, int]
    added_open: list[str]
    missing_tokens: list[str]
    extra_tokens: list[str]
    errors: list[str]
    urgent_queue: list[dict[str, str]]


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: object required")
    return value


def require_text(row: dict[str, Any], field: str, errors: list[str], prefix: str) -> None:
    value = row.get(field)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{prefix}.{field}: non-empty string required")


def validate_added(row: dict[str, Any], errors: list[str]) -> None:
    token = str(row.get("token") or "added")
    for field in ("token", "domain", "state", "urgency", "attention_state", "claim_boundary"):
        require_text(row, field, errors, token)
    if row.get("priority") not in {"P0", "P1", "P2"}:
        errors.append(f"{token}.priority: invalid")
    if not isinstance(row.get("state"), str) or not row["state"].startswith("OPEN_"):
        errors.append(f"{token}.state: must remain OPEN")
    if row.get("attention_state") in FORBIDDEN_ATTENTION:
        errors.append(f"{token}.attention_state: forbidden ignored/abandoned state")
    deps = row.get("dependencies")
    if not isinstance(deps, list) or any(not isinstance(dep, str) for dep in deps):
        errors.append(f"{token}.dependencies: list[str] required")
    elif token in deps:
        errors.append(f"{token}: self dependency forbidden")
    mechanism = row.get("mechanism")
    if not isinstance(mechanism, dict):
        errors.append(f"{token}.mechanism: object required")
    else:
        for field in ("id", "class", "driver", "trigger", "deliverable", "verification", "falsifier"):
            require_text(mechanism, field, errors, f"{token}.mechanism")
    close_when = row.get("close_when")
    if not isinstance(close_when, list) or not close_when or any(not isinstance(x, str) or not x.strip() for x in close_when):
        errors.append(f"{token}.close_when: non-empty list[str] required")


def validate(root: Path = ROOT, delta_path: Path = DELTA) -> Result:
    root = root.resolve()
    errors: list[str] = []
    predecessor = validate_v3(root, PREDECESSOR_DELTA)
    if predecessor.decision != "PASS":
        errors.append("predecessor mechanism gate V3 must PASS")

    delta_full = delta_path if delta_path.is_absolute() else root / delta_path
    delta = load(delta_full)
    if delta.get("schema") != SCHEMA:
        errors.append(f"delta schema must be {SCHEMA}")
    if delta.get("claim_allowed") is not False or delta.get("publication_ready") is not False:
        errors.append("delta must preserve claim_allowed=false and publication_ready=false")
    if delta.get("predecessor_delta") != str(PREDECESSOR_DELTA):
        errors.append("predecessor_delta mismatch")

    current = build_current_view(root, generated_at="2026-08-08T07:10:00Z")
    current_open = {
        row["token"] for row in current["results"]
        if isinstance(row.get("state"), str) and row["state"].startswith("OPEN_")
    }
    source_view = str(current.get("view"))
    if delta.get("source_view") != source_view:
        errors.append(f"source_view mismatch delta={delta.get('source_view')!r} current={source_view!r}")

    effective: dict[str, dict[str, Any]] = {
        row["token"]: {
            "token": row["token"],
            "priority": row["priority"],
            "urgency": row["urgency"],
            "attention_state": row["attention_state"],
            "mechanism": {"id": row["mechanism_id"]},
        }
        for row in predecessor.urgent_queue
    }
    added_tokens: set[str] = set()
    added = delta.get("added_open_mechanisms")
    if not isinstance(added, list) or not added:
        errors.append("added_open_mechanisms must be non-empty list")
        added = []
    for index, row in enumerate(added):
        if not isinstance(row, dict):
            errors.append(f"added_open_mechanisms[{index}]: object required")
            continue
        validate_added(row, errors)
        token = row.get("token")
        if not isinstance(token, str) or not token.startswith("TOKEN_VAZIO_"):
            errors.append(f"added_open_mechanisms[{index}].token: invalid")
            continue
        if token in effective or token in added_tokens:
            errors.append(f"{token}: duplicate mechanism token")
            continue
        if token not in current_open:
            errors.append(f"{token}: added mechanism must be OPEN in V5")
        added_tokens.add(token)
        effective[token] = row

    effective_tokens = set(effective)
    missing = sorted(current_open - effective_tokens)
    extra = sorted(effective_tokens - current_open)
    if missing:
        errors.append("missing current tokens: " + ", ".join(missing))
    if extra:
        errors.append("extra non-open mechanisms: " + ", ".join(extra))

    if delta.get("expected_open_denominator") != len(current_open):
        errors.append(f"expected_open_denominator mismatch current={len(current_open)}")
    counts = Counter(str(row.get("priority")) for row in effective.values())
    actual_counts = {p: counts.get(p, 0) for p in ("P0", "P1", "P2")}
    expected_raw = delta.get("expected_priority_counts") or {}
    expected_counts = {p: int(expected_raw.get(p, -1)) for p in ("P0", "P1", "P2")}
    if actual_counts != expected_counts:
        errors.append(f"priority mismatch actual={actual_counts} expected={expected_counts}")

    rank = {"P0": 0, "P1": 1, "P2": 2}
    queue = [
        {
            "priority": str(row.get("priority")),
            "token": token,
            "urgency": str(row.get("urgency")),
            "attention_state": str(row.get("attention_state")),
            "mechanism_id": str((row.get("mechanism") or {}).get("id")),
        }
        for token, row in effective.items()
    ]
    queue.sort(key=lambda item: (rank.get(item["priority"], 99), item["token"]))

    return Result(
        schema="rll.open_work_mechanism_gate.v4",
        decision="PASS" if not errors else "BLOCKED",
        claim_allowed=False,
        publication_effect="NONE",
        source_view=source_view,
        predecessor_decision=predecessor.decision,
        predecessor_open_count=predecessor.current_open_count,
        current_open_count=len(current_open),
        effective_registry_count=len(effective_tokens),
        priority_counts=actual_counts,
        expected_priority_counts=expected_counts,
        added_open=sorted(added_tokens),
        missing_tokens=missing,
        extra_tokens=extra,
        errors=errors,
        urgent_queue=queue,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--delta", type=Path, default=DELTA)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    result = validate(args.repo_root, args.delta)
    root = args.repo_root.resolve()
    output = args.output if args.output.is_absolute() else root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(asdict(result), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "decision": result.decision,
        "predecessor_open_count": result.predecessor_open_count,
        "current_open_count": result.current_open_count,
        "priority_counts": result.priority_counts,
        "added_open": result.added_open,
        "error_count": len(result.errors),
    }, sort_keys=True))
    for error in result.errors:
        print("ERROR:", error)
    return 0 if result.decision == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
