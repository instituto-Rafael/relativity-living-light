from __future__ import annotations

"""Locate the finite lower 95% profile-likelihood crossing for Dovekie CPL wa.

This module consumes the already materialized finite profile as a starting point,
expands to more-negative wa only when needed, and brackets/bisects the one-degree-
of-freedom Delta-chi2=3.8414588 crossing. Omega_m and w0 are re-optimized at
every fixed wa. It is a frequentist profile diagnostic, not a posterior interval.
"""

import argparse
import json
import math
import os
import tempfile
import time
from pathlib import Path
from typing import Any, Callable, Sequence

from . import dovekie_fit_three_model as _dov
from . import dovekie_cpl_wa_profile as _profile

SCHEMA = "rll_dovekie_cpl_wa_lower_bound_v1"
TARGET = _profile.DELTA_CHI2_95_1DOF


def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", suffix=".part", delete=False
    ) as handle:
        tmp = Path(handle.name)
        json.dump(payload, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    try:
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)


def _best_chi2(rows: Sequence[dict[str, Any]]) -> float:
    values = [float(row["chi2"]) for row in rows]
    if not values or any(not math.isfinite(value) for value in values):
        raise ValueError("profile rows require finite chi2 values")
    return min(values)


def lower_bracket_from_rows(
    rows: Sequence[dict[str, Any]],
    *,
    target: float = TARGET,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None, float]:
    """Return (excluded_low, included_high, best_chi2) on the lower-wa side."""
    ordered = sorted(rows, key=lambda row: float(row["wa"]))
    best = _best_chi2(ordered)
    best_wa = float(min(ordered, key=lambda row: float(row["chi2"]))["wa"])
    lower_side = [row for row in ordered if float(row["wa"]) < best_wa]
    included = [row for row in lower_side if float(row["chi2"]) - best <= target]
    if not included:
        return None, None, best
    included_high = min(included, key=lambda row: float(row["wa"]))
    excluded = [
        row
        for row in lower_side
        if float(row["wa"]) < float(included_high["wa"])
        and float(row["chi2"]) - best > target
    ]
    excluded_low = max(excluded, key=lambda row: float(row["wa"])) if excluded else None
    return excluded_low, included_high, best


def bisect_crossing(
    evaluator: Callable[[float], dict[str, Any]],
    low: dict[str, Any],
    high: dict[str, Any],
    all_rows: list[dict[str, Any]],
    *,
    target: float = TARGET,
    max_iterations: int = 18,
    wa_tolerance: float = 0.01,
) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]], float]:
    """Bisect a lower-tail crossing while allowing the global best to update."""
    if float(low["wa"]) >= float(high["wa"]):
        raise ValueError("lower bracket must satisfy low.wa < high.wa")
    evaluated: list[dict[str, Any]] = []
    for _ in range(int(max_iterations)):
        best = _best_chi2(all_rows)
        low_delta = float(low["chi2"]) - best
        high_delta = float(high["chi2"]) - best
        if not (low_delta > target and high_delta <= target):
            candidate_low, candidate_high, best = lower_bracket_from_rows(all_rows, target=target)
            if candidate_low is None or candidate_high is None:
                raise ValueError("profile points no longer form a valid lower crossing bracket")
            low, high = candidate_low, candidate_high
        if abs(float(high["wa"]) - float(low["wa"])) <= wa_tolerance:
            break
        mid_wa = 0.5 * (float(low["wa"]) + float(high["wa"]))
        mid = evaluator(mid_wa)
        evaluated.append(mid)
        all_rows.append(mid)
        best = _best_chi2(all_rows)
        if float(mid["chi2"]) - best > target:
            low = mid
        else:
            high = mid
    return low, high, evaluated, _best_chi2(all_rows)


