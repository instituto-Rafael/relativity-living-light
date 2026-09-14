"""
FASE 20 — MCMC Joint + Bayes Factor (G1 + G3 fechados)

G1: MCMC com emcee (32 walkers × 1500 steps, burn 400)
    → posterior completa de Ωs0; limite superior 1σ/2σ
G3: Nested sampling com dynesty (nlive=150)
    → log-evidências Z_RLL e Z_ΛCDM; ln(B₁₀) formal

Herança intacta de FASE 19:
  - Dupla calibração Planck 2018 VI (arXiv:1807.06209):
      rs_star: +0.1988 Mpc  (chi²_CMB ≈ 0)
      rd:      −3.614 Mpc   (rd = 147.09 Mpc)
  - r_s(z_*) para l_A do CMB  (Chen+ 2019 arXiv:1808.05724)
  - Prior BBN (Cooke+ 2018 arXiv:1710.11129)
  - 5 datasets, 1677 pontos

Status epistêmico: [E] posterior e evidência Bayesiana com dados reais
"""

import numpy as np
import json
import csv
import sys
from pathlib import Path
from scipy.optimize import minimize
import emcee
import dynesty

# ─── Paths ─────────────────────────────────────────────────────────────────
REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data" / "real"
RESULTS = REPO / "results"
PANTHEON_PATH = REPO / "validacao_real" / "data" / "pantheon_data.dat"

# ─── Constantes físicas ────────────────────────────────────────────────────
C_KMS = 299792.458
OMEGA_R = 9.18e-5
Z_CMB   = 1089.92
OMEGA_GAMMA_H2 = 2.47e-5

# ─── Prior BBN ─────────────────────────────────────────────────────────────
BBN_OBH2     = 0.02236
BBN_OBH2_SIG = 0.00015

# ─── Alvos de calibração Planck 2018 VI ───────────────────────────────────
RD_PLANCK2018 = 147.09
THETA_PLANCK  = [67.36, 0.3153, 0.04931, 0.0, 1.0, 0.3]

# ─── Calibrações (preenchidas em main()) ───────────────────────────────────
_RS_STAR_CALIB_MPC = 0.0
_RD_CALIB_MPC      = 0.0

# ─── Grids de integração ───────────────────────────────────────────────────
_ZG        = np.concatenate([[0.0], np.logspace(-4, np.log10(1200.0), 7000)])
_Z_RS_HIGH = 5e5
_Z_RS_N    = 4000

# ─── Priors MCMC / nested sampling ─────────────────────────────────────────
_PR = {
    'H0':  (60.0,  80.0),
    'om':  (0.20,  0.50),
    'ob':  (0.030, 0.070),
    'os0': (0.0,   0.15),
    'zt':  (0.1,   20.0),
    'wt':  (0.05,  2.0),
}
# ΛCDM usa só H0, om, ob
_PR_LCDM = {k: _PR[k] for k in ('H0', 'om', 'ob')}


# ══════════════════════════════════════════════════════════════════════════
# HORIZONTE SONORO (idêntico a FASE 19)
# ══════════════════════════════════════════════════════════════════════════

def _zdrag_EH98(om_h2, ob_h2):
    b1 = 0.313 * om_h2**(-0.419) * (1.0 + 0.607 * om_h2**0.674)
    b2 = 0.238 * om_h2**0.223
    return 1291.0 * om_h2**0.251 / (1.0 + 0.659 * om_h2**0.828) * (1.0 + b1 * ob_h2**b2)


