#!/usr/bin/env python3
"""Pure-stdlib RLL vs LCDM fit for real H(z)+DESI DR2 BAO.

No third-party imports. No user-defined functions.
Additive route: does not replace the SciPy joint pipeline.
"""

import csv
import json
import math
import os
import random
import subprocess
import time
from pathlib import Path

t0 = time.perf_counter()
root = Path(__file__).resolve().parents[1]
results = Path(__file__).resolve().parent / "results"
results.mkdir(parents=True, exist_ok=True)

hz_path = root / "data" / "real" / "cosmology" / "Hz_cosmic_chronometers_independent.csv"
bao_path = root / "data" / "real" / "cosmology" / "desi_dr2_bao_primary_points.csv"
cov_path = root / "data" / "real" / "desi_dr2_bao_covariance.csv"

stem = os.environ.get("RLL_STDLIB_OUTPUT_STEM", "rll_lcdm_hz_bao_stdlib_v1").strip()
if not stem or "/" in stem or "\\" in stem or stem.endswith((".json", ".csv")):
    raise SystemExit("unsafe RLL_STDLIB_OUTPUT_STEM")

seed = int(os.environ.get("RLL_STDLIB_SEED", "1"))
maxiter = max(1, int(os.environ.get("RLL_STDLIB_MAXITER", "12")))
nint = max(32, int(os.environ.get("RLL_STDLIB_SIMPSON", "128")))
if nint % 2:
    nint += 1

C = 299792.458
OR = 9.0e-5

hz = []
with hz_path.open("r", encoding="utf-8", newline="") as f:
    for r in csv.DictReader(f):
        hz.append((float(r["z"]), float(r["H_obs"]), float(r["sigma_H"])))

bao = []
with bao_path.open("r", encoding="utf-8", newline="") as f:
    for r in csv.DictReader(f):
        bao.append((float(r["z_eff"]), r["observable"], float(r["value"])))

cov = []
with cov_path.open("r", encoding="utf-8", newline="") as f:
    rr = csv.reader(f)
    next(rr)
    for r in rr:
        cov.append([float(x) for x in r[1:]])

n = len(cov)
if n != len(bao) or any(len(r) != n for r in cov):
    raise SystemExit("DESI covariance shape mismatch")

aug = []
for i in range(n):
    aug.append(cov[i][:] + [1.0 if i == j else 0.0 for j in range(n)])
for col in range(n):
    piv = col
    for r in range(col + 1, n):
        if abs(aug[r][col]) > abs(aug[piv][col]):
            piv = r
    if abs(aug[piv][col]) < 1e-30:
        raise SystemExit("singular DESI covariance")
    if piv != col:
        aug[col], aug[piv] = aug[piv], aug[col]
    p = aug[col][col]
    for j in range(2 * n):
        aug[col][j] /= p
    for r in range(n):
        if r == col:
            continue
        q = aug[r][col]
        if q:
            for j in range(2 * n):
                aug[r][j] -= q * aug[col][j]
cov_inv = [r[n:] for r in aug]

models = ["LCDM", "RLL"]
bounds = {
    "LCDM": [(55.0, 85.0), (0.10, 0.60), (0.018, 0.026)],
    "RLL": [(55.0, 85.0), (0.10, 0.60), (0.0, 0.25), (0.1, 10.0), (0.05, 2.0), (0.018, 0.026)],
}
names = {
    "LCDM": ["H0", "Om", "Ob_h2"],
    "RLL": ["H0", "Om", "Os0", "zt", "wt", "Ob_h2"],
}

fits = {}
lcdm_best = None

