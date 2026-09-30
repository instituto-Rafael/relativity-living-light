#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
from data.pipelines.strong_gravity.gravitational_cascade_network import CascadeNetwork, Edge, Node, branching_potential

def digest(x): return hashlib.sha256(json.dumps(x, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def main():
    p=argparse.ArgumentParser(); p.add_argument("scenario", type=Path); p.add_argument("--output", type=Path); a=p.parse_args()
    payload=json.loads(a.scenario.read_text())
    cfg=payload["network"]
    net=CascadeNetwork([Node(**x) for x in payload["nodes"]],[Edge(**x) for x in payload["edges"]],attenuation_scale_m=cfg["attenuation_scale_m"],attenuation_exponent=cfg.get("attenuation_exponent",2.0),propagation_speed_m_s=cfg.get("propagation_speed_m_s",299792458.0))
    r=net.run(payload["seed"])
    receipt={"schema_version":"1.0","module":"gravitational_cascade_trigger_network","claim_allowed":False,"input_sha256":digest(payload),"result":{"avalanche_size":r.avalanche_size,"active_fraction":r.active_fraction,"max_depth":r.max_depth,"duration_s":r.duration_s,"total_seed_j":r.total_seed_j,"total_released_j":r.total_released_j,"activations":[e.__dict__ for e in r.activations],"branching_potential":branching_potential(net)},"claim_boundary":"Computational threshold cascade only; no physical cosmic-avalanche claim without source-specific derivation and falsification."}
    receipt["receipt_sha256"]=digest(receipt); text=json.dumps(receipt,indent=2,sort_keys=True)+"\n"
    if a.output: a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(text)
    else: sys.stdout.write(text)
    return 0
if __name__ == "__main__": raise SystemExit(main())
