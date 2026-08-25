#!/usr/bin/env python3
"""Fail-closed validator for the RLL formula↔literature evidence graph.

This validator deliberately does not compute a scalar truth score. It validates
provenance, source identity, independence, falsifiability, TOKEN_VAZIO
completeness, structured closure receipts and monotone history/coverage
semantics.
"""
from __future__ import annotations

import argparse
import json
import re
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
EXTERNAL_CONCORDANCE = {"SUPPORT", "MIXED", "CONTRADICT", "UNKNOWN", "NOT_APPLICABLE"}
CONTRADICTION_STRENGTH = {"NONE", "SINGLE_PATH", "TWO_PLUS_INDEPENDENT", "INTERNAL_MATH"}
REPRODUCIBILITY = {"NONE", "REFERENCE_ONLY", "MULTI_GROUP", "EXACT_RLL_PIPELINE"}
CLOSURE_KINDS = {"EVIDENCE_RECEIPT", "DETERMINISTIC_DEDUP"}
HEX64 = re.compile(r"^[0-9a-f]{64}$")
DEDUP_GAP_ID = "TOKEN_VAZIO_DEDUP_COUNT"


def fail(msg: str) -> None:
    raise ValueError(msg)


def _require_nonempty(value: Any, label: str) -> None:
    if not isinstance(value, str) or not value.strip():
        fail(f"{label}: expected non-empty string")


