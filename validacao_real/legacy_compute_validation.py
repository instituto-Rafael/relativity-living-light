#!/usr/bin/env python3
"""RLL vs LCDM real-data validation engine.

Region of validity: z in [0, 2.4] (where DESI DR2 + cosmic chronometers exist).
We do not compute the immensity; we mark the region where the ruler falls.

Physics
-------
E(z) = H(z)/H0.
  LCDM: E^2 = Om (1+z)^3 + Or (1+z)^4 + OL
  RLL : E^2 = Om (1+z)^3 + Or (1+z)^4 + OL + Os [ f(z) + (1-f(z))(1+z)^3 ]
        f(z) = 1 / (1 + exp((z - zt)/wt))   (logistic transition, README canonical)
  OL renormalized so E(0)=1 exactly in both models.

BAO observables (dimensionless, divided by r_d):
  DH/rd = c / (H(z) r_d)
  DM/rd = (c/H0) * integral_0^z dz'/E(z')  / r_d
  DV/rd = [ z * DM^2 * DH ]^(1/3) / r_d

Scoring: chi2 (diagonal), AIC = 2k + chi2, BIC = k ln(n) + chi2.
Falsifiability: per-point pull = (model-obs)/sigma; a model is rejected in a
regime if the mean |pull| there exceeds REJECT_SIGMA.

Stdlib only. No numpy, scipy, pandas.
"""

from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
FETCHED = HERE / "fetched"
RESULTS = HERE / "results"

C_KM_S = 299792.458
RD_MPC = 147.09          # sound horizon at drag epoch (Planck-consistent)
REJECT_SIGMA = 3.0       # falsifiability threshold on mean |pull|


@dataclass(frozen=True)
class Cosmo:
    name: str
    H0: float
    Om: float
    Or: float
    Os: float = 0.0       # superposition sector amplitude (RLL only)
    zt: float = 1.0       # logistic transition redshift
    wt: float = 0.3       # logistic width
    k_params: int = 3     # free parameters for AIC/BIC


def _OL(c: Cosmo) -> float:
    """Renormalize OL so E(0)=1. At z=0, f=~1 so the Os bracket contributes Os."""
    f0 = 1.0 / (1.0 + math.exp((0.0 - c.zt) / c.wt))
    os_term0 = c.Os * (f0 + (1.0 - f0) * 1.0)
    return 1.0 - c.Om - c.Or - os_term0


def E(c: Cosmo, z: float) -> float:
    a3 = (1.0 + z) ** 3
    a4 = (1.0 + z) ** 4
    base = c.Om * a3 + c.Or * a4 + _OL(c)
    if c.Os != 0.0:
        f = 1.0 / (1.0 + math.exp((z - c.zt) / c.wt))
        base += c.Os * (f + (1.0 - f) * a3)
    return math.sqrt(base)


def H(c: Cosmo, z: float) -> float:
    return c.H0 * E(c, z)


def _simpson(fn, a: float, b: float, n: int = 512) -> float:
    if b <= a:
        return 0.0
    if n % 2:
        n += 1
    h = (b - a) / n
    s = fn(a) + fn(b)
    for i in range(1, n):
        s += (4 if i % 2 else 2) * fn(a + i * h)
    return s * h / 3.0


def DM_over_rd(c: Cosmo, z: float) -> float:
    dc = (C_KM_S / c.H0) * _simpson(lambda zp: 1.0 / E(c, zp), 0.0, z)
    return dc / RD_MPC


def DH_over_rd(c: Cosmo, z: float) -> float:
    return (C_KM_S / H(c, z)) / RD_MPC


def DV_over_rd(c: Cosmo, z: float) -> float:
    dm = DM_over_rd(c, z) * RD_MPC
    dh = DH_over_rd(c, z) * RD_MPC
    dv = (z * dm * dm * dh) ** (1.0 / 3.0)
    return dv / RD_MPC


def model_bao(c: Cosmo, z: float, observable: str) -> float:
    if observable == "DM_over_rd":
        return DM_over_rd(c, z)
    if observable == "DH_over_rd":
        return DH_over_rd(c, z)
    if observable == "DV_over_rd":
        return DV_over_rd(c, z)
    raise ValueError(f"unknown observable: {observable}")


def load_points(path: Path) -> list[dict]:
    return yaml.safe_load(path.read_text(encoding="utf-8")).get("points", [])


