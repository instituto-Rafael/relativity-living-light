"""
FASE 17 — Análise Completa RLL: 5 datasets reais, 6 parâmetros livres,
rd auto-consistente (Eisenstein & Hu), profile likelihood (Ωs0 × z_t).

Datasets:
  1. Moresco H(z) 2022       — 33 pontos CC+BAO_BOSS (H(z) em km/s/Mpc)
  2. BAO histórico            — 4 pontos não-DESI (DV/rs: 6dFGS, MGS, BOSS LOWZ/CMASS)
  3. DESI DR2 BAO 2025       — 13 dados (1 iso + 6 pares anisotrópicos)
  4. Pantheon+SH0ES          — 1624 SNe (calibradores excluídos, M_B marginalizado)
  5. CMB shift Planck 2018   — 3 observáveis (R, l_A, Ωb·h²) com cov. 3×3

Parâmetros livres: H₀, Ωm, Ωb, Ωs0, z_t, w_t
Parâmetros fixos:  Ωr = 9.18×10⁻⁵ (T_CMB = 2.7255 K)
rd: auto-consistente via aproximação Eisenstein & Hu (1998)

Status epistêmico: [E] análise quantitativa com dados reais
"""

import numpy as np
import json
import csv
import sys
import os
from pathlib import Path
from scipy.optimize import minimize

# ─── Paths ─────────────────────────────────────────────────────────────────
REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data" / "real"
RESULTS = REPO / "results"
PANTHEON_PATH = REPO / "validacao_real" / "data" / "pantheon_data.dat"

# ─── Constantes físicas ────────────────────────────────────────────────────
C_KMS = 299792.458   # velocidade da luz em km/s
OMEGA_R = 9.18e-5    # densidade de radiação (T_CMB = 2.7255 K)
Z_CMB = 1089.92      # redshift da recombinação (Planck 2018)

# ─── Grid de integração em z (log-espaçado, cobre 0 a 1200) ───────────────
# Ponto z=0 adicionado explicitamente; alta resolução em z baixo onde RLL difere
_ZG = np.concatenate([[0.0], np.logspace(-4, np.log10(1200.0), 7000)])

# ─── Eisenstein & Hu (1998) — horizonte sonoro no drag epoch ──────────────
def compute_rd(om_h2: float, ob_h2: float) -> float:
    """rd em Mpc via fórmula de ajuste E&H 1998 (eq. 6 em Aubourg+ 2015)."""
    return 147.49 * (om_h2 / 0.1432)**(-0.255) * (ob_h2 / 0.02236)**(-0.128)

# ─── Modelo RLL — E²(z) ───────────────────────────────────────────────────
def _e2_vec(z: np.ndarray, om: float, os0: float, zt: float, wt: float) -> np.ndarray:
    """E²(z) vetorizado para array z."""
    f = 1.0 / (1.0 + np.exp((z - zt) / wt))
    rho_s = os0 * (f + (1.0 - f) * (1.0 + z)**3)
    ol = 1.0 - om - OMEGA_R - os0
    return om*(1.+z)**3 + OMEGA_R*(1.+z)**4 + rho_s + ol

def _build_integrals(H0: float, om: float, os0: float, zt: float, wt: float):
    """
    Constrói chi(z) = ∫₀^z dz'/E(z') e H(z) = H₀·E(z) sobre o grid _ZG.
    Retorna (chi_arr, hz_arr) no mesmo grid _ZG.
    """
    e2 = _e2_vec(_ZG, om, os0, zt, wt)
    e2 = np.maximum(e2, 1e-30)
    e = np.sqrt(e2)
    inv_e = 1.0 / e
    # Integração trapezoidal acumulada
    dz = np.diff(_ZG)
    mid = 0.5 * (inv_e[:-1] + inv_e[1:])
    chi_arr = np.zeros_like(_ZG)
    chi_arr[1:] = np.cumsum(dz * mid)
    hz_arr = H0 * e
    return chi_arr, hz_arr

