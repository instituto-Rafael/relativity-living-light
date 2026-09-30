#!/usr/bin/env python3
"""Validate/materialize the branch-maturity reconciliation decision packet."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from rx.kernel import dump_json, load_json

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "data/governance/RLL_BRANCH_MATURITY_RECONCILIATION_DECISION_V1.json"
OUT = ROOT / "results/rll_branch_maturity_decision_packet.json"


def build():
    payload = load_json(CONTRACT)
    if payload.get("schema") != "rll.branch_maturity_reconciliation_decision.v1":
        raise ValueError("unexpected branch maturity decision schema")
    if payload.get("claim_allowed") is not False:
        raise ValueError("claim boundary must remain false")
    selected = str(payload.get("selected_option", "TOKEN_VAZIO"))
    options = payload.get("options", [])
    ids = {row.get("id") for row in options}
    if len(ids) != len(options) or None in ids:
        raise ValueError("branch maturity options must have unique ids")
    terminal = not selected.startswith("TOKEN_VAZIO")
    if terminal and selected not in ids:
        raise ValueError("selected option is not declared")
    observed = payload.get("observed_against_main", {})
    destructive_risk = [
        ref for ref, row in observed.items()
        if int(row.get("ahead_by", 0)) > 0
    ]
    return {
        "schema": "rll.branch_maturity_decision_packet.v1",
        "state": "READY_FOR_GOVERNANCE_DECISION" if not terminal else "READY_FOR_VERSIONED_IMPLEMENTATION",
        "selected_option": selected,
        "options": options,
        "observed_against_main": observed,
        "branches_with_unique_commits": destructive_risk,
        "force_reset_allowed": False,
        "claim_allowed": False,
        "boundary": "This packet exposes governance alternatives and current divergence; it does not authorize branch history mutation."
    }


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    result = build()
    if args.write:
        dump_json(OUT, result)
    print(json.dumps({
        "state": result["state"],
        "selected_option": result["selected_option"],
        "branches_with_unique_commits": result["branches_with_unique_commits"],
        "claim_allowed": False,
    }, ensure_ascii=False, indent=2))
    if args.write:
        print("wrote", OUT.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
