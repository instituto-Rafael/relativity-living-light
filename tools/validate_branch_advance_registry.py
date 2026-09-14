#!/usr/bin/env python3
"""Validate the branch advance registry without claiming unscanned refs are resolved."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ALLOWED = {
    "ABSORBED_AHEAD_ZERO", "MERGED_HISTORY_FALSE_AHEAD", "DOCS_ONLY_AHEAD",
    "STACKED_NOT_MAIN_FORWARD_PORTED", "MATURITY_STRANDED_FORWARD_PORTED",
    "MATURITY_STRANDED_SOURCE", "MATURITY_GAP_RELEASE_NOT_PROMOTED",
}


def validate(payload: dict) -> list[str]:
    errors: list[str] = []
    if payload.get("schema") != "rll.branch_advance_registry.v2": errors.append("SCHEMA")
    if payload.get("claim_allowed") is not False: errors.append("CLAIM_BOUNDARY")
    entries = payload.get("entries")
    if not isinstance(entries, list) or len(entries) < 40: errors.append("INSUFFICIENT_AUDITED_REFS"); return errors
    seen=set()
    for i,e in enumerate(entries):
        p=f"entry[{i}]"
        if not isinstance(e,dict): errors.append(p+":TYPE"); continue
        b=e.get("branch"); a=e.get("ahead"); d=e.get("behind"); c=e.get("class")
        if not isinstance(b,str) or not b: errors.append(p+":BRANCH")
        elif b in seen: errors.append(p+":DUPLICATE")
        else: seen.add(b)
        if not isinstance(a,int) or a<0 or not isinstance(d,int) or d<0: errors.append(p+":COUNTS")
        if c not in ALLOWED: errors.append(p+":CLASS")
        if not str(e.get("f_next","")).strip(): errors.append(p+":F_NEXT")
        if c=="ABSORBED_AHEAD_ZERO" and a!=0: errors.append(p+":ABSORBED_NONZERO")
        if c=="MERGED_HISTORY_FALSE_AHEAD" and (a<=0 or not e.get("source_pr") or e.get("merge_target")!="main"): errors.append(p+":FALSE_AHEAD_EVIDENCE")
        if c=="STACKED_NOT_MAIN_FORWARD_PORTED" and (a<=0 or not e.get("forward_port_scope")): errors.append(p+":STACKED_SCOPE")
        if c.startswith("MATURITY_STRANDED") and a<=0: errors.append(p+":MATURITY_AHEAD")
    if not str(payload.get("unclassified_remainder","")).startswith("TOKEN_VAZIO_"): errors.append("UNCLASSIFIED_REMAINDER_BOUNDARY")
    return errors


def main() -> int:
    p=argparse.ArgumentParser(); p.add_argument("path", nargs="?", default="data/governance/branch_advance_registry.v2.json"); args=p.parse_args()
    payload=json.loads(Path(args.path).read_text(encoding="utf-8")); errors=validate(payload)
    out={"schema":"rll.branch_advance_registry.validation.v1","entries":len(payload.get("entries",[])),"decision":"PASS" if not errors else "FAIL","errors":errors,"claim_allowed":False}
    print(json.dumps(out,indent=2)); return 0 if not errors else 1


if __name__=="__main__": sys.exit(main())
