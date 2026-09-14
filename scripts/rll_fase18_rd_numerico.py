"""
FASE 18 — Análise RLL: rd Numérico + Prior BBN em Ωb·h²

Melhoras em relação à FASE 17:
  A. rd numérico: substitui fórmula E&H (1998) por integral completa
       rd = ∫_{z_drag}^∞ c_s(z)/H(z) dz   (horizonte sonoro no drag epoch)
       z_drag: equação E&H (1998) Eq. 4 (mantida, acurácia ~0.5%)
  B. Prior BBN em Ωb·h²: Gaussiana com Ωb·h² = 0.02236 ± 0.00015
       (Cooke, Pettini & Steidel 2018, arXiv:1710.11129)
       Elimina deriva artificial de Ωb durante otimização livre

Propósito epistêmico:
  A tensão CMB da FASE 17 (χ²_CMB/3 = 6.56) veio de dois efeitos:
    1. E&H subestima rd em ~3% fora do regime de calibração (Ωm·h²≈0.127 < 0.143)
    2. Ωb·h² deriva para 0.02284 (vs BBN 0.02236), sozinho adicionando Δχ²≈10
  Esta FASE corrige ambos simultaneamente e reavalia o estado epistêmico.

Datasets (iguais à FASE 17):
  Moresco H(z) 2022 · BAO histórico · DESI DR2 · Pantheon+SH0ES · CMB shift

Status epistêmico: [E] análise quantitativa com dados reais
Referência rd numérico: Hu & Sugiyama 1996, Eisenstein & Hu 1998 (z_drag)
Referência BBN: Cooke, Pettini & Steidel 2018 arXiv:1710.11129
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
C_KMS = 299792.458          # velocidade da luz em km/s
OMEGA_R = 9.18e-5           # radiação total (fótons + neutrinos), T_CMB=2.7255 K
Z_CMB   = 1089.92           # redshift da recombinação (Planck 2018)

# Prior BBN (Cooke et al. 2018)
BBN_OBH2     = 0.02236
BBN_OBH2_SIG = 0.00015

# Densidade de fótons: Ωγ·h² = 2.47×10⁻⁵ (T_CMB = 2.7255 K)
OMEGA_GAMMA_H2 = 2.47e-5    # h²-independent: Ωγ = OMEGA_GAMMA_H2 / h²

# ─── Grid de integração cosmológica (0 a 1200, log-espaçado) ──────────────
_ZG = np.concatenate([[0.0], np.logspace(-4, np.log10(1200.0), 7000)])

# ─── Grid para rd numérico (drag epoch a z_high, log-espaçado) ────────────
_Z_RD_HIGH = 5e5            # "infinito" bem dentro da era de radiação
_Z_RD_N    = 4000           # resolução da integral (0.05% acurácia)


# ══════════════════════════════════════════════════════════════════════════
# rd NUMÉRICO — horizonte sonoro no drag epoch
# ══════════════════════════════════════════════════════════════════════════

def _zdrag_EH98(om_h2: float, ob_h2: float) -> float:
    """z_drag via Eisenstein & Hu (1998) Eq. 4."""
    b1 = 0.313 * om_h2**(-0.419) * (1.0 + 0.607 * om_h2**0.674)
    b2 = 0.238 * om_h2**0.223
    return 1291.0 * om_h2**0.251 / (1.0 + 0.659 * om_h2**0.828) * (1.0 + b1 * ob_h2**b2)


def compute_rd_numerical(H0: float, om: float, ob: float,
                          os0: float, zt: float, wt: float) -> float:
    """
    rd = ∫_{z_drag}^{z_high} c_s(z) / H(z) dz    [Mpc]

    c_s(z) = c / sqrt(3 * (1 + R_b(z)))
    R_b(z) = (3 Ωb) / (4 Ωγ) / (1 + z)   (razão bárion–fóton)

    H(z) usa o modelo RLL completo via _e2_vec.
    """
    h = H0 / 100.
    om_h2 = om * h**2
    ob_h2 = ob * h**2

    z_drag = _zdrag_EH98(om_h2, ob_h2)

    # Grid log-espaçado de z_drag até z_high
    z_rd = np.logspace(np.log10(max(z_drag, 1.0)), np.log10(_Z_RD_HIGH), _Z_RD_N)

    # Velocidade do som
    omega_gamma = OMEGA_GAMMA_H2 / h**2          # Ωγ em unidade de fração crítica
    R0 = 3.0 * ob / (4.0 * omega_gamma)          # R_b(z=0) = 3Ωb/(4Ωγ)
    R_b = R0 / (1.0 + z_rd)                      # R_b(z)
    cs = C_KMS / np.sqrt(3.0 * (1.0 + R_b))     # km/s

    # H(z) do modelo RLL
    e2 = _e2_vec(z_rd, om, os0, zt, wt)
    Hz = H0 * np.sqrt(np.maximum(e2, 1e-30))    # km/s/Mpc

    integrand = cs / Hz   # cs [km/s] / Hz [km/s/Mpc] = [Mpc]; ∫ dz·Mpc = Mpc

    # Integração trapezoidal manual (compatível com NumPy ≥ 2.0)
    dz_rd = np.diff(z_rd)
    rd = float(np.sum(dz_rd * 0.5 * (integrand[:-1] + integrand[1:])))
    return rd


# ══════════════════════════════════════════════════════════════════════════
# Modelo RLL — E²(z)
# ══════════════════════════════════════════════════════════════════════════

def _e2_vec(z: np.ndarray, om: float, os0: float, zt: float, wt: float) -> np.ndarray:
    with np.errstate(over='ignore'):
        f = 1.0 / (1.0 + np.exp((z - zt) / wt))
    rho_s = os0 * (f + (1.0 - f) * (1.0 + z)**3)
    ol = 1.0 - om - OMEGA_R - os0
    return om*(1.+z)**3 + OMEGA_R*(1.+z)**4 + rho_s + ol


def _build_integrals(H0: float, om: float, os0: float, zt: float, wt: float):
    e2 = _e2_vec(_ZG, om, os0, zt, wt)
    e2 = np.maximum(e2, 1e-30)
    e = np.sqrt(e2)
    inv_e = 1.0 / e
    dz = np.diff(_ZG)
    mid = 0.5 * (inv_e[:-1] + inv_e[1:])
    chi_arr = np.zeros_like(_ZG)
    chi_arr[1:] = np.cumsum(dz * mid)
    hz_arr = H0 * e
    return chi_arr, hz_arr


def dm_mpc(z_q, H0, chi_arr):
    return np.interp(z_q, _ZG, chi_arr) * (C_KMS / H0)

def dh_mpc(z_q, hz_arr):
    return C_KMS / np.interp(z_q, _ZG, hz_arr)

def hz_kms(z_q, hz_arr):
    return np.interp(z_q, _ZG, hz_arr)


# ══════════════════════════════════════════════════════════════════════════
# 1. Moresco H(z)
# ══════════════════════════════════════════════════════════════════════════

def load_moresco():
    rows = []
    with open(DATA / "Hz_data_real.csv") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append([float(r['z']), float(r['H_obs']), float(r['sigma_H'])])
    return np.array(rows)


def chi2_moresco(theta, data):
    H0, om, ob, os0, zt, wt = theta
    _, hz_arr = _build_integrals(H0, om, os0, zt, wt)
    h_th = hz_kms(data[:, 0], hz_arr)
    return float(np.sum(((data[:, 1] - h_th) / data[:, 2])**2))


# ══════════════════════════════════════════════════════════════════════════
# 2. BAO histórico (DV/rs)
# ══════════════════════════════════════════════════════════════════════════

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
    return np.array(rows)


def chi2_bao_hist(theta, data, rd_mpc):
    H0, om, ob, os0, zt, wt = theta
    chi_arr, hz_arr = _build_integrals(H0, om, os0, zt, wt)
    z = data[:, 0]
    dm = dm_mpc(z, H0, chi_arr)
    dh = dh_mpc(z, hz_arr)
    dv = (z * dm**2 * dh)**(1./3.)
    dv_th = dv / rd_mpc
    return float(np.sum(((data[:, 1] - dv_th) / data[:, 2])**2))


# ══════════════════════════════════════════════════════════════════════════
# 3. DESI DR2 BAO — blocos de covariância 2×2
# ══════════════════════════════════════════════════════════════════════════

def load_desi_dr2():
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
            blocks.append({'type': 'iso', 'z': float(r['z_eff']),
                           'obs': float(r['value']), 'sig': float(r['sigma'])})
        else:
            dm_r = next(r for r in rows if r['observable'] == 'DM_over_rd')
            dh_r = next(r for r in rows if r['observable'] == 'DH_over_rd')
            blocks.append({'type': 'aniso', 'z': float(dm_r['z_eff']),
                           'dm_obs': float(dm_r['value']), 'dm_sig': float(dm_r['sigma']),
                           'dh_obs': float(dh_r['value']), 'dh_sig': float(dh_r['sigma']),
                           'rho': float(dm_r['correlation_coefficient'])})
    return blocks


def chi2_desi_dr2(theta, blocks, rd_mpc):
    H0, om, ob, os0, zt, wt = theta
    chi_arr, hz_arr = _build_integrals(H0, om, os0, zt, wt)
    total = 0.0
    for b in blocks:
        z = b['z']
        chi_z = np.interp(z, _ZG, chi_arr)
        hz_z  = np.interp(z, _ZG, hz_arr)
        dm = (C_KMS / H0) * chi_z
        dh = C_KMS / hz_z
        if b['type'] == 'iso':
            dv = (z * dm**2 * dh)**(1./3.)
            total += ((b['obs'] - dv/rd_mpc) / b['sig'])**2
        else:
            d1 = (b['dm_obs'] - dm/rd_mpc) / b['dm_sig']
            d2 = (b['dh_obs'] - dh/rd_mpc) / b['dh_sig']
            rho = b['rho']
            total += (d1**2 - 2.*rho*d1*d2 + d2**2) / (1.0 - rho**2)
    return float(total)


# ══════════════════════════════════════════════════════════════════════════
# 4. Pantheon+SH0ES — marginalização analítica de M_B
# ══════════════════════════════════════════════════════════════════════════

def load_pantheon():
    with open(PANTHEON_PATH) as f:
        header = f.readline().split()
    idx = {name: i for i, name in enumerate(header)}
    data = np.genfromtxt(PANTHEON_PATH, skip_header=1, dtype=str)
    z   = data[:, idx["zHD"]].astype(float)
    mu  = data[:, idx["MU_SH0ES"]].astype(float)
    err = data[:, idx["MU_SH0ES_ERR_DIAG"]].astype(float)
    cal = data[:, idx["IS_CALIBRATOR"]].astype(float)
    mask = cal == 0
    return z[mask], mu[mask], err[mask]


def chi2_sn(theta, sn_data):
    H0, om, ob, os0, zt, wt = theta
    z_arr, mu_obs, mu_err = sn_data
    chi_arr, _ = _build_integrals(H0, om, os0, zt, wt)
    chi_z = np.interp(z_arr, _ZG, chi_arr)
    dl = (1.0 + z_arr) * (C_KMS / H0) * chi_z
    dl = np.maximum(dl, 1e-10)
    mu_th = 5.0 * np.log10(dl) + 25.0
    delta = mu_obs - mu_th
    w = 1.0 / mu_err**2
    mb_opt = np.sum(delta * w) / np.sum(w)
    res = delta - mb_opt
    return float(np.sum(w * res**2))


# ══════════════════════════════════════════════════════════════════════════
# 5. CMB shift Planck 2018 — covariância 3×3
# ══════════════════════════════════════════════════════════════════════════

def load_cmb_shift():
    with open(DATA / "CMB_shift_real.json") as f:
        d = json.load(f)
    obs = np.array([d['R_obs'], d['la_obs'], d['ob_h2_obs']])
    cov_inv = np.linalg.inv(np.array(d['covariance']))
    return {'obs': obs, 'cov_inv': cov_inv, 'z_cmb': float(d['z_CMB'])}


def chi2_cmb(theta, cmb_data, rd_mpc):
    H0, om, ob, os0, zt, wt = theta
    h = H0 / 100.
    ob_h2 = ob * h**2
    chi_arr, _ = _build_integrals(H0, om, os0, zt, wt)
    z_cmb = cmb_data['z_cmb']
    chi_cmb = np.interp(z_cmb, _ZG, chi_arr)
    R_th    = np.sqrt(om) * chi_cmb
    DM_cmb  = (C_KMS / H0) * chi_cmb
    l_A_th  = np.pi * DM_cmb / rd_mpc
    th = np.array([R_th, l_A_th, ob_h2])
    delta = cmb_data['obs'] - th
    return float(delta @ cmb_data['cov_inv'] @ delta)


# ══════════════════════════════════════════════════════════════════════════
# 6. Prior BBN em Ωb·h² — Cooke et al. 2018
# ══════════════════════════════════════════════════════════════════════════

def chi2_bbn(theta):
    H0, om, ob, os0, zt, wt = theta
    h = H0 / 100.
    ob_h2 = ob * h**2
    return ((ob_h2 - BBN_OBH2) / BBN_OBH2_SIG)**2


# ══════════════════════════════════════════════════════════════════════════
# χ² total (calcula rd numérico uma vez por avaliação)
# ══════════════════════════════════════════════════════════════════════════

def chi2_total(theta, datasets):
    H0, om, ob, os0, zt, wt = theta
    if ob <= 0 or om <= 0.10 or os0 < 0 or wt <= 0:
        return 1e12
    ol = 1.0 - om - OMEGA_R - os0
    if ol < 0.0 or (om + os0 + OMEGA_R) > 0.995:
        return 1e12
    try:
        moresco, bao_hist, desi_blocks, sn_data, cmb_data = datasets
        rd = compute_rd_numerical(H0, om, ob, os0, zt, wt)
        return (chi2_moresco(theta, moresco)
                + chi2_bao_hist(theta, bao_hist, rd)
                + chi2_desi_dr2(theta, desi_blocks, rd)
                + chi2_sn(theta, sn_data)
                + chi2_cmb(theta, cmb_data, rd)
                + chi2_bbn(theta))
    except Exception:
        return 1e12


def chi2_lcdm(theta3, datasets):
    """χ² ΛCDM — parâmetros: (H0, om, ob)."""
    H0, om, ob = theta3
    os0, zt, wt = 0.0, 1.0, 0.3
    return chi2_total([H0, om, ob, os0, zt, wt], datasets)


# ══════════════════════════════════════════════════════════════════════════
# Otimização MAP
# ══════════════════════════════════════════════════════════════════════════

def _bbn_ob(H0):
    """Ωb tal que Ωb·h² = BBN_OBH2 (prior centrado)."""
    return BBN_OBH2 / (H0 / 100.)**2


# Pontos de partida com Ωb ancorado no prior BBN (Ωb·h² ≈ 0.02236)
# Cobrindo H₀ ∈ [64, 72] e Ωm ∈ [0.26, 0.33] para escapar de mínimos locais
_STARTS_6D = [
    # Planck-like (referência CMB)
    [67.4, 0.315, _bbn_ob(67.4), 0.000, 1.0, 0.30],
    [67.4, 0.315, _bbn_ob(67.4), 0.010, 0.8, 0.30],
    # H₀ um pouco menor
    [66.0, 0.320, _bbn_ob(66.0), 0.000, 1.0, 0.30],
    [65.0, 0.330, _bbn_ob(65.0), 0.000, 1.2, 0.40],
    # H₀ um pouco maior (explorar tensão)
    [68.5, 0.308, _bbn_ob(68.5), 0.000, 1.0, 0.30],
    [70.0, 0.295, _bbn_ob(70.0), 0.000, 1.0, 0.30],
    # Pontos com z_t alternativo
    [67.0, 0.312, _bbn_ob(67.0), 0.005, 0.5, 0.20],
    [67.4, 0.318, _bbn_ob(67.4), 0.020, 2.0, 0.50],
    # Fallback: pontos sem ancoragem BBN (como FASE 17)
    [67.4, 0.315, 0.049, 0.000, 1.0, 0.30],
    [68.5, 0.310, 0.049, 0.000, 1.0, 0.30],
]

_NM_OPTS = {'xatol': 1e-6, 'fatol': 1e-6, 'maxiter': 10000, 'adaptive': True}


def optimize_6d(datasets):
    best, best_val = None, 1e15
    for x0 in _STARTS_6D:
        try:
            res = minimize(lambda x: chi2_total(x, datasets), x0,
                           method='Nelder-Mead', options=_NM_OPTS)
            if res.fun < best_val:
                best_val = res.fun
                best = res
        except Exception:
            pass
    return best


def optimize_lcdm(datasets):
    starts = [[67.4, 0.315, 0.049], [68.5, 0.300, 0.048], [70.0, 0.310, 0.050]]
    best, best_val = None, 1e15
    for x0 in starts:
        try:
            res = minimize(lambda x: chi2_lcdm(x, datasets), x0,
                           method='Nelder-Mead', options=_NM_OPTS)
            if res.fun < best_val:
                best_val = res.fun
                best = res
        except Exception:
            pass
    return best


# ══════════════════════════════════════════════════════════════════════════
# Profile likelihood: grade 10×10 em (Ωs0, z_t)
# ══════════════════════════════════════════════════════════════════════════

_OS0_GRID = np.array([0.000, 0.001, 0.003, 0.005, 0.010, 0.020,
                      0.030, 0.050, 0.070, 0.100])
_ZT_GRID  = np.array([0.3, 0.5, 0.7, 0.9, 1.1, 1.4, 1.7, 2.0, 2.5, 3.0])

def _starts_4d():
    """Pontos de partida para profile (wt livre, os0 e z_t fixos)."""
    return [
        [67.4, 0.315, _bbn_ob(67.4), 0.30],
        [66.0, 0.320, _bbn_ob(66.0), 0.30],
        [68.5, 0.308, _bbn_ob(68.5), 0.30],
        [67.4, 0.315, 0.049,         0.30],   # fallback sem BBN
    ]
_STARTS_4D = _starts_4d()


def profile_likelihood(datasets):
    results = []
    total = len(_OS0_GRID) * len(_ZT_GRID)
    idx = 0
    for os0 in _OS0_GRID:
        for zt in _ZT_GRID:
            idx += 1
            def local_obj(x4, _os0=os0, _zt=zt):
                H0, om, ob, wt = x4
                return chi2_total([H0, om, ob, _os0, _zt, wt], datasets)
            best_c2, best_x = 1e15, None
            for x0 in _STARTS_4D:
                try:
                    res = minimize(local_obj, x0, method='Nelder-Mead',
                                   options={'xatol': 1e-5, 'fatol': 1e-5,
                                            'maxiter': 5000, 'adaptive': True})
                    if res.fun < best_c2:
                        best_c2 = res.fun
                        best_x = res.x
                except Exception:
                    pass
            c2 = float(best_c2)
            results.append({'os0': float(os0), 'zt': float(zt), 'chi2': c2,
                             'H0': float(best_x[0]) if best_x is not None else None,
                             'om': float(best_x[1]) if best_x is not None else None})
            print(f"  [{idx:3d}/{total}] Ωs0={os0:.3f}, z_t={zt:.1f} → χ²={c2:.3f}")
            sys.stdout.flush()
    return results


# ══════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 65)
    print("  RLL FASE 18 — rd Numérico + Prior BBN")
    print("  5 datasets · 6 parâmetros · BBN · profile 10×10")
    print("=" * 65)

    # ── Carregar dados ──────────────────────────────────────────────────
    print("\n[1/5] Moresco H(z) 2022 ...")
    moresco = load_moresco()
    print(f"      {len(moresco)} pontos")

    print("[2/5] BAO histórico ...")
    bao_hist = load_bao_hist()
    print(f"      {len(bao_hist)} pontos")

    print("[3/5] DESI DR2 BAO 2025 ...")
    desi_blocks = load_desi_dr2()
    n_desi = sum(2 if b['type']=='aniso' else 1 for b in desi_blocks)
    print(f"      {len(desi_blocks)} tracers → {n_desi} dados")

    print("[4/5] Pantheon+SH0ES ...")
    sn_data = load_pantheon()
    print(f"      {len(sn_data[0])} SNe")

    print("[5/5] CMB shift Planck 2018 ...")
    cmb_data = load_cmb_shift()
    print(f"      R_obs={cmb_data['obs'][0]:.4f}, l_A_obs={cmb_data['obs'][1]:.3f}")

    n_total = len(moresco) + len(bao_hist) + n_desi + len(sn_data[0]) + 3
    print(f"\n  Total de dados: {n_total} = {len(moresco)} + {len(bao_hist)} + "
          f"{n_desi} + {len(sn_data[0])} + 3")
    print(f"  Prior BBN: Ωb·h² = {BBN_OBH2} ± {BBN_OBH2_SIG} (Cooke+ 2018)\n")

    datasets = (moresco, bao_hist, desi_blocks, sn_data, cmb_data)

    # ── MAP RLL (6 parâmetros) ─────────────────────────────────────────
    print("── Otimização MAP RLL (6 parâmetros) ─────────────────────────")
    res_rll = optimize_6d(datasets)
    H0, om, ob, os0, zt, wt = res_rll.x
    h = H0 / 100.
    ob_h2 = ob * h**2
    om_h2 = om * h**2
    ol    = 1.0 - om - OMEGA_R - os0
    rd    = compute_rd_numerical(H0, om, ob, os0, zt, wt)
    zdrag = _zdrag_EH98(om_h2, ob_h2)

    c2_mor = chi2_moresco(res_rll.x, moresco)
    c2_bao = chi2_bao_hist(res_rll.x, bao_hist, rd)
    c2_des = chi2_desi_dr2(res_rll.x, desi_blocks, rd)
    c2_sn  = chi2_sn(res_rll.x, sn_data)
    c2_cmb = chi2_cmb(res_rll.x, cmb_data, rd)
    c2_bbn = chi2_bbn(res_rll.x)
    c2_tot = res_rll.fun

    print(f"  H₀  = {H0:.4f} km/s/Mpc")
    print(f"  Ωm  = {om:.5f}")
    print(f"  Ωb  = {ob:.5f}  (Ωb·h² = {ob_h2:.5f})")
    print(f"  Ωs0 = {os0:.6f}")
    print(f"  z_t = {zt:.4f}")
    print(f"  w_t = {wt:.4f}")
    print(f"  ΩΛ  = {ol:.5f}")
    print(f"  z_drag  = {zdrag:.2f}")
    print(f"  rd      = {rd:.4f} Mpc  (integral numérica)")
    print()
    print(f"  χ² breakdown:")
    print(f"    Moresco H(z)   : {c2_mor:.3f}  / {len(moresco)}  = {c2_mor/len(moresco):.4f}/pt")
    print(f"    BAO histórico  : {c2_bao:.3f}  / {len(bao_hist)}  = {c2_bao/len(bao_hist):.4f}/pt")
    print(f"    DESI DR2 BAO   : {c2_des:.3f} / {n_desi} = {c2_des/n_desi:.4f}/pt")
    print(f"    Pantheon+SH0ES : {c2_sn:.3f} / {len(sn_data[0])} = {c2_sn/len(sn_data[0]):.4f}/pt")
    print(f"    CMB shift      : {c2_cmb:.4f} / 3  = {c2_cmb/3:.5f}/pt")
    print(f"    Prior BBN      : {c2_bbn:.4f}  (contribuição ao χ²_total)")
    print(f"    TOTAL          : {c2_tot:.3f} / {n_total} = {c2_tot/n_total:.5f}/pt")

    # ── MAP ΛCDM (3 parâmetros) ────────────────────────────────────────
    print()
    print("── Otimização MAP ΛCDM (3 parâmetros: H₀, Ωm, Ωb) ──────────")
    res_lcdm = optimize_lcdm(datasets)
    H0l, oml, obl = res_lcdm.x
    hl = H0l / 100.
    rdl = compute_rd_numerical(H0l, oml, obl, 0.0, 1.0, 0.3)
    c2_lcdm = res_lcdm.fun
    print(f"  H₀  = {H0l:.4f} km/s/Mpc")
    print(f"  Ωm  = {oml:.5f}")
    print(f"  Ωb  = {obl:.5f}  (Ωb·h² = {obl*hl**2:.5f})")
    print(f"  rd  = {rdl:.4f} Mpc")
    print(f"  χ²  = {c2_lcdm:.3f}")

    k_rll, k_lcdm = 6, 3
    delta_chi2 = c2_tot - c2_lcdm
    delta_aic  = (c2_tot + 2*k_rll) - (c2_lcdm + 2*k_lcdm)
    delta_bic  = (c2_tot + k_rll*np.log(n_total)) - (c2_lcdm + k_lcdm*np.log(n_total))
    ln_b10     = -delta_bic / 2.0
    print()
    print(f"  Comparação:")
    print(f"    Δχ²(RLL−ΛCDM)  = {delta_chi2:.4f}")
    print(f"    ΔAIC(RLL−ΛCDM) = {delta_aic:.4f}  (k_RLL={k_rll}, k_ΛCDM={k_lcdm})")
    print(f"    ΔBIC(RLL−ΛCDM) = {delta_bic:.4f}")
    print(f"    ln(B₁₀)_Bayes  = {ln_b10:.4f}  (−ΔBIC/2)")

    # ── Profile likelihood ─────────────────────────────────────────────
    print()
    print("── Profile likelihood: grade 10×10 em (Ωs0 × z_t) ──────────")
    prof_rows = profile_likelihood(datasets)

    # Resumo por Ωs0 (mínimo sobre z_t)
    profile_by_os0 = {}
    for r in prof_rows:
        os0_v = r['os0']
        if os0_v not in profile_by_os0 or r['chi2'] < profile_by_os0[os0_v]['chi2']:
            profile_by_os0[os0_v] = r
    chi2_min = min(r['chi2'] for r in prof_rows)

    print()
    print(f"  Mínimo do profile: Ωs0={min(profile_by_os0, key=lambda k: profile_by_os0[k]['chi2']):.3f}")
    print(f"    χ²_profile_min = {chi2_min:.3f}")
    print(f"    vs χ²_ΛCDM    = {c2_lcdm:.3f}")
    print(f"    Δχ²_profile    = {chi2_min - c2_lcdm:.4f}")
    print()
    print("  Profile likelihood — χ²_min(Ωs0) = min_{z_t} χ²(Ωs0, z_t):")
    print(f"  {'Ωs0':>8} {'χ²_min':>10} {'Δχ² vs 0':>10} {'z_t_opt':>8} {'H₀':>8} {'Ωm':>7}")
    os0_vals = sorted(profile_by_os0.keys())
    chi2_at_zero = profile_by_os0[0.0]['chi2']
    for os0_v in os0_vals:
        r = profile_by_os0[os0_v]
        zt_opt = r['zt']
        h0_opt = r['H0'] or float('nan')
        om_opt = r['om'] or float('nan')
        dchi2  = r['chi2'] - chi2_at_zero
        print(f"  {os0_v:8.3f} {r['chi2']:10.3f} {dchi2:>+10.3f} {zt_opt:8.1f} {h0_opt:8.3f} {om_opt:7.4f}")

    # ── Comparação com FASE 17 ─────────────────────────────────────────
    print()
    print("── Comparação FASE 17 vs FASE 18 ────────────────────────────")
    print(f"  rd (E&H FASE 17)    = 151.554 Mpc")
    print(f"  rd (numérico F18)   = {rd:.4f} Mpc")
    print(f"  Δrd                 = {rd - 151.554:.4f} Mpc")
    print(f"  χ²_CMB (FASE 17)    = 19.6846")
    print(f"  χ²_CMB (FASE 18)    = {c2_cmb:.4f}")
    print(f"  Δχ²_CMB             = {c2_cmb - 19.6846:.4f}")
    print(f"  Ωb·h² (FASE 17)     = 0.02284 (livre, sem prior)")
    print(f"  Ωb·h² (FASE 18)     = {ob_h2:.5f} (com prior BBN)")

    # ── Salvar JSON ────────────────────────────────────────────────────
    RESULTS.mkdir(exist_ok=True)
    out = {
        "metadata": {
            "fase": "FASE 18",
            "melhorias": ["rd_numerico_integral", "prior_bbn_obh2"],
            "status_epistemico": "[E] análise completa — rd numérico + prior BBN",
            "referencia_rd": "Eisenstein & Hu 1998 (z_drag) + integral numérica r_s",
            "referencia_bbn": "Cooke, Pettini & Steidel 2018 arXiv:1710.11129",
            "n_total": n_total
        },
        "prior_bbn": {
            "ob_h2_center": BBN_OBH2,
            "ob_h2_sigma": BBN_OBH2_SIG
        },
        "map_rll_6param": {
            "H0": H0, "om": om, "ob": ob, "os0": os0, "zt": zt, "wt": wt,
            "ol": ol, "ob_h2": ob_h2,
            "z_drag": zdrag, "rd_mpc_numerico": rd,
            "chi2_total": c2_tot,
            "chi2_breakdown": {
                "moresco_hz": c2_mor, "bao_historico": c2_bao,
                "desi_dr2": c2_des, "pantheon_sn": c2_sn,
                "cmb_shift": c2_cmb, "prior_bbn": c2_bbn
            }
        },
        "map_lcdm_3param": {
            "H0": H0l, "om": oml, "ob": obl,
            "ob_h2": obl * hl**2, "rd_mpc_numerico": rdl,
            "chi2_total": c2_lcdm
        },
        "comparacao_modelos": {
            "delta_chi2": delta_chi2, "delta_aic": delta_aic,
            "delta_bic": delta_bic, "ln_B10_Jeffreys": ln_b10,
            "k_rll": k_rll, "k_lcdm": k_lcdm, "n_dados": n_total
        },
        "comparacao_fase17": {
            "rd_EH_fase17": 151.554,
            "rd_numerico_fase18": rd,
            "delta_rd": rd - 151.554,
            "chi2_cmb_fase17": 19.6846,
            "chi2_cmb_fase18": c2_cmb,
            "delta_chi2_cmb": c2_cmb - 19.6846
        },
        "profile_likelihood": prof_rows,
        "profile_summary_by_os0": [
            {"os0": os0_v,
             "chi2_min": profile_by_os0[os0_v]['chi2'],
             "delta_chi2": profile_by_os0[os0_v]['chi2'] - chi2_at_zero,
             "zt_opt": profile_by_os0[os0_v]['zt'],
             "H0_opt": profile_by_os0[os0_v]['H0'],
             "om_opt": profile_by_os0[os0_v]['om']}
            for os0_v in os0_vals
        ]
    }
    out_path = RESULTS / "rll_fase18_rd_numerico.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\n  JSON salvo: {out_path}")

    print()
    print("=" * 65)
    print("  CONCLUSÃO FASE 18")
    print("=" * 65)
    print(f"  rd numérico          = {rd:.4f} Mpc  (E&H: 151.554 Mpc)")
    print(f"  Ωb·h² (MAP+BBN)      = {ob_h2:.5f} ≈ {BBN_OBH2} (BBN)")
    print(f"  χ²_CMB/3 FASE 17     = {19.6846/3:.4f}  ← tensão alta")
    print(f"  χ²_CMB/3 FASE 18     = {c2_cmb/3:.4f}  ← melhora?")
    print(f"  Ωs0 MAP              = {os0:.6f}  → colapso ΛCDM mantido")
    print(f"  ΔBIC                 = {delta_bic:.4f}")
    print(f"  ln(B₁₀)              = {ln_b10:.4f}")
    print("=" * 65)


if __name__ == "__main__":
    main()
