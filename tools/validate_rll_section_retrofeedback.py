#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "data/contracts/rll_section_retrofeedback_operator.v1.json"
ATLAS = ROOT / "data/governance/RLL_SECTION_DELTA_ATLAS_20260926_V1.json"

def load(path: Path) -> dict[str, Any]:
    value=json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value,dict): raise ValueError(f"{path}: JSON object required")
    return value

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def validate(contract: dict[str,Any], atlas: dict[str,Any]) -> list[str]:
    e=[]
    if contract.get("schema")!="rll.section_retrofeedback_operator.v1": e.append("contract schema mismatch")
    if atlas.get("schema")!="rll.section_delta_atlas.v1": e.append("atlas schema mismatch")
    if contract.get("claim_allowed") is not False or atlas.get("claim_allowed") is not False: e.append("claim_allowed must remain false")
    if atlas.get("append_only") is not True: e.append("atlas must be append_only")
    symbols=[x.get("id") for x in contract.get("symbols",[]) if isinstance(x,dict)]
    expected=["§E","§Δ","§I","§T","§L","§F","§G","§R","§P","§C","§A","§Q","§H","§S","§V","§X","§M","§U","§B","§N","§K","§O","§D","§μ","§Ω","§∞"]
    if symbols!=expected: e.append("canonical § symbol vocabulary/order mismatch")
    required=contract.get("event_required_fields",[])
    allowed_out=set(contract.get("outcomes",[]))
    directions=set(contract.get("uncertainty_directions",[]))
    ids=set()
    for i,event in enumerate(atlas.get("events",[]),1):
        if not isinstance(event,dict): e.append(f"event[{i}] must be object"); continue
        eid=event.get("§ID")
        if not isinstance(eid,str) or not eid: e.append(f"event[{i}] §ID required")
        elif eid in ids: e.append(f"duplicate event id {eid}")
        else: ids.add(eid)
        for field in required:
            if field not in event: e.append(f"{eid or i}: missing {field}")
        result=event.get("§RESULTADO",{})
        outcome=result.get("outcome")
        if outcome not in allowed_out: e.append(f"{eid}: invalid outcome")
        if result.get("claim_allowed") is not False: e.append(f"{eid}: claim_allowed must remain false")
        after=event.get("§INCERTEZA_DEPOIS",{})
        direction=after.get("direction")
        if direction not in directions: e.append(f"{eid}: invalid uncertainty direction")
        evidence=after.get("evidence",[])
        reduced=direction=="REDUCED"
        if reduced and not evidence: e.append(f"{eid}: reduced uncertainty requires evidence")
        epistemic=result.get("epistemic_evolution") is True
        negative=outcome in {"FAIL","BLOCKED","ERROR","TOKEN_VAZIO"}
        if negative and epistemic:
            if not reduced: e.append(f"{eid}: negative outcome can be epistemic evolution only with reduced uncertainty")
            if result.get("negative_evidence_preserved") is not True: e.append(f"{eid}: negative evidence must be preserved")
            if result.get("promotion_authorized") is not False: e.append(f"{eid}: negative outcome cannot authorize promotion")
            if not event.get("§F_NEXT"): e.append(f"{eid}: negative evolution requires F_NEXT")
        token=event.get("§TOKEN_VAZIO")
        receipt=event.get("§RECEIPT",{})
        gate=event.get("§GATE",{})
        if receipt.get("state")=="TOKEN_VAZIO" and not token: e.append(f"{eid}: missing-evidence receipt requires TOKEN_VAZIO")
        if gate.get("state")!="PASS" and result.get("promotion_authorized") is True: e.append(f"{eid}: promotion requires gate PASS")
        if result.get("promotion_authorized") is True:
            if not event.get("§PROVENIÊNCIA"): e.append(f"{eid}: promotion requires provenance")
            if receipt.get("state") in {None,"TOKEN_VAZIO"}: e.append(f"{eid}: promotion requires nonempty receipt")
            if event.get("§ROLLBACK",{}).get("ready") is not True: e.append(f"{eid}: promotion requires rollback")
            if event.get("§H",{}).get("human_rights_regression") is not False: e.append(f"{eid}: promotion forbids human-rights regression")
            if event.get("§A",{}).get("auditability_regression") is not False: e.append(f"{eid}: promotion forbids auditability regression")
        if not isinstance(event.get("§BOUNDARY"),str) or not event["§BOUNDARY"]: e.append(f"{eid}: boundary required")
    return e

def receipt(contract:dict[str,Any],atlas:dict[str,Any],errors:list[str])->dict[str,Any]:
    events=atlas.get("events",[])
    return {
      "schema":"rll.section_retrofeedback.receipt.v1",
      "valid":not errors,
      "claim_allowed":False,
      "contract_sha256":sha256(CONTRACT),
      "atlas_sha256":sha256(ATLAS),
      "event_count":len(events),
      "epistemic_evolution_count":sum(1 for x in events if x.get("§RESULTADO",{}).get("epistemic_evolution") is True),
      "negative_evidence_event_count":sum(1 for x in events if x.get("§RESULTADO",{}).get("outcome") in {"FAIL","BLOCKED","ERROR","TOKEN_VAZIO"}),
      "authorized_promotion_count":sum(1 for x in events if x.get("§RESULTADO",{}).get("promotion_authorized") is True),
      "token_vazio_count":sum(len(x.get("§TOKEN_VAZIO",[])) for x in events if isinstance(x.get("§TOKEN_VAZIO"),list)),
      "errors":errors,
      "boundary":"Valid means the § governance/state-transition contract is internally coherent. It is not scientific, legal, ethical, security or Six-Sigma certification."
    }

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--contract",type=Path,default=CONTRACT)
    ap.add_argument("--atlas",type=Path,default=ATLAS)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    c=load(args.contract); a=load(args.atlas); errors=validate(c,a); r=receipt(c,a,errors)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(r,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(r,ensure_ascii=False,sort_keys=True))
    return 0 if r["valid"] else 2

if __name__=="__main__": raise SystemExit(main())