def _validate_closure_receipts(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    closures = data.get("gap_closures", [])
    if not isinstance(closures, list):
        fail("gap_closures must be an array when present")
    by_gap: dict[str, dict[str, Any]] = {}
    for index, closure in enumerate(closures):
        if not isinstance(closure, dict):
            fail(f"gap_closures[{index}] must be an object")
        gap_id = closure.get("gap_id")
        _require_nonempty(gap_id, f"gap_closures[{index}].gap_id")
        if gap_id in by_gap:
            fail(f"duplicate gap closure: {gap_id}")
        kind = closure.get("closure_kind")
        if kind not in CLOSURE_KINDS:
            fail(f"{gap_id}: invalid closure_kind {kind!r}")
        receipt = closure.get("receipt")
        if not isinstance(receipt, dict):
            fail(f"{gap_id}: closure receipt must be a structured object")
        if receipt.get("schema") != "rll.gap_closure_receipt.v1":
            fail(f"{gap_id}: invalid closure receipt schema")
        if receipt.get("gap_id") != gap_id:
            fail(f"{gap_id}: closure receipt gap_id mismatch")
        if receipt.get("immutable_event") is not True:
            fail(f"{gap_id}: closure receipt must be immutable_event=true")
        _require_nonempty(receipt.get("event_id"), f"{gap_id}.receipt.event_id")
        _require_nonempty(receipt.get("artifact_path"), f"{gap_id}.receipt.artifact_path")
        digest = receipt.get("artifact_sha256")
        if not isinstance(digest, str) or HEX64.fullmatch(digest) is None:
            fail(f"{gap_id}: closure receipt requires lowercase SHA-256")
        if kind == "DETERMINISTIC_DEDUP":
            total = receipt.get("deduplicated_total")
            if not isinstance(total, int) or isinstance(total, bool) or total < 0:
                fail(f"{gap_id}: deterministic dedup receipt requires non-negative integer deduplicated_total")
        by_gap[gap_id] = closure
    return by_gap


def _validate_evidence_vector(
    fid: str,
    state: dict[str, Any],
    formula_edges: list[dict[str, Any]],
    ref_by_id: dict[str, dict[str, Any]],
) -> None:
    vec = state.get("evidence_vector")
    if not isinstance(vec, dict):
        fail(f"{fid}: evidence_vector must be an object")
    for key in ("math_defined", "units_closed", "exact_prediction"):
        if not isinstance(vec.get(key), bool):
            fail(f"{fid}: evidence_vector.{key} must be boolean")
    for key in ("independent_groups", "false_positive_controls"):
        value = vec.get(key)
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            fail(f"{fid}: evidence_vector.{key} must be a non-negative integer")
    if vec.get("external_concordance") not in EXTERNAL_CONCORDANCE:
        fail(f"{fid}: invalid external_concordance")
    if vec.get("contradiction_strength") not in CONTRADICTION_STRENGTH:
        fail(f"{fid}: invalid contradiction_strength")
    if vec.get("reproducibility") not in REPRODUCIBILITY:
        fail(f"{fid}: invalid reproducibility")
    if vec.get("claim_boundary") != "claim_allowed=false":
        fail(f"{fid}: evidence vector cannot promote claim")

    edge_groups = {str(e["independence_group"]) for e in formula_edges}
    if vec["independent_groups"] != len(edge_groups):
        fail(
            f"{fid}: evidence_vector.independent_groups={vec['independent_groups']} "
            f"does not match edge-derived groups={len(edge_groups)}"
        )

    reference_ids = {str(e["reference_id"]) for e in formula_edges}
    max_controls = sum(len(ref_by_id[rid]["false_positive_controls"]) for rid in reference_ids)
    controlled_groups = {
        str(e["independence_group"])
        for e in formula_edges
        if ref_by_id[str(e["reference_id"])]["false_positive_controls"]
    }
    min_controls = len(controlled_groups)
    declared_controls = vec["false_positive_controls"]
    if declared_controls < min_controls or declared_controls > max_controls:
        fail(
            f"{fid}: evidence_vector.false_positive_controls={declared_controls} "
            f"outside evidence-derived bounds [{min_controls}, {max_controls}]"
        )

    supports = any(e.get("relation") == "SUPPORTS_EXACT" for e in formula_edges)
    contradicts = any(e.get("relation") == "CONTRADICTS_EXACT" for e in formula_edges)
    if supports and contradicts:
        expected_concordance = "MIXED"
    elif supports:
        expected_concordance = "SUPPORT"
    elif contradicts:
        expected_concordance = "CONTRADICT"
    elif state.get("state") in {"MALFORMED", "REJECTED_NON_FALSIFIABLE"}:
        expected_concordance = "NOT_APPLICABLE"
    else:
        expected_concordance = "UNKNOWN"
    if vec["external_concordance"] != expected_concordance:
        fail(
            f"{fid}: external_concordance={vec['external_concordance']} "
            f"does not match edge/state-derived {expected_concordance}"
        )

    contradiction_groups = {
        str(e["independence_group"])
        for e in formula_edges
        if e.get("relation") == "CONTRADICTS_EXACT"
    }
    strength = vec["contradiction_strength"]
    if state.get("state") == "MALFORMED":
        if strength != "INTERNAL_MATH":
            fail(f"{fid}: MALFORMED requires contradiction_strength=INTERNAL_MATH")
    elif len(contradiction_groups) >= 2:
        if strength != "TWO_PLUS_INDEPENDENT":
            fail(f"{fid}: contradiction_strength must reflect >=2 independent contradiction groups")
    elif len(contradiction_groups) == 1:
        if strength != "SINGLE_PATH":
            fail(f"{fid}: contradiction_strength must reflect one contradiction group")
    elif strength != "NONE":
        fail(f"{fid}: contradiction_strength must be NONE without contradiction edges")


def validate_graph(data: dict[str, Any]) -> None:
    if data.get("schema") != "rll.formula_literature_edges.v1":
        fail("schema must be rll.formula_literature_edges.v1")
    if data.get("append_only") is not True:
        fail("append_only must be true")
    if data.get("claim_allowed") is not False:
        fail("claim_allowed must remain false")
    if data.get("publication_effect") != "NONE":
        fail("publication_effect must remain NONE")

    closures_by_gap = _validate_closure_receipts(data)

    inventory = data.get("source_inventory") or {}
    if inventory.get("extracted_formula_manifest") != 486:
        fail("source inventory must preserve the verified 486-formula manifest count")
    if inventory.get("desi_hypothesis_intake") != 50:
        fail("source inventory must preserve the 50-hypothesis DESI intake count")
    if inventory.get("raw_union_upper_bound_before_dedup") != 536:
        fail("536 is a raw upper bound before dedup, not a unique formula count")
    dedup = inventory.get("deduplicated_total")
    if isinstance(dedup, str) and dedup.startswith("TOKEN_VAZIO"):
        pass
    elif isinstance(dedup, int) and not isinstance(dedup, bool) and dedup >= 0:
        closure = closures_by_gap.get(DEDUP_GAP_ID)
        if not closure or closure.get("closure_kind") != "DETERMINISTIC_DEDUP":
            fail("deduplicated_total requires a structured DETERMINISTIC_DEDUP closure receipt")
        if closure["receipt"].get("deduplicated_total") != dedup:
            fail("deduplicated_total does not match deterministic dedup receipt")
    else:
        fail("deduplicated_total must be TOKEN_VAZIO or a receipt-backed non-negative integer")

    references = data.get("references")
    edges = data.get("edges")
    states = data.get("formula_states")
    if not isinstance(references, list) or not isinstance(edges, list) or not isinstance(states, list):
        fail("references, edges and formula_states must be arrays")

    ref_by_id: dict[str, dict[str, Any]] = {}
    ref_by_persistent_id: dict[str, str] = {}
    for ref in references:
        if not isinstance(ref, dict):
            fail("reference entry must be an object")
        rid = ref.get("reference_id")
        _require_nonempty(rid, "reference_id")
        if rid in ref_by_id:
            fail(f"duplicate reference_id: {rid}")
        _require_nonempty(ref.get("independence_group"), f"{rid}.independence_group")
        persistent_id = ref.get("persistent_id")
        _require_nonempty(persistent_id, f"{rid}.persistent_id")
        if persistent_id in ref_by_persistent_id:
            fail(
                f"duplicate persistent_id: {persistent_id} aliases "
                f"{ref_by_persistent_id[persistent_id]} and {rid}"
            )
        ref_by_persistent_id[persistent_id] = rid
        _require_nonempty(ref.get("url"), f"{rid}.url")
        controls = ref.get("false_positive_controls")
        if not isinstance(controls, list) or not controls or not all(isinstance(x, str) and x.strip() for x in controls):
            fail(f"{rid}: false_positive_controls must be a non-empty list")
        ref_by_id[rid] = ref

    state_by_id: dict[str, dict[str, Any]] = {}
    for state in states:
        if not isinstance(state, dict):
            fail("formula_state entry must be an object")
        fid = state.get("formula_id")
        _require_nonempty(fid, "formula_state.formula_id")
        if fid in state_by_id:
            fail(f"duplicate formula_id in formula_states: {fid}")
        state_by_id[fid] = state

    edge_by_id: dict[str, dict[str, Any]] = {}
    edges_by_formula: dict[str, list[dict[str, Any]]] = {}
    for edge in edges:
        if not isinstance(edge, dict):
            fail("edge entry must be an object")
        eid = edge.get("edge_id")
        _require_nonempty(eid, "edge_id")
        if eid in edge_by_id:
            fail(f"duplicate edge_id: {eid}")
        fid = edge.get("formula_id")
        rid = edge.get("reference_id")
        _require_nonempty(fid, f"{eid}.formula_id")
        if fid not in state_by_id:
            fail(f"{eid}: formula_id {fid!r} has no formula_state")
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

    for fid, state in state_by_id.items():
        st = state.get("state")
        if st not in ALLOWED_STATES:
            fail(f"{fid}: invalid state {st!r}")
        _require_nonempty(state.get("expression"), f"{fid}.expression")
        _require_nonempty(state.get("interpretation"), f"{fid}.interpretation")
        _require_nonempty(state.get("falsifier"), f"{fid}.falsifier")
        _require_nonempty(state.get("next_test"), f"{fid}.next_test")

        formula_edges = edges_by_formula.get(fid, [])
        _validate_evidence_vector(fid, state, formula_edges, ref_by_id)
        vec = state["evidence_vector"]
        exact_edges = [e for e in formula_edges if e.get("relation") in {"SUPPORTS_EXACT", "CONTRADICTS_EXACT"}]
        groups = {e.get("independence_group") for e in exact_edges}

        if st == "PAIR_A":
            if len(groups) < 2:
                fail(f"{fid}: PAIR_A requires >=2 exact-evidence independence groups")
            for e in exact_edges:
                ref = ref_by_id[e["reference_id"]]
                if not ref.get("false_positive_controls"):
                    fail(f"{fid}: PAIR_A reference lacks false-positive controls")
        elif st == "PAIR_B":
            exact_refs = {e["reference_id"] for e in exact_edges}
            author_groups = {ref_by_id[rid].get("group") for rid in exact_refs}
            if len(exact_refs) < 2 or len(author_groups) < 2:
                fail(f"{fid}: PAIR_B requires >=2 exact-evidence references from distinct author groups")
        elif st == "CLASS_MATCH":
            if not any(e.get("relation") == "CLASS_MATCH" for e in formula_edges):
                fail(f"{fid}: CLASS_MATCH state requires at least one CLASS_MATCH edge")
        elif st == "CONTRADICTED_EXTERNAL_2PLUS":
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

        gaps = state.get("token_vazio", [])
        if not isinstance(gaps, list):
            fail(f"{fid}: token_vazio must be an array")
        seen_formula_gaps: set[str] = set()
        for gap in gaps:
            if not isinstance(gap, dict):
                fail(f"{fid}: token_vazio entry must be an object")
            for key in ("id", "cause", "evidence_needed", "falsifier", "F_next"):
                _require_nonempty(gap.get(key), f"{fid}.token_vazio.{key}")
            if gap["id"] in seen_formula_gaps:
                fail(f"{fid}: duplicate token_vazio id {gap['id']}")
            seen_formula_gaps.add(gap["id"])

    open_gaps = data.get("open_gaps", [])
    if not isinstance(open_gaps, list):
        fail("open_gaps must be an array")
    seen_open_gaps: set[str] = set()
    for gap in open_gaps:
        if not isinstance(gap, dict):
            fail("open_gap entry must be an object")
        for key in ("id", "cause", "evidence_needed", "falsifier", "F_next"):
            _require_nonempty(gap.get(key), f"open_gap.{key}")
        if gap["id"] in seen_open_gaps:
            fail(f"duplicate open gap id: {gap['id']}")
        seen_open_gaps.add(gap["id"])

    rules = data.get("non_regression_rules")
    if not isinstance(rules, list) or not rules:
        fail("non_regression_rules must be explicit")
    rules_text = "\n".join(str(x) for x in rules).lower()
    if "reference count" not in rules_text and "bibliography" not in rules_text:
        fail("rules must explicitly reject bibliography/reference count as truth strength")


def assert_non_regression(old: dict[str, Any], new: dict[str, Any]) -> None:
    """Require immutable bibliography/evidence/formula events to survive snapshots."""
    validate_graph(old)
    validate_graph(new)
    if new.get("claim_allowed") is not False or new.get("publication_effect") != "NONE":
        fail("claim boundary regression")

    old_refs = {x["reference_id"]: x for x in old.get("references", [])}
    new_refs = {x["reference_id"]: x for x in new.get("references", [])}
    old_edges = {x["edge_id"]: x for x in old.get("edges", [])}
    new_edges = {x["edge_id"]: x for x in new.get("edges", [])}
    old_states = {x["formula_id"]: x for x in old.get("formula_states", [])}
    new_states = {x["formula_id"]: x for x in new.get("formula_states", [])}

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
    for fid, item in old_states.items():
        if fid not in new_states:
            fail(f"non-regression: formula state removed: {fid}")
        if new_states[fid] != item:
            fail(f"non-regression: historical formula state mutated: {fid}; create a successor/version ID")

    old_gap_ids = {g.get("id") for g in old.get("open_gaps", [])}
    new_gap_ids = {g.get("id") for g in new.get("open_gaps", [])}
    disappeared = old_gap_ids - new_gap_ids
    closure_ids = set(_validate_closure_receipts(new))
    unjustified = disappeared - closure_ids
    if unjustified:
        fail(f"non-regression: gaps disappeared without structured receipt: {sorted(unjustified)}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("graph", nargs="?", default="data/science/rll_formula_literature_edges.v1.json")
    parser.add_argument("--previous", help="previous graph snapshot for append-only non-regression check")
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
