from __future__ import annotations

"""Proper nested-sampling evidence for the modern DES-Dovekie SN likelihood.

Unlike the optimization likelihood, the additive magnitude nuisance is sampled
with one explicit proper prior shared by LCDM, CPL and RLL.  The full Gaussian
normalization from the precision matrix is included, so stored logZ values are
mathematically defined for the declared finite prior volumes.
"""

import argparse
import importlib.metadata
import json
import math
import os
import tempfile
import time
from pathlib import Path
from typing import Any, Sequence

import dynesty
import numpy as np
from dynesty.utils import merge_runs

from . import dovekie_fit_three_model as _dov

SCHEMA = "rll_dovekie_nested_evidence_v1"
MODEL_ORDER = (_dov.LCDM, _dov.CPL, _dov.RLL)
CORE_PARAMETERS = {
    _dov.LCDM: ("Omega_m",),
    _dov.CPL: ("Omega_m", "w0", "wa"),
    _dov.RLL: ("Omega_m", "Omega_s0", "z_t", "w_t"),
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


def load_prior_registry(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema") != "rll.modern_bayes_prior_registry.v1":
        raise ValueError("unexpected prior registry schema")
    if payload.get("claim_allowed") is not False:
        raise ValueError("prior registry must preserve claim_allowed=false")
    priors = payload.get("priors")
    if not isinstance(priors, dict) or set(priors) != set(MODEL_ORDER):
        raise ValueError("prior registry must define exactly LCDM/CPL/RLL Dovekie models")
    offsets = []
    for model in MODEL_ORDER:
        expected = (*CORE_PARAMETERS[model], "M_offset")
        if tuple(priors[model].keys()) != expected:
            raise ValueError(f"{model}: prior parameter order must be {expected}")
        for name, interval in priors[model].items():
            if not isinstance(interval, list) or len(interval) != 2:
                raise ValueError(f"{model}.{name}: prior must be [lower, upper]")
            lower, upper = map(float, interval)
            if not math.isfinite(lower) or not math.isfinite(upper) or upper <= lower:
                raise ValueError(f"{model}.{name}: invalid finite prior interval")
        offsets.append(tuple(map(float, priors[model]["M_offset"])))
    if len(set(offsets)) != 1:
        raise ValueError("M_offset prior must be identical across all models")
    return payload


def _prior_arrays(registry: dict[str, Any], model: str) -> tuple[list[str], np.ndarray, np.ndarray]:
    mapping = registry["priors"][model]
    names = list(mapping.keys())
    lower = np.asarray([float(mapping[name][0]) for name in names], dtype=float)
    upper = np.asarray([float(mapping[name][1]) for name in names], dtype=float)
    return names, lower, upper


def gaussian_loglike_factory(data: _dov.DovekieData, model: str):
    sign, logdet_precision = np.linalg.slogdet(data.precision)
    if sign <= 0 or not math.isfinite(float(logdet_precision)):
        raise ValueError("precision matrix log-determinant is not positive/finite")
    log_norm = 0.5 * float(logdet_precision) - 0.5 * data.n * math.log(2.0 * math.pi)

    def loglike(theta: np.ndarray) -> float:
        vector = np.asarray(theta, dtype=float)
        core = vector[:-1]
        offset = float(vector[-1])
        try:
            model_mu = _dov.distance_modulus(data, model, core)
        except (ValueError, FloatingPointError, OverflowError):
            return -math.inf
        residual = model_mu + offset - data.mu_obs
        weighted = data.precision @ residual
        chi2 = float(residual @ weighted)
        if not math.isfinite(chi2) or chi2 < -1.0e-7:
            return -math.inf
        return float(log_norm - 0.5 * max(0.0, chi2))

    return loglike, float(log_norm)


def weighted_quantile(values: np.ndarray, weights: np.ndarray, quantiles: Sequence[float]) -> list[float]:
    order = np.argsort(values)
    v = np.asarray(values, dtype=float)[order]
    w = np.asarray(weights, dtype=float)[order]
    total = float(np.sum(w))
    if not math.isfinite(total) or total <= 0.0:
        raise ValueError("invalid posterior weights")
    cumulative = np.cumsum(w) / total
    return [float(np.interp(float(q), cumulative, v)) for q in quantiles]


def summarize_results(results: Any, names: Sequence[str], lower: np.ndarray, upper: np.ndarray) -> dict[str, Any]:
    logz = float(results.logz[-1])
    logzerr = float(results.logzerr[-1])
    weights = np.exp(np.asarray(results.logwt, dtype=float) - logz)
    weights /= np.sum(weights)
    samples = np.asarray(results.samples, dtype=float)
    posterior: dict[str, Any] = {}
    alerts: list[str] = []
    for index, name in enumerate(names):
        q05, q50, q95 = weighted_quantile(samples[:, index], weights, (0.05, 0.50, 0.95))
        width = float(upper[index] - lower[index])
        low_fraction = (q05 - float(lower[index])) / width
        high_fraction = (float(upper[index]) - q95) / width
        boundary = low_fraction < 0.02 or high_fraction < 0.02
        if boundary:
            alerts.append(name)
        posterior[name] = {
            "q05": q05,
            "q50": q50,
            "q95": q95,
            "prior": [float(lower[index]), float(upper[index])],
            "near_prior_boundary": boundary,
        }
    return {
        "logZ": logz,
        "logZ_error": logzerr,
        "niter": int(results.niter),
        "ncall": int(np.sum(results.ncall)),
        "posterior": posterior,
        "prior_boundary_alerts": alerts,
    }


def run_one(
    data: _dov.DovekieData,
    registry: dict[str, Any],
    model: str,
    *,
    seed: int,
    nlive: int,
    dlogz: float,
) -> tuple[Any, dict[str, Any]]:
    names, lower, upper = _prior_arrays(registry, model)
    loglike, log_norm = gaussian_loglike_factory(data, model)

    def prior_transform(unit_cube: np.ndarray) -> np.ndarray:
        u = np.asarray(unit_cube, dtype=float)
        return lower + u * (upper - lower)

    rng = np.random.default_rng(int(seed))
    started = time.perf_counter()
    sampler = dynesty.NestedSampler(
        loglike,
        prior_transform,
        len(names),
        nlive=int(nlive),
        bound="multi",
        sample="rwalk",
        rstate=rng,
    )
    sampler.run_nested(dlogz=float(dlogz), print_progress=False)
    elapsed = time.perf_counter() - started
    summary = summarize_results(sampler.results, names, lower, upper)
    summary.update(
        {
            "seed": int(seed),
            "nlive": int(nlive),
            "dlogz": float(dlogz),
            "runtime_seconds": float(elapsed),
            "parameter_order": names,
            "gaussian_log_normalization": log_norm,
        }
    )
    return sampler.results, summary


def _consistency(first: dict[str, Any], second: dict[str, Any]) -> dict[str, Any]:
    delta = abs(float(first["logZ"]) - float(second["logZ"]))
    sigma = math.sqrt(float(first["logZ_error"]) ** 2 + float(second["logZ_error"]) ** 2)
    z = delta / sigma if sigma > 0.0 else math.inf
    return {"abs_delta_logZ": delta, "combined_sigma": sigma, "z_score": z, "consistent_3sigma": bool(z <= 3.0)}


def build_evidence(
    hd_path: Path,
    precision_path: Path,
    prior_registry_path: Path,
    output_path: Path,
    *,
    seeds: Sequence[int],
    nlive: int = 160,
    dlogz: float = 0.15,
    integration_points: int = 4096,
) -> dict[str, Any]:
    if len(seeds) < 2 or len(set(map(int, seeds))) != len(seeds):
        raise ValueError("at least two unique internal numerical seeds are required")
    registry = load_prior_registry(prior_registry_path)
    data, original_rows = _dov.load_data(hd_path, precision_path, integration_points=integration_points)
    started = time.perf_counter()
    models: dict[str, Any] = {}
    merged_objects: dict[str, Any] = {}

    for model in MODEL_ORDER:
        names, lower, upper = _prior_arrays(registry, model)
        run_objects = []
        runs = []
        for seed in seeds:
            result_obj, summary = run_one(
                data, registry, model, seed=int(seed), nlive=nlive, dlogz=dlogz
            )
            run_objects.append(result_obj)
            runs.append(summary)
        merged = merge_runs(run_objects)
        merged_summary = summarize_results(merged, names, lower, upper)
        models[model] = {
            "runs": runs,
            "internal_numerical_consistency": _consistency(runs[0], runs[1]),
            "merged": merged_summary,
        }
        merged_objects[model] = merged

    lcdm = models[_dov.LCDM]["merged"]
    cpl = models[_dov.CPL]["merged"]
    rll = models[_dov.RLL]["merged"]
    ln_b_cpl_lcdm = float(cpl["logZ"] - lcdm["logZ"])
    ln_b_rll_lcdm = float(rll["logZ"] - lcdm["logZ"])
    err_cpl = math.sqrt(float(cpl["logZ_error"]) ** 2 + float(lcdm["logZ_error"]) ** 2)
    err_rll = math.sqrt(float(rll["logZ_error"]) ** 2 + float(lcdm["logZ_error"]) ** 2)
    all_consistent = all(
        bool(models[model]["internal_numerical_consistency"]["consistent_3sigma"])
        for model in MODEL_ORDER
    )

    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "state": "VERIFIED_INTERNAL_NUMERICAL_REPLICATION" if all_consistent else "TOKEN_VAZIO_NUMERICAL_REPLICATION",
        "claim_allowed": False,
        "publication_ready": False,
        "independent_replication": False,
        "sampler": {
            "name": "dynesty.NestedSampler",
            "version": importlib.metadata.version("dynesty"),
            "nlive_per_run": int(nlive),
            "dlogz": float(dlogz),
            "seeds": [int(seed) for seed in seeds],
            "bound": "multi",
            "sample": "rwalk",
        },
        "inputs": {
            "hubble_diagram_sha256": _dov.sha256_file(hd_path),
            "precision_sha256": _dov.sha256_file(precision_path),
            "prior_registry_sha256": _dov.sha256_file(prior_registry_path),
            "prior_set": registry["prior_set"],
            "n_supernovae": data.n,
            "original_rows": original_rows,
        },
        "likelihood": {
            "matrix_semantics": "inverse_covariance_precision",
            "magnitude_offset": "sampled proper shared nuisance",
            "H0_reference": _dov.H0_REFERENCE,
            "H0_inferred": False,
            "full_gaussian_normalization": True,
        },
        "models": models,
        "bayes_factors": {
            "CPL_vs_LCDM": {"lnB": ln_b_cpl_lcdm, "approx_error": err_cpl},
            "RLL_vs_LCDM": {"lnB": ln_b_rll_lcdm, "approx_error": err_rll},
        },
        "runtime_seconds": float(time.perf_counter() - started),
        "scientific_boundary": "This is real prior-locked nested-sampling evidence for the modern DES-Dovekie SN-only likelihood. It does not combine overlapping SN compilations, does not include DESI/CMB/LSS, and internal repeated seeds are not independent external replication.",
        "resolves_token_by_reduction": "TOKEN_VAZIO_REAL_BAYES_MODERN_3MODEL_PRIOR_LOCK",
        "successor_tokens": [
            "TOKEN_VAZIO_REAL_BAYES_JOINT_MULTI_PROBE",
            "TOKEN_VAZIO_INDEPENDENT_REPLICATION"
        ],
        "F_ok": [
            "LCDM, CPL and RLL use one identical materialized Dovekie likelihood.",
            "The magnitude nuisance is sampled with a proper shared prior rather than profiled away for evidence.",
            "Prior ranges are frozen and hashed before execution.",
            "Two internal nested runs per model are merged and checked for numerical consistency."
        ],
        "F_gap": [
            "TOKEN_VAZIO_REAL_BAYES_JOINT_MULTI_PROBE",
            "TOKEN_VAZIO_INDEPENDENT_REPLICATION"
        ],
        "F_next": [
            "Add official DESI/CMB/LSS likelihood components only after their own reproduction gates pass; never double-count overlapping SN compilations.",
            "Obtain independent external replication before scientific promotion."
        ],
    }
    _atomic_json(output_path, payload)
    return payload


def _parse_seeds(text: str) -> list[int]:
    values = [int(value.strip()) for value in text.split(",") if value.strip()]
    if len(values) < 2 or len(set(values)) != len(values):
        raise ValueError("seeds must contain at least two unique integers")
    return values


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run proper prior-locked Dovekie three-model nested evidence")
    parser.add_argument("--hd", type=Path, required=True)
    parser.add_argument("--precision", type=Path, required=True)
    parser.add_argument("--priors", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seeds", default="20260807,20260808")
    parser.add_argument("--nlive", type=int, default=160)
    parser.add_argument("--dlogz", type=float, default=0.15)
    parser.add_argument("--integration-points", type=int, default=4096)
    args = parser.parse_args(argv)
    try:
        payload = build_evidence(
            args.hd,
            args.precision,
            args.priors,
            args.output,
            seeds=_parse_seeds(args.seeds),
            nlive=args.nlive,
            dlogz=args.dlogz,
            integration_points=args.integration_points,
        )
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 2
    print(json.dumps({
        "state": payload["state"],
        "CPL_vs_LCDM": payload["bayes_factors"]["CPL_vs_LCDM"],
        "RLL_vs_LCDM": payload["bayes_factors"]["RLL_vs_LCDM"],
        "claim_allowed": False,
    }, sort_keys=True))
    return 0 if payload["state"] == "VERIFIED_INTERNAL_NUMERICAL_REPLICATION" else 3


if __name__ == "__main__":
    raise SystemExit(main())
