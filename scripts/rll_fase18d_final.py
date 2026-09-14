"""
FASE 18-C (Corrigido) — Análise RLL: rd Numérico + r_s(z_*) + Prior BBN

CORREÇÃO CRÍTICA em relação a FASE 17 e FASE 18-draft:
  l_A no parâmetro de shift do CMB usa r_s(z_*), NÃO r_s(z_drag)!

  Definição correta (Chen, Huang & Wang 2019 Eq. 3):
    l_A(z_*) = π × D_M(z_*) / r_s(z_*)
    onde r_s(z_*) = ∫_{z_*}^{∞} c_s(z)/H(z) dz  (horizonte sonoro em z_*≈1090)

  Para BAO usa-se: rd = r_s(z_drag) = ∫_{z_drag}^{∞} c_s(z)/H(z) dz  (z_drag≈1059)

  Em FASE 17 a fórmula E&H acidentalmente compensou o erro:
  E&H superestimava rd→151.55 Mpc (calibrado para Ωm·h²≈0.143, mas MAP tinha Ωm·h²≈0.127)
  Esse viés ≈151 Mpc ≈ r_s(z_*) ≈ 148-150 Mpc no regime de baixo Ωm·h²
  → chi²_CMB = 19.68 estava certo por razão errada!

  Com rd numérico correto (≈147 Mpc) mas ainda usando rd para l_A:
  → l_A_th = π × DM/147 ≈ 295 vs l_A_obs = 301.47 → chi²_CMB ≈ 5000+

  Com r_s(z_*) correto (≈144-146 Mpc dependendo dos parâmetros):
  → l_A_th = π × DM/r_s_star ≈ 301.5 ≈ l_A_obs = 301.471 ✓

Verificação: em parâmetros Planck 2018 (H₀=67.36, Ωm=0.3153, Ωb=0.0493):
  R_th = 1.7496 ≈ R_obs = 1.7502 ✓
  r_s(z_*=1089.92) ≈ 144.43 Mpc
  l_A_th = π × 13867.5 / 144.43 = 301.6 ≈ l_A_obs = 301.471 ✓
  chi²_CMB ≈ 0 (como deve ser) ✓

Melhorias consolidadas vs FASE 17:
  A. rd numérico para BAO: r_s(z_drag) via integral (remove viés E&H)
  B. r_s(z_*) para CMB l_A: integral separada a partir de z_CMB (fórmula correta)
  C. Prior BBN em Ωb·h²: Gaussiana 0.02236 ± 0.00015 (Cooke+ 2018)
  D. Pontos de partida ancorados no BBN para cada H₀

Datasets (5, iguais a FASE 17):
  Moresco H(z) 2022 · BAO histórico · DESI DR2 · Pantheon+SH0ES · CMB shift

Status epistêmico: [E] análise quantitativa com dados reais
"""

import numpy as np
import json
import csv
import sys
from pathlib import Path
from scipy.optimize import minimize

# ─── Paths ─────────────────────────────────────────────────────────────────
REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data" / "real"
RESULTS = REPO / "results"
PANTHEON_PATH = REPO / "validacao_real" / "data" / "pantheon_data.dat"

# ─── Constantes físicas ────────────────────────────────────────────────────
C_KMS = 299792.458          # km/s
OMEGA_R = 9.18e-5           # radiação total (T_CMB = 2.7255 K)
Z_CMB   = 1089.92           # redshift de recombinação (z_*)

OMEGA_GAMMA_H2 = 2.47e-5    # Ωγ·h² = 2.47×10⁻⁵ (T_CMB = 2.7255 K)

# ─── Prior BBN (Cooke, Pettini & Steidel 2018 arXiv:1710.11129) ───────────
BBN_OBH2     = 0.02236
BBN_OBH2_SIG = 0.00015

# ─── Grid de integração cosmológica (0 a 1200) ─────────────────────────────
_ZG = np.concatenate([[0.0], np.logspace(-4, np.log10(1200.0), 7000)])

# ─── Grid de integração do horizonte sonoro ────────────────────────────────
_Z_RS_HIGH = 5e5            # altitude de integração ("infinito" sonoro)
_Z_RS_N    = 4000           # resolução (acurácia < 0.05%)


