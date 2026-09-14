#!/usr/bin/env python3
"""Parametrização coerente RLL — otimização joint sobre 3 datasets.

Modelo canônico (setor logístico):
  E²(z) = Ωm(1+z)³ + Ωr(1+z)⁴ + Ωs0·ρ_std(z) + ΩΛ
  ρ_std(z) = f(z) + (1-f(z))·(1+z)³
  f(z) = 1/(1+exp((z-z_t)/w_t))
  ΩΛ = 1 - Ωm - Ωr - Ωs0   [flat FLRW]

5 parâmetros livres: H₀, Ωm, Ωs0, z_t, w_t
Fixados: Ωr=9.18e-5 (T_CMB=2.7255 K), rd=147.09 Mpc (Planck 2018)

Datasets:
  1. Moresco H(z) — 33 pontos (CC, 2022)
  2. DESI DR2 BAO — 13 pontos (DM/rd, DH/rd, DV/rd) com covariância total
  3. Pantheon+SH0ES — 1624 SNe (M_B marginalizado analiticamente)

χ²_joint = χ²_Hz + χ²_BAO + χ²_SN

Output: results/rll_joint_parametrizacao.json
"""
from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path
from itertools import product

import numpy as np
from scipy.integrate import quad
from scipy.optimize import minimize

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "results" / "rll_joint_parametrizacao.json"

# ── Constantes ────────────────────────────────────────────────────────────────

C_KM = 299792.458      # c em km/s
C_MPC = C_KM           # para DH = c/H(z) em Mpc quando H em km/s/Mpc
OMEGA_R = 9.18e-5      # rad. + neutrinos, T_CMB=2.7255 K
RD_MPC = 147.09        # som. horizon [Mpc], Planck 2018 (fixo)

# grade de integração (evita quad repetido em cada avaliação)
_ZG = np.linspace(0.0, 3.5, 6000)

# ── Modelo RLL ────────────────────────────────────────────────────────────────

def rll_f(z: np.ndarray, zt: float, wt: float) -> np.ndarray:
    return 1.0 / (1.0 + np.exp((z - zt) / wt))


def rll_e2(z: np.ndarray, om: float, os0: float, zt: float, wt: float) -> np.ndarray:
    """E²(z) = H²(z)/H₀²."""
    f = rll_f(z, zt, wt)
    rho_std = os0 * (f + (1.0 - f) * (1.0 + z) ** 3)
    ol = 1.0 - om - OMEGA_R - os0
    return om * (1.0 + z) ** 3 + OMEGA_R * (1.0 + z) ** 4 + rho_std + ol


def _chi_comoving(z_arr: np.ndarray, om: float, os0: float, zt: float, wt: float) -> np.ndarray:
    """χ(z) = ∫₀ᶻ dz'/E(z') por trapézio numa grade comum, depois interpolado."""
    e = np.sqrt(np.maximum(rll_e2(_ZG, om, os0, zt, wt), 1e-30))
    inv_e = 1.0 / e
    cumint = np.concatenate(([0.0], np.cumsum(
        (inv_e[1:] + inv_e[:-1]) * 0.5 * np.diff(_ZG)
    )))
    return np.interp(z_arr, _ZG, cumint)


def d_L(z: np.ndarray, h0: float, om: float, os0: float, zt: float, wt: float) -> np.ndarray:
    """Distância de luminosidade [Mpc]."""
    chi = _chi_comoving(z, om, os0, zt, wt)
    return (C_KM / h0) * (1.0 + z) * chi


def dm_over_rd(z: np.ndarray, h0: float, om: float, os0: float, zt: float, wt: float) -> np.ndarray:
    chi = _chi_comoving(z, om, os0, zt, wt)
    return (C_KM / h0) * chi / RD_MPC


def dh_over_rd(z: np.ndarray, h0: float, om: float, os0: float, zt: float, wt: float) -> np.ndarray:
    e = np.sqrt(np.maximum(rll_e2(z, om, os0, zt, wt), 1e-30))
    return C_KM / (h0 * e * RD_MPC)


def dv_over_rd(z: np.ndarray, h0: float, om: float, os0: float, zt: float, wt: float) -> np.ndarray:
    dm = dm_over_rd(z, h0, om, os0, zt, wt) * RD_MPC   # DM em Mpc
    dh = dh_over_rd(z, h0, om, os0, zt, wt) * RD_MPC   # DH em Mpc
    dv = (z * dm ** 2 * dh) ** (1.0 / 3.0)
    return dv / RD_MPC


