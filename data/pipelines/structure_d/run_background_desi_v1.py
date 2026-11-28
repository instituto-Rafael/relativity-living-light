"""Opt-in DESI-only background run; never overwrites historical results."""
import argparse
import json
import hashlib
from pathlib import Path
from .background_likelihood_v1 import BackgroundLikelihood, GaussianBlock, Row, fit_background

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--maxiter',type=int,default=180)
    args=parser.parse_args()
    if args.output.exists(): raise FileExistsError(args.output)
    from . import joint_real_likelihood as producer
    import pandas as pd
    paths=(producer.DESI_POINTS_PATH,producer.DESI_FULL_COV_PATH)
    hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    points=pd.read_csv(producer.DESI_POINTS_PATH)
    summary=pd.read_csv(producer.DESI_COV_SUMMARY_PATH)
    cov, info=producer._load_desi_covariance(points,summary)
    if info.get('mode')!='official_full' or not info.get('ready') or info.get('uncertainty_or_covariance_status')!='manifest_bound_native_cobaya_permuted_to_primary_order':
        raise ValueError('TOKEN_VAZIO_VERIFIED_OFFICIAL_ORDERED_COVARIANCE')
    if hashes!={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}: raise ValueError('input changed during preflight')
    rows=[Row(f'{r.tracer}:{r.observable}:{r.z_eff}',str(r.observable),float(r.z_eff),float(r.value)) for r in points.itertuples()]
    b=GaussianBlock(rows,cov,[r.key for r in rows],source_ref='https://arxiv.org/abs/2503.14738',overlap_groups=('DESI_DR2_BAO_LYA',))
    likelihood=BackgroundLikelihood([b]); common={'om':(.1,.6),'rd':(100.,200.)}
    extras={'lcdm':{},'wcdm':{'w0':(-2.,-.3)},'cpl':{'w0':(-2.,-.3),'wa':(-3.,3.)},'rll':{'os0':(0.,.25),'zt':(.1,10.),'wt':(.05,2.)}}
    payload={'schema':'rll.background.desi.v1','claim_allowed':False,'scope':'DESI DR2 BAO only; radiation omitted; H0=70 arbitrary scale pivot, not measured','data_covariance':info,'input_sha256':hashes,'excluded':{'CC':'TOKEN_VAZIO_RECONCILED_CC_COVARIANCE','SN':'TOKEN_VAZIO_FROZEN_CATALOGS','LyA_AP':'TOKEN_VAZIO_REPLACEMENT_COVARIANCE','growth':'TOKEN_VAZIO_PHYSICAL_CLOSURE','CMB':'TOKEN_VAZIO_PHYSICAL_CLOSURE'},'results':[]}
    for model, extra in extras.items():
        payload['results'].append(fit_background(likelihood,model,{**common,**extra},fixed={'h0':70.},maxiter=args.maxiter))
    # A nested candidate cannot have a true optimum worse than its null.
    null=payload['results'][0]['best']['chi2']
    for result in payload['results'][1:]:
        if result['best']['chi2']>null+1e-3:
            result['state']='OPTIMIZATION_UNCONFIRMED_NULL_DOMINATES'; result['metrics']={'AIC':None,'AICc':None,'BIC':None}
    with args.output.open('x',encoding='utf-8') as f: json.dump(payload,f,indent=2,allow_nan=False)
if __name__=='__main__': main()
