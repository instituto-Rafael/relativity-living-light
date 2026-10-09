#!/usr/bin/env python3
"""Source-bound G0/G1/G2 experiment; no change to likelihood or historical fit."""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
from types import SimpleNamespace
import numpy as np
from scipy.integrate import quad
from data.pipelines.structure_d import joint_real_likelihood as joint
from scripts import check_rll_growth as growth
from scripts import rll_joint_physics_preflight as previous

SOURCE=Path('data/pipelines/structure_d/joint_real_likelihood.py')
ARCHIVE=Path('results/structure_d/joint_real_likelihood.json')
SCHEMA='rll.joint_g0_g2_source_adapter.v1'

def _fingerprint(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def _model(row):
    h0,om,ol=map(float,(row['H0'],row['Om'],row['OL']))
    name=row['model']
    if name.startswith('LCDM'): return joint.e2_lcdm,(h0,om,ol)
    if name.startswith('wCDM'): return joint.e2_wcdm,(h0,om,ol,float(row['w']))
    if name.startswith('CPL'): return joint.e2_cpl,(h0,om,ol,float(row['w0']),float(row['wa']))
    if name.startswith('RLL'): return joint.e2_rll,(h0,om,ol,float(row['Os0']),float(row['zt']),float(row['wt']))
    raise ValueError('unsupported historical model: '+str(name))

def analyze(source=SOURCE,archived=ARCHIVE):
    facts=previous.source_facts(source.read_text(encoding='utf-8'))
    if not all(facts['functions_present'].values()) or not facts['cmb_uses_rd_drag_mpc'] or not facts['growth_uses_omega_m_z_approximation']:
        return {'schema':SCHEMA,'state':'TOKEN_VAZIO_SOURCE_DRIFT','claim_allowed':False,'facts':facts}
    data=json.loads(archived.read_text(encoding='utf-8'))
    models=[]
    for row in data['rows']:
        func,params=_model(row)
        actual_h0=float(joint.hz_from_e2(0.,func,params))
        ratio=actual_h0/params[0]
        models.append({'name':row['model'],'H0_fit':params[0], 'H_z0':actual_h0,'E_0':ratio,'gap':abs(ratio-1)})
    # Fiducial, normalized flat LCDM only. Not an RLL recombination model.
    h0,om,obh2,zstar=67.4,.315,.0224,1089.92
    ol=1-om-float(joint.ORAD)
    params=(h0,om,ol)
    r_drag=joint.rd_drag_mpc(h0,om,obh2)
    d_m=joint.comoving_distance_mpc(zstar,joint.e2_lcdm,params)
    rb=3*obh2/(4*2.4728e-5)
    r_star=(joint.C_KMS/(h0*math.sqrt(3)))*quad(lambda a:1/math.sqrt((float(joint.ORAD)+om*a+ol*a**4)*(1+rb*a)),0,1/(1+zstar),epsrel=1e-9)[0]
    l_drag=float(joint.cmb_shift_prediction(joint.e2_lcdm,params,obh2,zstar)[1])
    l_star=math.pi*d_m/r_star
    gp=SimpleNamespace(omega_m=om,sigma8_0=.8,a_min=.01,steps=1200)
    gr=growth.integrate_growth('lcdm',gp)
    growth_rows=[]
    for z in (0.,.5,1.,2.):
        ode=growth.interp(gr,z,'fsigma8')
        shortcut=float(joint.fsigma8_prediction(np.array([z]),joint.e2_lcdm,params,.8)[0])
        growth_rows.append({'z':z,'smooth_GR_control':ode,'joint_shortcut':shortcut,'absolute_gap':abs(ode-shortcut)})
    best=min(data['rows'],key=lambda r:float(r['BIC']))
    return {'schema':SCHEMA,'claim_allowed':False,'state':'NUMERIC_SOURCE_DIAGNOSTIC_NOT_PHYSICAL_VALIDATION',
        'source_sha256':_fingerprint(source),'archive_sha256':_fingerprint(archived),
        'historical_created_utc':data.get('created_utc'),'source_facts':facts,
        'g0':models,
        'g1':{'scope':'flat_normalized_LCDM_proxy_only_no_recombination_solver','z_star':zstar,'rd_drag_mpc':r_drag,
              'rs_star_background_proxy_mpc':r_star,'lA_drag_in_joint':l_drag,'lA_recombination_proxy':l_star,
              'absolute_delta_lA':abs(l_star-l_drag),'Boltzmann_backend':'TOKEN_VAZIO_NOT_RUN'},
        'g2':{'scope':'smooth_LCDM_GR_ode_control_radiation_omitted_in_growth_solver','rows':growth_rows,
              'RLL_perturbations':'TOKEN_VAZIO_NOT_RUN'},
        'g3':{'archived_RLL_Os0_zero':any(r.get('Os0')==0 for r in data['rows'] if str(r.get('model')).startswith('RLL'))},
        'g4':{'BIC_winner_archived':best['model'],'historical_interpretation':data.get('interpretation_label')},
        'fnext':'match physical convention, use CLASS/CAMB and rerun fit with identical priors'}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,default=SOURCE)
    p.add_argument('--archived',type=Path,default=ARCHIVE)
    p.add_argument('--output',type=Path)
    a=p.parse_args()
    if a.output and a.output.resolve() in (a.source.resolve(),a.archived.resolve()):p.error('cannot overwrite scientific input')
    result=analyze(a.source,a.archived)
    data=json.dumps(result,indent=2,ensure_ascii=False,sort_keys=True,allow_nan=False)+'\n'
    if a.output:
        a.output.parent.mkdir(parents=True,exist_ok=True)
        a.output.write_text(data,encoding='utf-8')
    else:print(data,end='')
    return 0 if result['state'].startswith('NUMERIC_') else 3
if __name__=='__main__':raise SystemExit(main())