# ─── Distâncias computadas ─────────────────────────────────────────────────
def dm_mpc(z_q: np.ndarray, H0: float, chi_arr: np.ndarray) -> np.ndarray:
    """Distância comóvel DM(z) em Mpc."""
    return np.interp(z_q, _ZG, chi_arr) * (C_KMS / H0)

def dh_mpc(z_q: np.ndarray, hz_arr: np.ndarray) -> np.ndarray:
    """Distância de Hubble DH(z) = c/H(z) em Mpc."""
    return C_KMS / np.interp(z_q, _ZG, hz_arr)

def hz_kms(z_q: np.ndarray, hz_arr: np.ndarray) -> np.ndarray:
    return np.interp(z_q, _ZG, hz_arr)

# ═══════════════════════════════════════════════════════════════════════════
# 1. Moresco H(z) — χ²
# ═══════════════════════════════════════════════════════════════════════════
def load_moresco():
    rows = []
    with open(DATA / "Hz_data_real.csv") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append([float(r['z']), float(r['H_obs']), float(r['sigma_H'])])
    return np.array(rows)   # shape (33, 3)

def chi2_moresco(theta, data):
    H0, om, ob, os0, zt, wt = theta
    _, hz_arr = _build_integrals(H0, om, os0, zt, wt)
    h_th = hz_kms(data[:, 0], hz_arr)
    return float(np.sum(((data[:, 1] - h_th) / data[:, 2])**2))

# ═══════════════════════════════════════════════════════════════════════════
# 2. BAO histórico (DV/rs) — exclui DESI2024 e BOSS_Lya para evitar
#    dupla contagem com DESI DR2 e DESI DR2 Lya
# ═══════════════════════════════════════════════════════════════════════════
_BAO_HIST_EXCLUDE = {'DESI2024_BGS', 'DESI2024_LRG1', 'DESI2024_LRG2',
                     'DESI2024_ELG', 'DESI2024_QSO', 'BOSS_Lya'}

def load_bao_hist():
    rows = []
    with open(DATA / "BAO_data_real.csv") as f:
        reader = csv.DictReader(f)
        for r in reader:
            if r['survey'] in _BAO_HIST_EXCLUDE:
                continue
            rows.append([float(r['z_eff']), float(r['DV_over_rs']), float(r['sigma'])])
    return np.array(rows)   # shape (4, 3): 6dFGS, MGS, BOSS_LOWZ, BOSS_CMASS

def chi2_bao_hist(theta, data, rd_mpc_override=None):
    H0, om, ob, os0, zt, wt = theta
    h = H0 / 100.
    rd = rd_mpc_override if rd_mpc_override else compute_rd(om*h**2, ob*h**2)
    chi_arr, hz_arr = _build_integrals(H0, om, os0, zt, wt)
    z = data[:, 0]
    dm = dm_mpc(z, H0, chi_arr)
    dh = dh_mpc(z, hz_arr)
    dv = (z * dm**2 * dh)**(1./3.)
    dv_th = dv / rd
    return float(np.sum(((data[:, 1] - dv_th) / data[:, 2])**2))

# ═══════════════════════════════════════════════════════════════════════════
# 3. DESI DR2 BAO — χ² com blocos de covariância 2×2
# ═══════════════════════════════════════════════════════════════════════════
def load_desi_dr2():
    """Retorna lista de blocos BAO DESI DR2."""
    rows_by_tracer = {}
    with open(DATA / "cosmology" / "desi_dr2_bao_primary_points.csv") as f:
        reader = csv.DictReader(f)
        for r in reader:
            t = r['tracer']
            rows_by_tracer.setdefault(t, []).append(r)

    blocks = []
    for tracer, rows in rows_by_tracer.items():
        if len(rows) == 1:
            r = rows[0]
            blocks.append({
                'type': 'iso', 'z': float(r['z_eff']),
                'obs': float(r['value']), 'sig': float(r['sigma'])
            })
        else:
            dm_r = next(r for r in rows if r['observable'] == 'DM_over_rd')
            dh_r = next(r for r in rows if r['observable'] == 'DH_over_rd')
            blocks.append({
                'type': 'aniso', 'z': float(dm_r['z_eff']),
                'dm_obs': float(dm_r['value']), 'dm_sig': float(dm_r['sigma']),
                'dh_obs': float(dh_r['value']), 'dh_sig': float(dh_r['sigma']),
                'rho': float(dm_r['correlation_coefficient'])
            })
    return blocks

