#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

TV="TOKEN_VAZIO"

def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def numeric(v):
    return isinstance(v,int) and not isinstance(v,bool) and 0 <= v <= 4

def blank_assessment(program, method):
    dims=[d["id"] for d in method["dimensions"]]
    return {
      "schema":"raf.rll.rigor_assessment.v1",
      "research_units":{
        u["id"]:{
          "title":u["title"],"type":u["type"],
          "epistemic_class":TV,
          "claim_state":"HYPOTHESIS" if u["type"]=="MATHEMATICAL_HYPOTHESIS" else TV,
          "scores_by_dimension":{d:TV for d in dims},
          "supporting_evidence":[],"counterevidence":[],
          "falsifier":TV,"prior_art_state":TV,"nibiguiri_findings":[],
          "promotion_decision":"BLOCKED",
          "F_ok":[],
          "F_gap":["RIGOR_12_UNASSESSED"],
          "F_next":["ASSESS_RG01_RG12_WITH_EVIDENCE_AND_COUNTEREVIDENCE"],
          "provenance":[]
        } for u in program["research_units"]
      }
    }

def compute_one(rec, method):
    weights={d["id"]:float(d["weight"]) for d in method["dimensions"]}
    hard={d["id"] for d in method["dimensions"] if d.get("hard_gate")}
    vals=rec.get("scores_by_dimension",{})
    known={k:v for k,v in vals.items() if k in weights and numeric(v)}
    total_w=sum(weights.values())
    known_w=sum(weights[k] for k in known)
    coverage=known_w/total_w if total_w else 0.0
    score=(sum(weights[k]*known[k] for k in known)/(4*known_w)*100) if known_w else None

    blockers=[]
    critical=any(isinstance(x,dict) and x.get("severity")=="CRITICAL" and x.get("resolved") is not True
                 for x in rec.get("counterevidence",[]))
    if critical:
        blockers.append("UNRESOLVED_CRITICAL_COUNTEREVIDENCE")
    for k in sorted(hard):
        if vals.get(k,TV)==TV:
            blockers.append("HARD_GATE_TOKEN_VAZIO:"+k)
    if rec.get("prior_art_state",TV)==TV:
        blockers.append("PRIOR_ART_TOKEN_VAZIO")
    if rec.get("falsifier",TV)==TV:
        blockers.append("FALSIFIER_TOKEN_VAZIO")

    cls="R0_UNASSESSED"
    if coverage>=.50 and score is not None: cls="R1_SPECULATIVE"
    if coverage>=.60 and score is not None and score>=40: cls="R2_FORMALIZED"
    if (coverage>=.70 and score is not None and score>=55 and
        all(numeric(vals.get(k)) and vals[k]>=3 for k in ("RG01","RG02","RG04"))):
        cls="R3_TESTABLE"
    if (coverage>=.80 and score is not None and score>=70 and
        all(numeric(vals.get(k)) and vals[k]>=2 for k in ("RG03","RG05","RG11"))):
        cls="R4_SUPPORTED"
    if (coverage>=.90 and score is not None and score>=85 and
        all(numeric(vals.get(k)) and vals[k]>=3 for k in hard) and not critical):
        cls="R5_STRONG"
    exact=rec.get("claim_state")=="PASS_EXACT" or rec.get("proof_status")=="PROVEN"
    if exact and all(vals.get(k)==4 for k in ("RG01","RG02","RG03","RG04")) and not critical:
        cls="R6_EXACT_PROVEN"

    return {
      "coverage":round(coverage,6),
      "rigor_score":None if score is None else round(score,6),
      "rigor_class":cls,
      "hard_gate_status":"BLOCKED" if blockers else "CLEAR",
      "promotion_blockers":blockers,
      "promotion_decision":"BLOCKED" if blockers else "ELIGIBLE_FOR_REVIEW"
    }

def adversarial_prompts(unit_id, method):
    out=[]
    for d in method["dimensions"]:
        for n in method["autocritique"]["nibiguiri_lenses"]:
            out.append({
              "unit_id":unit_id,"rigor_dimension":d["id"],
              "nibiguiri":n["id"],"angle_deg":n["angle_deg"],
              "prompt":f"{unit_id}/{d['id']}/{n['id']}: tente refutar ou rebaixar o rigor de '{d['title']}' pela lente '{n['title']}'."
            })
    return out

def validate(program,method,assessment):
    errors=[]
    units=program.get("research_units",[])
    if len(units)!=48: errors.append(f"expected 48 units, got {len(units)}")
    if len(method.get("dimensions",[]))!=12: errors.append("expected 12 rigor dimensions")
    if len(method.get("autocritique",{}).get("nibiguiri_lenses",[]))!=12: errors.append("expected 12 Nibiguiri lenses")
    dim_ids=[d.get("id") for d in method.get("dimensions",[])]
    if dim_ids != [f"RG{i:02d}" for i in range(1,13)]: errors.append("rigor dimensions must be RG01..RG12 in order")
    if method.get("autocritique",{}).get("base_matrix_cells") != 576: errors.append("method base matrix must be 576")
    if method.get("autocritique",{}).get("adversarial_tensor_cells") != 6912: errors.append("method adversarial tensor must be 6912")
    tv_desc=method.get("cell_scale",{}).get(TV,"")
    if "nunca" not in tv_desc.lower() or "0" not in tv_desc: errors.append("TOKEN_VAZIO must explicitly remain distinct from numeric zero")
    ids=[u["id"] for u in units]
    if len(ids)!=len(set(ids)): errors.append("duplicate research unit ids")
    assess=assessment.get("research_units",{})
    missing=[i for i in ids if i not in assess]
    if missing: errors.append("missing assessments: "+",".join(missing))
    dims={d["id"] for d in method["dimensions"]}
    for uid in ids:
        vals=assess.get(uid,{}).get("scores_by_dimension",{})
        for k,v in vals.items():
            if k not in dims: errors.append(f"{uid}: unknown dimension {k}")
            elif v!=TV and not numeric(v): errors.append(f"{uid}/{k}: invalid score {v!r}")
    return errors

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--program",required=True)
    ap.add_argument("--method",required=True)
    ap.add_argument("--assessment")
    ap.add_argument("--emit-blank")
    ap.add_argument("--emit-report")
    ap.add_argument("--emit-adversarial")
    args=ap.parse_args()

    program=load(args.program); method=load(args.method)
    assessment=load(args.assessment) if args.assessment else blank_assessment(program,method)
    if args.emit_blank:
        Path(args.emit_blank).write_text(json.dumps(assessment,ensure_ascii=False,indent=2),encoding="utf-8")
    errors=validate(program,method,assessment)
    if errors:
        for e in errors: print("FAIL",e,file=sys.stderr)
        return 2

    report={
      "schema":"raf.rll.rigor_report.v1",
      "summary":{"research_units":48,"rigor_dimensions":12,"base_matrix_cells":576,"adversarial_tensor_cells":6912},
      "results":{uid:compute_one(rec,method) for uid,rec in assessment["research_units"].items()}
    }
    if args.emit_report:
        Path(args.emit_report).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    if args.emit_adversarial:
        prompts=[]
        for uid in assessment["research_units"]:
            prompts.extend(adversarial_prompts(uid,method))
        Path(args.emit_adversarial).write_text(json.dumps(prompts,ensure_ascii=False,indent=2),encoding="utf-8")
    print("PASS units=48 rigor_dimensions=12 base_cells=576 adversarial_cells=6912")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
