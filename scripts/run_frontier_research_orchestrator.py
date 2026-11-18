#!/usr/bin/env python3
"""Iterate the research prompt gates to a deterministic epistemic fixed point."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

TOKEN_PREFIX = "TOKEN_VAZIO"
PASS_MINIMUM_STAGE = {
    "P0_ATOMIZE": "S0_FRAGMENT",
    "P1_SOURCE": "S1_REFERENCE",
    "P2_FORMAL": "S3_FORMALIZATION",
    "P3_LIMITS": "S3_FORMALIZATION",
    "P4_IMPLEMENT": "S4_IMPLEMENTATION",
    "P5_STATISTICS": "S6_OBSERVATIONAL_VALIDATION",
    "P6_FALSIFY": "S7_FALSIFICATION",
    "P7_REPLICATE": "S8_REPLICATION",
    "P8_SYNTHESIZE": "S9_SYNTHESIS",
}
STAGE_IDS = (
    "S0_FRAGMENT", "S1_REFERENCE", "S2_HYPOTHESIS", "S3_FORMALIZATION",
    "S4_IMPLEMENTATION", "S5_SYNTHETIC_VALIDATION", "S6_OBSERVATIONAL_VALIDATION",
    "S7_FALSIFICATION", "S8_REPLICATION", "S9_SYNTHESIS",
)


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: root must be a mapping")
    return data


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stage_order(contract: dict[str, Any]) -> dict[str, int]:
    if not isinstance(contract, dict):
        raise ValueError("INVALID_CONTRACT_ROOT")
    stages = contract.get("stages")
    if not isinstance(stages, list) or not stages:
        raise ValueError("INVALID_STAGE_INDEX")
    orders: dict[str, int] = {}
    for position, stage in enumerate(stages):
        if (not isinstance(stage, dict) or not isinstance(stage.get("id"), str)
                or not stage["id"] or stage["id"] in orders
                or type(stage.get("order")) is not int or stage["order"] != position):
            raise ValueError("INVALID_STAGE_INDEX")
        orders[stage["id"]] = position
    if tuple(orders) != STAGE_IDS:
        raise ValueError("INVALID_STAGE_INDEX_ORDER")
    return orders


def validate_passes(contract: dict[str, Any]) -> list[dict[str, Any]]:
    evolution = contract.get("prompt_evolution")
    passes = evolution.get("passes") if isinstance(evolution, dict) else None
    if not isinstance(passes, list):
        raise ValueError("INVALID_PASS_INDEX")
    seen: set[str] = set()
    for entry in passes:
        if not isinstance(entry, dict):
            raise ValueError("INVALID_PASS_INDEX")
        pid = entry.get("id")
        if not isinstance(pid, str) or pid not in PASS_MINIMUM_STAGE or pid in seen:
            raise ValueError("INVALID_PASS_INDEX")
        seen.add(pid)
        checks = entry.get("checks")
        if (not isinstance(checks, list) or not checks
                or any(not isinstance(check, str) or not check.strip() for check in checks)
                or not isinstance(entry.get("on_failure"), str)
                or not entry["on_failure"].startswith(TOKEN_PREFIX)):
            raise ValueError("INVALID_PASS_CONTRACT")
    if seen != set(PASS_MINIMUM_STAGE):
        raise ValueError("MISSING_REQUIRED_PASS")
    return passes


def evaluate_item(item: dict[str, Any], contract: dict[str, Any]) -> dict[str, Any]:
    orders = stage_order(contract)
    passes = validate_passes(contract)
    if not isinstance(item, dict):
        raise ValueError("INVALID_QUEUE_ITEM")
    for field in ("fragment_id", "title", "state", "current_stage"):
        if not isinstance(item.get(field), str) or not item[field].strip():
            raise ValueError("INVALID_QUEUE_ITEM_" + field)
    for field in ("evidence", "gaps"):
        values = item.get(field, [])
        if not isinstance(values, list) or any(not isinstance(value, str) or not value.strip() for value in values):
            raise ValueError("INVALID_QUEUE_ITEM_" + field)
    current_stage = item["current_stage"]
    if current_stage not in orders:
        raise ValueError("UNKNOWN_CURRENT_STAGE")
    current_order = orders[current_stage]
    outcomes: list[dict[str, Any]] = []
    for prompt_pass in passes:
        pass_id = str(prompt_pass["id"])
        minimum_stage = PASS_MINIMUM_STAGE[pass_id]
        minimum_order = orders[minimum_stage]
        reached = current_order >= minimum_order
        if reached:
            state = "TOKEN_VAZIO_CHECK_EXECUTION"
            reason = f"declared stage {current_stage} reaches {minimum_stage}; checks not executed by this router"
        else:
            state = str(prompt_pass["on_failure"])
            reason = f"current stage {current_stage} does not reach {minimum_stage}"
        outcomes.append({
            "pass_id": pass_id,
            "minimum_stage": minimum_stage,
            "state": state,
            "reason": reason,
            "checks": list(prompt_pass["checks"]),
            "declared_stage_reached": reached,
            "checks_execution": "NOT_RUN",
        })
    return {
        "fragment_id": item["fragment_id"],
        "title": item["title"],
        "current_stage": current_stage,
        "declared_state": item["state"],
        "prompt_passes": outcomes,
        "unresolved_gaps": list(item.get("gaps", [])),
        "claim_allowed": False,
    }


def iterate_to_fixed_point(
    contract: dict[str, Any],
    queue: dict[str, Any],
    max_iterations: int = 32,
) -> tuple[list[dict[str, Any]], int]:
    stage_order(contract)
    validate_passes(contract)
    if (not isinstance(queue, dict) or contract.get("claim_allowed") is not False
            or queue.get("claim_allowed") is not False):
        raise ValueError("INVALID_QUEUE_OR_CLAIM_POLICY")
    if type(max_iterations) is not int or max_iterations < 2:
        raise ValueError("AT_LEAST_TWO_ITERATIONS_REQUIRED")
    items = queue.get("items")
    if not isinstance(items, list) or not items:
        raise ValueError("INVALID_QUEUE_ITEMS")
    ids: set[str] = set()
    for item in items:
        fid = item.get("fragment_id") if isinstance(item, dict) else None
        if not isinstance(fid, str) or not fid.startswith("FRAG-") or fid in ids:
            raise ValueError("INVALID_OR_DUPLICATE_FRAGMENT_ID")
        ids.add(fid)
    previous: str | None = None
    latest: list[dict[str, Any]] = []
    for iteration in range(1, max_iterations + 1):
        latest = [evaluate_item(item, contract) for item in queue["items"]]
        fingerprint = json.dumps(latest, sort_keys=True, ensure_ascii=False)
        if fingerprint == previous:
            return latest, iteration
        previous = fingerprint
    raise RuntimeError("prompt evolution did not reach a fixed point")


def build_receipt(contract_path: Path, queue_path: Path) -> dict[str, Any]:
    contract = load_yaml(contract_path)
    queue = load_yaml(queue_path)
    results, iterations = iterate_to_fixed_point(contract, queue)
    unresolved = [
        outcome["state"]
        for item in results
        for outcome in item["prompt_passes"]
        if str(outcome["state"]).startswith(TOKEN_PREFIX)
    ]
    return {
        "schema": "rll.frontier_research_prompt_evolution.receipt.v1",
        "status": "FIXED_POINT",
        "fixed_point_scope": "DECLARATION_EVALUATION_ONLY",
        "scientific_checks_execution": "NOT_RUN",
        "iterations": iterations,
        "claim_allowed": False,
        "publication_effect": "NONE",
        "contract_sha256": sha256(contract_path),
        "queue_sha256": sha256(queue_path),
        "item_count": len(results),
        "token_vazio_pass_count": len(unresolved),
        "items": results,
    }


def render_markdown(receipt: dict[str, Any]) -> str:
    lines = [
        "# Frontier research prompt-evolution receipt",
        "",
        f"- status: `{receipt['status']}`",
        f"- iterations to fixed point: `{receipt['iterations']}`",
        f"- fixed point scope: `{receipt['fixed_point_scope']}`",
        f"- scientific checks execution: `{receipt['scientific_checks_execution']}`",
        f"- claim_allowed: `{str(receipt['claim_allowed']).lower()}`",
        f"- TOKEN_VAZIO pass outcomes: `{receipt['token_vazio_pass_count']}`",
        "",
    ]
    for item in receipt["items"]:
        lines.extend([
            f"## {item['fragment_id']} — {item['title']}",
            "",
            f"Current stage: `{item['current_stage']}`  ",
            f"Declared state: `{item['declared_state']}`",
            "",
            "| Pass | State | Boundary |",
            "|---|---|---|",
        ])
        for outcome in item["prompt_passes"]:
            lines.append(f"| `{outcome['pass_id']}` | `{outcome['state']}` | {outcome['reason']} |")
        lines.append("")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--queue", type=Path, required=True)
    parser.add_argument("--json-out", type=Path, required=True)
    parser.add_argument("--md-out", type=Path, required=True)
    args = parser.parse_args()
    receipt = build_receipt(args.contract, args.queue)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.md_out.write_text(render_markdown(receipt), encoding="utf-8")
    print(json.dumps({
        "status": receipt["status"],
        "iterations": receipt["iterations"],
        "items": receipt["item_count"],
        "token_vazio_pass_count": receipt["token_vazio_pass_count"],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