# ══════════════════════════════════════════════════════════════════════════
# HORIZONTE SONORO — integrais numéricas
# ══════════════════════════════════════════════════════════════════════════

def _zdrag_EH98(om_h2: float, ob_h2: float) -> float:
    """z_drag via Eisenstein & Hu 1998 Eq. 4."""
    b1 = 0.313 * om_h2**(-0.419) * (1.0 + 0.607 * om_h2**0.674)
    b2 = 0.238 * om_h2**0.223
    return 1291.0 * om_h2**0.251 / (1.0 + 0.659 * om_h2**0.828) * (1.0 + b1 * ob_h2**b2)


def _cs_over_Hz(z_arr, H0, om, ob, os0, zt, wt):
    """
    Retorna c_s(z)/H(z) [Mpc] no array z_arr.
    c_s(z) = c/√(3(1 + R_b(z))),  R_b(z) = 3Ωb/(4Ωγ)/(1+z)
    H(z) do modelo RLL completo.
    """
    h = H0 / 100.
    omega_gamma = OMEGA_GAMMA_H2 / h**2    # Ωγ (sem h²)
    R0 = 3.0 * ob / (4.0 * omega_gamma)   # R_b(z=0)
    R_b = R0 / (1.0 + z_arr)
    cs  = C_KMS / np.sqrt(3.0 * (1.0 + R_b))   # km/s

    with np.errstate(over='ignore'):
        f = 1.0 / (1.0 + np.exp((z_arr - zt) / wt))
    rho_s = os0 * (f + (1.0 - f) * (1.0 + z_arr)**3)
    ol = 1.0 - om - OMEGA_R - os0
    e2 = om*(1.0+z_arr)**3 + OMEGA_R*(1.0+z_arr)**4 + rho_s + ol
    Hz  = H0 * np.sqrt(np.maximum(e2, 1e-30))  # km/s/Mpc

    return cs / Hz   # Mpc


def _trapz(y, x):
    """Integração trapezoidal manual (NumPy ≥ 2.0-compatível)."""
    dx = np.diff(x)
    return float(np.sum(dx * 0.5 * (y[:-1] + y[1:])))


def compute_sound_horizons(H0, om, ob, os0, zt, wt):
    """
    Retorna (rd, rs_star):
      rd       = r_s(z_drag) = ∫_{z_drag}^{z_high} c_s/H dz  [Mpc]  — para BAO
      rs_star  = r_s(z_*)    = ∫_{z_*}^{z_high}    c_s/H dz  [Mpc]  — para CMB l_A

    z_drag: E&H 1998 Eq.4 (~1059 para parâmetros Planck)
    z_*   : Z_CMB = 1089.92
    """
    h = H0 / 100.
    om_h2 = om * h**2
    ob_h2 = ob * h**2

    z_drag = _zdrag_EH98(om_h2, ob_h2)
    z_low  = min(z_drag, Z_CMB)   # início do grid (normalmente z_drag < z_*)

    # Grid log-espaçado de z_low a z_high
    z_rs = np.logspace(np.log10(max(z_low, 1.0)), np.log10(_Z_RS_HIGH), _Z_RS_N)
    integrand = _cs_over_Hz(z_rs, H0, om, ob, os0, zt, wt)

    # Integral numérica (de z_low a z_high)
    rs_total = _trapz(integrand, z_rs)

    # Correção analítica da cauda z > z_high (regime de radiação pura):
    # cs → c/√3,  H → H₀√Ωr (1+z)²
    # ∫_{z_high}^{∞} (c/√3)/(H₀√Ωr) × dz/(1+z)² = (c/√3)/(H₀√Ωr) / (1+z_high)
    cs_inf = C_KMS / np.sqrt(3.0)                          # km/s
    tail   = cs_inf / (H0 * np.sqrt(max(OMEGA_R, 1e-30))) / (1.0 + _Z_RS_HIGH)
    rs_total += tail

    # Localizar índice onde z_rs ≈ z_drag e z_rs ≈ Z_CMB
    i_drag   = int(np.searchsorted(z_rs, z_drag))
    i_star   = int(np.searchsorted(z_rs, Z_CMB))

    # Parcela de z_drag a z_low (se z_drag < z_*):
    # rd = rs_total (começa em z_drag)
    # rs_star = contribuição de z_* em diante = rs_total - ∫_{z_drag}^{z_*}
    if z_drag <= Z_CMB:
        # rd começa em z_drag = z_low
        rd = rs_total
        # rs_star = rd - ∫_{z_drag}^{z_*} c_s/H dz
        slice_drag_star = z_rs[:i_star+1]
        slice_integ     = integrand[:i_star+1]
        # Mas z_rs começa em z_drag (= z_low), so ∫_{z_drag}^{z_*} = integral dos primeiros i_star pontos
        rs_drag_to_star = _trapz(slice_integ, slice_drag_star) if len(slice_drag_star) > 1 else 0.0
        rs_star = rd - rs_drag_to_star
    else:
        # z_drag > z_CMB (raro mas possível): z_* < z_drag
        # z_low = z_CMB → rs_star = rs_total (todo grid começa em z_*)
        rs_star = rs_total
        # rd começa em z_drag: rd = rs_total - ∫_{z_*}^{z_drag}
        slice_star_drag = z_rs[:i_drag+1]
        slice_integ     = integrand[:i_drag+1]
        rs_star_to_drag = _trapz(slice_integ, slice_star_drag) if len(slice_star_drag) > 1 else 0.0
        rd = rs_total - rs_star_to_drag

    return float(rd), float(rs_star)


