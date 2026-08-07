from __future__ import annotations

"""Profile-likelihood sensitivity for the DES-Dovekie CPL wa boundary.

The production three-model fit found wa at its declared lower bound (-3). This
module expands the scanned wa domain while preserving the same Dovekie HD,
precision matrix, profiled magnitude offset, H0 reference scale and CPL
background equations. It does not turn a profile scan into Bayesian evidence.
"""

import argparse
import json
import math
import os
import tempfile
import time
from pathlib import Path
from typing import Any, Sequence

import numpy as np
from scipy.optimize import minimize

from . import dovekie_fit_three_model as _dov

SCHEMA = "rll_dovekie_cpl_wa_profile_v1"


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


def fixed_wa_objective_gradient(
    data: _dov.DovekieData, free_parameters: np.ndarray, wa: float
) -> tuple[float, np.ndarray]:
    omega_m, w0 = map(float, free_parameters)
    full = np.asarray([omega_m, w0, float(wa)], dtype=float)
    chi2, gradient = _dov.objective_and_gradient(data, _dov.CPL, full)
    return float(chi2), np.asarray(gradient[:2], dtype=float)


def fit_fixed_wa(
    data: _dov.DovekieData,
    wa: float,
    starts: Sequence[Sequence[float]],
    *,
    maxiter: int = 180,
    ftol: float = 1.0e-10,
) -> dict[str, Any]:
    bounds = [(0.10, 0.60), (-2.0, -0.3)]
    runs: list[dict[str, Any]] = []
    for index, start in enumerate(starts):
        initial = np.asarray(start, dtype=float)
        if initial.shape != (2,):
            raise ValueError("fixed-wa start must contain Omega_m,w0")
        started = time.perf_counter()
        result = minimize(
            lambda x: fixed_wa_objective_gradient(data, np.asarray(x, dtype=float), wa),
            initial,
            method="L-BFGS-B",
            jac=True,
            bounds=bounds,
            options={"maxiter": int(maxiter), "ftol": float(ftol), "maxls": 40},
        )
        elapsed = time.perf_counter() - started
        free = np.asarray(result.x, dtype=float)
        full = np.asarray([free[0], free[1], float(wa)], dtype=float)
        chi2, offset, _ = _dov.profiled_likelihood(data, _dov.CPL, full)
        runs.append(
            {
                "start_index": index,
                "initial": {"Omega_m": float(initial[0]), "w0": float(initial[1])},
                "Omega_m": float(free[0]),
                "w0": float(free[1]),
                "wa": float(wa),
                "M_offset_profiled": float(offset),
                "chi2": float(chi2),
                "success": bool(result.success),
                "message": str(result.message),
                "iterations": int(result.nit),
                "function_evaluations": int(result.nfev),
                "runtime_seconds": float(elapsed),
            }
        )
    best = min(runs, key=lambda row: row["chi2"])
    return {
        "wa": float(wa),
        "chi2": float(best["chi2"]),
        "Omega_m": float(best["Omega_m"]),
        "w0": float(best["w0"]),
        "M_offset_profiled": float(best["M_offset_profiled"]),
        "all_starts_converged": all(row["success"] for row in runs),
        "runs": runs,
    }


