#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
import yaml

DEFAULT = Path("data/contracts/rll_geometric_operator_omega_g.v1.yaml")

def validate(data):
    errors=[]
    def req(ok,msg):
        if not ok: errors.append(msg)
    req(data.get("schema")=="rll.geometric_operator_omega_g.v1","schema mismatch")
    req(data.get("claim_allowed") is False,"claim_allowed must be false")
    req(data.get("scientific_confirmation") is False,"scientific_confirmation must be false")
    src=data.get("canonical_math_source",{})
    req(src.get("repository")=="rafaelmeloreisnovo/Matem-tica-","canonical math repository mismatch")
    req(src.get("yaml_commit")=="7986c6dbafe2583b21d224224308267f576ef7bf","canonical YAML commit mismatch")
    ident=data.get("identity",{})
    req("data/omega_operational/rll_omega7_operational.json" in ident.get("distinct_from",[]),"Omega7 distinction missing")
    bind=data.get("rll_binding",{})
    req(bind.get("direct_likelihood_binding") is False,"direct likelihood binding must remain false")
    req(bind.get("required_bridge")=="BIND(I_j,O_k,mechanism,units,covariance,falsifier)","binding gate mismatch")
    req(data.get("gates",{}).get("scientific_claim")=="BLOCKED","scientific claim must be blocked")
    return {"schema":"rll.geometric_operator_omega_g.validation.v1","valid":not errors,"errors":errors,"claim_allowed":False,"boundary":"STRUCTURAL_PASS != SCIENTIFIC_CONFIRMATION"}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--contract",type=Path,default=DEFAULT)
    args=ap.parse_args()
    data=yaml.safe_load(args.contract.read_text(encoding="utf-8"))
    result=validate(data)
    print(json.dumps(result,indent=2))
    return 0 if result["valid"] else 1

if __name__=="__main__":
    raise SystemExit(main())
