#!/usr/bin/env python3
"""Fail-closed validator for the RLL formula↔literature evidence graph.

This validator deliberately does not compute a scalar truth score. It validates
provenance, independence, falsifiability, TOKEN_VAZIO completeness and monotone
history/coverage semantics.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ALLOWED_RELATIONS = {
    "SUPPORTS_EXACT", "CONTRADICTS_EXACT", "CLASS_MATCH",
    "METHOD_ONLY", "SYSTEMATICS_CONTROL", "BACKGROUND",
}
ALLOWED_STATES = {
    "PAIR_A", "PAIR_B", "CLASS_MATCH", "CONTRADICTED_EXTERNAL_2PLUS",
    "TOKEN_VAZIO_EXACT_TEST", "MALFORMED", "REJECTED_NON_FALSIFIABLE",
}


def fail(msg: str) -> None:
    raise ValueError(msg)


def _require_nonempty(value: Any, label: str) -> None:
    if not isinstance(value, str) or not value.strip():
        fail(f"{label}: expected non-empty string")


def validate_graph(data: dict[str, Any]) -> None:
    if data.get("schema") != "rll.formula_literature_edges.v1":
        fail("schema must be rll.formula_literature_edges.v1")
    if data.get("append_only") is not True:
        fail("append_only must be true")
    if data.get("claim_allowed") is not False:
        fail("claim_allowed must remain false")
    if data.get("publication_effect") != "NONE":
        fail("publication_effect must remain NONE")

    inventory = data.get("source_inventory") or {}
    if inventory.get("extracted_formula_manifest") != 486:
        fail("source inventory must preserve the verified 486-formula manifest count")
    if inventory.get("desi_hypothesis_intake") != 50:
        fail("source inventory must preserve the 50-hypothesis DESI intake count")
    if inventory.get("raw_union_upper_bound_before_dedup") != 536:
        fail("536 is a raw upper bound before dedup, not a unique formula count")
    dedup = str(inventory.get("deduplicated_total", ""))
    if not dedup.startswith("TOKEN_VAZIO"):
        fail("deduplicated_total must stay TOKEN_VAZIO until a deterministic receipt exists")

    references = data.get("references")
    edges = data.get("edges")
    states = data.get("formula_states")
    if not isinstance(references, list) or not isinstance(edges, list) or not isinstance(states, list):
        fail("references, edges and formula_states must be arrays")

    ref_by_id: dict[str, dict[str, Any]] = {}
    for ref in references:
        rid = ref.get("reference_id")
        _require_nonempty(rid, "reference_id")
        if rid in ref_by_id:
            fail(f"duplicate reference_id: {rid}")
        _require_nonempty(ref.get("independence_group"), f"{rid}.independence_group")
        _require_nonempty(ref.get("persistent_id"), f"{rid}.persistent_id")
        _require_nonempty(ref.get("url"), f"{rid}.url")
        controls = ref.get("false_positive_controls")
        if not isinstance(controls, list) or not controls or not all(isinstance(x, str) and x.strip() for x in controls):
            fail(f"{rid}: false_positive_controls must be a non-empty list")
        ref_by_id[rid] = ref

    edge_by_id: dict[str, dict[str, Any]] = {}
    edges_by_formula: dict[str, list[dict[str, Any]]] = {}
    for edge in edges:
        eid = edge.get("edge_id")
        _require_nonempty(eid, "edge_id")
        if eid in edge_by_id:
            fail(f"duplicate edge_id: {eid}")
        fid = edge.get("formula_id")
        rid = edge.get("reference_id")
        _require_nonempty(fid, f"{eid}.formula_id")
        if rid not in ref_by_id:
            fail(f"{eid}: unknown reference_id {rid!r}")
        if edge.get("relation") not in ALLOWED_RELATIONS:
            fail(f"{eid}: invalid relation")
        if edge.get("immutable_event") is not True:
            fail(f"{eid}: immutable_event must be true")
        if edge.get("independence_group") != ref_by_id[rid].get("independence_group"):
            fail(f"{eid}: edge/reference independence_group mismatch")
        _require_nonempty(edge.get("scope"), f"{eid}.scope")
        _require_nonempty(edge.get("provenance"), f"{eid}.provenance")
        edge_by_id[eid] = edge
        edges_by_formula.setdefault(fid, []).append(edge)

    for state in states:
        fid = state.get("formula_id")
        _require_nonempty(fid, "formula_state.formula_id")
        st = state.get("state")
        if st not in ALLOWED_STATES:
            fail(f"{fid}: invalid state {st!r}")
        _require_nonempty(state.get("falsifier"), f"{fid}.falsifier")
        _require_nonempty(state.get("next_test"), f"{fid}.next_test")
        vec = state.get("evidence_vector") or {}
        if vec.get("claim_boundary") != "claim_allowed=false":
            fail(f"{fid}: evidence vector cannot promote claim")

        formula_edges = edges_by_formula.get(fid, [])
        exact_edges = [e for e in formula_edges if e.get("relation") in {"SUPPORTS_EXACT", "CONTRADICTS_EXACT"}]
        groups = {e.get("independence_group") for e in exact_edges}

        if st == "PAIR_A":
            if len(groups) < 2:
                fail(f"{fid}: PAIR_A requires >=2 exact-evidence independence groups")
            for e in exact_edges:
                ref = ref_by_id[e["reference_id"]]
                if not ref.get("false_positive_controls"):
                    fail(f"{fid}: PAIR_A reference lacks false-positive controls")
        if st == "CONTRADICTED_EXTERNAL_2PLUS":
            contra = [e for e in formula_edges if e.get("relation") == "CONTRADICTS_EXACT"]
            contra_groups = {e.get("independence_group") for e in contra}
            if len(contra_groups) < 2:
                fail(f"{fid}: CONTRADICTED_EXTERNAL_2PLUS requires >=2 independent contradiction paths")
            if vec.get("contradiction_strength") != "TWO_PLUS_INDEPENDENT":
                fail(f"{fid}: contradiction_strength must match state")

        if st == "TOKEN_VAZIO_EXACT_TEST":
            # CLASS_MATCH is informative context but cannot close an exact gate.
            if any(e.get("relation") == "SUPPORTS_EXACT" for e in formula_edges):
                fail(f"{fid}: TOKEN_VAZIO_EXACT_TEST cannot contain SUPPORTS_EXACT")
            gaps = state.get("token_vazio")
            if not isinstance(gaps, list) or not gaps:
                fail(f"{fid}: TOKEN_VAZIO_EXACT_TEST requires at least one explicit gap")

        for gap in state.get("token_vazio", []):
            for key in ("id", "cause", "evidence_needed", "falsifier", "F_next"):
                _require_nonempty(gap.get(key), f"{fid}.token_vazio.{key}")

    for gap in data.get("open_gaps", []):
        for key in ("id", "cause", "evidence_needed", "falsifier", "F_next"):
            _require_nonempty(gap.get(key), f"open_gap.{key}")

    rules = data.get("non_regression_rules")
    if not isinstance(rules, list) or not rules:
        fail("non_regression_rules must be explicit")
    rules_text = "\n".join(str(x) for x in rules).lower()
    if "reference count" not in rules_text and "bibliography" not in rules_text:
        fail("rules must explicitly reject bibliography/reference count as truth strength")


def assert_non_regression(old: dict[str, Any], new: dict[str, Any]) -> None:
    """Require immutable bibliography/evidence events to survive future snapshots."""
    validate_graph(old)
    validate_graph(new)
    if new.get("claim_allowed") is not False or new.get("publication_effect") != "NONE":
        fail("claim boundary regression")

    old_refs = {x["reference_id"]: x for x in old.get("references", [])}
    new_refs = {x["reference_id"]: x for x in new.get("references", [])}
    old_edges = {x["edge_id"]: x for x in old.get("edges", [])}
    new_edges = {x["edge_id"]: x for x in new.get("edges", [])}
    for rid, item in old_refs.items():
        if rid not in new_refs:
            fail(f"non-regression: reference removed: {rid}")
        if new_refs[rid] != item:
            fail(f"non-regression: historical reference mutated: {rid}")
    for eid, item in old_edges.items():
        if eid not in new_edges:
            fail(f"non-regression: evidence edge removed: {eid}")
        if new_edges[eid] != item:
            fail(f"non-regression: historical evidence edge mutated: {eid}")

    old_gap_ids = {g.get("id") for g in old.get("open_gaps", [])}
    new_gap_ids = {g.get("id") for g in new.get("open_gaps", [])}
    disappeared = old_gap_ids - new_gap_ids
    # A gap may be closed only through an append-only closure receipt entry.
    closure_ids = {c.get("gap_id") for c in new.get("gap_closures", []) if isinstance(c, dict) and c.get("receipt")}
    unjustified = disappeared - closure_ids
    if unjustified:
        fail(f"non-regression: gaps disappeared without receipt: {sorted(unjustified)}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("graph", nargs="?", default="data/science/rll_formula_literature_edges.v1.json")
    parser.add_argument("--previous", help="optional previous graph snapshot for append-only non-regression check")
    args = parser.parse_args()
    data = json.loads(Path(args.graph).read_text(encoding="utf-8"))
    validate_graph(data)
    if args.previous:
        old = json.loads(Path(args.previous).read_text(encoding="utf-8"))
        assert_non_regression(old, data)
    print(f"PASS rll_formula_literature_edges_v1 references={len(data['references'])} edges={len(data['edges'])} formulas={len(data['formula_states'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
