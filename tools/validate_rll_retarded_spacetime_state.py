#!/usr/bin/env python3
"""Structural validator for rll.retarded_spacetime_state.v1.

PASS here validates the contract shape and epistemic boundaries only.
It does not validate a cosmological or plasma-physics claim.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

DEFAULT = Path("data/contracts/rll_retarded_spacetime_state.v1.yml")

REQUIRED_TOP = {
    "schema", "claim_allowed", "semantic_boundaries", "invariants",
    "global_parameters", "event_state", "time_geometry", "signal_path",
    "matter_worldline", "foreground_segments", "arrival_time_budget",
    "redshift_budget", "plasma_and_gravity", "observation_model",
    "uncertainty", "geometry_relational_layer", "falsification",
    "validation_plan", "R3",
}

REQUIRED_INVARIANTS = {
    "SOURCE != ARTEFACT != EXECUTION != EVIDENCE != CLAIM",
    "TOKEN_VAZIO != 0",
    "OBSERVATION_EVENT != PRESENT_SOURCE_STATE",
    "NULL_SIGNAL_PATH != TIMELIKE_MATTER_WORLDLINE",
    "GLOBAL_COSMOLOGICAL_PARAMETER != POST_HOC_PER_POINT_PARAMETER",
    "VACUUM_LOCAL_C_IS_INVARIANT",
    "NO_PATH_EFFECT_DOUBLE_COUNTING",
}


def validate_contract(data: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    missing = sorted(REQUIRED_TOP - set(data))
    if missing:
        errors.append(f"missing top-level keys: {missing}")

    if data.get("schema") != "rll.retarded_spacetime_state.v1":
        errors.append("schema mismatch")
    if data.get("claim_allowed") is not False:
        errors.append("claim_allowed must remain false")
    if data.get("scientific_confirmation") is not False:
        errors.append("scientific_confirmation must remain false")

    invariants = set(data.get("invariants", []))
    if not REQUIRED_INVARIANTS <= invariants:
        errors.append("required epistemic/relativistic invariants missing")

    if data.get("global_parameters", {}).get("per_point_post_hoc_allowed") is not False:
        errors.append("per-point post-hoc cosmological fitting must remain blocked")

    sem = data.get("semantic_boundaries", {})
    if not str(sem.get("syntropy", "")).startswith("TOKEN_VAZIO"):
        errors.append("physical syntropy must remain TOKEN_VAZIO until operationally defined")

    pg = data.get("plasma_and_gravity", {})
    if pg.get("no_new_force_claim") is not True:
        errors.append("plasma gravity boundary must not imply a new force")
    if pg.get("strong_gravity_plasma_state") != "ROUTED_SEPARATE_AUTHORITY":
        errors.append("strong-gravity plasma must stay under separate authority")

    if data.get("geometry_relational_layer", {}).get("physical_metric_claim") is not False:
        errors.append("relational geometry must not be promoted to physical cosmic metric")

    plan = data.get("validation_plan", [])
    states = {x.get("id"): x.get("state") for x in plan if isinstance(x, dict)}
    if states.get("V7_CLAIM_GATE") != "BLOCKED":
        errors.append("claim gate must remain BLOCKED")
    for gate in ("V1_SYNTHETIC_LIGHTCONE", "V2_DYNAMIC_FOREGROUND",
                 "V3_LENS_TIME_DELAY", "V4_PLASMA_PROPAGATION",
                 "V5_REAL_DATA_ABLATION", "V6_CROSS_SURVEY_REPRODUCTION"):
        if not str(states.get(gate, "")).startswith("TOKEN_VAZIO"):
            errors.append(f"{gate} must remain TOKEN_VAZIO before execution")

    return {
        "schema": "rll.retarded_spacetime_state.validation.v1",
        "valid": not errors,
        "claim_allowed": False,
        "errors": errors,
        "boundary": "STRUCTURAL_PASS != SCIENTIFIC_CONFIRMATION",
        "checked_validation_states": states,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, default=DEFAULT)
    args = parser.parse_args()

    data = yaml.safe_load(args.contract.read_text(encoding="utf-8"))
    result = validate_contract(data)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
