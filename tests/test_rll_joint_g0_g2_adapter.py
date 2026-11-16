"""Boundary tests; numerical discrepancies are preserved as evidence, not PASS claims."""
from scripts import rll_joint_g0_g2_adapter as a

def test_real_archived_g0_and_g1_numeric_sensitivity():
    report=a.analyze()
    assert report['claim_allowed'] is False
    assert report['state']=='NUMERIC_SOURCE_DIAGNOSTIC_NOT_PHYSICAL_VALIDATION'
    models={r['name']:r for r in report['g0']}
    assert models['LCDM_joint_real']['gap']>0.01
    assert models['RLL_joint_real']['gap']>0.01
    assert report['g1']['absolute_delta_lA']>0.1
    assert report['g1']['Boltzmann_backend']=='TOKEN_VAZIO_NOT_RUN'

def test_growth_null_boundary_and_bic_archive():
    report=a.analyze()
    one=next(x for x in report['g2']['rows'] if x['z']==1.0)
    assert one['absolute_gap']>0.05
    assert report['g3']['archived_RLL_Os0_zero'] is True
    assert report['g4']['BIC_winner_archived']=='CPL_w0waCDM_joint_real'
    assert report['g4']['historical_interpretation']=='lcdm_preferred'

def test_input_rejection_and_source_drift(tmp_path):
    historical=tmp_path/'archived.json'; historical.write_text('{"rows": []}',encoding='utf-8')
    source=tmp_path/'source.py';source.write_text('ORAD=0.00009\n',encoding='utf-8')
    r=a.analyze(source,historical)
    assert r['state']=='TOKEN_VAZIO_SOURCE_DRIFT'
    assert r['claim_allowed'] is False
