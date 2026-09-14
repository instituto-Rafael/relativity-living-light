from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

import numpy as np
from scipy.linalg import LinAlgError, cho_factor, cho_solve
from scipy.optimize import minimize

C_KM_S = 299_792.458
OMEGA_R0 = 9.0e-5
SCHEMA = "rll_pantheon_full_covariance_fit_v1"
LCDM = "LCDM_pantheon_full"
RLL = "RLL_pantheon_full"

MODEL_SPECS: dict[str, dict[str, Any]] = {
    LCDM: {
        "parameter_names": ("H0", "Omega_m"),
        "bounds": ((60.0, 80.0), (0.10, 0.60)),
        "canonical_start": (70.0, 0.30),
        "k_including_profiled_M_B": 3,
    },
    RLL: {
        "parameter_names": ("H0", "Omega_m", "Omega_s0", "z_t", "w_t"),
        "bounds": ((60.0, 80.0), (0.10, 0.60), (0.0, 0.25), (0.10, 10.0), (0.05, 2.0)),
        "canonical_start": (70.0, 0.30, 0.0, 1.0, 0.30),
        "k_including_profiled_M_B": 6,
    },
}


@dataclass
class PantheonData:
    z_hd: np.ndarray
    z_hel: np.ndarray
    m_b_corr: np.ndarray
    ceph_dist: np.ndarray
    is_calibrator: np.ndarray
    covariance: np.ndarray
    cholesky: tuple[np.ndarray, bool]
    cinv_ones: np.ndarray
    one_cinv_one: float
    integration_grid: np.ndarray

    @property
    def n(self) -> int:
        return int(self.z_hd.size)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        temporary = Path(handle.name)
        json.dump(payload, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def load_catalog(path: Path, *, z_min: float = 0.01) -> dict[str, np.ndarray]:
    table = np.genfromtxt(path, names=True, dtype=None, encoding="utf-8")
    if table.shape == ():
        table = np.asarray([table], dtype=table.dtype)
    required = {"zHD", "zHEL", "m_b_corr", "CEPH_DIST", "IS_CALIBRATOR"}
    available = set(table.dtype.names or ())
    missing = sorted(required - available)
    if missing:
        raise ValueError(f"Pantheon+ catalog missing columns: {missing}")
    z_hd = np.asarray(table["zHD"], dtype=float)
    is_calibrator = np.asarray(table["IS_CALIBRATOR"], dtype=int) == 1
    selection = (z_hd > float(z_min)) | is_calibrator
    if np.count_nonzero(selection) < 3:
        raise ValueError("Pantheon+ selection retained fewer than three rows")
    return {
        "original_rows": np.asarray([len(z_hd)], dtype=int),
        "selection": selection,
        "z_hd": z_hd[selection],
        "z_hel": np.asarray(table["zHEL"], dtype=float)[selection],
        "m_b_corr": np.asarray(table["m_b_corr"], dtype=float)[selection],
        "ceph_dist": np.asarray(table["CEPH_DIST"], dtype=float)[selection],
        "is_calibrator": is_calibrator[selection],
    }


def load_covariance(path: Path, expected_n: int) -> np.ndarray:
    tokens = np.fromfile(path, dtype=float, sep=" ")
    if tokens.size < 1:
        raise ValueError("empty covariance file")
    dimension = int(tokens[0])
    values = tokens[1:]
    if dimension != expected_n:
        raise ValueError(f"covariance dimension={dimension}, catalog rows={expected_n}")
    expected_values = dimension * dimension
    if values.size != expected_values:
        raise ValueError(f"covariance values={values.size}, expected={expected_values}")
    covariance = values.reshape((dimension, dimension))
    if not np.all(np.isfinite(covariance)):
        raise ValueError("covariance contains non-finite values")
    asymmetry = float(np.max(np.abs(covariance - covariance.T)))
    scale = max(1.0, float(np.max(np.abs(covariance))))
    if asymmetry > 1.0e-10 * scale:
        raise ValueError(f"covariance is not symmetric: max asymmetry={asymmetry}")
    if np.any(np.diag(covariance) <= 0.0):
        raise ValueError("covariance diagonal must be strictly positive")
    return covariance


def prepare_data(
    z_hd: Sequence[float],
    z_hel: Sequence[float],
    m_b_corr: Sequence[float],
    ceph_dist: Sequence[float],
    is_calibrator: Sequence[bool],
    covariance: np.ndarray,
    *,
    integration_points: int = 4096,
) -> PantheonData:
    arrays = [np.asarray(item) for item in (z_hd, z_hel, m_b_corr, ceph_dist, is_calibrator)]
    n = int(arrays[0].size)
    if n < 3 or any(array.size != n for array in arrays):
        raise ValueError("catalog arrays must have the same length >= 3")
    if covariance.shape != (n, n):
        raise ValueError(f"covariance shape {covariance.shape} does not match {(n, n)}")
    numeric = np.concatenate([np.asarray(array, dtype=float) for array in arrays[:4]])
    if not np.all(np.isfinite(numeric)):
        raise ValueError("catalog contains non-finite numeric values")
    z_hd_arr = np.asarray(arrays[0], dtype=float)
    z_hel_arr = np.asarray(arrays[1], dtype=float)
    calibrator_arr = np.asarray(arrays[4], dtype=bool)
    if np.any(z_hd_arr[~calibrator_arr] <= 0.0) or np.any(z_hel_arr[~calibrator_arr] <= -1.0):
        raise ValueError("non-calibrator redshifts are outside the luminosity-distance domain")
    if np.any(np.asarray(arrays[3], dtype=float)[calibrator_arr] <= 0.0):
        raise ValueError("calibrator rows require positive CEPH_DIST distance moduli")
    try:
        factor = cho_factor(np.asarray(covariance, dtype=float), lower=True, check_finite=True)
    except LinAlgError as exc:
        raise ValueError("covariance is not positive definite; no jitter is applied") from exc
    ones = np.ones(n, dtype=float)
    cinv_ones = cho_solve(factor, ones, check_finite=False)
    one_cinv_one = float(ones @ cinv_ones)
    if not math.isfinite(one_cinv_one) or one_cinv_one <= 0.0:
        raise ValueError("invalid 1^T C^-1 1 normalization")
    z_max = max(0.01, float(np.max(z_hd_arr)))
    base_grid = np.linspace(0.0, z_max, max(64, int(integration_points)), dtype=float)
    integration_grid = np.unique(np.concatenate((base_grid, np.clip(z_hd_arr, 0.0, None))))
    return PantheonData(
        z_hd=z_hd_arr,
        z_hel=z_hel_arr,
        m_b_corr=np.asarray(arrays[2], dtype=float),
        ceph_dist=np.asarray(arrays[3], dtype=float),
        is_calibrator=calibrator_arr,
        covariance=np.asarray(covariance, dtype=float),
        cholesky=factor,
        cinv_ones=cinv_ones,
        one_cinv_one=one_cinv_one,
        integration_grid=integration_grid,
    )


def load_data(
    catalog_path: Path,
    covariance_path: Path,
    *,
    integration_points: int = 4096,
    z_min: float = 0.01,
) -> tuple[PantheonData, int]:
    catalog = load_catalog(catalog_path, z_min=z_min)
    original_rows = int(catalog.pop("original_rows")[0])
    selection = np.asarray(catalog.pop("selection"), dtype=bool)
    full_covariance = load_covariance(covariance_path, original_rows)
    covariance = full_covariance[np.ix_(selection, selection)]
    return (
        prepare_data(covariance=covariance, integration_points=integration_points, **catalog),
        original_rows,
    )


def transition_f(z: np.ndarray, z_t: float, w_t: float) -> np.ndarray:
    argument = np.clip((z - float(z_t)) / float(w_t), -500.0, 500.0)
    return 1.0 / (1.0 + np.exp(argument))


def e2(model: str, z: np.ndarray, parameters: Sequence[float]) -> np.ndarray:
    z_array = np.asarray(z, dtype=float)
    zp1 = 1.0 + z_array
    if model == LCDM:
        _, omega_m = map(float, parameters)
        omega_lambda = 1.0 - omega_m - OMEGA_R0
        value = omega_m * zp1**3 + OMEGA_R0 * zp1**4 + omega_lambda
    elif model == RLL:
        _, omega_m, omega_s0, z_t, w_t = map(float, parameters)
        omega_lambda = 1.0 - omega_m - OMEGA_R0 - omega_s0
        if omega_lambda <= 0.0:
            return np.full_like(z_array, np.nan)
        f_z = transition_f(z_array, z_t, w_t)
        superposition = omega_s0 * (f_z + (1.0 - f_z) * zp1**3)
        value = omega_m * zp1**3 + OMEGA_R0 * zp1**4 + omega_lambda + superposition
    else:
        raise ValueError(f"unsupported model: {model}")
    return value


def distance_modulus(data: PantheonData, model: str, parameters: Sequence[float]) -> np.ndarray:
    h0 = float(parameters[0])
    expansion_squared = e2(model, data.integration_grid, parameters)
    if h0 <= 0.0 or np.any(~np.isfinite(expansion_squared)) or np.any(expansion_squared <= 0.0):
        raise ValueError("non-physical expansion history")
    inverse_hubble = C_KM_S / (h0 * np.sqrt(expansion_squared))
    dz = np.diff(data.integration_grid)
    comoving = np.concatenate(
        ([0.0], np.cumsum(0.5 * (inverse_hubble[:-1] + inverse_hubble[1:]) * dz))
    )
    dc = np.interp(data.z_hd, data.integration_grid, comoving)
    luminosity_distance = (1.0 + data.z_hel) * dc
    if np.any(luminosity_distance[~data.is_calibrator] <= 0.0):
        raise ValueError("non-positive luminosity distance")
    predicted = np.empty(data.n, dtype=float)
    predicted[data.is_calibrator] = data.ceph_dist[data.is_calibrator]
    non_calibrator = ~data.is_calibrator
    predicted[non_calibrator] = 5.0 * np.log10(luminosity_distance[non_calibrator]) + 25.0
    return predicted


def profiled_likelihood(
    data: PantheonData, model: str, parameters: Sequence[float]
) -> tuple[float, float, np.ndarray]:
    mu = distance_modulus(data, model, parameters)
    difference = data.m_b_corr - mu
    cinv_difference = cho_solve(data.cholesky, difference, check_finite=False)
    m_b_hat = float((np.ones(data.n) @ cinv_difference) / data.one_cinv_one)
    profiled_residual = difference - m_b_hat
    weighted_residual = cinv_difference - m_b_hat * data.cinv_ones
    chi2 = float(profiled_residual @ weighted_residual)
    if chi2 < -1.0e-7 or not math.isfinite(chi2):
        raise ValueError(f"invalid profiled chi2: {chi2}")
    return max(0.0, chi2), m_b_hat, weighted_residual


def objective_and_gradient(
    data: PantheonData, model: str, parameters: np.ndarray
) -> tuple[float, np.ndarray]:
    chi2, _, weighted_residual = profiled_likelihood(data, model, parameters)
    bounds = MODEL_SPECS[model]["bounds"]
    gradient = np.zeros_like(parameters, dtype=float)
    for index, (lower, upper) in enumerate(bounds):
        scale = max(1.0, abs(float(parameters[index])), float(upper - lower))
        step = 1.0e-5 * scale
        low = max(float(lower), float(parameters[index]) - step)
        high = min(float(upper), float(parameters[index]) + step)
        if high <= low:
            continue
        plus = np.asarray(parameters, dtype=float).copy()
        minus = np.asarray(parameters, dtype=float).copy()
        plus[index] = high
        minus[index] = low
        d_residual = -(
            distance_modulus(data, model, plus) - distance_modulus(data, model, minus)
        ) / (high - low)
        gradient[index] = 2.0 * float(d_residual @ weighted_residual)
    return chi2, gradient


def information_criteria(chi2: float, n: int, k: int) -> dict[str, float | int]:
    aic = float(chi2 + 2.0 * k)
    denominator = n - k - 1
    aicc = float(aic + (2.0 * k * (k + 1) / denominator)) if denominator > 0 else math.inf
    bic = float(chi2 + k * math.log(n))
    return {
        "chi2": float(chi2),
        "AIC": aic,
        "AICc": aicc,
        "BIC": bic,
        "N": n,
        "k": k,
        "dof": n - k,
    }


def _start_for_seed(model: str, seed: int, index: int) -> tuple[np.ndarray, str]:
    spec = MODEL_SPECS[model]
    if index == 0:
        return np.asarray(spec["canonical_start"], dtype=float), "canonical_null_nested_start"
    rng = np.random.default_rng(int(seed))
    bounds = np.asarray(spec["bounds"], dtype=float)
    return rng.uniform(bounds[:, 0], bounds[:, 1]), "seeded_uniform_multistart"


def fit_model(
    data: PantheonData,
    model: str,
    seeds: Sequence[int],
    *,
    maxiter: int = 250,
    ftol: float = 1.0e-10,
) -> dict[str, Any]:
    if model not in MODEL_SPECS:
        raise ValueError(f"unsupported model: {model}")
    if not seeds:
        raise ValueError("at least one seed is required")
    spec = MODEL_SPECS[model]
    bounds = list(spec["bounds"])
    runs: list[dict[str, Any]] = []
    for index, seed in enumerate(seeds):
        initial, strategy = _start_for_seed(model, int(seed), index)
        started = time.perf_counter()
        result = minimize(
            lambda x: objective_and_gradient(data, model, np.asarray(x, dtype=float)),
            initial,
            method="L-BFGS-B",
            jac=True,
            bounds=bounds,
            options={"maxiter": int(maxiter), "ftol": float(ftol), "maxls": 40},
        )
        elapsed = time.perf_counter() - started
        parameters = np.asarray(result.x, dtype=float)
        chi2, m_b_hat, _ = profiled_likelihood(data, model, parameters)
        boundary_hits = []
        for name, value, (lower, upper) in zip(spec["parameter_names"], parameters, bounds):
            tolerance = 1.0e-5 * max(1.0, upper - lower)
            if abs(float(value) - lower) <= tolerance or abs(float(value) - upper) <= tolerance:
                boundary_hits.append(name)
        runs.append(
            {
                "seed": int(seed),
                "start_strategy": strategy,
                "initial_parameters": {
                    name: float(value) for name, value in zip(spec["parameter_names"], initial)
                },
                "parameters": {
                    name: float(value) for name, value in zip(spec["parameter_names"], parameters)
                },
                "M_B_profiled": float(m_b_hat),
                "chi2": float(chi2),
                "success": bool(result.success),
                "message": str(result.message),
                "iterations": int(result.nit),
                "function_evaluations": int(result.nfev),
                "gradient_evaluations": int(getattr(result, "njev", 0)),
                "runtime_seconds": float(elapsed),
                "boundary_hits": boundary_hits,
            }
        )
    best = min(runs, key=lambda item: item["chi2"])
    chi_values = np.asarray([item["chi2"] for item in runs], dtype=float)
    k = int(spec["k_including_profiled_M_B"])
    row = {
        "model": model,
        **information_criteria(float(best["chi2"]), data.n, k),
        "M_B_profiled": float(best["M_B_profiled"]),
        **best["parameters"],
    }
    return {
        "model": model,
        "status": "PASS" if all(item["success"] for item in runs) else "TOKEN_VAZIO_CONVERGENCE",
        "best_seed": int(best["seed"]),
        "best": row,
        "stability": {
            "seed_count": len(runs),
            "converged_count": sum(bool(item["success"]) for item in runs),
            "chi2_min": float(np.min(chi_values)),
            "chi2_max": float(np.max(chi_values)),
            "chi2_span": float(np.ptp(chi_values)),
            "all_finite": bool(np.all(np.isfinite(chi_values))),
        },
        "runs": runs,
    }


def build_result(
    catalog_path: Path,
    covariance_path: Path,
    output_path: Path,
    *,
    seeds: Sequence[int],
    maxiter: int = 250,
    ftol: float = 1.0e-10,
    integration_points: int = 4096,
    z_min: float = 0.01,
) -> dict[str, Any]:
    started = time.perf_counter()
    data, original_rows = load_data(
        catalog_path,
        covariance_path,
        integration_points=integration_points,
        z_min=z_min,
    )
    lcdm = fit_model(data, LCDM, seeds, maxiter=maxiter, ftol=ftol)
    rll = fit_model(data, RLL, seeds, maxiter=maxiter, ftol=ftol)
    rows = [lcdm["best"], rll["best"]]
    baseline, candidate = rows
    deltas = {
        metric: float(candidate[metric] - baseline[metric])
        for metric in ("chi2", "AIC", "AICc", "BIC")
    }
    delta_bic = deltas["BIC"]
    if delta_bic <= -10.0:
        interpretation = "candidate_numerically_preferred_in_pantheon_only_likelihood"
    elif delta_bic >= 10.0:
        interpretation = "lcdm_numerically_preferred_in_pantheon_only_likelihood"
    else:
        interpretation = "pantheon_only_likelihood_inconclusive_by_bic"
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "status": (
            "PASS_LIMITED"
            if lcdm["status"] == rll["status"] == "PASS"
            else "TOKEN_VAZIO_CONVERGENCE"
        ),
        "claim_allowed": False,
        "publication_effect": "NONE",
        "scientific_boundary": (
            "A full-covariance Pantheon+SH0ES numerical fit is one likelihood block; "
            "it is not external validation, model confirmation, or a superiority claim."
        ),
        "inputs": {
            "catalog": {
                "path": str(catalog_path),
                "bytes": catalog_path.stat().st_size,
                "sha256": sha256_file(catalog_path),
            },
            "covariance": {
                "path": str(covariance_path),
                "bytes": covariance_path.stat().st_size,
                "sha256": sha256_file(covariance_path),
            },
            "original_rows": original_rows,
            "selected_rows": data.n,
            "covariance_shape_after_selection": [data.n, data.n],
        },
        "method": {
            "observable": "m_b_corr",
            "selection": f"(zHD > {float(z_min):.8g}) OR IS_CALIBRATOR==1",
            "include_shoes": True,
            "calibrator_prediction": "CEPH_DIST",
            "non_calibrator_distance": "(1+zHEL)*D_C(zHD)",
            "covariance": "full_statistical_plus_systematic",
            "linear_algebra": "Cholesky solve; no diagonal approximation; no jitter",
            "nuisance": "M_B analytically profiled and counted in k",
            "optimizer": (
                "multi-start L-BFGS-B with finite-difference model Jacobian "
                "and profiled likelihood gradient"
            ),
            "seeds": [int(seed) for seed in seeds],
            "maxiter": int(maxiter),
            "ftol": float(ftol),
            "integration_points": int(integration_points),
            "flat_closure": True,
        },
        "rows": rows,
        "models": {LCDM: lcdm, RLL: rll},
        "comparison": {
            "baseline": LCDM,
            "candidate": RLL,
            "candidate_minus_baseline": deltas,
        },
        "interpretation_label": interpretation,
        "runtime_seconds": float(time.perf_counter() - started),
        "environment": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "platform": platform.platform(),
        },
        "F_ok": [
            "Pantheon+ calibrator and Hubble-flow rows share one full covariance likelihood.",
            "The absolute magnitude nuisance is profiled analytically and counted in information criteria.",
            "LCDM and RLL use identical catalog, covariance, common bounds, seeds, optimizer, and integration grid.",
        ],
        "F_gap": [
            "Pantheon+ alone does not test growth, BAO, CMB, or independent replication.",
            "Numerical convergence and cross-implementation reproduction remain required before scientific interpretation.",
        ],
        "F_next": [
            "Reproduce the receipt on an independent machine and compare hashes and fitted metrics.",
            "Compose this likelihood with DESI BAO, H(z), growth, and compressed CMB without overwriting historical artifacts.",
        ],
    }
    _atomic_json(output_path, payload)
    return payload


