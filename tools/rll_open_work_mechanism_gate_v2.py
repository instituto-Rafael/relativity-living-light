#!/usr/bin/env python3
from __future__ import annotations

"""Validate the append-only effective RLL open-work mechanism queue V2.

V1 keeps the historical 14-open snapshot. V2 composes that registry with the
late-evidence delta and the TOKEN_VAZIO V3 view, so only evidence-backed
closures leave the current queue. All remaining open mechanisms stay saturated.
"""

import argparse
import json
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from tools.rll_open_work_mechanism_gate_v1 import DEFAULT_REGISTRY as BASE_REGISTRY, ROOT, validate_registry
from tools.rll_token_vazio_reconcile_v3 import build_current_view

DELTA = Path("data/governance/RLL_OPEN_WORK_MECHANISM_REGISTRY_DELTA_20260808_V2.json")
OUTPUT = Path("artifacts/governance/RLL_OPEN_WORK_MECHANISM_GATE_V2.json")
SCHEMA = "rll.open_work_mechanism_registry_delta.v1"


@dataclass(frozen=True)
class Result:
    schema: str
    decision: str
    claim_allowed: bool
    publication_effect: str
    source_view: str
    historical_registry_count: int
    current_open_count: int
    effective_registry_count: int
    priority_counts: dict[str, int]
    expected_priority_counts: dict[str, int]
    resolved_by_evidence: list[str]
    missing_tokens: list[str]
    extra_tokens: list[str]
    errors: list[str]
    urgent_queue: list[dict[str, str]]


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: top-level object required")
    return value


def repo_path(root: Path, value: str) -> Path:
    return root / value


