#!/usr/bin/env python3
"""Validate the RLL multiphysics filament matrix with Python stdlib only."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

EXPECTED_FILAMENTS = [
    "electrical_source_coil_ac",
    "water_spray_charge_ions",
    "thermal_mass_phase_transfer",
    "skin_sweat_contact_electricity",
    "neuroionic_autonomic_state",
    "cardiac_electric_magnetic_pressure",
    "respiration_co2_acid_base",
    "voice_acoustics_joy_relaxation",
    "hair_static_point_geometry",
    "electrical_fault_lightning_safety",
]

REQUIRED_POLICY_TRUE = {
    "parallel_filaments",
    "typed_cross_filament_edges",
    "shared_state_without_semantic_collapse",
    "coupling_does_not_imply_causality",
    "external_evidence_is_not_local_measurement",
    "subjective_state_is_not_instrument_measurement",
    "numeric_frequency_match_is_not_mechanism_identity",
}

REQUIRED_BLOCKS = {
    "electrical_source_coil_ac": {
        "APPLIANCE_HAS_COIL_THEREFORE_BRAIN_EFFECT",
        "NUMERIC_FREQUENCY_MATCH_THEREFORE_SAME_MECHANISM",
    },
    "water_spray_charge_ions": {
        "HEATER_RESISTANCE_DIRECTLY_CAUSES_IONIZATION",
        "AIR_IONS_DIRECTLY_BECOME_NEURAL_ION_CURRENTS",
    },
    "thermal_mass_phase_transfer": {
        "WARMTH_ALWAYS_MEANS_RELAXATION",
        "VAPORIZATION_IS_IONIZATION",
    },
    "skin_sweat_contact_electricity": {
        "SWEAT_PROTECTS_FROM_ELECTRIC_SHOCK",
        "SKIN_CONDUCTANCE_IS_DIRECT_MEASURE_OF_EMOTION_CONTENT",
    },
    "neuroionic_autonomic_state": {
        "AMBIENT_ION_COUNT_EQUALS_BRAIN_ION_SIGNALING",
        "EXTERNAL_STATIC_CHARGE_ENCODES_EMOTION",
    },
    "cardiac_electric_magnetic_pressure": {
        "HEART_MAGNETIC_FIELD_TRANSMITS_SEMANTIC_EMOTION",
        "DETECTABLE_FIELD_IMPLIES_DOMINANT_CAUSAL_PATH",
    },
    "respiration_co2_acid_base": {
        "EMOTION_HAS_AN_INTRINSIC_PH",
        "SELF_REPORTED_MOOD_IS_A_BLOOD_PH_MEASUREMENT",
    },
    "voice_acoustics_joy_relaxation": {
        "IONIZATION_CAUSES_SINGING",
        "JOY_OR_RELAXATION_CAN_BE_INFERRED_WITHOUT_REPORT_OR_VALIDATED_MEASURE",
    },
    "hair_static_point_geometry": {
        "HAIR_MOVEMENT_PROVES_INTERNAL_PHYSIOLOGICAL_EFFECT",
        "HUMAN_BODY_IS_A_SAFE_LIGHTNING_ROD",
    },
    "electrical_fault_lightning_safety": {
        "WET_SKIN_IS_PROTECTIVE",
        "SHOWER_IS_SAFE_DURING_THUNDERSTORM",
        "POINT_EFFECT_IS_A_BENEFICIAL_HUMAN_ADAPTATION",
    },
}

REQUIRED_GATES = {
    "SOURCE_AND_TIMESTAMP",
    "UNITS_AND_CALIBRATION",
    "LOCAL_MEASUREMENT_OR_EXPLICIT_NOT_APPLICABLE",
    "CONFOUNDERS",
    "MECHANISM_WITH_ALTERNATIVES",
    "REPRODUCTION",
    "SAFETY_REVIEW",
    "FALSIFIER",
}


class MatrixError(ValueError):
    """Raised when a structural, scientific-custody or safety invariant fails."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise MatrixError(message)


