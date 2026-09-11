#!/usr/bin/env python3
"""NOAA -> RLL Trinity633 custody/orchestration cycle.

This is an observation and provenance bridge, not a detector of new physics.
It deliberately does not compute a physical ΔOBS or a causal residual. Network
access is opt-in. Every execution emits a self-describing receipt and keeps
claim_allowed=false.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_CONTRACT = Path("data/contracts/rll_noaa_trinity_633.v1.json")
DEFAULT_SOURCE_REGISTRY = Path("data/climate/rll_climate_source_registry.v1.json")

SCHEDULE_TO_PHASE = {
    "17 0,12 * * *": "LUX_6H",
    "17 6,18 * * *": "SPIRITUM_3H",
    "17 9,21 * * *": "VERBUM_3H",
}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


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


def validate_source_bindings(contract: dict[str, Any], registry: dict[str, Any]) -> list[dict[str, Any]]:
    by_id = {item["id"]: item for item in registry["sources"]}
    bound = []
    for declared in contract["sources"]:
        source_id = declared["id"]
        if source_id not in by_id:
            raise ValueError(f"Trinity source missing from climate registry: {source_id}")
        source = by_id[source_id]
        if source.get("authority") not in {"NOAA_SWPC", "NOAA_NCEI"}:
            raise ValueError(f"Trinity source is not declared NOAA authority: {source_id}")
        if not str(source.get("sample_url", "")).startswith("https://"):
            raise ValueError(f"Trinity source is not HTTPS: {source_id}")
        bound.append({
            "id": source_id,
            "measurement_family": declared["measurement_family"],
            "authority": source["authority"],
            "domain": source["domain"],
            "url": source["sample_url"],
        })
    return bound


def run_fetch(source_id: str, output_dir: Path, execute_network: bool) -> dict[str, Any]:
    command = [
        sys.executable,
        "scripts/fetch_rll_climate_sources.py",
        "--source",
        source_id,
        "--output-dir",
        str(output_dir),
    ]
    if execute_network:
        command.append("--execute")
    completed = subprocess.run(command, text=True, capture_output=True, check=False)
    payload: dict[str, Any]
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError:
        payload = {
            "status": "FAIL",
            "error": "FETCHER_OUTPUT_NOT_JSON",
            "stdout": completed.stdout[-2000:],
        }
    payload["returncode"] = completed.returncode
    payload["stderr_tail"] = completed.stderr[-2000:]
    return payload


def build_receipt(
    contract: dict[str, Any],
    registry: dict[str, Any],
    phase: str,
    output_dir: Path,
    execute_network: bool,
) -> dict[str, Any]:
    spec = phase_spec(contract, phase)
    bound_sources = validate_source_bindings(contract, registry)
    source_dir = output_dir / "sources"
    source_dir.mkdir(parents=True, exist_ok=True)

    observations = []
    success_families: set[str] = set()
    for source in bound_sources:
        result = run_fetch(source["id"], source_dir, execute_network)
        executed_ok = execute_network and result.get("returncode") == 0 and isinstance(result.get("sha256"), str)
        if executed_ok:
            success_families.add(source["measurement_family"])
        observations.append({
            **source,
            "execution": result,
            "custody_observed": executed_ok,
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
    receipt = {
        "schema": "rll.noaa.trinity633.receipt.v1",
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
        "F_gap": (
            "physical ΔOBS, temporal correlation, statistical independence and numeric residual remain TOKEN_VAZIO"
        ),
        "F_next": (
            "hydrate timestamped NOAA variables into a typed ΔOBS window and compare 6h baseline -> 3h challenge -> 3h feedback"
        ),
    }
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT))
    parser.add_argument("--source-registry", default=str(DEFAULT_SOURCE_REGISTRY))
    parser.add_argument("--phase", choices=["auto", "LUX_6H", "SPIRITUM_3H", "VERBUM_3H"], default="auto")
    parser.add_argument("--schedule-expression", default="")
    parser.add_argument("--output-dir", default="artifacts/rll-real-run/noaa-trinity633")
    parser.add_argument("--execute-network", action="store_true")
    args = parser.parse_args()

    try:
        contract = load_json(Path(args.contract))
        registry = load_json(Path(args.source_registry))
        phase = resolve_phase(args.phase, args.schedule_expression)
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        receipt = build_receipt(contract, registry, phase, output_dir, args.execute_network)
        receipt_path = output_dir / "TRINITY633_RECEIPT.json"
        receipt_path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(json.dumps(receipt, indent=2, ensure_ascii=False))
        # The action succeeds when an auditable receipt is produced, even when
        # the external network/source is unavailable. Availability remains a
        # typed gate_status/TOKEN_VAZIO, not a process crash. Contract or parser
        # failures still return non-zero through the exception boundary below.
        return 0
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({
            "status": "FAIL",
            "error": str(exc),
            "claim_allowed": False,
        }, indent=2, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
