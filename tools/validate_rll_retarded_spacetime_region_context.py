#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

DEFAULT = Path("data/contracts/rll_retarded_spacetime_region_context.v1.yaml")

REQ_INV = {
    "SOURCE != ARTEFACT != EXECUTION != EVIDENCE != CLAIM",
    "TOKEN_VAZIO != 0",
    "SIGNAL_NULL_PATH != MATTER_TIMELIKE_PATH",
    "OBSERVED_EMISSION_STATE != CURRENT_MATTER_STATE_INFERENCE",
    "CAUSAL_FUTURE_EVENT_CANNOT_AFFECT_ALREADY_PASSED_PHOTON_SEGMENT",
    "GLOBAL_COSMOLOGY_PARAMETERS_NOT_CHOSEN_POST_HOC_PER_DATUM",
    "DIMENSIONAL_CONSISTENCY_REQUIRED",
    "PLASMA_GRAVITY_IS_NOT_A_SEPARATE_FORCE_WITHOUT_AN_EXPLICIT_TESTABLE_MODEL",
}

REQ_SEGMENT_GROUPS = {
    "epoch_geometry",
    "spacetime_motion",
    "relativistic_gravity",
    "plasma_mhd",
    "matter_environment",
    "evidence_fields",
}


def req(ok: bool, message: str, errors: list[str]) -> None:
    if not ok:
        errors.append(message)


def validate_contract(data: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []

    req(
        data.get("schema") == "rll.retarded_spacetime_region_context.v1",
        "schema mismatch",
        errors,
    )
    parent = data.get("canonical_parent", {})
    req(
        parent.get("path") == "data/contracts/rll_retarded_spacetime_state.v1.yml",
        "canonical parent mismatch",
        errors,
    )
    req(
        parent.get("duplicate_authority_forbidden") is True,
        "region context must remain an extension, not a competing authority",
        errors,
    )
    req(data.get("claim_allowed") is False, "claim_allowed must remain false", errors)
    req(
        data.get("scientific_confirmation") is False,
        "scientific_confirmation must remain false",
        errors,
    )

    req(
        REQ_INV <= set(data.get("core_invariants", [])),
        "required invariants missing",
        errors,
    )

    current_state = data.get("observation_state", {}).get("current_state_inference", {})
    req(
        current_state.get("direct_observation") is False,
        "current state must not be marked direct observation",
        errors,
    )

    region = data.get("region_path_model", {})
    req(
        region.get("representation") == "ordered_segments_on_null_path",
        "region path must be ordered null-path segments",
        errors,
    )
    req(
        REQ_SEGMENT_GROUPS <= set(region.get("segment_fields", {})),
        "required segment groups missing",
        errors,
    )

    theta = data.get("parameter_model", {}).get("global_theta", {})
    req(
        theta.get("post_hoc_per_datum_adaptation_allowed") is False,
        "post-hoc per-datum global parameter adaptation must be blocked",
        errors,
    )

    unresolved = data.get("physics_boundary", {}).get("unresolved", {})
    req(
        unresolved.get("physical_syntropy") == "TOKEN_VAZIO",
        "physical syntropy must remain TOKEN_VAZIO",
        errors,
    )

    plasma_blocked = set(
        data.get("physics_boundary", {})
        .get("plasma_components", {})
        .get("blocked_claims", [])
    )
    req(
        "plasma_gravity_as_new_fundamental_force" in plasma_blocked,
        "new plasma-gravity force claim must be blocked",
        errors,
    )

    stats = data.get("statistics", {})
    req(len(stats.get("S7_observation", [])) == 7, "S7_observation must have 7 entries", errors)
    req(len(stats.get("S7_model", [])) == 7, "S7_model must have 7 entries", errors)

    falsifiers = data.get("falsifiers", [])
    req(len(falsifiers) >= 7, "at least seven falsifiers required", errors)

    req(
        data.get("gates", {}).get("scientific_claim") == "BLOCKED",
        "scientific claim must be BLOCKED",
        errors,
    )

    return {
        "schema": "rll.retarded_spacetime_region_context.validation.v1",
        "valid": not errors,
        "claim_allowed": False,
        "scientific_confirmation": False,
        "errors": errors,
        "falsifiers": len(falsifiers),
        "boundary": "STRUCTURAL_PASS != SCIENTIFIC_CONFIRMATION",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, default=DEFAULT)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    data = yaml.safe_load(args.contract.read_text(encoding="utf-8"))
    result = validate_contract(data)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
