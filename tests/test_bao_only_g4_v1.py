"""Exact-source BAO-only multi-model null and fit regression.

Scope: 13 DESI DR2 BAO coordinates, not Pantheon+ full covariance.
"""
import math
import pytest
from scripts.run_bao_only_from_g4_v1 import run, model_e2

def test_bao_only_g4_nested_null_limits():
    z=[0,0.2,0.7,2.3]
    a=model_e2(z,'LCDM',[29.52,.30])
    b=model_e2(z,'wCDM',[29.52,.30,-1])
    c=model_e2(z,'RLL',[29.52,.30,0,1,.30])
    assert max(abs(x-y) for x,y in zip(a,b)) < 1e-12
    assert max(abs(x-y) for x,y in zip(a,c)) < 1e-12

def test_bao_only_g4_three_model_full_covariance_source():
    report=run(starts_extra=18)
    assert report['claim_allowed'] is False
    assert report['Pantheon_plus']=='TOKEN_VAZIO_FULL_COVARIANCE'
    assert report['n_observables']==13
    by={x['model']:x for x in report['models']}
    assert set(by)=={'LCDM','wCDM','RLL'}
    checks={'LCDM':10.902987388584126,
            'wCDM':7.467261231906272,
            'RLL':6.474229158053462}
    for model,chi in checks.items():
        v=by[model]
        assert math.isfinite(v['chi2'])
        assert abs(v['chi2']-chi)<1e-4
        assert math.isfinite(v['AICc'])
        assert v['claim_allowed'] is False
    # Antipadrão: menor chi2 não implica menor AICc.
    assert by['RLL']['chi2'] < by['LCDM']['chi2']
    assert by['RLL']['AICc'] > by['LCDM']['AICc']
