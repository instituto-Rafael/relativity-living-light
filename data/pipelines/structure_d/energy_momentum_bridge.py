"""Energy-momentum bridge accounting for the RLL SGP/FNext validation gate.

Synthetic rows are acceptable for code sanity tests, but this module treats
observational ledgers conservatively: missing required measured fields keep
``F_gap`` as ``None`` instead of inventing a bridge term.
"""

from __future__ import annotations

import math
from collections.abc import Iterable, Mapping
from typing import Any

from .synthetic_real_boundary import CLAIM_BOUNDARY

C_M_PER_S = 299_792_458.0
ENERGY_DENSITY_CONVENTION = "ENERGY_DENSITY_CONVENTION"
MASS_DENSITY_CONVENTION = "MASS_DENSITY_CONVENTION"
VALID_DIMENSIONAL_CONVENTIONS = frozenset(
    {ENERGY_DENSITY_CONVENTION, MASS_DENSITY_CONVENTION}
)
REQUIRED_LEDGER_FIELDS = (
    "rho_before",
    "rho_rest_after",
    "rho_radiation",
    "rho_kinetic",
    "rho_thermal",
    "pressure",
    "rho_field",
)
REQUIRED_UNITS = {
    "rho_before": "J/m^3",
    "rho_rest_after": "J/m^3",
    "rho_radiation": "J/m^3",
    "rho_kinetic": "J/m^3",
    "rho_thermal": "J/m^3",
    "pressure": "Pa",
    "rho_field": "J/m^3",
}


def _finite_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number):
        return None
    return number


def pressure_density(pressure_pa: float, c: float = C_M_PER_S) -> float:
    """Return the mass-equivalent density P/c^2 in kg/m^3."""
    return float(pressure_pa) / (float(c) ** 2)


def pressure_energy_density(pressure_pa: float) -> float:
    """Return pressure as energy density; 1 Pa == 1 J/m^3 dimensionally."""
    return float(pressure_pa)


def energy_density_to_mass_density(value_j_per_m3: float, c: float = C_M_PER_S) -> float:
    return float(value_j_per_m3) / (float(c) ** 2)


def _require_dimensional_convention(convention: str) -> str:
    if convention not in VALID_DIMENSIONAL_CONVENTIONS:
        raise ValueError(
            "dimensional convention must be ENERGY_DENSITY_CONVENTION "
            "or MASS_DENSITY_CONVENTION"
        )
    return convention


def compute_a_lost(
    rho_before: float,
    rho_rest_after: float,
    *,
    convention: str = ENERGY_DENSITY_CONVENTION,
    c: float = C_M_PER_S,
) -> float:
    value = float(rho_before) - float(rho_rest_after)
    convention = _require_dimensional_convention(convention)
    if convention == MASS_DENSITY_CONVENTION:
        return energy_density_to_mass_density(value, c)
    return value


def compute_a_transition(
    rho_radiation: float,
    rho_kinetic: float,
    rho_thermal: float,
    pressure: float,
    rho_field: float,
    c: float = C_M_PER_S,
    *,
    convention: str | None = None,
) -> float:
    """Compute a dimensionally coherent scalar transition proxy.

    Historical calls with zero pressure remain valid as an energy-density
    proxy.  Non-zero pressure is fail-closed unless the caller explicitly
    selects one of the two dimensional conventions.  This function only
    closes dimensional arithmetic; it does not establish that pressure should
    enter a scalar physical budget.
    """
    pressure = float(pressure)
    if convention is None:
        if pressure != 0.0:
            raise ValueError(
                "nonzero pressure requires explicit dimensional convention"
            )
        convention = ENERGY_DENSITY_CONVENTION

    convention = _require_dimensional_convention(convention)
    energy_terms = (
        float(rho_radiation)
        + float(rho_kinetic)
        + float(rho_thermal)
        + float(rho_field)
    )
    if convention == ENERGY_DENSITY_CONVENTION:
        return energy_terms + pressure_energy_density(pressure)
    return energy_density_to_mass_density(energy_terms, c) + pressure_density(
        pressure, c
    )


