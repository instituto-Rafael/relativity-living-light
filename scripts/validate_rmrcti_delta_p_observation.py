#!/usr/bin/env python3
"""Validate the governed RMRCTI Delta-P schema and synthetic fixture."""

from __future__ import annotations

import json
import math
import statistics
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "rmrcti_delta_p_observation.schema.json"
FIXTURE_PATH = ROOT / "fixtures" / "rmrcti_delta_p_observation.example.json"
FORMULA = "P(stable_any=1|peak)-P(stable_any=1|nonpeak)"


def stop(message: str) -> None:
    raise SystemExit(f"RMRCTI Delta-P validation failed: {message}")


def load_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        stop(f"cannot parse {path}: {exc}")
    if not isinstance(value, dict):
        stop(f"expected JSON object: {path}")
    return value


def close(left: float, right: float, tolerance: float = 1e-12) -> bool:
    return math.isclose(left, right, rel_tol=tolerance, abs_tol=tolerance)


def validate_schema(schema: dict[str, Any]) -> None:
    description = str(schema.get("description", "")).lower()
    if "structural contract" not in description:
        stop("schema description must declare structural contract")
    if "does not authorize" not in description:
        stop("schema description must preserve negative authorization")
    if schema.get("type") != "object":
        stop("schema root must be an object")
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))
    expected = {
        "observation_id",
        "source",
        "metric",
        "runs",
        "aggregate",
        "claim_boundary",
        "use_policy",
    }
    if not expected.issubset(properties) or not expected.issubset(required):
        stop("schema root contract is incomplete")


def validate_run(run: dict[str, Any], index: int) -> float:
    counts = run.get("counts")
    if not isinstance(counts, dict):
        stop(f"run {index}: counts must be an object")

    peak_total = counts.get("peaks_total")
    peak_stable = counts.get("peaks_stable")
    non_total = counts.get("nonpeaks_total")
    non_stable = counts.get("nonpeaks_stable")
    values = [peak_total, peak_stable, non_total, non_stable]
    if any(not isinstance(value, int) for value in values):
        stop(f"run {index}: counts must be integers")
    if peak_total <= 0 or non_total <= 0:
        stop(f"run {index}: group totals must be positive")
    if not 0 <= peak_stable <= peak_total:
        stop(f"run {index}: invalid peak stable count")
    if not 0 <= non_stable <= non_total:
        stop(f"run {index}: invalid non-peak stable count")

    p_peak = peak_stable / peak_total
    p_non = non_stable / non_total
    delta = p_peak - p_non
    if not close(float(run.get("p_stable_given_peaks")), p_peak):
        stop(f"run {index}: peak proportion does not match counts")
    if not close(float(run.get("p_stable_given_nonpeaks")), p_non):
        stop(f"run {index}: non-peak proportion does not match counts")
    if not close(float(run.get("delta_p")), delta):
        stop(f"run {index}: Delta-P does not match proportions")
    return delta


def validate_fixture(fixture: dict[str, Any]) -> None:
    source = fixture.get("source", {})
    if source.get("repository") != "rafaelmeloreisnovo/llamaRafaelia":
        stop("unexpected source repository")
    if source.get("code_path") != "rmrCti/gbs3_color.c":
        stop("the actual source path must remain gbs3_color.c")
    if source.get("spoken_alias_state") != "token_vazio":
        stop("unresolved spoken alias must remain token_vazio")

    metric = fixture.get("metric", {})
    if metric.get("formula") != FORMULA:
        stop("metric formula changed")
    peak = metric.get("peak_definition", {})
    if peak.get("fallback_gates") != [3, 4, 8]:
        stop("fallback peak gates must be [3, 4, 8]")
    expected_delta = float(metric.get("expected_delta_p"))
    tolerance = float(metric.get("tolerance"))
    if not close(expected_delta, 0.18):
        stop("synthetic fixture target must remain 0.18")
    if tolerance <= 0:
        stop("tolerance must be positive")

    runs = fixture.get("runs")
    if not isinstance(runs, list) or len(runs) < 3:
        stop("synthetic fixture needs at least three runs")
    if any(run.get("source_state") != "synthetic_fixture" for run in runs):
        stop("fixture cannot present synthetic runs as real traces")
    deltas = [validate_run(run, index) for index, run in enumerate(runs)]

    aggregate = fixture.get("aggregate", {})
    mean = statistics.fmean(deltas)
    median = statistics.median(deltas)
    mad = statistics.median(abs(value - median) for value in deltas)
    stdev = statistics.stdev(deltas)
    checks = {
        "run_count": len(deltas),
        "delta_p_mean": mean,
        "delta_p_median": median,
        "delta_p_min": min(deltas),
        "delta_p_max": max(deltas),
        "delta_p_sample_stdev": stdev,
        "delta_p_mad": mad,
    }
    for name, expected in checks.items():
        observed = aggregate.get(name)
        if name == "run_count":
            if observed != expected:
                stop(f"aggregate.{name} is inconsistent")
        elif not close(float(observed), float(expected)):
            stop(f"aggregate.{name} is inconsistent")

    replicated = (
        len(deltas) >= 3
        and abs(median - expected_delta) <= tolerance
        and mad <= tolerance / 2.0 + 1e-12
    )
    if aggregate.get("replicated_stability_candidate") is not replicated:
        stop("replicated candidate flag is inconsistent")
    if aggregate.get("claim_state") != "REPLICATED_STABILITY_CANDIDATE":
        stop("synthetic fixture claim state must remain candidate-only")

    boundary = fixture.get("claim_boundary", {})
    required_boundary = {
        "attractor_claim": "TOKEN_VAZIO",
        "universal_constant_claim": "NOT_ESTABLISHED",
        "causal_mechanism_claim": "NOT_ESTABLISHED",
        "cosmological_inference": "BLOCKED",
        "fractal_claim": "NOT_ESTABLISHED",
    }
    for name, expected in required_boundary.items():
        if boundary.get(name) != expected:
            stop(f"claim_boundary.{name} must be {expected}")

    policy = fixture.get("use_policy", {})
    if policy.get("data_class") != "synthetic":
        stop("fixture data class must remain synthetic")
    if policy.get("training_eligibility") != "no":
        stop("training eligibility must remain no")
    if policy.get("operational_gate") != "research_only":
        stop("fixture must remain research_only")


def main() -> int:
    validate_schema(load_object(SCHEMA_PATH))
    validate_fixture(load_object(FIXTURE_PATH))
    print("OK: RMRCTI Delta-P schema and synthetic fixture are claim-bounded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
