from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRODUCT = ROOT / "products/rll-evidence-runner"
sys.path.insert(0, str(PRODUCT / "src"))

from rll_evidence.dovekie_wa_lower_bound import (
    TARGET,
    bisect_crossing,
    lower_bracket_from_rows,
)


def test_lower_bracket_selects_nearest_excluded_and_lowest_included_point():
    rows = [
        {"wa": -16.0, "chi2": 10.0},
        {"wa": -12.0, "chi2": 4.5},
        {"wa": -8.0, "chi2": 1.0},
        {"wa": -6.0, "chi2": 0.0},
        {"wa": -4.0, "chi2": 0.5},
    ]
    low, high, best = lower_bracket_from_rows(rows)
    assert best == 0.0
    assert low is not None and low["wa"] == -12.0
    assert high is not None and high["wa"] == -8.0


def test_bisection_converges_to_known_quadratic_lower_crossing():
    rows = [
        {"wa": -12.0, "chi2": 9.0},
        {"wa": -8.0, "chi2": 1.0},
        {"wa": -7.0, "chi2": 0.0},
        {"wa": -6.0, "chi2": 1.0},
    ]

    def evaluator(wa: float):
        return {
            "wa": wa,
            "chi2": (wa + 7.0) ** 2,
            "Omega_m": 0.3,
            "w0": -1.0,
            "M_offset_profiled": 0.0,
            "all_starts_converged": True,
        }

    low, high, evaluated, best = bisect_crossing(
        evaluator,
        rows[0],
        rows[1],
        rows,
        target=TARGET,
        max_iterations=20,
        wa_tolerance=0.005,
    )
    expected = -7.0 - TARGET**0.5
    estimate = 0.5 * (low["wa"] + high["wa"])
    assert abs(estimate - expected) < 0.01
    assert low["chi2"] - best > TARGET
    assert high["chi2"] - best <= TARGET
    assert evaluated


def test_no_lower_included_point_fails_closed():
    rows = [
        {"wa": -10.0, "chi2": 10.0},
        {"wa": -8.0, "chi2": 8.0},
        {"wa": -6.0, "chi2": 0.0},
    ]
    low, high, best = lower_bracket_from_rows(rows)
    assert best == 0.0
    assert low is None
    assert high is None