def chi2_desi_dr2(theta, blocks, rd_mpc_override=None):
    H0, om, ob, os0, zt, wt = theta
    h = H0 / 100.
    rd = rd_mpc_override if rd_mpc_override else compute_rd(om*h**2, ob*h**2)
    chi_arr, hz_arr = _build_integrals(H0, om, os0, zt, wt)
    total = 0.0
    for b in blocks:
        z = b['z']
        chi_z = np.interp(z, _ZG, chi_arr)
        hz_z = np.interp(z, _ZG, hz_arr)
        dm = (C_KMS / H0) * chi_z
        dh = C_KMS / hz_z
        if b['type'] == 'iso':
            dv = (z * dm**2 * dh)**(1./3.)
            d = (b['obs'] - dv/rd) / b['sig']
            total += d**2
        else:
            dm_th = dm / rd
            dh_th = dh / rd
            d1 = (b['dm_obs'] - dm_th) / b['dm_sig']
            d2 = (b['dh_obs'] - dh_th) / b['dh_sig']
            rho = b['rho']
            inv_det = 1.0 / (1.0 - rho**2)
            total += inv_det * (d1**2 - 2.*rho*d1*d2 + d2**2)
    return float(total)

# ═══════════════════════════════════════════════════════════════════════════
# 4. Pantheon+SH0ES — χ² com marginalização analítica de M_B
# ═══════════════════════════════════════════════════════════════════════════
def load_pantheon():
    """Carrega Pantheon+SH0ES (1624 SNe cosmológicas, calibradores excluídos)."""
    with open(PANTHEON_PATH) as f:
        header = f.readline().split()
    idx = {name: i for i, name in enumerate(header)}
    data = np.genfromtxt(PANTHEON_PATH, skip_header=1, dtype=str)
    z = data[:, idx["zHD"]].astype(float)
    mu = data[:, idx["MU_SH0ES"]].astype(float)
    mu_err = data[:, idx["MU_SH0ES_ERR_DIAG"]].astype(float)
    is_calib = data[:, idx["IS_CALIBRATOR"]].astype(float)
    mask = is_calib == 0
    return z[mask], mu[mask], mu_err[mask]

def chi2_sn(theta, sn_data):
    H0, om, ob, os0, zt, wt = theta
    z_arr, mu_obs, mu_err = sn_data
    chi_arr, _ = _build_integrals(H0, om, os0, zt, wt)
    chi_z = np.interp(z_arr, _ZG, chi_arr)
    dl = (1.0 + z_arr) * (C_KMS / H0) * chi_z
    dl = np.maximum(dl, 1e-10)
    mu_th = 5.0 * np.log10(dl) + 25.0
    # Marginalização analítica de M_B
    delta = mu_obs - mu_th
    w = 1.0 / mu_err**2
    mb_opt = np.sum(delta * w) / np.sum(w)
    res = delta - mb_opt
    return float(np.sum(w * res**2))

# ═══════════════════════════════════════════════════════════════════════════
# 5. CMB shift Planck 2018 — χ² com covariância 3×3
# ═══════════════════════════════════════════════════════════════════════════
def load_cmb_shift():
    with open(DATA / "CMB_shift_real.json") as f:
        d = json.load(f)
    obs = np.array([d['R_obs'], d['la_obs'], d['ob_h2_obs']])
    cov = np.array(d['covariance'])
    cov_inv = np.linalg.inv(cov)
    return {'obs': obs, 'cov_inv': cov_inv, 'z_cmb': float(d['z_CMB'])}

