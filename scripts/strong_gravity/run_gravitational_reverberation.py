#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from data.pipelines.strong_gravity.gravitational_reverberation_response import DampedMode,ReverberationConfig,response_summary,sample_response

def digest(x): return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def frange(start,stop,step):
    if step<=0 or stop<start: raise ValueError("invalid sampling range")
    n=int((stop-start)/step+0.5)
    for i in range(n+1):
        v=start+i*step
        if v<=stop+step*1e-9: yield v

def main():
    p=argparse.ArgumentParser(); p.add_argument("scenario",type=Path); p.add_argument("--output",type=Path); a=p.parse_args()
    payload=json.loads(a.scenario.read_text()); c=payload["config"]
    cfg=ReverberationConfig(event_time_s=c.get("event_time_s",0),direct_amplitude=c.get("direct_amplitude",0),direct_width_s=c.get("direct_width_s",1),modes=tuple(DampedMode(**m) for m in c.get("modes",[])),tail_amplitude=c.get("tail_amplitude",0),tail_scale_s=c.get("tail_scale_s",1),tail_power=c.get("tail_power",2),memory_delta=c.get("memory_delta",0),memory_rise_s=c.get("memory_rise_s",1))
    o=payload.get("observer",{}); s=payload["sampling"]
    samples=sample_response(cfg,tuple(frange(s["start_s"],s["stop_s"],s["step_s"])),distance_m=o.get("distance_m",0),propagation_speed_m_s=o.get("propagation_speed_m_s",299792458.0))
    receipt={"schema_version":"1.0","module":"gravitational_reverberation_response","claim_allowed":False,"input_sha256":digest(payload),"summary":response_summary(samples,cfg),"samples":[x.__dict__ for x in samples],"cascade_energy_bridge":"TOKEN_VAZIO","claim_boundary":"Synthetic signal reference only; no astrophysical fit or new-physics claim."}
    receipt["receipt_sha256"]=digest(receipt); text=json.dumps(receipt,indent=2,sort_keys=True)+"\n"
    if a.output: a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(text)
    else: sys.stdout.write(text)
    return 0
if __name__=="__main__": raise SystemExit(main())
