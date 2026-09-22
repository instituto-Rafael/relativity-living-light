#!/usr/bin/env python3
"""Isolated DESI DR2 vector-likelihood adapter.

Consumes an emitted OBSERVABLE_ORDER.csv, covariance matrix CSV, and a predictions
CSV keyed by index. It computes full-covariance and diagonal chi2 without
modifying the canonical cosmological fit. It does not validate the physical
model, official cross-block covariance, or scientific superiority.
"""
from __future__ import annotations
import argparse,csv,json,math
from pathlib import Path

CLAIM_ALLOWED=False

class VectorLikelihoodError(RuntimeError): pass

def _rows(p):
    with Path(p).open(encoding='utf-8',newline='') as h: return list(csv.DictReader(h))

def _matrix(p):
    rows=_rows(p)
    if not rows: raise VectorLikelihoodError('empty covariance matrix')
    cols=[k for k in rows[0] if k!='row']
    m=[[float(r[c]) for c in cols] for r in rows]
    if len(m)!=len(cols) or any(len(r)!=len(m) for r in m): raise VectorLikelihoodError('covariance must be square')
    return m

def _solve(a,b):
    n=len(a); aug=[list(map(float,a[i]))+[float(b[i])] for i in range(n)]
    for c in range(n):
        p=max(range(c,n),key=lambda r:abs(aug[r][c]))
        if abs(aug[p][c])<1e-15: raise VectorLikelihoodError('singular covariance')
        aug[c],aug[p]=aug[p],aug[c]
        q=aug[c][c]; aug[c]=[x/q for x in aug[c]]
        for r in range(n):
            if r==c: continue
            q=aug[r][c]
            aug[r]=[aug[r][j]-q*aug[c][j] for j in range(n+1)]
    return [aug[i][-1] for i in range(n)]

def evaluate(order_path,cov_path,pred_path):
    order=_rows(order_path); pred=_rows(pred_path); cov=_matrix(cov_path)
    if len(order)!=len(cov): raise VectorLikelihoodError('order/covariance size mismatch')
    by={int(r['index']):r for r in pred}
    if set(by)!=set(range(len(order))): raise VectorLikelihoodError('predictions must cover every emitted index exactly once')
    residual=[]
    for i,row in enumerate(order):
        obs=float(row['value']); model=float(by[i]['prediction'])
        if not math.isfinite(obs) or not math.isfinite(model): raise VectorLikelihoodError('non-finite value')
        residual.append(obs-model)
    solved=_solve(cov,residual)
    chi2_full=sum(r*s for r,s in zip(residual,solved))
    chi2_diag=0.0
    for i,r in enumerate(residual):
        v=cov[i][i]
        if v<=0: raise VectorLikelihoodError('non-positive covariance diagonal')
        chi2_diag+=r*r/v
    return {'schema':'rll.desi_dr2_vector_likelihood.v1','observable_count':len(order),'chi2_full':chi2_full,'chi2_diagonal':chi2_diag,'delta_chi2_full_minus_diagonal':chi2_full-chi2_diag,'claim_allowed':False,'scientific_fit_promoted':False,'full_official_cross_block_covariance_claimed':False}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--order',required=True); ap.add_argument('--covariance',required=True); ap.add_argument('--predictions',required=True); ap.add_argument('--output')
    a=ap.parse_args()
    try: out=evaluate(a.order,a.covariance,a.predictions)
    except (VectorLikelihoodError,ValueError,KeyError) as e:
        print(f'VECTOR_LIKELIHOOD_ERROR: {e}'); return 2
    text=json.dumps(out,indent=2,sort_keys=True)+'\n'
    if a.output: Path(a.output).write_text(text,encoding='utf-8')
    print(text,end=''); return 0
if __name__=='__main__': raise SystemExit(main())
