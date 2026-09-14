from __future__ import annotations

import json

import numpy as np
import pandas as pd
import pytest

from data.pipelines.structure_d import joint_real_likelihood as joint


def test_desi_covariance_materializes_committed_dm_dh_blocks() -> None:
    points = pd.read_csv(joint.DESI_POINTS_PATH)
    summary = pd.read_csv(joint.DESI_COV_SUMMARY_PATH)

    cov = joint.build_desi_covariance(points, summary)

    assert cov.shape == (13, 13)
    assert np.allclose(np.diag(cov), points["sigma"].astype(float).to_numpy() ** 2)
    lrg1 = points.index[points["covariance_block"] == "DESI_DR2_LRG1_DM_DH"].tolist()
    assert len(lrg1) == 2
    assert cov[lrg1[0], lrg1[1]] == cov[lrg1[1], lrg1[0]]
    assert cov[lrg1[0], lrg1[1]] < 0.0


def test_joint_evaluation_uses_all_four_real_axes() -> None:
    inputs = joint.load_joint_inputs()
    vector = np.array([67.7, 0.31, 0.69, 0.0224, 0.8], dtype=float)

    components = joint.evaluate_components(joint.MODEL_LCDM, vector, inputs)

    assert set(components) == {"Hz", "DESI_DR2_BAO", "fsigma8", "CMB_shift", "total"}
    assert components["total"] == components["Hz"] + components["DESI_DR2_BAO"] + components["fsigma8"] + components["CMB_shift"]
    assert np.isfinite(components["total"])


def test_joint_real_models_include_wcdm_and_cpl_on_same_inputs() -> None:
    inputs = joint.load_joint_inputs()
    wcdm_vector = np.array([67.7, 0.31, 0.69, -1.0, 0.0224, 0.8], dtype=float)
    cpl_vector = np.array([67.7, 0.31, 0.69, -1.0, 0.0, 0.0224, 0.8], dtype=float)

    wcdm_components = joint.evaluate_components(joint.MODEL_WCDM, wcdm_vector, inputs)
    cpl_components = joint.evaluate_components(joint.MODEL_CPL, cpl_vector, inputs)

    assert np.isfinite(wcdm_components["total"])
    assert np.isfinite(cpl_components["total"])
    assert joint.MODEL_PARAM_NAMES[joint.MODEL_WCDM] == ("H0", "Om", "OL", "w", "Ob_h2", "sigma8")
    assert joint.MODEL_PARAM_NAMES[joint.MODEL_CPL] == ("H0", "Om", "OL", "w0", "wa", "Ob_h2", "sigma8")


def test_joint_inputs_require_parameter_registry_and_covariance_readiness() -> None:
    inputs = joint.load_joint_inputs()

    assert inputs["parameter_registry"]["schema"].startswith("rll.parameter_origin_registry.")
    assert inputs["desi_covariance_info"]["ready"] is True
    assert inputs["desi_covariance_info"]["mode"] in {"official_full", "block_summary"}


def test_rd_drag_is_derived_from_parameter_changes() -> None:
    baseline = joint.rd_drag_mpc(67.7, 0.31, 0.02236)
    shifted = joint.rd_drag_mpc(73.0, 0.31, 0.02236)

    assert np.isfinite(baseline)
    assert np.isfinite(shifted)
    assert baseline != shifted


def test_cmb_shift_prediction_returns_R_lA_and_Ob_h2() -> None:
    params = (67.7, 0.31, 0.69)
    pred = joint.cmb_shift_prediction(joint.e2_lcdm, params, 0.0224, joint.Z_CMB_DEFAULT)

    assert pred.shape == (3,)
    assert pred[2] == 0.0224


def test_committed_cmb_shift_file_carries_full_covariance() -> None:
    cmb = json.loads(joint.CMB_SHIFT_PATH.read_text(encoding="utf-8"))

    assert cmb["parameter_order"] == ["R", "la", "ob_h2"]
    cov = np.asarray(cmb["covariance"], dtype=float)
    assert cov.shape == (3, 3)
    assert np.allclose(cov, cov.T)
    assert np.all(np.linalg.eigvalsh(cov) > 0.0)