def compute_f_gap(a_lost: float, a_transition: float) -> float:
    return float(a_lost) - float(a_transition)


def quadrature_uncertainty(values: list[float]) -> float:
    return math.sqrt(math.fsum(float(value) ** 2 for value in values))


def _entry_from_ledger(ledger: Mapping[str, Any], field: str) -> Mapping[str, Any] | None:
    fields = ledger.get("fields") if isinstance(ledger.get("fields"), Mapping) else ledger
    entry = fields.get(field) if isinstance(fields, Mapping) else None
    return entry if isinstance(entry, Mapping) else None


def validate_ledger(ledger: Mapping[str, Any] | None) -> dict[str, Any]:
    if ledger is None:
        return {"valid": False, "status": "not_measured", "errors": ["ledger absent"]}

    errors: list[str] = []
    for field in REQUIRED_LEDGER_FIELDS:
        entry = _entry_from_ledger(ledger, field)
        if entry is None:
            errors.append(f"missing required field: {field}")
            continue
        unit = entry.get("unit")
        if not unit:
            errors.append(f"missing unit: {field}")
        elif unit != REQUIRED_UNITS[field]:
            errors.append(f"unexpected unit for {field}: {unit}")
        measured = bool(entry.get("measured"))
        if measured and not entry.get("source"):
            errors.append(f"measured field missing source: {field}")
        local_path = entry.get("local_path") or entry.get("path") or entry.get("file")
        if measured and local_path and not entry.get("sha256"):
            errors.append(f"measured local field missing sha256: {field}")
        if measured and _finite_float(entry.get("value")) is None:
            errors.append(f"measured field missing finite value: {field}")

    return {"valid": not errors, "status": "measured" if not errors else "not_measured", "errors": errors}


def compute_from_ledger(
    ledger: Mapping[str, Any],
    c: float = C_M_PER_S,
    *,
    convention: str | None = None,
) -> dict[str, Any]:
    validation = validate_ledger(ledger)
    if not validation["valid"]:
        return {
            "status": "not_measured",
            "F_gap": None,
            "F_gap_uncertainty": None,
            "uncertainty_status": "incomplete",
            "errors": validation["errors"],
        }

    values = {field: float(_entry_from_ledger(ledger, field)["value"]) for field in REQUIRED_LEDGER_FIELDS}  # type: ignore[index]
    if values["pressure"] != 0.0 and convention is None:
        return {
            "status": "blocked_dimensional_convention_required",
            "F_gap": None,
            "F_gap_uncertainty": None,
            "uncertainty_status": "incomplete",
            "dimensional_convention": "TOKEN_VAZIO_SCIENTIFIC_DIMENSIONAL_AUTHORITY",
            "F_gap_unit": None,
            "errors": ["nonzero pressure requires explicit dimensional convention"],
        }

    active_convention = convention or ENERGY_DENSITY_CONVENTION
    active_convention = _require_dimensional_convention(active_convention)
    a_lost = compute_a_lost(
        values["rho_before"],
        values["rho_rest_after"],
        convention=active_convention,
        c=c,
    )
    a_transition = compute_a_transition(
        values["rho_radiation"],
        values["rho_kinetic"],
        values["rho_thermal"],
        values["pressure"],
        values["rho_field"],
        c,
        convention=active_convention,
    )
    uncertainties = {field: _finite_float(_entry_from_ledger(ledger, field).get("uncertainty")) for field in REQUIRED_LEDGER_FIELDS}  # type: ignore[union-attr]
    uncertainty_status = "complete" if all(value is not None for value in uncertainties.values()) else "incomplete"
    f_gap_uncertainty = None
    if uncertainty_status == "complete":
        a_lost_unc = quadrature_uncertainty([uncertainties["rho_before"], uncertainties["rho_rest_after"]])  # type: ignore[list-item]
        a_transition_unc = quadrature_uncertainty(
            [
                uncertainties["rho_radiation"],  # type: ignore[list-item]
                uncertainties["rho_kinetic"],  # type: ignore[list-item]
                uncertainties["rho_thermal"],  # type: ignore[list-item]
                (
                    uncertainties["pressure"]  # type: ignore[list-item]
                    if active_convention == ENERGY_DENSITY_CONVENTION
                    else pressure_density(uncertainties["pressure"], c)  # type: ignore[arg-type]
                ),
                uncertainties["rho_field"],  # type: ignore[list-item]
            ]
        )
        f_gap_uncertainty = quadrature_uncertainty([a_lost_unc, a_transition_unc])

    return {
        "status": "measured",
        "A_lost": a_lost,
        "A_transition": a_transition,
        "pressure_term": (
            pressure_energy_density(values["pressure"])
            if active_convention == ENERGY_DENSITY_CONVENTION
            else pressure_density(values["pressure"], c)
        ),
        "dimensional_convention": active_convention,
        "F_gap_unit": (
            "J/m^3"
            if active_convention == ENERGY_DENSITY_CONVENTION
            else "kg/m^3"
        ),
        "F_gap": compute_f_gap(a_lost, a_transition),
        "F_gap_uncertainty": f_gap_uncertainty,
        "uncertainty_status": uncertainty_status,
        "errors": [],
    }