def chi2_cmb(theta, cmb_data):
    H0, om, ob, os0, zt, wt = theta
    h = H0 / 100.
    ob_h2 = ob * h**2
    om_h2 = om * h**2
    rd = compute_rd(om_h2, ob_h2)
    chi_arr, _ = _build_integrals(H0, om, os0, zt, wt)
    z_cmb = cmb_data['z_cmb']
    chi_cmb = np.interp(z_cmb, _ZG, chi_arr)
    # Parâmetro de shift: R = √Ωm · χ(z_CMB)
    R_th = np.sqrt(om) * chi_cmb
    # Escala acústica: l_A = π · DM(z_CMB) / rd
    DM_cmb = (C_KMS / H0) * chi_cmb       # em Mpc
    l_A_th = np.pi * DM_cmb / rd
    # Densidade baryon
    ob_h2_th = ob_h2
    th = np.array([R_th, l_A_th, ob_h2_th])
    delta = cmb_data['obs'] - th
    return float(delta @ cmb_data['cov_inv'] @ delta)

# ═══════════════════════════════════════════════════════════════════════════
# χ² total + penalidade de físico
# ═══════════════════════════════════════════════════════════════════════════
def chi2_total(theta, datasets):
    H0, om, ob, os0, zt, wt = theta
    # Verificações de físico
    if ob <= 0 or om <= 0.10 or os0 < 0 or wt <= 0:
        return 1e12
    ol = 1.0 - om - OMEGA_R - os0
    if ol < 0.0 or (om + os0 + OMEGA_R) > 0.995:
        return 1e12
    try:
        moresco, bao_hist, desi_blocks, sn_data, cmb_data = datasets
        return (chi2_moresco(theta, moresco) +
                chi2_bao_hist(theta, bao_hist) +
                chi2_desi_dr2(theta, desi_blocks) +
                chi2_sn(theta, sn_data) +
                chi2_cmb(theta, cmb_data))
    except Exception:
        return 1e12

# ═══════════════════════════════════════════════════════════════════════════
# Otimização MAP — 6 parâmetros
# ═══════════════════════════════════════════════════════════════════════════
_STARTS_6D = [
    [68.5,  0.315, 0.049, 0.000, 1.0,  0.30],
    [67.4,  0.315, 0.049, 0.020, 0.8,  0.30],
    [70.0,  0.300, 0.048, 0.010, 1.2,  0.50],
    [68.0,  0.320, 0.050, 0.030, 0.7,  0.25],
    [69.5,  0.300, 0.046, 0.005, 1.5,  0.40],
    [68.0,  0.310, 0.049, 0.000, 1.0,  0.30],
    [68.7,  0.303, 0.049, 0.001, 0.5,  0.20],
    [67.5,  0.325, 0.051, 0.040, 2.0,  0.60],
]

def optimize_6d(datasets, starts=None):
    starts = starts or _STARTS_6D
    best, best_val = None, 1e15
    for x0 in starts:
        try:
            res = minimize(
                lambda x: chi2_total(x, datasets), x0,
                method='Nelder-Mead',
                options={'xatol': 1e-6, 'fatol': 1e-6, 'maxiter': 8000,
                         'adaptive': True}
            )
            if res.fun < best_val:
                best_val = res.fun
                best = res
        except Exception:
            pass
    return best

# ═══════════════════════════════════════════════════════════════════════════
# Profile likelihood: grade 10×10 em (Ωs0, z_t)
# ═══════════════════════════════════════════════════════════════════════════
_OS0_GRID = np.array([0.000, 0.001, 0.003, 0.005, 0.010, 0.020,
                      0.030, 0.050, 0.070, 0.100])
