#!/usr/bin/env python3
"""Fail-closed validator for supplemental Drive formula graph reconstruction batch 1."""

from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "data/provenance/drive_formula_index_20260808.json"
PATCH = ROOT / "data/provenance/drive_formula_graph_patch_20260808_batch1.jsonl"

EXPECTED_NODES = 18
EXPECTED_EDGES = 36
EXPECTED_ORIGINAL_GAP = 122
EXPECTED_REMAINING_GAP = 104
EXPECTED_SOURCE = "source:cb2c4adc80d9cf2525c32f2ce6df84a4baceaa43a47ce587fdcd057ad1b44243"

def load_jsonl(path: Path):
    rows = []
    with path.open("r", encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise AssertionError(f"{path}:{lineno}: invalid JSON: {exc}") from exc
    return rows

def validate() -> dict:
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    rows = load_jsonl(PATCH)
    nodes = [r for r in rows if r.get("record") == "node"]
    edges = [r for r in rows if r.get("record") == "edge"]

    assert index["claim_allowed"] is False
    assert index["counts"]["graph_missing_formula_nodes"] == EXPECTED_ORIGINAL_GAP
    missing = set(index["missing_graph_formula_hashes"])

    assert len(nodes) == EXPECTED_NODES
    assert len(edges) == EXPECTED_EDGES
    assert len({n["id"] for n in nodes}) == EXPECTED_NODES

    node_ids = set()
    for n in nodes:
        assert n["type"] == "FORMULA"
        assert n["claim_allowed"] is False
        assert n["tag"] == "[H]"
        assert n["epistemic_state"] == "SOURCE_OBSERVED"
        assert n["reconstruction"] == "SHA256_EXACT_LITERAL_MATCH"
        assert n["original_graph_state"] == "MISSING_NODE"
        assert n["mathematical_validity"] == "NOT_INFERRED_FROM_HASH"
        assert n["source_id"] == EXPECTED_SOURCE
        h = hashlib.sha256(n["formula_text"].encode("utf-8")).hexdigest()
        assert h == n["formula_sha256"]
        assert n["id"] == f"formula:{h}"
        assert h in missing
        node_ids.add(n["id"])

    from_edges = [e for e in edges if e.get("relation") == "FROM_SOURCE"]
    has_edges = [e for e in edges if e.get("relation") == "HAS_FORMULA"]
    assert len(from_edges) == EXPECTED_NODES
    assert len(has_edges) == EXPECTED_NODES

    assert {e["source"] for e in from_edges} == node_ids
    assert {e["target"] for e in from_edges} == {EXPECTED_SOURCE}
    assert {e["source"] for e in has_edges} == {EXPECTED_SOURCE}
    assert {e["target"] for e in has_edges} == node_ids

    reconstructed = {n["formula_sha256"] for n in nodes}
    remaining = missing - reconstructed
    assert len(remaining) == EXPECTED_REMAINING_GAP

    return {
        "status": "PASS",
        "claim_allowed": False,
        "original_gap": len(missing),
        "reconstructed_exact_literal": len(reconstructed),
        "remaining_gap": len(remaining),
        "source": EXPECTED_SOURCE,
    }

if __name__ == "__main__":
    print(json.dumps(validate(), ensure_ascii=False, sort_keys=True))
