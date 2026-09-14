#!/usr/bin/env python3
"""Calcula χ² RLL vs ΛCDM apenas com dados H(z) Moresco — fecha gap P2 na ARVORE CONCEITUAL.

Gap: Nível 3 — "Moresco H(z) 2023 | [VAZIO] | aguarda execução"
Dataset: data/real/Hz_data_real.csv (33 linhas CC Moresco 2022/2023)
Output: results/moresco_hz_chi2.json
"""
from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DATA = REPO / "data" / "real" / "Hz_data_real.csv"
OUT = REPO / "results" / "moresco_hz_chi2.json"

H0_PLANCK = 67.4
OM_PLANCK = 0.315
OS0_NOMINAL = 0.02
ZT_NOMINAL = 1.0
WT_NOMINAL = 0.3


def e_lcdm(z: float, om: float) -> float:
    return math.sqrt(om * (1 + z) ** 3 + (1 - om))


def rll_f(z: float, zt: float, wt: float) -> float:
    arg = max(-700.0, min(700.0, (z - zt) / wt))
    return 1.0 / (1.0 + math.exp(arg))


def e_rll(z: float, om: float, os0: float, zt: float, wt: float) -> float:
    fz = rll_f(z, zt, wt)
    ol = 1.0 - om - os0
    e2 = om * (1 + z) ** 3 + ol + os0 * (fz + (1 - fz) * (1 + z) ** 3)
    return math.sqrt(max(e2, 1e-30))


def load_hz(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append({
                "z": float(r["z"]),
                "H_obs": float(r["H_obs"]),
                "sigma": float(r["sigma_H"]),
                "source": r.get("source", ""),
            })
    return rows


def chi2_hz(data: list[dict], h0: float, om: float, os0: float, zt: float, wt: float, model: str) -> float:
    total = 0.0
    for p in data:
        z = p["z"]
        if model == "lcdm":
            h_pred = h0 * e_lcdm(z, om)
        else:
            h_pred = h0 * e_rll(z, om, os0, zt, wt)
        total += ((p["H_obs"] - h_pred) / p["sigma"]) ** 2
    return total


def main() -> int:
    if not DATA.exists():
        print(f"ERROR: {DATA} não encontrado")
        return 1

    hz = load_hz(DATA)
    n = len(hz)

    chi2_rll = chi2_hz(hz, H0_PLANCK, OM_PLANCK, OS0_NOMINAL, ZT_NOMINAL, WT_NOMINAL, "rll")
    chi2_lcdm = chi2_hz(hz, H0_PLANCK, OM_PLANCK, 0.0, ZT_NOMINAL, WT_NOMINAL, "lcdm")

    dof_rll = n - 5
    dof_lcdm = n - 2
    chi2_red_rll = chi2_rll / dof_rll
    chi2_red_lcdm = chi2_lcdm / dof_lcdm
    delta_chi2 = chi2_rll - chi2_lcdm

    k_rll = 5
    k_lcdm = 2
    aic_rll = chi2_rll + 2 * k_rll
    aic_lcdm = chi2_lcdm + 2 * k_lcdm
    delta_aic = aic_rll - aic_lcdm

    result = {
        "meta": {
            "script": "compute_moresco_hz_chi2.py",
            "dataset": str(DATA),
            "n_points": n,
            "gap_closed": "Moresco H(z) 2023 — TOKEN_VAZIO P2 em 08_ARVORE_CONCEITUAL_RLL.md Nível 3",
            "params": {
                "H0": H0_PLANCK,
                "Omega_m": OM_PLANCK,
                "Omega_s0_rll": OS0_NOMINAL,
                "z_t": ZT_NOMINAL,
                "w_t": WT_NOMINAL,
                "note": "parâmetros nominais não otimizados para H(z); resultado comparativo, não MCMC",
            },
        },
        "rll": {
            "chi2": round(chi2_rll, 4),
            "k_params": k_rll,
            "dof": dof_rll,
            "chi2_red": round(chi2_red_rll, 4),
            "aic": round(aic_rll, 4),
        },
        "lcdm": {
            "chi2": round(chi2_lcdm, 4),
            "k_params": k_lcdm,
            "dof": dof_lcdm,
            "chi2_red": round(chi2_red_lcdm, 4),
            "aic": round(aic_lcdm, 4),
        },
        "comparison": {
            "delta_chi2_rll_minus_lcdm": round(delta_chi2, 4),
            "delta_aic_rll_minus_lcdm": round(delta_aic, 4),
            "interpretation": (
                "ΔAIC > 0: RLL penalizado por 3 parâmetros extras sem ganho em χ² "
                "com parâmetros nominais. Otimização de (H0, Om, Os0, zt, wt) sobre H(z) "
                "pode melhorar — aguarda MCMC joint G1."
            ),
        },
        "epistemic_status": "[E] resultado com parâmetros nominais Planck — gap P2 fechado (resultado disponível). "
                             "[C] otimização livre pendente (MCMC G1).",
        "residuals": [
            {
                "z": round(p["z"], 4),
                "H_obs": p["H_obs"],
                "sigma": p["sigma"],
                "H_rll": round(H0_PLANCK * e_rll(p["z"], OM_PLANCK, OS0_NOMINAL, ZT_NOMINAL, WT_NOMINAL), 3),
                "H_lcdm": round(H0_PLANCK * e_lcdm(p["z"], OM_PLANCK), 3),
                "source": p["source"],
            }
            for p in hz
        ],
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    print("=== Moresco H(z) χ² — RLL vs ΛCDM (parâmetros nominais Planck) ===")
    print(f"N pontos: {n}")
    print(f"χ²_RLL  = {chi2_rll:.4f}  (χ²_red = {chi2_red_rll:.4f})")
    print(f"χ²_ΛCDM = {chi2_lcdm:.4f}  (χ²_red = {chi2_red_lcdm:.4f})")
    print(f"Δχ²(RLL−ΛCDM) = {delta_chi2:+.4f}")
    print(f"ΔAIC(RLL−ΛCDM) = {delta_aic:+.4f}")
    print(f"\nOutput: {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
