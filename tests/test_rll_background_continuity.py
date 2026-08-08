from __future__ import annotations

import importlib.util
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "check_rll_background.py"
SPEC = importlib.util.spec_from_file_location("check_rll_background", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
bg = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bg)

ZT = 1.164
WT = 0.405
OM = 0.315
OS0 = 0.059


def test_documented_continuity_residual_matches_closed_form() -> None:
    for z in (0.0, 0.3, 1.0, ZT, 2.0, 5.0):
        a = 1.0 / (1.0 + z)
        expected = bg.df_dlna(z, ZT, WT) * (1.0 - a ** -3)
        actual = bg.continuity_residual_documented(z, ZT, WT)
        assert math.isclose(actual, expected, rel_tol=1e-12, abs_tol=1e-12)


def test_documented_pressure_is_not_separately_conserved_during_transition() -> None:
    residual = bg.continuity_residual_documented(ZT, ZT, WT)
    assert abs(residual) > 1.0e-6


def test_conserved_pressure_closes_continuity() -> None:
    for z in (0.0, 0.3, 1.0, ZT, 2.0, 5.0):
        residual = bg.continuity_residual_conserved(z, ZT, WT)
        assert abs(residual) <= 1.0e-12


def test_conserved_equation_of_state_differs_from_documented_ratio() -> None:
    z = 1.0
    assert not math.isclose(
        bg.w_conserved(z, ZT, WT),
        bg.w_eff(z, ZT, WT),
        rel_tol=1e-6,
        abs_tol=1e-6,
    )


def test_conserved_kinetic_gate_is_finite_for_central_parameters() -> None:
    for z in (0.0, 0.3, 1.0, ZT, 2.0, 5.0):
        value = bg.kinetic_gate_conserved(z, OM, OS0, ZT, WT)
        assert math.isfinite(value)