def test_cmb_chi2_uses_full_covariance_when_available_and_matches_manual_computation() -> None:
    inputs = joint.load_joint_inputs()
    cmb = inputs["cmb"]
    params = (67.7, 0.31, 0.69)
    ob_h2 = 0.0224

    chi2 = joint._cmb_chi2(cmb, joint.e2_lcdm, params, ob_h2)

    pred = joint.cmb_shift_prediction(joint.e2_lcdm, params, ob_h2, float(cmb["z_CMB"]))
    obs = np.array([cmb["R_obs"], cmb["la_obs"], cmb["ob_h2_obs"]], dtype=float)
    cov = np.asarray(cmb["covariance"], dtype=float)
    residual = obs - pred
    expected = float(residual @ np.linalg.solve(cov, residual))

    assert chi2 == pytest.approx(expected)
    assert chi2 >= 0.0


def test_cmb_chi2_falls_back_to_diagonal_without_committed_covariance() -> None:
    cmb = {"z_CMB": 1089.92, "R_obs": 1.75, "la_obs": 301.0, "R_sig": 0.03, "la_sig": 0.35}
    params = (67.7, 0.31, 0.69)

    chi2 = joint._cmb_chi2(cmb, joint.e2_lcdm, params, 0.0224)

    assert np.isfinite(chi2)
    assert chi2 >= 0.0


def test_k_is_derived_from_registry() -> None:
    """Verify k_from_registry produces correct k for each model using the committed registry."""
    registry = joint.load_parameter_registry()

    for model, param_names in joint.MODEL_PARAM_NAMES.items():
        expected_k = len(param_names)
        derived_k = joint.k_from_registry(param_names, registry)
        assert derived_k == expected_k, (
            f"k_from_registry mismatch for {model}: "
            f"expected {expected_k}, got {derived_k}"
        )


def test_model_row_includes_registry_schema_and_commit_sha() -> None:
    """Verify _model_row embeds registry_schema and commit_sha when registry is provided."""
    inputs = joint.load_joint_inputs()
    registry = inputs["parameter_registry"]
    vector = np.array([67.7, 0.31, 0.69, 0.0224, 0.8], dtype=float)
    components = {"total": 10.0, "Hz": 2.0, "DESI_DR2_BAO": 3.0, "fsigma8": 2.5, "CMB_shift": 2.5}

    row = joint._model_row(joint.MODEL_LCDM, vector, components, 50, registry=registry, commit_sha="abc123")

    assert row["registry_schema"] == registry["schema"]
    assert row["commit_sha"] == "abc123"
    assert row["k"] == len(joint.MODEL_PARAM_NAMES[joint.MODEL_LCDM])


def test_model_row_without_registry_falls_back_to_len_param_names() -> None:
    """Verify _model_row falls back to len(param_names) when registry is None."""
    vector = np.array([67.7, 0.31, 0.69, 0.0224, 0.8], dtype=float)
    components = {"total": 10.0, "Hz": 2.0, "DESI_DR2_BAO": 3.0, "fsigma8": 2.5, "CMB_shift": 2.5}

    row = joint._model_row(joint.MODEL_LCDM, vector, components, 50)

    assert row["k"] == len(joint.MODEL_PARAM_NAMES[joint.MODEL_LCDM])
    assert row["registry_schema"] is None
    assert row["commit_sha"] is None


def test_committed_joint_real_json_exposes_dataset_type_claim_boundary_and_fnext() -> None:
    import json
    from pathlib import Path

    payload = json.loads(Path("results/structure_d/joint_real_likelihood.json").read_text(encoding="utf-8"))
    assert payload["dataset_type"] == "real_observational"
    assert payload["claim_boundary"] == "No superiority claim unless real-data metrics pass predefined thresholds."
    assert payload["claim_allowed"] is False
    assert payload["publication_language"] == "RLL is a candidate effective dynamic-transition cosmology under real-data evaluation."
    assert payload["fnext"]["status"] == "not_measured"
    assert payload["fnext"]["F_gap"] is None
    assert payload["fnext"]["score"] is None
    assert payload["fnext"]["claim_allowed"] is False
    assert not any("synthetic" in value or "fixtures" in value for value in payload["datasets"].values())
