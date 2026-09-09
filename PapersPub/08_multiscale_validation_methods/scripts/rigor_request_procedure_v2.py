#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, importlib.util, json
from pathlib import Path

TV="TOKEN_VAZIO"
def load(p): return json.loads(Path(p).read_text(encoding="utf-8"))
def dump(p,o): Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding="utf-8")
def canon(o): return json.dumps(o,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def sha(o): return hashlib.sha256(canon(o).encode("utf-8")).hexdigest()

def load_engine(path):
    s=importlib.util.spec_from_file_location("rigor_engine",path); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m

def normalize_request(req,method,program):
    out=dict(req)
    if out.get("target_unit_ids") in (None,[],["ALL_48"],"ALL_48"):
        out["target_unit_ids"]=[u["id"] for u in program["research_units"]]
    out.setdefault("preset_id",method["default_preset"]); out.setdefault("claim_goal","TRUTH")
    out.setdefault("requested_by","TOKEN_VAZIO_REQUESTOR"); out.setdefault("created_at","TOKEN_VAZIO_DATE")
    out.setdefault("title","RLL RIGOR procedure request")
    out.setdefault("request_id","REQ-"+sha({"title":out["title"],"created_at":out["created_at"]})[:16])
    return out

def procedure_steps():
    return [
      ("P00","REQUEST_RECEIVED","validate required request fields"),
      ("P01","REQUEST_NORMALIZED","normalize target, preset and claim goal"),
      ("P02","SCOPE_BOUND","bind exact T/H target units"),
      ("P03","SOURCE_BOUND","bind source/origin and claim hashes"),
      ("P04","DEDUP_CHECKED","deduplicate hypothesis/evidence identities"),
      ("P05","FORMAL_STATEMENT_BOUND","bind mathematical statement/domain/assumptions"),
      ("P06","EVIDENCE_BOUND","bind evidence and counterevidence INFO_PRIME records"),
      ("P07","FALSIFIER_BOUND","bind counterexample/refutation protocol"),
      ("P08","RIGOR_ASSESSED","score RG01..RG12 with coverage and bounds"),
      ("P09","NIBIGUIRI_ASSESSED","run applicable 96-lens self-critique"),
      ("P10","DEPENDENCIES_PROPAGATED","propagate failed dependencies/staleness"),
      ("P11","GATES_EVALUATED","evaluate G0..G6 and claim-specific hard gates"),
      ("P12","REVIEW_REQUIRED","require independent/adversarial review when material"),
      ("P13","ELIGIBLE_FOR_CLAIM_TRANSITION","human/authority transition decision; never automatic"),
      ("P14","COMPLETED_RECEIPT","append-only receipt, hashes, event log and next action")]

def build_packet(req,method,program,full,engine):
    req=normalize_request(req,method,program); errs=engine.validate_request(req,method,program)
    if errs: raise ValueError("; ".join(errs))
    a=engine.blank_assessment(program,method,req)
    packet={"schema":"raf.rll.rigor_procedure_packet.v2","request":req,"preset":method["presets"][req["preset_id"]],
      "procedure":[{"id":i,"state":s,"action":x,"status":"DECLARED"} for i,s,x in procedure_steps()],
      "assessment":a,"coverage_architecture":{
        "units":len(a["research_units"]),"rigor_dimensions":12,"full_lenses":len(full["lenses_96"]),
        "adversarial_obligations":len(a["research_units"])*12*len(full["lenses_96"]),
        "ae_permutations_available":len(full.get("AE_permutations_120",[])),
        "relation_operators_available":len(full.get("relation_operators_12",[])),
        "semantic_slots_available":len(full.get("semantic_slots_34",[]))},
      "next_action":"BIND_FORMAL_STATEMENTS_SOURCES_EVIDENCE_AND_FALSIFIERS","claim_allowed":False}
    packet["request_hash"]=sha(req); packet["packet_hash"]=sha({k:v for k,v in packet.items() if k!="packet_hash"})
    return packet

def validate_no_missing_step(packet):
    e=[]; steps=packet.get("procedure",[])
    if [x.get("id") for x in steps] != [f"P{i:02d}" for i in range(15)]: e.append("procedure must be P00..P14")
    for s in steps:
        if not s.get("state") or not s.get("action") or not s.get("status"): e.append("step missing state/action/status:"+str(s.get("id")))
    if not packet.get("next_action"): e.append("packet missing next_action")
    if packet.get("claim_allowed") is not False: e.append("new packet must start fail-closed")
    return e

def main():
    ap=argparse.ArgumentParser()
    for x in ("request","method","program","full-method","engine","output"): ap.add_argument("--"+x,required=True)
    a=ap.parse_args(); req=load(a.request); method=load(a.method); program=load(a.program); full=load(a.full_method); engine=load_engine(a.engine)
    p=build_packet(req,method,program,full,engine); e=validate_no_missing_step(p)
    if e: raise SystemExit("FAIL "+"; ".join(e))
    dump(a.output,p); print("PASS procedure_steps=15 next_action_bound=true claim_allowed=false"); return 0
if __name__=="__main__": raise SystemExit(main())
