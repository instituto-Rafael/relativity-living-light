#!/usr/bin/env python3
"""Validate the canonical RLL environmental signal manifest with stdlib only."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

EXPECTED_MODULES = [
    "source_custody",
    "medium_state",
    "optical_transport",
    "cloud_phase_microphysics",
    "combustion_and_mineral_aerosol",
    "spray_electrification",
    "electrical_heating_shower",
    "human_acoustic_context",
    "detector_specific_background",
    "noise_classification",
    "reproduction_and_mechanism",
    "decision_and_claim_gate",
]

REQUIRED_DIESEL_COMPONENTS = {
    "ELEMENTAL_CARBON_SOOT",
    "ORGANIC_CARBON_AND_ADSORBED_ORGANICS",
    "CONDENSABLE_PARTICULATE_MATTER",
    "SULFATE_NITRATE",
    "ASH_AND_TRACE_METALS",
}

REQUIRED_GATES = {"SEMANTIC_MEANING", "REPRODUCTION", "MECHANISM"}


class ManifestError(ValueError):
    """Raised when a claim-boundary or structural invariant is violated."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ManifestError(message)


def validate_manifest(data: dict[str, Any], *, strict: bool = True) -> dict[str, Any]:
    _require(data.get("schema_version") == "1.0", "schema_version must be 1.0")
    _require(data.get("claim_allowed") is False, "top-level claim_allowed must be false")

    policy = data.get("orchestration_policy", {})
    _require(policy.get("yaml_role") == "ORDER_ONLY", "YML must remain order-only")
    _require(policy.get("shell_role") == "TYPED_MODULE_INVOCATION", "shell role mismatch")
    _require(
        policy.get("semantic_authority") == "MANIFEST_AND_MODULE_CONTRACTS",
        "semantic authority must remain in manifest/module contracts",
    )
    _require(
        policy.get("no_new_workflow_required") is True,
        "manifest must not require a new workflow",
    )

    modules = data.get("modules")
    _require(isinstance(modules, list), "modules must be a list")
    actual_ids = [module.get("id") for module in modules]
    _require(actual_ids == EXPECTED_MODULES, f"module order mismatch: {actual_ids!r}")
    _require(
        [module.get("order") for module in modules] == list(range(1, 13)),
        "module order numbers must be 1..12",
    )
    _require(len(actual_ids) == len(set(actual_ids)), "module IDs must be unique")
    for module in modules:
        _require(
            module.get("claim_allowed") is False,
            f"{module.get('id')}: claim_allowed must be false",
        )
        _require(bool(module.get("responsibility")), f"{module.get('id')}: responsibility is required")
        _require(bool(module.get("inputs")), f"{module.get('id')}: inputs are required")
        _require(bool(module.get("outputs")), f"{module.get('id')}: outputs are required")

    facts = data.get("physical_facts", {})

    diesel = facts.get("diesel_exhaust", {})
    _require(
        diesel.get("phase_model") == "MIXED_PHASE_AEROSOL",
        "diesel phase must be mixed aerosol",
    )
    _require(
        diesel.get("solid_carbonaceous_core") is True,
        "solid carbonaceous core must be preserved",
    )
    _require(
        diesel.get("solid_only") is False,
        "diesel particulate matter must not be declared solid-only",
    )
    components = set(diesel.get("components", []))
    missing = REQUIRED_DIESEL_COMPONENTS - components
    _require(not missing, f"diesel components missing: {sorted(missing)}")

    shower = facts.get("electric_shower", {})
    _require(
        shower.get("primary_heating_mechanism") == "JOULE_HEATING",
        "shower heating must be Joule heating",
    )
    _require(
        shower.get("resistance_directly_ionizes_surroundings") is False,
        "resistance ionization claim must remain false",
    )
    _require(
        shower.get("spray_electrification_candidate") is True,
        "spray electrification candidate missing",
    )
    _require(
        shower.get("local_ion_measurement_state") == "TOKEN_VAZIO_LOCAL_MEASUREMENT",
        "local ion measurement must remain TOKEN_VAZIO until measured",
    )

    singing = facts.get("singing_context", {})
    _require(
        singing.get("ionization_causes_singing") is False,
        "ionization must not be claimed to cause singing",
    )
    supported = set(singing.get("supported_route", []))
    _require(
        "ROOM_ACOUSTIC_REFLECTION_AND_REVERBERATION" in supported,
        "room acoustics route missing",
    )
    _require("PERCEIVED_VOCAL_SUPPORT" in supported, "vocal support route missing")

    icecube = facts.get("icecube_background", {})
    _require(
        icecube.get("detection_medium") == "ANTARCTIC_ICE_CHERENKOV",
        "IceCube medium mismatch",
    )
    _require(
        icecube.get("optical_refraction_equivalent") is False,
        "IceCube must not be reduced to telescope refraction",
    )
    _require(
        {"ATMOSPHERIC_MUONS", "ATMOSPHERIC_NEUTRINOS"}.issubset(
            set(icecube.get("atmospheric_backgrounds", []))
        ),
        "IceCube atmospheric backgrounds incomplete",
    )

    decision = data.get("decision_policy", {})
    _require(
        set(decision.get("required_gates", [])) == REQUIRED_GATES,
        "three decision gates are mandatory",
    )
    _require(decision.get("promotion_allowed") is False, "promotion must remain blocked")
    _require(
        decision.get("current_state") == "BLOCKED_PENDING_REPRODUCTION_AND_MECHANISM",
        "current state must remain blocked",
    )

    refs = data.get("references", [])
    _require(len(refs) >= 5, "at least five references are required")
    for ref in refs:
        locator = str(ref.get("locator", ""))
        _require(
            locator.startswith("http") or locator.startswith("doi:"),
            f"invalid reference locator: {locator}",
        )

    _require(bool(data.get("next_gate")), "next_gate is required")

    return {
        "manifest_id": data.get("manifest_id"),
        "modules": len(modules),
        "references": len(refs),
        "claim_allowed": False,
        "promotion_allowed": False,
        "status": "PASS",
        "strict": strict,
    }


def load_manifest(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ManifestError("manifest root must be an object")
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "manifest",
        nargs="?",
        default="data/manifests/rll_environmental_signal_manifest.v1.json",
    )
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument(
        "--report-path",
        default="data/results/rll_environmental_signal_validation.json",
    )
    args = parser.parse_args()

    try:
        data = load_manifest(Path(args.manifest))
        report = validate_manifest(data, strict=args.strict)
    except (OSError, json.JSONDecodeError, ManifestError) as exc:
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
