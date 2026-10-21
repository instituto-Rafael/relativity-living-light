#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CONTRACT=ROOT/"data/contracts/rll_observer_observation_science_routing.v1.json"
INSTANCE=ROOT/"data/observations/2026-10-20_observer_science_closure.v1.json"

def load(p): return json.loads(Path(p).read_text(encoding="utf-8"))

def validate(c,o):
    e=[]
    routes={x["id"] for x in c.get("science_routes",[])}
    if c.get("schema")!="rll.observer-observation-science-routing/v1": e.append("contract_schema")
    if o.get("schema")!="rll.observer-observation-instance/v1": e.append("instance_schema")
    if o.get("observer_id")==o.get("observation_id"): e.append("observer_observation_collision")
    for f in c.get("required_observation_fields",[]):
        if f not in o: e.append(f"missing:{f}")
    if o.get("epistemic_state") not in c.get("epistemic_states",[]): e.append("epistemic_state")
    for x in o.get("conduct",[]):
        if x not in c.get("conduct",[]): e.append(f"conduct:{x}")
    for x in o.get("phenomenon_tags",[]):
        if x not in c.get("phenomenon_tags",[]): e.append(f"phenomenon:{x}")
    sr=o.get("science_routes",[])
    if not sr: e.append("science_routes_empty")
    for x in sr:
        if x.get("id") not in routes: e.append(f"science_route:{x.get('id')}")
        if x.get("role") not in {"PRIMARY","SECONDARY"}: e.append("science_route_role")
    if o.get("epistemic_state") in {"UNCERTAIN","UNKNOWN"} and not o.get("typed_gaps"):
        e.append("unknown_without_typed_gap")
    for g in o.get("typed_gaps",[]):
        if not str(g.get("id","")).startswith("TOKEN_VAZIO_") or not g.get("type") or not g.get("closure"):
            e.append("untyped_gap")
    if o.get("raw_session_text_stored") is not False: e.append("raw_session_text_boundary")
    if not o.get("required_gates"): e.append("gates_empty")
    if not o.get("rollback"): e.append("rollback_empty")
    return e

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--contract",type=Path,default=CONTRACT)
    ap.add_argument("--instance",type=Path,default=INSTANCE)
    a=ap.parse_args()
    e=validate(load(a.contract),load(a.instance))
    print(json.dumps({"schema":"rll.observer-observation-validation/v1","state":"PASS" if not e else "FAIL","errors":e,"claim_allowed":False},indent=2))
    return 0 if not e else 1
if __name__=="__main__": raise SystemExit(main())
