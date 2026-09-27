#!/usr/bin/env python3
"""Real DESI DR2 BAO comparison for the RMRCTI/geometry bridge.

This does not map RMRCTI stable/peak labels onto cosmological data.
It compares already-bound physical observables and model predictions, and
records the direct Delta-P mapping as blocked until a typed physical mapping
exists.
"""
from __future__ import annotations
import csv, json, math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data/real/cosmology/desi_dr2_bao_primary_points.csv"
G4=ROOT/"results/RLL_G4_DESI_GEOMETRY_LCDM_RLL_REPRODUCTION_V1.json"
BRIDGE=ROOT/"data/governance/RLL_RMRCTI_DELTA_P_CALIBRATION_BRIDGE_V1.json"

TRACERS=("LRG1","LRG2","LRG3_PLUS_ELG1","ELG2","QSO","Lya")

def load_rows():
    with DATA.open("r",encoding="utf-8",newline="") as f:
        out=[]
        for r in csv.DictReader(f):
            out.append({
                "tracer":r["tracer"],"z":float(r["z_eff"]),
                "observable":r["observable"],"value":float(r["value"]),
                "sigma":float(r["sigma"]),"block":r["covariance_block"],
                "rho":float(r["correlation_coefficient"]) if r["correlation_coefficient"] else None,
            })
        return out

def pred_map(payload,model):
    return {(r["tracer"],r["observable"]):r for r in payload["outputs"][model]["predictions"]}

def standardized_residuals(rows,preds):
    out=[]
    for r in rows:
        p=preds[(r["tracer"],r["observable"])]
        residual=r["value"]-float(p["predicted"])
        out.append({**r,"predicted":float(p["predicted"]),"residual":residual,"z_residual":residual/r["sigma"]})
    zs=[x["z_residual"] for x in out]
    absz=sorted(abs(x) for x in zs)
    return {
        "rows":out,
        "rms_z":math.sqrt(sum(x*x for x in zs)/len(zs)),
        "mean_z":sum(zs)/len(zs),
        "median_abs_z":absz[len(absz)//2],
        "max_abs_z":max(absz),
    }

def block_summary_chi2(rows,preds):
    total=0.0
    blocks=[]
    b=next(r for r in rows if r["tracer"]=="BGS")
    pb=preds[(b["tracer"],b["observable"])]
    z=(b["value"]-float(pb["predicted"]))/b["sigma"]
    total+=z*z
    blocks.append({"block":b["block"],"chi2":z*z})
    for t in TRACERS:
        dm=next(r for r in rows if r["tracer"]==t and r["observable"]=="DM_over_rd")
        dh=next(r for r in rows if r["tracer"]==t and r["observable"]=="DH_over_rd")
        pdm=preds[(t,"DM_over_rd")]
        pdh=preds[(t,"DH_over_rd")]
        dx=dm["value"]-float(pdm["predicted"])
        dy=dh["value"]-float(pdh["predicted"])
        rho=float(dm["rho"])
        q=(dx*dx/(dm["sigma"]**2)-2*rho*dx*dy/(dm["sigma"]*dh["sigma"])+dy*dy/(dh["sigma"]**2))/(1-rho*rho)
        total+=q
        blocks.append({"block":dm["block"],"chi2":q})
    return {"chi2":total,"blocks":blocks}

def geometry_pairs(rows,preds):
    out=[]
    for t in TRACERS:
        dm=next(r for r in rows if r["tracer"]==t and r["observable"]=="DM_over_rd")
        dh=next(r for r in rows if r["tracer"]==t and r["observable"]=="DH_over_rd")
        x,y=dm["value"],dh["value"]
        px=float(preds[(t,"DM_over_rd")]["predicted"])
        py=float(preds[(t,"DH_over_rd")]["predicted"])
        obs_s=.5*math.log(x*y); obs_a=math.log(x/y)
        pr_s=.5*math.log(px*py); pr_a=math.log(px/py)
        out.append({
            "tracer":t,"z":dm["z"],
            "observed":{"log_scale":obs_s,"anisotropy":obs_a},
            "predicted":{"log_scale":pr_s,"anisotropy":pr_a},
            "residual":{"log_scale":obs_s-pr_s,"anisotropy":obs_a-pr_a},
        })
    return out

def build():
    rows=load_rows()
    g4=json.loads(G4.read_text(encoding="utf-8"))
    bridge=json.loads(BRIDGE.read_text(encoding="utf-8"))
    models={}
    for model in ("LCDM","RLL"):
        preds=pred_map(g4,model)
        sr=standardized_residuals(rows,preds)
        block=block_summary_chi2(rows,preds)
        full=float(g4["outputs"][model]["chi2_DESI_recomputed"])
        models[model]={
            "standardized_residual_summary":{k:sr[k] for k in ("rms_z","mean_z","median_abs_z","max_abs_z")},
            "block_summary_chi2":block,
            "full_covariance_g4_chi2":full,
            "full_minus_block_summary_chi2":full-block["chi2"],
            "geometry_pairs":geometry_pairs(rows,preds),
        }
    return {
      "schema":"rll.rmrcti_physical_comparison.v1",
      "date":"2026-09-26",
      "claim_allowed":False,
      "physical_dataset":{
        "name":"DESI DR2 BAO 2025",
        "points":len(rows),
        "anisotropic_pairs":len(TRACERS),
        "source":str(DATA.relative_to(ROOT)),
        "prediction_source":str(G4.relative_to(ROOT)),
      },
      "models":models,
      "cross_model_geometry":g4["cross_model_geometry"],
      "rmrcti_calibration_reference":bridge,
      "direct_delta_p_physical_test":{
        "state":"BLOCKED_NO_TYPED_STABLE_PEAK_PHYSICS_MAPPING",
        "reason":"DESI BAO rows do not define RMRCTI stable_any or peak semantics. Inventing them from residual sign/magnitude would be post-hoc.",
        "delta_p_computed_on_desi":False,
      },
      "result":{
        "background_geometry_discrimination":"NULL_SUBMANIFOLD_NO_DISCRIMINATION",
        "reason":"recorded G4 RLL best fit has Omega_s0=0 and its predictions match LCDM at numerical/best-fit residual scale",
        "physical_delta_p_claim":"NOT_ESTABLISHED",
      },
      "boundary":"physical residual comparison != RMRCTI Delta-P physical binding",
    }

def main():
    out=build()
    print(json.dumps(out,ensure_ascii=False,indent=2,sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
