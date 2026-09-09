#!/usr/bin/env python3
"""Evaluate the Borsanyi et al. (2016) full-SM g_rho(T), g_s(T) table.

The source Supplementary Table S3 instructs use of a simple cubic spline in
log10(T/MeV). This implementation uses a natural cubic spline as an explicit
repository reconstruction choice because the paper does not state endpoint
boundary conditions. Exact source knots are returned exactly. Extrapolation is
fail-closed by default.
"""
from __future__ import annotations

import argparse
import bisect
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TABLE = ROOT / "data/inputs/qcd_primordial/borsanyi_2016_full_sm_gstar_table_s3.v1.json"


@dataclass(frozen=True)
class GStarPoint:
    temperature_MeV: float
    log10_T_MeV: float
    g_rho: float
    g_s: float
    g_rho_over_g_s: float
    interpolation: str


def load_table(path: Path = DEFAULT_TABLE) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload.get("rows")
    if not isinstance(rows, list) or len(rows) < 2:
        raise ValueError("Borsanyi table must contain at least two rows")
    xs = [float(row["log10_T_MeV"]) for row in rows]
    if any(not math.isfinite(x) for x in xs) or any(b <= a for a, b in zip(xs, xs[1:])):
        raise ValueError("log10 temperature knots must be finite and strictly increasing")
    for row in rows:
        if float(row["g_rho"]) <= 0.0 or float(row["g_rho_over_g_s"]) <= 0.0:
            raise ValueError("g-star source values must be positive")
    return payload


def _natural_second_derivatives(xs: list[float], ys: list[float]) -> list[float]:
    n = len(xs)
    if n != len(ys) or n < 2:
        raise ValueError("invalid spline vectors")
    if n == 2:
        return [0.0, 0.0]
    m = n - 2
    lower = [0.0] * m
    diag = [0.0] * m
    upper = [0.0] * m
    rhs = [0.0] * m
    for j in range(1, n - 1):
        i = j - 1
        h0 = xs[j] - xs[j - 1]
        h1 = xs[j + 1] - xs[j]
        lower[i] = h0 if i > 0 else 0.0
        diag[i] = 2.0 * (h0 + h1)
        upper[i] = h1 if i < m - 1 else 0.0
        rhs[i] = 6.0 * ((ys[j + 1] - ys[j]) / h1 - (ys[j] - ys[j - 1]) / h0)
    for i in range(1, m):
        factor = lower[i] / diag[i - 1]
        diag[i] -= factor * upper[i - 1]
        rhs[i] -= factor * rhs[i - 1]
    interior = [0.0] * m
    interior[-1] = rhs[-1] / diag[-1]
    for i in range(m - 2, -1, -1):
        interior[i] = (rhs[i] - upper[i] * interior[i + 1]) / diag[i]
    return [0.0, *interior, 0.0]


def _spline_eval(xs: list[float], ys: list[float], seconds: list[float], x: float) -> float:
    if x < xs[0] or x > xs[-1]:
        raise ValueError("temperature lies outside the source Table S3 domain")
    for knot, value in zip(xs, ys):
        if x == knot:
            return value
    i = bisect.bisect_right(xs, x) - 1
    if i >= len(xs) - 1:
        return ys[-1]
    h = xs[i + 1] - xs[i]
    a = (xs[i + 1] - x) / h
    b = (x - xs[i]) / h
    return (
        a * ys[i]
        + b * ys[i + 1]
        + ((a**3 - a) * seconds[i] + (b**3 - b) * seconds[i + 1]) * h * h / 6.0
    )


def evaluate(temperature_MeV: float, payload: dict | None = None) -> GStarPoint:
    if not math.isfinite(temperature_MeV) or temperature_MeV <= 0.0:
        raise ValueError("temperature_MeV must be positive and finite")
    data = payload or load_table()
    rows = data["rows"]
    xs = [float(row["log10_T_MeV"]) for row in rows]
    g_rho_values = [float(row["g_rho"]) for row in rows]
    ratios = [float(row["g_rho_over_g_s"]) for row in rows]
    x = math.log10(temperature_MeV)
    if x < xs[0] or x > xs[-1]:
        raise ValueError(
            f"T={temperature_MeV} MeV outside Borsanyi Table S3 domain "
            f"[{10**xs[0]}, {10**xs[-1]}] MeV; extrapolation forbidden"
        )
    exact = next((i for i, knot in enumerate(xs) if math.isclose(x, knot, rel_tol=0.0, abs_tol=1e-12)), None)
    if exact is not None:
        g_rho = g_rho_values[exact]
        ratio = ratios[exact]
        mode = "EXACT_SOURCE_KNOT"
        x = xs[exact]
    else:
        g_rho = _spline_eval(xs, g_rho_values, _natural_second_derivatives(xs, g_rho_values), x)
        ratio = _spline_eval(xs, ratios, _natural_second_derivatives(xs, ratios), x)
        mode = "NATURAL_CUBIC_SPLINE_RECONSTRUCTION"
    if g_rho <= 0.0 or ratio <= 0.0:
        raise ValueError("interpolated g-star state became non-physical")
    return GStarPoint(
        temperature_MeV=float(temperature_MeV),
        log10_T_MeV=x,
        g_rho=g_rho,
        g_s=g_rho / ratio,
        g_rho_over_g_s=ratio,
        interpolation=mode,
    )


def build_receipt(temperatures: Iterable[float]) -> dict:
    payload = load_table()
    points = [asdict(evaluate(float(t), payload)) for t in temperatures]
    return {
        "schema": "rll.borsanyi_full_sm_gstar.receipt.v1",
        "claim_allowed": False,
        "source_table": "Borsanyi et al. 2016 Supplementary Table S3",
        "doi": "10.1038/nature20115",
        "arxiv": "1606.07494",
        "table_knots": len(payload["rows"]),
        "source_domain_log10_T_MeV": [
            payload["rows"][0]["log10_T_MeV"],
            payload["rows"][-1]["log10_T_MeV"],
        ],
        "interpolation": "NATURAL_CUBIC_SPLINE_RECONSTRUCTION",
        "source_instruction": "simple cubic spline interpolation",
        "boundary_condition_status": "IMPLEMENTATION_CHOICE_NOT_EXPLICIT_IN_PAPER",
        "points": points,
        "status": "MATERIALIZED_BORSANYI_TABLE_S3",
        "publication_effect": "NONE",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("temperatures", nargs="*", type=float, default=[130.0, 154.0, 200.0, 400.0])
    args = parser.parse_args()
    print(json.dumps(build_receipt(args.temperatures), indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
