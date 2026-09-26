#!/usr/bin/env python3
"""WS01 evidence executor: measure decision sensitivity without selecting semantics."""
from __future__ import annotations
import argparse, csv, hashlib, json, math, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
 sys.path.insert(0,str(ROOT))

from rx import cosmology
from rx.kernel import dump_json, simpson
OUT=ROOT/"artifacts/science/background/RLL_WS01_BACKGROUND_DECISION_EVIDENCE_V1.json"
HZ28=ROOT/"data/real/cosmology/Hz_cosmic_chronometers_independent.csv"
HZ33=ROOT/"data/real/Hz_data_real.csv"
OMEGA_R=(9.0e-5,9.18e-5)
STEPS=(64,128,256,512,1024,2048)
ZGRID=(0.01,0.1,0.3,0.5,1.0,1.5,2.0,3.0,5.0,10.0,1100.0)
VECTORS={
 "LCDM":[67.4,0.315,0.02236,0.811],
 "RLL_NULL":[67.4,0.315,0.0,1.0,0.3,0.02236,0.811],
 "RLL_PROBE":[67.4,0.315,0.001,1.0,0.3,0.02236,0.811],
}

def sha256(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for b in iter(lambda:f.read(1<<20),b""): h.update(b)
 return h.hexdigest()

def rows(p):
 with p.open(encoding="utf-8",newline="") as f:return list(csv.DictReader(f))

def set_orad(x):
 cosmology.ORAD=float(x)

def trap(fn,a,b,n):
 h=(b-a)/n
 return h*(0.5*fn(a)+sum(fn(a+i*h) for i in range(1,n))+0.5*fn(b))

def dc(model,z,v,n,method):
 xmax=math.log1p(z); fn=lambda x: math.exp(x)/math.sqrt(max(cosmology.e2(model,math.exp(x)-1.0,v),1e-300))
 integ=simpson(fn,0,xmax,n) if method=="simpson" else trap(fn,0,xmax,n)
 return cosmology.C_KMS/v[0]*integ

def overlap(a,b):
 def key(r):
  for k in ("z","z_eff","redshift"):
   if k in r and r[k] not in ("",None):
    try:return round(float(r[k]),10)
    except ValueError:pass
  return None
 ka={key(r) for r in a}; kb={key(r) for r in b}; ka.discard(None);kb.discard(None)
 return sorted(ka&kb)

def build():
 a,b=rows(HZ28),rows(HZ33)
 sensitivity=[]
 for model,v in VECTORS.items():
  m="RLL" if model.startswith("RLL") else model
  for z in ZGRID:
   vals={}
   for o in OMEGA_R:
    set_orad(o); vals[str(o)]=cosmology.hubble(m,z,v)
   den=max(abs(vals[str(OMEGA_R[0])]),1e-300)
   sensitivity.append({"model":model,"z":z,"H_orad_9e5":vals[str(OMEGA_R[0])],"H_orad_9p18e5":vals[str(OMEGA_R[1])],"relative_delta":abs(vals[str(OMEGA_R[1])]-vals[str(OMEGA_R[0])])/den})
 convergence=[]
 set_orad(OMEGA_R[1])
 for model,v in VECTORS.items():
  m="RLL" if model.startswith("RLL") else model
  for z in ZGRID[:-1]:
   ref=dc(m,z,v,STEPS[-1],"trap")
   for n in STEPS:
    s=dc(m,z,v,n,"simpson"); t=dc(m,z,v,n,"trap")
    convergence.append({"model":model,"z":z,"steps":n,"simpson_mpc":s,"trap_mpc":t,"simpson_vs_trap_rel":abs(s-t)/max(abs(t),1e-300),"simpson_vs_ref_rel":abs(s-ref)/max(abs(ref),1e-300)})
 max_orad=max(x["relative_delta"] for x in sensitivity)
 finest=[x for x in convergence if x["steps"]==STEPS[-1]]
 max_cross=max(x["simpson_vs_trap_rel"] for x in finest)
 max_ref=max(x["simpson_vs_ref_rel"] for x in finest)
 ov=overlap(a,b)
 def row_key(r):
  return (float(r["z"]),float(r["H_obs"]),float(r["sigma_H"]),str(r["source"]))
 a_keys=[row_key(r) for r in a]
 pure_b=[r for r in b if str(r.get("source","")).startswith("CC_") and "BAO" not in str(r.get("source","")).upper()]
 pure_b_keys=[row_key(r) for r in pure_b]
 a_z={round(float(r["z"]),10) for r in a}
 extra=[{"z":float(r["z"]),"H_obs":float(r["H_obs"]),"sigma_H":float(r["sigma_H"]),"source":str(r["source"])} for r in b if round(float(r["z"]),10) not in a_z]
 extra_all_bao=bool(extra) and all("BAO" in r["source"].upper() for r in extra)
 pure_projection_match=a_keys==pure_b_keys
 return {
  "schema":"rll.ws01.background_decision_evidence.v1",
  "state":"EVIDENCE_MATERIALIZED_DECISION_STILL_FAIL_CLOSED",
  "claim_allowed":False,
  "decision_selected":False,
  "inputs":{"omega_r":OMEGA_R,"hz_surfaces":[{"path":str(HZ28.relative_to(ROOT)),"rows":len(a),"sha256":sha256(HZ28)},{"path":str(HZ33.relative_to(ROOT)),"rows":len(b),"sha256":sha256(HZ33)}]},
  "hz_overlap":{"shared_redshift_count":len(ov),"shared_redshifts":ov,"extra_rows_in_33":extra,"extra_row_count":len(extra),"extra_all_bao_labeled":extra_all_bao,"pure_cc_projection_rows":len(pure_b),"pure_cc_projection_matches_independent_28_exactly":pure_projection_match,"selection_authority":"G4/WS02 pre-existing rule: source begins with CC_ and excludes labels containing BAO","boundary":"The 33-row container is not a 33-row pure-CC likelihood surface when the pre-existing G4/WS02 no-double-count selection is applied."},
  "omega_r_sensitivity":{"max_relative_H_delta":max_orad,"rows":sensitivity},
  "distance_integration":{"methods":["log1p_simpson","log1p_trapezoid_independent_implementation"],"steps":STEPS,"max_finest_simpson_vs_trapezoid_relative":max_cross,"max_finest_simpson_vs_2048_trapezoid_reference_relative":max_ref,"rows":convergence},
  "axis_status":{"omega_r":"EVIDENCE_ADDED_NOT_SELECTED","hz_dataset":"EVIDENCE_SUPPORTS_PURE_CC28_FREEZE_BY_PREEXISTING_NO_DOUBLE_COUNT_POLICY" if pure_projection_match and extra_all_bao else "BLOCKED_HZ_SURFACE_MISMATCH","growth_mode":"TOKEN_VAZIO_UNTIL_WS06","distance_integration":"EVIDENCE_ADDED_TOLERANCE_NOT_YET_PROMOTED"},
  "promotion":"BLOCKED",
  "boundary":"This executor measures sensitivity and numerical convergence only. It MUST NOT choose the canonical option from fit quality."
 }
def main(argv=None):
 p=argparse.ArgumentParser();p.add_argument("--write",action="store_true");a=p.parse_args(argv)
 x=build()
 if a.write:dump_json(OUT,x)
 print(json.dumps({"state":x["state"],"max_relative_H_delta":x["omega_r_sensitivity"]["max_relative_H_delta"],"max_finest_crosscheck":x["distance_integration"]["max_finest_simpson_vs_trapezoid_relative"],"promotion":x["promotion"],"claim_allowed":False},indent=2))
 return 0
if __name__=="__main__":raise SystemExit(main())
