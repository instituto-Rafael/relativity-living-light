#!/usr/bin/env python3
"""Fail-closed validator for the governed 24-formula RLL test matrix.

This registry is a test/diagnostic crosswalk. It does not alter canonical
RLL cosmology equations and cannot promote scientific claims.
"""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/inputs/cosmology_joint/rll_formula_test_matrix_24.v1.csv"

EXPECTED_IDS = {
    "005","006","007","022","023","024","025",
    "051","053","055","057","059","060","085",
    "061","063","067","069","070",
    "072","073","076","079","080",
}
EXPECTED_FAMILIES = {
    "SPIRAL_NORMALIZATION": 7,
    "SPECTRAL_STABILITY": 7,
    "SIGNAL_RESIDUAL_DIAGNOSTICS": 5,
    "STATISTICAL_INFERENCE": 5,
}
ALLOWED_GRAPH_PREFIX = "figs/"
TOKEN_VAZIO_GRAPH = "TOKEN_VAZIO_NO_CANONICAL_GRAPH"

def load_rows(path: Path = REGISTRY):
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))

def validate(path: Path = REGISTRY):
    errors = []
    rows = load_rows(path)
    ids = [r["source_id"] for r in rows]

    if len(rows) != 24:
        errors.append(f"expected 24 rows, got {len(rows)}")
    if len(set(ids)) != len(ids):
        errors.append("source_id values must be unique")
    if set(ids) != EXPECTED_IDS:
        errors.append(f"source_id set mismatch: {sorted(set(ids) ^ EXPECTED_IDS)}")

    families = Counter(r["family"] for r in rows)
    if dict(families) != EXPECTED_FAMILIES:
        errors.append(f"family distribution mismatch: {dict(families)}")

    required = {
        "source_id","family","name","source_formula","test_formula",
        "epistemic_state","test_role","hypothesis_links","graph_ref",
        "graph_role","claim_allowed","notes",
    }
    for i, row in enumerate(rows, start=2):
        missing = [k for k in required if not row.get(k)]
        if missing:
            errors.append(f"line {i}: empty required fields {missing}")
        if row.get("claim_allowed", "").lower() != "false":
            errors.append(f"line {i}: claim_allowed must remain false")
        hrefs = [x for x in row.get("hypothesis_links", "").split(";") if x]
        if any(not (h.startswith("H") and len(h) == 3 and h[1:].isdigit()) for h in hrefs):
            errors.append(f"line {i}: malformed hypothesis link")
        graph_ref = row.get("graph_ref", "")
        if graph_ref != TOKEN_VAZIO_GRAPH:
            for ref in [x for x in graph_ref.split(";") if x]:
                if not ref.startswith(ALLOWED_GRAPH_PREFIX):
                    errors.append(f"line {i}: graph ref outside figs/: {ref}")
                elif not (ROOT / ref).is_file():
                    errors.append(f"line {i}: graph ref does not exist: {ref}")

    by_id = {r["source_id"]: r for r in rows}
    if "Mtilde_n =" not in by_id["007"]["test_formula"]:
        errors.append("ID007 must use explicit L2 normalization operator")
    if "1/300" not in by_id["055"]["test_formula"]:
        errors.append("ID055 must use the corrected 300-node mean/second moment")
    if "rho(A) < 1" not in by_id["059"]["test_formula"]:
        errors.append("ID059 must encode strict discrete asymptotic stability")
    if "xdot=A x" not in by_id["060"]["test_formula"]:
        errors.append("ID060 must remain scoped to continuous-time dynamics")
    if "r^T C^{-1} r" not in by_id["079"]["test_formula"]:
        errors.append("ID079 must use covariance-aware residual chi-square for RLL")

    return errors

def main():
    errors = validate()
    if errors:
        for err in errors:
            print(f"FAIL: {err}")
        raise SystemExit(1)
    print("PASS: governed 24-formula RLL test matrix")
    print("claim_allowed=false")
    print("direct_model_integration=false")
    print("graph references verified or TOKEN_VAZIO")

if __name__ == "__main__":
    main()
