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
    # These anchors are independently recomputed with the *source-bound*
    # native Cobaya covariance permutation, including Lya DH↔DM.
    checks={'LCDM':10.291044479494511,
            'wCDM':9.027488132763317,
            'RLL':7.803973727991534}
    for model,chi in checks.items():
        v=by[model]
        assert math.isfinite(v['chi2'])
        assert abs(v['chi2']-chi)<1e-4
        assert math.isfinite(v['AICc'])
        assert v['claim_allowed'] is False
    # Antipadrão: menor chi2 não implica menor AICc.
    assert by['RLL']['chi2'] < by['LCDM']['chi2']
    assert by['RLL']['AICc'] > by['LCDM']['AICc']
    assert by['RLL']['BIC'] > by['LCDM']['BIC']
    assert all(row['optimizer_success'] is True for row in by.values())
    assert abs(by['RLL']['parameters']['w_t']-0.05)<1e-9
    assert by['RLL']['parameters']['Omega_s0']>0.0



def test_bao_native_lyman_alpha_axis_permutation_is_not_silent():
    """The source native Cobaya order is Lya DH,DM; Table-IV is DM,DH.

    The historical fixture assumed identity index mapping. It is NOT equivalent
    to the verified G4 loader. This test catches silent covariance swap drift.
    """
    import numpy as np
    from tools import run_g4_background_tournament as g4
    block=g4.load_desi()
    native=np.loadtxt(g4.DESI_COV_PATH,delimiter=",",skiprows=1,
                      usecols=range(1,14),dtype=float)
    permutation=list(range(11))+[12,11]
    expected=native[np.ix_(permutation,permutation)]
    np.testing.assert_allclose(block.covariance,expected,rtol=0.0,atol=1e-12)
    assert not np.allclose(native,block.covariance,rtol=0.0,atol=1e-12)
    assert block.observable[-2:]==('DM_over_rd','DH_over_rd')
    assert np.linalg.eigvalsh(block.covariance).min()>0.0
