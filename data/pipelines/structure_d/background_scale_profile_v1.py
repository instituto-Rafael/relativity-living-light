"""Independent BAO scale-profile and predictive diagnostic; no physical promotion."""
from dataclasses import replace
import math
import numpy as np
from scipy.linalg import solve_triangular
from scipy.optimize import differential_evolution

from .background_likelihood_v1 import Background, GaussianBlock, Row

BAO = frozenset(("DM_over_rd", "DH_over_rd", "DV_over_rd"))
BOUNDS = {
    "lcdm": {"om": (.1, .6)},
    "wcdm": {"om": (.1, .6), "w0": (-2., -.3)},
    "cpl": {"om": (.1, .6), "w0": (-2., -.3), "wa": (-3., 3.)},
    "rll": {"om": (.1, .6), "os0": (0., .25), "zt": (.1, 10.), "wt": (.05, 2.)},
}


def profile_scale(block, model, rd_bounds=(100., 200.)):
    """Profile q=1/rd analytically at a declared H0 pivot, not an H0 measurement."""
    if block.sn_catalog or any(row.obs not in BAO for row in block.rows):
        raise ValueError("BAO-only profile required")
    lo, hi = map(float, rd_bounds)
    if not (0 < lo < hi < math.inf):
        raise ValueError("invalid rd bounds")
    unit = replace(model, rd=1.)
    t = solve_triangular(block.lower, [unit.predict(r.obs, r.z) for r in block.rows], lower=True)
    y = solve_triangular(block.lower, [r.value for r in block.rows], lower=True)
    denom = float(t @ t)
    if not math.isfinite(denom) or denom <= 0.:
        raise ValueError("unidentified scale")
    unconstrained = float(t @ y) / denom
    q = min(1./lo, max(1./hi, unconstrained))
    fitted = replace(model, rd=1./q)
    resid = y - q*t
    return fitted, {"chi2": float(resid @ resid), "scale_boundary": not 1./hi < unconstrained < 1./lo,
                    "H0_rd": fitted.h0*fitted.rd, "claim_allowed": False}


def split_lya(block, indices):
    """Hold out complete Ly-alpha axes. Refuse correlated train/test partitions."""
    hold = tuple(indices)
    n = len(block.rows)
    if not hold or len(set(hold)) != len(hold) or any(i < 0 or i >= n for i in hold):
        raise ValueError("invalid holdout indices")
    train = tuple(i for i in range(n) if i not in hold)
    if not train:
        raise ValueError("empty training set")
    cov = block.lower @ block.lower.T
    if np.any(cov[np.ix_(train, hold)] != 0.):
        raise ValueError("cross covariance requires conditional predictive likelihood")
    def subset(ids, group):
        rows = tuple(block.rows[i] for i in ids)
        return GaussianBlock(rows, cov[np.ix_(ids, ids)], [r.key for r in rows],
                             source_ref=block.source_ref, overlap_groups=(group,))
    return subset(train, "DESI_TRAIN"), subset(hold, "DESI_LYA_HOLDOUT")


def fit_profile(block, model, *, pivot=70., seeds=(42,43,44), maxiter=180, null_om=None, rd_bounds=(100.,200.)):
    bounds = BOUNDS[model]
    names = tuple(bounds)
    if len(seeds) < 2 or len(set(seeds)) != len(seeds) or maxiter < 1:
        raise ValueError("multiseed policy required")
    def score(x):
        try:
            candidate = Background(model, pivot, rd=150., **dict(zip(names, map(float,x))))
            return profile_scale(block, candidate, rd_bounds)[1]["chi2"]
        except (ValueError, OverflowError, FloatingPointError):
            return float("inf")
    starts = {"lcdm": (.3,), "wcdm": (.3,-1.), "cpl": (.3,-1.,0.), "rll": (.3,0.,1.,.3)}
    x0 = list(starts[model])
    if null_om is not None:
        x0[0] = float(null_om)
    runs = []
    for seed in seeds:
        result = differential_evolution(score, list(bounds.values()), seed=int(seed), x0=x0,
                                        maxiter=maxiter, tol=1e-7, polish=True, workers=1)
        if not math.isfinite(result.fun):
            raise ValueError("nonfinite fit")
        runs.append((float(result.fun), list(map(float,result.x)), bool(result.success), int(seed)))
    best = min(runs, key=lambda x:x[0])
    fitted, profile = profile_scale(block, Background(model, pivot, rd=150., **dict(zip(names,best[1]))), rd_bounds)
    boundary = [name for name, val in zip(names,best[1])
                if min(val-bounds[name][0],bounds[name][1]-val) <= 1e-4*(bounds[name][1]-bounds[name][0])]
    if profile["scale_boundary"]:
        boundary.append("rd_pivot")
    spread = max(x[0] for x in runs)-min(x[0] for x in runs)
    stable = all(x[2] for x in runs) and spread <= 1e-3
    return fitted, {**profile, "runs":[{"chi2":x[0],"shape":dict(zip(names,x[1])),"success":x[2],"seed":x[3]} for x in runs],
                    "spread":spread, "boundary":boundary, "state":"PROFILED_FIT_SCOPED" if stable else "OPTIMIZATION_UNCONFIRMED",
                    "physical_identifiability":"TOKEN_VAZIO_POSTERIOR_AND_RANK", "claim_allowed":False}


def run_desi(*, seeds=(42,43,44), maxiter=180):
    """Reuse G4's producer-bound DESI vector and full covariance order guard."""
    from tools.run_g4_background_tournament import load_desi
    data = load_desi()
    rows = [Row(str(i),obs,float(z),float(y)) for i,(obs,z,y) in enumerate(zip(data.observable,data.z,data.observed))]
    block = GaussianBlock(rows,data.covariance,[r.key for r in rows],
                          source_ref="https://arxiv.org/abs/2503.14738",overlap_groups=("DESI_DR2",))
    hold = tuple(i for i,r in enumerate(rows) if math.isclose(r.z,2.33,abs_tol=1e-9,rel_tol=0.))
    if len(rows)!=13 or len(hold)!=2 or {rows[i].obs for i in hold}!={"DM_over_rd","DH_over_rd"}:
        raise ValueError("unexpected DESI DR2 holdout identities")
    train,test = split_lya(block,hold)
    results = {}
    for label, sample in (("all",block),("train_without_lya",train)):
        fits = {}
        baseline = None
        for name in BOUNDS:
            fitted, report = fit_profile(sample,name,seeds=seeds,maxiter=maxiter,
                                         null_om=None if baseline is None else baseline.om)
            if baseline is None:
                baseline = fitted
            elif report["chi2"] > sample.chi2(baseline)+1e-3:
                report["state"] = "OPTIMIZATION_UNCONFIRMED_NULL_DOMINATES"
            fits[name] = {**report,"parameters":vars(fitted),
                          "holdout_chi2": test.chi2(fitted) if label=="train_without_lya" else None}
        results[label]=fits
    return {"schema":"rll.background.scale_profile.v1","results":results,"claim_allowed":False,
            "scope":"BAO only, late time, no radiation, no independent H0 or rd inference",
            "holdout_policy":"same fixed parameters including scale; no refit on Ly-alpha",
            "excluded":"TOKEN_VAZIO_FULL_CMB_GROWTH_CC_SN_AND_NULL_MOCKS"}


if __name__ == "__main__":
    import argparse
    import json
    from pathlib import Path
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--maxiter",type=int,default=180)
    args=parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    result=run_desi(maxiter=args.maxiter)
    with args.output.open("x",encoding="utf-8") as handle:
        json.dump(result,handle,indent=2,allow_nan=False)
