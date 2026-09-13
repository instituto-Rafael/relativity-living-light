#!/usr/bin/env python3
"""Validate the RLL safe-expansion contract and gap dependency graph."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "data/governance/RLL_SAFE_EXPANSION_CONTRACT_V1.json"
GAPS = ROOT / "data/governance/RLL_GAP_DECOMPOSITION_V1.json"

REQUIRED_GATES = {
    "IDENTITY",
    "SCOPE",
    "BASELINE",
    "SCHEMA",
    "CAPABILITY",
    "READ_ONLY",
    "CANARY",
    "ROBUSTNESS",
    "SCALE",
    "CONTROL",
}

REQUIRED_INVARIANTS = {
    "SOURCE != CONFIG != ARTEFACT != EXECUTION != EVIDENCE != CLAIM",
    "TOKEN_VAZIO != 0",
    "IMPLEMENTED_UNTESTED != PASS",
    "CONFIG_ACCEPTED != CONFIG_EFFECTIVE",
    "RETRIEVAL_SCORE != TRUTH",
    "AI_GENERATED_REPORT != PRIMARY_SOURCE",
    "FIT_SUCCESS != SCIENTIFIC_CLAIM",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _cycle_errors(items: list[dict[str, Any]]) -> list[str]:
    ids = {item["id"] for item in items}
    deps = {
        item["id"]: [d for d in item.get("depends_on", []) if d in ids]
        for item in items
    }
    visiting: set[str] = set()
    visited: set[str] = set()
    errors: list[str] = []

    def visit(node: str, chain: list[str]) -> None:
        if node in visited:
            return
        if node in visiting:
            errors.append("dependency cycle: " + " -> ".join(chain + [node]))
            return
        visiting.add(node)
        for dep in deps[node]:
            visit(dep, chain + [node])
        visiting.remove(node)
        visited.add(node)

    for node in ids:
        visit(node, [])
    return errors


def build_report() -> dict[str, Any]:
    contract = load_json(CONTRACT)
    gaps = load_json(GAPS)
    errors: list[str] = []

    gate_ids = {g["id"] for g in contract.get("gates", [])}
    missing_gates = sorted(REQUIRED_GATES - gate_ids)
    if missing_gates:
        errors.append(f"missing gates: {missing_gates}")

    invariants = set(contract.get("invariants", []))
    missing_invariants = sorted(REQUIRED_INVARIANTS - invariants)
    if missing_invariants:
        errors.append(f"missing invariants: {missing_invariants}")

    items = gaps.get("items", [])
    ids = [item.get("id") for item in items]
    if len(ids) != len(set(ids)):
        errors.append("duplicate gap ids")

    id_set = set(ids)
    for item in items:
        for field in ("id", "domain", "status", "claim_allowed", "depends_on", "next_step"):
            if field not in item:
                errors.append(f"{item.get('id', '<unknown>')}: missing {field}")
        for dep in item.get("depends_on", []):
            if dep not in id_set and not str(dep).startswith("EXTERNAL:"):
                errors.append(f"{item['id']}: unknown dependency {dep}")
        if item.get("claim_allowed") is True and item.get("status") not in set(gaps.get("resolved_statuses", [])):
            errors.append(f"{item['id']}: unresolved item cannot allow claim")

    errors.extend(_cycle_errors(items))

    resolved = set(gaps.get("resolved_statuses", []))
    status_by_id = {item["id"]: item["status"] for item in items}
    actionable = []
    for item in items:
        if item["status"] in resolved:
            continue
        internal_deps = [d for d in item.get("depends_on", []) if d in status_by_id]
        if all(status_by_id[d] in resolved for d in internal_deps):
            actionable.append(item["id"])

    return {
        "schema": "rll.safe_expansion_gate_report.v1",
        "pass": not errors,
        "claim_allowed": False,
        "errors": errors,
        "gap_count": len(items),
        "resolved_count": sum(item["status"] in resolved for item in items),
        "actionable_now": sorted(actionable),
        "status": "SAFE_EXPANSION_CONTRACT_VALID" if not errors else "SAFE_EXPANSION_CONTRACT_BLOCKED",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    report = build_report()
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    print(payload, end="")
    if args.output:
        out = args.output if args.output.is_absolute() else ROOT / args.output
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(payload, encoding="utf-8")
    return 0 if report["pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