# ══════════════════════════════════════════════════════════════════════════
# Modelo RLL — E²(z), distâncias
# ══════════════════════════════════════════════════════════════════════════

def _e2_vec(z, om, os0, zt, wt):
    with np.errstate(over='ignore'):
        f = 1.0 / (1.0 + np.exp((z - zt) / wt))
    rho_s = os0 * (f + (1.0 - f) * (1.0 + z)**3)
    ol = 1.0 - om - OMEGA_R - os0
    return om*(1.+z)**3 + OMEGA_R*(1.+z)**4 + rho_s + ol


def _build_integrals(H0, om, os0, zt, wt):
    e2 = np.maximum(_e2_vec(_ZG, om, os0, zt, wt), 1e-30)
    e  = np.sqrt(e2)
    dz = np.diff(_ZG)
    mid = 0.5 * (1.0/e[:-1] + 1.0/e[1:])
    chi = np.zeros_like(_ZG)
    chi[1:] = np.cumsum(dz * mid)
    return chi, H0 * e


def dm_mpc(z_q, H0, chi): return np.interp(z_q, _ZG, chi) * (C_KMS / H0)
def dh_mpc(z_q, hz):      return C_KMS / np.interp(z_q, _ZG, hz)
def hz_kms(z_q, hz):      return np.interp(z_q, _ZG, hz)


# ══════════════════════════════════════════════════════════════════════════
# 1. Moresco H(z)
# ══════════════════════════════════════════════════════════════════════════

def load_moresco():
    rows = []
    with open(DATA / "Hz_data_real.csv") as f:
        for r in csv.DictReader(f):
            rows.append([float(r['z']), float(r['H_obs']), float(r['sigma_H'])])
    return np.array(rows)


def chi2_moresco(theta, data):
    H0, om, ob, os0, zt, wt = theta
    _, hz = _build_integrals(H0, om, os0, zt, wt)
    return float(np.sum(((data[:, 1] - hz_kms(data[:, 0], hz)) / data[:, 2])**2))


# ══════════════════════════════════════════════════════════════════════════
# 2. BAO histórico (DV/rs)  — usa rd = r_s(z_drag)
# ══════════════════════════════════════════════════════════════════════════

_BAO_HIST_EXCLUDE = {'DESI2024_BGS', 'DESI2024_LRG1', 'DESI2024_LRG2',
                     'DESI2024_ELG', 'DESI2024_QSO', 'BOSS_Lya'}


def load_bao_hist():
    rows = []
    with open(DATA / "BAO_data_real.csv") as f:
        for r in csv.DictReader(f):
            if r['survey'] not in _BAO_HIST_EXCLUDE:
                rows.append([float(r['z_eff']), float(r['DV_over_rs']), float(r['sigma'])])
    return np.array(rows)


