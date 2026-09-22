import math
import sys
from pathlib import Path

TOOLS = Path(__file__).parents[1] / "tools"
sys.path.insert(0, str(TOOLS))
import rll_qcd_s_sector_bound as q


def test_rll_transition_has_cubic_upper_bound():
    for z in [0.0, 1.0, 10.0, 1.0e3]:
        a = (1.0 + z) ** 3
        for f in [0.0, 0.2, 0.7, 1.0]:
            g = f + (1.0 - f) * a
            assert g <= q.rll_g_upper_bound(z)


def test_bound_decreases_with_temperature():
    b130 = q.evaluate_bound(130.0)
    b400 = q.evaluate_bound(400.0)
    assert b130.delta_h_over_h_upper > b400.delta_h_over_h_upper


def test_bound_increases_with_h0_max():
    b50 = q.evaluate_bound(130.0, h0_km_s_mpc=50.0)
    b90 = q.evaluate_bound(130.0, h0_km_s_mpc=90.0)
    assert b90.delta_h_over_h_upper > b50.delta_h_over_h_upper


def test_entropy_floor_is_conservative():
    b1 = q.evaluate_bound(130.0, gs_ratio_floor=1.0)
    b10 = q.evaluate_bound(130.0, gs_ratio_floor=10.0)
    assert b1.delta_h_over_h_upper > b10.delta_h_over_h_upper


def test_canonical_conservative_number():
    bound = q.evaluate_bound(130.0)
    assert math.isclose(bound.delta_h_over_h_upper, 5.2851781861724384e-11, rel_tol=2e-12)
    assert bound.rho_s_over_radiation_upper < 1.06e-10


def test_bbn_proxy_is_percent_scale():
    proxy = q.bbn_neff_expansion_proxy()
    assert 0.010 < proxy < 0.011


def test_receipt_keeps_full_rll_token_vazio():
    class Args:
        omega_s0_ul = q.DEFAULT_OMEGA_S0_UL95
        h0_max = q.DEFAULT_H0_MAX
        t0_k = q.DEFAULT_T0_K
        t_min_mev = q.DEFAULT_T_MIN_MEV
        t_max_mev = q.DEFAULT_T_MAX_MEV
        gs_ratio_floor = q.DEFAULT_GS_RATIO_FLOOR
        omega_gamma_h2_floor = q.DEFAULT_OMEGA_GAMMA_H2_FLOOR

    receipt = q.build_receipt(Args())
    assert receipt["s_sector_verdict"] == "PASS_LIMITED_DERIVED_BOUND"
    assert receipt["full_rll_verdict"] == "TOKEN_VAZIO"
    assert receipt["claim_allowed"] is False
    assert receipt["separation_orders_log10"] > 8.2
