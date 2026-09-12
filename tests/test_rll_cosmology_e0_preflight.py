from __future__ import annotations

import math

from tools import rll_cosmology_e0_preflight as e0
from data.pipelines.structure_d import joint_real_likelihood as joint


def test_e0_preflight_fails_closed_on_current_joint_parameterization() -> None:
    report = e0.build_report()

    assert report["status"] == "BLOCKED_FAIL_CLOSED"
    assert report["claim_allowed"] is False
    assert report["model_selection_claim_allowed"] is False
    assert report["historical_results_mutated"] is False


def test_current_optimizer_admits_non_unit_e0_squared() -> None:
    checks = {
        item["model"]: item
        for item in e0.build_report()["checks"]["z0_normalization_and_closure"]
    }

    for model in joint.MODEL_ORDER:
        check = checks[model]
        assert check["free_OL"] is True
        assert check["free_Ok"] is False
        lo, hi = check["e0_squared_interval_from_bounds"]
        assert lo < 1.0 < hi
        assert check["pass"] is False


def test_normalized_reference_vector_has_h_of_zero_equal_h0() -> None:
    h0 = 67.7
    om = 0.31
    ol = 1.0 - om - joint.ORAD
    params = (h0, om, ol)

    e0_squared = float(joint.e2_lcdm(0.0, *params))
    hz0 = float(joint.hz_from_e2(0.0, joint.e2_lcdm, params))

    assert math.isclose(e0_squared, 1.0, rel_tol=0.0, abs_tol=1.0e-12)
    assert math.isclose(hz0, h0, rel_tol=0.0, abs_tol=1.0e-10)


def test_growth_proxy_is_explicitly_claim_blocked() -> None:
    growth = e0.build_report()["checks"]["growth_likelihood"]

    assert growth["mode"] == "growth_index_proxy"
    assert growth["uses_D_of_z"] is False
    assert growth["pass"] is False


def test_cmb_acoustic_scale_rd_substitution_is_claim_blocked() -> None:
    cmb = e0.build_report()["checks"]["cmb_acoustic_scale"]

    assert cmb["acoustic_scale_uses_rd_drag"] is True
    assert cmb["requires_rs_at_recombination"] is True
    assert cmb["pass"] is False


def test_h0_is_not_promoted_while_closure_gap_exists() -> None:
    h0 = e0.build_report()["checks"]["h0_identification"]

    assert h0["physical_identification_pass"] is False
    assert all(bounds == [60.0, 80.0] for bounds in h0["optimizer_bounds"].values())
