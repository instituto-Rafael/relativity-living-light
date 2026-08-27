#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CLOSURE = ROOT / "data/registries/rll_mpemba_horizon_closure_registry.v1.json"
DEFAULT_MANIFEST = ROOT / "data/real/strong_gravity/eht_2026_d01_01_manifest.json"
DEFAULT_PROTOCOL = ROOT / "data/contracts/eht_mpemba_observational_protocol.v1.json"
DEFAULT_BASE_CONTRACT = ROOT / "data/contracts/mpemba_horizon_falsifier.v1.json"
DEFAULT_SOURCE_REGISTRY = ROOT / "data/registries/rll_recent_primary_sources_2026.json"

REQUIRED_ITEM_KEYS = {
    "id",
    "priority",
    "urgency",
    "domain",
    "state",
    "attention_state",
    "owner_class",
    "provenance",
    "known",
    "blocker",
    "mechanism",
    "deliverable",
    "verification",
    "falsifier",
    "close_when",
    "claim_boundary",
}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path}: root must be an object")
    return value


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate_closure(closure: dict[str, Any]) -> None:
    require(closure.get("no_untracked_gaps") is True, "closure must declare no_untracked_gaps=true")
    require(closure.get("global_scientific_claim_allowed") is False, "global claim must remain fail-closed")
    items = closure.get("items")
    require(isinstance(items, list) and items, "closure items must be a non-empty list")

    ids: list[str] = []
    priorities: Counter[str] = Counter()
    for item in items:
        require(isinstance(item, dict), "every closure item must be an object")
        missing = REQUIRED_ITEM_KEYS - item.keys()
        require(not missing, f"{item.get('id', '<unknown>')}: missing keys {sorted(missing)}")
        require(isinstance(item["id"], str) and item["id"], "closure item id must be non-empty")
        require(item["priority"] in {"P0", "P1", "P2", "P3"}, f"{item['id']}: invalid priority")
        require(isinstance(item["urgency"], str) and item["urgency"], f"{item['id']}: urgency required")
        require(isinstance(item["owner_class"], str) and item["owner_class"], f"{item['id']}: owner_class required")
        require(isinstance(item["provenance"], list) and item["provenance"], f"{item['id']}: provenance required")
        require(isinstance(item["close_when"], list) and item["close_when"], f"{item['id']}: close_when required")
        require(isinstance(item["falsifier"], str) and item["falsifier"], f"{item['id']}: falsifier required")
        ids.append(item["id"])
        priorities[item["priority"]] += 1

    require(len(ids) == len(set(ids)), "closure item ids must be unique")
    summary = closure.get("priority_summary", {})
    for priority in ("P0", "P1", "P2", "P3"):
        expected = summary.get(priority, 0)
        require(priorities.get(priority, 0) == expected, f"priority summary mismatch for {priority}")
    require(summary.get("untracked") == 0, "untracked gap count must be zero")

    closure_state = closure.get("closure_state", {})
    require(closure_state.get("operational_tracking_complete") is True, "operational tracking must be complete")
    require(closure_state.get("astrophysical_mpemba_claim_state") == "TOKEN_VAZIO", "BH-MP-06 must remain TOKEN_VAZIO")
    require(closure_state.get("hawking_thermometry_claim_state") == "TOKEN_VAZIO", "BH-MP-08 must remain TOKEN_VAZIO")
    require(closure_state.get("global_scientific_claim_allowed") is False, "closure state must remain fail-closed")


def validate_manifest(manifest: dict[str, Any]) -> None:
    product = manifest.get("product", {})
    require(product.get("code") == "2026-D01-01", "unexpected EHT product code")
    require(product.get("title") == "2018 and 2021 Calibrated polarimetric data", "unexpected EHT product title")
    require(product.get("official_last_updated") == "2026-06-29", "unexpected EHT catalog date")
    require(product.get("reference_doi") == "10.1051/0004-6361/202555855", "unexpected EHT reference DOI")

    source = manifest.get("source_verification", {})
    require(source.get("catalog_metadata_verified") is True, "official catalog metadata must be verified")
    require(source.get("distribution_browser_location_verified") is True, "distribution browser location must be verified")

    custody = manifest.get("custody", {})
    if custody.get("bytes_materialized_into_rll_execution_environment") is False:
        require(custody.get("sha256_verified") is False, "cannot verify SHA256 without materialized bytes")
        require(custody.get("file_inventory_verified") is False, "cannot verify file inventory without materialization")
        require(custody.get("file_inventory") == [], "unmaterialized manifest must not invent file inventory")
        require(custody.get("state") == "BLOCKED_EXTERNAL_BYTE_ACCESS", "unmaterialized state must remain explicit")

    require(manifest.get("materialization_contract", {}).get("promotion_allowed_without_success") is False, "custody promotion must fail closed")
    require(manifest.get("claim_allowed") is False, "data manifest cannot enable scientific claim")


