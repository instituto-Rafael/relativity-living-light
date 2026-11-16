#!/usr/bin/env python3
"""Validate a frozen RLL authority graph; no network, ref writes, or claim promotion.

Static consistency != fresh provider observation. Requery the live provider
before any reviewed forward-port or governed branch promotion.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from tools.branch_divergence_inventory import classify_topology

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON = ROOT / "data/governance/RLL_CURRENT_STATE_AUTHORITY_GRAPH_20261115_V2.json"
DEFAULT_MD = ROOT / "docs/governance/RLL_CURRENT_STATE_AUTHORITY_GRAPH_20261115_V2.md"
SHA = re.compile(r"[0-9a-f]{40}\Z")


def validate_graph(graph: dict, markdown: str) -> list[str]:
    errors: list[str] = []
    if graph.get("schema") != "rll.current_state_authority_graph.v2":
        errors.append("SCHEMA_MISMATCH")
    if graph.get("claim_allowed") is not False or graph.get("auto_merge") is not False:
        errors.append("UNAUTHORIZED_CLAIM_OR_MERGE")
    if graph.get("publication_effect") != "NONE":
        errors.append("UNAUTHORIZED_PUBLICATION")
    if graph.get("rollback", {}).get("executed") is not False:
        errors.append("ROLLBACK_NOT_PERFORMED")
    if not graph.get("supersedes_snapshot"):
        errors.append("PREDECESSOR_MISSING")

    rows = graph.get("refs")
    refs = {}
    if not isinstance(rows, list) or len(rows) != 4:
        errors.append("REFERENCE_SET_MISMATCH")
        rows = []
    for row in rows:
        if not isinstance(row, dict):
            errors.append("INVALID_REF_ROW")
            continue
        name, sha = row.get("name"), row.get("sha")
        if name in refs or not isinstance(name, str) or not SHA.fullmatch(str(sha)):
            errors.append("INVALID_OR_DUPLICATE_REF")
            continue
        if type(row.get("workflow_files")) is not int or row["workflow_files"] < 0:
            errors.append("INVALID_WORKFLOW_COUNT")
        if type(row.get("protected_metadata")) is not bool:
            errors.append("UNVERIFIED_PROTECTION_TYPE")
        refs[name] = sha
        if sha not in markdown or f"`{name}`" not in markdown:
            errors.append("HUMAN_MACHINE_REF_MISMATCH")

    if set(refs) != {"main", "rll/lab", "rll/integration", "rll/release"}:
        errors.append("CANONICAL_REF_SET_MISMATCH")

    edges = graph.get("compare_edges")
    if not isinstance(edges, list) or len(edges) != 4:
        errors.append("EDGE_SET_MISMATCH")
        edges = []
    pairs = set()
    for edge in edges:
        if not isinstance(edge, dict):
            errors.append("INVALID_EDGE")
            continue
        left, right = edge.get("left"), edge.get("right")
        if (left, right) in pairs or left not in refs or right not in refs or left == right:
            errors.append("INVALID_EDGE_ENDPOINTS")
            continue
        pairs.add((left, right))
        a, b = edge.get("left_only_commits"), edge.get("right_only_commits")
        if type(a) is not int or type(b) is not int or a < 0 or b < 0:
            errors.append("INVALID_COMMIT_COUNTS")
            continue
        if edge.get("topology_status") != classify_topology(a, b):
            errors.append("TOPOLOGY_CLASSIFICATION_MISMATCH")
        if not SHA.fullmatch(str(edge.get("merge_base"))):
            errors.append("INVALID_MERGE_BASE")
        if str(edge.get("merge_base")) not in markdown:
            errors.append("HUMAN_MACHINE_MERGE_BASE_MISMATCH")
        # Presence in the human document: do not mistake this for live freshness.
        if f"{a:,}".replace(",", ",") not in markdown and str(a) not in markdown:
            errors.append("HUMAN_COMMIT_COUNT_MISSING")
        if f"{b:,}" not in markdown and str(b) not in markdown:
            errors.append("HUMAN_COMMIT_COUNT_MISSING")
    if ("main", "rll/lab") not in pairs:
        errors.append("MAIN_LAB_EDGE_MISSING")

    layers = graph.get("layers")
    if not isinstance(layers, list) or {x.get("layer") for x in layers if isinstance(x, dict)} != {
        "EXACT", "EMPIRICAL", "OPERATIONAL"
    }:
        errors.append("EPISTEMIC_LAYERS_MISMATCH")

    gaps = graph.get("gaps")
    if not isinstance(gaps, list) or len(gaps) < 4:
        errors.append("GAP_SET_INCOMPLETE")
    else:
        ids = set()
        for gap in gaps:
            if not isinstance(gap, dict) or not all(gap.get(k) for k in ("id", "state", "next", "issue")):
                errors.append("GAP_NOT_TYPED")
            elif gap["id"] in ids:
                errors.append("GAP_DUPLICATE")
            else:
                ids.add(gap["id"])
    if graph.get("root_authority") != "rll/lab":
        errors.append("REVIEW_TARGET_DRIFT")
    if "claim_allowed=false" not in markdown or "auto_merge=false" not in markdown:
        errors.append("HUMAN_CLAIM_BOUNDARY_MISSING")
    return sorted(set(errors))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MD)
    args = parser.parse_args()
    graph = json.loads(args.json.read_text(encoding="utf-8"))
    errors = validate_graph(graph, args.markdown.read_text(encoding="utf-8"))
    print(json.dumps({
        "status": "PASS_SCOPED_STATIC" if not errors else "FAIL",
        "errors": errors,
        "claim_allowed": False,
        "provider_freshness": "NOT_TESTED",
        "promotion_authority": "NONE",
    }, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
