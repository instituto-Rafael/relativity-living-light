#!/usr/bin/env python3
"""Validate the RLL edge-science water chemistry/biology matrix with stdlib only."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


EXPECTED_IDS = [
    "catchment_source_context",
    "redox_geochemistry",
    "iron_manganese_mineralogy",
    "nitrogen_species_cycle",
    "microbiological_and_biofilm_state",
    "hydraulic_transport_and_seasonality",
    "magnetic_particle_response",
    "iron_manganese_treatment",
    "nitrate_nitrite_treatment",
    "zeolite_and_volcanic_media_identity",
    "exposure_and_toxicology",
    "analytical_measurement_and_qa_qc",
    "semantic_tokenization_and_context",
    "derivative_antiderivative_inverse_operators",
    "causal_graph_and_model_discrepancy",
    "multiscale_visualization",
    "edge_science_claim_gate",
    "receipt_and_longitudinal_feedback",
]

REQUIRED_GLOBAL_INVARIANTS = {
    "OBSERVABLE_IS_NOT_COMPOSITION",
    "COLOR_IS_NOT_MINERAL_IDENTIFICATION",
    "SOURCE_CONTEXT_IS_NOT_CONTAMINANT_CONCENTRATION",
    "EXTERNAL_EVIDENCE_IS_NOT_LOCAL_MEASUREMENT",
    "ABSENCE_IS_NOT_ZERO",
    "TREATMENT_MEDIA_NAME_IS_NOT_PERFORMANCE_PROOF",
}

REQUIRED_BLOCKS = {
    "catchment_source_context": {"FOREST_STREAM_IMPLIES_HIGH_NITRATE", "CLEAR_WATER_IMPLIES_SAFE"},
    "iron_manganese_mineralogy": {"RED_ORANGE_BIOFILM_EQUALS_HIGH_IRON", "BLACK_STAIN_EQUALS_MAGNETITE"},
    "nitrogen_species_cycle": {"TOTAL_NITROGEN_EQUALS_NITRATE", "NITRATE_IS_ALWAYS_FROM_FOREST", "NITRATE_IS_BIOACCUMULATIVE_IN_HUMANS"},
    "microbiological_and_biofilm_state": {"BOILING_REMOVES_NITRATE"},
    "magnetic_particle_response": {"WATER_DEFLECTION_PROVES_IRON", "ALL_RUST_IS_STRONGLY_MAGNETIC"},
    "nitrate_nitrite_treatment": {"CONVENTIONAL_SEDIMENT_FILTER_REMOVES_NITRATE", "BOILING_REMOVES_NITRATE"},
    "zeolite_and_volcanic_media_identity": {"WHITE_VOLCANIC_STONE_IS_ZEOLITE", "NATURAL_ZEOLITE_EFFECTIVELY_REMOVES_NITRATE_BY_DEFAULT"},
    "analytical_measurement_and_qa_qc": {"BELOW_DETECTION_EQUALS_ZERO", "TEST_STRIP_IS_LABORATORY_CONFIRMATION"},
    "semantic_tokenization_and_context": {"EMBEDDING_SIMILARITY_IS_CAUSALITY", "TOKEN_EQUALS_PHYSICAL_OBJECT"},
    "derivative_antiderivative_inverse_operators": {"DERIVATIVE_PROVES_CAUSE", "ANTIDERIVATIVE_RECOVERS_UNIQUE_ORIGIN_WITHOUT_BOUNDARY", "LOG_LOG_STRAIGHT_LINE_PROVES_POWER_LAW"},
    "edge_science_claim_gate": {"EDGE_SCIENCE_EXEMPTS_SAFETY_OR_METHOD", "LACK_OF_REFUTATION_EQUALS_PROOF"},
    "receipt_and_longitudinal_feedback": {"COMMIT_EQUALS_EXECUTION", "FAILED_TEST_IS_DELETED_AS_NOISE"},
}

REQUIRED_OPERATORS = {
    "DIRECT", "DERIVATIVE", "ANTIDERIVATIVE", "REVERSIVE",
    "RECIPROCAL", "LOG1P_ROUNDTRIP", "LOG_LOG", "NESTED_LOG_LOG",
}


class MatrixError(ValueError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise MatrixError(message)


def load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    _require(isinstance(value, dict), "root must be an object")
    return value


def validate(data: dict[str, Any]) -> dict[str, Any]:
    _require(data.get("schema_version") == "1.0", "schema_version must be 1.0")
    _require(data.get("matrix_id") == "rll-edge-science-water-chem-bio-v1", "matrix_id mismatch")
    _require(data.get("claim_allowed") is False, "claim_allowed must remain false")
    _require(data.get("training_allowed") is False, "training_allowed must remain false")
    _require(data.get("stdlib_only_validation") is True, "stdlib-only validation required")
    _require(data.get("new_workflow_required") is False, "no new workflow/YML may be required")

    token = data.get("token_contract", {})
    invariants = set(token.get("invariants", []))
    _require(REQUIRED_GLOBAL_INVARIANTS <= invariants, "token invariants incomplete")
    _require(len(token.get("required_fields", [])) >= 15, "typed token custody fields incomplete")
    _require("FALSIFIER" in token.get("semantic_roles", []), "FALSIFIER semantic role required")

    vector = data.get("state_vector", {})
    components = vector.get("components", [])
    ids = [item.get("id") for item in components]
    _require(len(ids) == len(set(ids)) and len(ids) >= 20, "state vector must contain >=20 unique components")
    for required in ("iron_total_mg_L", "nitrate_as_N_mg_L", "nitrite_as_N_mg_L", "e_coli_CFU_100mL", "redox_potential_V"):
        _require(required in ids, f"state vector missing {required}")
    _require(vector.get("validity_mask_required") is True, "validity mask required")
    _require(vector.get("uncertainty_required") is True, "uncertainty required")

    anchors = data.get("regulatory_anchors", {}).get("brazil_portaria_gm_ms_888_2021", {})
    _require(anchors.get("nitrate_as_N_mg_L_vmp") == 10.0, "Brazil nitrate VMP must be 10 mg/L as N")
    _require(anchors.get("nitrite_as_N_mg_L_vmp") == 1.0, "Brazil nitrite VMP must be 1 mg/L as N")
    _require(anchors.get("iron_mg_L_organoleptic_vmp") == 0.3, "Brazil iron organoleptic VMP must be 0.3 mg/L")
    _require("<=1" in anchors.get("combined_rule", ""), "combined nitrate/nitrite rule required")

    filaments = data.get("filaments")
    _require(isinstance(filaments, list), "filaments must be a list")
    actual_ids = [item.get("id") for item in filaments]
    _require(actual_ids == EXPECTED_IDS, f"filament order mismatch: {actual_ids!r}")
    _require([item.get("order") for item in filaments] == list(range(1, 19)), "orders must be 1..18")
    by_id = {item["id"]: item for item in filaments}
    for fid, required in REQUIRED_BLOCKS.items():
        blocks = set(by_id[fid].get("blocked_inferences", []))
        _require(required <= blocks, f"{fid}: missing blocked inferences {sorted(required-blocks)}")
    for item in filaments:
        for field in ("domain", "inputs", "outputs", "mechanism", "evidence_state", "local_measurement_state", "blocked_inferences"):
            _require(item.get(field), f"{item['id']}: {field} required")

    edges = data.get("cross_filament_edges", [])
    _require(isinstance(edges, list) and len(edges) >= 12, "at least 12 typed edges required")
    for edge in edges:
        _require(edge.get("from") in by_id and edge.get("to") in by_id, "edge endpoint unknown")
        _require(edge.get("from") != edge.get("to"), "self-edge requires separate explicit model")
        _require(edge.get("type") and edge.get("state"), "typed edge state required")
    candidate_edges = [e for e in edges if e.get("state") == "TOKEN_VAZIO_CAUSAL"]
    _require(len(candidate_edges) >= 2, "at least two causal gaps must remain explicit")

    operators = data.get("operator_contracts", {})
    _require(REQUIRED_OPERATORS == set(operators), "operator contract set mismatch")
    _require("boundary_condition" in operators["ANTIDERIVATIVE"]["requires"], "antiderivative boundary required")
    _require("competing_models" in operators["LOG_LOG"]["requires"], "log-log model competition required")
    _require(operators["RECIPROCAL"].get("on_zero") == "ABSTAIN_TOKEN_VAZIO_DOMAIN", "reciprocal zero abstention required")

    fals = data.get("falsifiability_contract", {})
    _require("falsifier" in fals.get("claim_required_fields", []), "claim falsifier required")
    rules = set(fals.get("frontier_science_rules", []))
    _require("MODEL_DISCREPANCY_IS_NOT_AUTOMATIC_NEW_PHYSICS" in rules, "model discrepancy guard required")
    _require("SAFETY_AND_ETHICS_OUTRANK_DISCOVERY_PRESSURE" in rules, "safety/ethics guard required")

    refs = data.get("references", [])
    _require(len(refs) >= 10, "at least ten references required")
    supported = {fid: 0 for fid in EXPECTED_IDS}
    for ref in refs:
        locator = str(ref.get("locator", ""))
        _require(locator.startswith(("http", "doi:", "internal:")), f"invalid locator {locator}")
        for fid in ref.get("supports", []):
            _require(fid in supported, f"reference supports unknown filament {fid}")
            supported[fid] += 1
    for fid in ("catchment_source_context", "redox_geochemistry", "nitrogen_species_cycle",
                "nitrate_nitrite_treatment", "zeolite_and_volcanic_media_identity",
                "exposure_and_toxicology", "analytical_measurement_and_qa_qc"):
        _require(supported[fid] >= 1, f"{fid} requires external support")

    _require(data.get("current_state") == "BLOCKED_PENDING_LOCAL_CERTIFIED_WATER_RECEIPT", "fail-closed current_state required")
    _require(bool(data.get("next_gate")), "next_gate required")
    return {
        "matrix_id": data["matrix_id"],
        "filaments": len(filaments),
        "edges": len(edges),
        "vector_components": len(components),
        "references": len(refs),
        "claim_allowed": False,
        "training_allowed": False,
        "new_workflow_required": False,
        "status": "PASS",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", nargs="?", default="data/manifests/rll_edge_science_water_chem_bio.v1.json")
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--report-path", default="data/results/rll_edge_science_water_validation.v1.json")
    args = parser.parse_args()
    try:
        report = validate(load(Path(args.manifest)))
    except (OSError, json.JSONDecodeError, MatrixError) as exc:
        print(f"FAIL: {exc}")
        return 1
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    if args.write_report:
        path = Path(args.report_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
