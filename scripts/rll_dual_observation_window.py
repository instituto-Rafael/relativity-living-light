#!/usr/bin/env python3
"""Dual observational window gate for RLL.

SOURCE != ARTEFACT != EXECUTION != EVIDENCE != CLAIM
RESIDUAL != NOISE != CAUSE != NEW_PHYSICS
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any, Sequence

INPUT_SCHEMA = "rll.dual_observation_window.input.v1"
OUTPUT_SCHEMA = "rll.dual_observation_window.receipt.v1"


def _vectors(doc: dict[str, Any]) -> tuple[list[float], ...]:
    names = ("observed", "baseline", "candidate", "uncertainty")
    vecs = []
    for name in names:
        raw = doc.get(name)
        if not isinstance(raw, list) or not raw:
            raise ValueError(f"{name} must be a non-empty list")
        vec = [float(v) for v in raw]
        if not all(math.isfinite(v) for v in vec):
            raise ValueError(f"{name} must contain finite values")
        vecs.append(vec)
    n = len(vecs[0])
    if any(len(v) != n for v in vecs):
        raise ValueError("observed/baseline/candidate/uncertainty length mismatch")
    if any(v <= 0.0 for v in vecs[3]):
        raise ValueError("uncertainty must be > 0; unknown scale is TOKEN_VAZIO")
    return tuple(vecs)  # type: ignore[return-value]


def reduced_loss(observed: Sequence[float], predicted: Sequence[float],
                 uncertainty: Sequence[float]) -> float:
    n = len(observed)
    return sum(
        ((y - m) / s) ** 2
        for y, m, s in zip(observed, predicted, uncertainty)
    ) / n


def spectral_entropy(values: Sequence[float]) -> float | None:
    n = len(values)
    if n < 4:
        return None
    mean = sum(values) / n
    xs = [v - mean for v in values]
    powers = []
    for k in range(1, n // 2 + 1):
        re = im = 0.0
        for t, value in enumerate(xs):
            angle = -2.0 * math.pi * k * t / n
            re += value * math.cos(angle)
            im += value * math.sin(angle)
        powers.append(re * re + im * im)
    total = sum(powers)
    if total <= 0.0:
        return None
    probs = [p / total for p in powers if p > 0.0]
    if len(probs) <= 1:
        return 0.0
    return -sum(p * math.log(p) for p in probs) / math.log(len(powers))


def lag1(values: Sequence[float]) -> float | None:
    if len(values) < 3:
        return None
    x = values[:-1]
    y = values[1:]
    return pearson(x, y)


def pearson(x: Sequence[float], y: Sequence[float]) -> float | None:
    if len(x) != len(y) or len(x) < 2:
        return None
    mx = sum(x) / len(x)
    my = sum(y) / len(y)
    dx = [v - mx for v in x]
    dy = [v - my for v in y]
    vx = sum(v * v for v in dx)
    vy = sum(v * v for v in dy)
    if vx <= 0.0 or vy <= 0.0:
        return None
    return sum(a * b for a, b in zip(dx, dy)) / math.sqrt(vx * vy)


def _falsifier_state(prereg: dict[str, Any]) -> tuple[bool, list[str]]:
    rows = prereg.get("hard_falsifiers", [])
    if not isinstance(rows, list):
        raise ValueError("hard_falsifiers must be a list")
    failed = []
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("id"), str):
            raise ValueError("each hard falsifier requires an id")
        state = row.get("state")
        if state not in ("PASS", "FAIL", "TOKEN_VAZIO"):
            raise ValueError("hard falsifier state must be PASS, FAIL or TOKEN_VAZIO")
        if state == "FAIL":
            failed.append(row["id"])
    return bool(failed), failed


def evaluate(doc: dict[str, Any]) -> dict[str, Any]:
    if doc.get("schema") != INPUT_SCHEMA:
        raise ValueError(f"schema must be {INPUT_SCHEMA}")

    observed, baseline, candidate, uncertainty = _vectors(doc)
    prereg = doc.get("preregistration")
    if not isinstance(prereg, dict):
        raise ValueError("preregistration is required")
    tolerance = float(prereg.get("delta_loss_tolerance", 0.0))
    if not math.isfinite(tolerance) or tolerance < 0.0:
        raise ValueError("delta_loss_tolerance must be finite and >= 0")

    hard_failed, failed_ids = _falsifier_state(prereg)
    q0 = reduced_loss(observed, baseline, uncertainty)
    q1 = reduced_loss(observed, candidate, uncertainty)
    delta = q1 - q0
    support = max(0.0, -delta)
    opposition = max(0.0, delta)

    if hard_failed:
        state = "BLOCKED_HARD_FALSIFIER"
    elif abs(delta) <= tolerance:
        state = "NEUTRAL_WITHIN_TOLERANCE"
    elif delta < 0.0:
        state = "RELATIVE_SUPPORT"
    else:
        state = "RELATIVE_OPPOSITION"

    residual0 = [y - m for y, m in zip(observed, baseline)]
    residual1 = [y - m for y, m in zip(observed, candidate)]

    context = doc.get("context_covariates", {})
    if not isinstance(context, dict):
        raise ValueError("context_covariates must be an object")
    correlations: dict[str, Any] = {}
    for name, raw in sorted(context.items()):
        if not isinstance(raw, list) or len(raw) != len(observed):
            correlations[name] = {"state": "TOKEN_VAZIO_LENGTH_MISMATCH", "r": None}
            continue
        values = [float(v) for v in raw]
        if not all(math.isfinite(v) for v in values):
            correlations[name] = {"state": "TOKEN_VAZIO_NONFINITE", "r": None}
            continue
        correlations[name] = {
            "state": "NUMERIC_CORRELATION_NOT_CAUSE",
            "r": pearson(residual1, values),
        }

    mechanism = doc.get("mechanism")
    mechanism_state = "TOKEN_VAZIO_MECHANISM"
    if isinstance(mechanism, dict) and mechanism.get("state") == "PREREGISTERED_TESTABLE":
        mechanism_state = "PREREGISTERED_TESTABLE_NOT_CONFIRMED"

    return {
        "schema": OUTPUT_SCHEMA,
        "observable": doc.get("observable", {}),
        "relative_fit": {
            "baseline_reduced_loss": q0,
            "candidate_reduced_loss": q1,
            "delta_loss": delta,
            "support_channel": support,
            "opposition_channel": opposition,
            "state": state,
            "tolerance": tolerance,
        },
        "hard_falsifiers": {
            "failed": failed_ids,
            "noncompensatory_block": hard_failed,
        },
        "residual_structure": {
            "baseline_spectral_entropy": spectral_entropy(residual0),
            "candidate_spectral_entropy": spectral_entropy(residual1),
            "baseline_lag1": lag1(residual0),
            "candidate_lag1": lag1(residual1),
            "context_correlations": correlations,
        },
        "mechanism_state": mechanism_state,
        "residual_is_noise": False,
        "residual_is_cause": False,
        "new_physics_detected": False,
        "claim_allowed": False,
        "F_ok": "support and opposition channels preserved with residual diagnostics",
        "F_gap": "mechanism, common-mode exclusion and independent replication remain separate gates",
        "F_next": "bind real sourced vectors with covariance and preregistered environmental controls",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_json")
    parser.add_argument("--output", default="-")
    args = parser.parse_args()
    try:
        doc = json.loads(Path(args.input_json).read_text(encoding="utf-8"))
        out = evaluate(doc)
        code = 0
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        out = {
            "schema": OUTPUT_SCHEMA,
            "state": "FAIL_CLOSED",
            "error": str(exc),
            "claim_allowed": False,
        }
        code = 2
    text = json.dumps(out, indent=2, ensure_ascii=False) + "\n"
    if args.output == "-":
        print(text, end="")
    else:
        Path(args.output).write_text(text, encoding="utf-8")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