def evaluate(models: dict[str, Cosmo]) -> dict:
    bao = load_points(FETCHED / "desi_dr2_bao.yml")
    hz = load_points(FETCHED / "hz_cosmic_chronometers.yml")

    rows = []
    chi2 = {m: {"bao": 0.0, "hz": 0.0} for m in models}
    pulls = {m: {"bao": [], "hz": []} for m in models}

    for p in bao:
        z, obs, val, sig = p["z_eff"], p["observable"], p["value"], p["sigma"]
        row = {"dataset": "DESI_DR2_BAO", "tracer": p.get("tracer", ""), "z": z,
               "observable": obs, "obs_value": val, "sigma": sig}
        for m, c in models.items():
            pred = model_bao(c, z, obs)
            pull = (pred - val) / sig
            chi2[m]["bao"] += pull * pull
            pulls[m]["bao"].append(abs(pull))
            row[f"pred_{m}"] = round(pred, 5)
            row[f"pull_{m}"] = round(pull, 4)
        rows.append(row)

    for p in hz:
        z, val, sig = p["z"], p["H"], p["sigma"]
        row = {"dataset": "Hz_CC", "tracer": "", "z": z,
               "observable": "H_z", "obs_value": val, "sigma": sig}
        for m, c in models.items():
            pred = H(c, z)
            pull = (pred - val) / sig
            chi2[m]["hz"] += pull * pull
            pulls[m]["hz"].append(abs(pull))
            row[f"pred_{m}"] = round(pred, 4)
            row[f"pull_{m}"] = round(pull, 4)
        rows.append(row)

    n = len(bao) + len(hz)
    summary = {}
    for m, c in models.items():
        total = chi2[m]["bao"] + chi2[m]["hz"]
        k = c.k_params
        mean_pull_bao = sum(pulls[m]["bao"]) / len(pulls[m]["bao"])
        mean_pull_hz = sum(pulls[m]["hz"]) / len(pulls[m]["hz"])
        summary[m] = {
            "params": asdict(c),
            "chi2_bao": round(chi2[m]["bao"], 4),
            "chi2_hz": round(chi2[m]["hz"], 4),
            "chi2_total": round(total, 4),
            "n_points": n,
            "k_params": k,
            "chi2_per_dof": round(total / max(n - k, 1), 4),
            "aic": round(2 * k + total, 4),
            "bic": round(k * math.log(n) + total, 4),
            "mean_abs_pull_bao": round(mean_pull_bao, 4),
            "mean_abs_pull_hz": round(mean_pull_hz, 4),
            "falsified_bao": mean_pull_bao > REJECT_SIGMA,
            "falsified_hz": mean_pull_hz > REJECT_SIGMA,
        }

    names = list(models)
    if len(names) == 2:
        a, b = names
        d_chi2 = summary[a]["chi2_total"] - summary[b]["chi2_total"]
        d_aic = summary[a]["aic"] - summary[b]["aic"]
        d_bic = summary[a]["bic"] - summary[b]["bic"]
        verdict = {
            "compared": f"{a} - {b}",
            "delta_chi2": round(d_chi2, 4),
            "delta_aic": round(d_aic, 4),
            "delta_bic": round(d_bic, 4),
            "preferred_by_aic": a if d_aic < 0 else b,
            "preferred_by_bic": a if d_bic < 0 else b,
            "reject_sigma": REJECT_SIGMA,
        }
    else:
        verdict = {}

    return {
        "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "region_of_validity": {"z_min": 0.0, "z_max": 2.4},
        "constants": {"c_km_s": C_KM_S, "rd_mpc": RD_MPC},
        "summary": summary,
        "verdict": verdict,
        "rows": rows,
    }


def write_artifacts(result: dict) -> None:
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "validation_summary.json").write_text(json.dumps(
        {k: v for k, v in result.items() if k != "rows"}, indent=2), encoding="utf-8")

    rows = result["rows"]
    fields = ["dataset", "tracer", "z", "observable", "obs_value", "sigma"]
    for m in result["summary"]:
        fields += [f"pred_{m}", f"pull_{m}"]
    with (RESULTS / "per_point_predictions.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})

    with (RESULTS / "model_comparison.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["model", "chi2_total", "chi2_per_dof", "aic", "bic",
                    "mean_abs_pull_bao", "mean_abs_pull_hz", "falsified_bao", "falsified_hz"])
        for m, s in result["summary"].items():
            w.writerow([m, s["chi2_total"], s["chi2_per_dof"], s["aic"], s["bic"],
                        s["mean_abs_pull_bao"], s["mean_abs_pull_hz"],
                        s["falsified_bao"], s["falsified_hz"]])


def main() -> int:
    models = {
        "LCDM": Cosmo(name="LCDM", H0=67.4, Om=0.315, Or=9.2e-5, k_params=3),
        "RLL": Cosmo(name="RLL", H0=67.4, Om=0.315, Or=9.2e-5, Os=0.02, zt=1.0, wt=0.3, k_params=5),
    }
    result = evaluate(models)
    write_artifacts(result)

    print("=== RLL vs LCDM — real-data validation ===")
    for m, s in result["summary"].items():
        print(f"[{m}] chi2={s['chi2_total']:.2f}  chi2/dof={s['chi2_per_dof']:.3f}  "
              f"AIC={s['aic']:.2f}  BIC={s['bic']:.2f}  "
              f"falsified(bao/hz)={s['falsified_bao']}/{s['falsified_hz']}")
    v = result["verdict"]
    if v:
        print(f"\nDelta chi2 ({v['compared']}) = {v['delta_chi2']:.2f}")
        print(f"Preferred by AIC: {v['preferred_by_aic']} | by BIC: {v['preferred_by_bic']}")
    print(f"\nartifacts -> {RESULTS.relative_to(HERE)}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
