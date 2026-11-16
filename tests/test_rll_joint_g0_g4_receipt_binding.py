"""Negative source, archive, normalization and interpretability gates.

These tests do not re-fit observational data or mutate archived results.
"""
from __future__ import annotations
import json
from pathlib import Path
from scripts import rll_joint_g0_g2_adapter as a

def _archive(tmp_path, mutate=None):
    payload=json.loads(a.ARCHIVE.read_text(encoding='utf-8'))
    if mutate is not None:
        mutate(payload)
    path=tmp_path/'archive.json'
    path.write_text(json.dumps(payload),encoding='utf-8')
    return path

def test_alternative_source_cannot_be_claimed_as_imported_runtime(tmp_path):
    # Both texts pass the old AST presence guard, but the alternate file has
    # not supplied any of the functions actually imported by the adapter.
    source=tmp_path/'different_model.py'
    source.write_bytes(a.SOURCE.read_bytes()+b'\n# unexecuted alternative source\n')
    r=a.analyze(source,a.ARCHIVE)
    assert r['state']=='TOKEN_VAZIO_SOURCE_RUNTIME_BINDING'
    assert r['claim_allowed'] is False
    assert r['source_identity']=='PATH_MISMATCH_OR_UNKNOWN'

def test_source_unavailable_and_invalid_are_typed(tmp_path):
    r=a.analyze(tmp_path/'missing_source.py',a.ARCHIVE)
    assert r['state']=='TOKEN_VAZIO_SOURCE_UNAVAILABLE'
    broken=tmp_path/'invalid.py'
    broken.write_text('def missing(:\n',encoding='utf-8')
    assert a.analyze(broken,a.ARCHIVE)['state']=='TOKEN_VAZIO_SOURCE_DRIFT'

def test_missing_and_malformed_archives_are_typed(tmp_path):
    assert a.analyze(a.SOURCE,tmp_path/'missing.json')['state']=='TOKEN_VAZIO_ARCHIVE_UNAVAILABLE'
    invalid=tmp_path/'invalid.json'
    invalid.write_text('{"rows": [NaN]}',encoding='utf-8')
    assert a.analyze(a.SOURCE,invalid)['state']=='TOKEN_VAZIO_ARCHIVE_INVALID'

def test_archival_nonfinite_wrong_schema_zero_h0_duplicate_models(tmp_path):
    mutators=(
        lambda p: p.update(schema='invented'),
        lambda p: p['rows'][0].update(H0=0),
        lambda p: p['rows'][0].update(Om=float('nan')),
        lambda p: p['rows'][0].update(BIC='Infinity'),
        lambda p: p['rows'].append(p['rows'][0].copy()),
        lambda p: p.update(rows=[]),
    )
    for index,mutate in enumerate(mutators):
        folder=tmp_path/str(index)
        folder.mkdir()
        r=a.analyze(a.SOURCE,_archive(folder,mutate))
        assert r['state']=='TOKEN_VAZIO_ARCHIVE_INVALID', (index,r)
        assert not r['claim_allowed']

def test_nonpositive_e2_cannot_be_masked_by_hz_sqrt_floor(tmp_path):
    def mutate(p):
        p['rows'][0].update(Om=-10.,OL=-10.)
    r=a.analyze(a.SOURCE,_archive(tmp_path,mutate))
    assert r['state']=='TOKEN_VAZIO_MODEL_E2_NONPOSITIVE'
    assert r['claim_allowed'] is False

def test_archived_bic_scopes_remain_distinct_and_unattested():
    r=a.analyze()
    assert r['state']=='NUMERIC_SOURCE_DIAGNOSTIC_NOT_PHYSICAL_VALIDATION'
    assert r['g4']['BIC_winner_archived']=='CPL_w0waCDM_joint_real'
    assert r['g4']['BIC_winner_RLL_vs_LCDM']=='LCDM_joint_real'
    assert r['g4']['historical_label_scope'].startswith('TOKEN_VAZIO')
    assert r['source_archive_execution_identity'].startswith('TOKEN_VAZIO')
    assert r['runtime_source_path_identity']=='MATCH_SCOPED_NOT_BYTECODE_ATTESTATION'
    assert r['claim_allowed'] is False