def build_lower_bound(
    hd_path: Path,
    precision_path: Path,
    profile_path: Path,
    output_path: Path,
    *,
    maxiter: int = 180,
    ftol: float = 1.0e-10,
    integration_points: int = 4096,
    max_expand_steps: int = 8,
) -> dict[str, Any]:
    started = time.perf_counter()
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    if profile.get("claim_allowed") is not False:
        raise ValueError("profile must preserve claim_allowed=false")
    if profile.get("source_sha256") != _dov.sha256_file(hd_path):
        raise ValueError("profile HD hash does not match materialized input")
    if profile.get("precision_sha256") != _dov.sha256_file(precision_path):
        raise ValueError("profile precision hash does not match materialized input")

    data, original_rows = _dov.load_data(hd_path, precision_path, integration_points=integration_points)
    rows: list[dict[str, Any]] = [
        {
            "wa": float(row["wa"]),
            "chi2": float(row["chi2"]),
            "Omega_m": float(row["Omega_m"]),
            "w0": float(row["w0"]),
            "M_offset_profiled": float(row["M_offset_profiled"]),
            "all_starts_converged": bool(row["all_starts_converged"]),
            "source": "input_profile",
        }
        for row in profile["rows"]
    ]

    cache = {float(row["wa"]): row for row in rows}

    def evaluate(wa: float) -> dict[str, Any]:
        key = float(wa)
        if key in cache:
            return cache[key]
        nearest = min(cache.values(), key=lambda row: abs(float(row["wa"]) - key))
        starts = [
            (float(nearest["Omega_m"]), float(nearest["w0"])),
            (0.30, -1.0),
            (0.42, -0.80),
        ]
        fit = _profile.fit_fixed_wa(data, key, starts, maxiter=maxiter, ftol=ftol)
        row = {
            "wa": key,
            "chi2": float(fit["chi2"]),
            "Omega_m": float(fit["Omega_m"]),
            "w0": float(fit["w0"]),
            "M_offset_profiled": float(fit["M_offset_profiled"]),
            "all_starts_converged": bool(fit["all_starts_converged"]),
            "source": "lower_bound_solver",
        }
        cache[key] = row
        return row

    excluded_low, included_high, best = lower_bracket_from_rows(rows)
    expansion_rows: list[dict[str, Any]] = []
    if included_high is None:
        raise ValueError("input profile has no included lower-side point to seed the lower-bound search")

    probe_wa = float(included_high["wa"]) * 2.0
    if probe_wa >= float(included_high["wa"]):
        probe_wa = float(included_high["wa"]) - 4.0

    for _ in range(int(max_expand_steps)):
        if excluded_low is not None:
            break
        probe = evaluate(probe_wa)
        expansion_rows.append(probe)
        rows.append(probe)
        excluded_low, included_high, best = lower_bracket_from_rows(rows)
        probe_wa *= 2.0

    if excluded_low is None or included_high is None:
        payload = {
            "schema": SCHEMA,
            "state": "TOKEN_VAZIO_LOWER_BOUND_NOT_BRACKETED",
            "claim_allowed": False,
            "publication_ready": False,
            "source_sha256": _dov.sha256_file(hd_path),
            "precision_sha256": _dov.sha256_file(precision_path),
            "profile_sha256": _dov.sha256_file(profile_path),
            "n_supernovae": data.n,
            "original_rows": original_rows,
            "target_delta_chi2": TARGET,
            "expansion_rows": expansion_rows,
            "token_vazio": ["TOKEN_VAZIO_CPL_DOVEKIE_WA_LOWER_PROFILE_CLOSURE"],
            "claim_boundary": "No finite lower bound is claimed because the target crossing was not bracketed.",
        }
        _atomic_json(output_path, payload)
        return payload

    low, high, bisection_rows, best = bisect_crossing(
        evaluate,
        excluded_low,
        included_high,
        rows,
        target=TARGET,
    )
    low_delta = float(low["chi2"]) - best
    high_delta = float(high["chi2"]) - best
    width = float(high["wa"]) - float(low["wa"])
    estimate = 0.5 * (float(low["wa"]) + float(high["wa"]))
    all_converged = all(bool(row.get("all_starts_converged", False)) for row in rows)
    verified = (
        all_converged
        and low_delta > TARGET
        and high_delta <= TARGET
        and width <= 0.02
    )
    state = "VERIFIED_FINITE_LOWER_95_BOUND" if verified else "TOKEN_VAZIO_LOWER_BOUND_NUMERICAL_CLOSURE"
    token_vazio = [] if verified else ["TOKEN_VAZIO_CPL_DOVEKIE_WA_LOWER_PROFILE_CLOSURE"]

    payload = {
        "schema": SCHEMA,
        "state": state,
        "claim_allowed": False,
        "publication_ready": False,
        "source_sha256": _dov.sha256_file(hd_path),
        "precision_sha256": _dov.sha256_file(precision_path),
        "profile_sha256": _dov.sha256_file(profile_path),
        "n_supernovae": data.n,
        "original_rows": original_rows,
        "target": {
            "parameter": "wa",
            "confidence_rule": "Delta-chi2 1 dof",
            "delta_chi2": TARGET,
        },
        "global_best_chi2": best,
        "lower_95_bound": {
            "wa_estimate": estimate,
            "excluded_low_wa": float(low["wa"]),
            "excluded_low_delta_chi2": low_delta,
            "included_high_wa": float(high["wa"]),
            "included_high_delta_chi2": high_delta,
            "bracket_width": width,
        },
        "expansion_rows": expansion_rows,
        "bisection_rows": bisection_rows,
        "all_starts_converged": all_converged,
        "token_vazio": token_vazio,
        "claim_boundary": "This is a Dovekie SN-only frequentist profile lower bound. It is not a Bayesian credible interval, does not validate CPL over LCDM, and does not close multi-probe inference.",
        "F_ok": [
            "The 95% lower crossing is explicitly bracketed by one excluded and one included wa point.",
            "Omega_m and w0 are re-optimized at every solver evaluation.",
            "The solver fails closed if no bracket or numerical convergence is obtained."
        ],
        "F_gap": [] if verified else ["TOKEN_VAZIO_CPL_DOVEKIE_WA_LOWER_PROFILE_CLOSURE"],
        "F_next": [
            "Use the finite lower bound only as a profile-likelihood diagnostic.",
            "Keep prior-locked Bayesian evidence and multi-probe likelihoods as separate authorities."
        ],
    }
    _atomic_json(output_path, payload)
    return payload


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Locate the finite lower 95% Dovekie CPL wa profile bound")
    parser.add_argument("--hd", type=Path, required=True)
    parser.add_argument("--precision", type=Path, required=True)
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--maxiter", type=int, default=180)
    parser.add_argument("--ftol", type=float, default=1.0e-10)
    parser.add_argument("--integration-points", type=int, default=4096)
    args = parser.parse_args(argv)
    try:
        payload = build_lower_bound(
            args.hd,
            args.precision,
            args.profile,
            args.output,
            maxiter=args.maxiter,
            ftol=args.ftol,
            integration_points=args.integration_points,
        )
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 2
    print(json.dumps({
        "state": payload["state"],
        "lower_95_bound": payload.get("lower_95_bound"),
        "claim_allowed": False,
    }, sort_keys=True))
    return 0 if payload["state"] == "VERIFIED_FINITE_LOWER_95_BOUND" else 3


if __name__ == "__main__":
    raise SystemExit(main())