def validate(root: Path = ROOT, delta_path: Path = DELTA) -> Result:
    errors: list[str] = []
    root = root.resolve()
    delta_full = delta_path if delta_path.is_absolute() else root / delta_path
    delta = load(delta_full)

    historical = validate_registry(root, BASE_REGISTRY)
    if historical.decision != "PASS":
        errors.append("historical V1 mechanism registry no longer reproduces its 14-open V2 snapshot")
        errors.extend(f"historical:{err}" for err in historical.content_errors)

    if delta.get("schema") != SCHEMA:
        errors.append(f"delta schema must be {SCHEMA}")
    if delta.get("claim_allowed") is not False:
        errors.append("delta claim_allowed must remain false")
    if delta.get("publication_ready") is not False:
        errors.append("delta publication_ready must remain false")
    if delta.get("base_registry") != str(BASE_REGISTRY):
        errors.append("delta base_registry must point to canonical V1 mechanism registry")

    base = load(root / BASE_REGISTRY)
    base_items = base.get("tokens") if isinstance(base.get("tokens"), list) else []
    base_by_token = {row.get("token"): row for row in base_items if isinstance(row, dict)}

    current = build_current_view(root, generated_at="2026-08-08T05:51:00Z")
    current_open = {
        row["token"]
        for row in current["results"]
        if isinstance(row.get("state"), str) and row["state"].startswith("OPEN_")
    }
    source_view = str(current.get("view"))
    if delta.get("source_view") != source_view:
        errors.append(f"source_view mismatch delta={delta.get('source_view')!r} current={source_view!r}")

    closures = delta.get("resolved_by_evidence")
    if not isinstance(closures, list) or not closures:
        closures = []
        errors.append("resolved_by_evidence must be non-empty list")
    resolved: set[str] = set()
    for index, row in enumerate(closures):
        prefix = f"resolved_by_evidence[{index}]"
        if not isinstance(row, dict):
            errors.append(f"{prefix}: object required")
            continue
        token = row.get("token")
        if not isinstance(token, str) or token not in base_by_token:
            errors.append(f"{prefix}: token must exist in base registry")
            continue
        if token in resolved:
            errors.append(f"{token}: duplicate resolved_by_evidence entry")
        resolved.add(token)
        if token in current_open:
            errors.append(f"{token}: listed resolved but still OPEN in V3")
        for field in ("classification", "evidence_path", "closure_override_path"):
            value = row.get(field)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{prefix}.{field}: non-empty string required")
        for field in ("evidence_path", "closure_override_path"):
            value = row.get(field)
            if isinstance(value, str) and not repo_path(root, value).is_file():
                errors.append(f"{token}: {field} does not exist: {value}")

    effective = {token: row for token, row in base_by_token.items() if token not in resolved}
    effective_tokens = set(effective)
    missing = sorted(current_open - effective_tokens)
    extra = sorted(effective_tokens - current_open)
    if missing:
        errors.append("missing current tokens: " + ", ".join(missing))
    if extra:
        errors.append("historical tokens not closed by delta: " + ", ".join(extra))

    expected_open = delta.get("expected_open_denominator")
    if expected_open != len(current_open):
        errors.append(f"expected_open_denominator={expected_open!r} current={len(current_open)}")

    counts = Counter(str(row.get("priority")) for row in effective.values())
    actual_counts = {p: counts.get(p, 0) for p in ("P0", "P1", "P2")}
    expected_raw = delta.get("expected_priority_counts") or {}
    expected_counts = {p: int(expected_raw.get(p, -1)) for p in ("P0", "P1", "P2")}
    if actual_counts != expected_counts:
        errors.append(f"priority mismatch actual={actual_counts} expected={expected_counts}")

    enrichments = delta.get("mechanism_enrichments")
    if not isinstance(enrichments, list):
        enrichments = []
        errors.append("mechanism_enrichments must be list")
    enriched_tokens: set[str] = set()
    for index, row in enumerate(enrichments):
        prefix = f"mechanism_enrichments[{index}]"
        if not isinstance(row, dict):
            errors.append(f"{prefix}: object required")
            continue
        token = row.get("token")
        if not isinstance(token, str) or token not in current_open:
            errors.append(f"{prefix}: token must be currently open")
            continue
        if token in enriched_tokens:
            errors.append(f"{token}: duplicate mechanism enrichment")
        enriched_tokens.add(token)
        base_mechanism = base_by_token[token].get("mechanism") or {}
        if row.get("mechanism_id") != base_mechanism.get("id"):
            errors.append(f"{token}: mechanism_id does not match base registry")
        spec_path = row.get("spec_path")
        if not isinstance(spec_path, str) or not spec_path.strip():
            errors.append(f"{token}: spec_path required")
        else:
            full = repo_path(root, spec_path)
            if not full.is_file():
                errors.append(f"{token}: spec_path does not exist: {spec_path}")
            else:
                spec = load(full)
                if spec.get("claim_allowed") is not False:
                    errors.append(f"{token}: spec must preserve claim_allowed=false")
                if spec.get("token") not in {token, None}:
                    errors.append(f"{token}: spec token mismatch {spec.get('token')!r}")
        if not isinstance(row.get("effect"), str) or not row["effect"].strip():
            errors.append(f"{token}: enrichment effect required")

    priority_rank = {"P0": 0, "P1": 1, "P2": 2}
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
    queue.sort(key=lambda item: (priority_rank.get(item["priority"], 99), item["token"]))

    return Result(
        schema="rll.open_work_mechanism_gate.v2",
        decision="PASS" if not errors else "BLOCKED",
        claim_allowed=False,
        publication_effect="NONE",
        source_view=source_view,
        historical_registry_count=len(base_by_token),
        current_open_count=len(current_open),
        effective_registry_count=len(effective_tokens),
        priority_counts=actual_counts,
        expected_priority_counts=expected_counts,
        resolved_by_evidence=sorted(resolved),
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
    output.write_text(json.dumps(asdict(result), ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "decision": result.decision,
        "historical_registry_count": result.historical_registry_count,
        "current_open_count": result.current_open_count,
        "effective_registry_count": result.effective_registry_count,
        "priority_counts": result.priority_counts,
        "resolved_by_evidence": result.resolved_by_evidence,
        "error_count": len(result.errors),
    }, sort_keys=True))
    for error in result.errors:
        print("ERROR:", error)
    return 0 if result.decision == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