def classify_profile(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    if len(rows) < 5:
        raise ValueError("wa profile requires at least five grid points")
    ordered = sorted(rows, key=lambda row: float(row["wa"]))
    wa = np.asarray([float(row["wa"]) for row in ordered], dtype=float)
    chi2 = np.asarray([float(row["chi2"]) for row in ordered], dtype=float)
    if np.any(~np.isfinite(wa)) or np.any(~np.isfinite(chi2)) or np.any(np.diff(wa) <= 0.0):
        raise ValueError("wa profile grid must be finite and strictly increasing")
    best_index = int(np.argmin(chi2))
    delta = chi2 - chi2[best_index]
    minimum_at_profile_edge = best_index in {0, len(ordered) - 1}

    below_95 = delta <= 3.841458820694124
    below_1s = delta <= 1.0
    interval_95 = [float(np.min(wa[below_95])), float(np.max(wa[below_95]))]
    interval_1s = [float(np.min(wa[below_1s])), float(np.max(wa[below_1s]))]

    has_left_exclusion_95 = bool(np.any((wa < wa[best_index]) & (delta > 3.841458820694124)))
    has_right_exclusion_95 = bool(np.any((wa > wa[best_index]) & (delta > 3.841458820694124)))
    bounded_95_on_grid = (not minimum_at_profile_edge) and has_left_exclusion_95 and has_right_exclusion_95

    state = "VERIFIED_BOUNDED_PROFILE" if bounded_95_on_grid else "VERIFIED_LIMITED_EDGE_OR_OPEN_PROFILE"
    return {
        "state": state,
        "best_index": best_index,
        "best_wa": float(wa[best_index]),
        "best_chi2": float(chi2[best_index]),
        "minimum_at_profile_edge": minimum_at_profile_edge,
        "bounded_95_on_grid": bounded_95_on_grid,
        "wa_1sigma_grid_interval": interval_1s,
        "wa_95_grid_interval": interval_95,
        "has_left_exclusion_95": has_left_exclusion_95,
        "has_right_exclusion_95": has_right_exclusion_95,
        "delta_chi2": [float(value) for value in delta],
    }


def build_profile(
    hd_path: Path,
    precision_path: Path,
    output_path: Path,
    *,
    wa_values: Sequence[float],
    maxiter: int = 180,
    ftol: float = 1.0e-10,
    integration_points: int = 4096,
) -> dict[str, Any]:
    started = time.perf_counter()
    values = sorted(set(float(value) for value in wa_values))
    if len(values) < 5:
        raise ValueError("at least five unique wa values are required")
    if values[0] >= -3.0:
        raise ValueError("profile must extend below the historical wa=-3 lower bound")

    data, original_rows = _dov.load_data(hd_path, precision_path, integration_points=integration_points)
    rows: list[dict[str, Any]] = []
    continuation: tuple[float, float] | None = None
    for wa in values:
        starts: list[tuple[float, float]] = [(0.30, -1.0), (0.42, -0.80)]
        if continuation is not None:
            starts.insert(0, continuation)
        row = fit_fixed_wa(data, wa, starts, maxiter=maxiter, ftol=ftol)
        continuation = (float(row["Omega_m"]), float(row["w0"]))
        rows.append(row)

    classification = classify_profile(rows)
    for row, delta in zip(sorted(rows, key=lambda item: item["wa"]), classification["delta_chi2"]):
        row["delta_chi2"] = float(delta)

    all_converged = all(row["all_starts_converged"] for row in rows)
    if not all_converged:
        state = "TOKEN_VAZIO_PROFILE_CONVERGENCE"
    else:
        state = classification["state"]

    token_vazio = (
        []
        if state == "VERIFIED_BOUNDED_PROFILE"
        else ["TOKEN_VAZIO_CPL_DOVEKIE_WA_LOWER_PROFILE_CLOSURE"]
    )
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "state": state,
        "claim_allowed": False,
        "publication_ready": False,
        "source_sha256": _dov.sha256_file(hd_path),
        "precision_sha256": _dov.sha256_file(precision_path),
        "n_supernovae": data.n,
        "original_rows": original_rows,
        "nuisance_policy": "one additive SN magnitude offset analytically profiled; H0 fixed only as a reference distance scale and not inferred",
        "profile_parameter": "wa",
        "historical_bound": [-3.0, 3.0],
        "profile_grid": values,
        "classification": classification,
        "rows": sorted(rows, key=lambda item: item["wa"]),
        "all_starts_converged": all_converged,
        "runtime_seconds": float(time.perf_counter() - started),
        "scientific_boundary": "A frequentist profile-likelihood sensitivity scan tests whether the previous wa=-3 optimum was imposed by the declared bound. It is not a posterior interval and not Bayesian evidence.",
        "token_vazio": token_vazio,
        "F_ok": [
            "The wa scan extends below the historical -3 bound while holding the Dovekie data, precision matrix and nuisance policy fixed.",
            "Omega_m and w0 are re-optimized at every fixed wa value.",
            "The result explicitly records whether the expanded profile remains edge-limited or lacks one-sided 95% closure."
        ],
        "F_gap": [] if state == "VERIFIED_BOUNDED_PROFILE" else [
            "The expanded wa profile is not yet bounded at 95% on both sides of the best grid point, or one/more optimization starts did not converge."
        ],
        "F_next": [
            "If no left-side 95% exclusion is observed, extend the lower wa grid and characterize whether the direction approaches an asymptotic/non-identifiable degeneracy.",
            "If the profile becomes bounded, use it only as a frequentist diagnostic and retain modern three-model nested-sampling evidence as a separate P0 gate."
        ],
    }
    _atomic_json(output_path, payload)
    return payload


def parse_grid(text: str) -> list[float]:
    values = [float(value.strip()) for value in text.split(",") if value.strip()]
    if len(set(values)) < 5:
        raise ValueError("wa-grid must contain at least five unique values")
    return sorted(set(values))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Profile DES-Dovekie CPL wa beyond the historical lower bound")
    parser.add_argument("--hd", type=Path, required=True)
    parser.add_argument("--precision", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--wa-grid", default="-8,-6,-5,-4,-3,-2,-1,0,1,2,3")
    parser.add_argument("--maxiter", type=int, default=180)
    parser.add_argument("--ftol", type=float, default=1.0e-10)
    parser.add_argument("--integration-points", type=int, default=4096)
    args = parser.parse_args(argv)
    try:
        payload = build_profile(
            args.hd,
            args.precision,
            args.output,
            wa_values=parse_grid(args.wa_grid),
            maxiter=args.maxiter,
            ftol=args.ftol,
            integration_points=args.integration_points,
        )
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 2
    info = payload["classification"]
    print(
        f"{payload['state']} best_wa={info['best_wa']:.8g} "
        f"edge={str(info['minimum_at_profile_edge']).lower()} "
        f"bounded95={str(info['bounded_95_on_grid']).lower()} claim_allowed=false"
    )
    return 0 if payload["state"] != "TOKEN_VAZIO_PROFILE_CONVERGENCE" else 3


if __name__ == "__main__":
    raise SystemExit(main())
