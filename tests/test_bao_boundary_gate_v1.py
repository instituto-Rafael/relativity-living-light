import copy, json
import numpy as np
import pytest
from pathlib import Path
from scipy.optimize import least_squares
from tools.bao_boundary_gate_v1 import boundary_report, gate_boundary_claim, format_chi2


def _one_dim(target):
    return least_squares(lambda v: np.array([v[0]-target]), x0=np.array([.3]),bounds=([.1],[.5]),xtol=1e-12,gtol=1e-12,ftol=1e-12)


def test_lower_bound_even_when_raw_gradient_nonzero():
    r=_one_dim(.08)
    d=boundary_report(r,([.1],[.5]),['Omega_m'],13)
    assert d['at_boundary']['Omega_m']
    assert d['corner_solution'] is True and d['strict_corner'] is False
    assert d['n_residual_dof_nominal']==12
    assert d['n_effective_dof'] is None
    assert d['min_grad_inf'] > 0.019
    assert d['kkt_violation_inf'] < 1e-7
    assert np.linalg.norm(r.jac,np.inf) > .9 # differs from gradient, catches wrong proxy
    assert d['optimizer_optimality'] < 1e-7
    assert format_chi2(6.47422916,d)=='6.4742*'


def test_interior_solution_and_render():
    r=_one_dim(.25)
    d=boundary_report(r,([.1],[.5]),['Omega_m'],13)
    assert not d['corner_solution'] and d['active_bound_count']==0
    assert format_chi2(7.80397373,d)=='7.8040'
    assert gate_boundary_claim(d)


def test_true_intersection_of_two_bounds():
    r=least_squares(lambda v: np.array([v[0]-.08,v[1]-.03]),x0=[.3,.25],bounds=([.1,.05],[.5,.5]),xtol=1e-12,gtol=1e-12,ftol=1e-12)
    d=boundary_report(r,([.1,.05],[.5,.5]),['Omega_m','w_t'],13)
    assert d['strict_corner'] and d['active_bound_count']==2
    assert all(d['at_boundary'].values())


def test_false_green_is_rejected():
    d=boundary_report(_one_dim(.08),([.1],[.5]),['Omega_m'],13)
    bad=copy.deepcopy(d);bad['claim_allowed']=True
    with pytest.raises(ValueError):gate_boundary_claim(bad)
    bad=copy.deepcopy(d);bad['claim_blocked_reason']='good'
    with pytest.raises(ValueError):gate_boundary_claim(bad)
    bad=copy.deepcopy(d);bad['corner_solution']=False
    with pytest.raises(ValueError):gate_boundary_claim(bad)


def test_invalid_input_fails_closed():
    r=_one_dim(.25)
    for bounds in (([.5],[.1]),([float('nan')],[.5])):
        with pytest.raises(ValueError):boundary_report(r,bounds,['Omega_m'],13)
    with pytest.raises(ValueError):boundary_report(r,([.1],[.5]),['Omega_m'],0)


def test_schema_is_valid_and_accepts_real_diagnostic():
    import jsonschema
    schema=json.loads((Path(__file__).resolve().parents[1]/'schemas/rll_bao_boundary_diagnostics_v1.schema.json').read_text())
    jsonschema.Draft202012Validator.check_schema(schema)
    obj=boundary_report(_one_dim(.08),([.1],[.5]),['Omega_m'],13)
    jsonschema.validate(obj,schema)
    bad=copy.deepcopy(obj);bad.pop('corner_solution')
    with pytest.raises(jsonschema.ValidationError):jsonschema.validate(bad,schema)
