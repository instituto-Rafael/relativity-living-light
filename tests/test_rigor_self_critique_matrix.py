from __future__ import annotations
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'PapersPub' / '08_multiscale_validation_methods'
METHOD_PATH = BASE / 'rigor_self_critique_method_20260906.v1.json'
PROGRAM_PATH = BASE / 'math_research_program_48_20260905.v1.json'
ENGINE_PATH = BASE / 'scripts' / 'rigor_self_critique_matrix.py'


def load_engine():
    spec = importlib.util.spec_from_file_location('rigor_engine', ENGINE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_rigor12_fail_closed_baseline():
    method = json.loads(METHOD_PATH.read_text(encoding='utf-8'))
    program = json.loads(PROGRAM_PATH.read_text(encoding='utf-8'))
    engine = load_engine()

    assert [d['id'] for d in method['dimensions']] == [f'RG{i:02d}' for i in range(1, 13)]
    assert len(method['autocritique']['nibiguiri_lenses']) == 12
    assert method['autocritique']['base_matrix_cells'] == 576
    assert method['autocritique']['adversarial_tensor_cells'] == 6912

    assessment = engine.blank_assessment(program, method)
    assert len(assessment['research_units']) == 48
    assert engine.validate(program, method, assessment) == []

    for rec in assessment['research_units'].values():
        assert set(rec['scores_by_dimension']) == {f'RG{i:02d}' for i in range(1, 13)}
        assert all(v == engine.TV for v in rec['scores_by_dimension'].values())
        result = engine.compute_one(rec, method)
        assert result['coverage'] == 0
        assert result['rigor_score'] is None
        assert result['rigor_class'] == 'R0_UNASSESSED'
        assert result['hard_gate_status'] == 'BLOCKED'
        assert result['promotion_decision'] == 'BLOCKED'


def test_token_vazio_is_not_numeric_zero_and_is_excluded_from_score():
    method = json.loads(METHOD_PATH.read_text(encoding='utf-8'))
    program = json.loads(PROGRAM_PATH.read_text(encoding='utf-8'))
    engine = load_engine()
    assessment = engine.blank_assessment(program, method)
    rec = assessment['research_units']['H01']

    assert engine.TV != 0
    assert not engine.numeric(engine.TV)
    rec['scores_by_dimension']['RG01'] = 4
    result = engine.compute_one(rec, method)
    assert result['coverage'] > 0
    assert result['coverage'] < 1
    assert result['rigor_score'] == 100.0
    # A high score over the known slice cannot bypass unknown hard gates.
    assert result['promotion_decision'] == 'BLOCKED'


def test_adversarial_tensor_cardinality():
    method = json.loads(METHOD_PATH.read_text(encoding='utf-8'))
    program = json.loads(PROGRAM_PATH.read_text(encoding='utf-8'))
    engine = load_engine()
    assessment = engine.blank_assessment(program, method)

    total = sum(len(engine.adversarial_prompts(uid, method)) for uid in assessment['research_units'])
    assert total == 48 * 12 * 12 == 6912
