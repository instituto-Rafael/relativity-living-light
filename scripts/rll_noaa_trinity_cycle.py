#!/usr/bin/env python3
"""NOAA -> RLL Trinity633 custody/orchestration cycle.

Observation/provenance bridge only. Network access is opt-in and constrained by
an explicit zero-trust/privacy contract. No physical ΔOBS, causal residual,
statistical independence or scientific claim is inferred here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_CONTRACT = Path("data/contracts/rll_noaa_trinity_633.v1.json")
DEFAULT_GOVERNANCE = Path("data/governance/rll_noaa_trinity633_data_governance.v1.json")
DEFAULT_SOURCE_REGISTRY = Path("data/climate/rll_climate_source_registry.v1.json")

SCHEDULE_TO_PHASE = {
    "17 0,12 * * *": "LUX_6H",
    "17 6,18 * * *": "SPIRITUM_3H",
    "17 9,21 * * *": "VERBUM_3H",
}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_phase(requested: str, schedule_expression: str) -> str:
    if requested != "auto":
        return requested
    if schedule_expression in SCHEDULE_TO_PHASE:
        return SCHEDULE_TO_PHASE[schedule_expression]
    hour = datetime.now(timezone.utc).hour
    if hour in {0, 12}:
        return "LUX_6H"
    if hour in {6, 18}:
        return "SPIRITUM_3H"
    if hour in {9, 21}:
        return "VERBUM_3H"
    return "LUX_6H"


def phase_spec(contract: dict[str, Any], phase: str) -> dict[str, Any]:
    for item in contract["phases"]:
        if item["id"] == phase:
            return item
    raise ValueError(f"unknown phase {phase}")


def validate_source_bindings(
    contract: dict[str, Any],
    registry: dict[str, Any],
    governance: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    if governance is None:
        governance = load_json(DEFAULT_GOVERNANCE)

    allowlist = governance["allowed_sources"]
    contract_ids = [item["id"] for item in contract["sources"]]
    if contract_ids != allowlist:
        raise ValueError("Trinity contract sources must exactly match zero-trust allowlist")

    by_id = {item["id"]: item for item in registry["sources"]}
    content_marker = str(governance["network"]["required_content_type_contains"]).lower()
    bound = []
    for declared in contract["sources"]:
        source_id = declared["id"]
        if source_id not in by_id:
            raise ValueError(f"Trinity source missing from climate registry: {source_id}")
        source = by_id[source_id]
        if source.get("authority") != "NOAA_SWPC":
            raise ValueError(f"Trinity source authority must be NOAA_SWPC: {source_id}")
        if source.get("access") != "PUBLIC_GET":
            raise ValueError(f"Trinity source must be non-parameterized PUBLIC_GET: {source_id}")
        if source.get("fetch_by_default") is not False:
            raise ValueError(f"Trinity source must remain opt-in: {source_id}")

        url = str(source.get("sample_url", ""))
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme != "https":
            raise ValueError(f"Trinity source is not HTTPS: {source_id}")
        if parsed.hostname != source.get("domain"):
            raise ValueError(f"Trinity source hostname/domain mismatch: {source_id}")
        if parsed.username or parsed.password:
            raise ValueError(f"Trinity source URL userinfo is forbidden: {source_id}")
        if parsed.port is not None:
            raise ValueError(f"Trinity source custom port is forbidden: {source_id}")
        if parsed.query:
            raise ValueError(f"Trinity source query parameters are forbidden: {source_id}")
        if parsed.fragment:
            raise ValueError(f"Trinity source URL fragment is forbidden: {source_id}")
        expected_path = governance.get("allowed_routes", {}).get(source_id)
        if not expected_path or parsed.path != expected_path:
            raise ValueError(f"Trinity source path is not exact-governance allowlisted: {source_id}")

        bound.append({
            "id": source_id,
            "measurement_family": declared["measurement_family"],
            "authority": source["authority"],
            "domain": source["domain"],
            "url": url,
            "required_content_type_contains": content_marker,
        })
    return bound


def run_fetch(
    source_id: str,
    output_dir: Path,
    execute_network: bool,
    timeout_seconds: float,
    max_bytes: int,
) -> dict[str, Any]:
    command = [
        sys.executable,
        "scripts/fetch_rll_climate_sources.py",
        "--source",
        source_id,
        "--output-dir",
        str(output_dir),
        "--timeout",
        str(timeout_seconds),
        "--max-bytes",
        str(max_bytes),
    ]
    if execute_network:
        command.append("--execute")
    completed = subprocess.run(command, text=True, capture_output=True, check=False)
    try:
        payload: dict[str, Any] = json.loads(completed.stdout)
    except json.JSONDecodeError:
        payload = {
            "status": "FAIL",
            "error": "FETCHER_OUTPUT_NOT_JSON",
            "stdout_tail": completed.stdout[-2000:],
        }
    payload["returncode"] = completed.returncode
    payload["stderr_tail"] = completed.stderr[-2000:]
    return payload



def validate_payload_shape(path: Path, source_id: str, governance: dict[str, Any]) -> tuple[bool, str]:
    """Validate structural source shape only; no physical semantics are inferred."""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return False, "PAYLOAD_JSON_INVALID"

    shape = governance.get("payload_shapes", {}).get(source_id)
    if not shape:
        return False, "TOKEN_VAZIO_PAYLOAD_SHAPE_CONTRACT"

    if shape.get("top_level") == "list":
        if not isinstance(payload, list) or not payload:
            return False, "PAYLOAD_TOP_LEVEL_LIST_REQUIRED"
        if shape.get("record_type") == "object" and not all(isinstance(item, dict) for item in payload):
            return False, "PAYLOAD_RECORD_OBJECT_REQUIRED"
        required = shape.get("required_keys", [])
        if not all(all(key in item for key in required) for item in payload if isinstance(item, dict)):
            return False, "PAYLOAD_REQUIRED_KEY_MISSING"
        return True, "STRUCTURAL_SCHEMA_PASS"

    if shape.get("top_level") == "object":
        if not isinstance(payload, dict):
            return False, "PAYLOAD_TOP_LEVEL_OBJECT_REQUIRED"
        for key in shape.get("required_keys", []):
            if key not in payload:
                return False, "PAYLOAD_REQUIRED_KEY_MISSING"
        if shape.get("type_value") is not None and payload.get("type") != shape["type_value"]:
            return False, "PAYLOAD_TYPE_VALUE_MISMATCH"
        if shape.get("features_type") == "list" and not isinstance(payload.get("features"), list):
            return False, "PAYLOAD_FEATURES_LIST_REQUIRED"
        return True, "STRUCTURAL_SCHEMA_PASS"

    return False, "TOKEN_VAZIO_PAYLOAD_SHAPE_MODE"


def source_custody_ok(result: dict[str, Any], source: dict[str, Any], governance: dict[str, Any]) -> bool:
    if result.get("returncode") != 0:
        return False
    if result.get("status") not in governance["network"]["accepted_http_status"]:
        return False
    if not isinstance(result.get("sha256"), str) or len(result["sha256"]) != 64:
        return False
    if int(result.get("bytes", 0)) <= 0:
        return False
    marker = source["required_content_type_contains"]
    if marker not in str(result.get("content_type", "")).lower():
        return False
    saved_path = result.get("saved_path")
    if not isinstance(saved_path, str) or not saved_path:
        return False
    schema_ok, _ = validate_payload_shape(Path(saved_path), source["id"], governance)
    return schema_ok


def build_receipt(
    contract: dict[str, Any],
    registry: dict[str, Any],
    phase: str,
    output_dir: Path,
    execute_network: bool,
    governance: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if governance is None:
        governance = load_json(DEFAULT_GOVERNANCE)

    spec = phase_spec(contract, phase)
    bound_sources = validate_source_bindings(contract, registry, governance)
    source_dir = output_dir / "sources"
    source_dir.mkdir(parents=True, exist_ok=True)

    timeout_seconds = float(governance["network"]["timeout_seconds"])
    max_bytes = int(governance["network"]["max_bytes_per_source"])

    observations = []
    success_families: set[str] = set()
    for source in bound_sources:
        result = run_fetch(source["id"], source_dir, execute_network, timeout_seconds, max_bytes)
        schema_ok = False
        schema_state = "DRY_RUN"
        if execute_network and isinstance(result.get("saved_path"), str):
            schema_ok, schema_state = validate_payload_shape(Path(result["saved_path"]), source["id"], governance)
        executed_ok = bool(execute_network and source_custody_ok(result, source, governance))
        if executed_ok:
            success_families.add(source["measurement_family"])
        observations.append({
            **source,
            "execution": result,
            "custody_observed": executed_ok,
            "personal_data_expected": False,
            "credential_required": False,
            "payload_structural_schema_ok": schema_ok,
            "payload_structural_schema_state": schema_state,
        })

    if not execute_network:
        gate_status = "DRY_RUN"
    elif len(success_families) == len(bound_sources):
        gate_status = "SOURCE_CUSTODY_COMPLETE"
    elif success_families:
        gate_status = "SOURCE_CUSTODY_PARTIAL"
    else:
        gate_status = "SOURCE_CUSTODY_UNAVAILABLE"

    boundary = contract["epistemic_boundary"]
    return {
        "schema": "rll.noaa.trinity633.receipt.v2",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "phase": phase,
        "cycle_hours": contract["cycle_hours"],
        "state_transition": {
            "from": spec["state_from"],
            "via": spec.get("state_via"),
            "to": spec["state_to"],
        },
        "actions": spec["actions"],
        "network_execution_requested": execute_network,
        "gate_status": gate_status,
        "zero_trust": {
            "deny_by_default": True,
            "source_allowlist_enforced": True,
            "exact_hostname_enforced": True,
            "https_enforced": True,
            "query_parameters_forbidden": True,
            "repository_credentials_used": False,
            "arbitrary_url_input_allowed": False,
            "exact_path_allowlist_enforced": True,
            "infrastructure_egress_firewall_verified": False,
            "infrastructure_egress_state": governance["zero_trust"]["infrastructure_egress_state"],
        },
        "supply_chain": {
            "runner_image": governance["supply_chain"]["runner_image"],
            "dependency_lock_verified": False,
            "dependency_lock_state": governance["supply_chain"]["dependency_lock_state"],
            "package_hashes_verified": False,
            "package_hash_state": governance["supply_chain"]["package_hash_state"],
        },
        "privacy": {
            "data_classification": governance["privacy"]["data_classification"],
            "personal_data_expected": False,
            "user_or_device_identifiers_allowed": False,
            "precise_person_location_allowed": False,
            "behavioral_profiling_allowed": False,
            "compliance_claim": False,
        },
        "runtime_context": {
            "github_sha": os.environ.get("GITHUB_SHA", "TOKEN_VAZIO_GITHUB_SHA"),
            "github_run_id": os.environ.get("GITHUB_RUN_ID", "TOKEN_VAZIO_GITHUB_RUN_ID"),
            "github_run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT", "TOKEN_VAZIO_GITHUB_RUN_ATTEMPT"),
        },
        "sources_declared": len(bound_sources),
        "measurement_families_declared": sorted({x["measurement_family"] for x in bound_sources}),
        "measurement_families_with_custody": sorted(success_families),
        "cross_domain_readiness": len(success_families) >= 3,
        "cross_domain_readiness_semantics": "availability/custody gate only; not a physical correlation result",
        "observed_cross_domain": False,
        "numeric_residual": boundary["numeric_residual_default"],
        "cause": boundary["cause_default"],
        "statistical_independence_established": False,
        "claim_allowed": False,
        "observations": observations,
        "F_ok": (
            f"{len(success_families)} NOAA measurement-family custody paths observed"
            if execute_network
            else "Trinity633 action plan resolved without network execution"
        ),
        "F_gap": "infrastructure egress enforcement, dependency lock/hashes, payload semantic fields, physical ΔOBS, temporal correlation, statistical independence and numeric residual remain TOKEN_VAZIO",
        "F_next": "hydrate timestamped NOAA variables into typed 6h baseline -> 3h challenge -> 3h feedback windows with preregistered uncertainty gates",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT))
    parser.add_argument("--governance", default=str(DEFAULT_GOVERNANCE))
    parser.add_argument("--source-registry", default=str(DEFAULT_SOURCE_REGISTRY))
    parser.add_argument("--phase", choices=["auto", "LUX_6H", "SPIRITUM_3H", "VERBUM_3H"], default="auto")
    parser.add_argument("--schedule-expression", default="")
    parser.add_argument("--output-dir", default="artifacts/rll-real-run/noaa-trinity633")
    parser.add_argument("--execute-network", action="store_true")
    args = parser.parse_args()

    paths = {
        "contract": Path(args.contract),
        "governance": Path(args.governance),
        "source_registry": Path(args.source_registry),
    }
    try:
        contract = load_json(paths["contract"])
        governance = load_json(paths["governance"])
        registry = load_json(paths["source_registry"])
        phase = resolve_phase(args.phase, args.schedule_expression)
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        receipt = build_receipt(contract, registry, phase, output_dir, args.execute_network, governance)
        receipt["contract_sha256"] = {name: sha256_file(path) for name, path in paths.items()}
        receipt_path = output_dir / "TRINITY633_RECEIPT.json"
        receipt_path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(json.dumps(receipt, indent=2, ensure_ascii=False))
        # External availability is a typed observation state, not an executor
        # failure. Contract, policy and internal execution errors remain fail-closed.
        return 0
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({
            "schema": "rll.noaa.trinity633.receipt.v2",
            "status": "FAIL",
            "error": str(exc),
            "claim_allowed": False,
            "compliance_claim": False,
        }, indent=2, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
