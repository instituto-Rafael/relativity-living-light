#!/usr/bin/env python3
"""Fail-closed validator for the governed DESI 50-hypothesis intake."""
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/inputs/cosmology_joint/desi_50_hypothesis_intake.v1.csv"
META = ROOT / "data/contracts/desi_50_hypothesis_intake.v1.json"

VALID_STATES = {"H", "U", "A", "R"}
VALID_RELEVANCE = {"DIRECT_DESI", "INDIRECT_COSMOLOGY", "OUTSIDE_DESI_CORE"}
VALID_GATE = {"PASS", "FAIL", "TOKEN_VAZIO"}
GATES = ("D", "P", "O", "F", "E")
EXPECTED_IDS = {f"H{i:02d}" for i in range(1, 51)}
EXPECTED_STATE_COUNTS = {"H": 15, "U": 29, "A": 5, "R": 1}
EXPECTED_RELEVANCE_COUNTS = {"DIRECT_DESI": 17, "INDIRECT_COSMOLOGY": 21, "OUTSIDE_DESI_CORE": 12}


def load_rows(path: Path = DATA):
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def validate(rows=None, meta=None):
    rows = load_rows() if rows is None else rows
    meta = json.loads(META.read_text(encoding="utf-8")) if meta is None else meta
    errors = []

    if len(rows) != 50:
        errors.append(f"expected 50 hypotheses, got {len(rows)}")
    ids = [r.get("id", "") for r in rows]
    if set(ids) != EXPECTED_IDS or len(ids) != len(set(ids)):
        errors.append("IDs must be unique and exactly H01..H50")

    state_counts = Counter(r.get("state") for r in rows)
    if dict(state_counts) != EXPECTED_STATE_COUNTS:
        errors.append(f"state counts drifted: {dict(state_counts)}")
    relevance_counts = Counter(r.get("desi_relevance") for r in rows)
    if dict(relevance_counts) != EXPECTED_RELEVANCE_COUNTS:
        errors.append(f"DESI relevance counts drifted: {dict(relevance_counts)}")

    for r in rows:
        hid = r.get("id", "?")
        if r.get("state") not in VALID_STATES:
            errors.append(f"{hid}: invalid state")
        if r.get("desi_relevance") not in VALID_RELEVANCE:
            errors.append(f"{hid}: invalid DESI relevance")
        for g in GATES:
            if r.get(g) not in VALID_GATE:
                errors.append(f"{hid}: invalid {g} gate")
        if r.get("E") == "PASS":
            errors.append(f"{hid}: E may not be PASS without an evidence receipt in this intake")
        if r.get("state") in {"A", "R"} and all(r.get(g) == "PASS" for g in GATES):
            errors.append(f"{hid}: symbolic/rejected item cannot be fully promoted")
        if r.get("desi_relevance") == "DIRECT_DESI" and r.get("O") != "PASS":
            errors.append(f"{hid}: DIRECT_DESI requires an observable mapping")
        if not r.get("formula", "").strip() or not r.get("next_test", "").strip():
            errors.append(f"{hid}: formula and next_test are mandatory")

    by_id = {r["id"]: r for r in rows}
    if by_id.get("H15", {}).get("P") != "FAIL":
        errors.append("H15 must preserve the sigma8(z=0)=0 normalization defect")
    if by_id.get("H35", {}).get("P") != "FAIL":
        errors.append("H35 must preserve exp(pi i)=-1 power-spectrum defect")
    if by_id.get("H44", {}).get("D") != "FAIL":
        errors.append("H44 must preserve scalar-vs-matrix formal mismatch")
    if by_id.get("H50", {}).get("state") != "R" or by_id.get("H50", {}).get("F") != "FAIL":
        errors.append("H50 absolute-certainty clause must remain rejected/fail-closed")

    if meta.get("claim_allowed") is not False or meta.get("promotion_allowed") is not False:
        errors.append("manifest must remain fail-closed")
    if meta.get("source_count") != 50:
        errors.append("manifest source_count must be 50")
    if meta.get("governed_by") != "data/contracts/cross_domain_equation_intake.v1.json":
        errors.append("wrong governance authority")

    return errors


def main():
    errors = validate()
    if errors:
        print("DESI_50_HYPOTHESIS_INTAKE: FAIL")
        for err in errors:
            print(f"- {err}")
        raise SystemExit(1)
    print("DESI_50_HYPOTHESIS_INTAKE: PASS")
    print("count=50 claim_allowed=false promotion_allowed=false evidence_gate=TOKEN_VAZIO")


if __name__ == "__main__":
    main()
