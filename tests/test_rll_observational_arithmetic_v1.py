"""Observational arithmetic falsifiers on pinned real inputs, not synthetic fits.

The historical metrics are a 33-Hz-row / source-unreordered-covariance
artifact. Their reproduction is evidence of OLD arithmetic only, not evidence
for the scientific correctness of the old likelihood or physical model.
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd
import pytest

from data.pipelines.structure_d import joint_real_likelihood as joint
from data.pipelines.structure_d.likelihood import chi2_with_covariance

GOLDEN_HZ28 = {
    joint.MODEL_LCDM: 17.221810087685437,
    joint.MODEL_WCDM: 17.319878281600825,
    joint.MODEL_CPL: 18.769708304918407,
    joint.MODEL_RLL: 17.22381463433642,
}
GOLDEN_ALIGNED_BAO = {
    joint.MODEL_LCDM: 19.588271120383823,
    joint.MODEL_WCDM: 16.157667914980838,
    joint.MODEL_CPL: 17.40556415320231,
    joint.MODEL_RLL: 19.617237739051095,
}


def _historical_rows():
    data = json.loads(
        (joint.RESULTS / "joint_real_likelihood.json").read_text(encoding="utf-8")
    )
    assert data["claim_allowed"] is False
    return {row["model"]: row for row in data["rows"]}


def _historical_evaluator(row):
    names = joint.MODEL_PARAM_NAMES[row["model"]]
    theta = np.array([row[name] for name in names], dtype=float)
    e2_fn, params, h0, ob_h2, sigma8, _extra = joint._model_runtime(
        row["model"], theta
    )
    return e2_fn, params, h0, ob_h2, sigma8


def _hz_chi2(frame, row):
    e2_fn, params, *_ = _historical_evaluator(row)
    predicted = joint.hz_from_e2(frame["z"].to_numpy(dtype=float), e2_fn, params)
    d = (frame["H_obs"].to_numpy(dtype=float) - predicted) / frame["sigma_H"].to_numpy(dtype=float)
    return float(d @ d)


def test_real_cc_selection_custody_and_duplicate_policy():
    raw = pd.read_csv(joint.BASE_DIR / "data/real/Hz_data_real.csv")
    canonical = pd.read_csv(joint.HZ_PATH)
    selected = raw[
        raw["source"].str.startswith("CC_")
        & ~raw["source"].str.contains("BAO", case=False)
    ].reset_index(drop=True)
    assert len(raw) == 33
    assert len(canonical) == len(selected) == 28
    assert sum(raw["source"].str.contains("BAO", case=False)) == 5
    pd.testing.assert_frame_equal(canonical.reset_index(drop=True), selected)
    growth = pd.read_csv(joint.FSIGMA8_PATH)
    assert len(growth) == 16
    # z=0.600 is two different surveys, never de-duplicate on z alone.
    assert len(growth[growth["z"] == 0.600]) == 2


@pytest.mark.parametrize("model", tuple(GOLDEN_HZ28))
def test_archive_and_pure_cc_chi2_separated_at_fixed_old_parameters(model):
    historical = _historical_rows()[model]
    full = pd.read_csv(joint.BASE_DIR / "data/real/Hz_data_real.csv")
    pure = pd.read_csv(joint.HZ_PATH)
    archived_reproduction = _hz_chi2(full, historical)
    selected_reproduction = _hz_chi2(pure, historical)
    assert archived_reproduction == pytest.approx(historical["chi2_Hz"], abs=1e-8)
    assert selected_reproduction == pytest.approx(GOLDEN_HZ28[model], abs=1e-6)
    assert archived_reproduction - selected_reproduction > 1.0


@pytest.mark.parametrize("model", tuple(GOLDEN_ALIGNED_BAO))
def test_real_bao_residual_covariance_reorders_and_changes_observation_chi2(model):
    row = _historical_rows()[model]
    e2_fn, params, _, ob_h2, _ = _historical_evaluator(row)
    points = pd.read_csv(joint.DESI_POINTS_PATH)
    raw_cov = pd.read_csv(joint.DESI_FULL_COV_PATH, index_col=0).to_numpy(dtype=float)
    aligned, evidence = joint._load_desi_covariance(
        points, pd.read_csv(joint.DESI_COV_SUMMARY_PATH)
    )
    assert evidence["source_order_to_observation_order"] == list(range(11)) + [12, 11]
    cache = {}
    predicted = np.array(
        [joint.bao_prediction(data, e2_fn, params, ob_h2, cache=cache)
         for _, data in points.iterrows()],
        dtype=float,
    )
    observed = points["value"].to_numpy(dtype=float)
    old = chi2_with_covariance(observed, predicted, raw_cov)
    corrected = chi2_with_covariance(observed, predicted, aligned)
    # Reproducing the archived wrong order is useful as a falsifier.
    assert old == pytest.approx(row["chi2_DESI_DR2_BAO"], abs=5e-4)
    assert corrected == pytest.approx(GOLDEN_ALIGNED_BAO[model], abs=5e-4)
    assert corrected != pytest.approx(old, abs=1e-2)


@pytest.mark.parametrize("sigma", [-2.0, 0.0, float("nan")])
def test_diagonal_observation_chi2_fails_closed_on_invalid_uncertainty(sigma):
    with pytest.raises(ValueError, match="OBSERVATION_SIGMA"):
        joint._chi2_diag(
            np.array([10.0, 12.0]),
            np.array([11.0, 11.0]),
            np.array([1.0, sigma]),
        )


def test_diagonal_observation_chi2_does_not_silently_broadcast_predictions():
    with pytest.raises(ValueError, match="OBSERVATION_SHAPE"):
        joint._chi2_diag(
            np.array([10.0, 12.0]),
            np.array([11.0]),
            np.array([1.0, 1.0]),
        )


def test_diagonal_observation_chi2_rejects_nonfinite_observation():
    with pytest.raises(ValueError, match="OBSERVATION_NONFINITE"):
        joint._chi2_diag(
            np.array([10.0, float("nan")]),
            np.array([11.0, 11.0]),
            np.array([1.0, 1.0]),
        )
