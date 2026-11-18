#!/usr/bin/env python3
"""Independent DESI DR2 BAO-only 3-model test; G4 source equations and source-bound C.

Purpose: diagnose LCDM/wCDM/RLL background on the same BAO vector.
NOT Pantheon, NOT G4 full background, NOT a scientific confirmation.
claim_allowed=False. G4 E2 is authoritative; this file does not duplicate it.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import sys
import numpy as np
from scipy.linalg import solve_triangular
from scipy.optimize import least_squares
from numpy.polynomial.legendre import leggauss

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))
from tools import run_g4_background_tournament as g4
from tools.bao_boundary_gate_v1 import boundary_report, gate_boundary_claim, format_chi2

C_KM_S=299792.458
PARAMS={
    'LCDM': ('q_c_over_H0_rd','Omega_m'),
    'wCDM': ('q_c_over_H0_rd','Omega_m','w'),
    'RLL': ('q_c_over_H0_rd','Omega_m','Omega_s0','z_t','w_t'),
}
LIMITS={
    'LCDM': ((18,.10),(42,.60)),
    'wCDM': ((18,.10,-2),(42,.60,-.3)),
    'RLL': ((18,.10,0,.10,.05),(42,.60,.25,10,2)),
}
STARTS={
    'LCDM': ((29.52,.30),),
    'wCDM': ((29.52,.30,-1.0),),
    'RLL': ((29.52,.30,0,1,.30),(28.45,.14,.13,.40,.05)),
}

def model_e2(z,model,p):
    # BAO-only q=c/(H0*rd) absorbs H0 and rd. H0 and omega_b_h2 are
    # dummy positive constants *only* for G4 E2, which does not depend on
    # either for LCDM/wCDM/RLL. No inference on H0 or rd is permitted.
    return g4.e2(model,z,[70.0,float(p[1]),.02236,*map(float,p[2:])])

def model_predictions(block,model,p,nodes,weights):
    z=np.asarray(block.z,float)
    zs=.5*z[:,None]*(nodes[None,:]+1)
    e2grid=model_e2(zs,model,p)
    e2z=model_e2(z,model,p)
    if not (np.isfinite(e2grid).all() and np.isfinite(e2z).all() and
            np.all(e2grid>0) and np.all(e2z>0)):
        raise ValueError('E2 must be finite and positive')
    dc=.5*z*np.sum(weights[None,:]/np.sqrt(e2grid),axis=1)
    dh=1/np.sqrt(e2z)
    q=float(p[0])
    dm_pred=q*dc;dh_pred=q*dh;dv_pred=q*(z*dh*dc**2)**(1/3)
    d={'DM_over_rd':dm_pred,'DH_over_rd':dh_pred,'DV_over_rd':dv_pred}
    out=np.asarray([d[key][i] for i,key in enumerate(block.observable)],float)
    if not np.all(np.isfinite(out)):
        raise ValueError('BAO predictions not finite')
    return out

def _input_block():
    block=g4.load_desi()  # validates 13 rows and source/covariance ordering
    if block.n!=13 or block.covariance.shape!=(13,13):
        raise ValueError('unsupported DESI shape')
    if not np.allclose(block.covariance,block.covariance.T,rtol=0,atol=1e-12):
        raise ValueError('covariance must be symmetric')
    np.linalg.cholesky(block.covariance)
    return block

def fit(block,model,starts_extra=18,seed=20261118):
    lower,upper=LIMITS[model]
    rng=np.random.default_rng(seed)
    initials=[np.asarray(x,float) for x in STARTS[model]]
    initials += [rng.uniform(lower,upper) for _ in range(starts_extra)]
    l=np.linalg.cholesky(block.covariance)
    nodes,weights=leggauss(96)
    nodes_hi,weights_hi=leggauss(192)
    def residual(p):
        try:
            out=model_predictions(block,model,p,nodes,weights)
            return solve_triangular(l,out-block.observed,lower=True,check_finite=True)
        except (ValueError,OverflowError,FloatingPointError):
            return np.full(block.n,1e6)
    scores=[]
    for i,p0 in enumerate(initials):
        opt=least_squares(residual,p0,bounds=(lower,upper),max_nfev=500,
                          xtol=1e-11,ftol=1e-11,gtol=1e-10)
        chi=float(opt.fun@opt.fun)
        scores.append((chi,i,opt))
    chi,i,opt=min(scores,key=lambda x:x[0])
    # Recheck quadrature with twice as many nodes, against identical data/C.
    out=model_predictions(block,model,opt.x,nodes_hi,weights_hi)
    diff=solve_triangular(l,out-block.observed,lower=True,check_finite=True)
    exact_chi=float(diff@diff)
    n=block.n;k=len(opt.x)
    boundary=boundary_report(opt,(lower,upper),PARAMS[model],n)
    gate_boundary_claim(boundary)
    result={'model':model,'N':n,'k':k,'chi2':exact_chi,
            'chi2_display':format_chi2(exact_chi,boundary),
            'boundary_diagnostics':boundary,
            'min_grad_inf':boundary['min_grad_inf'],
            'claim_blocked_reason':boundary['claim_blocked_reason'],
            'optimization_quadrature_nodes':96,
            'verification_quadrature_nodes':192,
            'AIC':exact_chi+2*k,'AICc':exact_chi+2*k+2*k*(k+1)/(n-k-1),
            'BIC':exact_chi+k*math.log(n),
            'parameters':dict(zip(PARAMS[model],map(float,opt.x))),
            'best_initialization_index':i,'optimizer_success':bool(opt.success),
            'starts':len(initials),
            'finite_starts':sum(math.isfinite(x[0]) for x in scores),
            'chi2_min_max':[float(min(s[0] for s in scores)),float(max(s[0] for s in scores))],
            'predictions':[float(x) for x in out],
            'claim_allowed':False}
    return result

def run(starts_extra=18):
    block=_input_block()
    z_check=np.linspace(0,2.5,131)
    base=model_e2(z_check,'LCDM',[29.52,.30])
    null_tests={
       'wCDM_w_minus_one':float(np.max(np.abs(base-model_e2(z_check,'wCDM',[29.52,.30,-1])))),
       'RLL_Omega_s0_zero':float(np.max(np.abs(base-model_e2(z_check,'RLL',[29.52,.30,0,1,.30])))),
    }
    if any(v>1e-12 for v in null_tests.values()):
        raise ValueError('nested null-limit failure')
    rows=[fit(block,name,starts_extra=starts_extra) for name in PARAMS]
    results={item['model']: {
        'chi2':item['chi2'],
        'chi2_display':item['chi2_display'],
        'boundary_diagnostics':item['boundary_diagnostics'],
        'min_grad_inf':item['min_grad_inf'],
        'claim_allowed':False,
        'claim_blocked_reason':item['claim_blocked_reason'],
    } for item in rows}
    for item in results.values():
        gate_boundary_claim(item['boundary_diagnostics'])
    rendered_table={
        'rows':[{'model':item['model'], 'chi2':item['chi2_display'],
                 'AICc':item['AICc'], 'BIC':item['BIC']} for item in rows],
        'footnote':'* corner: fitted optimum at declared parameter bound; see results.<model>.boundary_diagnostics. Not a scientific endorsement.',
    }
    return {'schema':'rll.bao_only_g4_three_model.v1','state':'BAO_ONLY_EXECUTED','claim_allowed':False,
            'source':'rll/lab tools/run_g4_background_tournament.py + pinned DESI DR2 local input',
            'data_blobs':{'points':'f6d05ead6fef7fea663eff8b31bc2c337dc30435','covariance':'e01d0235a2f0e61d81af0c36a7338953f845f5c3'},
            'n_observables':block.n,'covariance':'full_13x13_source_order_bound',
            'null_tests':null_tests,'independent_amplitude':'q=c/(H0*r_d)',
            'radiation_source':'G4 OMEGA_R0',
            'models':rows,
            'results':results,
            'rendered_table':rendered_table,
            'Pantheon_plus':'TOKEN_VAZIO_FULL_COVARIANCE',
            'G4_joint_fit':'NOT_RUN',
            'claim_note':'BAO-only results depend on bounds, are not Pantheon or full physics and cannot confirm RLL superiority.'}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--starts-extra',type=int,default=18)
    parser.add_argument('--output',type=Path,required=True)
    ns=parser.parse_args()
    if not 0<=ns.starts_extra<=64:parser.error('starts-extra outside 0..64')
    if ns.output.exists():parser.error('append-only safety: output exists, choose a new path')
    report=run(starts_extra=ns.starts_extra)
    ns.output.parent.mkdir(parents=True,exist_ok=True)
    ns.output.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({'state':report['state'],'rows':[{'model':r['model'],'chi2':r['chi2_display'],'AICc':r['AICc'],'BIC':r['BIC']} for r in report['models']], 'footnote':report['rendered_table']['footnote'],'Pantheon_plus':report['Pantheon_plus']},ensure_ascii=False))

if __name__=='__main__':main()