def compute_bridge_row(
    row: Mapping[str, Any],
    c_m_per_s: float = C_M_PER_S,
    *,
    convention: str | None = None,
) -> dict[str, Any]:
    values: dict[str, float] = {}
    missing = []
    for field in REQUIRED_LEDGER_FIELDS:
        parsed = _finite_float(row.get(field))
        if parsed is None:
            missing.append(field)
        else:
            values[field] = parsed
    if missing:
        raise ValueError(f"transition ledger row missing finite fields: {missing}")

    if values["pressure"] != 0.0 and convention is None:
        raise ValueError("nonzero pressure requires explicit dimensional convention")

    active_convention = _require_dimensional_convention(
        convention or ENERGY_DENSITY_CONVENTION
    )
    a_lost = compute_a_lost(
        values["rho_before"],
        values["rho_rest_after"],
        convention=active_convention,
        c=c_m_per_s,
    )
    a_transition = compute_a_transition(
        values["rho_radiation"],
        values["rho_kinetic"],
        values["rho_thermal"],
        values["pressure"],
        values["rho_field"],
        c_m_per_s,
        convention=active_convention,
    )
    return {
        "A_lost": a_lost,
        "A_transition": a_transition,
        "pressure_term": (
            pressure_energy_density(values["pressure"])
            if active_convention == ENERGY_DENSITY_CONVENTION
            else pressure_density(values["pressure"], c_m_per_s)
        ),
        "dimensional_convention": active_convention,
        "F_gap_unit": (
            "J/m^3"
            if active_convention == ENERGY_DENSITY_CONVENTION
            else "kg/m^3"
        ),
        "F_gap": compute_f_gap(a_lost, a_transition),
    }


def summarize_f_gap(rows: Iterable[Mapping[str, Any]] | None) -> dict[str, Any]:
    if rows is None:
        return {
            "status": "not_measured",
            "rows_used": 0,
            "F_gap": None,
            "note": "No transition ledger supplied; missing bridge term must be measured, not invented.",
        }
    computed = [compute_bridge_row(row) for row in rows]
    if not computed:
        return {
            "status": "not_measured",
            "rows_used": 0,
            "F_gap": None,
            "note": "Empty transition ledger; missing bridge term must be measured, not invented.",
        }
    total_gap = math.fsum(item["F_gap"] for item in computed)
    return {"status": "measured", "rows_used": len(computed), "F_gap": total_gap, "mean_F_gap": total_gap / len(computed), "components": computed}