def mu_theory(z: np.ndarray, h0: float, om: float, os0: float, zt: float, wt: float) -> np.ndarray:
    """Módulo de distância μ = 5·log10(d_L/10pc)."""
    dl = d_L(z, h0, om, os0, zt, wt)
    return 5.0 * np.log10(dl) + 25.0


# ── Carregadores de dados ─────────────────────────────────────────────────────

def load_hz() -> dict:
    path = REPO / "data" / "real" / "Hz_data_real.csv"
    z, h_obs, sigma_h = [], [], []
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            z.append(float(row["z"]))
            h_obs.append(float(row["H_obs"]))
            sigma_h.append(float(row["sigma_H"]))
    return {"z": np.array(z), "H": np.array(h_obs), "sH": np.array(sigma_h)}


def load_desi_bao() -> list[dict]:
    """Carrega DESI DR2 BAO; agrupa pares correlacionados por bloco."""
    path = REPO / "data" / "real" / "cosmology" / "desi_dr2_bao_primary_points.csv"
    rows = []
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["primary_likelihood"].strip().lower() != "true":
                continue
            rows.append({
                "z": float(row["z_eff"]),
                "obs": row["observable"].strip(),
                "val": float(row["value"]),
                "sig": float(row["sigma"]),
                "cov_block": row["covariance_block"].strip(),
                "paired_obs": row.get("paired_observable", "").strip(),
                "rho": float(row["correlation_coefficient"]) if row["correlation_coefficient"].strip() else 0.0,
            })
    # Agrupa por bloco: se bloco tem 2 linhas → par correlacionado
    blocks: dict[str, list] = {}
    for r in rows:
        blocks.setdefault(r["cov_block"], []).append(r)
    return list(blocks.values())


def load_pantheon() -> dict:
    path = REPO / "validacao_real" / "data" / "pantheon_data.dat"
    with open(path) as f:
        header = f.readline().split()
    idx = {name: i for i, name in enumerate(header)}
    data = np.genfromtxt(path, skip_header=1, dtype=str)
    z = data[:, idx["zHD"]].astype(float)
    mu = data[:, idx["MU_SH0ES"]].astype(float)
    mu_err = data[:, idx["MU_SH0ES_ERR_DIAG"]].astype(float)
    is_calib = data[:, idx["IS_CALIBRATOR"]].astype(float)
    mask = is_calib == 0
    return {"z": z[mask], "mu": mu[mask], "mu_err": mu_err[mask], "n": mask.sum()}


# ── Funções de χ² ─────────────────────────────────────────────────────────────

def chi2_hz(theta: tuple, data: dict) -> float:
    h0, om, os0, zt, wt = theta
    e = np.sqrt(np.maximum(rll_e2(data["z"], om, os0, zt, wt), 1e-30))
    h_th = h0 * e
    return float(np.sum(((data["H"] - h_th) / data["sH"]) ** 2))


def chi2_bao(theta: tuple, blocks: list) -> float:
    h0, om, os0, zt, wt = theta
    total = 0.0
    for block in blocks:
        if len(block) == 1:
            r = block[0]
            z = np.array([r["z"]])
            if r["obs"] == "DV_over_rd":
                th = dv_over_rd(z, h0, om, os0, zt, wt)[0]
            elif r["obs"] == "DM_over_rd":
                th = dm_over_rd(z, h0, om, os0, zt, wt)[0]
            elif r["obs"] == "DH_over_rd":
                th = dh_over_rd(z, h0, om, os0, zt, wt)[0]
            else:
                continue
            total += ((r["val"] - th) / r["sig"]) ** 2
        else:
            # Par correlacionado (DM, DH) com matriz 2×2
            r1, r2 = block[0], block[1]
            z = np.array([r1["z"]])
            if r1["obs"] == "DM_over_rd":
                th1 = dm_over_rd(z, h0, om, os0, zt, wt)[0]
                th2 = dh_over_rd(z, h0, om, os0, zt, wt)[0]
            else:
                th1 = dh_over_rd(z, h0, om, os0, zt, wt)[0]
                th2 = dm_over_rd(z, h0, om, os0, zt, wt)[0]
            rho = r1["rho"]
            d1 = (r1["val"] - th1) / r1["sig"]
            d2 = (r2["val"] - th2) / r2["sig"]
            # χ² = [d1 d2] · C⁻¹ · [d1 d2]ᵀ   com C⁻¹ = 1/(1-ρ²) × [[1 -ρ], [-ρ 1]]
            inv = 1.0 / (1.0 - rho ** 2)
            total += inv * (d1 ** 2 - 2.0 * rho * d1 * d2 + d2 ** 2)
    return total


