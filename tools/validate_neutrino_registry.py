#!/usr/bin/env python3
"""Fail-closed, stdlib-only metadata gate. NOT an astrophysical analysis."""
import argparse
import copy
import hashlib
import json
from pathlib import Path

REQUIRED = {"ICETRACKS_DR2_2026", "KM3_230213A_2025",
            "PLANCK18_PARAMS", "DESI_DR2_2026", "DES_Y6_2026"}
DOMAINS = {"astrophysical_source_search", "astrophysical_single_event",
           "cosmological_neutrino_constraints", "cosmological_expansion"}

def inspect(obj):
    problems = []
    if obj.get("schema_version") != "rll-neutrino-evidence-v1":
        problems.append("schema_version")
    for key in ("claim_allowed", "joint_likelihood_executed",
                "independent_replication", "cross_dataset_event_merge_authorized"):
        if obj.get(key) is not False:
            problems.append("unsafe_true_or_missing:" + key)
    if obj.get("astrophysical_to_cosmological_bridge") != "TOKEN_VAZIO_UNMODELLED":
        problems.append("unproven_scale_bridge")
    src = obj.get("sources")
    if not isinstance(src, list):
        return problems + ["missing_sources"]
    ids = []
    for row in src:
        if not isinstance(row, dict):
            problems.append("invalid_source")
            continue
        ident = row.get("id", "?")
        ids.append(ident)
        if row.get("domain") not in DOMAINS:
            problems.append(ident + ":invalid_domain")
        if row.get("materialization") != "METADATA_ONLY":
            problems.append(ident + ":raw_data_not_audited")
        if row.get("raw_sha256") is not None:
            problems.append(ident + ":raw_hash_claim_without_materialization")
        if row.get("analysis_status") != "NOT_RUN":
            problems.append(ident + ":unverified_execution")
        if not str(row.get("url", "")).startswith("https://"):
            problems.append(ident + ":missing_https_provenance")
        if not row.get("caveat"):
            problems.append(ident + ":missing_caveat")
    if len(ids) != len(set(ids)):
        problems.append("duplicate_source_ids")
    if set(ids) != REQUIRED:
        problems.append("required_source_set_mismatch")
    return problems

def self_test(obj):
    assert not inspect(obj), inspect(obj)
    for key, value in [
        ("claim_allowed", True),
        ("joint_likelihood_executed", True),
        ("cross_dataset_event_merge_authorized", True),
        ("astrophysical_to_cosmological_bridge", "VALIDATED")]:
        broken = copy.deepcopy(obj)
        broken[key] = value
        assert inspect(broken), "negative gate failed: " + key
    broken = copy.deepcopy(obj)
    broken["sources"].append(copy.deepcopy(broken["sources"][0]))
    assert inspect(broken), "duplicate accepted"
    broken = copy.deepcopy(obj)
    broken["sources"][0]["materialization"] = "DOWNLOADED"
    assert inspect(broken), "unsupported raw data accepted"
    return 6

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--manifest", default="data/governance/NEUTRINO_OBSERVATIONAL_EVIDENCE_20261028.json")
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args()
    raw = Path(args.manifest).read_bytes()
    obj = json.loads(raw)
    problems = inspect(obj)
    count = 0
    if args.self_test and not problems:
        count = self_test(obj)
    receipt = {
        "status": "PASS_SCOPED_METADATA_ONLY" if not problems else "HOLD_INVALID_METADATA",
        "manifest_sha256": hashlib.sha256(raw).hexdigest(),
        "sources_checked": len(obj.get("sources", [])),
        "negative_tests": count,
        "problems": problems,
        "raw_data_validated": False,
        "joint_fit_validated": False,
        "claim_allowed": False,
    }
    print(json.dumps(receipt, sort_keys=True))
    return 0 if not problems else 2

if __name__ == "__main__":
    raise SystemExit(main())