_ZT_GRID  = np.array([0.3, 0.5, 0.7, 0.9, 1.1, 1.4, 1.7, 2.0, 2.5, 3.0])

def profile_likelihood(datasets):
    results = []
    total = len(_OS0_GRID) * len(_ZT_GRID)
    idx = 0
    for os0 in _OS0_GRID:
        for zt in _ZT_GRID:
            idx += 1
            def local_obj(x4):
                H0, om, ob, wt = x4
                return chi2_total([H0, om, ob, os0, zt, wt], datasets)
            try:
                res = minimize(
                    local_obj, [68.5, 0.315, 0.049, 0.30],
                    method='Nelder-Mead',
                    options={'xatol': 1e-5, 'fatol': 1e-5, 'maxiter': 3000,
                             'adaptive': True}
                )
                chi2_v = float(res.fun)
                H0_o, om_o, ob_o, wt_o = res.x
            except Exception:
                chi2_v = 1e12
                H0_o, om_o, ob_o, wt_o = 68.5, 0.315, 0.049, 0.30

            results.append({
                'os0': float(os0), 'zt': float(zt), 'chi2': chi2_v,
                'H0': float(H0_o), 'om': float(om_o),
                'ob': float(ob_o), 'wt': float(wt_o)
            })
            print(f"  [{idx:3d}/{total}] Ωs0={os0:.3f}, z_t={zt:.1f} → χ²={chi2_v:.3f}")
    return results

# ═══════════════════════════════════════════════════════════════════════════
# Otimização ΛCDM pura (3 parâmetros: H₀, Ωm, Ωb)
# ═══════════════════════════════════════════════════════════════════════════
def optimize_lcdm(datasets):
    def obj(x3):
        H0, om, ob = x3
        return chi2_total([H0, om, ob, 0.0, 1.0, 0.3], datasets)
    starts = [[68.5, 0.315, 0.049], [67.4, 0.310, 0.048], [69.5, 0.300, 0.046]]
    best, best_val = None, 1e15
    for x0 in starts:
        try:
            res = minimize(obj, x0, method='Nelder-Mead',
                           options={'xatol': 1e-6, 'fatol': 1e-6, 'maxiter': 5000})
            if res.fun < best_val:
                best_val = res.fun
                best = res
        except Exception:
            pass
    return best

