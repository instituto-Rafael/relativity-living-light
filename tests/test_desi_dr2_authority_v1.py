"""Adversarial source-bound tests; positive cases use real RLL data in checkout."""
from __future__ import annotations

import json

import numpy as np
import pandas as pd
import pytest

from rll.desi_dr2_authority_v1 import (
    SOURCE_SHA256,
    UPSTREAM,
    align_verified_desi_covariance,
    observation_vector_n,
)


def test_real_desi_mean_covariance_order_and_no_mutation():
    from data.pipelines.structure_d import joint_real_likelihood as joint

    points = pd.read_csv(joint.DESI_POINTS_PATH)
    raw_cov = pd.read_csv(joint.DESI_FULL_COV_PATH, index_col=0).to_numpy(dtype=float)
    before = raw_cov.copy()
    aligned, receipt = align_verified_desi_covariance(points, raw_cov, joint.DESI_FULL_COV_PATH)
    assert receipt["source_covariance_sha256"] == SOURCE_SHA256
    assert receipt["source_order_to_observation_order"] == list(range(11)) + [12, 11]
    assert receipt["lyalpha_reordered"] is True
    assert receipt["claim_allowed"] is False
    assert np.array_equal(raw_cov, before)
    ix = list(range(11)) + [12, 11]
    assert np.allclose(aligned, raw_cov[np.ix_(ix, ix)])
    assert np.all(np.linalg.eigvalsh(aligned) > 0.0)
    sigmas = points["sigma"].to_numpy(dtype=float)
    assert np.max(np.abs(np.diag(aligned) / sigmas**2 - 1.0)) < 0.15


def test_active_real_data_count_respects_cmb_covariance_dimension():
    from data.pipelines.structure_d import joint_real_likelihood as joint

    inputs = joint.load_joint_inputs()
    assert len(inputs["hz"]) == 28
    assert len(inputs["desi"]) == 13
    assert len(inputs["fs8"]) == 16
    assert observation_vector_n(inputs) == 60
    assert inputs["desi_covariance_info"]["source_order_to_observation_order"] == list(range(11)) + [12, 11]
    with open("results/structure_d/joint_real_likelihood.json", encoding="utf-8") as f:
        legacy = json.load(f)
    assert all(row["N"] == 64 for row in legacy["rows"])
    assert legacy["claim_allowed"] is False


def test_reject_wrong_order_or_duplicate_observable(monkeypatch, tmp_path):
    from rll import desi_dr2_authority_v1 as guard
    import hashlib

    source = tmp_path / "pinned.csv"
    source.write_bytes(b"check-sha")
    monkeypatch.setattr(guard, "SOURCE_SHA256", hashlib.sha256(b"check-sha").hexdigest())
    identities = pd.DataFrame([
        {"tracer": t, "observable": obs, "z_eff": z, "value": value, "sigma": 1.0}
        for t, obs, z, value in UPSTREAM
    ])
    a = np.eye(13)
    result, info = align_verified_desi_covariance(identities, a, source)
    assert info["source_order_to_observation_order"] == list(range(13))
    assert result.shape == (13, 13)
    duplicate = identities.copy()
    duplicate.loc[12, ["tracer", "observable", "z_eff"]] = duplicate.loc[11, ["tracer", "observable", "z_eff"]]
    with pytest.raises(ValueError, match="IDENTITY_OR_DUPLICATE"):
        align_verified_desi_covariance(duplicate, a, source)
    invalid = identities.copy()
    invalid.loc[0, "value"] += 1.0
    with pytest.raises(ValueError, match="SOURCE_VALUE_MISMATCH"):
        align_verified_desi_covariance(invalid, a, source)
    source.write_bytes(b"tampered")
    with pytest.raises(ValueError, match="SOURCE_SHA256"):
        align_verified_desi_covariance(identities, a, source)


def test_malformed_cmb_cannot_silently_fallback():
    inputs = {"hz": list(range(28)), "desi": list(range(13)), "fs8": list(range(16)),
              "cmb": {"parameter_order": ["R", "la", "ob_h2"], "covariance": np.eye(3).tolist()}}
    assert observation_vector_n(inputs) == 60
    inputs["cmb"]["parameter_order"] = ["la", "R", "ob_h2"]
    with pytest.raises(ValueError, match="PARAMETER_ORDER"):
        observation_vector_n(inputs)
    inputs["cmb"] = {"parameter_order": ["R", "la", "ob_h2"], "covariance": [[1, 0], [0, 1]]}
    with pytest.raises(ValueError, match="COVARIANCE_SHAPE"):
        observation_vector_n(inputs)
    inputs["cmb"] = {}
    assert observation_vector_n(inputs) == 59


def test_background_normalization_is_still_a_blocker_not_an_autofix():
    from data.pipelines.structure_d import joint_real_likelihood as joint

    r = json.loads(joint.RESULTS.joinpath("joint_real_likelihood.json").read_text(encoding="utf-8"))
    lcdm = next(row for row in r["rows"] if row["model"] == joint.MODEL_LCDM)
    vector = (lcdm["H0"], lcdm["Om"], lcdm["OL"])
    e2_zero = float(joint.e2_lcdm(0.0, *vector))
    assert abs(e2_zero - 1.0) > 0.1
    assert r["claim_allowed"] is False


def test_rll_os0_zero_makes_transition_unidentifiable():
    from data.pipelines.structure_d import joint_real_likelihood as joint

    z = np.array([0.0, 0.1, 1.0, 2.0], dtype=float)
    p = (67.7, 0.31, 0.69, 0.0)
    x = joint.e2_rll(z, *p, 0.5, 0.2)
    y = joint.e2_rll(z, *p, 8.0, 1.5)
    assert np.array_equal(x, y)


@pytest.mark.parametrize("n", [59, 60, 64, 65])
def test_historical_aicc_count_sensitivity_fixed_chi2_only(n):
    """Do not confuse an N arithmetic perturbation with a new likelihood fit."""
    from data.pipelines.structure_d import joint_real_likelihood as joint

    with joint.RESULTS.joinpath("joint_real_likelihood.json").open(encoding="utf-8") as f:
        artifact = json.load(f)
    rows = artifact["rows"]
    def aicc(row):
        k, chi2 = row["k"], row["chi2"]
        return chi2 + 2 * k + 2 * k * (k + 1) / (n - k - 1)
    best = min(rows, key=aicc)
    assert best["model"] == joint.MODEL_CPL
    rll = next(row for row in rows if row["model"] == joint.MODEL_RLL)
    assert aicc(rll) - aicc(best) > 33.0
    assert artifact["claim_allowed"] is False


def test_interpretation_label_is_pairwise_not_global_winner():
    """The historic label is RLL-vs-LCDM; the global winner must be separate."""
    from data.pipelines.structure_d import joint_real_likelihood as joint

    with joint.RESULTS.joinpath("joint_real_likelihood.json").open(encoding="utf-8") as f:
        artifact = json.load(f)
    rows = artifact["rows"]
    assert artifact["interpretation_label"] == "lcdm_preferred"
    assert min(rows, key=lambda row: row["AICc"])["model"] == joint.MODEL_CPL
    assert min(rows, key=lambda row: row["BIC"])["model"] == joint.MODEL_CPL
    assert artifact["model_deltas_vs_lcdm"][joint.MODEL_RLL]["delta_aicc_rll_minus_lcdm"] > 0.0
    assert artifact["claim_allowed"] is False
