from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "rll_bp_physical_contract.py"
SPEC = importlib.util.spec_from_file_location("rll_bp_physical_contract", MODULE_PATH)
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mod
SPEC.loader.exec_module(mod)


def test_contract_keeps_claim_boundary_and_blueprint_non_authority():
    payload = mod.load_contract()
    assert payload["claim_allowed"] is False
    assert payload["historical_blueprint_ranges"]["authority"] == "BLUEPRINT_NOT_PRIOR"
    assert payload["statistical_prior_state"].startswith("TOKEN_VAZIO")


def test_magnetic_energy_density_is_nonnegative_and_even_in_B():
    assert mod.magnetic_energy_density_si(0.0) == 0.0
    assert mod.magnetic_energy_density_si(2.0) > 0.0
    assert mod.magnetic_energy_density_si(2.0) == mod.magnetic_energy_density_si(-2.0)


def test_a_minus_four_separately_conserved_implies_radiation_w():
    assert math.isclose(mod.w_from_density_scaling_exponent(4.0), 1.0 / 3.0)
    assert math.isclose(mod.w_from_density_scaling_exponent(3.0), 0.0)


def test_negative_B_or_P_is_rejected_in_physical_density_profile():
    for b, p in ((-1e-9, 0.0), (0.0, -1e-9), (-1e-9, -1e-9)):
        try:
            mod.validate_physical_background(b, p)
        except ValueError as exc:
            assert "cannot be negative" in str(exc)
        else:
            raise AssertionError("negative physical energy-density coefficient must fail closed")


def test_zero_null_limit_is_valid():
    receipt = mod.validate_physical_background(0.0, 0.0)
    assert receipt["Omega_BP0"] == 0.0
    assert receipt["B_sign"].startswith("NONNEGATIVE_RESOLVED")
    assert receipt["P_sign"].startswith("NONNEGATIVE_RESOLVED")
    assert receipt["full_physical_CMB_likelihood"] == "TOKEN_VAZIO"


def test_background_delta_neff_mapping_is_monotonic_and_null_at_zero():
    omega_gamma_h2 = 2.4728e-5
    zero = mod.delta_neff_background_equivalent(0.0, 0.0, 67.4, omega_gamma_h2)
    low = mod.delta_neff_background_equivalent(1e-7, 1e-7, 67.4, omega_gamma_h2)
    high = mod.delta_neff_background_equivalent(2e-7, 2e-7, 67.4, omega_gamma_h2)
    assert zero == 0.0
    assert 0.0 < low < high


def test_mapping_keeps_background_only_guard_in_cli_receipt_contract():
    receipt = mod.validate_physical_background(1e-7, 2e-7)
    assert receipt["B_perturbations"].startswith("TOKEN_VAZIO")
    assert receipt["P_perturbations"].startswith("TOKEN_VAZIO")
    assert receipt["statistical_prior"].startswith("TOKEN_VAZIO")
