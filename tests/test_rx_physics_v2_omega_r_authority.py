from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "tools/rx_physics_v2_omega_r_authority.py"


def load_module():
    spec = importlib.util.spec_from_file_location("ws01_omega_authority_test", MODULE)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def test_derived_radiation_authority_passes_preregistered_checks():
    mod = load_module()
    report = mod.build_report()
    assert report["state"] == "PASS_DERIVED_STANDARD_RADIATION_AUTHORITY"
    assert report["passed"] is True
    assert report["claim_allowed"] is False
    assert report["scientific_confirmation"] is False
    assert report["legacy_fixed_values_promoted"] is False


def test_physical_density_is_h0_invariant_but_fraction_is_not():
    mod = load_module()
    report = mod.build_report()
    rows = report["reference_grid"]
    assert report["checks"]["omega_r_h2_relative_span"] <= 1e-14
    assert report["checks"]["omega_r_monotonic_decreasing_with_H0"] is True
    assert rows[0]["Omega_r"] > rows[-1]["Omega_r"]


def test_rll_null_limit_survives_derived_radiation_semantics():
    mod = load_module()
    report = mod.build_report()
    assert report["checks"]["RLL_LCDM_null_max_abs_e2_delta"] <= 1e-12


def test_fixed_values_are_only_reference_h0_snapshots():
    mod = load_module()
    report = mod.build_report()
    snapshots = report["legacy_fixed_snapshots"]
    assert "9e-05" in snapshots
    assert "9.18e-05" in snapshots
    for row in snapshots.values():
        assert 60.0 < row["equivalent_H0_km_s_Mpc_under_derived_physical_density"] < 80.0


def test_massive_neutrino_transition_boundary_remains_explicit():
    mod = load_module()
    report = mod.build_report()
    assert report["checks"]["full_massive_neutrino_transition_modelled"] is False
    assert "Boltzmann" in report["remaining_boundary"]