# ═══════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════
def main():
    print("=" * 65)
    print("  RLL Análise Completa — FASE 17")
    print("  5 datasets reais · 6 parâmetros · profile likelihood 10×10")
    print("=" * 65)

    # ── Carregar dados ─────────────────────────────────────────────────────
    print("\n[1/5] Carregando Moresco H(z) 2022 ...")
    moresco = load_moresco()
    print(f"      {len(moresco)} pontos, z ∈ [{moresco[:,0].min():.3f}, {moresco[:,0].max():.3f}]")

    print("[2/5] Carregando BAO histórico ...")
    bao_hist = load_bao_hist()
    print(f"      {len(bao_hist)} pontos (6dFGS + MGS + BOSS LOWZ + BOSS CMASS)")

    print("[3/5] Carregando DESI DR2 BAO 2025 ...")
    desi_blocks = load_desi_dr2()
    n_desi_pts = sum(1 if b['type'] == 'iso' else 2 for b in desi_blocks)
    print(f"      {len(desi_blocks)} tracers → {n_desi_pts} dados")

    print("[4/5] Carregando Pantheon+SH0ES ...")
    sn_data = load_pantheon()
    n_sn = len(sn_data[0])
    print(f"      {n_sn} SNe (calibradores excluídos)")

    print("[5/5] Carregando CMB shift Planck 2018 ...")
    cmb_data = load_cmb_shift()
    print(f"      R_obs={cmb_data['obs'][0]:.4f}, l_A_obs={cmb_data['obs'][1]:.3f}, Ωb·h²={cmb_data['obs'][2]:.5f}")

    N_hz   = len(moresco)
    N_bao  = len(bao_hist)
    N_desi = n_desi_pts
    N_sn   = n_sn
    N_cmb  = 3
    N_total = N_hz + N_bao + N_desi + N_sn + N_cmb
    k_rll  = 6
    k_lcdm = 3

    print(f"\n  Total de dados: {N_total} = {N_hz} + {N_bao} + {N_desi} + {N_sn} + {N_cmb}")

    datasets = (moresco, bao_hist, desi_blocks, sn_data, cmb_data)

    # ── MAP RLL 6 parâmetros ───────────────────────────────────────────────
    print("\n── Otimização MAP RLL (6 parâmetros, 8 pontos de partida) ──────")
    res_rll = optimize_6d(datasets)
    H0, om, ob, os0, zt, wt = res_rll.x
    chi2_rll = res_rll.fun
    h = H0 / 100.
    rd_rll = compute_rd(om*h**2, ob*h**2)
    ol_rll = 1. - om - OMEGA_R - os0

    print(f"  H₀  = {H0:.4f} km/s/Mpc")
    print(f"  Ωm  = {om:.5f}")
    print(f"  Ωb  = {ob:.5f}  (Ωb·h² = {ob*h**2:.5f})")
    print(f"  Ωs0 = {os0:.6f}")
    print(f"  z_t = {zt:.4f}")
    print(f"  w_t = {wt:.4f}")
    print(f"  ΩΛ  = {ol_rll:.5f}  (derivado)")
    print(f"  rd  = {rd_rll:.4f} Mpc  (auto-consistente E&H)")

    # Breakdown do χ²
    theta_rll = list(res_rll.x)
    c_hz   = chi2_moresco(theta_rll, moresco)
    c_bao  = chi2_bao_hist(theta_rll, bao_hist)
    c_desi = chi2_desi_dr2(theta_rll, desi_blocks)
    c_sn   = chi2_sn(theta_rll, sn_data)
    c_cmb  = chi2_cmb(theta_rll, cmb_data)

    print(f"\n  χ² breakdown:")
    print(f"    Moresco H(z)   : {c_hz:.3f}  / {N_hz}  = {c_hz/N_hz:.4f}/pt")
    print(f"    BAO histórico  : {c_bao:.3f}  / {N_bao}  = {c_bao/N_bao:.4f}/pt")
    print(f"    DESI DR2 BAO   : {c_desi:.3f} / {N_desi} = {c_desi/N_desi:.4f}/pt")
    print(f"    Pantheon+SH0ES : {c_sn:.3f} / {N_sn} = {c_sn/N_sn:.4f}/pt")
    print(f"    CMB shift      : {c_cmb:.4f} / {N_cmb}  = {c_cmb/N_cmb:.5f}/pt")
    print(f"    TOTAL          : {chi2_rll:.3f} / {N_total} = {chi2_rll/N_total:.5f}/pt")

    # ── MAP ΛCDM 3 parâmetros ──────────────────────────────────────────────
    print("\n── Otimização MAP ΛCDM (3 parâmetros: H₀, Ωm, Ωb) ────────────")
    res_lcdm = optimize_lcdm(datasets)
    H0_l, om_l, ob_l = res_lcdm.x
    chi2_lcdm = res_lcdm.fun
    h_l = H0_l / 100.
    rd_l = compute_rd(om_l*h_l**2, ob_l*h_l**2)

    print(f"  H₀  = {H0_l:.4f} km/s/Mpc")
    print(f"  Ωm  = {om_l:.5f}")
    print(f"  Ωb  = {ob_l:.5f}  (Ωb·h² = {ob_l*h_l**2:.5f})")
    print(f"  rd  = {rd_l:.4f} Mpc")
    print(f"  χ²  = {chi2_lcdm:.3f}  /  {N_total}  = {chi2_lcdm/N_total:.5f}/pt")

    # Δχ², AIC, BIC
    delta_chi2 = chi2_rll - chi2_lcdm
    aic_rll  = chi2_rll  + 2 * k_rll
    aic_lcdm = chi2_lcdm + 2 * k_lcdm
    bic_rll  = chi2_rll  + k_rll  * np.log(N_total)
    bic_lcdm = chi2_lcdm + k_lcdm * np.log(N_total)
    delta_aic = aic_rll - aic_lcdm
    delta_bic = bic_rll - bic_lcdm

    print(f"\n  Comparação:")
    print(f"    Δχ²(RLL−ΛCDM)  = {delta_chi2:.4f}")
    print(f"    ΔAIC(RLL−ΛCDM) = {delta_aic:.4f}  (k_RLL={k_rll}, k_ΛCDM={k_lcdm})")
    print(f"    ΔBIC(RLL−ΛCDM) = {delta_bic:.4f}")

    # ── Profile likelihood ─────────────────────────────────────────────────
    print("\n── Profile likelihood: grade 10×10 em (Ωs0 × z_t) ────────────")
    profile = profile_likelihood(datasets)

    chi2_profile_min = min(p['chi2'] for p in profile)
    best_profile = min(profile, key=lambda p: p['chi2'])

    print(f"\n  Mínimo do profile: Ωs0={best_profile['os0']:.3f}, z_t={best_profile['zt']:.1f}")
    print(f"    χ²_profile_min = {chi2_profile_min:.3f}")
    print(f"    vs χ²_ΛCDM    = {chi2_lcdm:.3f}")
    print(f"    Δχ²_profile    = {chi2_profile_min - chi2_lcdm:.4f}")

    # Tabela de perfil (condensada: mínimo por linha Ωs0)
    print("\n  Profile likelihood — χ²_min(Ωs0) = min_{z_t} χ²(Ωs0, z_t):")
    print(f"  {'Ωs0':>8}  {'χ²_min':>10}  {'Δχ² vs 0':>10}  {'z_t_opt':>8}  {'H₀':>7}  {'Ωm':>6}")
    for os0_v in _OS0_GRID:
        row = min((p for p in profile if p['os0'] == os0_v), key=lambda p: p['chi2'])
        dchi2 = row['chi2'] - chi2_lcdm
        print(f"  {os0_v:>8.3f}  {row['chi2']:>10.3f}  {dchi2:>+10.3f}  "
              f"{row['zt']:>8.1f}  {row['H0']:>7.3f}  {row['om']:>6.4f}")

    # ── Salvar JSON ────────────────────────────────────────────────────────
    RESULTS.mkdir(exist_ok=True)
    output = {
        "metadata": {
            "script": "scripts/rll_analise_completa.py",
            "date": "2026-07-13",
            "fase": "FASE 17",
            "status_epistemico": "[E] otimização MAP joint + profile likelihood executados",
            "referencia": "arXiv:2503.14738 (DESI DR2), arXiv:1808.05724 (CMB shift Planck 2018)",
            "rd_formula": "Eisenstein & Hu 1998 via Aubourg+ 2015 eq.6: 147.49*(om_h2/0.1432)^-0.255*(ob_h2/0.02236)^-0.128 Mpc"
        },
        "datasets_usados": {
            "moresco_hz_2022": {"n": int(N_hz), "fonte": "data/real/Hz_data_real.csv"},
            "bao_historico": {
                "n": int(N_bao), "fonte": "data/real/BAO_data_real.csv",
                "surveys": ["6dFGS", "SDSS_MGS", "BOSS_DR12_LOWZ", "BOSS_DR12_CMASS"],
                "excluidos": "DESI2024_* (dupla-contagem com DESI DR2) + BOSS_Lya (dupla-contagem com DESI DR2 Lya)"
            },
            "desi_dr2_bao_2025": {
                "n_dados": int(N_desi), "n_tracers": len(desi_blocks),
                "fonte": "data/real/cosmology/desi_dr2_bao_primary_points.csv",
                "referencia": "arXiv:2503.14738"
            },
            "pantheon_plus_shoes": {
                "n": int(N_sn), "fonte": "validacao_real/data/pantheon_data.dat",
                "nota": "IS_CALIBRATOR==0; M_B marginalizado analiticamente"
            },
            "cmb_shift_planck2018": {
                "n": int(N_cmb), "fonte": "data/real/CMB_shift_real.json",
                "observaveis": ["R", "l_A", "Omega_b_h2"],
                "referencia": "Chen, Huang, Wang 2019 arXiv:1808.05724"
            },
            "total_dados": int(N_total)
        },
        "map_rll_6param": {
            "H0": float(H0), "om": float(om), "ob": float(ob),
            "os0": float(os0), "zt": float(zt), "wt": float(wt),
            "ol_derivado": float(ol_rll),
            "rd_mpc_autoconsistente": float(rd_rll),
            "ob_h2": float(ob * h**2),
            "om_h2": float(om * h**2),
            "chi2_total": float(chi2_rll),
            "chi2_red": float(chi2_rll / N_total),
            "k_params": k_rll,
            "aic": float(aic_rll),
            "bic": float(bic_rll),
            "chi2_breakdown": {
                "moresco_hz": float(c_hz),
                "bao_historico": float(c_bao),
                "desi_dr2": float(c_desi),
                "pantheon_sn": float(c_sn),
                "cmb_shift": float(c_cmb)
            }
        },
        "map_lcdm_3param": {
            "H0": float(H0_l), "om": float(om_l), "ob": float(ob_l),
            "rd_mpc": float(rd_l),
            "chi2_total": float(chi2_lcdm),
            "chi2_red": float(chi2_lcdm / N_total),
            "k_params": k_lcdm,
            "aic": float(aic_lcdm),
            "bic": float(bic_lcdm)
        },
        "comparacao_modelos": {
            "delta_chi2_rll_minus_lcdm": float(delta_chi2),
            "delta_aic": float(delta_aic),
            "delta_bic": float(delta_bic),
            "n_dados": int(N_total),
            "k_rll": k_rll,
            "k_lcdm": k_lcdm,
            "interpretacao": (
                "ΔAIC>0 penaliza RLL; Δχ²≈0 confirma colapso Ωs0→0; "
                "ΛCDM mais parcimonioso com mesma evidência"
            ) if delta_chi2 > -1.0 else (
                "Δχ²<-1: RLL tem χ² menor; verificar se diferença é significativa"
            )
        },
        "profile_likelihood": profile,
        "profile_minimum": best_profile,
        "profile_summary": {
            "chi2_min_profile": float(chi2_profile_min),
            "delta_chi2_vs_lcdm": float(chi2_profile_min - chi2_lcdm),
            "os0_at_min": float(best_profile['os0']),
            "zt_at_min": float(best_profile['zt'])
        }
    }

    out_path = RESULTS / "rll_analise_completa.json"
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n  JSON salvo: {out_path}")
    print("\n" + "=" * 65)
    print("  CONCLUSÃO")
    print("=" * 65)
    print(f"  χ²_RLL (6p)   = {chi2_rll:.3f}  (rd = {rd_rll:.2f} Mpc auto-consistente)")
    print(f"  χ²_ΛCDM (3p)  = {chi2_lcdm:.3f}")
    print(f"  Δχ²           = {delta_chi2:+.4f}")
    print(f"  ΔAIC           = {delta_aic:+.4f}  ({'RLL penalizado' if delta_aic > 0 else 'RLL favorecido'})")
    print(f"  ΔBIC           = {delta_bic:+.4f}  ({'RLL penalizado' if delta_bic > 0 else 'RLL favorecido'})")
    print(f"  Ωs0 ótimo      = {os0:.6f}  {'→ colapso ΛCDM' if os0 < 0.001 else '→ setor RLL presente'}")
    print("=" * 65)

    return output

if __name__ == "__main__":
    main()
