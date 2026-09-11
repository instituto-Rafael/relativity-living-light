#!/usr/bin/env python3
"""Typed numerical ΔOBS/residual gate for normalized observation samples.

This module computes a preregistered cross-family numerical candidate only.
It does not establish sensor independence, common cause, or new physics.

SOURCE != ARTEFACT != EXECUTION != EVIDENCE != CLAIM
RESIDUAL != CAUSE
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timedelta, timezone
import json
import math
from pathlib import Path
from typing import Any, Iterable


INPUT_SCHEMA = "rll.deltaobs.normalized_input.v1"
OUTPUT_SCHEMA = "rll.deltaobs.residual_receipt.v1"


def parse_utc(value: str) -> datetime:
    if not isinstance(value, str) or not value:
        raise ValueError("timestamp must be a non-empty string")
    text = value.replace("Z", "+00:00")
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        raise ValueError("timestamp must be timezone-aware")
    return dt.astimezone(timezone.utc)


def validate_preregistration(doc: dict[str, Any]) -> dict[str, Any]:
    pre = doc.get("preregistration")
    if not isinstance(pre, dict):
        raise ValueError("preregistration is required before evaluating samples")
    required = ("z_threshold", "min_families", "min_samples_per_window")
    missing = [key for key in required if key not in pre]
    if missing:
        raise ValueError(f"missing preregistration fields: {missing}")

    z_threshold = float(pre["z_threshold"])
    min_families = int(pre["min_families"])
    min_samples = int(pre["min_samples_per_window"])
    if not math.isfinite(z_threshold) or z_threshold <= 0:
        raise ValueError("z_threshold must be finite and > 0")
    if min_families < 1:
        raise ValueError("min_families must be >= 1")
    if min_samples < 2:
        raise ValueError("min_samples_per_window must be >= 2")
    return {
        "z_threshold": z_threshold,
        "min_families": min_families,
        "min_samples_per_window": min_samples,
    }


def classify_window(ts: datetime, anchor: datetime) -> str | None:
    if anchor - timedelta(hours=6) <= ts < anchor:
        return "baseline"
    if anchor <= ts < anchor + timedelta(hours=3):
        return "challenge"
    if anchor + timedelta(hours=3) <= ts < anchor + timedelta(hours=6):
        return "feedback"
    return None


def _summary(samples: Iterable[dict[str, float]]) -> dict[str, float | int]:
    rows = list(samples)
    n = len(rows)
    if n == 0:
        raise ValueError("summary requires at least one sample")
    values = [float(row["value"]) for row in rows]
    uncertainties = [float(row["uncertainty"]) for row in rows]
    if not all(math.isfinite(x) for x in values + uncertainties):
        raise ValueError("values and uncertainties must be finite")
    if any(u < 0 for u in uncertainties):
        raise ValueError("uncertainty must be >= 0")

    mean = sum(values) / n
    sample_var = (
        sum((x - mean) ** 2 for x in values) / (n - 1)
        if n > 1
        else 0.0
    )
    # Variance of the mean combines observed scatter and declared
    # independent per-sample measurement uncertainty. This is only a
    # numerical gate; independence across measurement families is NOT inferred.
    uncertainty_var_of_mean = sum(u * u for u in uncertainties) / (n * n)
    var_mean = sample_var / n + uncertainty_var_of_mean
    return {
        "n": n,
        "mean": mean,
        "sample_variance": sample_var,
        "variance_of_mean": var_mean,
    }


def _residual(
    baseline: dict[str, float | int],
    other: dict[str, float | int],
) -> dict[str, Any]:
    variance = float(baseline["variance_of_mean"]) + float(other["variance_of_mean"])
    delta = float(other["mean"]) - float(baseline["mean"])
    if variance <= 0.0:
        return {
            "state": "TOKEN_VAZIO_ZERO_SCALE",
            "delta": delta,
            "z": None,
        }
    return {
        "state": "MEASURED_NUMERIC",
        "delta": delta,
        "z": delta / math.sqrt(variance),
    }


def evaluate(doc: dict[str, Any]) -> dict[str, Any]:
    if doc.get("schema") != INPUT_SCHEMA:
        raise ValueError(f"input schema must be {INPUT_SCHEMA}")

    pre = validate_preregistration(doc)
    anchor = parse_utc(doc["anchor_time_utc"])
    samples = doc.get("samples")
    if not isinstance(samples, list):
        raise ValueError("samples must be a list")

    grouped: dict[str, dict[str, list[dict[str, float]]]] = defaultdict(
        lambda: {"baseline": [], "challenge": [], "feedback": []}
    )

    for raw in samples:
        if not isinstance(raw, dict):
            raise ValueError("each sample must be an object")
        family = raw.get("measurement_family")
        if not isinstance(family, str) or not family:
            raise ValueError("measurement_family must be a non-empty string")
        ts = parse_utc(raw["timestamp_utc"])
        window = classify_window(ts, anchor)
        if window is None:
            continue
        value = float(raw["value"])
        uncertainty = float(raw["uncertainty"])
        if not math.isfinite(value) or not math.isfinite(uncertainty):
            raise ValueError("sample value/uncertainty must be finite")
        if uncertainty < 0:
            raise ValueError("sample uncertainty must be >= 0")
        grouped[family][window].append(
            {"value": value, "uncertainty": uncertainty}
        )

    family_results: dict[str, Any] = {}
    exceeding: list[str] = []
    min_samples = pre["min_samples_per_window"]
    threshold = pre["z_threshold"]

    for family in sorted(grouped):
        windows = grouped[family]
        counts = {name: len(rows) for name, rows in windows.items()}
        if any(counts[name] < min_samples for name in ("baseline", "challenge", "feedback")):
            family_results[family] = {
                "state": "TOKEN_VAZIO_INSUFFICIENT_WINDOW",
                "counts": counts,
            }
            continue

        baseline = _summary(windows["baseline"])
        challenge = _summary(windows["challenge"])
        feedback = _summary(windows["feedback"])
        challenge_residual = _residual(baseline, challenge)
        feedback_residual = _residual(baseline, feedback)

        if (
            challenge_residual["state"] == "MEASURED_NUMERIC"
            and abs(float(challenge_residual["z"])) >= threshold
        ):
            exceeding.append(family)

        family_results[family] = {
            "state": "MEASURED_NUMERIC",
            "counts": counts,
            "baseline": baseline,
            "challenge": challenge,
            "feedback": feedback,
            "challenge_residual": challenge_residual,
            "feedback_residual": feedback_residual,
        }

    candidate = len(exceeding) >= pre["min_families"]
    controls = doc.get("common_mode_controls")
    common_mode_state = (
        "DOCUMENTED_NOT_CAUSAL"
        if isinstance(controls, list) and len(controls) > 0
        else "TOKEN_VAZIO_COMMON_MODE_CONTROLS"
    )

    return {
        "schema": OUTPUT_SCHEMA,
        "anchor_time_utc": anchor.isoformat(),
        "windows_hours": {"baseline": 6, "challenge": 3, "feedback": 3},
        "preregistration": pre,
        "families_evaluated": sorted(family_results),
        "families_exceeding_preregistered_threshold": exceeding,
        "family_results": family_results,
        "numeric_deltaobs_state": (
            "NUMERIC_CROSS_FAMILY_CANDIDATE"
            if candidate
            else "NO_NUMERIC_CANDIDATE"
        ),
        "deltaobs_candidate": candidate,
        "common_mode_controls_state": common_mode_state,
        "observed_cross_domain": False,
        "statistical_independence_established": False,
        "cause": "TOKEN_VAZIO_CAUSA",
        "claim_allowed": False,
        "F_ok": "preregistered 6h->3h->3h numerical residual evaluated",
        "F_gap": (
            "cross-family statistical independence, common-mode causal exclusion, "
            "physical mechanism and causal interpretation remain unestablished"
        ),
        "F_next": (
            "run synthetic negative/positive controls and exact-head CI; only then "
            "bind this numeric candidate layer into Trinity633"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_json")
    parser.add_argument("--output", default="-")
    args = parser.parse_args()

    try:
        doc = json.loads(Path(args.input_json).read_text(encoding="utf-8"))
        receipt = evaluate(doc)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        receipt = {
            "schema": OUTPUT_SCHEMA,
            "state": "FAIL_CLOSED",
            "error": str(exc),
            "claim_allowed": False,
        }
        text = json.dumps(receipt, indent=2, ensure_ascii=False) + "\n"
        if args.output == "-":
            print(text, end="")
        else:
            Path(args.output).write_text(text, encoding="utf-8")
        return 2

    text = json.dumps(receipt, indent=2, ensure_ascii=False) + "\n"
    if args.output == "-":
        print(text, end="")
    else:
        Path(args.output).write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