def _cs_over_Hz(z_arr, H0, om, ob, os0, zt, wt):
    h = H0 / 100.
    R_b = (3.0 * ob / (4.0 * OMEGA_GAMMA_H2 / h**2)) / (1.0 + z_arr)
    cs  = C_KMS / np.sqrt(3.0 * (1.0 + R_b))
    with np.errstate(over='ignore'):
        f = 1.0 / (1.0 + np.exp((z_arr - zt) / wt))
    rho_s = os0 * (f + (1.0 - f) * (1.0 + z_arr)**3)
    ol = 1.0 - om - OMEGA_R - os0
    e2 = om*(1+z_arr)**3 + OMEGA_R*(1+z_arr)**4 + rho_s + ol
    return cs / (H0 * np.sqrt(np.maximum(e2, 1e-30)))


def _trapz(y, x):
    dx = np.diff(x)
    return float(np.sum(dx * 0.5 * (y[:-1] + y[1:])))


def compute_sound_horizons(H0, om, ob, os0, zt, wt):
    h = H0 / 100.
    z_drag = _zdrag_EH98(om*h**2, ob*h**2)
    z_low  = min(z_drag, Z_CMB)
    z_rs   = np.logspace(np.log10(max(z_low, 1.0)), np.log10(_Z_RS_HIGH), _Z_RS_N)
    integ  = _cs_over_Hz(z_rs, H0, om, ob, os0, zt, wt)
    rs_tot = _trapz(integ, z_rs)
    cs_inf = C_KMS / np.sqrt(3.0)
    rs_tot += cs_inf / (H0 * np.sqrt(max(OMEGA_R, 1e-30))) / (1.0 + _Z_RS_HIGH)
    i_drag = int(np.searchsorted(z_rs, z_drag))
    i_star = int(np.searchsorted(z_rs, Z_CMB))
    if z_drag <= Z_CMB:
        rd = rs_tot
        sl = z_rs[:i_star+1]; si = integ[:i_star+1]
        rs_star = rd - (_trapz(si, sl) if len(sl) > 1 else 0.0)
    else:
        rs_star = rs_tot
        sl = z_rs[:i_drag+1]; si = integ[:i_drag+1]
        rd = rs_tot - (_trapz(si, sl) if len(sl) > 1 else 0.0)
    return float(rd) + _RD_CALIB_MPC, float(rs_star) + _RS_STAR_CALIB_MPC


# ══════════════════════════════════════════════════════════════════════════
# Modelo RLL — E²(z), distâncias
# ══════════════════════════════════════════════════════════════════════════

def _build_integrals(H0, om, os0, zt, wt):
    with np.errstate(over='ignore'):
        f = 1.0 / (1.0 + np.exp((_ZG - zt) / wt))
    rho_s = os0 * (f + (1.0 - f) * (1.0 + _ZG)**3)
    ol = 1.0 - om - OMEGA_R - os0
    e2 = np.maximum(om*(1+_ZG)**3 + OMEGA_R*(1+_ZG)**4 + rho_s + ol, 1e-30)
    e  = np.sqrt(e2)
    dz = np.diff(_ZG)
    chi = np.zeros_like(_ZG)
    chi[1:] = np.cumsum(dz * 0.5 * (1.0/e[:-1] + 1.0/e[1:]))
    return chi, H0 * e


# ══════════════════════════════════════════════════════════════════════════
# Chi² por dataset
# ══════════════════════════════════════════════════════════════════════════

def chi2_moresco(theta, data):
    H0, om, ob, os0, zt, wt = theta
    _, hz = _build_integrals(H0, om, os0, zt, wt)
    return float(np.sum(((data[:, 1] - np.interp(data[:, 0], _ZG, hz)) / data[:, 2])**2))


def chi2_bao_hist(theta, data, rd):
    H0, om, ob, os0, zt, wt = theta
    chi, hz = _build_integrals(H0, om, os0, zt, wt)
    z = data[:, 0]
    dm = np.interp(z, _ZG, chi) * (C_KMS / H0)
    dh = C_KMS / np.interp(z, _ZG, hz)
    dv = (z * dm**2 * dh)**(1./3.)
    return float(np.sum(((data[:, 1] - dv/rd) / data[:, 2])**2))


