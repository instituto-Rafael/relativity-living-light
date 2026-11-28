"""Opt-in late-time background adapter; never changes legacy output or claims."""
from dataclasses import dataclass
import math
import numpy as np
from scipy.linalg import cholesky, solve_triangular
from scipy.integrate import quad

C = 299792.458
MODELS = ('lcdm', 'wcdm', 'cpl', 'rll')
BLOCKED = 'TOKEN_VAZIO_PHYSICAL_CLOSURE'

@dataclass(frozen=True)
class Background:
    model: str
    h0: float
    om: float
    rd: float
    w0: float = -1.
    wa: float = 0.
    os0: float = 0.
    zt: float = 1.
    wt: float = .3

    def __post_init__(self):
        if self.model not in MODELS or not all(math.isfinite(x) for x in (self.h0,self.om,self.rd,self.w0,self.wa,self.os0,self.zt,self.wt)):
            raise ValueError('invalid model or parameters')
        if not (self.h0 > 0 and self.rd > 0 and 0 < self.om < 1 and 0 <= self.os0 <= 1-self.om and self.wt > 0):
            raise ValueError('outside declared flat background domain')
        if self.model != 'rll' and self.os0 != 0 or self.model in ('lcdm','rll') and (self.w0 != -1 or self.wa != 0) or self.model == 'wcdm' and self.wa != 0:
            raise ValueError('inactive parameters must remain at null values')

    def h(self,z):
        # Reuse producer equations, not a second independently drifting model.
        from rll_vs_lcdm import h_model
        if not math.isfinite(z) or z < 0: raise ValueError('invalid redshift')
        model = 'w0wa' if self.model in ('wcdm','cpl') else self.model
        # Exact null dispatch avoids cancellation and tests the same likelihood.
        if (model == 'rll' and self.os0 == 0) or (model == 'w0wa' and self.w0 == -1 and self.wa == 0): model='lcdm'
        v=h_model(z,self.h0,model,self.om,self.w0,self.wa,self.os0,self.zt,self.wt)
        if not math.isfinite(v) or v <= 0: raise ValueError('nonpositive or nonfinite H')
        return v

    def predict(self, obs, z, zhel=None):
        if obs == 'H': return self.h(z)
        if obs == 'DH_over_rd': return C/self.h(z)/self.rd
        if obs in ('DM_over_rd','DV_over_rd','SN_mu'):
            dm=C*quad(lambda q: 1/self.h(q),0,z,epsabs=1e-11,epsrel=1e-9)[0]
            if obs == 'DM_over_rd': return dm/self.rd
            if obs == 'DV_over_rd': return (z*(dm/self.rd)**2*C/self.h(z)/self.rd)**(1/3)
            if zhel is None or not math.isfinite(zhel) or zhel <= -1 or dm <= 0: raise ValueError('SN requires zhel and positive distance')
            return 5*math.log10((1+zhel)*dm)+25
        raise ValueError('unsupported observable: '+str(obs))

    def physical_outputs(self):
        return {'rd_policy':'FREE_NUISANCE_LATE_TIME', 'fsigma8':BLOCKED,'S8':BLOCKED,'Cl':BLOCKED,'claim_allowed':False}

@dataclass(frozen=True)
class Row:
    key: str
    obs: str
    z: float
    value: float
    zhel: float | None = None

class GaussianBlock:
    def __init__(self, rows, covariance, axis_keys, *, source_ref, overlap_groups, sn_catalog=None):
        self.rows=tuple(rows)
        keys=tuple(r.key for r in self.rows)
        if not keys or len(set(keys)) != len(keys) or tuple(axis_keys)!=keys: raise ValueError('covariance axis mismatch')
        self.groups=frozenset(overlap_groups)
        if not source_ref or not self.groups or '' in self.groups: raise ValueError('missing source or overlap identity')
        self.source_ref=source_ref
        self.sn_catalog=sn_catalog
        if any(not math.isfinite(r.value) or not math.isfinite(r.z) or r.z<0 for r in self.rows): raise ValueError('nonfinite observation')
        sn=[r.obs=='SN_mu' for r in self.rows]
        if any(sn) != bool(sn_catalog) or any(sn) and not all(sn): raise ValueError('SN must be one separate catalog block')
        cov=np.array(covariance,dtype=float,copy=True)
        n=len(keys)
        if cov.shape!=(n,n) or not np.isfinite(cov).all() or not np.allclose(cov,cov.T,rtol=1e-12,atol=0): raise ValueError('invalid covariance')
        self.lower=cholesky(cov,lower=True)
        self.lower.setflags(write=False)

    def chi2(self, model):
        residual=np.array([r.value-model.predict(r.obs,r.z,r.zhel) for r in self.rows])
        y=solve_triangular(self.lower,residual,lower=True)
        if self.sn_catalog:
            # Profile one free additive magnitude nuisance for the entire catalog.
            t=solve_triangular(self.lower,np.ones(len(y)),lower=True)
            y=y-t*(np.dot(t,y)/np.dot(t,t))
        return float(np.dot(y,y))

