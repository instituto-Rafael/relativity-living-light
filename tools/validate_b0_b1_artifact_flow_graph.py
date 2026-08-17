#!/usr/bin/env python3
"""Validate B0/B1 generated-artifact flow semantics without inventing consumers."""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

DEFAULT_GRAPH = Path("data/governance/RLL_B0_B1_ARTIFACT_FLOW_GRAPH_20260816_V1.json")
RELATIONS = {
    "PRODUCES",
    "EXECUTES_PRODUCER",
    "READS_EXECUTABLY",
    "UPLOADS_CUSTODY",
    "DOCUMENTED_AUTHORITY_REFERENCE",
}


def validate(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("claim_allowed") is not False:
        errors.append("claim_allowed must remain false")
    if payload.get("auto_merge") is not False:
        errors.append("auto_merge must remain false")

    nodes = payload.get("nodes")
    edges = payload.get("edges")
    statuses = payload.get("artifact_status")
    if not isinstance(nodes, list) or not nodes:
        return errors + ["nodes must be a non-empty list"]
    if not isinstance(edges, list):
        return errors + ["edges must be a list"]
    if not isinstance(statuses, list):
        return errors + ["artifact_status must be a list"]

    node_ids: list[str] = []
    node_kind: dict[str, str] = {}
    for node in nodes:
        if not isinstance(node, dict):
            errors.append("each node must be an object")
            continue
        node_id = node.get("id")
        kind = node.get("kind")
        if not isinstance(node_id, str) or not node_id:
            errors.append("each node requires a non-empty id")
            continue
        if not isinstance(kind, str) or not kind:
            errors.append(f"node {node_id} requires kind")
        node_ids.append(node_id)
        node_kind[node_id] = str(kind)
    if len(node_ids) != len(set(node_ids)):
        errors.append("node ids must be unique")
    node_set = set(node_ids)
    artifacts = {node_id for node_id, kind in node_kind.items() if kind == "artifact"}

    edge_ids: list[str] = []
    relation_count: Counter[str] = Counter()
    producers: Counter[str] = Counter()
    readers: Counter[str] = Counter()
    custody: Counter[str] = Counter()
    doc_refs: Counter[str] = Counter()

    for edge in edges:
        if not isinstance(edge, dict):
            errors.append("each edge must be an object")
            continue
        edge_id = edge.get("id")
        source = edge.get("from")
        target = edge.get("to")
        relation = edge.get("relation")
        evidence = edge.get("evidence")
        if not isinstance(edge_id, str) or not edge_id:
            errors.append("each edge requires id")
            continue
        edge_ids.append(edge_id)
        if source not in node_set:
            errors.append(f"edge {edge_id} source is unknown: {source}")
        if target not in node_set:
            errors.append(f"edge {edge_id} target is unknown: {target}")
        if relation not in RELATIONS:
            errors.append(f"edge {edge_id} has invalid relation: {relation}")
            continue
        if not isinstance(evidence, str) or not evidence.strip():
            errors.append(f"edge {edge_id} requires explicit evidence")
        relation_count[relation] += 1
        if target in artifacts:
            if relation == "PRODUCES":
                producers[target] += 1
            elif relation == "READS_EXECUTABLY":
                readers[target] += 1
            elif relation == "UPLOADS_CUSTODY":
                custody[target] += 1
            elif relation == "DOCUMENTED_AUTHORITY_REFERENCE":
                doc_refs[target] += 1

    if len(edge_ids) != len(set(edge_ids)):
        errors.append("edge ids must be unique")

    for artifact in sorted(artifacts):
        if producers[artifact] < 1:
            errors.append(f"artifact {artifact} has no verified producer edge")

    status_by_artifact: dict[str, dict[str, Any]] = {}
    for status in statuses:
        if not isinstance(status, dict):
            errors.append("each artifact_status entry must be an object")
            continue
        artifact = status.get("artifact")
        if artifact not in artifacts:
            errors.append(f"artifact_status references unknown artifact: {artifact}")
            continue
        if artifact in status_by_artifact:
            errors.append(f"duplicate artifact_status: {artifact}")
        status_by_artifact[str(artifact)] = status

    if set(status_by_artifact) != artifacts:
        errors.append(
            "artifact_status must cover every artifact exactly once: "
            f"missing={sorted(artifacts-set(status_by_artifact))} "
            f"extra={sorted(set(status_by_artifact)-artifacts)}"
        )

    for artifact, status in status_by_artifact.items():
        if status.get("producer") != "VERIFIED":
            errors.append(f"artifact {artifact} producer status must be VERIFIED")
        if status.get("custody") == "VERIFIED" and custody[artifact] < 1:
            errors.append(f"artifact {artifact} claims custody VERIFIED without UPLOADS_CUSTODY edge")
        executable = status.get("executable_consumer")
        if executable == "VERIFIED" and readers[artifact] < 1:
            errors.append(f"artifact {artifact} claims executable consumer VERIFIED without READS_EXECUTABLY edge")
        if isinstance(executable, str) and executable.startswith("TOKEN_VAZIO") and readers[artifact] > 0:
            errors.append(f"artifact {artifact} keeps executable consumer TOKEN_VAZIO despite verified READS_EXECUTABLY edge")
        documented = status.get("documented_authority_reference")
        if documented == "VERIFIED" and doc_refs[artifact] < 1:
            errors.append(f"artifact {artifact} claims documented authority VERIFIED without documentary edge")

    scope = payload.get("resolved_scope")
    if not isinstance(scope, dict):
        errors.append("resolved_scope must be an object")
    else:
        expected_counts = {
            "generated_artifacts_mapped": len(artifacts),
            "producer_edges": relation_count["PRODUCES"],
            "executable_consumer_edges": relation_count["READS_EXECUTABLY"],
            "custody_edges": relation_count["UPLOADS_CUSTODY"],
            "documented_authority_edges": relation_count["DOCUMENTED_AUTHORITY_REFERENCE"],
        }
        for field, expected in expected_counts.items():
            if scope.get(field) != expected:
                errors.append(f"resolved_scope.{field}={scope.get(field)!r}, expected {expected}")

    if payload.get("decision") != "PARTIAL_CLOSURE_GENERATED_ARTIFACT_EDGES_VERIFIED_WITH_EXPLICIT_CONSUMER_GAPS":
        errors.append("decision must preserve partial closure with explicit consumer gaps")
    residuals = payload.get("residuals")
    if not isinstance(residuals, list):
        errors.append("residuals must be an explicit list")
    return errors


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--graph", type=Path, default=DEFAULT_GRAPH)
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        payload = json.loads(args.graph.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR ARTIFACT_FLOW: {exc}")
        return 2
    if not isinstance(payload, dict):
        print("ERROR ARTIFACT_FLOW: root must be an object")
        return 2
    errors = validate(payload)
    if errors:
        for error in errors:
            print(f"FAIL ARTIFACT_FLOW: {error}")
        return 1
    scope = payload["resolved_scope"]
    print(
        "PASS ARTIFACT_FLOW: "
        f"artifacts={scope['generated_artifacts_mapped']} producers={scope['producer_edges']} "
        f"executable_consumers={scope['executable_consumer_edges']} custody={scope['custody_edges']} "
        "claim_allowed=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
