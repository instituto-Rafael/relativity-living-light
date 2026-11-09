#!/usr/bin/env python3
"""RLL cosmology comparison evidence guard. Read-only; never refits."""
import argparse,csv,hashlib,json,math
from pathlib import Path
FILES={
"scan":"results/audit/rll_model_evidence_scan.json",
"csv64":"results/structure_d/joint_real_likelihood.csv",
"desi":"data/results/desi_dr2_bao_model_comparison.json",
"other64":"data/results/model_comparison.json",
"old45":"results/RLL_chi2_results.csv",
"growth":"results/growth_comparison_rll_vs_lcdm.json",
"perturb":"results/perturbation_rll_baseline_summary.json",
"g4":"data/contracts/rll_g4_background_tournament.v1.json",
"g5":"data/contracts/rll_g5_canonical_background_likelihood.v1.json",
"g6":"data/contracts/rll_g6_canonical_inference.v1.json",
"h52":"data/results/cosmology_joint/rll_g6_h52_nonidentifiability_20260926.v1.json"}
def eq(a,b,label,tol=2e-7):
    if not math.isfinite(float(a)) or not math.isclose(float(a),float(b),abs_tol=tol,rel_tol=0):
        raise ValueError("SOURCE_INCONSISTENCY "+label+" "+str(a)+" vs "+str(b))
def ic(chi,n,k):
    if k<0 or n<=k+1:raise ValueError("AICc_DOMAIN")
    a=chi+2*k
    return {"AIC":a,"AICc":a+2*k*(k+1)/(n-k-1),"BIC":chi+k*math.log(n)}
