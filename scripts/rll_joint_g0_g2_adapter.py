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

def _model(row):
    h0,om,ol=map(float,(row['H0'],row['Om'],row['OL']))
    name=row['model']
    if name.startswith('LCDM'): return joint.e2_lcdm,(h0,om,ol)
    if name.startswith('wCDM'): return joint.e2_wcdm,(h0,om,ol,float(row['w']))
    if name.startswith('CPL'): return joint.e2_cpl,(h0,om,ol,float(row['w0']),float(row['wa']))
    if name.startswith('RLL'): return joint.e2_rll,(h0,om,ol,float(row['Os0']),float(row['zt']),float(row['wt']))
    raise ValueError('unsupported historical model: '+str(name))

def _reject_nonfinite_json_constant(value):
    raise ValueError("non-finite JSON constant: " + value)

def _blocked(state, **details):
    return {'schema':SCHEMA, 'state':state, 'claim_allowed':False, **details}

def _valid_archived_rows(data):
    if not isinstance(data, dict) or data.get('schema') != 'rll.joint_real_likelihood.v2' or data.get('dataset_type') != 'real_observational':
        return False
    rows = data.get('rows')
    if not isinstance(rows, list) or not rows:
        return False
    names = set()
    for row in rows:
        if not isinstance(row, dict):
            return False
        model = row.get('model')
        if not isinstance(model, str) or model in names:
            return False
        names.add(model)
        specific = ('w',) if model.startswith('wCDM') else (('w0','wa') if model.startswith('CPL') else (('Os0','zt','wt') if model.startswith('RLL') else ()))
        if not model.startswith(('LCDM','wCDM','CPL','RLL')):
            return False
        for key in ('H0','Om','OL','BIC') + specific:
            item = row.get(key)
            if isinstance(item, bool) or item is None:
                return False
            try:
                if not math.isfinite(float(item)):
                    return False
            except (TypeError, ValueError, OverflowError):
                return False
        if float(row['H0']) <= 0.0:
            return False
    return True

def analyze(source=SOURCE,archived=ARCHIVE):
    # Single byte-observation for every source hash and AST check (avoid double-read drift).
    try:
        source_bytes=source.read_bytes()
    except OSError:
        return _blocked('TOKEN_VAZIO_SOURCE_UNAVAILABLE')
    try:
        facts=previous.source_facts(source_bytes.decode('utf-8'))
    except (UnicodeDecodeError, SyntaxError, ValueError):
        return _blocked('TOKEN_VAZIO_SOURCE_DRIFT',reason='SOURCE_SYNTAX_OR_ENCODING')
    if not all(facts['functions_present'].values()) or not facts['cmb_uses_rd_drag_mpc'] or not facts['growth_uses_omega_m_z_approximation']:
        return _blocked('TOKEN_VAZIO_SOURCE_DRIFT',facts=facts)
    # A caller-supplied source file cannot describe a separately imported executable.
    # Same-path binding is a minimum gate; in-memory module bytecode equivalence is not proven.
    imported_file=getattr(joint,'__file__',None)
    if not imported_file or source.resolve() != Path(imported_file).resolve():
        return _blocked('TOKEN_VAZIO_SOURCE_RUNTIME_BINDING',facts=facts,
                        source_identity='PATH_MISMATCH_OR_UNKNOWN')
    try:
        archive_bytes=archived.read_bytes()
    except OSError:
        return _blocked('TOKEN_VAZIO_ARCHIVE_UNAVAILABLE')
    try:
        data=json.loads(archive_bytes,parse_constant=_reject_nonfinite_json_constant)
    except (ValueError, TypeError, UnicodeDecodeError):
        return _blocked('TOKEN_VAZIO_ARCHIVE_INVALID',reason='JSON_UNPARSABLE_OR_NONFINITE')
    if not _valid_archived_rows(data):
        return _blocked('TOKEN_VAZIO_ARCHIVE_INVALID',reason='ARCHIVE_SCHEMA_ROWS_OR_FINITE_VALUES')
    models=[]
    for row in data['rows']:
        func,params=_model(row)
        e2_zero=float(func(0.,*params))
        if not math.isfinite(e2_zero) or e2_zero <= 0.0:
            return _blocked('TOKEN_VAZIO_MODEL_E2_NONPOSITIVE',model=row['model'])
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
    pairwise=[row for row in data['rows'] if row['model'].startswith(('LCDM','RLL'))]
    pairwise_best=min(pairwise,key=lambda r:float(r['BIC']))['model'] if pairwise else None
    return {'schema':SCHEMA,'claim_allowed':False,'state':'NUMERIC_SOURCE_DIAGNOSTIC_NOT_PHYSICAL_VALIDATION',
        'source_sha256':hashlib.sha256(source_bytes).hexdigest(),'archive_sha256':hashlib.sha256(archive_bytes).hexdigest(),
        'runtime_source_path_identity':'MATCH_SCOPED_NOT_BYTECODE_ATTESTATION',
        'source_archive_execution_identity':'TOKEN_VAZIO_HISTORICAL_FIT_SOURCE_NOT_ATTESTED',
        'historical_created_utc':data.get('created_utc'),'source_facts':facts,
        'g0':models,
        'g1':{'scope':'flat_normalized_LCDM_proxy_only_no_recombination_solver','z_star':zstar,'rd_drag_mpc':r_drag,
              'rs_star_background_proxy_mpc':r_star,'lA_drag_in_joint':l_drag,'lA_recombination_proxy':l_star,
              'absolute_delta_lA':abs(l_star-l_drag),'Boltzmann_backend':'TOKEN_VAZIO_NOT_RUN'},
        'g2':{'scope':'smooth_LCDM_GR_ode_control_radiation_omitted_in_growth_solver','rows':growth_rows,
              'RLL_perturbations':'TOKEN_VAZIO_NOT_RUN'},
        'g3':{'archived_RLL_Os0_zero':any(r.get('Os0')==0 for r in data['rows'] if str(r.get('model')).startswith('RLL'))},
        'g4':{'BIC_winner_archived':best['model'],'historical_interpretation':data.get('interpretation_label'),
              'BIC_winner_RLL_vs_LCDM':pairwise_best,
              'historical_label_scope':'TOKEN_VAZIO_UNRESOLVED_GLOBAL_VS_PAIRWISE'},
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