for mi, model in enumerate(models):
    if model == "LCDM":
        best = [67.4, 0.315, 0.02236]
    else:
        best = [lcdm_best[0], lcdm_best[1], 0.0, 1.0, 0.3, lcdm_best[2]]

    bb = bounds[model]
    step = [(hi - lo) * 0.12 for lo, hi in bb]
    rng = random.Random(seed + mi)
    best_chi2 = float("inf")
    best_parts = None

    for outer in range(maxiter + 1):
        candidates = [best[:]] if outer == 0 else []
        if outer:
            for pi in range(len(best)):
                for sign in (-1.0, 1.0):
                    x = best[:]
                    x[pi] += sign * step[pi]
                    lo, hi = bb[pi]
                    x[pi] = max(lo, min(hi, x[pi]))
                    candidates.append(x)
            if outer <= 3:
                candidates.append([lo + (hi - lo) * rng.random() for lo, hi in bb])

        improved = False
        for x in candidates:
            if model == "LCDM":
                H0, Om, Ob = x
                Os0, zt, wt = 0.0, 1.0, 0.3
            else:
                H0, Om, Os0, zt, wt, Ob = x

            OL = 1.0 - OR - Om - Os0
            if OL <= 0.0:
                continue

            omh2 = Om * (H0 / 100.0) ** 2
            if omh2 <= 0.0 or Ob <= 0.0:
                continue
            rd = 147.78 * (omh2 / 0.1432) ** (-0.255) * (Ob / 0.02236) ** (-0.134)

            chi_hz = 0.0
            bad = False
            for z, obs, sig in hz:
                zp1 = 1.0 + z
                if model == "LCDM":
                    e2 = Om * zp1**3 + OR * zp1**4 + OL
                else:
                    u = max(-500.0, min(500.0, (z - zt) / max(wt, 1e-12)))
                    fz = 1.0 / (1.0 + math.exp(u))
                    e2 = Om * zp1**3 + OR * zp1**4 + OL + Os0 * (fz + (1.0 - fz) * zp1**3)
                if e2 <= 0.0:
                    bad = True
                    break
                pred = H0 * math.sqrt(e2)
                chi_hz += ((pred - obs) / sig) ** 2
            if bad:
                continue

            dcache = {}
            for z, observable, obs in bao:
                if z in dcache:
                    continue
                xmax = math.log1p(z)
                h = xmax / nint
                s = 0.0
                for ii in range(nint + 1):
                    xx = ii * h
                    zz = math.exp(xx) - 1.0
                    zp1 = 1.0 + zz
                    if model == "LCDM":
                        e2 = Om * zp1**3 + OR * zp1**4 + OL
                    else:
                        u = max(-500.0, min(500.0, (zz - zt) / max(wt, 1e-12)))
                        fz = 1.0 / (1.0 + math.exp(u))
                        e2 = Om * zp1**3 + OR * zp1**4 + OL + Os0 * (fz + (1.0 - fz) * zp1**3)
                    if e2 <= 0.0:
                        bad = True
                        break
                    wgt = 1.0 if ii in (0, nint) else (4.0 if ii % 2 else 2.0)
                    s += wgt * math.exp(xx) / math.sqrt(e2)
                if bad:
                    break
                dcache[z] = (C / H0) * h * s / 3.0
            if bad:
                continue

            res = []
            for z, observable, obs in bao:
                zp1 = 1.0 + z
                if model == "LCDM":
                    e2 = Om * zp1**3 + OR * zp1**4 + OL
                else:
                    u = max(-500.0, min(500.0, (z - zt) / max(wt, 1e-12)))
                    fz = 1.0 / (1.0 + math.exp(u))
                    e2 = Om * zp1**3 + OR * zp1**4 + OL + Os0 * (fz + (1.0 - fz) * zp1**3)
                Hz = H0 * math.sqrt(e2)
                DM = dcache[z]
                if observable == "DM_over_rd":
                    pred = DM / rd
                elif observable == "DH_over_rd":
                    pred = (C / Hz) / rd
                elif observable == "DV_over_rd":
                    pred = (z * C * DM * DM / Hz) ** (1.0 / 3.0) / rd
                else:
                    bad = True
                    break
                res.append(obs - pred)
            if bad:
                continue

            chi_bao = 0.0
            for i in range(n):
                for j in range(n):
                    chi_bao += res[i] * cov_inv[i][j] * res[j]

            chi2 = chi_hz + chi_bao
            if math.isfinite(chi2) and chi2 < best_chi2:
                best = x[:]
                best_chi2 = chi2
                best_parts = {"Hz": chi_hz, "DESI_DR2_BAO": chi_bao}
                improved = True

        if outer:
            decay = 0.72 if improved else 0.50
            step = [max((hi - lo) * 1e-5, s * decay) for s, (lo, hi) in zip(step, bb)]

    fits[model] = {"vector": best, "chi2": best_chi2, "parts": best_parts}
    if model == "LCDM":
        lcdm_best = best[:]

