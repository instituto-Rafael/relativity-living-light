#!/usr/bin/env python3
"""Stdlib-only scientific operators for the RLL edge-science water matrix.

These operators measure transformations. They never promote causality.
"""

from __future__ import annotations

import math
from typing import Iterable, Sequence


class OperatorDomainError(ValueError):
    """Raised when an operator domain, unit, order or boundary invariant fails."""


def _floats(values: Iterable[float]) -> list[float]:
    out = [float(v) for v in values]
    if not out or not all(math.isfinite(v) for v in out):
        raise OperatorDomainError("values must be non-empty and finite")
    return out


def _xy(x: Iterable[float], y: Iterable[float]) -> tuple[list[float], list[float]]:
    xs, ys = _floats(x), _floats(y)
    if len(xs) != len(ys) or len(xs) < 2:
        raise OperatorDomainError("x and y must have equal length >= 2")
    if any(b <= a for a, b in zip(xs, xs[1:])):
        raise OperatorDomainError("x must be strictly increasing")
    return xs, ys


def finite_derivative(
    x: Iterable[float],
    y: Iterable[float],
    *,
    axis_unit: str,
    value_unit: str,
) -> dict[str, object]:
    """Return interval derivatives dy/dx; this is a change signature, not causal proof."""
    if not axis_unit or not value_unit:
        raise OperatorDomainError("axis_unit and value_unit are required")
    xs, ys = _xy(x, y)
    slopes = [(b_y - a_y) / (b_x - a_x) for a_x, b_x, a_y, b_y in zip(xs, xs[1:], ys, ys[1:])]
    mids = [(a + b) / 2.0 for a, b in zip(xs, xs[1:])]
    return {
        "operator": "DERIVATIVE",
        "axis": mids,
        "values": slopes,
        "unit": f"{value_unit}/{axis_unit}",
        "claim": "CHANGE_RATE_ONLY_NOT_CAUSAL_PROOF",
    }


def cumulative_trapezoid(
    x: Iterable[float],
    y: Iterable[float],
    *,
    boundary_value: float,
    axis_unit: str,
    value_unit: str,
) -> dict[str, object]:
    """Integrate y dx with an explicit boundary value."""
    if not axis_unit or not value_unit:
        raise OperatorDomainError("axis_unit and value_unit are required")
    if not math.isfinite(float(boundary_value)):
        raise OperatorDomainError("finite boundary_value required")
    xs, ys = _xy(x, y)
    accum = [float(boundary_value)]
    for a_x, b_x, a_y, b_y in zip(xs, xs[1:], ys, ys[1:]):
        accum.append(accum[-1] + (b_x - a_x) * (a_y + b_y) / 2.0)
    return {
        "operator": "ANTIDERIVATIVE",
        "axis": xs,
        "values": accum,
        "boundary_value": float(boundary_value),
        "unit": f"{value_unit}*{axis_unit}",
        "claim": "BOUNDARY_CONSTRAINED_FAMILY_NOT_UNIQUE_ORIGIN",
    }


def reconstruction_error(original: Iterable[float], reconstructed: Iterable[float]) -> dict[str, float | str]:
    """Measure reverse-path information loss."""
    a, b = _floats(original), _floats(reconstructed)
    if len(a) != len(b):
        raise OperatorDomainError("vectors must have equal length")
    residuals = [x - y for x, y in zip(a, b)]
    rmse = math.sqrt(sum(r * r for r in residuals) / len(residuals))
    max_abs = max(abs(r) for r in residuals)
    return {
        "operator": "REVERSIVE",
        "rmse": rmse,
        "max_abs_error": max_abs,
        "claim": "RECONSTRUCTION_QUALITY_NOT_ORIGIN_PROOF",
    }


def reciprocal(values: Iterable[float]) -> dict[str, object]:
    vals = _floats(values)
    if any(v == 0.0 for v in vals):
        return {
            "operator": "RECIPROCAL",
            "state": "ABSTAIN_TOKEN_VAZIO_DOMAIN",
            "values": [],
        }
    return {"operator": "RECIPROCAL", "state": "PASS", "values": [1.0 / v for v in vals]}


