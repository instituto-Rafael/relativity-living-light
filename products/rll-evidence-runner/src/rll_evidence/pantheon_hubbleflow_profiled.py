from __future__ import annotations

"""Pantheon+ Hubble-flow-only LCDM/CPL/RLL fit with Dovekie-like nuisance policy.

This companion likelihood removes SH0ES calibrator rows, fixes H0 only as a
reference distance scale, and analytically profiles one additive SN magnitude
offset.  That makes the supernova nuisance treatment comparable to the
DES-Dovekie likelihood without pretending the two samples/calibrations are the
same dataset.
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

from . import pantheon_fit as _core
from . import pantheon_fit_three_model as _three

SCHEMA = "rll_pantheon_hubbleflow_profiled_three_model_v1"
H0_REFERENCE = 70.0
LCDM = _core.LCDM
CPL = _three.CPL
RLL = _core.RLL

LOCAL_SPECS: dict[str, dict[str, Any]] = {
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


def load_hubbleflow_data(
    catalog_path: Path,
    covariance_path: Path,
    *,
    z_min: float = 0.01,
    integration_points: int = 4096,
) -> tuple[_core.PantheonData, int]:
    table = np.genfromtxt(catalog_path, names=True, dtype=None, encoding="utf-8")
    if table.shape == ():
        table = np.asarray([table], dtype=table.dtype)
    required = {"zHD", "zHEL", "m_b_corr", "CEPH_DIST", "IS_CALIBRATOR"}
    available = set(table.dtype.names or ())
    missing = sorted(required - available)
    if missing:
        raise ValueError(f"Pantheon+ catalog missing columns: {missing}")

    z_hd_all = np.asarray(table["zHD"], dtype=float)
    calibrator_all = np.asarray(table["IS_CALIBRATOR"], dtype=int) == 1
    selection = (z_hd_all > float(z_min)) & (~calibrator_all)
    selected = int(np.count_nonzero(selection))
    if selected < 3:
        raise ValueError("Pantheon+ Hubble-flow selection retained fewer than three rows")

    full_covariance = _core.load_covariance(covariance_path, len(z_hd_all))
    covariance = full_covariance[np.ix_(selection, selection)]
    data = _core.prepare_data(
        z_hd=z_hd_all[selection],
        z_hel=np.asarray(table["zHEL"], dtype=float)[selection],
        m_b_corr=np.asarray(table["m_b_corr"], dtype=float)[selection],
        ceph_dist=np.zeros(selected, dtype=float),
        is_calibrator=np.zeros(selected, dtype=bool),
        covariance=covariance,
        integration_points=integration_points,
    )
    return data, len(z_hd_all)


def expand_parameters(model: str, parameters: Sequence[float]) -> np.ndarray:
    if model not in LOCAL_SPECS:
        raise ValueError(f"unsupported model: {model}")
    return np.asarray((H0_REFERENCE, *map(float, parameters)), dtype=float)


def objective(data: _core.PantheonData, model: str, parameters: Sequence[float]) -> float:
    chi2, _offset, _weighted = _core.profiled_likelihood(data, model, expand_parameters(model, parameters))
    return float(chi2)


def information_criteria(chi2: float, n: int, k: int) -> dict[str, float | int]:
    aic = float(chi2 + 2.0 * k)
    denominator = n - k - 1
    aicc = float(aic + 2.0 * k * (k + 1) / denominator) if denominator > 0 else math.inf
    bic = float(chi2 + k * math.log(n))
    return {"chi2": float(chi2), "AIC": aic, "AICc": aicc, "BIC": bic, "N": n, "k": k, "dof": n - k}


def _start(model: str, seed: int, index: int) -> tuple[np.ndarray, str]:
    spec = LOCAL_SPECS[model]
    if index == 0:
        return np.asarray(spec["canonical_start"], dtype=float), "canonical_nested_start"
    rng = np.random.default_rng(int(seed))
    bounds = np.asarray(spec["bounds"], dtype=float)
    return rng.uniform(bounds[:, 0], bounds[:, 1]), "seeded_uniform_multistart"


def fit_model(
    data: _core.PantheonData,
    model: str,
    seeds: Sequence[int],
    *,
    maxiter: int = 250,
    ftol: float = 1.0e-10,
) -> dict[str, Any]:
    if model not in LOCAL_SPECS:
        raise ValueError(f"unsupported model: {model}")
    if not seeds:
        raise ValueError("at least one seed is required")
    spec = LOCAL_SPECS[model]
    runs: list[dict[str, Any]] = []
    for index, seed in enumerate(seeds):
        initial, strategy = _start(model, int(seed), index)
        started = time.perf_counter()
        result = minimize(
            lambda x: objective(data, model, np.asarray(x, dtype=float)),
            initial,
            method="L-BFGS-B",
            bounds=list(spec["bounds"]),
            options={"maxiter": int(maxiter), "ftol": float(ftol), "maxls": 40},
        )
        elapsed = time.perf_counter() - started
        params = np.asarray(result.x, dtype=float)
        chi2, offset_hat, _ = _core.profiled_likelihood(data, model, expand_parameters(model, params))
        runs.append(
            {
                "seed": int(seed),
                "start_strategy": strategy,
                "initial_parameters": {name: float(value) for name, value in zip(spec["parameter_names"], initial)},
                "parameters": {name: float(value) for name, value in zip(spec["parameter_names"], params)},
                "M_offset_profiled": float(offset_hat),
                "chi2": float(chi2),
                "success": bool(result.success),
                "message": str(result.message),
                "iterations": int(result.nit),
                "function_evaluations": int(result.nfev),
                "runtime_seconds": float(elapsed),
            }
        )
    best = min(runs, key=lambda row: row["chi2"])
    row = {
        "model": model,
        **information_criteria(float(best["chi2"]), data.n, int(spec["k_including_profiled_offset"])),
        "H0_reference": H0_REFERENCE,
        "M_offset_profiled": float(best["M_offset_profiled"]),
        **best["parameters"],
    }
    chi = np.asarray([run["chi2"] for run in runs], dtype=float)
    return {
        "model": model,
        "status": "PASS" if all(run["success"] for run in runs) else "TOKEN_VAZIO_CONVERGENCE",
        "best": row,
        "best_seed": int(best["seed"]),
        "stability": {
            "seed_count": len(runs),
            "converged_count": sum(bool(run["success"]) for run in runs),
            "chi2_min": float(np.min(chi)),
            "chi2_max": float(np.max(chi)),
            "chi2_span": float(np.ptp(chi)),
        },
        "runs": runs,
    }


def _delta(candidate: dict[str, Any], baseline: dict[str, Any]) -> dict[str, float]:
    return {metric: float(candidate[metric] - baseline[metric]) for metric in ("chi2", "AIC", "AICc", "BIC")}


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
    data, original_rows = load_hubbleflow_data(
        catalog_path, covariance_path, z_min=z_min, integration_points=integration_points
    )
    fits = {model: fit_model(data, model, seeds, maxiter=maxiter, ftol=ftol) for model in (LCDM, CPL, RLL)}
    rows = [fits[model]["best"] for model in (LCDM, CPL, RLL)]
    lcdm, cpl, rll = rows
    all_pass = all(fits[model]["status"] == "PASS" for model in (LCDM, CPL, RLL))
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "state": "VERIFIED_LIMITED" if all_pass else "TOKEN_VAZIO_CONVERGENCE",
        "status": "PASS_LIMITED" if all_pass else "TOKEN_VAZIO_CONVERGENCE",
        "claim_allowed": False,
        "publication_ready": False,
        "calibration_variant": "Pantheon+SH0ES_HUBBLE_FLOW_ONLY",
        "source_sha256": _core.sha256_file(catalog_path),
        "covariance_sha256": _core.sha256_file(covariance_path),
        "n_supernovae": data.n,
        "original_rows": original_rows,
        "nuisance_policy": "one additive SN magnitude offset analytically profiled; H0 fixed only as a reference distance scale and not inferred",
        "H0_reference": H0_REFERENCE,
        "z_min": float(z_min),
        "models": fits,
        "rows": rows,
        "comparison": {
            "baseline": LCDM,
            "cpl_minus_baseline": _delta(cpl, lcdm),
            "rll_minus_baseline": _delta(rll, lcdm),
        },
        "runtime_seconds": float(time.perf_counter() - started),
        "scientific_boundary": "This companion run aligns the SN-only nuisance/H0 policy with Dovekie. It does not make Pantheon+ and Dovekie the same calibration/sample and does not constitute Bayesian evidence.",
        "F_ok": [
            "SH0ES calibrator rows are explicitly excluded.",
            "H0 is fixed as a reference scale and one additive magnitude offset is profiled, matching the Dovekie SN-only nuisance logic.",
            "LCDM, CPL and RLL share one selected vector, covariance, optimizer policy and information-criterion counting convention."
        ],
        "F_gap": [
            "Cross-dataset differences in calibration, sample construction and covariance provenance remain and must be reported rather than canceled by this nuisance alignment.",
            "Real Bayesian evidence and independent replication remain open."
        ],
        "F_next": [
            "Compare this Hubble-flow-only Pantheon+ result against the Dovekie result through a dedicated calibration/sample ablation receipt.",
            "Run profile sensitivity for Dovekie CPL wa before parameter interpretation."
        ],
        "token_vazio": ["TOKEN_VAZIO_SN_COMMON_NUISANCE_ABLATION", "TOKEN_VAZIO_REAL_BAYES_INFERENCE", "TOKEN_VAZIO_INDEPENDENT_REPLICATION"]
    }
    _atomic_json(output_path, payload)
    return payload


def _parse_seeds(text: str) -> list[int]:
    seeds = [int(value.strip()) for value in text.split(",") if value.strip()]
    if not seeds or len(set(seeds)) != len(seeds):
        raise ValueError("seeds must be non-empty and unique")
    return seeds


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Pantheon+ Hubble-flow-only profiled LCDM/CPL/RLL companion fit")
    parser.add_argument("--catalog", type=Path, required=True)
    parser.add_argument("--covariance", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seeds", default="11,23,37")
    parser.add_argument("--maxiter", type=int, default=250)
    parser.add_argument("--ftol", type=float, default=1.0e-10)
    parser.add_argument("--integration-points", type=int, default=4096)
    parser.add_argument("--z-min", type=float, default=0.01)
    args = parser.parse_args(argv)
    try:
        payload = build_result(
            args.catalog,
            args.covariance,
            args.output,
            seeds=_parse_seeds(args.seeds),
            maxiter=args.maxiter,
            ftol=args.ftol,
            integration_points=args.integration_points,
            z_min=args.z_min,
        )
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 2
    print(
        f"{payload['status']} N={payload['n_supernovae']} "
        f"dchi2_CPL={payload['comparison']['cpl_minus_baseline']['chi2']:.8g} "
        f"dchi2_RLL={payload['comparison']['rll_minus_baseline']['chi2']:.8g} claim_allowed=false"
    )
    return 0 if payload["status"] == "PASS_LIMITED" else 3


if __name__ == "__main__":
    raise SystemExit(main())