N = len(hz) + len(bao)
rows = []
for model in models:
    x = fits[model]["vector"]
    chi2 = fits[model]["chi2"]
    k = len(x)
    AIC = chi2 + 2 * k
    BIC = chi2 + k * math.log(N)
    AICc = AIC + (2 * k * (k + 1)) / (N - k - 1) if N > k + 1 else None
    row = {
        "model": model,
        "chi2": chi2,
        "chi2_Hz": fits[model]["parts"]["Hz"],
        "chi2_DESI_DR2_BAO": fits[model]["parts"]["DESI_DR2_BAO"],
        "N": N,
        "k": k,
        "dof": N - k,
        "AIC": AIC,
        "AICc": AICc,
        "BIC": BIC,
    }
    for i, p in enumerate(names[model]):
        row[p] = x[i]
    rows.append(row)

nested_ok = rows[1]["chi2"] <= rows[0]["chi2"] + 1e-8

try:
    git_sha = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=root, text=True, stderr=subprocess.DEVNULL
    ).strip()
except Exception:
    git_sha = "TOKEN_VAZIO"

payload = {
    "schema": "rll.hz_bao.stdlib.v1",
    "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "runtime_seconds": time.perf_counter() - t0,
    "runtime": {
        "third_party_dependencies": [],
        "user_defined_functions": 0,
        "optimizer": "bounded coordinate search with seeded stdlib random probes",
        "seed": seed,
        "maxiter": maxiter,
        "simpson_steps": nint,
    },
    "datasets": {
        "Hz": str(hz_path.relative_to(root)),
        "DESI_DR2_BAO": str(bao_path.relative_to(root)),
        "DESI_covariance": str(cov_path.relative_to(root)),
    },
    "rows": rows,
    "nested_limit": {
        "relation": "RLL(Os0=0) -> LCDM-like background",
        "pass": nested_ok,
    },
    "claim_allowed": False,
    "model_selection_claim_allowed": False,
    "claim_boundary": [
        "stdlib-only route for reproducibility on minimal Python environments",
        "Hz uses diagonal uncertainties; DESI BAO uses the committed full covariance",
        "coordinate search is not a proof of global convergence or a posterior",
        "this route covers H(z)+BAO only, not the full Structure-D multiprobe stack",
    ],
    "git_commit": git_sha,
}

csv_out = results / (stem + ".csv")
json_out = results / (stem + ".json")
fields = []
for row in rows:
    for key in row:
        if key not in fields:
            fields.append(key)
with csv_out.open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    for row in rows:
        w.writerow(row)
with json_out.open("w", encoding="utf-8") as f:
    json.dump(payload, f, ensure_ascii=False, indent=2, allow_nan=False)
    f.write("\n")

print("=== RLL vs LCDM — stdlib-only H(z)+DESI DR2 BAO ===")
print("dependencies=0 third_party | user_defined_functions=0")
for row in rows:
    print(row["model"], "chi2=%.6f" % row["chi2"], "AIC=%.6f" % row["AIC"], "BIC=%.6f" % row["BIC"])
print("nested_limit_pass=", nested_ok)
print("claim_allowed=False")
print("wrote", csv_out.relative_to(root))
print("wrote", json_out.relative_to(root))