def log1p_roundtrip(values: Iterable[float]) -> dict[str, object]:
    vals = _floats(values)
    if any(v <= -1.0 for v in vals):
        raise OperatorDomainError("log1p requires x > -1")
    encoded = [math.log1p(v) for v in vals]
    decoded = [math.expm1(v) for v in encoded]
    result = reconstruction_error(vals, decoded)
    result.update({"operator": "LOG1P_ROUNDTRIP", "encoded": encoded})
    return result


def nested_log_log(values: Iterable[float], *, purpose: str) -> dict[str, object]:
    vals = _floats(values)
    if not purpose:
        raise OperatorDomainError("declared purpose required")
    if any(v <= 1.0 for v in vals):
        raise OperatorDomainError("log(log(x)) requires x > 1")
    return {
        "operator": "NESTED_LOG_LOG",
        "values": [math.log(math.log(v)) for v in vals],
        "purpose": purpose,
        "claim": "EXPLORATORY_SCALE_COMPRESSION_ONLY",
    }


def _fit_record(model: str, intercept: float, slope: float, sse: float, aic: float) -> dict[str, float | str]:
    return {"model": model, "intercept": intercept, "slope": slope, "sse": sse, "aic": aic}


def _linear_fit(x: Sequence[float], y: Sequence[float], model: str) -> dict[str, float | str]:
    n = len(x)
    mean_x = sum(x) / n
    mean_y = sum(y) / n
    denom = sum((v - mean_x) ** 2 for v in x)
    if denom == 0.0:
        raise OperatorDomainError("x variance must be positive")
    slope = sum((a - mean_x) * (b - mean_y) for a, b in zip(x, y)) / denom
    intercept = mean_y - slope * mean_x
    residuals = [b - (intercept + slope * a) for a, b in zip(x, y)]
    sse = sum(r * r for r in residuals)
    variance = max(sse / n, 1e-300)
    aic = n * math.log(variance) + 2 * 2
    return _fit_record(model, intercept, slope, sse, aic)


def log_log_model_competition(x: Iterable[float], y: Iterable[float]) -> dict[str, object]:
    """Compare linear y~x and power-law log(y)~log(x); no model is promoted automatically."""
    xs, ys = _xy(x, y)
    if len(xs) < 3:
        raise OperatorDomainError("model competition requires at least 3 points")
    if any(v <= 0.0 for v in xs + ys):
        raise OperatorDomainError("log-log requires x>0 and y>0")
    linear = _linear_fit(xs, ys, "LINEAR")
    power = _linear_fit([math.log(v) for v in xs], [math.log(v) for v in ys], "POWER_LAW_LOG_LOG")
    winner = min((linear, power), key=lambda f: float(f["aic"]))
    return {
        "operator": "LOG_LOG",
        "models": [linear, power],
        "aic_preferred_candidate": winner["model"],
        "claim": "MODEL_CANDIDATE_ONLY_NOT_POWER_LAW_PROOF",
    }


def combined_nitrate_nitrite_ratio(
    nitrate_as_n_mg_l: float,
    nitrite_as_n_mg_l: float,
    *,
    nitrate_vmp: float = 10.0,
    nitrite_vmp: float = 1.0,
) -> dict[str, float | bool | str]:
    values = [nitrate_as_n_mg_l, nitrite_as_n_mg_l, nitrate_vmp, nitrite_vmp]
    if not all(math.isfinite(float(v)) for v in values):
        raise OperatorDomainError("finite concentrations and limits required")
    if nitrate_as_n_mg_l < 0 or nitrite_as_n_mg_l < 0 or nitrate_vmp <= 0 or nitrite_vmp <= 0:
        raise OperatorDomainError("concentrations must be >=0 and limits >0")
    ratio = nitrate_as_n_mg_l / nitrate_vmp + nitrite_as_n_mg_l / nitrite_vmp
    return {
        "operator": "BRAZIL_NITRATE_NITRITE_COMBINED_RULE",
        "ratio": ratio,
        "passes": ratio <= 1.0,
        "claim": "REGULATORY_SCREEN_REQUIRES_CERTIFIED_MEASUREMENT",
    }
