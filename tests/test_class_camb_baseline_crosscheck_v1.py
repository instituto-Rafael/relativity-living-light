from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/crosscheck_class_camb_baselines.py"

spec = importlib.util.spec_from_file_location("class_camb_crosscheck", SCRIPT)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_relative_error_is_symmetric_and_bounded_for_equal_values():
    assert module.relative_error(1.0, 1.0) == 0.0
    assert module.relative_error(100.0, 101.0) == module.relative_error(101.0, 100.0)
    assert 0.0 < module.relative_error(100.0, 101.0) < 0.02


def test_baseline_parameter_vectors_are_explicit_and_non_crossing():
    lcdm = module.parameter_vector("lcdm")
    cpl = module.parameter_vector("cpl")
    assert lcdm["w0"] == -1.0 and lcdm["wa"] == 0.0
    assert cpl["w0"] == -0.90 and cpl["wa"] == 0.20
    assert cpl["w0"] + cpl["wa"] > -1.0
    assert lcdm["Omega_m"] == cpl["Omega_m"]
    assert lcdm["Omega_b"] == cpl["Omega_b"]


def test_declared_tolerances_are_not_relaxed_by_diagnostic_cycle():
    source = SCRIPT.read_text(encoding="utf-8")
    assert '"H_km_s_Mpc": 5.0e-3' in source
    assert '"D_A_Mpc": 5.0e-3' in source
    assert '"Pk_Mpc3": 8.0e-2' in source
    assert '"Cl_TT_dimensionless": 8.0e-2' in source