class BackgroundLikelihood:
    def __init__(self, blocks):
        self.blocks=tuple(blocks)
        if not self.blocks: raise ValueError('empty likelihood')
        seen=set(); seen_keys=set(); sn=0
        for b in self.blocks:
            if seen & b.groups: raise ValueError('overlap or cross-covariance not resolved')
            keys={r.key for r in b.rows}
            if seen_keys & keys: raise ValueError('duplicate observation identity')
            seen_keys.update(keys); seen.update(b.groups); sn+=bool(b.sn_catalog)
        if sn>1: raise ValueError('compare SN catalogs in separate runs')

    def evaluate(self, model):
        terms=[b.chi2(model) for b in self.blocks]
        return {'chi2':sum(terms),'components':terms,'state':'POINT_EVALUATION','claim_allowed':False}

    def split(self, held_out):
        if not 0 <= held_out < len(self.blocks) or len(self.blocks)<2: raise ValueError('invalid holdout')
        return BackgroundLikelihood(b for i,b in enumerate(self.blocks) if i!=held_out), self.blocks[held_out]

def fit_background(likelihood, model, bounds, *, fixed=None, seeds=(42,43,44), maxiter=180, tol=1e-7):
    """Explicit profiling, not posterior/evidence. No silent convergence promotion."""
    from scipy.optimize import differential_evolution
    fixed=dict(fixed or {})
    names=tuple(bounds)
    active={'lcdm':{'h0','om','rd'},'wcdm':{'h0','om','rd','w0'},'cpl':{'h0','om','rd','w0','wa'},'rll':{'h0','om','rd','os0','zt','wt'}}[model]
    if set(names)&set(fixed) or set(names)|set(fixed)!=active or not names: raise ValueError('explicit active parameter partition required')
    if len(seeds)<2 or len(set(seeds))!=len(seeds) or maxiter<1 or tol<=0: raise ValueError('invalid multiseed policy')
    if any(len(b)!=2 or not all(math.isfinite(x) for x in b) or b[0]>=b[1] for b in bounds.values()): raise ValueError('invalid bounds')
    # For BAO/SN-only, H0 and rd cannot be identified independently.
    if {'h0','rd'} <= set(names) and not any(r.obs=='H' for b in likelihood.blocks for r in b.rows): raise ValueError('unidentified absolute scale: fix one pivot or add independent H(z)')
    def objective(x):
        try: return likelihood.evaluate(Background(model,**fixed,**dict(zip(names,x))))['chi2']
        except (ValueError, OverflowError, FloatingPointError): return float('inf')
    runs=[]
    for seed in seeds:
        r=differential_evolution(objective,[bounds[n] for n in names],seed=seed,maxiter=maxiter,tol=tol,workers=1,polish=True)
        if not math.isfinite(r.fun): raise ValueError('no finite objective')
        runs.append({'seed':int(seed),'chi2':float(r.fun),'params':{**fixed,**dict(zip(names,map(float,r.x)))},'success':bool(r.success),'message':str(r.message),'nfev':int(r.nfev)})
    best=min(runs,key=lambda r:r['chi2'])
    stable=all(r['success'] for r in runs) and max(r['chi2'] for r in runs)-best['chi2']<=1e-3
    k=len(names)+sum(bool(b.sn_catalog) for b in likelihood.blocks)
    n=sum(len(b.rows) for b in likelihood.blocks)
    metrics={'AIC':None,'AICc':None,'BIC':None}
    if stable:
        metrics={'AIC':best['chi2']+2*k,'AICc':best['chi2']+2*k+2*k*(k+1)/(n-k-1) if n>k+1 else None,'BIC':best['chi2']+k*math.log(n)}
    return {'model':model,'state':'PROFILED_FIT_SCOPED' if stable else 'OPTIMIZATION_UNCONFIRMED','best':best,'runs':runs,'k':k,'n_rows':n,'metrics':metrics,'claim_allowed':False,'evidence':'TOKEN_VAZIO_POSTERIOR','criteria_boundary':'descriptive only; regularity and effective sample size must be checked'}