def validate_protocol(protocol: dict[str, Any]) -> None:
    existing = protocol.get("existing_public_data_scope", {})
    require(existing.get("analysis_class") == "RETROSPECTIVE_BOUNDED_VARIABILITY_ONLY", "existing public data must remain retrospective")
    require(existing.get("prospective_preregistration") is False, "published outcomes cannot be labelled prospective preregistration")

    future = protocol.get("future_candidate_design", {})
    required = set(future.get("required_data_properties", []))
    require("two or more physically comparable relaxation trajectories" in required, "matched relaxation trajectories are required")
    require("measurement uncertainties and calibration/systematics model" in required, "uncertainty model is required")
    require("immutable file-level custody with SHA256" in required, "SHA256 custody is required")
    require("internal CI and same-author reruns are reproducibility only" in future.get("independent_replication_rule", ""), "independence boundary missing")

    decision = protocol.get("current_decision", {})
    require(decision.get("EHT_2026_D01_01_is_sufficient_for_BH_MP_06") is False, "2026-D01-01 must not be auto-promoted to Mpemba evidence")
    require(decision.get("BH_MP_06") == "TOKEN_VAZIO", "BH-MP-06 must remain TOKEN_VAZIO")
    require(decision.get("BH_MP_08") == "TOKEN_VAZIO", "BH-MP-08 must remain TOKEN_VAZIO")
    require(protocol.get("global_scientific_claim_allowed") is False, "protocol must remain fail-closed")


def validate_base_contract(contract: dict[str, Any]) -> None:
    ledger = {item["id"]: item["state"] for item in contract.get("claim_ledger", [])}
    require(ledger.get("BH-MP-06") == "TOKEN_VAZIO", "base contract BH-MP-06 regression")
    require(ledger.get("BH-MP-08") == "TOKEN_VAZIO", "base contract BH-MP-08 regression")
    require(contract.get("global_scientific_claim_allowed") is False, "base contract claim gate regression")


def validate_source_registry(registry: dict[str, Any]) -> None:
    sources = {item.get("source_id"): item for item in registry.get("sources", [])}
    eht = sources.get("EHT-2026-D01-01")
    require(isinstance(eht, dict), "canonical source registry must retain EHT-2026-D01-01")
    require(eht.get("verification_status") == "metadata_verified", "EHT source must remain metadata_verified until custody closes")
    safe_use = eht.get("safe_use", "")
    require("SHA256" in safe_use and "TOKEN_VAZIO" in safe_use, "EHT source safe_use must preserve checksum boundary")
    require(registry.get("claim_allowed") is False, "source registry claim gate regression")


def validate_all(
    closure_path: Path = DEFAULT_CLOSURE,
    manifest_path: Path = DEFAULT_MANIFEST,
    protocol_path: Path = DEFAULT_PROTOCOL,
    base_contract_path: Path = DEFAULT_BASE_CONTRACT,
    source_registry_path: Path = DEFAULT_SOURCE_REGISTRY,
) -> dict[str, Any]:
    closure = load_json(closure_path)
    manifest = load_json(manifest_path)
    protocol = load_json(protocol_path)
    contract = load_json(base_contract_path)
    source_registry = load_json(source_registry_path)

    validate_closure(closure)
    validate_manifest(manifest)
    validate_protocol(protocol)
    validate_base_contract(contract)
    validate_source_registry(source_registry)

    return {
        "status": "PASS",
        "no_untracked_gaps": True,
        "closure_items": len(closure["items"]),
        "astrophysical_mpemba_claim_state": "TOKEN_VAZIO",
        "hawking_thermometry_claim_state": "TOKEN_VAZIO",
        "global_scientific_claim_allowed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate B10/C11 Mpemba-horizon operational closure")
    parser.add_argument("--closure", type=Path, default=DEFAULT_CLOSURE)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--protocol", type=Path, default=DEFAULT_PROTOCOL)
    args = parser.parse_args()
    result = validate_all(args.closure, args.manifest, args.protocol)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
