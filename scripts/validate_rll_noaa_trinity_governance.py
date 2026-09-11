#!/usr/bin/env python3
"""Fail-closed governance validator for NOAA -> RLL Trinity633.

This validates only repository-local contracts and workflow controls. It does not
certify legal compliance, source truth, or scientific validity.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import urllib.parse
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate(
    contract: dict[str, Any],
    governance: dict[str, Any],
    source_registry: dict[str, Any],
    workflow_text: str,
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    if governance.get("claim_allowed") is not False:
        errors.append("governance claim_allowed must be false")
    if governance.get("compliance_claim") is not False:
        errors.append("compliance_claim must be false")

    zero = governance.get("zero_trust", {})
    required_false = [
        "arbitrary_url_allowed",
        "url_userinfo_allowed",
        "url_query_allowed",
        "url_fragment_allowed",
        "custom_port_allowed",
        "redirect_cross_hostname_allowed",
        "repository_credentials_allowed",
    ]
    for key in required_false:
        if zero.get(key) is not False:
            errors.append(f"zero_trust.{key} must be false")
    for key in ["deny_by_default", "exact_source_id_allowlist_required", "exact_hostname_match_required", "exact_path_allowlist_required", "https_required"]:
        if zero.get(key) is not True:
            errors.append(f"zero_trust.{key} must be true")

    privacy = governance.get("privacy", {})
    if privacy.get("data_classification") != "PUBLIC_NON_PERSONAL_SCIENTIFIC_TELEMETRY":
        errors.append("unexpected data classification")
    if privacy.get("personal_data_expected") is not False:
        errors.append("personal_data_expected must be false")
    for key in [
        "user_or_device_identifiers_allowed",
        "precise_person_location_allowed",
        "audio_or_biometric_data_allowed",
        "behavioral_profiling_allowed",
        "secret_or_token_ingestion_allowed",
        "source_urls_may_contain_user_parameters",
        "raw_payload_commit_to_repository",
    ]:
        if privacy.get(key) is not False:
            errors.append(f"privacy.{key} must be false")

    network = governance.get("network", {})
    if int(network.get("timeout_seconds", 0)) <= 0:
        errors.append("network timeout must be positive")
    if not 0 < int(network.get("max_bytes_per_source", 0)) <= 5_000_000:
        errors.append("max_bytes_per_source must be in 1..5000000")
    if network.get("accepted_http_status") != [200]:
        errors.append("accepted_http_status must be exactly [200]")
    if str(network.get("required_content_type_contains", "")).lower() != "json":
        errors.append("required content type marker must be json")

    allowlist = governance.get("allowed_sources", [])
    if len(allowlist) != len(set(allowlist)):
        errors.append("allowed_sources contains duplicates")
    contract_sources = [item["id"] for item in contract.get("sources", [])]
    if contract_sources != allowlist:
        errors.append("contract source order/set must exactly match governance allowlist")

    registry_by_id = {item["id"]: item for item in source_registry.get("sources", [])}
    families = set()
    for item in contract.get("sources", []):
        source_id = item["id"]
        family = item["measurement_family"]
        if family in families:
            errors.append(f"duplicate measurement family: {family}")
        families.add(family)
        source = registry_by_id.get(source_id)
        if source is None:
            errors.append(f"source not found in registry: {source_id}")
            continue
        if source.get("authority") != "NOAA_SWPC":
            errors.append(f"source authority must be NOAA_SWPC: {source_id}")
        if source.get("access") != "PUBLIC_GET":
            errors.append(f"source access must be PUBLIC_GET: {source_id}")
        if source.get("fetch_by_default") is not False:
            errors.append(f"source must remain opt-in: {source_id}")

        parsed = urllib.parse.urlparse(str(source.get("sample_url", "")))
        if parsed.scheme != "https":
            errors.append(f"source must use HTTPS: {source_id}")
        if parsed.hostname != source.get("domain"):
            errors.append(f"source hostname/domain mismatch: {source_id}")
        if parsed.username or parsed.password:
            errors.append(f"URL userinfo forbidden: {source_id}")
        if parsed.port is not None:
            errors.append(f"custom port forbidden: {source_id}")
        if parsed.query:
            errors.append(f"query parameters forbidden in Trinity source: {source_id}")
        if parsed.fragment:
            errors.append(f"URL fragment forbidden: {source_id}")
        expected_path = governance.get("allowed_routes", {}).get(source_id)
        if not expected_path:
            errors.append(f"exact route missing from governance allowlist: {source_id}")
        elif parsed.path != expected_path:
            errors.append(f"source path does not match exact allowlist: {source_id}")

    required_workflow_markers = [
        "permissions:\n  contents: read",
        "persist-credentials: false",
        "scripts/rll_noaa_trinity_cycle.py",
        "scripts/validate_rll_noaa_trinity_governance.py",
    ]
    for marker in required_workflow_markers:
        if marker not in workflow_text:
            errors.append(f"workflow marker missing: {marker!r}")
    if "contents: write" in workflow_text or "pull-requests: write" in workflow_text:
        errors.append("workflow must not have repository write permissions")

    for cron in contract.get("schedule_utc", {}).values():
        if f'cron: "{cron}"' not in workflow_text:
            errors.append(f"workflow missing Trinity schedule: {cron}")

    return {
        "schema": "rll.noaa.trinity633.data_governance.validation.v1",
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "warnings": warnings,
        "sources_checked": len(contract_sources),
        "measurement_families": len(families),
        "claim_allowed": False,
        "compliance_claim": False,
        "boundary": "engineering governance validation only; no legal or scientific certification",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", default="data/contracts/rll_noaa_trinity_633.v1.json")
    parser.add_argument("--governance", default="data/governance/rll_noaa_trinity633_data_governance.v1.json")
    parser.add_argument("--source-registry", default="data/climate/rll_climate_source_registry.v1.json")
    parser.add_argument("--workflow", default=".github/workflows/rll-real-data-orchestrator.yml")
    parser.add_argument("--output", default="")
    args = parser.parse_args()

    paths = {
        "contract": Path(args.contract),
        "governance": Path(args.governance),
        "source_registry": Path(args.source_registry),
        "workflow": Path(args.workflow),
    }
    try:
        receipt = validate(
            load_json(paths["contract"]),
            load_json(paths["governance"]),
            load_json(paths["source_registry"]),
            paths["workflow"].read_text(encoding="utf-8"),
        )
        receipt["sha256"] = {name: sha256_file(path) for name, path in paths.items()}
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        receipt = {
            "schema": "rll.noaa.trinity633.data_governance.validation.v1",
            "status": "FAIL",
            "errors": [str(exc)],
            "claim_allowed": False,
            "compliance_claim": False,
        }

    text = json.dumps(receipt, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    if args.output:
        target = Path(args.output)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if receipt["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
