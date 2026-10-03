#!/usr/bin/env python3
"""Build a Jekyll data bundle with repository provenance and pending relation state."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
GRAPH_PATH = ROOT / "results/relational_validation/packages/ACADEMIC_CORR_001/relation_graph.json"
PACKAGE_PATH = ROOT / "results/relational_validation/packages/ACADEMIC_CORR_001/package.yml"
BIBLIOGRAPHY_PATH = ROOT / "data/research_fragments/academic_correlation_sources.yml"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def load_json(path: Path) -> tuple[dict[str, Any], bytes]:
    raw = path.read_bytes()
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ValueError(f"expected a JSON object: {path}")
    return value, raw


def load_yaml(path: Path) -> tuple[dict[str, Any], bytes]:
    raw = path.read_bytes()
    value = yaml.safe_load(raw.decode("utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected a YAML mapping: {path}")
    return value, raw


def build_bundle(
    graph: dict[str, Any],
    package: dict[str, Any],
    bibliography: dict[str, Any],
    source_sha256: dict[str, str],
    revision: str,
    run_id: str,
    candidate: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if graph.get("claim_allowed") is not False or package.get("claim_allowed") is not False:
        raise ValueError("claim_allowed must remain false in both graph and package")
    if bibliography.get("claim_allowed") is not False:
        raise ValueError("bibliography claim_allowed must remain false")

    nodes = graph.get("nodes")
    edges = graph.get("edges")
    papers = bibliography.get("papers")
    if not isinstance(nodes, list) or not isinstance(edges, list) or not isinstance(papers, list):
        raise ValueError("graph nodes/edges and bibliography papers must be lists")
    node_ids = [node.get("id") for node in nodes if isinstance(node, dict)]
    if len(node_ids) != len(nodes) or len(node_ids) != len(set(node_ids)):
        raise ValueError("graph node IDs must be present and unique")
    node_id_set = set(node_ids)

    paper_ids = set()
    paper_by_node: dict[str, list[str]] = {}
    for paper in papers:
        if not isinstance(paper, dict) or paper.get("claim_allowed") is not False:
            raise ValueError("bibliography entries must be mappings with claim_allowed=false")
        graph_node_id = paper.get("graph_node_id")
        work_id = paper.get("work_id")
        if graph_node_id not in node_id_set or not isinstance(work_id, str) or not work_id:
            raise ValueError("bibliography entry must refer to an existing graph node and work ID")
        if work_id in paper_ids:
            raise ValueError(f"duplicate bibliography work ID: {work_id}")
        paper_ids.add(work_id)
        paper_by_node.setdefault(graph_node_id, []).append(work_id)

    rendered_edges = []
    for edge in edges:
        if not isinstance(edge, dict) or edge.get("from") not in node_id_set or edge.get("to") not in node_id_set:
            raise ValueError("relation graph edge contains an unknown endpoint")
        evidence_work_ids = sorted(
            set(paper_by_node.get(edge["from"], []) + paper_by_node.get(edge["to"], []))
        )
        rendered_edges.append(
            {
                **edge,
                "evidence_work_ids": evidence_work_ids,
                "review_state": "RELATIONAL_PENDING",
            }
        )

    candidate_payload = None
    if candidate is not None:
        if candidate.get("schema") != "rll.research_source_candidate.v1":
            raise ValueError("candidate intake schema mismatch")
        if candidate.get("claim_allowed") is not False:
            raise ValueError("candidate intake claim_allowed must remain false")
        source_digest = candidate.get("source_sha256")
        if not isinstance(source_digest, str) or len(source_digest) != 64:
            raise ValueError("candidate source response SHA-256 is missing")
        for edge in candidate.get("candidate_relations", []):
            if edge.get("to") not in node_id_set or edge.get("from") != candidate.get("work_id"):
                raise ValueError("candidate relation edge contains an unknown endpoint")
            if edge.get("source_sha256") != source_digest:
                raise ValueError("candidate relation edge source digest does not match the intake")
            if edge.get("claim_allowed") is not False or edge.get("review_state") != "RELATIONAL_PENDING":
                raise ValueError("candidate relations must remain claim-gated and pending")
        candidate_payload = candidate

    return {
        "schema": "rll.research_fragment_page_data.v1",
        "graph_id": graph.get("graph_id"),
        "claim_id": graph.get("claim_id"),
        "state": package.get("state"),
        "status": graph.get("status"),
        "claim_allowed": False,
        "boundary": graph.get("boundary"),
        "next_gate": graph.get("next_gate"),
        "nodes": nodes,
        "edges": rendered_edges,
        "bibliography": papers,
        "bibliography_source_digest": bibliography.get("raw_source_digest", "TOKEN_VAZIO"),
        "candidate_intake": candidate_payload,
        "receipt": {
            "revision": revision,
            "run_id": run_id,
            "source_sha256": source_sha256,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--candidate-intake", type=Path)
    parser.add_argument("--revision", default=os.environ.get("GITHUB_SHA", "WORKING_TREE"))
    parser.add_argument("--run-id", default=os.environ.get("GITHUB_RUN_ID", "local-run"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    graph, graph_raw = load_json(GRAPH_PATH)
    package, package_raw = load_yaml(PACKAGE_PATH)
    bibliography, bibliography_raw = load_yaml(BIBLIOGRAPHY_PATH)
    source_sha256 = {
        "relation_graph": sha256_bytes(graph_raw),
        "package": sha256_bytes(package_raw),
        "bibliography": sha256_bytes(bibliography_raw),
    }
    candidate = None
    if args.candidate_intake is not None:
        candidate, _ = load_json(args.candidate_intake)
    bundle = build_bundle(
        graph=graph,
        package=package,
        bibliography=bibliography,
        source_sha256=source_sha256,
        revision=args.revision,
        run_id=args.run_id,
        candidate=candidate,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(bundle, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"built research fragment page data: {bundle['graph_id']} "
        f"state={bundle['status']} nodes={len(bundle['nodes'])} edges={len(bundle['edges'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
