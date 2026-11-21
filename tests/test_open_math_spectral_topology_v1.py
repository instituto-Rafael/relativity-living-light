"""Deterministic/negative controls for bounded arithmetic and finite F2 homology."""
import json
import hashlib
from fractions import Fraction
from pathlib import Path

import pytest
from tools.math import open_math_spectral_topology_v1 as m


def test_base_counts_and_repeatability():
    a = m.conditional_randomization(limit=10000, draws=15, seed=42)
    b = m.conditional_randomization(limit=10000, draws=15, seed=42)
    assert a == b
    assert a['candidate_count'] == 2108
    assert a['primes_among_candidates'] == 1224
    assert a['composites_among_candidates'] == 884
    assert a['coarse_classes'] == 24
    assert a['fine_classes'] == 120
    assert a['claim_allowed'] is False
    assert 1/16 <= a['empirical_tail_fraction'] <= 1


def test_coarse_marginals_and_fine_expectations():
    groups, prime, cand, obs = m.conditional_profile(10000)
    ex = m.conditional_expectations(groups, prime, cand)
    assert sum(prime.values()) == sum(obs.values()) == 1224
    assert abs(sum(ex.values()) - 1224) < 1e-9
    for coarse in groups:
        fine = [r for r in cand if r % 70 == coarse]
        assert sum(cand[r] for r in fine) == len(groups[coarse])
        assert sum(obs.get(r, 0) for r in fine) == prime[coarse]
        assert abs(sum(ex[r] for r in fine)-prime[coarse]) < 1e-9


def test_fourier_zero_residual_negative_control():
    expect = {r: 1.0 for r in m.admissible_residues(350)}
    obs = {r: 1 for r in expect}
    assert m.fourier_power(obs, expect)['max_power'] == 0
    assert m.fourier_power({}, {r: 0.0 for r in expect})['max_power'] == 0


def test_invalid_parameters_fail_closed():
    for kws in [dict(limit=999, draws=15), dict(limit=1000, draws=8),
                dict(limit=20001, draws=15), dict(limit=1000, draws=512),
                dict(limit=1000, draws=15, seed=-1)]:
        with pytest.raises(ValueError):
            m.conditional_randomization(**kws)
    with pytest.raises(ValueError):
        m.periodic_torus(2)
    with pytest.raises(ValueError):
        m.homology_f2([(0, 0, 1)])
    with pytest.raises(ValueError):
        m.homology_f2([(0, 1, 2), (2, 1, 0)])


def test_exact_homology_and_negative_face_control():
    for n in (3, 4, 5):
        result = m.topology_experiment(n)
        sphere, torus = result['sphere'], result['torus']
        punctured = result['punctured_torus_negative_control']
        assert [sphere['vertices'], sphere['edges'], sphere['faces']] == [4, 6, 4]
        assert [torus['vertices'], torus['edges'], torus['faces']] == [n*n, 3*n*n, 2*n*n]
        assert sphere['betti_f2'] == [1, 0, 1]
        assert torus['betti_f2'] == [1, 2, 1]
        assert punctured['betti_f2'] == [1, 2, 0]
        assert [sphere['euler_characteristic'], torus['euler_characteristic'],
                punctured['euler_characteristic']] == [2, 0, -1]
        assert all(item['boundary_squared_zero'] for item in (sphere, torus, punctured))
        assert result['claim_allowed'] is False


def test_boundary_rank_and_chain_consistency():
    assert m.gf2_rank([]) == 0
    assert m.gf2_rank([0, 1, 2, 3]) == 2
    # Exact topological cycle: triangle has H_1=1 without a filling face;
    # here the filled 2-simplex has b1=0.
    filled = m.homology_f2([(0, 1, 2)])
    assert filled['betti_f2'] == [1, 0, 0]
    assert filled['euler_characteristic'] == 1


def test_immutable_receipt_and_byte_digest(tmp_path):
    report = m.compute(limit=1000, draws=9, seed=123)
    dest = tmp_path / 'open_math'
    digest = m.write_report(dest, report)
    raw = (dest / 'report.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == digest
    assert json.loads(raw) == report
    receipt = (dest / 'receipt.md').read_text(encoding='utf-8')
    assert digest in receipt
    assert 'claim_allowed: `false`' in receipt
    with pytest.raises(FileExistsError):
        m.write_report(dest, report)
    assert hashlib.sha256((dest / 'report.json').read_bytes()).hexdigest() == digest
