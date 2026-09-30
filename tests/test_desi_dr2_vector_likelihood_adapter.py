import csv
from pathlib import Path
from tools.desi_dr2_vector_likelihood_adapter import evaluate, VectorLikelihoodError

def _write_csv(path,fields,rows):
    with Path(path).open('w',encoding='utf-8',newline='') as h:
        w=csv.DictWriter(h,fieldnames=fields); w.writeheader(); w.writerows(rows)

def test_vector_likelihood_full_vs_diagonal(tmp_path):
    order=tmp_path/'order.csv'; cov=tmp_path/'cov.csv'; pred=tmp_path/'pred.csv'
    _write_csv(order,['index','value'],[{'index':0,'value':1.0},{'index':1,'value':2.0}])
    _write_csv(cov,['row','obs_00','obs_01'],[{'row':'obs_00','obs_00':1.0,'obs_01':0.5},{'row':'obs_01','obs_00':0.5,'obs_01':1.0}])
    _write_csv(pred,['index','prediction'],[{'index':0,'prediction':0.0},{'index':1,'prediction':1.0}])
    out=evaluate(order,cov,pred)
    assert out['claim_allowed'] is False
    assert out['scientific_fit_promoted'] is False
    assert abs(out['chi2_diagonal']-2.0)<1e-12
    assert abs(out['chi2_full']-(4.0/3.0))<1e-12
    assert out['delta_chi2_full_minus_diagonal']<0

def test_predictions_must_cover_emitted_order(tmp_path):
    order=tmp_path/'order.csv'; cov=tmp_path/'cov.csv'; pred=tmp_path/'pred.csv'
    _write_csv(order,['index','value'],[{'index':0,'value':1.0},{'index':1,'value':2.0}])
    _write_csv(cov,['row','obs_00','obs_01'],[{'row':'obs_00','obs_00':1.0,'obs_01':0.0},{'row':'obs_01','obs_00':0.0,'obs_01':1.0}])
    _write_csv(pred,['index','prediction'],[{'index':0,'prediction':0.0}])
    try: evaluate(order,cov,pred)
    except VectorLikelihoodError: return
    raise AssertionError('missing prediction index must fail closed')
