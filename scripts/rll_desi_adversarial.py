#!/usr/bin/env python3
"""Claim-safe DESI DR2 BAO profiling / falsification diagnostic.

Isolated BAO-only analysis. No changes to production cosmology, source data, or
prior historical outputs. NumPy/SciPy are existing project requirements.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from scipy.linalg import solve_triangular
from scipy.optimize import least_squares
from scipy.special import expit
import scipy

ROOT = Path(__file__).resolve().parents[1]
MEAS = Path('data/real/desi_dr2_bao_measurements.csv')
COV = Path('data/real/desi_dr2_bao_covariance.csv')
# Producer Git blob identities, not SHA-256. Both the Git-blob SHA-1 pins and
# separately calculated SHA-256 values are recorded in the output manifest.
SOURCE_BLOBS = {
    'measurements': '8611587e98e60389f7f7b1cb2cf9ab095654d74a',
    'covariance': 'e01d0235a2f0e61d81af0c36a7338953f845f5c3',
}
C = 299792.458  # km/s
RD = 147.09      # Mpc, fixed baseline convention
OR = 9.2e-5
PARAMS = {
    'LCDM': (('H0', 'Om'), (55., .10), (85., .50)),
    'CPL': (('H0', 'Om', 'w0', 'wa'), (55., .10, -2.5, -3.), (85., .50, -.3, 3.)),
    'RLL': (('H0', 'Om', 'Os', 'zt', 'wt'), (55., .10, 0., .05, .05), (85., .50, .25, 3., 1.5)),
}
NODES, WEIGHTS = np.polynomial.legendre.leggauss(64)


def digest(path: Path) -> dict:
    raw = path.read_bytes()
    header = b'blob ' + str(len(raw)).encode('ascii') + b'\0'
    return {'git_blob_sha1': hashlib.sha1(header + raw).hexdigest(),
            'sha256': hashlib.sha256(raw).hexdigest(), 'size_bytes': len(raw)}


def load_inputs(root: Path = ROOT, enforce_pins: bool = True) -> dict:
    inputs = {name: digest(root / path) for name, path in [('measurements', MEAS), ('covariance', COV)]}
    for name, pin in SOURCE_BLOBS.items():
        if enforce_pins and inputs[name]['git_blob_sha1'] != pin:
            raise ValueError(f'UNPINNED_SOURCE_{name}: {inputs[name]["git_blob_sha1"]} != {pin}')
    with (root / MEAS).open(newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 13 or [int(r['index']) for r in rows] != list(range(13)):
        raise ValueError('EXPECTED_13_ORDERED_BAO_ROWS')
    if any(r['observable'] not in {'DV_over_rd', 'DM_over_rd', 'DH_over_rd'} for r in rows):
        raise ValueError('UNKNOWN_BAO_OBSERVABLE')
    z = np.array([float(r['z_eff']) for r in rows]); y = np.array([float(r['value']) for r in rows]); s = np.array([float(r['sigma']) for r in rows]); names = [r['tracer'] for r in rows]
    with (root / COV).open(newline='', encoding='utf-8') as f:
        rr = list(csv.reader(f))
    if rr[0] != [''] + [str(i) for i in range(13)] or len(rr) != 14:
        raise ValueError('COVARIANCE_HEADER_SHAPE_MISMATCH')
    if any(r[0] != str(i) or len(r) != 14 for i, r in enumerate(rr[1:])):
        raise ValueError('COVARIANCE_ROW_ID_MISMATCH')
    cov = np.array([[float(x) for x in r[1:]] for r in rr[1:]])
    if not (np.all(np.isfinite(y)) and np.all(np.isfinite(z)) and np.all(np.isfinite(s)) and np.all(np.isfinite(cov))):
        raise ValueError('NONFINITE_DATA')
    if np.any(z <= 0) or np.any(s <= 0) or np.any(np.diag(cov) <= 0) or not np.allclose(np.sqrt(np.diag(cov)), s, rtol=2e-8, atol=1e-10):
        raise ValueError('INVALID_SIGMA_COVARIANCE_CONSISTENCY')
    if not np.allclose(cov, cov.T, rtol=0, atol=1e-12):
        raise ValueError('NONSYMMETRIC_COVARIANCE')
    chol = np.linalg.cholesky(cov)
    if not np.all(np.isfinite(chol)):
        raise ValueError('BAD_CHOLESKY')
    # No artificial data fill, no rescaling of observational uncertainties.
    return {'z': z, 'y': y, 'cov': cov, 'chol': chol, 'obs': [r['observable'] for r in rows], 'tracer': names, 'source': inputs}


def hubble_ratio_sq(model: str, theta: np.ndarray, z: np.ndarray) -> np.ndarray:
    a = 1. + np.asarray(z)
    h0, om = theta[:2]
    if model == 'LCDM':
        return om * a**3 + OR * a**4 + (1. - om - OR)
    if model == 'CPL':
        w0, wa = theta[2:]
        return om * a**3 + OR * a**4 + (1. - om - OR) * a**(3 * (1 + w0 + wa)) * np.exp(-3 * wa * z / a)
    if model == 'RLL':
        os_, zt, wt = theta[2:]
        f = expit((zt - z) / wt)
        return om * a**3 + OR * a**4 + 1. - om - OR - os_ + os_ * (f + (1 - f) * a**3)
    raise ValueError('INVALID_MODEL')


def predict(model: str, theta: np.ndarray, z: np.ndarray, obs: list[str]) -> np.ndarray:
    # Gauss-Legendre 64-point integration of flat FLRW comoving distance.
    # This is an explicit phenomenological background, NOT a perturbation solver.
    zz = np.asarray(z, dtype=float)
    sample = .5 * zz[:, None] * (NODES[None, :] + 1.)
    e2 = hubble_ratio_sq(model, theta, sample)
    e2z = hubble_ratio_sq(model, theta, zz)
    if not np.all(np.isfinite(e2)) or not np.all(np.isfinite(e2z)) or np.min(e2) <= 0 or np.min(e2z) <= 0:
        raise ValueError('NONPOSITIVE_E2')
    dm = (C / (theta[0] * RD)) * .5 * zz * np.sum(WEIGHTS[None, :] / np.sqrt(e2), axis=1)
    dh = (C / (theta[0] * RD)) / np.sqrt(e2z)
    dv = np.cbrt(zz * dm * dm * dh)
    select = {'DM_over_rd': dm, 'DH_over_rd': dh, 'DV_over_rd': dv}
    return np.array([select[ob][i] for i, ob in enumerate(obs)])


def whiten(d: np.ndarray, l: np.ndarray) -> np.ndarray:
    return solve_triangular(l, d, lower=True, check_finite=False)


def chi2(data: dict, model: str, theta: np.ndarray) -> float:
    return float(np.dot(r := whiten(predict(model, theta, data['z'], data['obs']) - data['y'], data['chol']), r))


def initial(model: str, start: int, seed: int, lcdm: np.ndarray | None = None) -> np.ndarray:
    names, low, high = PARAMS[model]
    if start == 0:
        if model == 'LCDM': return np.array([67.4, .315])
        if model == 'CPL': return np.array([67.4, .315, -1., 0.])
        return np.array([67.4, .315, .02, 1., .3])
    # Source-documented observational warm start; disclosed, NOT external evidence.
    # It improves optimizer-basin discovery, not statistical significance.
    if start == 2 and model == 'RLL':
        return np.array([71.74798166, .1345220919, .1339438339, .3987865349, .050000001])
    if start == 1 and lcdm is not None:
        if model == 'CPL': return np.array([lcdm[0], lcdm[1], -1., 0.])
        if model == 'RLL': return np.array([lcdm[0], lcdm[1], 0., 1., .3])
    # Each start derives from a stable integer seed without depending on call order.
    rng = np.random.default_rng(np.random.SeedSequence([int(seed), int(start), {'LCDM': 10, 'CPL': 20, 'RLL': 30}[model]]))
    return rng.uniform(low, high)


def fit(data: dict, model: str, seed: int, starts: int, lcdm: np.ndarray | None = None, max_nfev: int = 400) -> dict:
    labels, lo, hi = PARAMS[model]
    if starts < 2:
        raise ValueError('AT_LEAST_TWO_STARTS_REQUIRED')
    l = np.array(lo); u = np.array(hi)
    best = None; trials = []
    for start in range(starts):
        x = initial(model, start, seed, lcdm)
        def residual(params: np.ndarray) -> np.ndarray:
            try:
                return whiten(predict(model, params, data['z'], data['obs']) - data['y'], data['chol'])
            except (ValueError, OverflowError, FloatingPointError):
                return np.full(len(data['y']), 1e8)
        opt = least_squares(residual, x0=x, bounds=(l, u), max_nfev=max_nfev, xtol=1e-10, ftol=1e-10, gtol=1e-10)
        val = float(np.dot(opt.fun, opt.fun))
        trials.append({'start': start, 'chi2': val, 'success': bool(opt.success), 'nfev': int(opt.nfev)})
        if np.isfinite(val) and opt.success and (best is None or val < best['chi2']):
            best = {'chi2': val, 'theta': opt.x, 'jac': opt.jac, 'starts': start, 'nfev': int(opt.nfev)}
    if best is None: raise RuntimeError('NO_CONVERGED_OPTIMUM_'+model)
    x = best['theta']
    near = [labels[i] for i, v in enumerate(x) if min(v-lo[i], hi[i]-v) < 1e-6 * (hi[i]-lo[i])]
    return {'model':model, 'params':{k:float(v) for k,v in zip(labels,x)}, 'chi2':best['chi2'], 'k_fit':len(labels), 'boundary_parameters':near,
            'converged':True, 'starts':trials, '_theta':x, '_jac':best['jac']}


def public_fit(f: dict, n: int) -> dict:
    k = f['k_fit']; x = {s:v for s,v in f.items() if not s.startswith('_')}
    x['scores_diagnostic_only'] = {'AIC':f['chi2']+2*k, 'BIC':f['chi2']+k*math.log(n), 'AICc':(f['chi2']+2*k+2*k*(k+1)/(n-k-1)) if n>k+1 else None}
    return x


def subdata(data: dict, indices: np.ndarray, y: np.ndarray | None = None) -> dict:
    cov = data['cov'][np.ix_(indices, indices)]
    return {'z':data['z'][indices], 'y':data['y'][indices] if y is None else y[indices], 'obs':[data['obs'][i] for i in indices],
            'tracer':[data['tracer'][i] for i in indices], 'cov':cov, 'chol':np.linalg.cholesky(cov)}


def holdout(data: dict, seed: int, starts: int) -> list[dict]:
    # Refit *without* the heldout block. Conditional Gaussian predictive score
    # handles C_train,heldout cross terms. Never use heldout points to select fits.
    rows = []
    for group in dict.fromkeys(data['tracer']):
        held = np.array([i for i,v in enumerate(data['tracer']) if v == group]); train = np.array([i for i,v in enumerate(data['tracer']) if v != group]); d = subdata(data, train)
        a=fit(d,'LCDM',seed,starts); r=fit(d,'RLL',seed,starts,a['_theta']); c=fit(d,'CPL',seed,starts,a['_theta'])
        ct = data['cov'][np.ix_(train,train)]; ch = data['cov'][np.ix_(held,held)]; cht = data['cov'][np.ix_(held,train)]
        gain = np.linalg.solve(ct, cht.T).T; cond_cov = ch - gain@cht.T; l=np.linalg.cholesky(cond_cov)
        scores={}
        for model, obj in [('LCDM',a),('CPL',c),('RLL',r)]:
            mtrain=predict(model,obj['_theta'],data['z'][train],d['obs']); mh=predict(model,obj['_theta'],data['z'][held],[data['obs'][i] for i in held])
            pred_cond=mh+gain@(data['y'][train]-mtrain)
            res=whiten(data['y'][held]-pred_cond,l)
            scores[model]={'train_chi2':obj['chi2'],'heldout_conditional_chi2':float(res@res)}
        rows.append({'tracer':group,'n_train':len(train),'n_heldout':len(held),'models':scores})
    return rows


def bootstrap_null(data: dict, fitted_null: dict, observed_alt: dict, n_sim: int, seed: int, starts: int) -> dict:
    theta0=fitted_null['_theta']; y0=predict('LCDM',theta0,data['z'],data['obs'])
    t_obs=max(0., fitted_null['chi2'] - observed_alt['chi2'])
    rng=np.random.default_rng(np.random.SeedSequence([seed, 999_007]))
    values=[]
    for i in range(n_sim):
        trial_y=y0 + data['chol'] @ rng.normal(size=len(data['y']))
        trial={**data,'y':trial_y}
        a=fit(trial,'LCDM',seed+i+1,starts)
        r=fit(trial,'RLL',seed+i+1,starts,a['_theta'])
        improvement=a['chi2']-r['chi2']
        if improvement < -1e-5: raise RuntimeError('NESTING_OPTIMIZER_FAILURE_BOOTSTRAP')
        values.append(max(0., improvement))
    k=sum(v >= t_obs - 1e-9 for v in values)
    return {'null':'LCDM', 'alternative':'RLL', 'observed_lrt':float(t_obs), 'replicates':n_sim, 'extreme_count':k,
            'plus_one_monte_carlo_p_exploratory':(k+1)/(n_sim+1), 'resolution':1/(n_sim+1),
            'reliable_tail_inference':False, 'critical_values_calibrated':False,
            'statistics':values, 'note':'No asymptotic chi-square p-value at Os=0: nuisance zt/wt unidentified. Bootstrap finite-sample, low B is a smoke test, not scientific significance.'}


def main(argv: list[str] | None = None) -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=ROOT);p.add_argument('--output-dir', type=Path, required=True)
    p.add_argument('--seed', type=int, default=1748365262);p.add_argument('--starts', type=int, default=8)
    p.add_argument('--bootstrap', type=int, default=8);p.add_argument('--leave-tracer-out', action='store_true')
    p.add_argument('--allow-unpinned', action='store_true', help='LOCAL TEST ONLY; forces claim_allowed=false and marks provenance as unverified')
    a=p.parse_args(argv)
    if a.seed<0 or a.bootstrap<0 or a.starts<2 or a.bootstrap>10000: p.error('invalid seed/starts/bootstrap')
    data=load_inputs(a.root, not a.allow_unpinned)
    fixed={'LCDM':chi2(data,'LCDM',np.array([67.4,.315])), 'RLL':chi2(data,'RLL',np.array([67.4,.315,.02,1.,.3]))}
    if not np.allclose([fixed['LCDM'],fixed['RLL']],[28.69374102,34.52753599],atol=0.00002,rtol=0) and not a.allow_unpinned:
        raise RuntimeError('BASELINE_CALCULATION_REGRESSION')
    fits={}
    fits['LCDM']=fit(data,'LCDM',a.seed,a.starts)
    fits['CPL']=fit(data,'CPL',a.seed,a.starts,fits['LCDM']['_theta'])
    fits['RLL']=fit(data,'RLL',a.seed,a.starts,fits['LCDM']['_theta'])
    if fits['RLL']['chi2'] > fits['LCDM']['chi2']+1e-6 or fits['CPL']['chi2'] > fits['LCDM']['chi2']+1e-6:
        raise RuntimeError('NESTING_OPTIMIZER_FAILURE_OBSERVED')
    jac=fits['RLL']['_jac']; scales=np.array([70.,.3,.1,.4,.1]); singular=np.linalg.svd(jac*scales, compute_uv=False)
    output={'schema':'rll.desi_dr2.adversarial_profile.v1','claim_allowed':False,'scientific_validation':'NOT_ESTABLISHED',
            'provenance_verified':not a.allow_unpinned,'source':data['source'],
            'method':{'likelihood':'correlated Gaussian BAO 13x13','integrator':'64 point Gauss-Legendre','fixed_rd_mpc':RD,'fixed_Omega_r':OR,
                      'seed':a.seed,'starts':a.starts,'bootstrap_simulations':a.bootstrap,'models':['LCDM','CPL','RLL'],
                      'numpy_version':np.__version__,'scipy_version':scipy.__version__,
                      'sigma_from_full_covariance':True,'no_asymptotic_LRT_under_nonregular_boundary':True},
            'fixed_point_chi2':fixed,'fit':{k:public_fit(v,len(data['y'])) for k,v in fits.items()},
            'rll_scaled_jacobian_singular_values':[float(v) for v in singular],
            'rll_fisher_condition_estimate':float((singular[0]/singular[-1])**2) if singular[-1] > 1e-10 else None,
            'rll_fisher_condition_state':'ILL_CONDITIONED' if singular[-1] > 1e-10 else 'SINGULAR_UNIDENTIFIED',
            'model_comparison':{'delta_chi2_rll_minus_lcdm':float(fits['RLL']['chi2']-fits['LCDM']['chi2']),
                                'delta_chi2_cpl_minus_lcdm':float(fits['CPL']['chi2']-fits['LCDM']['chi2']),
                                'information_criteria_exploratory_only':True},
            'holdout':holdout(data,a.seed,a.starts) if a.leave_tracer_out else {'state':'NOT_EXECUTED'},
            'null_bootstrap':bootstrap_null(data,fits['LCDM'],fits['RLL'],a.bootstrap,a.seed,a.starts) if a.bootstrap else {'state':'NOT_EXECUTED'},
            'limitations':['BAO only, no calibrated posterior/priors','fixed rd/Omega_r','not a certified global optimum',
                           'null boundary Os=0 unidentified zt/wt','no CLASS/CAMB perturbations','no joint SN/CMB/RSD full likelihood','not external referee verified']}
    payload=(json.dumps(output,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
    a.output_dir.mkdir(parents=True,exist_ok=True)
    fname=f'adversarial_s{a.seed}_n{a.starts}_b{a.bootstrap}_h{int(a.leave_tracer_out)}_{data["source"]["measurements"]["sha256"][:12]}.json'
    result=a.output_dir/fname
    with result.open('xb') as f:f.write(payload)  # never silently overwrite
    checksum=result.with_suffix(result.suffix+'.sha256')
    with checksum.open('x',encoding='ascii') as f:f.write(f'{hashlib.sha256(payload).hexdigest()}  {result.name}\n')
    print(json.dumps({'result':str(result),'sha256':hashlib.sha256(payload).hexdigest(),
                      'fixed_chi2':fixed,'fit_chi2':{k:v['chi2'] for k,v in fits.items()},'claim_allowed':False},sort_keys=True))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