def load_matrix(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise MatrixError("matrix root must be an object")
    return value


def validate_matrix(data: dict[str, Any], *, strict: bool = True) -> dict[str, Any]:
    _require(data.get("schema_version") == "1.0", "schema_version must be 1.0")
    _require(data.get("matrix_id") == "rll-multiphysics-filament-canonical-v1", "matrix_id mismatch")
    _require(data.get("claim_allowed") is False, "claim_allowed must remain false")
    _require(data.get("stdlib_only_validation") is True, "validator must remain stdlib-only")
    _require(data.get("new_workflow_required") is False, "no new workflow/YML may be required")

    policy = data.get("coupling_policy", {})
    for key in REQUIRED_POLICY_TRUE:
        _require(policy.get(key) is True, f"coupling policy must preserve {key}=true")

    filaments = data.get("filaments")
    _require(isinstance(filaments, list), "filaments must be a list")
    actual_ids = [item.get("id") for item in filaments]
    _require(actual_ids == EXPECTED_FILAMENTS, f"filament order mismatch: {actual_ids!r}")
    _require([item.get("order") for item in filaments] == list(range(1, 11)), "orders must be 1..10")
    _require(len(actual_ids) == len(set(actual_ids)), "filament ids must be unique")

    by_id = {item["id"]: item for item in filaments}
    for filament_id, required_blocks in REQUIRED_BLOCKS.items():
        item = by_id[filament_id]
        _require(bool(item.get("inputs")), f"{filament_id}: inputs required")
        _require(bool(item.get("outputs")), f"{filament_id}: outputs required")
        _require(bool(item.get("mechanism")), f"{filament_id}: mechanism required")
        blocks = set(item.get("blocked_inferences", []))
        missing = required_blocks - blocks
        _require(not missing, f"{filament_id}: blocked inferences missing: {sorted(missing)}")
        local_state = item.get("local_measurement_state")
        _require(
            local_state in {"TOKEN_VAZIO_LOCAL", "NOT_APPLICABLE_WITHOUT_NEUROINSTRUMENTATION"},
            f"{filament_id}: invalid local measurement state",
        )

    edge_list = data.get("cross_filament_edges", [])
    _require(isinstance(edge_list, list) and edge_list, "cross_filament_edges required")
    for edge in edge_list:
        _require(edge.get("from") in by_id, f"unknown edge source: {edge.get('from')}")
        _require(edge.get("to") in by_id, f"unknown edge target: {edge.get('to')}")
        _require(edge.get("from") != edge.get("to"), "self-coupling requires a separate declared model")

    correlation_edges = [
        edge for edge in edge_list
        if edge.get("type") == "CORRELATION_CANDIDATE_ONLY"
    ]
    _require(bool(correlation_edges), "at least one correlation-only edge is required")
    _require(
        all(edge.get("state") == "TOKEN_VAZIO_CAUSAL" for edge in correlation_edges),
        "correlation-only edges must remain TOKEN_VAZIO_CAUSAL",
    )

    units = data.get("conservation_and_units", {})
    _require(units.get("frequency_requires_unit") == "Hz", "frequency unit must be Hz")
    _require(units.get("magnetic_flux_density_requires_unit") == "T", "magnetic field unit must be T")
    _require(units.get("electric_field_requires_unit") == "V/m", "electric field unit must be V/m")
    _require(units.get("charge_requires_unit") == "C", "charge unit must be C")
    _require(units.get("conductivity_requires_unit") == "S/m", "conductivity unit must be S/m")
    _require(units.get("pressure_requires_unit") == "Pa", "pressure unit must be Pa")
    _require(units.get("mass_requires_unit") == "kg", "mass unit must be kg")
    _require(
        units.get("pH_is_dimensionless_but_requires_sample_and_method") is True,
        "pH requires sample and method",
    )
    _require(
        units.get("energy_mass_charge_accounting_required") is True,
        "energy, mass and charge accounting required",
    )

    gates = set(data.get("promotion_gates", []))
    missing_gates = REQUIRED_GATES - gates
    _require(not missing_gates, f"promotion gates missing: {sorted(missing_gates)}")

    refs = data.get("references", [])
    _require(len(refs) >= 8, "at least eight references required")
    supported = {fid: 0 for fid in EXPECTED_FILAMENTS}
    for ref in refs:
        locator = str(ref.get("locator", ""))
        _require(
            locator.startswith("doi:") or locator.startswith("pmid:") or locator.startswith("http"),
            f"invalid reference locator: {locator}",
        )
        for filament_id in ref.get("supports", []):
            _require(filament_id in supported, f"reference supports unknown filament: {filament_id}")
            supported[filament_id] += 1

    _require(supported["water_spray_charge_ions"] >= 1, "spray charge filament requires external reference")
    _require(supported["skin_sweat_contact_electricity"] >= 1, "skin/sweat filament requires external reference")
    _require(supported["cardiac_electric_magnetic_pressure"] >= 1, "cardiac biomagnetism filament requires external reference")
    _require(supported["hair_static_point_geometry"] >= 1, "hair/static filament requires external reference")
    _require(supported["electrical_fault_lightning_safety"] >= 2, "safety filament requires at least two references")

    _require(
        data.get("current_state") == "BLOCKED_PENDING_LOCAL_MULTIPHYSICS_RECEIPT",
        "matrix must remain blocked pending local receipt",
    )
    _require(bool(data.get("next_gate")), "next_gate is required")

    return {
        "matrix_id": data["matrix_id"],
        "filaments": len(filaments),
        "edges": len(edge_list),
        "references": len(refs),
        "claim_allowed": False,
        "new_workflow_required": False,
        "status": "PASS",
        "strict": strict,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "matrix",
        nargs="?",
        default="data/manifests/rll_multiphysics_filament_matrix.v1.json",
    )
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument(
        "--report-path",
        default="data/results/rll_multiphysics_filament_validation.json",
    )
    args = parser.parse_args()

    try:
        data = load_matrix(Path(args.matrix))
        report = validate_matrix(data, strict=args.strict)
    except (OSError, json.JSONDecodeError, MatrixError) as exc:
        print(f"FAIL: {exc}")
        return 1

    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    if args.write_report:
        report_path = Path(args.report_path)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
