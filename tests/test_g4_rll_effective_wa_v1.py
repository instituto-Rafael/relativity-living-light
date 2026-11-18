"""Direct G4 source E² vs the independent effective-dark-sector tangent formula."""
import math
import numpy as np
import pytest
from tools import run_g4_background_tournament as g4
from tools.rll_effective_wa_preflight_v1 import effective_cpl_tangent


def g4_effective_dark_density(z,om,s,zt,wt):
    z=np.asarray(z,dtype=float)
    x=1+z
    p=[70.,om,.02236,s,zt,wt]
    e2=g4.e2('RLL',z,p)
    return e2-om*x**3-g4.OMEGA_R0*x**4


def numerical_weff(z,om,s,zt,wt,h=1e-4):
    r0=g4_effective_dark_density(z,om,s,zt,wt)
    dr=(g4_effective_dark_density(z+h,om,s,zt,wt)-
        g4_effective_dark_density(z-h,om,s,zt,wt))/(2*h)
    return -1+(1+z)*dr/(3*r0)


@pytest.mark.parametrize('om,s,zt,wt',[
    (.315,.059,1.164,.405),
    (.1340362727,.1343514672,.398874769,.05),
    (.3,.01,.5,.25),
    (.3,0.,.8,.5),
])
def test_g4_local_tangent_matches_independent_numerical_derivatives(om,s,zt,wt):
    d=effective_cpl_tangent(om,s,zt,wt)
    numerical_w0=numerical_weff(0.,om,s,zt,wt)
    h=1e-4
    numerical_wa=(numerical_weff(h,om,s,zt,wt,h)-
                  numerical_weff(-h,om,s,zt,wt,h))/(2*h)
    assert abs(d['w0_eff']-numerical_w0)<1e-7
    assert abs(d['wa_eff_local_tangent']-numerical_wa)<2e-5
    assert d['wa_local_nonnegative_under_assumptions']
    assert d['claim_allowed'] is False
    assert d['perturbation_closure']=='TOKEN_VAZIO_NOT_DERIVED'


def test_nontrivial_example_wa_cons_positive():
    d=effective_cpl_tangent(.315,.059,1.164,.405)
    assert math.isclose(d['wa_eff_local_tangent'],.03527158747940185,rel_tol=2e-9)
    assert d['wa_eff_local_tangent']>0


def test_bao_corrected_fit_is_near_lcdm_but_not_negative_local_wa():
    d=effective_cpl_tangent(.1340362727,.1343514672,.398874769,.05)
    assert math.isclose(d['wa_eff_local_tangent'],.0022876253830907915,rel_tol=1e-7)
    assert d['wa_eff_local_tangent']>=0
    assert d['observational_wa_posterior'].startswith('TOKEN_VAZIO')


@pytest.mark.parametrize('v',[
    (.3,-.01,1,.5),(.3,.8,1,.5),(.3,.1,1,0),(.3,.1,1,-1),
    (.3,.1,0,.5),(.3,float('nan'),1,.5)])
def test_invalid_parameter_domain_fails_closed(v):
    with pytest.raises(ValueError):
        effective_cpl_tangent(*v)


def test_null_limit_exact_lcdm():
    d=effective_cpl_tangent(.31,0,1,.5)
    assert d['wa_eff_local_tangent']==0
    assert d['w0_eff']==-1
    p=[70.,.31,.02236,0.,1,.5]
    z=np.array([0.,.3,.7,2.33])
    np.testing.assert_allclose(g4.e2('RLL',z,p),
        g4.e2('LCDM',z,p[:3]),rtol=0,atol=1e-13)
