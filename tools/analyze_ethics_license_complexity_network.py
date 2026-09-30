#!/usr/bin/env python3
"""Deterministic structural analysis for the Ethics/License sustainment graph.

This tool measures topology, dependency reachability and closure routing. Its
metrics are structural diagnostics only: node degree, reachability, component
membership or centrality-like counts MUST NOT be interpreted as truth,
scientific evidence strength, ethical worth or legal validity.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from collections import deque
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY = ROOT / "governance/ethics_license_complexity_sustainment.v1.json"
VALIDATOR_PATH = ROOT / "tools/validate_ethics_license_complexity_sustainment.py"


def _load_validator():
    spec = importlib.util.spec_from_file_location("ethics_license_validator_for_network", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load sustainment validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _adjacency(nodes: list[str], edges: list[dict[str, Any]]):
    out = {node: [] for node in nodes}
    incoming = {node: [] for node in nodes}
    for edge in sorted(edges, key=lambda item: item["id"]):
        out[edge["source"]].append((edge["target"], edge["id"], edge["relation"]))
        incoming[edge["target"]].append((edge["source"], edge["id"], edge["relation"]))
    for values in out.values():
        values.sort()
    for values in incoming.values():
        values.sort()
    return out, incoming


def reachable_from(start: str, adjacency: dict[str, list[tuple[str, str, str]]]) -> list[str]:
    seen = {start}
    queue = deque([start])
    while queue:
        current = queue.popleft()
        for target, _edge_id, _relation in adjacency[current]:
            if target not in seen:
                seen.add(target)
                queue.append(target)
    seen.remove(start)
    return sorted(seen)


def shortest_path(start: str, goal: str, adjacency: dict[str, list[tuple[str, str, str]]]):
    if start == goal:
        return [start]
    queue = deque([start])
    parent: dict[str, str | None] = {start: None}
    while queue:
        current = queue.popleft()
        for target, _edge_id, _relation in adjacency[current]:
            if target in parent:
                continue
            parent[target] = current
            if target == goal:
                path = [goal]
                cursor = goal
                while parent[cursor] is not None:
                    cursor = parent[cursor]  # type: ignore[index]
                    path.append(cursor)
                return list(reversed(path))
            queue.append(target)
    return None


def strongly_connected_components(nodes: list[str], adjacency: dict[str, list[tuple[str, str, str]]]):
    index = 0
    stack: list[str] = []
    on_stack: set[str] = set()
    indices: dict[str, int] = {}
    lowlink: dict[str, int] = {}
    components: list[list[str]] = []

    def visit(node: str) -> None:
        nonlocal index
        indices[node] = index
        lowlink[node] = index
        index += 1
        stack.append(node)
        on_stack.add(node)
        for target, _eid, _rel in adjacency[node]:
            if target not in indices:
                visit(target)
                lowlink[node] = min(lowlink[node], lowlink[target])
            elif target in on_stack:
                lowlink[node] = min(lowlink[node], indices[target])
        if lowlink[node] == indices[node]:
            component: list[str] = []
            while True:
                member = stack.pop()
                on_stack.remove(member)
                component.append(member)
                if member == node:
                    break
            components.append(sorted(component))

    for node in sorted(nodes):
        if node not in indices:
            visit(node)
    return sorted(components, key=lambda group: (group[0], len(group)))


def build_report(registry_path: Path = DEFAULT_REGISTRY, root: Path = ROOT) -> dict[str, Any]:
    data = json.loads(registry_path.read_text(encoding="utf-8"))
    validator = _load_validator()
    validator.validate_graph(data, root)

    network = data["complex_network"]
    node_records = sorted(network["nodes"], key=lambda item: item["id"])
    edges = sorted(network["edges"], key=lambda item: item["id"])
    nodes = [item["id"] for item in node_records]
    node_type = {item["id"]: item["type"] for item in node_records}
    adjacency, incoming = _adjacency(nodes, edges)

    per_node: dict[str, Any] = {}
    all_reach: dict[str, list[str]] = {}
    for node in nodes:
        reach = reachable_from(node, adjacency)
        all_reach[node] = reach
        per_node[node] = {
            "type": node_type[node],
            "in_degree": len(incoming[node]),
            "out_degree": len(adjacency[node]),
            "reachable_count": len(reach),
            "reachable_nodes": reach,
            "predecessors": sorted({item[0] for item in incoming[node]}),
            "successors": sorted({item[0] for item in adjacency[node]}),
        }

    components = strongly_connected_components(nodes, adjacency)
    cyclic_components = [group for group in components if len(group) > 1]
    self_loops = sorted(edge["id"] for edge in edges if edge["source"] == edge["target"])
    roots = sorted(node for node in nodes if not incoming[node])
    sinks = sorted(node for node in nodes if not adjacency[node])
    isolated = sorted(node for node in nodes if not incoming[node] and not adjacency[node])

    closure_target = "NODE-RECEIPT"
    evidence_target = "NODE-EVIDENCE"
    token_node = "NODE-TOKEN-VAZIO"
    token_to_receipt = shortest_path(token_node, closure_target, adjacency)
    token_to_evidence = shortest_path(token_node, evidence_target, adjacency)
    operational_to_evidence = shortest_path("NODE-ETHICS-OPERATIONAL", evidence_target, adjacency)

    edge_relations: dict[str, int] = {}
    for edge in edges:
        edge_relations[edge["relation"]] = edge_relations.get(edge["relation"], 0) + 1

    reach_pairs = sum(len(value) for value in all_reach.values())
    possible_ordered_pairs = len(nodes) * max(len(nodes) - 1, 0)
    reachability_fraction = (reach_pairs / possible_ordered_pairs) if possible_ordered_pairs else 0.0

    invariants = {
        "no_dangling_edges": True,
        "unique_node_ids": len(nodes) == len(set(nodes)),
        "unique_edge_ids": len(edges) == len({edge["id"] for edge in edges}),
        "token_has_receipt_route": token_to_receipt is not None,
        "operational_ethics_has_evidence_route": operational_to_evidence is not None,
        "claim_allowed_false": data["claim_allowed"] is False,
        "legal_effect_claim_false": data["legal_effect_claim"] is False,
        "graph_metrics_are_not_truth_scores": True,
    }
    passed = all(invariants.values())

    return {
        "schema": "rll.ethics_license_complexity_network_analysis.v1",
        "state": "PASS_STRUCTURAL_NETWORK_ANALYSIS" if passed else "BLOCKED_STRUCTURAL_NETWORK_ANALYSIS",
        "claim_allowed": False,
        "scientific_confirmation": False,
        "legal_effect_claim": False,
        "publication_effect": "NONE",
        "registry_path": str(registry_path.relative_to(root)),
        "registry_sha256": sha256_file(registry_path),
        "boundary": "topology and reachability describe governance structure only; they are not truth, ethical-worth, causal, legal-validity or scientific-evidence scores",
        "graph": {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "root_nodes": roots,
            "sink_nodes": sinks,
            "isolated_nodes": isolated,
            "self_loop_edge_ids": self_loops,
            "strongly_connected_components": components,
            "cyclic_components": cyclic_components,
            "reachable_ordered_pairs": reach_pairs,
            "possible_ordered_pairs": possible_ordered_pairs,
            "reachability_fraction_structural_only": reachability_fraction,
            "edge_relation_counts": dict(sorted(edge_relations.items())),
            "per_node": per_node,
        },
        "critical_routes": {
            "TOKEN_VAZIO_to_RECEIPT": token_to_receipt,
            "TOKEN_VAZIO_to_EVIDENCE": token_to_evidence,
            "ETHICS_OPERATIONAL_to_EVIDENCE": operational_to_evidence,
        },
        "invariants": invariants,
        "F_ok": [key for key, value in invariants.items() if value],
        "F_gap": [key for key, value in invariants.items() if not value],
        "F_next": "if PASS, bind this deterministic report to CI artifact/hash before closing TOKEN_VAZIO_COMPLEX_NETWORK_RUNTIME; do not close legal, rights, physical-field, metric, stability or independent-review gaps",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("registry", nargs="?", default=str(DEFAULT_REGISTRY))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = build_report(Path(args.registry), ROOT)
    payload = json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0 if report["state"] == "PASS_STRUCTURAL_NETWORK_ANALYSIS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
