#!/usr/bin/env python3
"""Validate the RLL dependency queue without promoting gaps to facts."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")


def load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("queue root must be an object")
    return payload


def validate_document(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema") != "rll.execution_queue.v1":
        errors.append("unsupported schema")
    if payload.get("claim_allowed") is not False:
        errors.append("claim_allowed must remain false")
    commit = payload.get("source_main_commit")
    if not isinstance(commit, str) or not COMMIT_RE.fullmatch(commit):
        errors.append("source_main_commit must be a lowercase 40-char SHA")

    existing = payload.get("already_present")
    queue = payload.get("queue")
    if not isinstance(existing, list):
        errors.append("already_present must be an array")
        existing = []
    if not isinstance(queue, list) or not queue:
        errors.append("queue must be a non-empty array")
        queue = []

    existing_ids = [item.get("id") for item in existing if isinstance(item, dict)]
    queue_ids = [item.get("id") for item in queue if isinstance(item, dict)]
    for label, values in (("already_present", existing_ids), ("queue", queue_ids)):
        if len(values) != len(set(values)):
            errors.append(f"duplicate id in {label}")
    overlap = set(existing_ids) & set(queue_ids)
    if overlap:
        errors.append(f"implemented items duplicated in active queue: {sorted(overlap)}")

    queue_set = set(queue_ids)
    graph: dict[str, list[str]] = {}
    for item in queue:
        if not isinstance(item, dict):
            errors.append("queue item must be an object")
            continue
        item_id = item.get("id")
        urgency = item.get("urgency")
        if isinstance(item_id, str) and urgency in {"P0", "P1", "P2"}:
            if not item_id.startswith(f"RLL-{urgency}-"):
                errors.append(f"urgency/id mismatch: {item_id}")
        deps = item.get("depends_on")
        if not isinstance(deps, list):
            errors.append(f"depends_on must be an array: {item_id}")
            deps = []
        graph[str(item_id)] = [str(dep) for dep in deps]
        for dep in deps:
            if dep not in queue_set:
                errors.append(f"unknown dependency {dep} referenced by {item_id}")
        if item.get("evidence_class") == "H" and item.get("state") != "HYPOTHESIS_ONLY":
            errors.append(f"class H must remain HYPOTHESIS_ONLY: {item_id}")
        if item.get("evidence_class") == "P" and str(item.get("state", "")).startswith("DONE"):
            errors.append(f"class P cannot be DONE: {item_id}")
        if not item.get("acceptance"):
            errors.append(f"missing acceptance criteria: {item_id}")
        if not item.get("must_not"):
            errors.append(f"missing forbidden promotions: {item_id}")

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> None:
        if node in visited:
            return
        if node in visiting:
            errors.append(f"dependency cycle detected at {node}")
            return
        visiting.add(node)
        for parent in graph.get(node, []):
            visit(parent)
        visiting.remove(node)
        visited.add(node)

    for node in graph:
        visit(node)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "path",
        nargs="?",
        type=Path,
        default=Path("data/governance/RLL_EXECUTION_QUEUE_20260806_V1.json"),
    )
    args = parser.parse_args()
    try:
        errors = validate_document(load(args.path))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"BLOCKED: {exc}")
        return 2
    if errors:
        for error in errors:
            print(f"BLOCKED: {error}")
        return 1
    print("PASS: RLL execution queue is dependency-ordered and claim-bounded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