def audit(root):
    root=Path(root);d={};src={}
    for name,path in FILES.items():
        blob=(root/path).read_bytes()
        src[name]={"path":path,"sha256":hashlib.sha256(blob).hexdigest(),"bytes":len(blob)}
        d[name]=(list(csv.DictReader(blob.decode("utf-8-sig").splitlines())) if path.endswith(".csv") else json.loads(blob))
    scan=d["scan"]
    if scan.get("row_count")!=4 or scan.get("claim_status")!="CLAIM_BLOCKED":
        raise ValueError("CLAIM_BOUNDARY_CHANGED")
    models={r["model"]:r for r in scan["model_scans"]}
    rows={r["model"].replace("CPL_w0waCDM","CPL").replace("_joint_real",""):r for r in d["csv64"]}
    if set(models)!={"LCDM","wCDM","CPL","RLL"} or set(rows)!=set(models):
        raise ValueError("MISSING_MODEL")
    for name,r in models.items():
        n,k,chi=int(r["N"]),int(r["k"]),float(r["chi2"])
        if n!=64 or int(r["dof"])!=n-k:raise ValueError("DOF_"+name)
        for key,value in ic(chi,n,k).items():
            eq(r[key],value,name+"/formula/"+key)
            eq(rows[name][key],r[key],name+"/source_csv/"+key)
        eq(rows[name]["chi2"],chi,name+"/csv_chi2")
        eq(sum(r["component_chi2"].values()),chi,name+"/component_chi2")
    if models["RLL"]["Os0"]!=0.0:raise ValueError("RLL_OS0_CHANGED_REVIEW")
    delta64={name:{k:models["RLL"][k]-models[name][k] for k in ("chi2","AICc","BIC")} for name in ("LCDM","wCDM","CPL")}
    desi=d["desi"]
    if set(desi["models"])!={"LCDM","RLL"}:raise ValueError("DESI_MODEL")
    for name,r in desi["models"].items():
        if r["n_obs"]!=13:raise ValueError("DESI_COUNT")
        for k,v in ic(r["chi2"],13,r["k_params"]).items():
            if k in ("AIC","BIC"):eq(r[k],v,"DESI/"+name+"/"+k)
    dd={k:desi["models"]["RLL"][k]-desi["models"]["LCDM"][k] for k in ("chi2","AIC","BIC")}
    for k,v in dd.items():eq(desi["delta"]["delta_"+k.lower()+"_rll_minus_lcdm"],v,"DESI/delta/"+k)
    other=d["other64"]
    if other["n_obs"]!=64 or other["claim_allowed"] is not False:raise ValueError("OTHER64_SCOPE")
    otherdelta={}
    for k in ("chi2","AIC","BIC"):
        diff=other[k+"_rll"]-other[k+"_lcdm"]
        eq(other["delta_"+k.lower()+"_rll_minus_lcdm"],diff,"OTHER64/"+k)
        otherdelta[k]=diff
    old={r["Model"]:r for r in d["old45"] if r["Model"] in ("LCDM","RLL")}
    if set(old)!={"LCDM","RLL"}:raise ValueError("OLD_MODELS")
    for name,r in old.items():
        if int(r["N_obs"])!=45:raise ValueError("OLD_COUNT")
        for k,v in ic(float(r["chi2"]),45,int(r["k"])).items():
            if k in ("AIC","BIC"):eq(r[k],v,"OLD/"+name+"/"+k,tol=.003)
    olddelta={k:float(old["RLL"][k])-float(old["LCDM"][k]) for k in ("chi2","AIC","BIC")}
    g=d["growth"]; models_g=g["models"]
    if g["data_policy"]["full_covariance"]!="TOKEN_VAZIO" or g["quality_gates"]["claim_allowed"] is not False:
        raise ValueError("GROWTH_CLAIM")
    if any(models_g[k]["n_data"]!=16 for k in ("rll","lcdm")):raise ValueError("GROWTH_N")
    growthdelta=models_g["rll"]["chi2_fsigma8"]-models_g["lcdm"]["chi2_fsigma8"]
    eq(growthdelta,g["comparisons"]["chi2_fsigma8_rll_minus_lcdm"],"GROWTH/delta")
    p=d["perturb"]
    if p["status"]!="linear_perturbation_kernel_available" or p["cmb_cl_exact"]!="TOKEN_VAZIO" or p["nonlinear_pk_exact"]!="TOKEN_VAZIO":raise ValueError("PERTURBATION_REVIEW")
    for key in ("g4","g5","g6","h52"):
        if d[key]["claim_allowed"] is not False:raise ValueError("CLAIM_PROMOTION_"+key)
    return {"schema":"rll.comparator_evidence_matrix.v1","status":"PASS_SCOPED_SOURCE_CONSISTENCY",
      "claim_allowed":False,"scientific_confirmation":False,"sources":src,
      "regimes":{
        "joint64_scan":{"n_obs":64,"RLL_Os0":models["RLL"]["Os0"],"delta_rll_minus_models":delta64,"models":list(models)},
        "desi13":{"n_obs":13,"delta_rll_minus_lcdm":dd},
        "joint64_other":{"n_obs":64,"delta_rll_minus_lcdm":otherdelta,"different_parameterization":True},
        "legacy45":{"n_obs":45,"delta_rll_minus_lcdm":olddelta},
        "growth16":{"n_obs":16,"delta_chi2_rll_minus_lcdm":growthdelta,"covariance":"diagonal_only"}},
      "features":{"background_Hz_BAO":"AVAILABLE_SCOPED","linear_growth":"AVAILABLE_APPROXIMATE",
        "compressed_CMB_shift":"AVAILABLE_SCOPED","full_CMB_TT_TE_EE_Cl":"TOKEN_VAZIO",
        "nonlinear_Pk":"TOKEN_VAZIO","RLL_perturbation_CLASS_CAMB_closure":"TOKEN_VAZIO",
        "nested_G6_seed_stability":"TOKEN_VAZIO","independent_replication":"TOKEN_VAZIO"},
      "warning":"Equal N does NOT imply identical data, priors, covariance or likelihood. No pooling or cross-regime ranking.",
      "execution":"READ_ONLY_NO_REFIT"}
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[2]);ap.add_argument("--output",type=Path)
    a=ap.parse_args();report=audit(a.root)
    if a.output:
        a.output.parent.mkdir(parents=True,exist_ok=True)
        a.output.write_text(json.dumps(report,indent=2,sort_keys=True,ensure_ascii=False)+"\n")
    print(json.dumps({"status":report["status"],"regimes":list(report["regimes"]),"claim_allowed":False}))
if __name__=="__main__":main()