def chi2_sn(theta: tuple, data: dict) -> float:
    """χ² Pantheon+ com M_B marginalizado analiticamente."""
    h0, om, os0, zt, wt = theta
    mu_th = mu_theory(data["z"], h0, om, os0, zt, wt)
    delta = data["mu"] - mu_th
    w = 1.0 / data["mu_err"] ** 2
    # M_B ótimo analítico: M_B = Σ(δ·w)/Σw
    mb_opt = np.sum(delta * w) / np.sum(w)
    residuals = delta - mb_opt
    return float(np.sum(w * residuals ** 2))


def chi2_joint(theta: tuple, hz: dict, bao: list, sn: dict) -> float:
    h0, om, os0, zt, wt = theta
    # Rejeição fora de domínio físico
    ol = 1.0 - om - OMEGA_R - os0
    if h0 < 55 or h0 > 85:
        return 1e12
    if om < 0.1 or om > 0.6:
        return 1e12
    if os0 < 0.0 or os0 > 0.15:
        return 1e12
    if wt < 0.01 or wt > 3.0:
        return 1e12
    if zt < 0.05 or zt > 4.0:
        return 1e12
    if ol < 0.0:
        return 1e12
    # E(0) deve ser 1 — verificar por construção (ΩΛ = 1-Ωm-Ωr-Ωs0, logo E²(0)=1 ✓)
    try:
        return chi2_hz(theta, hz) + chi2_bao(theta, bao) + chi2_sn(theta, sn)
    except Exception:
        return 1e12


# ── Otimização ────────────────────────────────────────────────────────────────

STARTS = [
    # (H0, Om, Os0, zt, wt)  — pontos de partida variados
    (67.4, 0.315, 0.020, 1.00, 0.30),   # nominal Planck
    (67.4, 0.315, 0.001, 1.00, 0.30),   # Ωs0 → 0 (ΛCDM-like)
    (67.4, 0.315, 0.020, 0.30, 0.30),   # z_t preferido pelo BAO
    (68.0, 0.290, 0.030, 1.50, 0.50),   # z_t intermediário
    (70.0, 0.300, 0.020, 2.00, 0.80),   # H₀ maior
    (67.4, 0.315, 0.020, 0.80, 1.00),   # w_t mais largo
    (67.4, 0.315, 0.010, 0.50, 0.20),   # z_t baixo, transição estreita
    (69.0, 0.310, 0.005, 1.20, 0.40),   # Ωs0 pequeno
]


