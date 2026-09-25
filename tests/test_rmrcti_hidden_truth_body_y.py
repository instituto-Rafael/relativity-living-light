import math
from rx.rmrcti_hidden_truth_body_y import run_benchmark

def test_body_y_hidden_truth_recovery_is_deterministic_and_fail_closed():
    result=run_benchmark()
    assert result["dataset_type"]=="synthetic_hidden_truth"
    assert result["claim_allowed"] is False
    assert result["state"]=="PASS_SYNTHETIC_HIDDEN_TRUTH"
    assert result["hidden_truth_recovery"]=={"recovered":5,"total":5,"rate":1.0,"pass":True}
    assert all(row["winner"]=="truth" for row in result["seed_results"])

def test_adaptive_geometry_changes_numerics_not_physics():
    a=run_benchmark()["adaptive_numerics"]
    assert a["adaptive_not_worse"] is True
    assert a["adaptive_rk4_steps"]>a["fixed_rk4_steps"]
    assert a["adaptive_max_subdivision"]>1
    assert a["physical_parameters_changed"] is False
    assert a["adaptive_position_rmse"]<=a["fixed_position_rmse"]

def test_retarded_observation_and_weak_field_gate_are_explicit():
    result=run_benchmark()
    assert result["retarded_observation"]["iterative_emission_time"] is True
    gate=result["weak_field_gate"]
    assert gate["pass"] is True
    assert gate["strong_field_branch"] is False
    assert gate["max_GM_over_rc2_proxy"]<gate["declared_tolerance"]
    assert gate["max_v_over_c"]<0.05

def test_g6_primary_is_preregistered_and_rmrcti_target_is_not_fitted():
    result=run_benchmark()
    assert result["g6_preregistered_primary"]["feature"]=="retarded_xy_Mahalanobis2"
    assert "Holm" in result["g6_preregistered_primary"]["multiple_testing_policy"]
    r=result["rmrcti_adapter"]
    assert r["delta_p_target_0_18_fitted"] is False
    assert math.isclose(r["omega_persistence_recovery_fraction"],1.0,abs_tol=0.0)
    assert r["mean_delta_p_op"]==-0.15
