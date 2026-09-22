from __future__ import annotations

import json
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

from tools.rll_perturbation_a1_superhorizon_ic_v1 import (
    D0,
    V5,
    build,
    exact_recurrence_residuals,
    first_omitted_continuity_residual,
)


def test_exact_series_recurrence_coefficients_cancel():
    residuals = exact_recurrence_residuals()
    assert residuals
    assert all(value == 0 for value in residuals.values())


def test_leading_density_relation_matches_conditional_adiabatic_radiation_mode():
    assert D0 == Fraction(3, 4) * Fraction(-2, 1)


def test_first_omitted_residual_is_order_x5():
    x = 1.0e-2
    expected = float(V5) * x**5
    got = first_omitted_continuity_residual(x)
    assert abs(got - expected) <= 1.0e-30
    assert abs(got) < 2.0e-13


def test_a1_3_gate_passes_local_series_but_keeps_coupled_ic_open():
    payload = build()
    assert payload["state"] == "A1_3_COMPONENT_LOCAL_SUPERHORIZON_SERIES_PASS_COUPLED_IC_OPEN"
    assert payload["exact_recurrence_pass"] is True
    assert payload["conditional_adiabatic_leading_pass"] is True
    assert payload["passing_background_cases"] == payload["total_background_cases"] == 9
    assert payload["token_resolution"] == "NOT_RESOLVED"
    assert payload["class_camb_unlock"] is False
    assert "FULL_COUPLED_EINSTEIN_BOLTZMANN_INITIAL_CONDITIONS" in payload["hard_blockers"]


def test_direct_cli_execution_from_repository_root(tmp_path):
    out = tmp_path / "a1_3.json"
    proc = subprocess.run(
        [
            sys.executable,
            "tools/rll_perturbation_a1_superhorizon_ic_v1.py",
            "--output",
            str(out),
        ],
        cwd=Path(__file__).resolve().parents[1],
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr + proc.stdout
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["state"] == "A1_3_COMPONENT_LOCAL_SUPERHORIZON_SERIES_PASS_COUPLED_IC_OPEN"
    assert payload["class_camb_unlock"] is False
