#!/usr/bin/env python3
"""Pure-stdlib fail-closed validator for RLL cross-scale *metadata*. No physical fit."""
import argparse
import copy
import hashlib
import json
from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / "data/governance/RLL_CROSS_SCALE_EVIDENCE_GRAPH_20261028.json"
GATED = {
    "E06": "REQUIRES_SPECIFIC_EXPERIMENT",
    "E07": "THEORETICAL_ONLY",
    "E08": "UNSUPPORTED",
    "E09": "MODEL_NOT_REFITTED",
    "E10": "BACKGROUND_ONLY",
    "E11": "UNSUPPORTED",
}
REQUIRED_BENCHMARKS = {
    "CIV_BAO_DV_RD_Z1P92",
    "CIV_BAO_DV_RD_Z1P47",
    "RB87_SPIN_ANGLE0",
    "LRG2_PREDICTIVE_PREPRINT",
}

def check(g):
    issues = []
    if g.get("schema") != "rll.cross_scale_evidence_graph.v1":
        issues.append("bad_schema")
    if g.get("claim_allowed") is not False or g.get("scientific_fit_performed") is not False:
        issues.append("unsafe_claim_or_unproven_fit")
    for key in ("sources", "nodes", "edges", "benchmarks"):
        if not isinstance(g.get(key), list):
            return issues + ["missing_or_bad_" + key]
    ids = {}
    for key in ("sources", "nodes", "edges", "benchmarks"):
        found = [x.get("id") for x in g[key] if isinstance(x, dict)]
        if len(found) != len(g[key]) or any(not x for x in found):
            issues.append("malformed_"+key)
        if len(set(found)) != len(found):
            issues.append("duplicate_"+key)
        ids[key] = set(found)
    for s in g["sources"]:
        if not isinstance(s, dict) or not str(s.get("url", "")).startswith("https://"):
            issues.append("untraced_source")
    for n in g["nodes"]:
        if not isinstance(n, dict) or not n.get("scale") or not n.get("quantities"):
            issues.append("untyped_node")
    for e in g["edges"]:
        if not isinstance(e, dict):
            issues.append("malformed_edge")
            continue
        if e.get("from") not in ids["nodes"] or e.get("to") not in ids["nodes"]:
            issues.append("missing_endpoint")
        if e.get("evidence") not in ids["sources"]:
            issues.append("missing_source")
        if not e.get("type") or not e.get("relation") or not e.get("gate"):
            issues.append("incomplete_edge_contract")
    for eid, state in GATED.items():
        rows = [e for e in g["edges"] if isinstance(e, dict) and e.get("id") == eid]
        if len(rows) != 1 or rows[0].get("status") != state:
            issues.append("unsafe_promotion_" + eid)
    if ids["benchmarks"] != REQUIRED_BENCHMARKS:
        issues.append("missing_benchmark")
    for b in g["benchmarks"]:
        if b.get("source") not in ids["sources"] or not b.get("scope"):
            issues.append("untraced_benchmark")
    bench = {b["id"]: b for b in g["benchmarks"] if isinstance(b, dict) and b.get("id")}
    for ident, v, sigma in (
        ("CIV_BAO_DV_RD_Z1P92", 30.3, 0.9),
        ("CIV_BAO_DV_RD_Z1P47", 24.6, 1.0),
    ):
        if bench.get(ident, {}).get("measured", {}).get("DV_over_rd") != v or bench.get(ident, {}).get("measured", {}).get("sigma") != sigma:
            issues.append("source_benchmark_drift_"+ident)
    b = bench.get("RB87_SPIN_ANGLE0", {}).get("measured", {})
    if b.get("isotope") != "87Rb" or b.get("d_um") != 9.66 or b.get("Jxy_over_h_MHz") != 0.236:
        issues.append("rydberg_benchmark_drift")
    c = str(g.get("constraints", {}).get("ionization", ""))
    if not ("C IV" in c and "6 protons" in c and "3 bound electrons" in c):
        issues.append("ionization_typing_missing")
    return issues

def negatives(base):
    tests = [
        lambda g: g.update(schema="other"),
        lambda g: g.update(claim_allowed=True),
        lambda g: g.update(scientific_fit_performed=True),
        lambda g: g["sources"].append(copy.deepcopy(g["sources"][0])),
        lambda g: g["edges"][0].update(to="unobserved_domain"),
        lambda g: g["edges"][0].update(evidence="unobserved_source"),
        lambda g: next(x for x in g["edges"] if x["id"] == "E08").update(status="ESTABLISHED"),
        lambda g: next(x for x in g["edges"] if x["id"] == "E10").update(status="ESTABLISHED"),
        lambda g: next(x for x in g["benchmarks"] if x["id"] == "CIV_BAO_DV_RD_Z1P92")["measured"].update(DV_over_rd=42.0),
        lambda g: next(x for x in g["benchmarks"] if x["id"] == "RB87_SPIN_ANGLE0")["measured"].update(isotope="88Rb"),
    ]
    for i, mutate in enumerate(tests, 1):
        g = copy.deepcopy(base)
        mutate(g)
        if not check(g):
            raise AssertionError("unsafe mutation accepted: "+str(i))
    return len(tests)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", type=Path, default=PATH)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    payload = args.file.read_bytes()
    g = json.loads(payload)
    errors = check(g)
    n = negatives(g) if args.self_test and not errors else 0
    print(json.dumps({
        "status":"PASS_SCOPED_METADATA_ONLY" if not errors else "HOLD_INVALID",
        "manifest_sha256":hashlib.sha256(payload).hexdigest(),
        "nodes":len(g.get("nodes",[])),
        "edges":len(g.get("edges",[])),
        "negative_tests":n,
        "errors":errors,
        "data_fit_executed":False,
        "claim_allowed":False,
    },sort_keys=True))
    return 2 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
