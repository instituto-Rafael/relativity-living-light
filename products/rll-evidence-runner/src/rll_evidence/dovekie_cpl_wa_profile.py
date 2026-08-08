from __future__ import annotations

"""Profile-likelihood sensitivity for the DES-Dovekie CPL wa lower tail.

The production three-model fit found wa at its declared lower bound (-3). This
module expands the finite wa scan and also evaluates the mathematical
wa -> -infinity CPL distance-limit for z>0.  If that asymptotic likelihood stays
inside the 95% profile region, the absence of a finite lower wa constraint is a
negative identifiability result rather than an indefinitely empty token.
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

SCHEMA = "rll_dovekie_cpl_wa_profile_v2"
DELTA_CHI2_95_1DOF = 3.841458820694124


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


def asymptotic_cpl_distance_modulus(data: _dov.DovekieData, omega_m: float) -> np.ndarray:
    """Return the wa -> -infinity CPL luminosity-distance limit.

    For every fixed z>0,
      rho_DE(z)/rho_DE(0) = (1+z)^[3(1+w0+wa)] exp[-3 wa z/(1+z)]
    tends to zero because log(1+z)-z/(1+z) > 0. The shrinking z≈0 boundary
    layer has zero measure in the distance integral, so the integral limit uses
    the matter+radiation right-limit. w0 drops out and is therefore structurally
    unidentifiable in this tail.
    """
    z = data.integration_grid
    zp1 = 1.0 + z
    e2_limit = float(omega_m) * zp1**3 + _dov.OMEGA_R0 * zp1**4
    if np.any(~np.isfinite(e2_limit)) or np.any(e2_limit <= 0.0):
        raise ValueError("invalid asymptotic CPL expansion limit")
    inverse_hubble = _dov.C_KM_S / (_dov.H0_REFERENCE * np.sqrt(e2_limit))
    dz = np.diff(z)
    comoving = np.concatenate(
        ([0.0], np.cumsum(0.5 * (inverse_hubble[:-1] + inverse_hubble[1:]) * dz))
    )
    dc = np.interp(data.z_hd, z, comoving)
    luminosity_distance = (1.0 + data.z_hel) * dc
    if np.any(luminosity_distance <= 0.0):
        raise ValueError("non-positive asymptotic CPL luminosity distance")
    return 5.0 * np.log10(luminosity_distance) + 25.0


def asymptotic_profiled_likelihood(
    data: _dov.DovekieData, omega_m: float
) -> tuple[float, float]:
    model_mu = asymptotic_cpl_distance_modulus(data, omega_m)
    difference = model_mu - data.mu_obs
    weighted = data.precision @ difference
    offset_hat = -float(np.sum(weighted)) / data.one_precision_one
    profiled = difference + offset_hat
    weighted_profiled = weighted + offset_hat * data.precision_ones
    chi2 = float(profiled @ weighted_profiled)
    if not math.isfinite(chi2) or chi2 < -1.0e-7:
        raise ValueError("invalid asymptotic CPL chi2")
    return max(0.0, chi2), float(offset_hat)


def fit_asymptotic_limit(
    data: _dov.DovekieData,
    *,
    maxiter: int = 180,
    ftol: float = 1.0e-10,
) -> dict[str, Any]:
    runs: list[dict[str, Any]] = []
    for start in (0.25, 0.35, 0.50):
        started = time.perf_counter()
        result = minimize(
            lambda x: asymptotic_profiled_likelihood(data, float(np.asarray(x)[0]))[0],
            np.asarray([start], dtype=float),
            method="L-BFGS-B",
            bounds=[(0.10, 0.60)],
            options={"maxiter": int(maxiter), "ftol": float(ftol), "maxls": 40},
        )
        omega_m = float(result.x[0])
        chi2, offset = asymptotic_profiled_likelihood(data, omega_m)
        runs.append(
            {
                "initial_Omega_m": float(start),
                "Omega_m": omega_m,
                "M_offset_profiled": offset,
                "chi2": chi2,
                "success": bool(result.success),
                "message": str(result.message),
                "iterations": int(result.nit),
                "function_evaluations": int(result.nfev),
                "runtime_seconds": float(time.perf_counter() - started),
            }
        )
    best = min(runs, key=lambda row: row["chi2"])
    return {
        "limit": "wa_to_minus_infinity",
        "w0_identifiable_in_limit": False,
        "Omega_m": float(best["Omega_m"]),
        "M_offset_profiled": float(best["M_offset_profiled"]),
        "chi2": float(best["chi2"]),
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

    below_95 = delta <= DELTA_CHI2_95_1DOF
    below_1s = delta <= 1.0
    interval_95 = [float(np.min(wa[below_95])), float(np.max(wa[below_95]))]
    interval_1s = [float(np.min(wa[below_1s])), float(np.max(wa[below_1s]))]

    has_left_exclusion_95 = bool(np.any((wa < wa[best_index]) & (delta > DELTA_CHI2_95_1DOF)))
    has_right_exclusion_95 = bool(np.any((wa > wa[best_index]) & (delta > DELTA_CHI2_95_1DOF)))
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
    ordered_rows = sorted(rows, key=lambda item: item["wa"])
    for row, delta in zip(ordered_rows, classification["delta_chi2"]):
        row["delta_chi2"] = float(delta)

    asymptotic = fit_asymptotic_limit(data, maxiter=maxiter, ftol=ftol)
    overall_best_chi2 = min(float(classification["best_chi2"]), float(asymptotic["chi2"]))
    asymptotic_delta = float(asymptotic["chi2"] - overall_best_chi2)
    asymptotic["delta_chi2_from_overall_best"] = asymptotic_delta
    asymptotic["inside_95_profile"] = bool(asymptotic_delta <= DELTA_CHI2_95_1DOF)

    finite_converged = all(row["all_starts_converged"] for row in rows)
    all_converged = finite_converged and bool(asymptotic["all_starts_converged"])
    asymptotic_non_identifiable = (
        all_converged
        and asymptotic["inside_95_profile"]
        and not classification["has_left_exclusion_95"]
    )

    if not all_converged:
        state = "TOKEN_VAZIO_PROFILE_CONVERGENCE"
    elif asymptotic_non_identifiable:
        state = "VERIFIED_ASYMPTOTIC_LOWER_NON_IDENTIFIABILITY"
    elif classification["bounded_95_on_grid"]:
        state = "VERIFIED_BOUNDED_PROFILE"
    else:
        state = "VERIFIED_LIMITED_EDGE_OR_OPEN_PROFILE"

    token_vazio = (
        []
        if state in {"VERIFIED_BOUNDED_PROFILE", "VERIFIED_ASYMPTOTIC_LOWER_NON_IDENTIFIABILITY"}
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
        "asymptotic_limit": asymptotic,
        "rows": ordered_rows,
        "all_starts_converged": all_converged,
        "runtime_seconds": float(time.perf_counter() - started),
        "scientific_boundary": "This is a frequentist profile-identifiability diagnostic. The analytic wa→-∞ limit tests whether a finite lower 95% bound exists in this SN-only likelihood; it is not a posterior interval and not Bayesian evidence.",
        "token_vazio": token_vazio,
        "F_ok": [
            "The finite wa scan extends below the historical -3 bound while holding Dovekie data, precision and nuisance policy fixed.",
            "Omega_m and w0 are re-optimized at every finite wa value.",
            "The wa→-∞ likelihood limit is evaluated directly rather than inferred by arbitrarily extending a finite grid.",
        ],
        "F_gap": [] if not token_vazio else [
            "The lower profile is not yet closed or asymptotically characterized because the limiting fit/convergence does not satisfy the declared 95% criterion."
        ],
        "F_next": [
            "If the asymptotic limit lies inside the 95% region, record wa lower-tail non-identifiability as a terminal negative SN-only result.",
            "Keep proper prior-locked nested evidence separate because Bayesian evidence remains prior-volume dependent even when a frequentist lower bound is absent."
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
    parser = argparse.ArgumentParser(description="Profile DES-Dovekie CPL wa and test its analytic lower-tail limit")
    parser.add_argument("--hd", type=Path, required=True)
    parser.add_argument("--precision", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--wa-grid", default="-12,-10,-8,-6,-5,-4,-3,-2,-1,0,1,2,3")
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
    asym = payload["asymptotic_limit"]
    print(
        f"{payload['state']} best_wa={info['best_wa']:.8g} "
        f"asymptotic_delta_chi2={asym['delta_chi2_from_overall_best']:.8g} "
        f"asymptotic_inside95={str(asym['inside_95_profile']).lower()} claim_allowed=false"
    )
    return 0 if payload["state"] != "TOKEN_VAZIO_PROFILE_CONVERGENCE" else 3


if __name__ == "__main__":
    raise SystemExit(main())
