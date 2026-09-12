from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/rll_cmb_rs_camb_benchmark.py"

spec = importlib.util.spec_from_file_location("rll_cmb_rs_camb_benchmark", SCRIPT)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_benchmark_has_three_bounded_cases() -> None:
    cases = module.benchmark_cases()
    assert [row["id"] for row in cases] == [
        "baseline",
        "lower_background",
        "upper_background",
    ]
    for row in cases:
        h = float(row["H0"]) / 100.0
        assert float(row["Omega_m"]) * h * h > float(row["omega_b_h2"])


def test_relative_error_is_symmetric() -> None:
    assert module.relative_error(1.0, 1.0) == 0.0
    assert module.relative_error(144.0, 145.0) == module.relative_error(145.0, 144.0)


def test_tolerances_are_predeclared_and_bounded() -> None:
    assert module.ZSTAR_REL_TOL == 1.0e-2
    assert module.RS_FIT_ZSTAR_REL_TOL == 1.0e-2
    assert module.RS_CAMB_ZSTAR_REL_TOL == 5.0e-3


def test_claim_boundary_remains_fail_closed() -> None:
    source = SCRIPT.read_text(encoding="utf-8")
    assert '"claim_allowed": False' in source
    assert '"publication_ready": False' in source
    assert "does not validate RLL perturbations" in source
    assert "r_d(z_drag) is not substituted for r_s(zstar)" in source