def chi2_desi_dr2(theta, blocks, rd):
    H0, om, ob, os0, zt, wt = theta
    chi, hz = _build_integrals(H0, om, os0, zt, wt)
    total = 0.0
    for b in blocks:
        cz  = np.interp(b['z'], _ZG, chi)
        hzz = np.interp(b['z'], _ZG, hz)
        dm  = (C_KMS / H0) * cz
        dh  = C_KMS / hzz
        if b['type'] == 'iso':
            dv = (b['z'] * dm**2 * dh)**(1./3.)
            total += ((b['obs'] - dv/rd) / b['sig'])**2
        else:
            d1 = (b['dm_obs'] - dm/rd) / b['dm_sig']
            d2 = (b['dh_obs'] - dh/rd) / b['dh_sig']
            r  = b['rho']
            total += (d1**2 - 2.*r*d1*d2 + d2**2) / (1.0 - r**2)
    return float(total)


def chi2_sn(theta, sn_data):
    H0, om, ob, os0, zt, wt = theta
    z_arr, mu_obs, mu_err = sn_data
    chi, _ = _build_integrals(H0, om, os0, zt, wt)
    dl  = (1.0 + z_arr) * (C_KMS / H0) * np.interp(z_arr, _ZG, chi)
    mu_th = 5.0 * np.log10(np.maximum(dl, 1e-10)) + 25.0
    delta = mu_obs - mu_th
    w = 1.0 / mu_err**2
    res = delta - np.sum(delta * w) / np.sum(w)
    return float(np.sum(w * res**2))


def chi2_cmb(theta, cmb_data, rs_star):
    H0, om, ob, os0, zt, wt = theta
    ob_h2 = ob * (H0/100.)**2
    chi, _ = _build_integrals(H0, om, os0, zt, wt)
    chi_cmb = np.interp(cmb_data['z_cmb'], _ZG, chi)
    R_th   = np.sqrt(om) * chi_cmb
    l_A_th = np.pi * (C_KMS / H0) * chi_cmb / rs_star
    th = np.array([R_th, l_A_th, ob_h2])
    delta = cmb_data['obs'] - th
    return float(delta @ cmb_data['cov_inv'] @ delta)


def chi2_bbn(theta):
    H0, om, ob, os0, zt, wt = theta
    ob_h2 = ob * (H0/100.)**2
    return ((ob_h2 - BBN_OBH2) / BBN_OBH2_SIG)**2


def chi2_total(theta, datasets):
    H0, om, ob, os0, zt, wt = theta
    if ob <= 0 or om <= 0.10 or os0 < 0 or wt <= 0:
        return 1e12
    ol = 1.0 - om - OMEGA_R - os0
    if ol < 0.0 or (om + os0 + OMEGA_R) > 0.995:
        return 1e12
    try:
        moresco, bao_hist, desi, sn, cmb = datasets
        rd, rs_star = compute_sound_horizons(H0, om, ob, os0, zt, wt)
        return (chi2_moresco(theta, moresco)
                + chi2_bao_hist(theta, bao_hist, rd)
                + chi2_desi_dr2(theta, desi, rd)
                + chi2_sn(theta, sn)
                + chi2_cmb(theta, cmb, rs_star)
                + chi2_bbn(theta))
    except Exception:
        return 1e12


def chi2_lcdm(theta3, datasets):
    return chi2_total([theta3[0], theta3[1], theta3[2], 0.0, 1.0, 0.3], datasets)


# ══════════════════════════════════════════════════════════════════════════
# Carregamento de dados
# ══════════════════════════════════════════════════════════════════════════

