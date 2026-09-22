from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np

from tools.rll_perturbation_a1_gauge_regularization_v1 import (
    ACTIVE_FLOOR,
    algebraic_equivalence_probe,
    build,
    d2rho_factor_dlna2,
)
from tools.rll_perturbation_a1_restframe_candidate_v1 import (
    drho_factor_dlna,
    rho_factor,
)


def test_second_derivative_matches_centered_ln_a_finite_difference():
    z = 1.7
    zt = 1.0
    wt = 0.3
    a = 1.0 / (1.0 + z)
    h = 1.0e-5

    def rho_at_lna(offset: float) -> float:
        aa = a * np.exp(offset)
        zz = 1.0 / aa - 1.0
        return float(rho_factor(np.array([zz]), zt, wt)[0])

    numeric = (rho_at_lna(h) - 2.0 * rho_at_lna(0.0) + rho_at_lna(-h)) / (h * h)
    analytic = float(d2rho_factor_dlna2(np.array([z]), zt, wt)[0])
    assert abs(numeric - analytic) <= 5.0e-5 * max(1.0, abs(analytic))


def test_regularized_equations_are_algebraically_equivalent_away_from_divide():
    probe = algebraic_equivalence_probe(w=-0.63, q=2.4, ca2=-1.43)
    assert probe["delta_equivalent"] is True
    assert probe["u_equivalent"] is True


def test_a1_2_sweep_passes_only_regularization_gate_and_keeps_ic_open():
    payload = build()
    assert payload["state"] == "A1_2_GAUGE_VARIABLE_REGULARIZATION_PASS_IC_OPEN"
    assert payload["passing_cases"] == payload["total_cases"] == 9
    assert payload["token_resolution"] == "NOT_RESOLVED"
    assert payload["class_camb_unlock"] is False
    assert "SUPER_HORIZON_INITIAL_CONDITIONS" in payload["hard_blockers"]
    assert sum(payload["stiffness_counts"].values()) == 9
    for row in payload["cases"]:
        assert row["pass"] is True
        assert row["active_points"] > 0
        assert row["one_plus_w_min"] >= -1.0e-10
        assert row["finite_active_coefficients"] is True
        assert row["equivalence_probe"]["delta_equivalent"] is True
        assert row["equivalence_probe"]["u_equivalent"] is True
        assert row["active_floor"] == ACTIVE_FLOOR


def test_sharp_transitions_are_preserved_as_stiffness_not_silently_rejected():
    payload = build()
    sharp = [r for r in payload["cases"] if r["wt"] == 0.05]
    assert sharp
    assert any(r["stiffness"] in {"MODERATE", "HIGH"} for r in sharp)


def test_direct_cli_execution_from_repository_root(tmp_path):
    out = tmp_path / "a1_2.json"
    proc = subprocess.run(
        [
            sys.executable,
            "tools/rll_perturbation_a1_gauge_regularization_v1.py",
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
    assert payload["state"] == "A1_2_GAUGE_VARIABLE_REGULARIZATION_PASS_IC_OPEN"
    assert payload["passing_cases"] == payload["total_cases"] == 9
    assert payload["class_camb_unlock"] is False