def main() -> int:
    print("=== Parametrização Coerente RLL — Joint Fit ===")
    print("Carregando dados...")

    hz = load_hz()
    bao = load_desi_bao()
    sn = load_pantheon()

    print(f"  Moresco H(z): {len(hz['z'])} pontos")
    print(f"  DESI DR2 BAO: {sum(len(b) for b in bao)} pontos em {len(bao)} blocos")
    print(f"  Pantheon+SH0ES: {sn['n']} SNe cosmológicas (M_B marginalizado)")
    print(f"  rd = {RD_MPC} Mpc (fixo — Planck 2018)\n")

    best_chi2 = 1e15
    best_result = None
    best_x0 = None
    all_runs = []

    for i, x0 in enumerate(STARTS):
        try:
            res = minimize(
                chi2_joint, x0=x0,
                args=(hz, bao, sn),
                method="Nelder-Mead",
                options={"maxiter": 8000, "xatol": 1e-5, "fatol": 1e-5, "adaptive": True},
            )
            tag = "✓" if res.success else "~"
            print(f"  [{i+1}/{len(STARTS)}] {tag} H0={res.x[0]:.2f} Om={res.x[1]:.4f} "
                  f"Os0={res.x[2]:.4f} zt={res.x[3]:.4f} wt={res.x[4]:.4f}  "
                  f"χ²={res.fun:.3f}")
            all_runs.append({"x0": list(x0), "x_opt": list(res.x), "chi2": res.fun,
                             "success": res.success, "nit": res.nit})
            if res.fun < best_chi2:
                best_chi2 = res.fun
                best_result = res
                best_x0 = x0
        except Exception as e:
            print(f"  [{i+1}/{len(STARTS)}] ERRO: {e}")

    if best_result is None:
        print("FALHA: nenhum ponto convergiu.")
        return 1

    h0, om, os0, zt, wt = best_result.x
    ol = 1.0 - om - OMEGA_R - os0

    # Decompor χ² por dataset
    c2_hz = chi2_hz(best_result.x, hz)
    c2_bao = chi2_bao(best_result.x, bao)
    c2_sn = chi2_sn(best_result.x, sn)

    n_hz = len(hz["z"])
    n_bao = sum(len(b) for b in bao)
    n_sn = int(sn["n"])
    n_total = n_hz + n_bao + n_sn
    k = 5  # H₀, Ωm, Ωs0, z_t, w_t

    print(f"\n{'='*60}")
    print("PARÂMETROS ÓTIMOS RLL (joint)")
    print(f"{'='*60}")
    print(f"  H₀     = {h0:.3f} km/s/Mpc")
    print(f"  Ωm     = {om:.4f}")
    print(f"  Ωs0    = {os0:.5f}")
    print(f"  z_t    = {zt:.4f}")
    print(f"  w_t    = {wt:.4f}")
    print(f"  ΩΛ     = {ol:.4f}  [derivado: 1-Ωm-Ωr-Ωs0]")
    print(f"\n  χ²_Hz      = {c2_hz:.3f}   /dof = {c2_hz/(n_hz-k):.4f}  (N={n_hz})")
    print(f"  χ²_BAO     = {c2_bao:.3f}   /dof = {c2_bao/(n_bao-k):.4f}  (N={n_bao})")
    print(f"  χ²_SN      = {c2_sn:.3f}  /dof = {c2_sn/(n_sn-k):.4f}  (N={n_sn})")
    print(f"  χ²_joint   = {best_chi2:.3f}  /dof = {best_chi2/(n_total-k):.4f}  (N_total={n_total})")

    # Comparar com parâmetros nominais Planck
    x_planck = (67.4, 0.315, 0.02, 1.0, 0.3)
    c2_planck = chi2_joint(x_planck, hz, bao, sn)
    delta_chi2 = c2_planck - best_chi2
    print(f"\n  Δχ² (Planck nominal → ótimo) = {delta_chi2:.3f}")
    print(f"  {'Melhora significativa' if delta_chi2 > 5 else 'Melhora marginal'}")

    result = {
        "meta": {
            "script": "optimize_rll_joint_parametrizacao.py",
            "date": "2026-07-13",
            "model": "E²(z)=Ωm(1+z)³+Ωr(1+z)⁴+Ωs0·[f(z)+(1-f(z))(1+z)³]+ΩΛ",
            "n_free_params": k,
            "fixed": {"Omega_r": OMEGA_R, "rd_Mpc": RD_MPC},
            "datasets": {
                "Moresco_Hz": n_hz,
                "DESI_DR2_BAO": n_bao,
                "PantheonPlus": n_sn,
            },
            "n_total": n_total,
            "n_starts": len(STARTS),
        },
        "optimal_params": {
            "H0_km_s_Mpc": round(h0, 4),
            "Omega_m": round(om, 5),
            "Omega_s0": round(os0, 6),
            "z_t": round(zt, 5),
            "w_t": round(wt, 5),
            "Omega_Lambda_derived": round(ol, 5),
        },
        "chi2_breakdown": {
            "chi2_Hz": round(c2_hz, 4),
            "chi2_Hz_red": round(c2_hz / (n_hz - k), 5),
            "chi2_BAO": round(c2_bao, 4),
            "chi2_BAO_red": round(c2_bao / (n_bao - k), 5),
            "chi2_SN_marginal_MB": round(c2_sn, 4),
            "chi2_SN_red": round(c2_sn / (n_sn - k), 5),
            "chi2_joint": round(best_chi2, 4),
            "chi2_joint_red": round(best_chi2 / (n_total - k), 5),
        },
        "comparison_planck_nominal": {
            "chi2_planck_nominal": round(c2_planck, 4),
            "delta_chi2": round(delta_chi2, 4),
            "interpretation": (
                "Melhora significativa (Δχ² > 5)" if delta_chi2 > 5
                else "Melhora marginal (Δχ² ≤ 5)"
            ),
        },
        "best_start": list(best_x0),
        "all_runs": all_runs,
        "epistemic_status": (
            "[E] parâmetros ótimos por minimização MAP conjunta (Nelder-Mead). "
            "[C] rd=147.09 Mpc fixo (Planck 2018) — tratamento correto requer CMB likelihood. "
            "[C] M_B marginalizado analiticamente em Pantheon+. "
            "[VAZIO] incertezas nos parâmetros requerem MCMC (G1)."
        ),
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nOutput: {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
