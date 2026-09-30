from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "rll_bp_bbn_cmb_background_likelihood.py"
SPEC = importlib.util.spec_from_file_location("rll_bp_bbn_cmb_background_likelihood", MODULE_PATH)
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mod
SPEC.loader.exec_module(mod)


def test_untruncated_combined_summary_prefers_negative_delta_but_physical_map_is_zero():
    mean, sigma = mod.combined_untruncated_gaussian()
    assert mean < 0.0
    assert sigma > 0.0
    receipt = mod.likelihood_receipt()
    assert receipt["physical_MAP_delta_neff"] == 0.0


def test_truncated_95_upper_limit_is_reproducible():
    receipt = mod.likelihood_receipt(0.95)
    assert math.isclose(receipt["delta_neff_upper"], 0.10801185284957185, rel_tol=0.0, abs_tol=1e-14)
    assert math.isclose(receipt["omega_BP_h2_upper"], 6.06584817652547e-7, rel_tol=0.0, abs_tol=1e-18)


def test_positive_radiation_mapping_is_invertible():
    for delta in (0.0, 0.01, 0.1, 1.0):
        omega = mod.omega_bp_h2_from_delta_neff(delta)
        assert math.isclose(mod.delta_neff_from_omega_bp_h2(omega), delta, rel_tol=1e-14, abs_tol=1e-15)


def test_negative_extra_radiation_fails_closed():
    for value in (-1e-12, -1.0):
        try:
            mod.omega_bp_h2_from_delta_neff(value)
        except ValueError:
            pass
        else:
            raise AssertionError("negative physical Delta N_eff must fail closed")


def test_receipt_distinguishes_background_from_full_perturbative_cmb():
    receipt = mod.likelihood_receipt()
    assert receipt["background_profile_verdict"].startswith("PASS_BOUND")
    assert receipt["full_PMF_plasma_perturbative_CMB_verdict"] == "TOKEN_VAZIO"
    assert receipt["raw_likelihood_replay"] is False
    assert receipt["claim_allowed"] is False
    assert receipt["publication_effect"] == "NONE"


def test_upper_omega_examples_scale_as_inverse_h_squared():
    receipt = mod.likelihood_receipt()
    values = receipt["Omega_BP_upper_examples"]
    assert values["H0_50"] > values["H0_67p4"] > values["H0_90"]
