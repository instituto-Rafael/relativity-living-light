#!/usr/bin/env python3
"""Fail-closed state/evidence boundary for merged RLL audit PRs."""
import argparse
import hashlib
import json
from pathlib import Path

EXPECTED = {
    1172: ("dd7e749cf18c93ccd723bb50adf9655ef0d8bbbf", "dedb9888e7219f8edb676d3d962b0f71b3f6b44f4"),
    1173: ("01156d60ca61e777f3f7c454905a0c2f44dcf076", "42e700fe20b950884af9dfc06cea639a0b988dac"),
}
REQUIRED_GAPS = {
    "same_likelihood_reconciliation",
    "official_covariance_validation",
    "independent_reproduction",
    "full_cmb_tt_te_ee_lensing",
    "nonlinear_pk",
    "physical_model_validation",
}

def audit(path):
    path = Path(path)
    blob = path.read_bytes()
    data = json.loads(blob)
    if data.get("schema") != "rll.state_reconciliation.v1":
        raise ValueError("SCHEMA_MISMATCH")
    if data.get("claim_allowed") is not False or data.get("scientific_confirmation") is not False:
        raise ValueError("CLAIM_PROMOTION_BLOCKED")
    rows = data.get("pull_requests")
    if not isinstance(rows, list) or {r.get("number") for r in rows} != set(EXPECTED):
        raise ValueError("PR_SET_MISMATCH")
    for row in rows:
        number = row["number"]
        head, merge = EXPECTED[number]
        if row.get("state") != "MERGED":
            raise ValueError(f"PR_{number}_STATE_MISMATCH")
        if row.get("head_sha") != head or row.get("merge_commit_sha") != merge:
            raise ValueError(f"PR_{number}_SHA_MISMATCH")
        if row.get("source_ref") != f"https://api.github.com/repos/instituto-Rafael/relativity-living-light/pulls/{number}":
            raise ValueError(f"PR_{number}_SOURCE_MISMATCH")
    gates = data.get("scientific_gates")
    if not isinstance(gates, dict) or set(gates) != REQUIRED_GAPS:
        raise ValueError("SCIENTIFIC_GATE_SET_MISMATCH")
    if any(value not in {"TOKEN_VAZIO", "NOT_RUN"} for value in gates.values()):
        raise ValueError("UNSUPPORTED_GATE_PROMOTION")
    return {
        "status": "PASS_SCOPED_STATE_RECONCILIATION",
        "claim_allowed": False,
        "scientific_confirmation": False,
        "source_sha256": hashlib.sha256(blob).hexdigest(),
        "merged_prs": sorted(EXPECTED),
        "open_scientific_gates": sorted(gates),
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/governance/rll_state_reconciliation_20261115.v1.json")
    parser.add_argument("--output")
    args = parser.parse_args()
    report = audit(args.input)
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, sort_keys=True))

if __name__ == "__main__":
    main()