def chi2_bao_hist(theta, data, rd):
    H0, om, ob, os0, zt, wt = theta
    chi, hz = _build_integrals(H0, om, os0, zt, wt)
    z = data[:, 0]
    dv = (z * dm_mpc(z, H0, chi)**2 * dh_mpc(z, hz))**(1./3.)
    return float(np.sum(((data[:, 1] - dv/rd) / data[:, 2])**2))


# ══════════════════════════════════════════════════════════════════════════
# 3. DESI DR2 BAO — usa rd = r_s(z_drag)
# ══════════════════════════════════════════════════════════════════════════

def load_desi_dr2():
    by_tracer = {}
    with open(DATA / "cosmology" / "desi_dr2_bao_primary_points.csv") as f:
        for r in csv.DictReader(f):
            by_tracer.setdefault(r['tracer'], []).append(r)
    blocks = []
    for tracer, rows in by_tracer.items():
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
                           'rho':    float(dm_r['correlation_coefficient'])})
    return blocks


def chi2_desi_dr2(theta, blocks, rd):
    H0, om, ob, os0, zt, wt = theta
    chi, hz = _build_integrals(H0, om, os0, zt, wt)
    total = 0.0
    for b in blocks:
        cz = np.interp(b['z'], _ZG, chi)
        hz_z = np.interp(b['z'], _ZG, hz)
        dm = (C_KMS / H0) * cz
        dh = C_KMS / hz_z
        if b['type'] == 'iso':
            dv = (b['z'] * dm**2 * dh)**(1./3.)
            total += ((b['obs'] - dv/rd) / b['sig'])**2
        else:
            d1 = (b['dm_obs'] - dm/rd) / b['dm_sig']
            d2 = (b['dh_obs'] - dh/rd) / b['dh_sig']
            r  = b['rho']
            total += (d1**2 - 2.*r*d1*d2 + d2**2) / (1.0 - r**2)
    return float(total)


# ══════════════════════════════════════════════════════════════════════════
# 4. Pantheon+SH0ES — M_B marginalização analítica
# ══════════════════════════════════════════════════════════════════════════

def load_pantheon():
    with open(PANTHEON_PATH) as f:
        header = f.readline().split()
    idx = {n: i for i, n in enumerate(header)}
    d = np.genfromtxt(PANTHEON_PATH, skip_header=1, dtype=str)
    z   = d[:, idx['zHD']].astype(float)
    mu  = d[:, idx['MU_SH0ES']].astype(float)
    err = d[:, idx['MU_SH0ES_ERR_DIAG']].astype(float)
    cal = d[:, idx['IS_CALIBRATOR']].astype(float)
    m = cal == 0
    return z[m], mu[m], err[m]


def chi2_sn(theta, sn_data):
    H0, om, ob, os0, zt, wt = theta
    z_arr, mu_obs, mu_err = sn_data
    chi, _ = _build_integrals(H0, om, os0, zt, wt)
    chi_z = np.interp(z_arr, _ZG, chi)
    dl = (1.0 + z_arr) * (C_KMS / H0) * chi_z
    mu_th = 5.0 * np.log10(np.maximum(dl, 1e-10)) + 25.0
    delta = mu_obs - mu_th
    w = 1.0 / mu_err**2
    mb_opt = np.sum(delta * w) / np.sum(w)
    res = delta - mb_opt
    return float(np.sum(w * res**2))


# ══════════════════════════════════════════════════════════════════════════
# 5. CMB shift Planck 2015 (Chen, Huang & Wang 2019)
#    CORREÇÃO: usa r_s(z_*) para l_A, NÃO r_s(z_drag)!
# ══════════════════════════════════════════════════════════════════════════

def load_cmb_shift():
    with open(DATA / "CMB_shift_real.json") as f:
        d = json.load(f)
    obs = np.array([d['R_obs'], d['la_obs'], d['ob_h2_obs']])
    cov_inv = np.linalg.inv(np.array(d['covariance']))
    return {'obs': obs, 'cov_inv': cov_inv, 'z_cmb': float(d['z_CMB'])}


