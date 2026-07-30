#!/usr/bin/env python3
"""Dependency-free structural validator for the RLL climate 8x8 registry."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

FIB = [1, 2, 3, 5, 8, 13, 21, 34]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    require(isinstance(data, dict), f"{path}: root must be an object")
    return data


def validate_registry(data: dict[str, Any]) -> dict[str, Any]:
    require(data.get("schema_version") == "1.0", "schema_version must be 1.0")
    require(data.get("registry_id") == "rll-climate-multiphysics-8x8-v1", "unexpected registry_id")
    require(data.get("claim_allowed") is False, "claim_allowed must remain false")
    matrix = data.get("matrix_contract", {})
    require(matrix.get("shape") == [8, 8], "matrix shape must be 8x8")
    require(matrix.get("canonical_lift_required") is True, "canonical lift must be explicit")
    require(matrix.get("strict_lorentz_projection_default") is False, "raw strict projection must not be default")
    require(matrix.get("absence_policy") == "VALIDITY_MASK_AND_TYPED_TOKEN_VAZIO", "invalid absence policy")
    scheduler = data.get("scheduler", {})
    require(scheduler.get("sequence") == FIB, "scheduler sequence must be Fibonacci 1..34")
    require(scheduler.get("continuous_cycle") is True, "continuous_cycle must be true")

    sectors = data.get("sectors")
    require(isinstance(sectors, list) and len(sectors) == 8, "exactly 8 sectors are required")
    columns = set()
    variable_ids: set[str] = set()
    gate_ids: set[str] = set()
    for sector in sectors:
        column = sector.get("column")
        require(isinstance(column, int) and 0 <= column <= 7, "invalid column")
        require(column not in columns, f"duplicate column {column}")
        columns.add(column)
        require(sector.get("native_cadence_minutes", 0) > 0, "native cadence must be positive")
        require(sector.get("max_cadence_minutes", 0) >= sector.get("native_cadence_minutes", 0), "max cadence must be >= native cadence")
        gate = sector.get("temporal_gate", {})
        gate_id = gate.get("id")
        require(isinstance(gate_id, str) and gate_id, "gate id required")
        require(gate_id not in gate_ids, f"duplicate gate id {gate_id}")
        gate_ids.add(gate_id)
        variables = sector.get("variables")
        require(isinstance(variables, list) and len(variables) == 7, f"sector {sector.get('id')} must have 7 physical variables")
        rows = set()
        for item in variables:
            row = item.get("row")
            require(isinstance(row, int) and 1 <= row <= 7, "rows must be 1..7")
            require(row not in rows, f"duplicate row {row} in {sector.get('id')}")
            rows.add(row)
            var_id = item.get("id")
            require(isinstance(var_id, str) and var_id, "variable id required")
            require(var_id not in variable_ids, f"duplicate variable id {var_id}")
            variable_ids.add(var_id)
            require(float(item.get("warning_z", 0)) > 0, f"warning_z must be positive for {var_id}")
        require(rows == set(range(1, 8)), f"sector {sector.get('id')} must cover rows 1..7")
    require(columns == set(range(8)), "columns must cover 0..7")
    require(len(variable_ids) == 56, "registry must contain 56 physical variables")
    require(len(gate_ids) == 8, "registry must contain 8 temporal/evidence gates")
    lateral = data.get("lateral_candidates")
    require(isinstance(lateral, list) and len(lateral) >= 20, "at least 20 lateral candidates required")
    return {
        "status": "PASS",
        "matrix_cells": 64,
        "physical_variables": len(variable_ids),
        "temporal_gates": len(gate_ids),
        "sectors": len(sectors),
        "lateral_candidates": len(lateral),
        "claim_allowed": False
    }


def validate_sources(data: dict[str, Any]) -> dict[str, Any]:
    require(data.get("schema_version") == "1.0", "source schema_version must be 1.0")
    require(data.get("registry_id") == "rll-climate-source-registry-v1", "unexpected source registry_id")
    require(data.get("claim_allowed") is False, "source claim_allowed must be false")
    policy = data.get("network_policy", {})
    require(policy.get("https_only") is True, "HTTPS-only policy required")
    require(policy.get("default_mode") == "DRY_RUN", "default network mode must be DRY_RUN")
    sources = data.get("sources")
    require(isinstance(sources, list) and len(sources) >= 10, "at least 10 sources required")
    ids: set[str] = set()
    for source in sources:
        source_id = source.get("id")
        require(isinstance(source_id, str) and source_id, "source id required")
        require(source_id not in ids, f"duplicate source {source_id}")
        ids.add(source_id)
        url = source.get("sample_url", "")
        require(isinstance(url, str) and url.startswith("https://"), f"source {source_id} must use HTTPS")
        require(source.get("fetch_by_default") is False, f"source {source_id} must not fetch by default")
        require(isinstance(source.get("variables"), list) and source["variables"], f"source {source_id} needs variables")
    return {"status": "PASS", "sources": len(sources), "claim_allowed": False}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", default="data/climate/rll_climate_multiphysics_registry.v1.json")
    parser.add_argument("--sources", default="data/climate/rll_climate_source_registry.v1.json")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    try:
        result = {
            "registry": validate_registry(load_json(Path(args.registry))),
            "sources": validate_sources(load_json(Path(args.sources)))
        }
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, ensure_ascii=False, indent=2))
        return 2 if args.strict else 1
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
