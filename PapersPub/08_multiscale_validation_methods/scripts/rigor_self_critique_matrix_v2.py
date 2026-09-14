#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path

TV="TOKEN_VAZIO"; NA="NOT_APPLICABLE_WITH_REASON"
CANONICAL=["RAW_ORAL","RAW_NOTE","METAFORA","PARABOLA_DIDATICA","HIPOTESE","REF_REQUIRED","TOKEN_VAZIO","SOURCE_LINKED","METHOD_DEFINED","EVIDENCE_LINKED","RESULT_REPRODUCED","PEER_OR_REVIEW_READY","CLAIM_ALLOWED","CLAIM_BLOCKED"]

def load(p): return json.loads(Path(p).read_text(encoding="utf-8"))
def numeric(v): return isinstance(v,int) and not isinstance(v,bool) and 0<=v<=4
def is_na(v): return isinstance(v,dict) and v.get("state")==NA and bool(str(v.get("reason","")).strip())
def canonical_json(o): return json.dumps(o,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def sha256_obj(o): return hashlib.sha256(canonical_json(o).encode()).hexdigest()

def blank_assessment(program,method,request=None):
    dims=[d["id"] for d in method["dimensions"]]
    target=set((request or {}).get("target_unit_ids") or [u["id"] for u in program["research_units"]])
    return {"schema":"raf.rll.rigor_assessment.v2","request_id":(request or {}).get("request_id",TV),
      "preset_id":(request or {}).get("preset_id",method["default_preset"]),
      "research_units":{u["id"]:{
        "title":u["title"],"type":u["type"],"formal_statement":TV,"epistemic_class":TV,
        "claim_state":"HIPOTESE" if u["type"]=="MATHEMATICAL_HYPOTHESIS" else TV,
        "claim_goal":(request or {}).get("claim_goal",TV),"scores_by_dimension":{d:TV for d in dims},
        "supporting_evidence":[],"counterevidence":[],"falsifier":TV,"prior_art_state":TV,"proof_status":TV,
        "nibiguiri_findings":[],"dependencies":[],
        "assessment_basis":{"claim_hash":TV,"method_hash":TV,"evidence_snapshot_hash":TV,"source_commit":TV},
        "current_basis":{"claim_hash":TV,"method_hash":TV,"evidence_snapshot_hash":TV,"source_commit":TV},
        "promotion_decision":"BLOCKED","F_ok":[],"F_gap":["RIGOR_12_UNASSESSED"],
        "F_next":["BIND_FORMAL_STATEMENT_AND_EVIDENCE"],"provenance":[]
      } for u in program["research_units"] if u["id"] in target}}

def _basis(rec):
    a=rec.get("assessment_basis") or {}; c=rec.get("current_basis") or {}
    ks=("claim_hash","method_hash","evidence_snapshot_hash","source_commit")
    if any(a.get(k,TV)==TV or c.get(k,TV)==TV for k in ks): return "TOKEN_VAZIO_BASIS"
    return "CURRENT" if all(a.get(k)==c.get(k) for k in ks) else "STALE_REVIEW_REQUIRED"

def _eids(rec):
    return [e["evidence_id"] for e in rec.get("supporting_evidence",[])+rec.get("counterevidence",[])
            if isinstance(e,dict) and e.get("evidence_id")]

def _independent(rec):
    return any(isinstance(e,dict) and e.get("reviewer_relation") in ("INDEPENDENT","EXTERNAL")
               for e in rec.get("supporting_evidence",[]))

def _critical(rec):
    return any(isinstance(e,dict) and e.get("severity")=="CRITICAL" and e.get("resolved") is not True
               for e in rec.get("counterevidence",[]))

def _components(rec,method,preset):
    w={d["id"]:float(d["weight"]) for d in method["dimensions"]}; vals=rec.get("scores_by_dimension",{})
    allow=set(preset.get("allow_na",[])); na=set(); known={}; unknown={}
    for d,wt in w.items():
        v=vals.get(d,TV)
        if is_na(v) and d in allow: na.add(d)
        elif numeric(v): known[d]=v
        else: unknown[d]=wt
    app=sum(w[d] for d in w if d not in na); kw=sum(w[d] for d in known)
    cov=kw/app if app else 1.0
    obs=sum(w[d]*known[d] for d in known)/(4*kw)*100 if kw else None
    low=sum(w[d]*known[d] for d in known)/(4*app)*100 if app else 100.0
    high=(sum(w[d]*known[d] for d in known)+4*sum(unknown.values()))/(4*app)*100 if app else 100.0
    return w,vals,cov,obs,low,high

def _classify(rec,method,preset,cov,obs,vals):
    hard={d["id"] for d in method["dimensions"] if d.get("hard_gate")}
    if cov<.50 or obs is None: return "R0_UNASSESSED"
    cls="R1_SPECULATIVE"
    if not(cov>=.60 and obs>=40): return cls
    cls="R2_FORMALIZED"
    if not(cov>=.70 and obs>=55 and all(numeric(vals.get(k)) and vals[k]>=3 for k in ("RG01","RG02","RG04"))): return cls
    cls="R3_TESTABLE"; req=["RG03","RG11"]
    if not(is_na(vals.get("RG05")) and "RG05" in set(preset.get("allow_na",[]))): req.append("RG05")
    if not(cov>=.80 and obs>=70 and all(numeric(vals.get(k)) and vals[k]>=2 for k in req)): return cls
    cls="R4_SUPPORTED"; mh=int(preset.get("min_hard_gate_score",3))
    if not(cov>=.90 and obs>=85 and all(numeric(vals.get(k)) and vals[k]>=mh for k in hard) and not _critical(rec)): return cls
    cls="R5_STRONG"
    if cov==1.0 and rec.get("proof_status")=="PROVEN" and rec.get("formal_statement",TV)!=TV and not _critical(rec) and all(numeric(vals.get(k)) and vals[k]==4 for k in hard):
        return "R6_EXACT_PROVEN"
    return cls

def compute_one(rec,method,assessment):
    pid=assessment.get("preset_id") or method["default_preset"]; preset=method["presets"][pid]
    hard={d["id"] for d in method["dimensions"] if d.get("hard_gate")}
    _,vals,cov,obs,low,high=_components(rec,method,preset); blockers=[]; mh=int(preset.get("min_hard_gate_score",3))
    for k in sorted(hard):
        v=vals.get(k,TV)
        if v==TV: blockers.append("HARD_GATE_TOKEN_VAZIO:"+k)
        elif is_na(v): blockers.append("HARD_GATE_NOT_APPLICABLE:"+k)
        elif not numeric(v): blockers.append("HARD_GATE_INVALID:"+k)
        elif v<mh: blockers.append(f"HARD_GATE_BELOW_MIN:{k}:{v}<{mh}")
    if _critical(rec): blockers.append("UNRESOLVED_CRITICAL_COUNTEREVIDENCE")
    if rec.get("falsifier",TV)==TV: blockers.append("FALSIFIER_TOKEN_VAZIO")
    if rec.get("formal_statement",TV)==TV: blockers.append("FORMAL_STATEMENT_TOKEN_VAZIO")
    goal=rec.get("claim_goal",TV)
    if goal==TV: blockers.append("CLAIM_GOAL_TOKEN_VAZIO")
    if goal=="NOVELTY" and rec.get("prior_art_state",TV)==TV: blockers.append("PRIOR_ART_TOKEN_VAZIO_FOR_NOVELTY")
    if preset.get("require_independent_review_for_claim_allowed") and not _independent(rec): blockers.append("INDEPENDENT_REVIEW_MISSING")
    ids=_eids(rec)
    if len(ids)!=len(set(ids)): blockers.append("DUPLICATE_EVIDENCE_ID")
    bs=_basis(rec)
    if bs!="CURRENT": blockers.append(bs)
    cls=_classify(rec,method,preset,cov,obs,vals)
    return {"coverage":round(cov,6),"observed_score":None if obs is None else round(obs,6),
      "lower_bound":round(low,6),"upper_bound":round(high,6),"rigor_class":cls,
      "hard_gate_status":"BLOCKED" if any(x.startswith("HARD_GATE_") for x in blockers) else "CLEAR",
      "basis_state":bs,"promotion_blockers":blockers,
      "promotion_decision":"BLOCKED" if blockers else "ELIGIBLE_FOR_REVIEW"}

def adversarial_prompts(uid,rec,method,full):
    lenses=full.get("lenses_96",[])
    if len(lenses)!=96: raise ValueError("full_method must expose 96 lenses")
    eids=_eids(rec); out=[]
    for d in method["dimensions"]:
        for lens in lenses:
            out.append({"unit_id":uid,"rigor_dimension":d["id"],"lens":lens,
              "current_score":rec.get("scores_by_dimension",{}).get(d["id"],TV),"evidence_ids":eids,
              "formal_statement":rec.get("formal_statement",TV),
              "prompt":f"{uid}/{d['id']}/{lens}: tente refutar, rebaixar ou restringir '{d['title']}' usando statement, evidência, contraevidência, dependências, escopo, peso e threshold."})
    return out

def validate_request(req,method,program):
    e=[]
    for k in method["request_contract"]["required"]:
        if not req.get(k): e.append("missing request field:"+k)
    if req.get("claim_goal") not in method["request_contract"]["claim_goals"]: e.append("invalid claim_goal")
    if req.get("preset_id") not in method["presets"]: e.append("invalid preset_id")
    valid={u["id"] for u in program["research_units"]}; bad=[x for x in req.get("target_unit_ids",[]) if x not in valid]
    if bad: e.append("unknown target ids:"+",".join(bad))
    return e

def validate(program,method,full,assessment):
    e=[]; units=program.get("research_units",[])
    if len(units)!=48: e.append(f"expected 48 units, got {len(units)}")
    if len(method.get("dimensions",[]))!=12: e.append("expected 12 rigor dimensions")
    if len(full.get("lenses_96",[]))!=96: e.append("expected 96 lenses")
    if method.get("autocritique",{}).get("full_tensor")!=55296: e.append("full tensor must be 55296")
    if method.get("canonical_claim_states")!=CANONICAL: e.append("claim states do not match canonical ledger")
    ids=[u["id"] for u in units]; dims=[d["id"] for d in method["dimensions"]]
    if len(ids)!=len(set(ids)): e.append("duplicate research unit ids")
    preset=method["presets"].get(assessment.get("preset_id") or method["default_preset"],{}); allow=set(preset.get("allow_na",[]))
    for uid,rec in assessment.get("research_units",{}).items():
        if uid not in ids: e.append("unknown assessment unit:"+uid); continue
        if rec.get("claim_state") not in CANONICAL: e.append(f"{uid}: illegal claim_state")
        vals=rec.get("scores_by_dimension",{})
        for d in dims:
            v=vals.get(d,TV)
            if not(v==TV or numeric(v) or is_na(v)): e.append(f"{uid}/{d}: invalid cell")
            if is_na(v) and d not in allow: e.append(f"{uid}/{d}: N/A not permitted by preset")
        x=_eids(rec)
        if len(x)!=len(set(x)): e.append(f"{uid}: duplicate evidence_id")
        if not rec.get("F_next"): e.append(f"{uid}: missing F_next")
    return e

def next_action_for_result(r):
    if r["promotion_decision"]=="ELIGIBLE_FOR_REVIEW": return "REQUEST_INDEPENDENT_REVIEW_AND_CLAIM_TRANSITION_DECISION"
    for p in ("STALE_REVIEW_REQUIRED","TOKEN_VAZIO_BASIS","FORMAL_STATEMENT_TOKEN_VAZIO","FALSIFIER_TOKEN_VAZIO","PRIOR_ART_TOKEN_VAZIO_FOR_NOVELTY","INDEPENDENT_REVIEW_MISSING"):
        if p in r["promotion_blockers"]: return "RESOLVE_"+p
    hb=[x for x in r["promotion_blockers"] if x.startswith("HARD_GATE_")]
    return "RESOLVE_"+hb[0].replace(":","_").replace("<","_LT_") if hb else "REVIEW_PROMOTION_BLOCKERS"

def main():
    ap=argparse.ArgumentParser()
    for x in ("program","method","full-method"): ap.add_argument("--"+x,required=True)
    for x in ("request","assessment","emit-blank","emit-report","emit-adversarial"): ap.add_argument("--"+x)
    a=ap.parse_args(); program=load(a.program); method=load(a.method); full=load(a.full_method); req=load(a.request) if a.request else None
    if req:
        er=validate_request(req,method,program)
        if er: print("\n".join("FAIL "+x for x in er),file=sys.stderr); return 2
    ass=load(a.assessment) if a.assessment else blank_assessment(program,method,req)
    er=validate(program,method,full,ass)
    if er: print("\n".join("FAIL "+x for x in er),file=sys.stderr); return 2
    if a.emit_blank: Path(a.emit_blank).write_text(json.dumps(ass,ensure_ascii=False,indent=2),encoding="utf-8")
    results={uid:compute_one(rec,method,ass) for uid,rec in ass["research_units"].items()}
    report={"schema":"raf.rll.rigor_report.v2","summary":{"research_units":len(results),"rigor_dimensions":12,"full_lenses":96,"adversarial_tensor_cells":len(results)*12*96},
      "results":{uid:{**r,"next_action":next_action_for_result(r)} for uid,r in results.items()}}
    if a.emit_report: Path(a.emit_report).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    if a.emit_adversarial:
        p=[]; [p.extend(adversarial_prompts(uid,rec,method,full)) for uid,rec in ass["research_units"].items()]
        Path(a.emit_adversarial).write_text(json.dumps(p,ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"PASS units={len(results)} rigor_dimensions=12 full_lenses=96 adversarial_cells={len(results)*12*96}")
    return 0
if __name__=="__main__": raise SystemExit(main())