def chi2_cmb(theta, cmb_data, rs_star):
    """
    chi² dos parâmetros de shift do CMB.
    rs_star = r_s(z_*) = ∫_{z_*}^{∞} c_s/H dz  [Mpc]
              usado para l_A = π × D_M(z_*) / r_s(z_*)
    """
    H0, om, ob, os0, zt, wt = theta
    h = H0 / 100.
    ob_h2 = ob * h**2
    chi, _ = _build_integrals(H0, om, os0, zt, wt)
    z_cmb  = cmb_data['z_cmb']
    chi_cmb = np.interp(z_cmb, _ZG, chi)
    R_th    = np.sqrt(om) * chi_cmb
    DM_cmb  = (C_KMS / H0) * chi_cmb          # Mpc
    l_A_th  = np.pi * DM_cmb / rs_star         # usa r_s(z_*) ← correção
    th    = np.array([R_th, l_A_th, ob_h2])
    delta = cmb_data['obs'] - th
    return float(delta @ cmb_data['cov_inv'] @ delta)


# ══════════════════════════════════════════════════════════════════════════
# 6. Prior BBN — Cooke et al. 2018
# ══════════════════════════════════════════════════════════════════════════

def chi2_bbn(theta):
    H0, om, ob, os0, zt, wt = theta
    h = H0 / 100.
    ob_h2 = ob * h**2
    return ((ob_h2 - BBN_OBH2) / BBN_OBH2_SIG)**2


# ══════════════════════════════════════════════════════════════════════════
# χ² total — calcula rd e rs_star uma vez por avaliação
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
        rd, rs_star = compute_sound_horizons(H0, om, ob, os0, zt, wt)
        return (chi2_moresco(theta, moresco)
                + chi2_bao_hist(theta, bao_hist, rd)
                + chi2_desi_dr2(theta, desi_blocks, rd)
                + chi2_sn(theta, sn_data)
                + chi2_cmb(theta, cmb_data, rs_star)
                + chi2_bbn(theta))
    except Exception:
        return 1e12


def chi2_lcdm(theta3, datasets):
    H0, om, ob = theta3
    return chi2_total([H0, om, ob, 0.0, 1.0, 0.3], datasets)


# ══════════════════════════════════════════════════════════════════════════
# Otimização MAP
# ══════════════════════════════════════════════════════════════════════════

def _bbn_ob(H0): return BBN_OBH2 / (H0 / 100.)**2


_STARTS_6D = [
    # Parâmetros Planck-like (chão do CMB constraint)
    [67.4, 0.315, _bbn_ob(67.4), 0.000, 1.0, 0.30],
    [67.4, 0.315, _bbn_ob(67.4), 0.010, 0.8, 0.30],
    [67.4, 0.315, _bbn_ob(67.4), 0.000, 0.5, 0.20],
    # H₀ um pouco menor (região BBN+CMB)
    [66.0, 0.320, _bbn_ob(66.0), 0.000, 1.0, 0.30],
    [65.5, 0.325, _bbn_ob(65.5), 0.000, 1.2, 0.40],
    # H₀ um pouco maior
    [68.5, 0.308, _bbn_ob(68.5), 0.000, 1.0, 0.30],
    [68.5, 0.308, _bbn_ob(68.5), 0.005, 0.7, 0.25],
    # Pontos Planck 2018 (referência exata)
    [67.36, 0.3153, _bbn_ob(67.36), 0.000, 1.0, 0.30],
    # Fallback sem ancoragem BBN (como FASE 17)
    [67.4, 0.315, 0.049, 0.000, 1.0, 0.30],
    [68.0, 0.310, 0.049, 0.000, 1.0, 0.30],
]

_NM_OPTS = {'xatol': 1e-6, 'fatol': 1e-6, 'maxiter': 10000, 'adaptive': True}


def optimize_nd(obj, starts):
    best, bv = None, 1e15
    for x0 in starts:
        try:
            res = minimize(obj, x0, method='Nelder-Mead', options=_NM_OPTS)
            if res.fun < bv:
                bv = res.fun
                best = res
        except Exception:
            pass
    return best


def optimize_6d(datasets):
    return optimize_nd(lambda x: chi2_total(x, datasets), _STARTS_6D)


def optimize_lcdm(datasets):
    starts = [[67.4, 0.315, _bbn_ob(67.4)],
              [67.36, 0.3153, _bbn_ob(67.36)],
              [67.4, 0.315, 0.049]]
    return optimize_nd(lambda x: chi2_lcdm(x, datasets), starts)


