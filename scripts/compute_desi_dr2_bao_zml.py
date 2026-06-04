#!/usr/bin/env python3
"""Compute DESI DR2 Gaussian BAO real-data comparison for RLL vs LCDM.

Input files:
- data/real/desi_dr2_bao_measurements.csv
- data/real/desi_dr2_bao_covariance.csv

Outputs:
- data/results/desi_dr2_bao_model_comparison.json
- data/results/desi_dr2_bao_per_point_predictions.csv
- data/results/desi_dr2_bao_zml.yml

Policy: no synthetic fill. The calculation uses the materialized DESI DR2
Gaussian BAO vector and covariance already stored in data/real/.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MEASUREMENTS = ROOT / "data" / "real" / "desi_dr2_bao_measurements.csv"
COVARIANCE = ROOT / "data" / "real" / "desi_dr2_bao_covariance.csv"
OUT_JSON = ROOT / "data" / "results" / "desi_dr2_bao_model_comparison.json"
OUT_POINTS = ROOT / "data" / "results" / "desi_dr2_bao_per_point_predictions.csv"
OUT_ZML = ROOT / "data" / "results" / "desi_dr2_bao_zml.yml"

C_KM_S = 299792.458
RD_MPC = 147.09
CLAIM_BOUNDARY = "No superiority claim unless real-data metrics pass predefined thresholds."


@dataclass(frozen=True)
class Cosmo:
    name: str
    H0: float
    Om: float
    Or: float
    Os: float = 0.0
    zt: float = 1.0
    wt: float = 0.3
    k_params: int = 3


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_commit() -> str | None:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        return None


def ol(c: Cosmo) -> float:
    f0 = 1.0 / (1.0 + math.exp((0.0 - c.zt) / c.wt))
    os_term0 = c.Os * (f0 + (1.0 - f0))
    return 1.0 - c.Om - c.Or - os_term0


def ez(c: Cosmo, z: float) -> float:
    a3 = (1.0 + z) ** 3
    a4 = (1.0 + z) ** 4
    base = c.Om * a3 + c.Or * a4 + ol(c)
    if c.Os != 0.0:
        f = 1.0 / (1.0 + math.exp((z - c.zt) / c.wt))
        base += c.Os * (f + (1.0 - f) * a3)
    return math.sqrt(base)


def hz(c: Cosmo, z: float) -> float:
    return c.H0 * ez(c, z)


def simpson(fn, a: float, b: float, n: int = 1024) -> float:
    if b <= a:
        return 0.0
    if n % 2:
        n += 1
    h = (b - a) / n
    s = fn(a) + fn(b)
    for i in range(1, n):
        s += (4 if i % 2 else 2) * fn(a + i * h)
    return s * h / 3.0


def dm_over_rd(c: Cosmo, z: float) -> float:
    dc = (C_KM_S / c.H0) * simpson(lambda zp: 1.0 / ez(c, zp), 0.0, z)
    return dc / RD_MPC


def dh_over_rd(c: Cosmo, z: float) -> float:
    return (C_KM_S / hz(c, z)) / RD_MPC


def dv_over_rd(c: Cosmo, z: float) -> float:
    dm = dm_over_rd(c, z) * RD_MPC
    dh = dh_over_rd(c, z) * RD_MPC
    return (z * dm * dm * dh) ** (1.0 / 3.0) / RD_MPC


def predict(c: Cosmo, z: float, observable: str) -> float:
    if observable == "DM_over_rd":
        return dm_over_rd(c, z)
    if observable == "DH_over_rd":
        return dh_over_rd(c, z)
    if observable == "DV_over_rd":
        return dv_over_rd(c, z)
    raise ValueError(f"unknown observable: {observable}")


def load_measurements() -> list[dict[str, object]]:
    with MEASUREMENTS.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    out = []
    for row in rows:
        out.append(
            {
                "index": int(row["index"]),
                "tracer": row["tracer"],
                "z_eff": float(row["z_eff"]),
                "observable": row["observable"],
                "value": float(row["value"]),
                "sigma": float(row["sigma"]),
            }
        )
    return out


def load_covariance() -> list[list[float]]:
    rows = []
    with COVARIANCE.open("r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            rows.append([float(x) for x in row[1:]])
    return rows


def invert_matrix(a: list[list[float]]) -> list[list[float]]:
    n = len(a)
    aug = [[float(a[i][j]) for j in range(n)] + [1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(aug[r][col]))
        if abs(aug[pivot][col]) < 1e-15:
            raise ValueError("singular covariance matrix")
        if pivot != col:
            aug[col], aug[pivot] = aug[pivot], aug[col]
        div = aug[col][col]
        aug[col] = [x / div for x in aug[col]]
        for r in range(n):
            if r == col:
                continue
            factor = aug[r][col]
            aug[r] = [aug[r][j] - factor * aug[col][j] for j in range(2 * n)]
    return [row[n:] for row in aug]


def chi2_full(residuals: list[float], inv_cov: list[list[float]]) -> float:
    n = len(residuals)
    return sum(residuals[i] * inv_cov[i][j] * residuals[j] for i in range(n) for j in range(n))


def interpretation(delta_aic: float, delta_bic: float, delta_chi2: float) -> str:
    if delta_aic > 0 or delta_bic > 0:
        return "lcdm_preferred_for_this_desi_dr2_bao_setup"
    if delta_aic <= -6 and delta_bic <= -6 and delta_chi2 < 0:
        return "rll_preferred_strong_for_this_desi_dr2_bao_setup"
    if delta_aic <= -2 and delta_bic <= -2:
        return "rll_preferred_tentative_for_this_desi_dr2_bao_setup"
    return "inconclusive_for_this_desi_dr2_bao_setup"


def main() -> int:
    measurements = load_measurements()
    cov = load_covariance()
    inv_cov = invert_matrix(cov)
    models = {
        "LCDM": Cosmo(name="LCDM", H0=67.4, Om=0.315, Or=9.2e-5, k_params=3),
        "RLL": Cosmo(name="RLL", H0=67.4, Om=0.315, Or=9.2e-5, Os=0.02, zt=1.0, wt=0.3, k_params=5),
    }

    per_point: list[dict[str, object]] = []
    summary: dict[str, dict[str, object]] = {}
    n = len(measurements)

    for name, model in models.items():
        residuals: list[float] = []
        abs_pulls: list[float] = []
        preds: list[float] = []
        for row in measurements:
            pred = predict(model, float(row["z_eff"]), str(row["observable"]))
            resid = pred - float(row["value"])
            residuals.append(resid)
            preds.append(pred)
            abs_pulls.append(abs(resid / float(row["sigma"])))
        chi2 = chi2_full(residuals, inv_cov)
        k = model.k_params
        summary[name] = {
            "params": asdict(model),
            "n_obs": n,
            "k_params": k,
            "chi2": round(chi2, 8),
            "chi2_per_dof": round(chi2 / max(n - k, 1), 8),
            "AIC": round(chi2 + 2 * k, 8),
            "BIC": round(chi2 + k * math.log(n), 8),
            "mean_abs_pull_diagonal_sigma": round(sum(abs_pulls) / len(abs_pulls), 8),
        }
        for i, row in enumerate(measurements):
            if name == "LCDM":
                per_point.append(dict(row))
            per_point[i][f"pred_{name}"] = round(preds[i], 10)
            per_point[i][f"residual_{name}"] = round(residuals[i], 10)
            per_point[i][f"pull_diag_{name}"] = round(residuals[i] / float(row["sigma"]), 8)

    delta = {
        "delta_chi2_rll_minus_lcdm": round(float(summary["RLL"]["chi2"]) - float(summary["LCDM"]["chi2"]), 8),
        "delta_aic_rll_minus_lcdm": round(float(summary["RLL"]["AIC"]) - float(summary["LCDM"]["AIC"]), 8),
        "delta_bic_rll_minus_lcdm": round(float(summary["RLL"]["BIC"]) - float(summary["LCDM"]["BIC"]), 8),
    }
    delta["interpretation_label"] = interpretation(delta["delta_aic_rll_minus_lcdm"], delta["delta_bic_rll_minus_lcdm"], delta["delta_chi2_rll_minus_lcdm"])

    payload = {
        "schema": "rll.desi_dr2_bao.model_comparison.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit_hash": git_commit(),
        "claim_boundary": CLAIM_BOUNDARY,
        "dataset": {
            "name": "DESI DR2 Gaussian BAO ALL_GCcomb",
            "n_obs": n,
            "measurement_file": str(MEASUREMENTS.relative_to(ROOT)),
            "covariance_file": str(COVARIANCE.relative_to(ROOT)),
            "measurement_sha256": sha256_file(MEASUREMENTS),
            "covariance_sha256": sha256_file(COVARIANCE),
            "covariance_used": "full_13x13_inverse_covariance",
        },
        "models": summary,
        "delta": delta,
        "publication_language": "RLL is a candidate effective dynamic-transition cosmology under real-data evaluation.",
        "note": "This file evaluates the present RLL parameterization against materialized DESI DR2 BAO data. It does not erase prior timestamped predictions; those must be compared separately against an authorship/timestamp manifest.",
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    with OUT_POINTS.open("w", encoding="utf-8", newline="") as f:
        fields = [
            "index", "tracer", "z_eff", "observable", "value", "sigma",
            "pred_LCDM", "residual_LCDM", "pull_diag_LCDM",
            "pred_RLL", "residual_RLL", "pull_diag_RLL",
        ]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in per_point:
            writer.writerow({k: row.get(k, "") for k in fields})

    zml_lines = [
        "zml:",
        "  schema: rll.desi_dr2_bao.zml.v1",
        f"  generated_at_utc: {payload['generated_at_utc']}",
        "  source: DESI_DR2_Gaussian_BAO_ALL_GCcomb",
        f"  n_obs: {n}",
        f"  covariance_used: full_13x13_inverse_covariance",
        "  observables:",
    ]
    for row in measurements:
        zml_lines.append(f"    - index: {row['index']}")
        zml_lines.append(f"      tracer: {row['tracer']}")
        zml_lines.append(f"      z_eff: {row['z_eff']}")
        zml_lines.append(f"      observable: {row['observable']}")
        zml_lines.append(f"      value: {row['value']}")
        zml_lines.append(f"      sigma: {row['sigma']}")
    zml_lines += [
        "  model_comparison:",
        f"    LCDM_chi2: {summary['LCDM']['chi2']}",
        f"    RLL_chi2: {summary['RLL']['chi2']}",
        f"    delta_chi2_rll_minus_lcdm: {delta['delta_chi2_rll_minus_lcdm']}",
        f"    delta_aic_rll_minus_lcdm: {delta['delta_aic_rll_minus_lcdm']}",
        f"    delta_bic_rll_minus_lcdm: {delta['delta_bic_rll_minus_lcdm']}",
        f"    interpretation_label: {delta['interpretation_label']}",
        f"  claim_boundary: {CLAIM_BOUNDARY}",
    ]
    OUT_ZML.write_text("\n".join(zml_lines) + "\n", encoding="utf-8")

    print(json.dumps({"wrote": [str(OUT_JSON.relative_to(ROOT)), str(OUT_POINTS.relative_to(ROOT)), str(OUT_ZML.relative_to(ROOT))], "delta": delta}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
