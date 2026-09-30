from __future__ import annotations

"""DES-Dovekie three-model likelihood: LCDM x CPL x RLL.

The official DES-Dovekie release stores STAT+SYS.npz as a packed upper-triangle
*inverse covariance* (precision) matrix.  The likelihood here uses that precision
directly and analytically profiles one additive SN magnitude offset.  H0 is kept
at a fixed reference value because the profiled offset is fully degenerate with
H0 for a supernova-only Hubble diagram; no H0 measurement is emitted.
"""

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
from scipy.optimize import minimize

C_KM_S = 299_792.458
OMEGA_R0 = 9.0e-5
H0_REFERENCE = 70.0
SCHEMA = "rll_dovekie_three_model_fit_v1"
LCDM = "LCDM_dovekie"
CPL = "CPL_dovekie"
RLL = "RLL_dovekie"

MODEL_SPECS: dict[str, dict[str, Any]] = {
    LCDM: {
        "parameter_names": ("Omega_m",),
        "bounds": ((0.10, 0.60),),
        "canonical_start": (0.30,),
        "k_including_profiled_offset": 2,
    },
    CPL: {
        "parameter_names": ("Omega_m", "w0", "wa"),
        "bounds": ((0.10, 0.60), (-2.0, -0.3), (-3.0, 3.0)),
        "canonical_start": (0.30, -1.0, 0.0),
        "k_including_profiled_offset": 4,
    },
    RLL: {
        "parameter_names": ("Omega_m", "Omega_s0", "z_t", "w_t"),
        "bounds": ((0.10, 0.60), (0.0, 0.25), (0.10, 10.0), (0.05, 2.0)),
        "canonical_start": (0.30, 0.0, 1.0, 0.30),
        "k_including_profiled_offset": 5,
    },
}


