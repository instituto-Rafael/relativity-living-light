#!/usr/bin/env python3
"""Compile the RLL Omega route forest from compact, auditable inputs.

Frequency means counted route events per versioned structural snapshot.
Vectors are seven-direction routing coordinates derived from declared scores.
Machine-learning readiness is a governance classification; this tool never trains,
validates or deploys a model and never promotes a scientific claim.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
BLUEPRINT = ROOT / "data/knowledge_forest/rll_route_forest_blueprint.json"
EVENTS = ROOT / "data/knowledge_forest/rll_route_flow_events.jsonl"
BLUEPRINT_SCHEMA = ROOT / "schemas/rll_route_forest_blueprint.schema.json"
EVENT_SCHEMA = ROOT / "schemas/rll_route_flow_event.schema.json"
OUTPUT_SCHEMA = ROOT / "schemas/rll_route_forest.schema.json"
ARTIFACT_DIR = ROOT / "artifacts/route-forest"

DIRECTIONS = ("D1", "D2", "D3", "D4", "D5", "D6", "D7")
ML_GATES = (
    "provenance", "rights_license", "immutable_data", "target_definition",
    "feature_schema", "split_contract", "leakage_check", "baseline_model",
    "uncertainty", "bias_review", "model_card", "independent_review",
)
SAFE_REF = re.compile(r"^(?!/)(?!.*(?:^|/)\.\.(?:/|$))[A-Za-z0-9._@+%=-]+(?:/[A-Za-z0-9._@+%=-]+)*$")


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: root must be an object")
    return value


def read_events(path: Path) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        value = json.loads(raw)
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{number}: event must be an object")
        result.append(value)
    return result


def schema_findings(value: Any, schema: dict[str, Any], label: str) -> list[str]:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return [
        f"{label}:{'/'.join(str(part) for part in error.absolute_path) or '<root>'}: {error.message}"
        for error in sorted(validator.iter_errors(value), key=lambda item: list(item.absolute_path))
    ]


def duplicates(values: list[str]) -> list[str]:
    counts = Counter(values)
    return sorted(value for value, count in counts.items() if count > 1)


def graph_state(nodes: set[str], routes: dict[str, dict[str, Any]], roots: set[str]) -> tuple[int, int]:
    adjacency: dict[str, list[str]] = defaultdict(list)
    indegree = {node: 0 for node in nodes}
    for route in routes.values():
        adjacency[route["source"]].append(route["target"])
        indegree[route["target"]] += 1
    queue = deque(sorted(node for node, degree in indegree.items() if degree == 0))
    reduced = dict(indegree)
    visited = 0
    while queue:
        source = queue.popleft()
        visited += 1
        for target in adjacency[source]:
            reduced[target] -= 1
            if reduced[target] == 0:
                queue.append(target)
    cycles = 0 if visited == len(nodes) else len(nodes) - visited
    orphans = sum(1 for node, degree in indegree.items() if node not in roots and degree == 0)
    return cycles, orphans


def semantic_findings(blueprint: dict[str, Any], events: list[dict[str, Any]]) -> list[str]:
    findings: list[str] = []
    if blueprint.get("claim_allowed") is not False:
        findings.append("claim_allowed must remain false")
    if tuple(blueprint["vector_semantics"]["directions"]) != DIRECTIONS:
        findings.append("vector directions must be exactly D1..D7")
    if list(blueprint["regions"]) != [f"R{index}" for index in range(1, 8)]:
        findings.append("regions must be ordered R1..R7")
    if [item["direction"] for item in blueprint["regions"].values()] != list(DIRECTIONS):
        findings.append("region directions must be ordered D1..D7")

    nodes = blueprint["nodes"]
    routes = blueprint["routes"]
    trees = blueprint["trees"]
    region_ids = set(blueprint["regions"])

    membership: dict[str, str] = {}
    roots: set[str] = set()
    for tree_id, tree in trees.items():
        roots.add(tree["root"])
        if tree["root"] not in nodes:
            findings.append(f"{tree_id}: unknown root {tree['root']}")
        elif nodes[tree["root"]]["parent"] is not None:
            findings.append(f"{tree_id}: root parent must be null")
        for node_id in tree["nodes"]:
            if node_id not in nodes:
                findings.append(f"{tree_id}: unknown node {node_id}")
                continue
            if node_id in membership:
                findings.append(f"{node_id}: appears in multiple trees")
            membership[node_id] = tree_id
            if nodes[node_id]["tree"] != tree_id:
                findings.append(f"{node_id}: tree declaration mismatch")
        if tree["training_allowed"] and not all(tree["ml_gates"]):
            findings.append(f"{tree_id}: training requires all twelve gates")
        if tree["training_allowed"] and tree["ml_role"] == "governance_only":
            findings.append(f"{tree_id}: governance-only tree cannot train")

    missing_membership = sorted(set(nodes) - set(membership))
    if missing_membership:
        findings.append(f"nodes outside trees: {missing_membership}")

    for node_id, node in nodes.items():
        if node["tree"] not in trees:
            findings.append(f"{node_id}: unknown tree")
        if node["region"] not in region_ids:
            findings.append(f"{node_id}: unknown region")
        if len(node["scores"]) != 7:
            findings.append(f"{node_id}: score vector must have seven components")
        parent = node["parent"]
        if parent is not None:
            if parent not in nodes:
                findings.append(f"{node_id}: unknown parent")
            elif nodes[parent]["tree"] != node["tree"]:
                findings.append(f"{node_id}: parent belongs to another tree")
        for ref in node["refs"]:
            if not SAFE_REF.fullmatch(ref):
                findings.append(f"{node_id}: unsafe ref {ref}")

    for route_id, route in routes.items():
        if route["source"] == route["target"]:
            findings.append(f"{route_id}: self-loop")
        for endpoint in ("source", "target"):
            node_id = route[endpoint]
            if node_id not in nodes:
                findings.append(f"{route_id}: unknown {endpoint} {node_id}")
        if route["source"] in nodes and route["target"] in nodes:
            if nodes[route["source"]]["tree"] != route["tree"] or nodes[route["target"]]["tree"] != route["tree"]:
                findings.append(f"{route_id}: endpoint tree mismatch")
        for ref in route["refs"]:
            if not SAFE_REF.fullmatch(ref):
                findings.append(f"{route_id}: unsafe ref {ref}")

    event_ids = [event["event_id"] for event in events]
    if duplicates(event_ids):
        findings.append(f"duplicate events: {duplicates(event_ids)}")
    event_routes: set[str] = set()
    window = blueprint["frequency_semantics"]["window_id"]
    for event in events:
        if event["route_id"] not in routes:
            findings.append(f"{event['event_id']}: unknown route")
        else:
            event_routes.add(event["route_id"])
        if event["window_id"] != window:
            findings.append(f"{event['event_id']}: wrong window")
        if not SAFE_REF.fullmatch(event["source_ref"]):
            findings.append(f"{event['event_id']}: unsafe ref")
    without_events = sorted(set(routes) - event_routes)
    if without_events:
        findings.append(f"routes without events: {without_events}")

    cycles, orphans = graph_state(set(nodes), routes, roots)
    if cycles:
        findings.append(f"graph has {cycles} cyclic nodes")
    if orphans:
        findings.append(f"graph has {orphans} non-root orphans")
    return findings


def vector(scores: list[int]) -> list[float]:
    return [score / 4.0 for score in scores]


def norm(values: list[float]) -> float:
    return round(math.sqrt(sum(value * value for value in values)), 12)


def depth(node_id: str, nodes: dict[str, dict[str, Any]]) -> int:
    value = 1
    seen: set[str] = set()
    current = nodes[node_id]
    while current["parent"] is not None:
        parent = current["parent"]
        if parent in seen:
            raise ValueError(f"parent cycle at {parent}")
        seen.add(parent)
        current = nodes[parent]
        value += 1
    return value


def ml_readiness(tree: dict[str, Any]) -> dict[str, Any]:
    passed = sum(bool(value) for value in tree["ml_gates"])
    missing = [name for name, value in zip(ML_GATES, tree["ml_gates"]) if not value]
    if tree["ml_role"] == "governance_only":
        state = "NOT_APPLICABLE"
    elif passed <= 3:
        state = "NOT_READY"
    elif passed <= 7:
        state = "FEATURE_ENGINEERING_ONLY"
    elif passed <= 10:
        state = "BASELINE_READY"
    elif passed < 12 or not tree["training_allowed"]:
        state = "HUMAN_AUTHORIZATION_REQUIRED"
    else:
        state = "TRAINING_ELIGIBLE"
    return {
        "role": tree["ml_role"],
        "state": state,
        "passed_gates": passed,
        "total_gates": 12,
        "missing_gates": missing,
        "training_allowed": tree["training_allowed"],
    }


def compile_forest(blueprint: dict[str, Any], events: list[dict[str, Any]]) -> dict[str, Any]:
    source_nodes = blueprint["nodes"]
    compiled_nodes: list[dict[str, Any]] = []
    for node_id, node in source_nodes.items():
        coordinates = vector(node["scores"])
        compiled_nodes.append({
            "node_id": node_id,
            "tree_id": node["tree"],
            "region_id": node["region"],
            "label": node["label"],
            "kind": node["kind"],
            "epistemic_status": node["status"],
            "parent_id": node["parent"],
            "vector": coordinates,
            "vector_norm": norm(coordinates),
            "source_refs": node["refs"],
        })
    node_map = {node["node_id"]: node for node in compiled_nodes}

    grouped_events: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for event in events:
        grouped_events[event["route_id"]].append(event)

    compiled_routes: list[dict[str, Any]] = []
    for route_id, route in blueprint["routes"].items():
        route_events = grouped_events[route_id]
        source = node_map[route["source"]]["vector"]
        target = node_map[route["target"]]["vector"]
        delta = [round(right - left, 12) for left, right in zip(source, target)]
        compiled_routes.append({
            "route_id": route_id,
            "tree_id": route["tree"],
            "source_node_id": route["source"],
            "target_node_id": route["target"],
            "relation_type": route["relation"],
            "source_refs": route["refs"],
            "claim_allowed": False,
            "flow_frequency": sum(event["weight"] for event in route_events),
            "frequency_unit": "events_per_snapshot",
            "event_kinds": dict(sorted(Counter(event["event_kind"] for event in route_events).items())),
            "vector_delta": delta,
            "delta_norm": norm(delta),
        })

    compiled_regions: list[dict[str, Any]] = []
    for region_id, region in blueprint["regions"].items():
        members = [node for node in compiled_nodes if node["region_id"] == region_id]
        centroid = [
            round(sum(node["vector"][index] for node in members) / len(members), 12)
            for index in range(7)
        ]
        inbound = outbound = 0
        route_ids: set[str] = set()
        for route in compiled_routes:
            source_region = node_map[route["source_node_id"]]["region_id"]
            target_region = node_map[route["target_node_id"]]["region_id"]
            if source_region == region_id:
                outbound += route["flow_frequency"]
                route_ids.add(route["route_id"])
            if target_region == region_id:
                inbound += route["flow_frequency"]
                route_ids.add(route["route_id"])
        compiled_regions.append({
            "region_id": region_id,
            "direction_id": region["direction"],
            "name": region["name"],
            "description": region["description"],
            "node_ids": [node["node_id"] for node in members],
            "route_ids": sorted(route_ids),
            "centroid_vector": centroid,
            "inbound_flow": inbound,
            "outbound_flow": outbound,
            "total_flow": inbound + outbound,
        })

    compiled_trees: list[dict[str, Any]] = []
    for tree_id, tree in blueprint["trees"].items():
        tree_routes = [route for route in compiled_routes if route["tree_id"] == tree_id]
        compiled_trees.append({
            "tree_id": tree_id,
            "domain": tree["domain"],
            "root_node_id": tree["root"],
            "purpose": tree["purpose"],
            "node_ids": tree["nodes"],
            "route_ids": [route["route_id"] for route in tree_routes],
            "node_count": len(tree["nodes"]),
            "route_count": len(tree_routes),
            "depth": max(depth(node_id, source_nodes) for node_id in tree["nodes"]),
            "ml_readiness": ml_readiness(tree),
        })

    roots = {tree["root"] for tree in blueprint["trees"].values()}
    cycles, orphans = graph_state(set(source_nodes), blueprint["routes"], roots)
    ml_states = [
        tree["ml_readiness"]["state"] for tree in compiled_trees
        if tree["ml_readiness"]["state"] != "NOT_APPLICABLE"
    ]
    state = (
        "STRUCTURAL_MAP_READY_ML_BLOCKED"
        if any(value in {"NOT_READY", "FEATURE_ENGINEERING_ONLY"} for value in ml_states)
        else "STRUCTURAL_MAP_READY"
    )
    return {
        "schema": "rll.route_forest.v1",
        "forest_id": blueprint["forest_id"],
        "generated_at": blueprint["generated_at"],
        "source_commit": blueprint["source_commit"],
        "source_refs": blueprint["source_refs"],
        "claim_allowed": False,
        "boundaries": {
            "frequency": blueprint["frequency_semantics"]["boundary"],
            "vectors": blueprint["vector_semantics"]["boundary"],
            "machine_learning": "Feature routing and readiness classification do not train validate or deploy a model.",
        },
        "frequency_window": {
            "window_id": blueprint["frequency_semantics"]["window_id"],
            "window_kind": "structural_snapshot",
            "unit": "events_per_snapshot",
            "event_count": sum(event["weight"] for event in events),
            "event_records": len(events),
        },
        "vector_basis": {
            "class": "[C]",
            "directions": list(DIRECTIONS),
            "score_scale": {str(index): name for index, name in enumerate(blueprint["vector_semantics"]["score_scale"])},
            "normalization": blueprint["vector_semantics"]["normalization"],
            "boundary": blueprint["vector_semantics"]["boundary"],
        },
        "regions": compiled_regions,
        "nodes": compiled_nodes,
        "routes": compiled_routes,
        "trees": compiled_trees,
        "metrics": {
            "region_count": 7,
            "tree_count": len(compiled_trees),
            "node_count": len(compiled_nodes),
            "route_count": len(compiled_routes),
            "event_count": len(events),
            "weighted_flow": sum(route["flow_frequency"] for route in compiled_routes),
            "orphan_count": orphans,
            "cycle_count": cycles,
            "max_depth": max(tree["depth"] for tree in compiled_trees),
            "mean_vector_norm": round(sum(node["vector_norm"] for node in compiled_nodes) / len(compiled_nodes), 12),
        },
        "state": state,
        "next_gate": blueprint["next_gate"],
    }


def canonical(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def graphml(forest: dict[str, Any]) -> str:
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<graphml xmlns="http://graphml.graphdrawing.org/xmlns">',
        '  <key id="label" for="node" attr.name="label" attr.type="string"/>',
        '  <key id="region" for="node" attr.name="region" attr.type="string"/>',
        '  <key id="frequency" for="edge" attr.name="frequency" attr.type="int"/>',
        '  <graph id="RLLRouteForest" edgedefault="directed">',
    ]
    for node in forest["nodes"]:
        label = node["label"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        lines += [
            f'    <node id="{node["node_id"]}">',
            f'      <data key="label">{label}</data>',
            f'      <data key="region">{node["region_id"]}</data>',
            "    </node>",
        ]
    for route in forest["routes"]:
        lines += [
            f'    <edge id="{route["route_id"]}" source="{route["source_node_id"]}" target="{route["target_node_id"]}">',
            f'      <data key="frequency">{route["flow_frequency"]}</data>',
            "    </edge>",
        ]
    return "\n".join(lines + ["  </graph>", "</graphml>", ""])


def write_artifacts(forest: dict[str, Any], directory: Path) -> list[Path]:
    directory.mkdir(parents=True, exist_ok=True)
    report_json = directory / "route_forest_report.json"
    report_md = directory / "ROUTE_FOREST_REPORT.md"
    graph_file = directory / "rll_route_forest.graphml"
    report_json.write_text(canonical(forest), encoding="utf-8")
    graph_file.write_text(graphml(forest), encoding="utf-8")
    table = [
        "# RLL Omega Route Forest Report", "",
        f"- state: `{forest['state']}`",
        f"- regions: `{forest['metrics']['region_count']}`",
        f"- trees: `{forest['metrics']['tree_count']}`",
        f"- nodes: `{forest['metrics']['node_count']}`",
        f"- routes: `{forest['metrics']['route_count']}`",
        f"- events: `{forest['metrics']['event_count']}`", "",
        "## ML readiness", "",
        "| Tree | Role | State | Gates |", "|---|---|---|---:|",
    ]
    for tree in forest["trees"]:
        ready = tree["ml_readiness"]
        table.append(f"| `{tree['tree_id']}` | `{ready['role']}` | `{ready['state']}` | {ready['passed_gates']}/12 |")
    table += [
        "", "Frequency is an event count per snapshot, vectors are routing coordinates,",
        "and this compiler performs no model training or scientific claim promotion.", "",
    ]
    report_md.write_text("\n".join(table), encoding="utf-8")
    material = [report_json, report_md, graph_file]
    checksums = directory / "CHECKSUMS.sha256"
    checksums.write_text(
        "".join(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}\n" for path in sorted(material)),
        encoding="utf-8",
    )
    return material + [checksums]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compile the RLL Omega route forest")
    parser.add_argument("--blueprint", type=Path, default=BLUEPRINT)
    parser.add_argument("--events", type=Path, default=EVENTS)
    parser.add_argument("--artifact-dir", type=Path, default=ARTIFACT_DIR)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--write-report", action="store_true")
    args = parser.parse_args(argv)

    blueprint = read_json(args.blueprint)
    events = read_events(args.events)
    findings = schema_findings(blueprint, read_json(BLUEPRINT_SCHEMA), "blueprint")
    for index, event in enumerate(events):
        findings += schema_findings(event, read_json(EVENT_SCHEMA), f"event[{index}]")
    findings += semantic_findings(blueprint, events)

    forest = None
    if not findings:
        forest = compile_forest(blueprint, events)
        findings += schema_findings(forest, read_json(OUTPUT_SCHEMA), "forest")
    if forest is not None and args.write_report:
        write_artifacts(forest, args.artifact_dir)

    summary = {
        "passed": not findings,
        "findings": findings,
        "forest_id": None if forest is None else forest["forest_id"],
        "state": None if forest is None else forest["state"],
        "regions": None if forest is None else forest["metrics"]["region_count"],
        "trees": None if forest is None else forest["metrics"]["tree_count"],
        "nodes": None if forest is None else forest["metrics"]["node_count"],
        "routes": None if forest is None else forest["metrics"]["route_count"],
        "events": None if forest is None else forest["metrics"]["event_count"],
        "claim_allowed": False,
    }
    print(canonical(summary), end="")
    return 1 if args.strict and findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
