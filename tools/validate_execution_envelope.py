#!/usr/bin/env python3
"""Fail-closed validator for RLL development execution envelopes.

Python standard library only. It does not execute the requested action.
"""

from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
POLICY=ROOT/"data/governance/RLL_DEVELOPMENT_SAFETY_AUTHORITY_POLICY_V1.json"
REQUIRED=("actor","purpose","authority_level","data_classes","inputs","outputs","network_mode","write_scope","secrets_required","retention","audit_receipt","rollback","expiry")

def main(path):
    policy=json.loads(POLICY.read_text(encoding="utf-8"))
    env=json.loads(Path(path).read_text(encoding="utf-8"))
    reasons=[]
    missing=[k for k in REQUIRED if k not in env or env[k] in (None,"","TOKEN_VAZIO")]
    if missing:
        reasons.append("missing_required:"+",".join(missing))
    level=str(env.get("authority_level",""))
    levels={x["id"]:x for x in policy["authority_levels"]}
    if level not in levels:
        reasons.append("unknown_authority_level")
    data=set(env.get("data_classes",[]) or [])
    if not data:
        reasons.append("missing_data_class")
    if data & {"D3","D4"}:
        reasons.append("personal_or_sensitive_data_requires_review")
    if env.get("secrets_required") not in ([],False,None):
        reasons.append("secrets_require_review")
    if level in {"A3","A4","A5"}:
        reasons.append("human_authorization_required")
    if level=="A5":
        reasons.append("destructive_or_irreversible_default_deny")
    network=str(env.get("network_mode","")).lower()
    if network not in {"off","read_only","write"}:
        reasons.append("invalid_network_mode")
    if network=="write" and level not in {"A3","A4","A5"}:
        reasons.append("network_write_exceeds_authority")
    decision="ALLOW"
    if any("default_deny" in x or "missing_required" in x or "unknown_authority" in x or "exceeds_authority" in x for x in reasons):
        decision="DENY"
    elif reasons:
        decision="REVIEW"
    out={"schema":"rll.execution_envelope_decision.v1","decision":decision,"reasons":reasons,"claim_allowed":False,"action_executed":False}
    print(json.dumps(out,ensure_ascii=False,indent=2))
    return 0 if decision=="ALLOW" else (2 if decision=="REVIEW" else 3)

if __name__=="__main__":
    if len(sys.argv)!=2:
        print("usage: python3 tools/validate_execution_envelope.py envelope.json",file=sys.stderr)
        raise SystemExit(64)
    raise SystemExit(main(sys.argv[1]))