def load_all_data():
    moresco = []
    with open(DATA / "Hz_data_real.csv") as f:
        for r in csv.DictReader(f):
            moresco.append([float(r['z']), float(r['H_obs']), float(r['sigma_H'])])
    moresco = np.array(moresco)

    _EXCL = {'DESI2024_BGS','DESI2024_LRG1','DESI2024_LRG2','DESI2024_ELG','DESI2024_QSO','BOSS_Lya'}
    bao_hist = []
    with open(DATA / "BAO_data_real.csv") as f:
        for r in csv.DictReader(f):
            if r['survey'] not in _EXCL:
                bao_hist.append([float(r['z_eff']), float(r['DV_over_rs']), float(r['sigma'])])
    bao_hist = np.array(bao_hist)

    by_tracer = {}
    with open(DATA / "cosmology" / "desi_dr2_bao_primary_points.csv") as f:
        for r in csv.DictReader(f):
            by_tracer.setdefault(r['tracer'], []).append(r)
    desi = []
    for rows in by_tracer.values():
        if len(rows) == 1:
            r = rows[0]
            desi.append({'type':'iso','z':float(r['z_eff']),'obs':float(r['value']),'sig':float(r['sigma'])})
        else:
            dm_r = next(r for r in rows if r['observable']=='DM_over_rd')
            dh_r = next(r for r in rows if r['observable']=='DH_over_rd')
            desi.append({'type':'aniso','z':float(dm_r['z_eff']),
                         'dm_obs':float(dm_r['value']),'dm_sig':float(dm_r['sigma']),
                         'dh_obs':float(dh_r['value']),'dh_sig':float(dh_r['sigma']),
                         'rho':float(dm_r['correlation_coefficient'])})

    with open(PANTHEON_PATH) as f:
        header = f.readline().split()
    idx = {n: i for i, n in enumerate(header)}
    d = np.genfromtxt(PANTHEON_PATH, skip_header=1, dtype=str)
    z   = d[:, idx['zHD']].astype(float)
    mu  = d[:, idx['MU_SH0ES']].astype(float)
    err = d[:, idx['MU_SH0ES_ERR_DIAG']].astype(float)
    cal = d[:, idx['IS_CALIBRATOR']].astype(float)
    m = cal == 0
    sn = (z[m], mu[m], err[m])

    with open(DATA / "CMB_shift_real.json") as f:
        cd = json.load(f)
    cmb = {'obs': np.array([cd['R_obs'], cd['la_obs'], cd['ob_h2_obs']]),
           'cov_inv': np.linalg.inv(np.array(cd['covariance'])),
           'z_cmb': float(cd['z_CMB'])}

    return moresco, bao_hist, desi, sn, cmb


# ══════════════════════════════════════════════════════════════════════════
# Calibração (idêntica a FASE 19)
# ══════════════════════════════════════════════════════════════════════════

def calibrate(cmb):
    global _RS_STAR_CALIB_MPC, _RD_CALIB_MPC
    _RS_STAR_CALIB_MPC = 0.0
    _RD_CALIB_MPC      = 0.0

    # 1. rs_star
    _, rs_raw = compute_sound_horizons(*THETA_PLANCK)
    chi_c, _ = _build_integrals(67.36, 0.3153, 0.0, 1.0, 0.3)
    dm_c  = (C_KMS / 67.36) * float(np.interp(Z_CMB, _ZG, chi_c))
    rs_tg = np.pi * dm_c / cmb['obs'][1]
    _RS_STAR_CALIB_MPC = rs_tg - rs_raw

    # 2. rd (G2 — FASE 19)
    _RS_STAR_CALIB_MPC_sv = _RS_STAR_CALIB_MPC
    _RS_STAR_CALIB_MPC = 0.0
    _RD_CALIB_MPC = 0.0
    rd_raw, _ = compute_sound_horizons(*THETA_PLANCK)
    _RS_STAR_CALIB_MPC = _RS_STAR_CALIB_MPC_sv
    _RD_CALIB_MPC = RD_PLANCK2018 - rd_raw

    print(f"  _RS_STAR_CALIB_MPC = {_RS_STAR_CALIB_MPC:+.4f} Mpc")
    print(f"  _RD_CALIB_MPC      = {_RD_CALIB_MPC:+.4f} Mpc")
    rd_v, rs_v = compute_sound_horizons(*THETA_PLANCK)
    c2_v = chi2_cmb(THETA_PLANCK, cmb, rs_v)
    print(f"  Verificação Planck: rd={rd_v:.4f} Mpc, rs*={rs_v:.4f} Mpc, chi²_CMB={c2_v:.4f}")


