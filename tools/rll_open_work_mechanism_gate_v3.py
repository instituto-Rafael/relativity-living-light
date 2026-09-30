#!/usr/bin/env python3
from __future__ import annotations

"""Validate the V4 effective mechanism queue without rewriting V1/V2 custody."""

import argparse
import json
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from tools.rll_open_work_mechanism_gate_v1 import DEFAULT_REGISTRY as BASE_REGISTRY, ROOT
from tools.rll_open_work_mechanism_gate_v2 import DELTA as PREDECESSOR_DELTA, validate as validate_v2
from tools.rll_token_vazio_reconcile_v4 import build_current_view

DELTA = Path("data/governance/RLL_OPEN_WORK_MECHANISM_REGISTRY_DELTA_20260808_V3.json")
OUTPUT = Path("artifacts/governance/RLL_OPEN_WORK_MECHANISM_GATE_V3.json")
SCHEMA = "rll.open_work_mechanism_registry_delta.v2"
FORBIDDEN_ATTENTION = {"IGNORED", "LEFT", "ABANDONED", "CENSORED", "ABORTED"}


@dataclass(frozen=True)
class Result:
    schema: str
    decision: str
    claim_allowed: bool
    publication_effect: str
    source_view: str
    predecessor_decision: str
    historical_registry_count: int
    current_open_count: int
    effective_registry_count: int
    priority_counts: dict[str, int]
    expected_priority_counts: dict[str, int]
    newly_resolved: list[str]
    newly_added_open: list[str]
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


def validate_added_mechanism(row: dict[str, Any], errors: list[str]) -> None:
    token = row.get("token")
    prefix = str(token or "added_open_mechanism")
    for field in ("token", "domain", "state", "urgency", "attention_state", "claim_boundary"):
        require_text(row, field, errors, prefix)
    if row.get("priority") not in {"P0", "P1", "P2"}:
        errors.append(f"{prefix}.priority: invalid")
    if not isinstance(row.get("state"), str) or not row["state"].startswith("OPEN_"):
        errors.append(f"{prefix}.state: must remain OPEN")
    if row.get("attention_state") in FORBIDDEN_ATTENTION:
        errors.append(f"{prefix}.attention_state: forbidden ignored/abandoned state")
    deps = row.get("dependencies")
    if not isinstance(deps, list) or any(not isinstance(dep, str) for dep in deps):
        errors.append(f"{prefix}.dependencies: list[str] required")
    elif token in deps:
        errors.append(f"{prefix}: self dependency forbidden")
    mechanism = row.get("mechanism")
    if not isinstance(mechanism, dict):
        errors.append(f"{prefix}.mechanism: object required")
    else:
        for field in ("id", "class", "driver", "trigger", "deliverable", "verification", "falsifier"):
            require_text(mechanism, field, errors, f"{prefix}.mechanism")
    close_when = row.get("close_when")
    if not isinstance(close_when, list) or not close_when or any(not isinstance(x, str) or not x.strip() for x in close_when):
        errors.append(f"{prefix}.close_when: non-empty list[str] required")


def validate(root: Path = ROOT, delta_path: Path = DELTA) -> Result:
    root = root.resolve()
    errors: list[str] = []
    predecessor = validate_v2(root, PREDECESSOR_DELTA)
    if predecessor.decision != "PASS":
        errors.append("predecessor mechanism gate V2 must PASS")

    delta_full = delta_path if delta_path.is_absolute() else root / delta_path
    delta = load(delta_full)
    if delta.get("schema") != SCHEMA:
        errors.append(f"delta schema must be {SCHEMA}")
    if delta.get("claim_allowed") is not False or delta.get("publication_ready") is not False:
        errors.append("delta must preserve claim_allowed=false and publication_ready=false")
    if delta.get("predecessor_delta") != str(PREDECESSOR_DELTA):
        errors.append("predecessor_delta mismatch")

    base = load(root / BASE_REGISTRY)
    base_rows = base.get("tokens") if isinstance(base.get("tokens"), list) else []
    base_by_token = {row.get("token"): row for row in base_rows if isinstance(row, dict)}
    prior_delta = load(root / PREDECESSOR_DELTA)
    prior_resolved = {
        row.get("token") for row in (prior_delta.get("resolved_by_evidence") or []) if isinstance(row, dict)
    }

    current = build_current_view(root, generated_at="2026-08-08T06:50:00Z")
    current_open = {
        row["token"] for row in current["results"]
        if isinstance(row.get("state"), str) and row["state"].startswith("OPEN_")
    }
    source_view = str(current.get("view"))
    if delta.get("source_view") != source_view:
        errors.append(f"source_view mismatch delta={delta.get('source_view')!r} current={source_view!r}")

    new_resolved: set[str] = set()
    closures = delta.get("resolved_by_evidence")
    if not isinstance(closures, list) or not closures:
        errors.append("resolved_by_evidence must be non-empty list")
        closures = []
    predecessor_open = {row["token"] for row in predecessor.urgent_queue}
    for index, row in enumerate(closures):
        prefix = f"resolved_by_evidence[{index}]"
        if not isinstance(row, dict):
            errors.append(f"{prefix}: object required")
            continue
        token = row.get("token")
        if not isinstance(token, str) or token not in predecessor_open:
            errors.append(f"{prefix}.token: must be open in predecessor")
            continue
        if token in new_resolved:
            errors.append(f"{token}: duplicate new closure")
        new_resolved.add(token)
        if token in current_open:
            errors.append(f"{token}: closure claimed but token remains OPEN in V4")
        for field in ("classification", "evidence_path", "closure_override_path"):
            require_text(row, field, errors, prefix)
        for field in ("evidence_path", "closure_override_path"):
            value = row.get(field)
            if isinstance(value, str) and not (root / value).is_file():
                errors.append(f"{token}: missing {field}: {value}")

    effective: dict[str, dict[str, Any]] = {
        token: row for token, row in base_by_token.items() if token not in prior_resolved | new_resolved
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
        validate_added_mechanism(row, errors)
        token = row.get("token")
        if not isinstance(token, str) or not token.startswith("TOKEN_VAZIO_"):
            errors.append(f"added_open_mechanisms[{index}].token: invalid")
            continue
        if token in base_by_token or token in added_tokens:
            errors.append(f"{token}: added token duplicates historical/current mechanism")
            continue
        if token not in current_open:
            errors.append(f"{token}: added mechanism must be OPEN in V4")
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
    rank = {"P0": 0, "P1": 1, "P2": 2}
    queue.sort(key=lambda item: (rank.get(item["priority"], 99), item["token"]))

    return Result(
        schema="rll.open_work_mechanism_gate.v3",
        decision="PASS" if not errors else "BLOCKED",
        claim_allowed=False,
        publication_effect="NONE",
        source_view=source_view,
        predecessor_decision=predecessor.decision,
        historical_registry_count=len(base_by_token),
        current_open_count=len(current_open),
        effective_registry_count=len(effective_tokens),
        priority_counts=actual_counts,
        expected_priority_counts=expected_counts,
        newly_resolved=sorted(new_resolved),
        newly_added_open=sorted(added_tokens),
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
        "current_open_count": result.current_open_count,
        "priority_counts": result.priority_counts,
        "newly_resolved": result.newly_resolved,
        "newly_added_open": result.newly_added_open,
        "error_count": len(result.errors),
    }, sort_keys=True))
    for error in result.errors:
        print("ERROR:", error)
    return 0 if result.decision == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
