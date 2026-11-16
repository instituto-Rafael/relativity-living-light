"""Preflight contract tests: detection is not equivalent to model validation."""

from __future__ import annotations

from scripts.rll_joint_physics_preflight import audit, source_facts


STUB = '''ORAD = 9e-5

def e2_lcdm(): pass

def e2_wcdm(): pass

def e2_cpl(): pass

def e2_rll():
    superposition = os0 * (fz + (1.0 - fz) * (1.0 + z_arr) ** 3)

def hz_from_e2(): pass

def cmb_shift_prediction():
    return rd_drag_mpc(70, .3, .02)

def fsigma8_prediction():
    return omega_m_z_from_e2(1) ** 0.55
'''


def example_data():
    return {"interpretation_label": "lcdm_preferred", "rows": [
        {"model": "LCDM_joint_real", "H0": 60.0, "Om": .35, "OL": .91, "BIC": 115},
        {"model": "CPL_w0waCDM_joint_real", "H0": 60.1, "Om": .35, "OL": .66, "BIC": 92},
        {"model": "RLL_joint_real", "H0": 60.0, "Om": .35, "OL": .91, "BIC": 127, "Os0": 0.0},
    ]}


def test_preflight_reports_conflicts_without_claim_promotion():
    receipt = audit(example_data(), STUB)
    assert receipt["claim_allowed"] is False
    assert receipt["best_BIC_model_in_archived_rows"] == "CPL_w0waCDM_joint_real"
    assert "ARCHIVED_INTERPRETATION_LABEL_CONTRADICTS_BIC_ORDER" in receipt["flags"]
    assert "H0_NORMALIZATION_REQUIRES_PHYSICAL_CONVENTION_CHECK" in receipt["flags"]
    assert "RLL_NULL_BOUNDARY_ZT_WT_NONIDENTIFIABLE" in receipt["flags"]
    assert "CMB_RD_VS_RS_RECOMBINATION_REVIEW" in receipt["flags"]
    assert "FSIGMA8_MISSING_EXPLICIT_GROWTH_FACTOR_REVIEW" in receipt["flags"]


def test_fails_closed_if_formula_disappears():
    receipt = audit(example_data(), "ORAD = None\n")
    assert "TOKEN_VAZIO_SOURCE_FORMULA_GUARD" in receipt["flags"]
    assert source_facts("ORAD = None")["radiation_density"] is None


def test_default_outputs_are_deterministic_and_no_source_mutation():
    a = audit(example_data(), STUB)
    b = audit(example_data(), STUB)
    assert a == b
    assert a["scope"] == "archived_results_and_source_formula_preflight_only"