def parse_seeds(text: str) -> list[int]:
    seeds = [int(token.strip()) for token in text.split(",") if token.strip()]
    if not seeds or len(set(seeds)) != len(seeds):
        raise ValueError("seeds must be a non-empty comma-separated list of unique integers")
    return seeds


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Full-covariance Pantheon+SH0ES LCDM/RLL fit")
    parser.add_argument("--catalog", type=Path, required=True)
    parser.add_argument("--covariance", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seeds", default="11,23,37,53,71")
    parser.add_argument("--maxiter", type=int, default=250)
    parser.add_argument("--ftol", type=float, default=1.0e-10)
    parser.add_argument("--integration-points", type=int, default=4096)
    parser.add_argument("--z-min", type=float, default=0.01)
    args = parser.parse_args(argv)
    try:
        seeds = parse_seeds(args.seeds)
        if args.maxiter < 1 or args.integration_points < 64:
            raise ValueError("maxiter must be >=1 and integration-points >=64")
        payload = build_result(
            args.catalog,
            args.covariance,
            args.output,
            seeds=seeds,
            maxiter=args.maxiter,
            ftol=args.ftol,
            integration_points=args.integration_points,
            z_min=args.z_min,
        )
    except (OSError, ValueError, LinAlgError) as exc:
        print(json.dumps({"status": "FAIL", "claim_allowed": False, "error": str(exc)}, sort_keys=True))
        return 2
    print(
        json.dumps(
            {
                "status": payload["status"],
                "output": str(args.output),
                "delta_BIC": payload["comparison"]["candidate_minus_baseline"]["BIC"],
                "claim_allowed": False,
            },
            sort_keys=True,
        )
    )
    return 0 if payload["status"] == "PASS_LIMITED" else 3


if __name__ == "__main__":
    raise SystemExit(main())
