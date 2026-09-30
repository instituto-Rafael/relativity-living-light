#!/usr/bin/env python3
"""Validate the evidence-backed B0/B1 reconciliation dependency graph."""
from __future__ import annotations

import argparse
import json
from collections import deque
from pathlib import Path
from typing import Any, Iterable

DEFAULT_GRAPH = Path("data/governance/RLL_B0_B1_DEPENDENCY_GRAPH_20260816_V1.json")
VERIFIED_EDGE_STATES = {
    "VERIFIED_TEXTUAL_CONTRACT",
    "VERIFIED_EXECUTION_REFERENCE",
    "VERIFIED_IMPLEMENTATION_REFERENCE",
}


def _reachable(start: str, adjacency: dict[str, set[str]], allowed: set[str]) -> set[str]:
    seen = {start}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        for target in adjacency.get(node, set()):
            if target in allowed and target not in seen:
                seen.add(target)
                queue.append(target)
    return seen


def validate(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("claim_allowed") is not False:
        errors.append("claim_allowed must remain false")
    if payload.get("auto_merge") is not False:
        errors.append("auto_merge must remain false")

    nodes = payload.get("nodes")
    edges = payload.get("edges")
    sccs = payload.get("strongly_connected_components")
    if not isinstance(nodes, list) or not nodes:
        return errors + ["nodes must be a non-empty list"]
    if not isinstance(edges, list):
        return errors + ["edges must be a list"]
    if not isinstance(sccs, list):
        return errors + ["strongly_connected_components must be a list"]

    node_ids: list[str] = []
    for node in nodes:
        if not isinstance(node, dict):
            errors.append("each node must be an object")
            continue
        node_id = node.get("id")
        if not isinstance(node_id, str) or not node_id:
            errors.append("each node requires a non-empty id")
            continue
        node_ids.append(node_id)
        for field in ("batch", "ref", "path", "role"):
            if not isinstance(node.get(field), str) or not node[field]:
                errors.append(f"node {node_id} missing {field}")
    if len(node_ids) != len(set(node_ids)):
        errors.append("node ids must be unique")
    node_set = set(node_ids)

    edge_ids: list[str] = []
    adjacency: dict[str, set[str]] = {node_id: set() for node_id in node_set}
    reverse: dict[str, set[str]] = {node_id: set() for node_id in node_set}
    for edge in edges:
        if not isinstance(edge, dict):
            errors.append("each edge must be an object")
            continue
        edge_id = edge.get("id")
        if not isinstance(edge_id, str) or not edge_id:
            errors.append("each edge requires a non-empty id")
            continue
        edge_ids.append(edge_id)
        source = edge.get("from")
        target = edge.get("to")
        if source not in node_set:
            errors.append(f"edge {edge_id} source is unknown: {source}")
        if target not in node_set:
            errors.append(f"edge {edge_id} target is unknown: {target}")
        state = edge.get("state")
        evidence = edge.get("evidence")
        relation = edge.get("relation")
        if state not in VERIFIED_EDGE_STATES:
            errors.append(f"edge {edge_id} has unverified/invalid state: {state}")
        if not isinstance(evidence, str) or not evidence.strip():
            errors.append(f"edge {edge_id} requires explicit evidence")
        if not isinstance(relation, str) or not relation.strip():
            errors.append(f"edge {edge_id} requires relation")
        if source in node_set and target in node_set:
            adjacency[source].add(target)
            reverse[target].add(source)
    if len(edge_ids) != len(set(edge_ids)):
        errors.append("edge ids must be unique")

    for scc in sccs:
        if not isinstance(scc, dict):
            errors.append("each SCC must be an object")
            continue
        scc_id = scc.get("id", "TOKEN_VAZIO_SCC_ID")
        members_raw = scc.get("members")
        if not isinstance(members_raw, list) or len(members_raw) < 2:
            errors.append(f"SCC {scc_id} must have at least two members")
            continue
        members = set(members_raw)
        unknown = members - node_set
        if unknown:
            errors.append(f"SCC {scc_id} has unknown members: {sorted(unknown)}")
            continue
        start = members_raw[0]
        forward = _reachable(start, adjacency, members)
        backward = _reachable(start, reverse, members)
        if forward != members or backward != members:
            errors.append(
                f"SCC {scc_id} is not strongly connected: "
                f"forward_missing={sorted(members-forward)} backward_missing={sorted(members-backward)}"
            )

    token_edges = payload.get("token_vazio_edges")
    if not isinstance(token_edges, list):
        errors.append("token_vazio_edges must be an explicit list")
    decision = payload.get("decision")
    if decision != "B0_B1_COMPATIBILITY_GATE_REQUIRED_BEFORE_FORWARD_PORT":
        errors.append("decision must preserve compatibility gate before forward-port")
    return errors


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--graph", type=Path, default=DEFAULT_GRAPH)
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        payload = json.loads(args.graph.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR DEPENDENCY_GRAPH: {exc}")
        return 2
    if not isinstance(payload, dict):
        print("ERROR DEPENDENCY_GRAPH: root must be an object")
        return 2
    errors = validate(payload)
    if errors:
        for error in errors:
            print(f"FAIL DEPENDENCY_GRAPH: {error}")
        return 1
    print(
        "PASS DEPENDENCY_GRAPH: "
        f"nodes={len(payload['nodes'])} edges={len(payload['edges'])} "
        f"sccs={len(payload['strongly_connected_components'])} claim_allowed=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