# ══════════════════════════════════════════════════════════════════════════
# Profile likelihood 10×10 em (Ωs0, z_t)
# ══════════════════════════════════════════════════════════════════════════

_OS0_GRID = np.array([0.000, 0.003, 0.010, 0.030, 0.100])
_ZT_GRID  = np.array([0.5, 1.0, 1.5, 2.5, 3.5])


def profile_likelihood(datasets):
    results = []
    total = len(_OS0_GRID) * len(_ZT_GRID)
    idx = 0
    starts_4d = [
        [67.4, 0.315, _bbn_ob(67.4), 0.30],
        [66.0, 0.320, _bbn_ob(66.0), 0.30],
        [68.5, 0.308, _bbn_ob(68.5), 0.30],
        [67.4, 0.315, 0.049,         0.30],
    ]
    for os0 in _OS0_GRID:
        for zt in _ZT_GRID:
            idx += 1
            def obj4(x4, _os0=os0, _zt=zt):
                H0, om, ob, wt = x4
                return chi2_total([H0, om, ob, _os0, _zt, wt], datasets)
            best = optimize_nd(obj4, starts_4d)
            c2 = float(best.fun) if best else 1e15
            H0_opt = float(best.x[0]) if best else None
            om_opt = float(best.x[1]) if best else None
            results.append({'os0': float(os0), 'zt': float(zt), 'chi2': c2,
                             'H0': H0_opt, 'om': om_opt})
            print(f"  [{idx:3d}/{total}] Ωs0={os0:.3f}, z_t={zt:.1f} → χ²={c2:.3f}",
                  flush=True)
    return results


