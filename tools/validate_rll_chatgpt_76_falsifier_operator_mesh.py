#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DEFAULT=ROOT/"data/contracts/rll_chatgpt_76_falsifier_operator_mesh.v1.json"
OP_RE=re.compile(r"^OP(\d{2})$")
def load(p): return json.loads(Path(p).read_text(encoding="utf-8"))
def validate(m):
 e=[]
 if m.get("schema")!="rll.chatgpt-76-falsifier-operator-mesh/v1": e.append("schema")
 ops=m.get("operators",[])
 if m.get("operator_count")!=76 or len(ops)!=76: e.append("operator_count")
 ids=[o.get("id") for o in ops]
 if ids!=[f"OP{i:02d}" for i in range(1,77)]: e.append("operator_ids")
 if len(ids)!=len(set(ids)): e.append("duplicate_operator_id")
 for o in ops:
  if o.get("urgency") not in {"P0","P1","P2"}: e.append(f"urgency:{o.get('id')}")
  if not o.get("provenance_interactions"): e.append(f"provenance:{o.get('id')}")
  if o.get("state")!="PROPOSED_NOT_EXECUTED": e.append(f"premature_state:{o.get('id')}")
  if not o.get("falsifier") or not o.get("close_when"): e.append(f"missing_falsifier:{o.get('id')}")
  if o.get("claim_effect")!="NONE_UNTIL_EXECUTED": e.append(f"claim_effect:{o.get('id')}")
 p0=[o for o in ops if o.get("urgency")=="P0"]
 if not p0: e.append("no_p0")
 for tv in m.get("token_vazios",[]):
  if not str(tv.get("id","")).startswith("TOKEN_VAZIO_") or not tv.get("type") or not tv.get("close_when"):
   e.append("untyped_token_vazio")
 if m.get("claim_allowed") is not False or m.get("publication_ready") is not False: e.append("premature_promotion")
 return e
def main():
 ap=argparse.ArgumentParser(); ap.add_argument("--mesh",type=Path,default=DEFAULT); a=ap.parse_args()
 e=validate(load(a.mesh)); print(json.dumps({"state":"PASS" if not e else "FAIL","errors":e,"claim_allowed":False},indent=2)); return 0 if not e else 1
if __name__=="__main__": raise SystemExit(main())
