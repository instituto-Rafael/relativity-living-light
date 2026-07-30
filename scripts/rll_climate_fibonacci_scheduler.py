#!/usr/bin/env python3
"""Offline reference scheduler for the RLL climate 8x8 contract.

This script does not forecast weather. It converts already normalized sector states
into a declared H7->B7 canonical lift, computes anomaly and transition diagnostics,
and selects a source-aware Fibonacci polling multiplier.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

FIB = [1, 2, 3, 5, 8, 13, 21, 34]
EPS = 1e-12


def load(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def canonical_lift(values: list[float]) -> tuple[list[float], float]:
    if len(values) != 7:
        raise ValueError("canonical lift requires exactly seven coordinates")
    norm2 = sum(x * x for x in values)
    denom = math.sqrt(1.0 + norm2) + 1.0
    point = [x / denom for x in values]
    radius = math.sqrt(sum(x * x for x in point))
    if not radius < 1.0:
        raise ValueError("canonical lift escaped the Poincare ball")
    return point, radius


def distance_from_origin(radius: float) -> float:
    bounded = min(max(radius, 0.0), 1.0 - EPS)
    return 2.0 * math.atanh(bounded)


def rms_delta(a: list[float], b: list[float], valid: list[bool]) -> float:
    terms = [(x - y) ** 2 for x, y, ok in zip(a, b, valid) if ok]
    return math.sqrt(sum(terms) / len(terms)) if terms else 0.0


def threshold_fraction(values: list[float], warning_z: list[float], valid: list[bool]) -> float:
    checks = [abs(value) >= threshold for value, threshold, ok in zip(values, warning_z, valid) if ok]
    return sum(checks) / len(checks) if checks else 0.0


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def score_sector(values: list[float], previous: list[float], valid: list[bool], warning_z: list[float], gate: float) -> dict[str, float]:
    filled = [value if ok else 0.0 for value, ok in zip(values, valid)]
    point, radius = canonical_lift(filled)
    distance = distance_from_origin(radius)
    transition = rms_delta(values, previous, valid)
    exceedance = threshold_fraction(values, warning_z, valid)
    missing = 1.0 - (sum(valid) / 7.0)
    hazard = clamp01(0.45 * math.tanh(distance / 3.0) + 0.30 * math.tanh(transition / 2.0) + 0.20 * exceedance + 0.05 * clamp01(abs(gate)))
    acquisition = clamp01(0.65 * missing + 0.35 * math.tanh(transition / 2.0))
    priority = max(hazard, acquisition)
    return {
        "radius": radius,
        "hyperbolic_distance_from_baseline": distance,
        "transition_rms": transition,
        "threshold_fraction": exceedance,
        "missing_fraction": missing,
        "hazard_priority": hazard,
        "acquisition_priority": acquisition,
        "priority": priority,
        "point_l2": math.sqrt(sum(x * x for x in point))
    }


def fibonacci_multiplier(priority: float) -> int:
    index = int(round((1.0 - clamp01(priority)) * (len(FIB) - 1)))
    return FIB[index]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run(registry_path: Path, tile_path: Path) -> dict[str, Any]:
    registry = load(registry_path)
    tile = load(tile_path)
    by_id = {sector["id"]: sector for sector in registry["sectors"]}
    results = []
    for state in tile["sectors"]:
        sector_id = state["id"]
        if sector_id not in by_id:
            raise ValueError(f"unknown sector {sector_id}")
        spec = by_id[sector_id]
        values = [float(x) for x in state["normalized_values"]]
        previous = [float(x) for x in state["previous_normalized_values"]]
        valid = [bool(x) for x in state["validity_mask"]]
        if not (len(values) == len(previous) == len(valid) == 7):
            raise ValueError(f"sector {sector_id} needs seven values, previous values and validity flags")
        warning_z = [float(item["warning_z"]) for item in spec["variables"]]
        metrics = score_sector(values, previous, valid, warning_z, float(state.get("temporal_gate", 0.0)))
        multiplier = fibonacci_multiplier(metrics["priority"])
        native = int(spec["native_cadence_minutes"])
        maximum = int(spec["max_cadence_minutes"])
        next_minutes = min(maximum, native * multiplier)
        results.append({
            "id": sector_id,
            "column": spec["column"],
            "projection_mode": "DECLARED_CANONICAL_LIFT_H7_TO_B7",
            "strict_lorentz_projection_attempted": False,
            "fibonacci_multiplier": multiplier,
            "native_cadence_minutes": native,
            "next_cycle_minutes": next_minutes,
            "metrics": metrics,
            "claim_allowed": False
        })
    results.sort(key=lambda item: item["column"])
    return {
        "schema": "rll.climate.scheduler.receipt.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "registry_sha256": sha256_file(registry_path),
        "tile_sha256": sha256_file(tile_path),
        "mode": tile.get("mode", "UNKNOWN"),
        "claim_allowed": False,
        "forecast_generated": False,
        "sectors": results,
        "F_ok": "8x8 sector states mapped with explicit validity masks and declared canonical lift",
        "F_gap": "no forecast skill, causal attribution or operational warning is established by this receipt",
        "F_next": "hydrate one historical event and compare against uniform and conventional adaptive baselines"
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", default="data/climate/rll_climate_multiphysics_registry.v1.json")
    parser.add_argument("--tile", default="tests/fixtures/rll_climate_tile.synthetic.v1.json")
    parser.add_argument("--output")
    args = parser.parse_args()
    try:
        receipt = run(Path(args.registry), Path(args.tile))
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, ensure_ascii=False, indent=2))
        return 2
    text = json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