# ══════════════════════════════════════════════════════════════════════════
# G1: MCMC com emcee
# ══════════════════════════════════════════════════════════════════════════

def log_prior_rll(theta):
    H0, om, ob, os0, zt, wt = theta
    (H0_lo, H0_hi), (om_lo, om_hi) = _PR['H0'], _PR['om']
    (ob_lo, ob_hi), (os0_lo, os0_hi) = _PR['ob'], _PR['os0']
    (zt_lo, zt_hi), (wt_lo, wt_hi)  = _PR['zt'], _PR['wt']
    if not (H0_lo < H0 < H0_hi): return -np.inf
    if not (om_lo < om < om_hi):  return -np.inf
    if not (ob_lo < ob < ob_hi):  return -np.inf
    if not (os0_lo <= os0 < os0_hi): return -np.inf
    if not (zt_lo < zt < zt_hi):  return -np.inf
    if not (wt_lo < wt < wt_hi):  return -np.inf
    return 0.0


def log_prob_rll(theta, datasets):
    lp = log_prior_rll(theta)
    if not np.isfinite(lp):
        return -np.inf
    c2 = chi2_total(theta, datasets)
    if c2 > 1e10:
        return -np.inf
    return -0.5 * c2


def run_mcmc(datasets, ndim=6, nwalkers=32, nsteps=1500, burn=400):
    theta_map = [67.0, 0.314, 0.04964, 0.001, 2.0, 0.30]
    scales = np.array([0.5, 0.005, 0.0003, 0.003, 1.0, 0.05])
    rng = np.random.default_rng(42)
    pos = np.array(theta_map) + scales * rng.standard_normal((nwalkers, ndim))
    pos[:, 3] = np.abs(pos[:, 3])   # Os0 >= 0
    pos[:, 3] = np.clip(pos[:, 3], 0.0, 0.14)

    sampler = emcee.EnsembleSampler(nwalkers, ndim, log_prob_rll, args=[datasets])
    print(f"  Executando emcee: {nwalkers} walkers × {nsteps} steps ...", flush=True)
    sampler.run_mcmc(pos, nsteps, progress=True)
    return sampler, burn


def analyze_mcmc(sampler, burn):
    flat = sampler.get_chain(discard=burn, flat=True)
    names = ['H0', 'om', 'ob', 'os0', 'zt', 'wt']
    stats = {}
    for i, n in enumerate(names):
        v = flat[:, i]
        stats[n] = {
            'mean': float(np.mean(v)),
            'std':  float(np.std(v)),
            'p16':  float(np.percentile(v, 16)),
            'p50':  float(np.percentile(v, 50)),
            'p84':  float(np.percentile(v, 84)),
            'p95':  float(np.percentile(v, 95)),
        }
    acc = float(np.mean(sampler.acceptance_fraction))
    tau = None
    try:
        tau = sampler.get_autocorr_time(quiet=True).tolist()
    except Exception:
        pass
    return stats, acc, tau, flat


# ══════════════════════════════════════════════════════════════════════════
# G3: Nested sampling com dynesty
# ══════════════════════════════════════════════════════════════════════════

def _prior_transform_rll(u, datasets=None):
    v = np.empty(6)
    for i, k in enumerate(('H0','om','ob','os0','zt','wt')):
        lo, hi = _PR[k]
        v[i] = lo + (hi - lo) * u[i]
    return v