def _row_by_model(comparison_rows: Iterable[Mapping[str, Any]], model_name: str) -> Mapping[str, Any]:
    for row in comparison_rows:
        if row.get("model") == model_name:
            return row
    raise ValueError(f"model row not found: {model_name}")


def _comparison_delta_from_rows(comparison_rows: Iterable[Mapping[str, Any]], baseline_model: str, candidate_model: str) -> dict[str, float]:
    rows = list(comparison_rows)
    baseline = _row_by_model(rows, baseline_model)
    candidate = _row_by_model(rows, candidate_model)
    return {
        "delta_chi2_rll_minus_lcdm": float(candidate["chi2"]) - float(baseline["chi2"]),
        "delta_aic_rll_minus_lcdm": float(candidate["AIC"]) - float(baseline["AIC"]),
        "delta_bic_rll_minus_lcdm": float(candidate["BIC"]) - float(baseline["BIC"]),
    }


def build_fnext_gate(comparison_delta: dict | Iterable[Mapping[str, Any]], ledger: dict | None = None, *legacy_args: Any, **legacy_kwargs: Any) -> dict[str, Any]:
    """Build the diagnostic FNext gate without turning it into a claim.

    Preferred API: ``build_fnext_gate(comparison_delta, ledger=None)`` where the
    delta keys are RLL-minus-LCDM.  A legacy row-based call is still accepted for
    existing pipeline compatibility.
    """

    if not isinstance(comparison_delta, Mapping):
        baseline_model = str(ledger)
        candidate_model = str(legacy_args[0]) if legacy_args else str(legacy_kwargs.get("candidate_model"))
        bridge_rows = legacy_kwargs.get("bridge_rows", legacy_args[1] if len(legacy_args) > 1 else None)
        delta = _comparison_delta_from_rows(comparison_delta, baseline_model, candidate_model)
        ledger_result = summarize_f_gap(bridge_rows)
        f_gap = ledger_result["F_gap"]
        status = "measured" if ledger_result["status"] == "measured" else "not_measured"
        f_gap_uncertainty = None
        uncertainty_status = "incomplete"
        reason = ledger_result.get("note", "Legacy measured bridge rows supplied.")
    else:
        delta = dict(comparison_delta)
        ledger_result = compute_from_ledger(ledger) if ledger is not None else {"status": "not_measured", "F_gap": None, "F_gap_uncertainty": None, "uncertainty_status": "incomplete", "errors": ["ledger absent"]}
        f_gap = ledger_result["F_gap"]
        status = ledger_result["status"]
        f_gap_uncertainty = ledger_result.get("F_gap_uncertainty")
        uncertainty_status = ledger_result.get("uncertainty_status", "incomplete")
        reason = "; ".join(ledger_result.get("errors", [])) or "FNext is diagnostic and cannot authorize claims."

    dchi2 = _finite_float(delta.get("delta_chi2_rll_minus_lcdm"))
    daic = _finite_float(delta.get("delta_aic_rll_minus_lcdm"))
    dbic = _finite_float(delta.get("delta_bic_rll_minus_lcdm"))
    score = None
    score_status = "not_computable"
    if f_gap is not None and dchi2 is not None and daic is not None and dbic is not None:
        score_status = "blocked_until_normalization_defined"
        reason = "F_gap is measured, but no physically justified F_gap normalization is defined for a scalar FNext score."

    return {
        "schema": "rll.energy_momentum_bridge.fnext.v1",
        "status": status,
        "F_gap": f_gap,
        "F_gap_uncertainty": f_gap_uncertainty,
        "uncertainty_status": uncertainty_status,
        "delta_chi2_rll_minus_lcdm": dchi2,
        "delta_aic_rll_minus_lcdm": daic,
        "delta_bic_rll_minus_lcdm": dbic,
        "score": score,
        "score_status": score_status,
        "claim_boundary": CLAIM_BOUNDARY,
        "claim_allowed": False,
        "reason": reason,
    }
