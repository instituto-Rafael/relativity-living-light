from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_rll_minimal_model_benchmark.py"
CONTRACT = ROOT / "data" / "contracts" / "rll_minimal_one_parameter_benchmark.v1.json"

spec = importlib.util.spec_from_file_location("rll_min_benchmark", SCRIPT)
assert spec is not None and spec.loader is not None
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def _inputs():
    measurements = m.load_measurements(m.DEFAULT_MEASUREMENTS)
    covariance = m.load_covariance(m.DEFAULT_COVARIANCE)
    inv_cov = m.invert_matrix(covariance)
    return measurements, covariance, inv_cov


def test_contract_matches_executable_constants():
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    frozen = contract["rll_min"]["frozen"]
    gates = contract["promotion_gates"]
    assert frozen["z_t"] == m.ZT_FIXED
    assert frozen["w_t"] == m.WT_FIXED
    assert frozen["Omega_r"] == m.OMEGA_R
    assert gates["delta_chi2_primary_max"] == -8.0
    assert gates["delta_chi2_strong_max"] == -10.0
    assert gates["max_rll_only_extra_parameters"] == 1
    assert contract["claim_allowed"] is False
    assert contract["publication_ready"] is False


def test_current_desi_materialization_shape_and_symmetry():
    measurements, covariance, _ = _inputs()
    assert len(measurements) == 13
    assert len(covariance) == 13
    assert all(len(row) == 13 for row in covariance)
    for i in range(13):
        for j in range(13):
            assert abs(covariance[i][j] - covariance[j][i]) < 1e-12


def test_rll_min_nests_lcdm_at_zero_amplitude():
    measurements, _, _ = _inputs()
    om = 0.31
    lcdm = m.shape_vector(measurements, "LCDM", om, 0.0)
    rll0 = m.shape_vector(measurements, "RLL_MIN", om, 0.0)
    assert max(abs(a - b) for a, b in zip(lcdm, rll0)) < 1e-12


def test_one_parameter_target_is_not_promoted_on_current_data():
    measurements, covariance, inv_cov = _inputs()
    lcdm = m.fit_lcdm(measurements, inv_cov)
    rll = m.fit_rll_min(measurements, inv_cov)
    delta = rll.chi2 - lcdm.chi2

    # Frozen-data reproducibility fence. If this moves materially, inspect source,
    # covariance, model or optimizer before changing the expected range.
    assert 10.20 < lcdm.chi2 < 10.40
    assert 8.85 < rll.chi2 < 9.10
    assert -1.50 < delta < -1.10
    assert -0.10 < rll.omega_s0 < 0.10

    payload = m.build_payload(
        m.DEFAULT_MEASUREMENTS,
        m.DEFAULT_COVARIANCE,
        measurements,
        covariance,
        lcdm,
        rll,
    )
    comparison = payload["comparison"]
    gates = payload["successor_gates"]

    assert comparison["target_minus8_pass"] is False
    assert comparison["target_minus10_pass"] is False
    assert comparison["aic_improves"] is False
    assert comparison["bic_improves"] is False
    assert gates["desi_lya_full_shape"]["status"] == "NOT_RUN"
    assert gates["growth_fsigma8"]["status"] == "TOKEN_VAZIO"
    assert gates["bayesian_evidence"]["status"] == "NOT_RUN"
    assert payload["claim_allowed"] is False
    assert payload["publication_ready"] is False


def test_lya_bao_is_not_mislabeled_as_full_shape():
    measurements, covariance, inv_cov = _inputs()
    lcdm = m.fit_lcdm(measurements, inv_cov)
    rll = m.fit_rll_min(measurements, inv_cov)
    payload = m.build_payload(
        m.DEFAULT_MEASUREMENTS,
        m.DEFAULT_COVARIANCE,
        measurements,
        covariance,
        lcdm,
        rll,
    )
    diagnostic = payload["lya_bao_only_diagnostic"]
    assert diagnostic["indices"] == [11, 12]
    assert "NOT DESI 2026 LyA full-shape" in diagnostic["epistemic_boundary"]
