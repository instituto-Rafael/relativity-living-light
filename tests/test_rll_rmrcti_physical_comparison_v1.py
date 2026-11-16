import math
from tools.rll_rmrcti_physical_comparison_v1 import build

def test_real_desi_comparison_is_source_bound_and_claim_closed():
    out=build()
    assert out["physical_dataset"]["points"]==13
    assert out["physical_dataset"]["anisotropic_pairs"]==6
    assert out["claim_allowed"] is False
    assert out["direct_delta_p_physical_test"]["delta_p_computed_on_desi"] is False
    assert out["direct_delta_p_physical_test"]["state"].startswith("BLOCKED_")

def test_standardized_residuals_match_recorded_g4_null_geometry():
    out=build()
    assert math.isclose(out["models"]["LCDM"]["standardized_residual_summary"]["rms_z"],0.943563073605141,rel_tol=0,abs_tol=1e-12)
    assert math.isclose(out["models"]["RLL"]["standardized_residual_summary"]["rms_z"],0.943563074464895,rel_tol=0,abs_tol=1e-12)
    assert out["cross_model_geometry"]["max_abs_prediction_difference"]<1e-7
    assert out["result"]["background_geometry_discrimination"]=="NULL_SUBMANIFOLD_NO_DISCRIMINATION"

def test_block_summary_is_not_silently_called_full_covariance():
    out=build()
    for model in ("LCDM","RLL"):
        assert out["models"][model]["full_minus_block_summary_chi2"]>0.8
        assert out["models"][model]["full_covariance_g4_chi2"]>out["models"][model]["block_summary_chi2"]["chi2"]

def test_geometry_pair_features_are_six_and_finite():
    out=build()
    for model in ("LCDM","RLL"):
        rows=out["models"][model]["geometry_pairs"]
        assert len(rows)==6
        for row in rows:
            assert math.isfinite(row["residual"]["log_scale"])
            assert math.isfinite(row["residual"]["anisotropy"])


def test_joint_real_64_comparison_preserves_null_boundary_and_penalty():
    out=build()
    j=out["joint_real_64"]
    assert j["n_obs"]==64
    assert j["datasets"]==["Hz","DESI_DR2_BAO","fsigma8","CMB_shift"]
    assert math.isclose(j["delta_RLL_minus_LCDM"]["chi2"],0.006285088039717834,rel_tol=0,abs_tol=1e-12)
    assert j["delta_RLL_minus_LCDM"]["AIC"]>6.0
    assert j["delta_RLL_minus_LCDM"]["BIC"]>12.0
    assert j["RLL"]["Omega_s0"]==0.0
    assert j["execution_class"]=="COMMITTED_REAL_JOINT_ARTIFACT_RECOMPARISON_NOT_REFIT"
