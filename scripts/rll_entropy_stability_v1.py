#!/usr/bin/env python3
"""RLL entropy-stability counterexample: fixed 7 windows of 50 toy samples.

Demonstrates that H(X_t) constant cannot establish stationarity of X_t,
parameter stability or cosmological physical stability. No real sky data.

SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM
"""
from __future__ import annotations
import argparse
from collections import Counter
import json, math
from pathlib import Path

SCHEMA='rll.entropy_dispersion_stability.synthetic_counterexample.v1'


def finite_seq(xs):
    out=[float(x) for x in xs]
    if not out or not all(math.isfinite(x) for x in out):
        raise ValueError('empty or nonfinite values')
    return out


def sample_std(xs):
    xs=finite_seq(xs)
    if len(xs)<2:
        return None  # TOKEN_VAZIO_N_LT_2, never 0 by fiat
    avg=sum(xs)/len(xs)
    return math.sqrt(sum((x-avg)**2 for x in xs)/(len(xs)-1))


def entropy_discrete(xs):
    """Empirical discrete Shannon entropy (bits/sample); finite alphabet.

    This is NOT differential entropy, thermodynamic entropy, or an estimator
    with a finite-sample-bias correction. Relabeling is entropy invariant.
    """
    xs=finite_seq(xs)
    counts=Counter(xs);n=len(xs)
    return -sum((v/n)*math.log2(v/n) for v in counts.values())


def slope(x,y):
    x=finite_seq(x);y=finite_seq(y)
    if len(x)!=len(y) or len(x)<2:
        return None
    xx=sum(x)/len(x);yy=sum(y)/len(y)
    denom=sum((v-xx)**2 for v in x)
    if denom==0:
        return None
    return sum((a-xx)*(b-yy) for a,b in zip(x,y))/denom


def between_within(groups):
    if not groups:
        raise ValueError('no groups')
    vs=[v for g in groups for v in finite_seq(g)]
    grand=sum(vs)/len(vs)
    total=sum((v-grand)**2 for v in vs)
    within=0.0;between=0.0
    for grp in groups:
        grp=finite_seq(grp)
        mean=sum(grp)/len(grp)
        within+=sum((v-mean)**2 for v in grp)
        between+=len(grp)*(mean-grand)**2
    return dict(total_sse=total,within_sse=within,between_sse=between,
                closure_error=total-within-between,
                between_fraction=(between/total if total else 0.0))


def summarize(groups):
    x=list(range(len(groups)))
    h=[entropy_discrete(g) for g in groups]
    m=[sum(g)/len(g) for g in groups]
    s=[sample_std(g) for g in groups]
    return {
       'per_window':[
           {'time_index':i,'n':len(g),'mean':m[i],
            'sample_std':s[i],'shannon_empirical_bits_per_symbol':h[i]}
           for i,g in enumerate(groups)],
       'H_mean':sum(h)/len(h),'H_sample_std':sample_std(h),
       'H_linear_slope_bits_per_window':slope(x,h),
       'mean_linear_slope_value_per_window':slope(x,m),
       'mean_sample_std_across_windows':sample_std(m),
       'variance_decomposition':between_within(groups)
    }


def compute():
    # 50 samples/window, 5 discrete states each observed 10 times.
    # The second case is a pure translation of the alphabet in each window.
    # All seven windows have exactly the same Shannon entropy and intra-window
    # variance. However, their means have a nonzero systematic slope.
    core=[-2.,-1.,0.,1.,2.]*10
    stable=[core[:] for _ in range(7)]
    drift=[[v+float(j) for v in core] for j in range(7)]
    s0=summarize(stable);s1=summarize(drift)
    assert s0['H_sample_std']==0.0 and s1['H_sample_std']==0.0
    assert abs(s1['mean_linear_slope_value_per_window']-1.0)<1e-12
    assert abs(s0['mean_linear_slope_value_per_window'])<1e-12
    assert s1['variance_decomposition']['between_fraction']>0
    assert abs(s0['H_mean']-math.log2(5))<1e-12
    return {
       'schema':SCHEMA,
       'status':'PASS_SCOPED_SYNTHETIC_COUNTEREXAMPLE',
       'dataset':'SYNTHETIC_SEVEN_WINDOWS_OF_FIFTY; NOT_ASTRONOMICAL',
       'quantization':'native discrete integer alphabet; no observational bin estimator',
       'claim_allowed':False,'cosmology_fit_modified':False,
       'equal_entropy_does_not_imply_stationarity':True,
       'baseline':s0,'drifting':s1,
       'separate_questions':{
          'observational':'Residuals must use committed full covariance and physical units',
          'statistical':'H, std(H), slopes, KL and chi2 need null calibration',
          'physical':'Dynamical stability needs equations, initial states, perturbations, regime and timescales',
          'compression':'Same compression ratio does not establish equal Shannon entropy or semantics',
          'geometry':'T7 may index parameter sweeps; not seven physical spacetime dimensions'},
       'gates':{
          'real_data':'TOKEN_VAZIO_PINNED_COSMOLOGICAL_RESIDUAL_INPUTS',
          'null_ensemble':'TOKEN_VAZIO_PREREGISTERED_NULL_AND_BOOTSTRAP',
          'time_order':'TOKEN_VAZIO_ASTROPHYSICAL_TIME_COORDINATE',
          'likelihood':'PRESERVE_CURRENT_RLL_COVARIANCE_AND_CHI2',
          'held_out_validation':'NOT_RUN',
          'lyapunov':'TOKEN_VAZIO_PHYSICAL_DYNAMICS_AND_PERTURBATION_EVOLUTION',
          'thermal_entropy':'TOKEN_VAZIO_THERMODYNAMIC_STATE_AND_EOS',
          'independent_reproduction':'NOT_RUN'}
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--output',type=Path)
    args=p.parse_args()
    data=json.dumps(compute(),indent=2,ensure_ascii=False,sort_keys=True)+'\n'
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(data,encoding='utf-8')
    else:print(data,end='')

if __name__=='__main__':main()