def _prior_transform_lcdm(u, datasets=None):
    v = np.empty(3)
    for i, k in enumerate(('H0','om','ob')):
        lo, hi = _PR_LCDM[k]
        v[i] = lo + (hi - lo) * u[i]
    return v


def _logl_rll(theta, datasets):
    c2 = chi2_total(theta, datasets)
    return -0.5 * c2 if c2 < 1e10 else -1e100


def _logl_lcdm(theta3, datasets):
    c2 = chi2_lcdm(theta3, datasets)
    return -0.5 * c2 if c2 < 1e10 else -1e100


def run_nested(datasets, nlive=150):
    print(f"  Nested sampling RLL (ndim=6, nlive={nlive}) ...", flush=True)
    sRLL = dynesty.NestedSampler(
        _logl_rll, _prior_transform_rll, ndim=6,
        nlive=nlive, logl_args=[datasets], ptform_args=[datasets],
        rstate=np.random.default_rng(42)
    )
    sRLL.run_nested(print_progress=True, dlogz=0.5)
    logZ_rll   = float(sRLL.results.logz[-1])
    logZ_rll_e = float(sRLL.results.logzerr[-1])

    print(f"\n  Nested sampling ΛCDM (ndim=3, nlive={nlive}) ...", flush=True)
    sLCDM = dynesty.NestedSampler(
        _logl_lcdm, _prior_transform_lcdm, ndim=3,
        nlive=nlive, logl_args=[datasets], ptform_args=[datasets],
        rstate=np.random.default_rng(42)
    )
    sLCDM.run_nested(print_progress=True, dlogz=0.5)
    logZ_lcdm   = float(sLCDM.results.logz[-1])
    logZ_lcdm_e = float(sLCDM.results.logzerr[-1])

    # ln(B₁₀) = log(Z_RLL/Z_ΛCDM) = logZ_RLL - logZ_ΛCDM
    # Jeffreys: B₁₀ < 1 ↔ ln(B₁₀) < 0 → evidência para ΛCDM
    lnB10     = logZ_rll - logZ_lcdm
    lnB10_err = float(np.sqrt(logZ_rll_e**2 + logZ_lcdm_e**2))
    return logZ_rll, logZ_rll_e, logZ_lcdm, logZ_lcdm_e, lnB10, lnB10_err


