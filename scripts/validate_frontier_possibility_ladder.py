#!/usr/bin/env python3
"""Fail-closed validator for graded theory-practice possibility tiers."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

LADDER_SCHEMA = "rll.frontier_possibility_ladder.v1"
QUEUE_SCHEMA = "rll.frontier_research_queue.v1"
TOKEN_PREFIX = "TOKEN_VAZIO"
EXPECTED_TIERS = [
    ("P5_NEAR_OPERATIONAL", 5),
    ("P4_FORMALIZABLE_NEAR", 4),
    ("P3_TESTABLE_HYPOTHESIS", 3),
    ("P2_BRIDGE_CANDIDATE", 2),
    ("P1_SPECULATIVE_SEED", 1),
    ("P0_UNRANKABLE_TOKEN_VAZIO", 0),
]


def load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: root must be a mapping")
    return payload


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def validate_ladder(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    require(payload.get("schema") == LADDER_SCHEMA, "unexpected ladder schema", errors)
    require(payload.get("claim_allowed") is False, "claim_allowed must remain false", errors)
    require(payload.get("publication_effect") == "NONE", "publication_effect must be NONE", errors)

    orders = payload.get("separation_of_orders", {})
    require(orders.get("promotion_order") == "evidence_dependency", "promotion order must remain evidence-dependent", errors)
    require(
        orders.get("exploration_order") == "theory_practice_proximity_descending",
        "exploration order must rank theory-practice proximity",
        errors,
    )

    method = payload.get("method", {})
    require(method.get("name") == "categorical_bottleneck_then_pareto", "possibility method must be categorical bottleneck then Pareto", errors)
    dimensions = method.get("dimensions", [])
    require(isinstance(dimensions, list) and len(dimensions) >= 6, "at least six explicit dimensions are required", errors)
    forbidden = set(method.get("forbidden", []))
    require("numeric_truth_probability_without_calibration" in forbidden, "uncalibrated truth probability must be forbidden", errors)
    require("weighted_average_hiding_mandatory_gap" in forbidden, "gap-hiding weighted averages must be forbidden", errors)
    require("token_vazio_as_zero" in forbidden, "TOKEN_VAZIO must not become zero", errors)

    tiers = payload.get("tiers", [])
    observed = [(item.get("id"), item.get("rank")) for item in tiers if isinstance(item, dict)]
    require(observed == EXPECTED_TIERS, "tiers must be complete and ordered from P5 to P0", errors)
    for item in tiers:
        if not isinstance(item, dict):
            errors.append("each tier must be a mapping")
            continue
        tier_id = item.get("id", "UNKNOWN")
        require(bool(item.get("meaning")), f"{tier_id}: meaning required", errors)
        basis = item.get("minimum_basis", [])
        require(isinstance(basis, list) and bool(basis), f"{tier_id}: minimum_basis required", errors)

    rules = payload.get("rules", [])
    require(isinstance(rules, list) and len(rules) >= 5, "possibility rules are incomplete", errors)

    portfolio = payload.get("portfolio", [])
    require(isinstance(portfolio, list) and bool(portfolio), "portfolio must contain ranked fragments", errors)
    valid_tiers = {tier_id for tier_id, _ in EXPECTED_TIERS}
    fragment_ids: list[str] = []
    for item in portfolio:
        if not isinstance(item, dict):
            errors.append("portfolio item must be a mapping")
            continue
        fragment_id = str(item.get("fragment_id", ""))
        fragment_ids.append(fragment_id)
        require(fragment_id.startswith("FRAG-"), f"{fragment_id}: invalid fragment_id", errors)
        require(item.get("exploration_tier") in valid_tiers, f"{fragment_id}: unknown exploration_tier", errors)
        require(bool(item.get("current_promotion_state")), f"{fragment_id}: promotion state required", errors)
        require(bool(item.get("bottleneck")), f"{fragment_id}: bottleneck required", errors)
        require(bool(item.get("next_bridge")), f"{fragment_id}: next_bridge required", errors)
    require(len(fragment_ids) == len(set(fragment_ids)), "portfolio fragment ids must be unique", errors)
    return errors


def validate_against_queue(ladder: dict[str, Any], queue: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    require(queue.get("schema") == QUEUE_SCHEMA, "unexpected queue schema", errors)
    queue_by_id = {
        str(item.get("fragment_id")): item
        for item in queue.get("items", [])
        if isinstance(item, dict)
    }
    for ranked in ladder.get("portfolio", []):
        fragment_id = str(ranked.get("fragment_id", ""))
        source = queue_by_id.get(fragment_id)
        require(source is not None, f"{fragment_id}: ranked fragment absent from queue", errors)
        if source is None:
            continue
        require(
            ranked.get("current_promotion_state") == source.get("state"),
            f"{fragment_id}: promotion state differs from queue",
            errors,
        )
        bottleneck = str(ranked.get("bottleneck", ""))
        queue_gaps = {str(gap) for gap in source.get("gaps", [])}
        if bottleneck.startswith(TOKEN_PREFIX):
            require(bottleneck in queue_gaps, f"{fragment_id}: bottleneck is not recorded in queue gaps", errors)
    return errors


def build_report(ladder_path: Path, queue_path: Path) -> dict[str, Any]:
    ladder = load_yaml(ladder_path)
    queue = load_yaml(queue_path)
    errors = validate_ladder(ladder) + validate_against_queue(ladder, queue)
    tier_counts: dict[str, int] = {}
    for item in ladder.get("portfolio", []):
        tier = str(item.get("exploration_tier", "UNKNOWN"))
        tier_counts[tier] = tier_counts.get(tier, 0) + 1
    return {
        "schema": "rll.frontier_possibility_ladder.validation.v1",
        "status": "PASS" if not errors else "FAIL",
        "claim_allowed": False,
        "publication_effect": "NONE",
        "ladder_sha256": sha256(ladder_path),
        "queue_sha256": sha256(queue_path),
        "tier_count": len(ladder.get("tiers", [])),
        "portfolio_count": len(ladder.get("portfolio", [])),
        "tier_counts": tier_counts,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ladder", type=Path, required=True)
    parser.add_argument("--queue", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    report = build_report(args.ladder, args.queue)
    text = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