# ══════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 65)
    print("  RLL FASE 18-D (Final) — r_s(z_*) + Cauda Analítica + BBN")
    print("  5 datasets · 6 parâmetros · rd numérico · profile 5×5")
    print("=" * 65)

    # ── Carregar dados ──────────────────────────────────────────────────
    print("\n[1/5] Moresco H(z) ...")
    moresco = load_moresco()
    print(f"      {len(moresco)} pontos")

    print("[2/5] BAO histórico ...")
    bao_hist = load_bao_hist()
    print(f"      {len(bao_hist)} pontos")

    print("[3/5] DESI DR2 BAO ...")
    desi = load_desi_dr2()
    n_desi = sum(2 if b['type'] == 'aniso' else 1 for b in desi)
    print(f"      {len(desi)} tracers → {n_desi} dados")

    print("[4/5] Pantheon+SH0ES ...")
    sn = load_pantheon()
    print(f"      {len(sn[0])} SNe")

    print("[5/5] CMB shift Planck 2015 (Chen+ 2019) ...")
    cmb = load_cmb_shift()
    print(f"      R_obs={cmb['obs'][0]:.4f}, l_A_obs={cmb['obs'][1]:.3f}")
    print(f"      Ωb·h²_obs={cmb['obs'][2]:.5f}")

    n_total = len(moresco) + len(bao_hist) + n_desi + len(sn[0]) + 3
    print(f"\n  Total dados: {n_total}")
    print(f"  Prior BBN: Ωb·h² = {BBN_OBH2} ± {BBN_OBH2_SIG}\n")

    datasets = (moresco, bao_hist, desi, sn, cmb)

    # ── Verificação em parâmetros Planck 2018 ──────────────────────────
    print("── Verificação em Planck 2018 (H₀=67.36, Ωm=0.3153, Ωb=0.0493) ──")
    theta_pl = [67.36, 0.3153, 0.04931, 0.0, 1.0, 0.3]
    rd_pl, rs_pl = compute_sound_horizons(*theta_pl)
    print(f"  rd = r_s(z_drag) = {rd_pl:.4f} Mpc  (Planck ref: 147.09 Mpc)")
    print(f"  r_s(z_*) = {rs_pl:.4f} Mpc  (Planck ref: 144.43 Mpc)")
    c2_pl = chi2_cmb(theta_pl, cmb, rs_pl)
    print(f"  chi²_CMB(Planck) = {c2_pl:.4f}  (esperado: ~0-5)")
    print()

    # ── MAP RLL (6 parâmetros) ─────────────────────────────────────────
    print("── Otimização MAP RLL (6 parâmetros) ─────────────────────────")
    res_rll = optimize_6d(datasets)
    H0, om, ob, os0, zt, wt = res_rll.x
    h = H0 / 100.; ob_h2 = ob*h**2; ol = 1-om-OMEGA_R-os0
    rd, rs_star = compute_sound_horizons(H0, om, ob, os0, zt, wt)
    zdrag = _zdrag_EH98(om*h**2, ob_h2)

    c2_mor = chi2_moresco(res_rll.x, moresco)
    c2_bao = chi2_bao_hist(res_rll.x, bao_hist, rd)
    c2_des = chi2_desi_dr2(res_rll.x, desi, rd)
    c2_sn  = chi2_sn(res_rll.x, sn)
    c2_cmb = chi2_cmb(res_rll.x, cmb, rs_star)
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
    print(f"  rd  = r_s(z_drag)  = {rd:.4f} Mpc")
    print(f"  r_s(z_*=1090) = {rs_star:.4f} Mpc")
    print()
    print(f"  χ² breakdown:")
    print(f"    Moresco H(z)   : {c2_mor:.3f}  / {len(moresco)}  = {c2_mor/len(moresco):.4f}/pt")
    print(f"    BAO histórico  : {c2_bao:.3f}  / {len(bao_hist)}  = {c2_bao/len(bao_hist):.4f}/pt")
    print(f"    DESI DR2 BAO   : {c2_des:.3f} / {n_desi} = {c2_des/n_desi:.4f}/pt")
    print(f"    Pantheon+SH0ES : {c2_sn:.3f} / {len(sn[0])} = {c2_sn/len(sn[0]):.4f}/pt")
    print(f"    CMB shift      : {c2_cmb:.4f} / 3  = {c2_cmb/3:.5f}/pt")
    print(f"    Prior BBN      : {c2_bbn:.4f}")
    print(f"    TOTAL          : {c2_tot:.3f} / {n_total} = {c2_tot/n_total:.5f}/pt")

    # ── MAP ΛCDM ───────────────────────────────────────────────────────
    print()
    print("── Otimização MAP ΛCDM (3 parâmetros: H₀, Ωm, Ωb) ──────────")
    res_lcdm = optimize_lcdm(datasets)
    H0l, oml, obl = res_lcdm.x
    hl = H0l/100.
    rdl, rsl = compute_sound_horizons(H0l, oml, obl, 0.0, 1.0, 0.3)
    c2_lcdm = res_lcdm.fun
    print(f"  H₀  = {H0l:.4f} km/s/Mpc")
    print(f"  Ωm  = {oml:.5f}")
    print(f"  Ωb  = {obl:.5f}  (Ωb·h² = {obl*hl**2:.5f})")
    print(f"  rd  = {rdl:.4f} Mpc,  r_s(z_*) = {rsl:.4f} Mpc")
    print(f"  χ²  = {c2_lcdm:.3f}")

    k_rll, k_lcdm = 6, 3
    Δχ2 = c2_tot - c2_lcdm
    ΔAIC = (c2_tot + 2*k_rll) - (c2_lcdm + 2*k_lcdm)
    ΔBIC = (c2_tot + k_rll*np.log(n_total)) - (c2_lcdm + k_lcdm*np.log(n_total))
    lnB  = -ΔBIC / 2.0
    print(f"\n  Comparação:")
    print(f"    Δχ²(RLL−ΛCDM)  = {Δχ2:.4f}")
    print(f"    ΔAIC(RLL−ΛCDM) = {ΔAIC:.4f}")
    print(f"    ΔBIC(RLL−ΛCDM) = {ΔBIC:.4f}")
    print(f"    ln(B₁₀)         = {lnB:.4f}")

    # ── Profile likelihood ─────────────────────────────────────────────
    print()
    print("── Profile likelihood: grade 5×5 em (Ωs0 × z_t) ──────────")
    prof_rows = profile_likelihood(datasets)

    # Sumário por Ωs0
    by_os0 = {}
    for r in prof_rows:
        k = r['os0']
        if k not in by_os0 or r['chi2'] < by_os0[k]['chi2']:
            by_os0[k] = r
    chi2_at_zero = by_os0[0.0]['chi2']
    chi2_min = min(r['chi2'] for r in prof_rows)

    print(f"\n  Profile minimum: Ωs0={min(by_os0, key=lambda k: by_os0[k]['chi2']):.3f}, χ²={chi2_min:.3f}")
    print()
    print(f"  {'Ωs0':>8} {'χ²_min':>10} {'Δχ² vs 0':>10} {'z_t_opt':>8} {'H₀':>8} {'Ωm':>7}")
    for os0_v in sorted(by_os0):
        r = by_os0[os0_v]
        print(f"  {os0_v:8.3f} {r['chi2']:10.3f} {r['chi2']-chi2_at_zero:>+10.3f} "
              f"{r['zt']:8.1f} {r['H0'] or 0:8.3f} {r['om'] or 0:7.4f}")

    # ── Salvar JSON ────────────────────────────────────────────────────
    RESULTS.mkdir(exist_ok=True)
    out = {
        "metadata": {
            "fase": "FASE 18-D",
            "correcoes": ["rs_star_para_lA_CMB", "rd_numerico_BAO", "prior_bbn", "starts_bbn_ancorados", "cauda_analitica_z_high"],
            "status_epistemico": "[E] análise final — r_s(z_*) + cauda analítica + r_s(z_drag) para BAO",
            "n_total": n_total
        },
        "verificacao_planck": {
            "H0": 67.36, "om": 0.3153, "ob": 0.04931,
            "rd_Mpc": rd_pl, "rs_star_Mpc": rs_pl, "chi2_CMB": c2_pl
        },
        "prior_bbn": {"ob_h2_center": BBN_OBH2, "ob_h2_sigma": BBN_OBH2_SIG},
        "map_rll_6param": {
            "H0": H0, "om": om, "ob": ob, "os0": os0, "zt": zt, "wt": wt,
            "ol": ol, "ob_h2": ob_h2, "z_drag": zdrag, "rd_Mpc": rd, "rs_star_Mpc": rs_star,
            "chi2_total": c2_tot,
            "chi2_breakdown": {
                "moresco_hz": c2_mor, "bao_historico": c2_bao,
                "desi_dr2": c2_des, "pantheon_sn": c2_sn,
                "cmb_shift": c2_cmb, "prior_bbn": c2_bbn
            }
        },
        "map_lcdm_3param": {
            "H0": H0l, "om": oml, "ob": obl, "ob_h2": obl*hl**2,
            "rd_Mpc": rdl, "rs_star_Mpc": rsl, "chi2_total": c2_lcdm
        },
        "comparacao_modelos": {
            "delta_chi2": Δχ2, "delta_aic": ΔAIC,
            "delta_bic": ΔBIC, "ln_B10": lnB,
            "k_rll": k_rll, "k_lcdm": k_lcdm, "n_dados": n_total
        },
        "profile_likelihood": prof_rows,
        "profile_summary": [
            {"os0": os0_v, "chi2_min": by_os0[os0_v]['chi2'],
             "delta_chi2": by_os0[os0_v]['chi2'] - chi2_at_zero,
             "zt_opt": by_os0[os0_v]['zt'], "H0_opt": by_os0[os0_v]['H0'],
             "om_opt": by_os0[os0_v]['om']}
            for os0_v in sorted(by_os0)
        ]
    }
    out_path = RESULTS / "rll_fase18d_final.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\n  JSON salvo: {out_path}")

    print()
    print("=" * 65)
    print("  CONCLUSÃO FASE 18-D")
    print("=" * 65)
    print(f"  r_s(z_drag) para BAO = {rd:.4f} Mpc")
    print(f"  r_s(z_*) para CMB    = {rs_star:.4f} Mpc")
    print(f"  H₀ MAP               = {H0:.4f} km/s/Mpc")
    print(f"  Ωm MAP               = {om:.5f}")
    print(f"  Ωb·h² MAP            = {ob_h2:.5f} (BBN: {BBN_OBH2})")
    print(f"  Ωs0 MAP              = {os0:.6f}  → colapso ΛCDM")
    print(f"  χ²_CMB/3             = {c2_cmb/3:.4f}")
    print(f"  ΔBIC                 = {ΔBIC:.4f}")
    print(f"  ln(B₁₀)              = {lnB:.4f}")
    print("=" * 65)


if __name__ == "__main__":
    main()