@dataclass
class DovekieData:
    z_hd: np.ndarray
    z_hel: np.ndarray
    mu_obs: np.ndarray
    muerr_diag: np.ndarray
    precision: np.ndarray
    precision_ones: np.ndarray
    one_precision_one: float
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
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", suffix=".part", delete=False
    ) as handle:
        temporary = Path(handle.name)
        json.dump(payload, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    try:
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def load_hd(path: Path) -> dict[str, np.ndarray]:
    names: list[str] | None = None
    rows: list[list[str]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, raw in enumerate(handle, 1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("VARNAMES:"):
                names = line.split()[1:]
                required = {"zHD", "zHEL", "MU", "MUERR"}
                missing = sorted(required.difference(names))
                if missing:
                    raise ValueError(f"Dovekie HD missing columns: {missing}")
                continue
            if line.startswith("SN:"):
                if names is None:
                    raise ValueError(f"SN row before VARNAMES at line {line_number}")
                values = line.split()[1:]
                if len(values) != len(names):
                    raise ValueError(f"Dovekie HD row width mismatch at line {line_number}")
                rows.append(values)
                continue
            raise ValueError(f"unsupported Dovekie HD record at line {line_number}")

    if names is None or not rows:
        raise ValueError("Dovekie HD contains no usable SN rows")
    index = {name: names.index(name) for name in ("zHD", "zHEL", "MU", "MUERR")}
    z_hd = np.asarray([float(row[index["zHD"]]) for row in rows], dtype=float)
    z_hel = np.asarray([float(row[index["zHEL"]]) for row in rows], dtype=float)
    mu = np.asarray([float(row[index["MU"]]) for row in rows], dtype=float)
    muerr = np.asarray([float(row[index["MUERR"]]) for row in rows], dtype=float)
    selection = z_hd > 0.0
    arrays = [z_hd, z_hel, mu, muerr]
    if any(np.any(~np.isfinite(array)) for array in arrays):
        raise ValueError("Dovekie HD contains non-finite values")
    if np.any(z_hel[selection] <= -1.0) or np.any(muerr[selection] <= 0.0):
        raise ValueError("Dovekie HD violates redshift/error domain")
    return {
        "selection": selection,
        "z_hd": z_hd[selection],
        "z_hel": z_hel[selection],
        "mu_obs": mu[selection],
        "muerr_diag": muerr[selection],
        "original_rows": np.asarray([len(rows)], dtype=int),
    }


def load_precision(path: Path, expected_n: int) -> np.ndarray:
    with np.load(path, allow_pickle=False) as archive:
        files = list(archive.files)
        if len(files) < 2:
            raise ValueError(f"Dovekie precision NPZ requires >=2 arrays, found {files}")
        n_array = np.asarray(archive[files[0]]).ravel()
        packed = np.asarray(archive[files[1]], dtype=float).ravel()
    if n_array.size < 1:
        raise ValueError("Dovekie precision NPZ dimension array is empty")
    dimension = int(n_array[0])
    if dimension != expected_n:
        raise ValueError(f"precision dimension={dimension}, HD rows={expected_n}")
    expected_values = dimension * (dimension + 1) // 2
    if packed.size != expected_values:
        raise ValueError(f"precision packed values={packed.size}, expected={expected_values}")
    if np.any(~np.isfinite(packed)):
        raise ValueError("Dovekie precision contains non-finite values")
    precision = np.zeros((dimension, dimension), dtype=float)
    upper = np.triu_indices(dimension)
    precision[upper] = packed
    lower = np.tril_indices(dimension, -1)
    precision[lower] = precision.T[lower]
    if np.any(np.diag(precision) <= 0.0):
        raise ValueError("Dovekie precision diagonal must be positive")
    try:
        np.linalg.cholesky(precision)
    except np.linalg.LinAlgError as exc:
        raise ValueError("Dovekie precision is not positive definite") from exc
    return precision


def prepare_data(
    z_hd: Sequence[float],
    z_hel: Sequence[float],
    mu_obs: Sequence[float],
    muerr_diag: Sequence[float],
    precision: np.ndarray,
    *,
    integration_points: int = 4096,
) -> DovekieData:
    arrays = [np.asarray(value, dtype=float) for value in (z_hd, z_hel, mu_obs, muerr_diag)]
    n = int(arrays[0].size)
    if n < 3 or any(array.size != n for array in arrays):
        raise ValueError("Dovekie arrays must have equal length >=3")
    matrix = np.asarray(precision, dtype=float)
    if matrix.shape != (n, n):
        raise ValueError(f"precision shape={matrix.shape}, expected={(n, n)}")
    if np.any(~np.isfinite(matrix)) or np.any(np.diag(matrix) <= 0.0):
        raise ValueError("precision must be finite with positive diagonal")
    if not np.allclose(matrix, matrix.T, atol=1.0e-12, rtol=0.0):
        raise ValueError("precision must be symmetric")
    ones = np.ones(n, dtype=float)
    precision_ones = matrix @ ones
    one_precision_one = float(ones @ precision_ones)
    if not math.isfinite(one_precision_one) or one_precision_one <= 0.0:
        raise ValueError("invalid 1^T P 1 normalization")
    z_max = max(0.01, float(np.max(arrays[0])))
    base_grid = np.linspace(0.0, z_max, max(64, int(integration_points)), dtype=float)
    grid = np.unique(np.concatenate((base_grid, arrays[0])))
    return DovekieData(
        z_hd=arrays[0],
        z_hel=arrays[1],
        mu_obs=arrays[2],
        muerr_diag=arrays[3],
        precision=matrix,
        precision_ones=precision_ones,
        one_precision_one=one_precision_one,
        integration_grid=grid,
    )


def load_data(hd_path: Path, precision_path: Path, *, integration_points: int = 4096) -> tuple[DovekieData, int]:
    hd = load_hd(hd_path)
    original_rows = int(hd.pop("original_rows")[0])
    selection = np.asarray(hd.pop("selection"), dtype=bool)
    full_precision = load_precision(precision_path, original_rows)
    precision = full_precision[np.ix_(selection, selection)]
    return prepare_data(precision=precision, integration_points=integration_points, **hd), original_rows


def transition_f(z: np.ndarray, z_t: float, w_t: float) -> np.ndarray:
    width = max(float(w_t), 1.0e-12)
    argument = np.clip((np.asarray(z, dtype=float) - float(z_t)) / width, -500.0, 500.0)
    return 1.0 / (1.0 + np.exp(argument))


def e2(model: str, z: np.ndarray, parameters: Sequence[float]) -> np.ndarray:
    z_arr = np.asarray(z, dtype=float)
    zp1 = 1.0 + z_arr
    if model == LCDM:
        (omega_m,) = map(float, parameters)
        omega_de = 1.0 - omega_m - OMEGA_R0
        value = omega_m * zp1**3 + OMEGA_R0 * zp1**4 + omega_de
    elif model == CPL:
        omega_m, w0, wa = map(float, parameters)
        omega_de = 1.0 - omega_m - OMEGA_R0
        dark_energy = zp1 ** (3.0 * (1.0 + w0 + wa)) * np.exp(-3.0 * wa * z_arr / zp1)
        value = omega_m * zp1**3 + OMEGA_R0 * zp1**4 + omega_de * dark_energy
    elif model == RLL:
        omega_m, omega_s0, z_t, w_t = map(float, parameters)
        omega_de = 1.0 - omega_m - OMEGA_R0 - omega_s0
        if omega_de <= 0.0:
            return np.full_like(z_arr, np.nan)
        f_z = transition_f(z_arr, z_t, w_t)
        superposition = omega_s0 * (f_z + (1.0 - f_z) * zp1**3)
        value = omega_m * zp1**3 + OMEGA_R0 * zp1**4 + omega_de + superposition
    else:
        raise ValueError(f"unsupported model: {model}")
    if np.any(value <= 0.0):
        return np.full_like(z_arr, np.nan)
    return np.asarray(value, dtype=float)


def distance_modulus(data: DovekieData, model: str, parameters: Sequence[float]) -> np.ndarray:
    expansion_squared = e2(model, data.integration_grid, parameters)
    if np.any(~np.isfinite(expansion_squared)) or np.any(expansion_squared <= 0.0):
        raise ValueError("non-physical expansion history")
    inverse_hubble = C_KM_S / (H0_REFERENCE * np.sqrt(expansion_squared))
    dz = np.diff(data.integration_grid)
    comoving = np.concatenate(
        ([0.0], np.cumsum(0.5 * (inverse_hubble[:-1] + inverse_hubble[1:]) * dz))
    )
    dc = np.interp(data.z_hd, data.integration_grid, comoving)
    # Official Dovekie expression is (1+zCMB)(1+zHEL)D_A(zCMB), which in
    # flat geometry is exactly (1+zHEL)D_C(zCMB).
    luminosity_distance = (1.0 + data.z_hel) * dc
    if np.any(luminosity_distance <= 0.0):
        raise ValueError("non-positive Dovekie luminosity distance")
    return 5.0 * np.log10(luminosity_distance) + 25.0


def profiled_likelihood(
    data: DovekieData, model: str, parameters: Sequence[float]
) -> tuple[float, float, np.ndarray]:
    model_mu = distance_modulus(data, model, parameters)
    difference = model_mu - data.mu_obs
    weighted = data.precision @ difference
    b = float(np.sum(weighted))
    offset_hat = -b / data.one_precision_one
    weighted_profiled = weighted + offset_hat * data.precision_ones
    profiled = difference + offset_hat
    chi2 = float(profiled @ weighted_profiled)
    if not math.isfinite(chi2) or chi2 < -1.0e-7:
        raise ValueError(f"invalid Dovekie profiled chi2: {chi2}")
    return max(0.0, chi2), float(offset_hat), weighted_profiled


def objective_and_gradient(
    data: DovekieData, model: str, parameters: np.ndarray
) -> tuple[float, np.ndarray]:
    chi2, _, weighted_profiled = profiled_likelihood(data, model, parameters)
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
        derivative_mu = (
            distance_modulus(data, model, plus) - distance_modulus(data, model, minus)
        ) / (high - low)
        gradient[index] = 2.0 * float(derivative_mu @ weighted_profiled)
    return chi2, gradient


def information_criteria(chi2: float, n: int, k: int) -> dict[str, float | int]:
    aic = float(chi2 + 2.0 * k)
    denominator = n - k - 1
    aicc = float(aic + (2.0 * k * (k + 1) / denominator)) if denominator > 0 else math.inf
    bic = float(chi2 + k * math.log(n))
    return {"chi2": float(chi2), "AIC": aic, "AICc": aicc, "BIC": bic, "N": n, "k": k, "dof": n - k}


def _start_for_seed(model: str, seed: int, index: int) -> tuple[np.ndarray, str]:
    spec = MODEL_SPECS[model]
    if index == 0:
        return np.asarray(spec["canonical_start"], dtype=float), "canonical_nested_start"
    rng = np.random.default_rng(int(seed))
    bounds = np.asarray(spec["bounds"], dtype=float)
    return rng.uniform(bounds[:, 0], bounds[:, 1]), "seeded_uniform_multistart"


def fit_model(
    data: DovekieData,
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
        chi2, offset_hat, _ = profiled_likelihood(data, model, parameters)
        runs.append(
            {
                "seed": int(seed),
                "start_strategy": strategy,
                "initial_parameters": {name: float(value) for name, value in zip(spec["parameter_names"], initial)},
                "parameters": {name: float(value) for name, value in zip(spec["parameter_names"], parameters)},
                "M_offset_profiled": float(offset_hat),
                "chi2": float(chi2),
                "success": bool(result.success),
                "message": str(result.message),
                "iterations": int(result.nit),
                "function_evaluations": int(result.nfev),
                "gradient_evaluations": int(getattr(result, "njev", 0)),
                "runtime_seconds": float(elapsed),
            }
        )
    best = min(runs, key=lambda item: item["chi2"])
    chi_values = np.asarray([item["chi2"] for item in runs], dtype=float)
    k = int(spec["k_including_profiled_offset"])
    row = {
        "model": model,
        **information_criteria(float(best["chi2"]), data.n, k),
        "M_offset_profiled": float(best["M_offset_profiled"]),
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


def _delta(candidate: dict[str, Any], baseline: dict[str, Any]) -> dict[str, float]:
    return {metric: float(candidate[metric] - baseline[metric]) for metric in ("chi2", "AIC", "AICc", "BIC")}


def build_result(
    hd_path: Path,
    precision_path: Path,
    output_path: Path,
    *,
    seeds: Sequence[int],
    maxiter: int = 250,
    ftol: float = 1.0e-10,
    integration_points: int = 4096,
) -> dict[str, Any]:
    started = time.perf_counter()
    data, original_rows = load_data(hd_path, precision_path, integration_points=integration_points)
    fits = {model: fit_model(data, model, seeds, maxiter=maxiter, ftol=ftol) for model in (LCDM, CPL, RLL)}
    rows = [fits[model]["best"] for model in (LCDM, CPL, RLL)]
    lcdm, cpl, rll = rows
    statuses = [fits[model]["status"] for model in (LCDM, CPL, RLL)]
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "status": "PASS_LIMITED" if all(status == "PASS" for status in statuses) else "TOKEN_VAZIO_CONVERGENCE",
        "state": "VERIFIED_LIMITED" if all(status == "PASS" for status in statuses) else "TOKEN_VAZIO_CONVERGENCE",
        "claim_allowed": False,
        "publication_ready": False,
        "publication_effect": "NONE",
        "calibration_variant": "DES-Dovekie",
        "scientific_boundary": (
            "The DES-Dovekie Hubble diagram with its official precision matrix is a supernova-only likelihood. "
            "The profiled magnitude offset is degenerate with H0, so this result does not measure H0, provide "
            "Bayesian evidence, or independently validate RLL."
        ),
        "inputs": {
            "hubble_diagram": {"path": str(hd_path), "bytes": hd_path.stat().st_size, "sha256": sha256_file(hd_path)},
            "precision_matrix": {
                "path": str(precision_path),
                "bytes": precision_path.stat().st_size,
                "sha256": sha256_file(precision_path),
                "matrix_semantics": "inverse_covariance_precision",
                "storage_semantics": "packed_upper_triangle",
            },
            "original_rows": original_rows,
            "selected_rows": data.n,
            "precision_shape_after_selection": [data.n, data.n],
        },
        "method": {
            "observable": "MU",
            "selection": "zHD > 0",
            "distance": "(1+zHEL)*D_C(zHD) == (1+zHD)(1+zHEL)D_A(zHD) for flat geometry",
            "precision_usage": "direct quadratic form; no inverse->covariance->inverse round trip",
            "nuisance": "one additive SN magnitude offset analytically profiled and counted in k",
            "H0_policy": "fixed reference H0=70 km/s/Mpc; absorbed by profiled magnitude offset; no H0 inference",
            "optimizer": "multi-start L-BFGS-B with finite-difference model Jacobian and analytic profiled-likelihood gradient",
            "seeds": [int(seed) for seed in seeds],
            "maxiter": int(maxiter),
            "ftol": float(ftol),
            "integration_points": int(integration_points),
            "flat_closure": True,
        },
        "rows": rows,
        "models": fits,
        "comparison": {
            "baseline": LCDM,
            "cpl_minus_baseline": _delta(cpl, lcdm),
            "rll_minus_baseline": _delta(rll, lcdm),
        },
        "runtime_seconds": float(time.perf_counter() - started),
        "environment": {"python": sys.version.split()[0], "numpy": np.__version__, "platform": platform.platform()},
        "F_ok": [
            "DES-Dovekie HD ordering is used as the canonical precision-matrix ordering.",
            "The packed STAT+SYS object is used as an inverse covariance (precision) matrix, matching the official release semantics.",
            "LCDM, CPL and RLL share one HD vector, one precision matrix, one offset-nuisance policy, seeds, optimizer and integration grid.",
            "CPL nests LCDM at w0=-1 and wa=0.",
        ],
        "F_gap": [
            "Pantheon+ versus DES-Dovekie has not yet been rerun under one deliberately identical Hubble-flow-only nuisance contract.",
            "AIC/AICc/BIC do not replace nested-sampling evidence.",
            "Independent cross-implementation replication remains required.",
            "Explicit repository license was not found and remains TOKEN_VAZIO for redistribution review.",
        ],
        "F_next": [
            "Construct a Pantheon+ Hubble-flow-only companion likelihood with the same profiled-offset policy for a clean calibration/sample ablation.",
            "Feed the common likelihood components into real nested sampling with versioned priors.",
            "Replicate DES-Dovekie fitted metrics independently before scientific promotion.",
        ],
        "token_vazio": [
            "TOKEN_VAZIO_SN_COMMON_NUISANCE_ABLATION",
            "TOKEN_VAZIO_REAL_BAYES_INFERENCE",
            "TOKEN_VAZIO_INDEPENDENT_REPLICATION",
            "TOKEN_VAZIO_EXPLICIT_REPOSITORY_LICENSE_NOT_FOUND",
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
    parser = argparse.ArgumentParser(description="DES-Dovekie full-precision LCDM/CPL/RLL fit")
    parser.add_argument("--hd", type=Path, required=True)
    parser.add_argument("--precision", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seeds", default="11,23,37,53,71")
    parser.add_argument("--maxiter", type=int, default=250)
    parser.add_argument("--ftol", type=float, default=1.0e-10)
    parser.add_argument("--integration-points", type=int, default=4096)
    args = parser.parse_args(argv)
    try:
        result = build_result(
            args.hd,
            args.precision,
            args.output,
            seeds=parse_seeds(args.seeds),
            maxiter=args.maxiter,
            ftol=args.ftol,
            integration_points=args.integration_points,
        )
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 2
    cpl = result["comparison"]["cpl_minus_baseline"]
    rll = result["comparison"]["rll_minus_baseline"]
    print(
        f"{result['status']} N={result['inputs']['selected_rows']} "
        f"dchi2_CPL={cpl['chi2']:.8g} dchi2_RLL={rll['chi2']:.8g} claim_allowed=false"
    )
    return 0 if result["status"] == "PASS_LIMITED" else 3


if __name__ == "__main__":
    raise SystemExit(main())
