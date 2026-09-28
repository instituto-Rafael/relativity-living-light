#!/usr/bin/env python3
"""RLL multiscale heterogeneous residual decomposition.

Mathematical scope:
- population/sample variance;
- exact finite within/between-group SSE decomposition;
- residual-class bookkeeping;
- declared-uncertainty standardization;
- Fibonacci-sized contiguous diagnostic windows.

This module does NOT make a physical/cosmological claim.
Fibonacci scales are diagnostic window sizes, not probability weights.
Geometry references are typed metadata and do not alter likelihoods.

SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM
RESIDUAL != CAUSE
TOKEN_VAZIO != 0
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import json
import math
from pathlib import Path
from typing import Any

INPUT_SCHEMA = "rll.multiscale_heterogeneous_residual.input.v1"
OUTPUT_SCHEMA = "rll.multiscale_heterogeneous_residual.receipt.v1"

ALLOWED_RESIDUAL_CLASSES = {
    "DELTA_MEASUREMENT",
    "DELTA_MODEL",
    "DELTA_OMITTED_VARIABLE",
    "DELTA_LATENT",
    "DELTA_STOCHASTIC",
    "DELTA_UNCLASSIFIED",
}


def _finite(x: Any, name: str) -> float:
    value = float(x)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


def _mean(xs: list[float]) -> float:
    if not xs:
        raise ValueError("mean requires non-empty data")
    return sum(xs) / len(xs)


def _population_variance(xs: list[float], mu: float | None = None) -> float:
    if not xs:
        raise ValueError("population variance requires non-empty data")
    if mu is None:
        mu = _mean(xs)
    return sum((x - mu) ** 2 for x in xs) / len(xs)


def _sample_variance(xs: list[float], mu: float | None = None) -> float | None:
    if len(xs) < 2:
        return None
    if mu is None:
        mu = _mean(xs)
    return sum((x - mu) ** 2 for x in xs) / (len(xs) - 1)


def _fibonacci_window_sizes(n: int) -> list[int]:
    if n < 2:
        return []
    out = [2]
    a, b = 2, 3
    while b <= n:
        out.append(b)
        a, b = b, a + b
    return out


def _rolling(values: list[float], size: int) -> list[dict[str, float | int]]:
    rows: list[dict[str, float | int]] = []
    for start in range(0, len(values) - size + 1):
        window = values[start : start + size]
        mu = _mean(window)
        rows.append(
            {
                "start": start,
                "end_exclusive": start + size,
                "mean": mu,
                "population_variance": _population_variance(window, mu),
            }
        )
    return rows


def _group_decomposition(records: list[dict[str, Any]]) -> dict[str, Any]:
    grouped: dict[str, list[float]] = defaultdict(list)
    for row in records:
        group = row.get("group")
        if group is None:
            return {
                "state": "TOKEN_VAZIO_GROUPING",
                "reason": "at least one record has no group",
            }
        grouped[str(group)].append(float(row["value"]))

    values = [float(row["value"]) for row in records]
    mu = _mean(values)
    total_sse = sum((x - mu) ** 2 for x in values)

    within_sse = 0.0
    between_sse = 0.0
    groups: dict[str, Any] = {}
    for group in sorted(grouped):
        xs = grouped[group]
        gmu = _mean(xs)
        gss = sum((x - gmu) ** 2 for x in xs)
        within_sse += gss
        between_sse += len(xs) * (gmu - mu) ** 2
        groups[group] = {
            "n": len(xs),
            "mean": gmu,
            "population_variance": _population_variance(xs, gmu),
            "sample_variance": _sample_variance(xs, gmu),
            "within_sse": gss,
        }

    closure_error = total_sse - (within_sse + between_sse)
    scale = max(1.0, abs(total_sse), abs(within_sse) + abs(between_sse))
    closure_pass = abs(closure_error) <= 1e-12 * scale
    between_fraction = 0.0 if total_sse == 0.0 else between_sse / total_sse

    return {
        "state": "MEASURED_NUMERIC",
        "identity": "TOTAL_SSE = WITHIN_SSE + BETWEEN_SSE",
        "groups": groups,
        "total_sse": total_sse,
        "within_sse": within_sse,
        "between_sse": between_sse,
        "between_group_fraction": between_fraction,
        "closure_error": closure_error,
        "closure_pass": closure_pass,
    }


def evaluate(doc: dict[str, Any]) -> dict[str, Any]:
    if doc.get("schema") != INPUT_SCHEMA:
        raise ValueError(f"input schema must be {INPUT_SCHEMA}")

    raw_records = doc.get("records")
    if not isinstance(raw_records, list) or not raw_records:
        raise ValueError("records must be a non-empty list")

    ordered = bool(doc.get("ordered", False))
    records: list[dict[str, Any]] = []
    for i, raw in enumerate(raw_records):
        if not isinstance(raw, dict):
            raise ValueError("each record must be an object")
        value = _finite(raw["value"], f"records[{i}].value")
        prediction = _finite(raw["prediction"], f"records[{i}].prediction")
        residual = value - prediction
        residual_class = raw.get("residual_class", "DELTA_UNCLASSIFIED")
        if residual_class not in ALLOWED_RESIDUAL_CLASSES:
            raise ValueError(f"unsupported residual_class: {residual_class}")

        uncertainty_raw = raw.get("uncertainty")
        if uncertainty_raw is None:
            uncertainty = None
            standardized = {
                "state": "TOKEN_VAZIO_UNCERTAINTY",
                "z": None,
            }
        else:
            uncertainty = _finite(uncertainty_raw, f"records[{i}].uncertainty")
            if uncertainty < 0:
                raise ValueError("uncertainty must be >= 0")
            if uncertainty == 0:
                standardized = {
                    "state": "TOKEN_VAZIO_ZERO_SCALE",
                    "z": None,
                }
            else:
                standardized = {
                    "state": "MEASURED_NUMERIC",
                    "z": residual / uncertainty,
                }

        records.append(
            {
                "id": str(raw.get("id", f"obs-{i:04d}")),
                "group": raw.get("group"),
                "value": value,
                "prediction": prediction,
                "residual": residual,
                "residual_class": residual_class,
                "uncertainty": uncertainty,
                "standardized_residual": standardized,
            }
        )

    values = [row["value"] for row in records]
    residuals = [row["residual"] for row in records]
    mu = _mean(values)
    pop_var = _population_variance(values, mu)
    sample_var = _sample_variance(values, mu)

    uncertainties = [row["uncertainty"] for row in records]
    if all(u is not None for u in uncertainties):
        n = len(records)
        observed_component = 0.0 if sample_var is None else sample_var / n
        measurement_component = sum(float(u) ** 2 for u in uncertainties) / (n * n)
        var_mean = observed_component + measurement_component
        se_mean: float | None = math.sqrt(var_mean)
        se_state = "MEASURED_NUMERIC"
    else:
        var_mean = None
        se_mean = None
        se_state = "TOKEN_VAZIO_UNCERTAINTY"

    critical = doc.get("critical_value")
    if critical is None or se_mean is None:
        margin = {
            "state": (
                "TOKEN_VAZIO_CRITICAL_VALUE"
                if critical is None
                else "TOKEN_VAZIO_UNCERTAINTY"
            ),
            "critical_value": critical,
            "margin": None,
        }
    else:
        cv = _finite(critical, "critical_value")
        if cv <= 0:
            raise ValueError("critical_value must be > 0")
        margin = {
            "state": "MEASURED_NUMERIC",
            "critical_value": cv,
            "margin": cv * se_mean,
        }

    by_class: dict[str, dict[str, float | int]] = {}
    for cls in sorted(ALLOWED_RESIDUAL_CLASSES):
        rs = [row["residual"] for row in records if row["residual_class"] == cls]
        if rs:
            by_class[cls] = {
                "count": len(rs),
                "signed_sum": sum(rs),
                "sse": sum(r * r for r in rs),
            }

    total_residual_sse = sum(r * r for r in residuals)
    classified_sse = sum(
        float(item["sse"])
        for cls, item in by_class.items()
        if cls != "DELTA_UNCLASSIFIED"
    )
    unclassified_sse = float(
        by_class.get("DELTA_UNCLASSIFIED", {}).get("sse", 0.0)
    )

    if ordered:
        scales = _fibonacci_window_sizes(len(records))
        multiscale = {
            "state": "MEASURED_NUMERIC",
            "window_family": "CLASSICAL_FIBONACCI_SIZES",
            "weights_likelihood": False,
            "order_sensitive": True,
            "scales": [
                {
                    "size": size,
                    "value_windows": _rolling(values, size),
                    "residual_windows": _rolling(residuals, size),
                }
                for size in scales
            ],
        }
    else:
        multiscale = {
            "state": "TOKEN_VAZIO_ORDERING",
            "reason": "ordered=false; Fibonacci windows are not evaluated",
            "weights_likelihood": False,
        }

    return {
        "schema": OUTPUT_SCHEMA,
        "n": len(records),
        "global_distribution": {
            "mean": mu,
            "population_variance": pop_var,
            "population_stddev": math.sqrt(pop_var),
            "sample_variance": sample_var,
            "sample_stddev": None if sample_var is None else math.sqrt(sample_var),
            "variance_of_mean_state": se_state,
            "variance_of_mean": var_mean,
            "standard_error_mean": se_mean,
            "margin_of_error": margin,
        },
        "heterogeneity": _group_decomposition(records),
        "residual_budget": {
            "total_sse": total_residual_sse,
            "by_class": by_class,
            "classified_sse": classified_sse,
            "unclassified_sse": unclassified_sse,
            "partition_closure_pass": math.isclose(
                total_residual_sse,
                classified_sse + unclassified_sse,
                rel_tol=1e-12,
                abs_tol=1e-12,
            ),
            "boundary": (
                "classification partitions residual records; "
                "it does not prove causal ownership"
            ),
        },
        "multiscale": multiscale,
        "records": records,
        "geometry_binding": {
            "fibonacci_role": "diagnostic window scale / traversal family only",
            "sqrt3_over_2_role": "declared Euclidean geometry/projection kernel only",
            "poincare_role": "typed manifold/metric adapter only",
            "venturi_role": (
                "physical adapter only after variables, units, boundary conditions, "
                "covariance and falsifier"
            ),
            "calendar_role": (
                "temporal lattice/cycle comparator only; no causal cosmology binding"
            ),
        },
        "claim_allowed": False,
        "F_ok": (
            "variance types, finite heterogeneity identity, residual classes and "
            "Fibonacci multiscale diagnostics are separated"
        ),
        "F_gap": (
            "physical mechanism, causal ownership, covariance beyond declared "
            "uncertainties, and external validation remain unresolved"
        ),
        "F_next": (
            "bind to a declared RLL dataset with frozen grouping/order/covariance; "
            "compare against the existing deltaobs gate without replacing it"
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
        rc = 0
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        receipt = {
            "schema": OUTPUT_SCHEMA,
            "state": "FAIL_CLOSED",
            "error": str(exc),
            "claim_allowed": False,
        }
        rc = 2

    text = json.dumps(receipt, indent=2, ensure_ascii=False) + "\n"
    if args.output == "-":
        print(text, end="")
    else:
        Path(args.output).write_text(text, encoding="utf-8")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
