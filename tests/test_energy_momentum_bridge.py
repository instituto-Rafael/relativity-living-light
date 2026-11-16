from __future__ import annotations

import math

import pytest

from data.pipelines.structure_d.energy_momentum_bridge import (
    C_M_PER_S,
    ENERGY_DENSITY_CONVENTION,
    MASS_DENSITY_CONVENTION,
    build_fnext_gate,
    compute_a_lost,
    compute_a_transition,
    compute_bridge_row,
    compute_f_gap,
    compute_from_ledger,
    energy_density_to_mass_density,
    pressure_density,
    pressure_energy_density,
    quadrature_uncertainty,
    validate_ledger,
)
from data.pipelines.structure_d.synthetic_real_boundary import CLAIM_BOUNDARY


def _field(name: str, value: float | None, unit: str, uncertainty: float | None = 0.1, *, measured: bool = True, source: str | None = "lab") -> dict:
    return {
        "name": name,
        "value": value,
        "uncertainty": uncertainty,
        "unit": unit,
        "source": source,
        "doi_or_url": "https://example.org/source",
        "sha256": None,
        "local_path": None,
        "license": "test-only",
        "measured": measured,
        "notes": "synthetic_regression_test fixture, not real observational data",
    }


def _complete_ledger(uncertainty: bool = True, *, pressure: float = 0.0) -> dict:
    sigma = 0.1 if uncertainty else None
    return {
        "schema": "rll.energy_momentum_observational_ledger.v1",
        "dataset_type": "real_observational",
        "status": "measured",
        "fields": {
            "rho_before": _field("rho_before", 10.0, "J/m^3", sigma),
            "rho_rest_after": _field("rho_rest_after", 4.0, "J/m^3", sigma),
            "rho_radiation": _field("rho_radiation", 1.0, "J/m^3", sigma),
            "rho_kinetic": _field("rho_kinetic", 2.0, "J/m^3", sigma),
            "rho_thermal": _field("rho_thermal", 2.0, "J/m^3", sigma),
            "pressure": _field("pressure", pressure, "Pa", sigma),
            "rho_field": _field("rho_field", 0.5, "J/m^3", sigma),
        },
    }


def test_pressure_density_calculates_p_over_c_squared() -> None:
    assert pressure_density(9.0, c=3.0) == 1.0
    assert pressure_density(1.0) == pytest.approx(1.0 / C_M_PER_S**2)
    assert pressure_energy_density(9.0) == 9.0
    assert energy_density_to_mass_density(9.0, c=3.0) == 1.0


def test_core_energy_momentum_formulas() -> None:
    assert compute_a_lost(10.0, 4.0) == 6.0
    assert compute_a_transition(1.0, 2.0, 2.5, 0.0, 0.5) == 6.0
    assert compute_f_gap(6.0, 5.5) == 0.5
    assert quadrature_uncertainty([3.0, 4.0]) == 5.0


def test_nonzero_pressure_requires_explicit_dimensional_convention() -> None:
    with pytest.raises(ValueError, match="explicit dimensional convention"):
        compute_a_transition(9.0, 18.0, 27.0, 36.0, 9.0, c=3.0)


def test_typed_transition_conventions_are_dimensionally_equivalent() -> None:
    energy = compute_a_transition(
        9.0,
        18.0,
        27.0,
        36.0,
        9.0,
        c=3.0,
        convention=ENERGY_DENSITY_CONVENTION,
    )
    mass = compute_a_transition(
        9.0,
        18.0,
        27.0,
        36.0,
        9.0,
        c=3.0,
        convention=MASS_DENSITY_CONVENTION,
    )
    assert energy == 99.0
    assert mass == 11.0
    assert energy_density_to_mass_density(energy, c=3.0) == mass


def test_typed_bridge_row_closes_same_proxy_in_both_units() -> None:
    row = {
        "rho_before": 180.0,
        "rho_rest_after": 81.0,
        "rho_radiation": 9.0,
        "rho_kinetic": 18.0,
        "rho_thermal": 27.0,
        "pressure": 36.0,
        "rho_field": 9.0,
    }
    energy = compute_bridge_row(
        row,
        c_m_per_s=3.0,
        convention=ENERGY_DENSITY_CONVENTION,
    )
    mass = compute_bridge_row(
        row,
        c_m_per_s=3.0,
        convention=MASS_DENSITY_CONVENTION,
    )
    assert energy["A_lost"] == energy["A_transition"] == 99.0
    assert mass["A_lost"] == mass["A_transition"] == 11.0
    assert energy["F_gap"] == mass["F_gap"] == 0.0
    assert energy["F_gap_unit"] == "J/m^3"
    assert mass["F_gap_unit"] == "kg/m^3"


