#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, math, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from rx import cosmology
from rx.kernel import dump_json, simpson

CONTRACT=ROOT/"data/contracts/rll_ws01_distance_integration_tolerance.v1.json"
OUT=ROOT/"artifacts/science/background/RLL_WS01_DISTANCE_INTEGRATION_TOLERANCE_RECEIPT.json"

def load():
 x=json.loads(CONTRACT.read_text(encoding="utf-8"))
 if x.get("state")!="PREREGISTERED_BEFORE_SUCCESSOR_EXECUTION": raise ValueError("tolerance contract not preregistered")
 if x.get("claim_allowed") is not False: raise ValueError("claim boundary drift")
 return x

def trap(fn,a,b,n):
 h=(b-a)/n
 return h*(0.5*fn(a)+sum(fn(a+i*h) for i in range(1,n))+0.5*fn(b))

def dc_trap(model,z,v,n):
 xmax=math.log1p(z)
 fn=lambda xx: math.exp(xx)/math.sqrt(max(cosmology.e2(model,math.exp(xx)-1.0,v),1e-300))
 return cosmology.C_KMS/v[0]*trap(fn,0.0,xmax,n)

def ok(a,b,rtol,atol):
 return abs(a-b) <= atol + rtol*abs(b)

def build():
 c=load(); cosmology.ORAD=float(c["omega_r"])
 s=c["steps"]; rtol=float(c["tolerance"]["rtol"]); atol=float(c["tolerance"]["atol_mpc"])
 rows=[]; failures=[]
 for label,v in c["models"].items():
  model="RLL" if label.startswith("RLL") else label
  for z in c["redshift_grid"]:
   coarse=cosmology.comoving_distance_mpc(model,z,v,steps=int(s["coarse"]),integration_mode="log1p")
   fine=cosmology.comoving_distance_mpc(model,z,v,steps=int(s["fine"]),integration_mode="log1p")
   direct=cosmology.comoving_distance_mpc(model,z,v,steps=int(s["fine"]),integration_mode="direct_z")
   ref=dc_trap(model,z,v,int(s["reference_trapezoid"]))
   checks={
    "fine_vs_trapezoid_reference":ok(fine,ref,rtol,atol),
    "fine_vs_direct_z_simpson":ok(fine,direct,rtol,atol),
    "coarse_vs_fine":ok(coarse,fine,rtol,atol)
   }
   row={
    "model":label,"z":z,"coarse_log1p_simpson_mpc":coarse,"fine_log1p_simpson_mpc":fine,
    "direct_z_simpson_mpc":direct,"log1p_trapezoid_reference_mpc":ref,
    "relative_fine_vs_trapezoid":abs(fine-ref)/max(abs(ref),1e-300),
    "relative_fine_vs_direct":abs(fine-direct)/max(abs(direct),1e-300),
    "relative_coarse_vs_fine":abs(coarse-fine)/max(abs(fine),1e-300),
    "checks":checks
   }
   rows.append(row)
   if not all(checks.values()): failures.append({"model":label,"z":z,"failed":[k for k,vv in checks.items() if not vv]})
 passed=not failures
 return {
  "schema":"rll.ws01_distance_integration_tolerance_receipt.v1",
  "state":"PASS_PREREGISTERED_DISTANCE_TOLERANCE" if passed else "FAIL_PREREGISTERED_DISTANCE_TOLERANCE",
  "claim_allowed":False,
  "promotion_scope":"NUMERICAL_INTEGRATION_ONLY" if passed else "NONE",
  "contract":str(CONTRACT.relative_to(ROOT)),
  "tolerance":c["tolerance"],
  "row_count":len(rows),
  "max_relative_fine_vs_trapezoid":max(r["relative_fine_vs_trapezoid"] for r in rows),
  "max_relative_fine_vs_direct":max(r["relative_fine_vs_direct"] for r in rows),
  "max_relative_coarse_vs_fine":max(r["relative_coarse_vs_fine"] for r in rows),
  "failures":failures,
  "rows":rows,
  "boundary":"PASS freezes only the numerical integration method/tolerance; it is not evidence for RLL physics."
 }

def main():
 ap=argparse.ArgumentParser();ap.add_argument("--write",action="store_true");args=ap.parse_args()
 r=build()
 if args.write: dump_json(OUT,r)
 print(json.dumps({k:r[k] for k in ("state","row_count","max_relative_fine_vs_trapezoid","max_relative_fine_vs_direct","max_relative_coarse_vs_fine","claim_allowed")},indent=2))
 return 0 if r["state"].startswith("PASS") else 2
if __name__=="__main__":raise SystemExit(main())
