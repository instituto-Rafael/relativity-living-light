"""Public literature fixed-parameter H(z) screen; no joint-dataset mutation."""
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if not __package__:
    sys.path.insert(0, str(ROOT))

from rx import cosmology
CONTRACT = ROOT / "data/contracts/rll_literature_cc_loubser.v1.json"
VARIANTS = ("reported_total_correlation", "systematic_only_sensitivity", "diagonal_diagnostic")


def covariance(rows, rho, variant):
    if variant not in VARIANTS or len(rows) != 3 or len(rho) != 3 or any(len(r) != 3 for r in rho):
        raise ValueError("INVALID_SHAPE_OR_VARIANT")
    stat = [r["stat"] for r in rows]
    syst = [r["syst"] for r in rows]
    if any(not math.isfinite(x) or x <= 0 for x in stat+syst):
        raise ValueError("INVALID_UNCERTAINTY")
    for i in range(3):
        for j in range(3):
            if (not math.isfinite(rho[i][j]) or abs(rho[i][j]) > 1
                    or rho[i][j] != rho[j][i] or (i == j and rho[i][j] != 1)):
                raise ValueError("INVALID_CORRELATION")
    total = [math.hypot(a,b) for a,b in zip(stat,syst)]
    if variant == VARIANTS[0]:
        return [[rho[i][j]*total[i]*total[j] for j in range(3)] for i in range(3)]
    if variant == VARIANTS[1]:
        return [[rho[i][j]*syst[i]*syst[j]+(stat[i]**2 if i==j else 0) for j in range(3)] for i in range(3)]
    return [[total[i]**2 if i==j else 0 for j in range(3)] for i in range(3)]


def chi2(residual, cov):
    # Cholesky whitening: no inverse and reject nonpositive pivots.
    n = len(residual)
    if n not in (2, 3) or len(cov) != n or any(len(r) != n for r in cov):
        raise ValueError("INVALID_COVARIANCE_SHAPE")
    if any(not math.isfinite(x) for x in residual):
        raise ValueError("NONFINITE_RESIDUAL")
    lower = [[0.0]*n for _ in range(n)]
    for i in range(n):
        for j in range(i+1):
            if not math.isfinite(cov[i][j]) or not math.isclose(cov[i][j],cov[j][i],rel_tol=1e-12,abs_tol=1e-12):
                raise ValueError("INVALID_COVARIANCE")
            v = cov[i][j]-math.fsum(lower[i][k]*lower[j][k] for k in range(j))
            if i == j:
                if v <= 0 or not math.isfinite(v):
                    raise ValueError("COVARIANCE_NOT_SPD")
                lower[i][j] = math.sqrt(v)
            else:
                lower[i][j] = v/lower[j][j]
    x = []
    for i in range(n):
        x.append((residual[i]-math.fsum(lower[i][j]*x[j] for j in range(i)))/lower[i][i])
    value = math.fsum(v*v for v in x)
    if not math.isfinite(value):
        raise ValueError("NONFINITE_CHI2")
    return value


def leave_one_out(zs, residuals, covs):
    """Diagnostic influence screen; recompute the marginal covariance, no refit."""
    if len(zs) != 3 or set(residuals) != {"LCDM", "RLL_PROBE"} or any(len(r) != 3 for r in residuals.values()):
        raise ValueError("INVALID_INFLUENCE_INPUT")
    out = {}
    for name, cov in covs.items():
        full = chi2(residuals["RLL_PROBE"], cov) - chi2(residuals["LCDM"], cov)
        rows = []
        for excluded in range(3):
            kept = [i for i in range(3) if i != excluded]
            marginal = [[cov[i][j] for j in kept] for i in kept]
            scores = {m: chi2([r[i] for i in kept], marginal) for m, r in residuals.items()}
            delta = scores["RLL_PROBE"] - scores["LCDM"]
            rows.append(dict(excluded_z=zs[excluded], chi2=scores, delta_chi2=delta,
                             sign_reversal=(full < 0 < delta or delta < 0 < full)))
        out[name] = dict(full_delta_chi2=full, omissions=rows,
                         sign_robust=not any(r["sign_reversal"] for r in rows))
    return out


def build():
    c = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if (c.get("schema") != "rll.literature_cc_covariance_screen.v1"
            or c.get("claim_allowed") is not False or c.get("promotion_allowed") is not False
            or c.get("unit") != "km s^-1 Mpc^-1" or c.get("covariance_variants") != list(VARIANTS)
            or c.get("joint_ingestion") != "BLOCKED_OVERLAP_AND_COVARIANCE_NOT_VERIFIED"):
        raise ValueError("CONTRACT_DRIFT")
    model_bytes = Path(cosmology.__file__).read_bytes()
    model_blob = hashlib.sha1(b"blob " + str(len(model_bytes)).encode("ascii") + b"\0" + model_bytes).hexdigest()
    if c["model_source"]["blob"] != model_blob:
        raise ValueError("MODEL_SOURCE_BLOB_DRIFT")
    rows = c["rows"]
    zs = [r["z"] for r in rows]
    if len(rows)!=3 or zs!=sorted(set(zs)) or any(not math.isfinite(r[k]) or r[k]<=0 for r in rows for k in ("z","h")):
        raise ValueError("INVALID_MEASUREMENT")
    covs = {v:covariance(rows,c["correlation"],v) for v in VARIANTS}
    models = c["model_source"]["models"]
    prior = cosmology.ORAD
    results = {}
    try:
        cosmology.ORAD = c["model_source"]["omega_r"]
        for name in ("LCDM","RLL_NULL","RLL_PROBE"):
            pred = [cosmology.hubble("LCDM" if name=="LCDM" else "RLL",z,models[name]) for z in zs]
            if any(not math.isfinite(x) or x<=0 for x in pred):
                raise ValueError("INVALID_MODEL")
            residual = [r["h"]-x for r,x in zip(rows,pred)]
            results[name] = dict(h=pred, residual=residual, chi2={v:chi2(residual,cov) for v,cov in covs.items()})
    finally:
        cosmology.ORAD = prior
    if any(not math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-12) for a,b in zip(results["LCDM"]["h"],results["RLL_NULL"]["h"])):
        raise ValueError("NULL_EQUIVALENCE_FAIL")
    influence = leave_one_out(zs, {m: results[m]["residual"] for m in ("LCDM", "RLL_PROBE")}, covs)
    return dict(schema="rll.literature_cc_covariance_receipt.v1",claim_allowed=False,
                promotion_allowed=False,model_selection="NOT_RUN",joint_ingestion=c["joint_ingestion"],
                source=c["source"],contract_sha256=hashlib.sha256(CONTRACT.read_bytes()).hexdigest(),
                model_source_sha256=hashlib.sha256(model_bytes).hexdigest(), model_source_git_blob=model_blob,
                covariance=covs,results=results, leave_one_out=influence,
                influence_boundary="EXPLORATORY_NO_REFIT_NO_MODEL_SELECTION")


if __name__ == "__main__":
    print(json.dumps(build(),indent=2,allow_nan=False))