# ══════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 70)
    print("  RLL FASE 20 — MCMC Joint (G1) + Bayes Factor Formal (G3)")
    print("  Dupla calibração Planck 2018 · 5 datasets · 1677 pontos")
    print("=" * 70)

    # ── Dados ──────────────────────────────────────────────────────────
    print("\n[Carregando dados] ...")
    moresco, bao_hist, desi, sn, cmb = load_all_data()
    n_desi = sum(2 if b['type'] == 'aniso' else 1 for b in desi)
    n_total = len(moresco) + len(bao_hist) + n_desi + len(sn[0]) + 3
    print(f"  {n_total} pontos totais")
    datasets = (moresco, bao_hist, desi, sn, cmb)

    # ── Calibração ─────────────────────────────────────────────────────
    print("\n── Calibração dupla Planck 2018 ────────────────────────────")
    calibrate(cmb)

    # ── G1: MCMC ───────────────────────────────────────────────────────
    print("\n── G1: MCMC com emcee ──────────────────────────────────────")
    sampler, burn = run_mcmc(datasets, nsteps=1500, burn=400)
    stats, acc, tau, flat = analyze_mcmc(sampler, burn)

    print(f"\n  Fração de aceitação: {acc:.4f}")
    if tau:
        print(f"  Tempo de autocorrelação τ: {[f'{t:.1f}' for t in tau]}")

    os0_stats = stats['os0']
    print(f"\n  Posterior Ωs0:")
    print(f"    mediana = {os0_stats['p50']:.5f}")
    print(f"    1σ range = [{os0_stats['p16']:.5f}, {os0_stats['p84']:.5f}]")
    print(f"    limite 95% superior = {os0_stats['p95']:.5f}")
    print(f"    média ± σ = {os0_stats['mean']:.5f} ± {os0_stats['std']:.5f}")

    print(f"\n  Posterior H₀:  {stats['H0']['p50']:.4f} + {stats['H0']['p84']-stats['H0']['p50']:.4f} - {stats['H0']['p50']-stats['H0']['p16']:.4f}")
    print(f"  Posterior Ωm:  {stats['om']['p50']:.5f} + {stats['om']['p84']-stats['om']['p50']:.5f} - {stats['om']['p50']-stats['om']['p16']:.5f}")

    # ── G3: Nested sampling ────────────────────────────────────────────
    print("\n── G3: Nested sampling com dynesty ─────────────────────────")
    logZ_rll, logZ_rll_e, logZ_lcdm, logZ_lcdm_e, lnB10, lnB10_err = run_nested(datasets, nlive=150)

    print(f"\n  log Z_RLL  = {logZ_rll:.3f} ± {logZ_rll_e:.3f}")
    print(f"  log Z_ΛCDM = {logZ_lcdm:.3f} ± {logZ_lcdm_e:.3f}")
    print(f"  ln(B₁₀)    = {lnB10:.3f} ± {lnB10_err:.3f}")

    jeffreys = ("|ln(B₁₀)| > 5: evidência muito forte para ΛCDM"
                if abs(lnB10) > 5 else
                "|ln(B₁₀)| 2.5-5: evidência forte para ΛCDM"
                if abs(lnB10) > 2.5 else
                "|ln(B₁₀)| < 2.5: positiva ou não vale menção")
    print(f"  Escala Jeffreys: {jeffreys}")

    # ── Salvar JSON ────────────────────────────────────────────────────
    RESULTS.mkdir(exist_ok=True)
    out = {
        "metadata": {
            "fase": "FASE 20",
            "gaps_fechados": ["G1 (MCMC joint)", "G3 (Bayes Factor formal)"],
            "calibracao": {
                "rs_star_calib_Mpc": _RS_STAR_CALIB_MPC,
                "rd_calib_Mpc": _RD_CALIB_MPC
            },
            "n_total": n_total
        },
        "mcmc_g1": {
            "nwalkers": 32, "nsteps": 1500, "burn": 400,
            "acceptance_fraction": acc,
            "autocorr_time": tau,
            "posteriors": stats,
            "os0_upper95": os0_stats['p95'],
            "os0_median": os0_stats['p50'],
            "os0_mean": os0_stats['mean'],
            "os0_std": os0_stats['std'],
        },
        "nested_g3": {
            "nlive": 150,
            "logZ_rll":    logZ_rll,   "logZ_rll_err":    logZ_rll_e,
            "logZ_lcdm":   logZ_lcdm,  "logZ_lcdm_err":   logZ_lcdm_e,
            "lnB10":       lnB10,      "lnB10_err":       lnB10_err,
            "jeffreys_scale": jeffreys,
            "prior_volume_ratio": "RLL/ΛCDM = V_RLL/V_ΛCDM (6D/3D priors)"
        },
        "fase19_referencia": {
            "delta_bic": 22.27, "lnB10_approx": -11.14,
            "os0_map": 0.0
        }
    }
    out_path = RESULTS / "rll_fase20_mcmc_bayes.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\n  JSON salvo: {out_path}")

    print()
    print("=" * 70)
    print("  CONCLUSÃO FASE 20")
    print("=" * 70)
    print(f"  G1 (MCMC): Ωs0 mediana = {os0_stats['p50']:.5f}, 95% UL = {os0_stats['p95']:.4f}")
    print(f"  G3 (Bayes): ln(B₁₀) = {lnB10:.3f} ± {lnB10_err:.3f}")
    print(f"  → {jeffreys}")
    print("=" * 70)


if __name__ == "__main__":
    main()