def test_compute_bridge_row_conserves_measured_transition_terms() -> None:
    bridge = compute_bridge_row(
        {
            "rho_before": 10.0,
            "rho_rest_after": 4.0,
            "rho_radiation": 1.0,
            "rho_kinetic": 2.0,
            "rho_thermal": 2.5,
            "pressure": 0.0,
            "rho_field": 0.5,
        }
    )
    assert bridge["A_lost"] == 6.0
    assert bridge["A_transition"] == 6.0
    assert bridge["F_gap"] == 0.0


def test_ledger_complete_calculates_f_gap_and_uncertainty() -> None:
    result = compute_from_ledger(_complete_ledger())
    assert result["status"] == "measured"
    assert result["F_gap"] == pytest.approx(0.5)
    assert result["F_gap_uncertainty"] is not None
    assert result["uncertainty_status"] == "complete"


def test_nonzero_pressure_ledger_blocks_without_authority_selection() -> None:
    result = compute_from_ledger(_complete_ledger(pressure=9.0), c=3.0)
    assert result["status"] == "blocked_dimensional_convention_required"
    assert result["F_gap"] is None
    assert result["dimensional_convention"].startswith("TOKEN_VAZIO")


def test_nonzero_pressure_ledger_runs_only_with_explicit_typed_convention() -> None:
    energy = compute_from_ledger(
        _complete_ledger(pressure=9.0),
        c=3.0,
        convention=ENERGY_DENSITY_CONVENTION,
    )
    mass = compute_from_ledger(
        _complete_ledger(pressure=9.0),
        c=3.0,
        convention=MASS_DENSITY_CONVENTION,
    )
    assert energy["status"] == mass["status"] == "measured"
    assert energy["dimensional_convention"] == ENERGY_DENSITY_CONVENTION
    assert mass["dimensional_convention"] == MASS_DENSITY_CONVENTION
    assert energy["F_gap_unit"] == "J/m^3"
    assert mass["F_gap_unit"] == "kg/m^3"
    assert energy["F_gap"] / 9.0 == pytest.approx(mass["F_gap"])
    assert energy["F_gap_uncertainty"] / 9.0 == pytest.approx(
        mass["F_gap_uncertainty"]
    )


def test_ledger_absent_or_incomplete_keeps_f_gap_null() -> None:
    assert compute_from_ledger({})["F_gap"] is None
    incomplete = _complete_ledger()
    del incomplete["fields"]["rho_field"]
    result = compute_from_ledger(incomplete)
    assert result["status"] == "not_measured"
    assert result["F_gap"] is None


def test_measured_without_source_fails() -> None:
    ledger = _complete_ledger()
    ledger["fields"]["rho_before"]["source"] = None
    validation = validate_ledger(ledger)
    assert not validation["valid"]
    assert "measured field missing source: rho_before" in validation["errors"]


def test_missing_unit_fails() -> None:
    ledger = _complete_ledger()
    ledger["fields"]["rho_before"]["unit"] = ""
    validation = validate_ledger(ledger)
    assert not validation["valid"]
    assert "missing unit: rho_before" in validation["errors"]


def test_local_measured_file_without_sha256_fails() -> None:
    ledger = _complete_ledger()
    ledger["fields"]["rho_before"]["local_path"] = "data/real/example.csv"
    validation = validate_ledger(ledger)
    assert not validation["valid"]
    assert "measured local field missing sha256: rho_before" in validation["errors"]


def test_incomplete_uncertainties_mark_uncertainty_status_incomplete() -> None:
    result = compute_from_ledger(_complete_ledger(uncertainty=False))
    assert result["status"] == "measured"
    assert result["F_gap"] == pytest.approx(0.5)
    assert result["F_gap_uncertainty"] is None
    assert result["uncertainty_status"] == "incomplete"


def test_fnext_without_ledger_has_null_score_and_no_claim() -> None:
    gate = build_fnext_gate(
        {
            "delta_chi2_rll_minus_lcdm": -1.0,
            "delta_aic_rll_minus_lcdm": -2.0,
            "delta_bic_rll_minus_lcdm": -3.0,
        }
    )
    assert gate["status"] == "not_measured"
    assert gate["F_gap"] is None
    assert gate["score"] is None
    assert gate["claim_allowed"] is False
    assert gate["claim_boundary"] == CLAIM_BOUNDARY


def test_fnext_with_complete_ledger_blocks_scalar_score_until_normalization() -> None:
    gate = build_fnext_gate(
        {
            "delta_chi2_rll_minus_lcdm": -1.0,
            "delta_aic_rll_minus_lcdm": -2.0,
            "delta_bic_rll_minus_lcdm": -3.0,
        },
        _complete_ledger(),
    )
    assert gate["status"] == "measured"
    assert gate["F_gap"] == pytest.approx(0.5)
    assert gate["score"] is None
    assert gate["score_status"] == "blocked_until_normalization_defined"
    assert gate["claim_allowed"] is False


def test_transition_ledger_rejects_incomplete_rows() -> None:
    with pytest.raises(ValueError, match="missing finite fields"):
        compute_bridge_row({"rho_before": 1.0})
