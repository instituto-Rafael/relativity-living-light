#!/usr/bin/env python3
"""G6 canonical inference on the exact G5 background likelihood.

Runs independently seeded emcee ensembles plus multiseed dynesty evidence for
LCDM and RLL.  Historical FASE20 results are comparison-only because their
likelihood/data/prior route differs from G5.

Pantheon M_B is analytically profiled exactly as in G5.  Because the quadratic
coefficient 1^T C^-1 1 is data/covariance-only and identical between models,
profiling differs from flat-measure marginalization by a common multiplicative
constant.  Therefore this gate interprets *differences* in sampler logZ
(ln B10), not the absolute logZ normalization as a universal evidence value.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import platform
import sys
import time
from pathlib import Path
from types import ModuleType
from typing import Any, Sequence

import numpy as np

try:
    import emcee
    import dynesty
    import scipy
except ImportError as exc:  # pragma: no cover
    raise ImportError("G6 requires emcee, dynesty, numpy and scipy") from exc

ROOT = Path(__file__).resolve().parents[1]
G4_MODULE = ROOT / "tools/run_g4_background_tournament.py"
G5_BUILDER = ROOT / "tools/build_g5_canonical_background_manifest.py"
G6_CONTRACT = ROOT / "data/contracts/rll_g6_canonical_inference.v1.json"
MODELS = ("LCDM", "RLL")


def _module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected JSON object")
    return value


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _bounds_array(g4: ModuleType, model: str, override: dict[str, Sequence[float]] | None = None) -> np.ndarray:
    names = g4.parameter_names(model)
    base = {name: tuple(bound) for name, bound in zip(names, g4.bounds(model), strict=True)}
    if override:
        for name, bound in override.items():
            if name not in base:
                raise ValueError(f"prior override parameter not in {model}: {name}")
            if len(bound) != 2 or float(bound[0]) >= float(bound[1]):
                raise ValueError(f"invalid prior override {name}={bound}")
            base[name] = (float(bound[0]), float(bound[1]))
    return np.asarray([base[name] for name in names], dtype=float)


def _inside(theta: np.ndarray, b: np.ndarray) -> bool:
    return bool(theta.shape == (len(b),) and np.all(np.isfinite(theta)) and np.all(theta >= b[:, 0]) and np.all(theta <= b[:, 1]))


def _log_likelihood(g4: ModuleType, data: Any, model: str, theta: np.ndarray) -> float:
    try:
        components = g4.profiled_components(data, model, theta)
        value = -0.5 * float(components["total"])
    except Exception:
        return -1.0e300
    return value if math.isfinite(value) else -1.0e300


def _posterior(g4: ModuleType, data: Any, model: str, b: np.ndarray):
    def fn(theta: np.ndarray) -> float:
        arr = np.asarray(theta, dtype=float)
        if not _inside(arr, b):
            return -np.inf
        value = _log_likelihood(g4, data, model, arr)
        return value if value > -1.0e299 else -np.inf
    return fn


def _split_rhat(chains: list[np.ndarray]) -> list[float]:
    if len(chains) < 2:
        raise ValueError("Rhat requires at least two chains")
    n = min(chain.shape[0] for chain in chains)
    if n < 4:
        raise ValueError("Rhat chains too short")
    arr = np.stack([chain[:n] for chain in chains], axis=0)  # m,n,d
    m = arr.shape[0]
    means = np.mean(arr, axis=1)
    variances = np.var(arr, axis=1, ddof=1)
    w = np.mean(variances, axis=0)
    b = n * np.var(means, axis=0, ddof=1)
    var_hat = ((n - 1.0) / n) * w + b / n
    with np.errstate(divide="ignore", invalid="ignore"):
        rhat = np.sqrt(var_hat / w)
    rhat = np.where((w == 0.0) & (b == 0.0), 1.0, rhat)
    return [float(x) for x in rhat]


def run_mcmc(
    g4: ModuleType,
    data: Any,
    model: str,
    best: dict[str, Any],
    *,
    seeds: Sequence[int],
    walkers: int,
    steps: int,
    burn: int,
) -> dict[str, Any]:
    names = g4.parameter_names(model)
    b = _bounds_array(g4, model)
    ndim = len(names)
    if walkers < 2 * ndim:
        raise ValueError(f"{model}: walkers={walkers} < 2*ndim={2*ndim}")
    center = np.asarray([float(best[name]) for name in names], dtype=float)
    widths = b[:, 1] - b[:, 0]
    eps = 1.0e-8 * widths
    log_prob = _posterior(g4, data, model, b)
    ensemble_records: list[dict[str, Any]] = []
    pooled_chains: list[np.ndarray] = []
    all_samples: list[np.ndarray] = []
    for seed in seeds:
        rng = np.random.default_rng(int(seed))
        p0 = center + rng.normal(0.0, 0.02, size=(walkers, ndim)) * widths
        p0 = np.clip(p0, b[:, 0] + eps, b[:, 1] - eps)
        sampler = emcee.EnsembleSampler(walkers, ndim, log_prob)
        started = time.perf_counter()
        sampler.run_mcmc(p0, steps, progress=False, skip_initial_state_check=True)
        elapsed = time.perf_counter() - started
        post = np.asarray(sampler.get_chain(discard=burn), dtype=float)  # step,walker,dim
        flat = post.reshape(-1, ndim)
        if not np.all(np.isfinite(flat)):
            raise RuntimeError(f"{model}: non-finite MCMC samples seed={seed}")
        pooled_chains.append(flat)
        all_samples.append(flat)
        acceptance = float(np.mean(sampler.acceptance_fraction))
        ensemble_records.append(
            {
                "seed": int(seed),
                "postburn_samples": int(flat.shape[0]),
                "mean_acceptance_fraction": acceptance,
                "runtime_seconds": elapsed,
            }
        )
    rhats = _split_rhat(pooled_chains)
    combined = np.concatenate(all_samples, axis=0)
    quantiles: dict[str, dict[str, float]] = {}
    for i, name in enumerate(names):
        q16, q50, q84, q95 = np.quantile(combined[:, i], [0.16, 0.50, 0.84, 0.95])
        quantiles[name] = {"q16": float(q16), "q50": float(q50), "q84": float(q84), "q95": float(q95)}
    boundary: dict[str, Any] = {}
    if model == "RLL":
        idx = names.index("Omega_s0")
        prior_width = b[idx, 1] - b[idx, 0]
        boundary["Omega_s0_fraction_within_1pct_prior_width_of_zero"] = float(np.mean(combined[:, idx] <= b[idx, 0] + 0.01 * prior_width))
        boundary["Omega_s0_q95"] = quantiles["Omega_s0"]["q95"]
    return {
        "model": model,
        "parameter_names": list(names),
        "ensembles": ensemble_records,
        "total_postburn_samples": int(combined.shape[0]),
        "Rhat": dict(zip(names, rhats, strict=True)),
        "max_Rhat": float(max(rhats)),
        "quantiles": quantiles,
        "boundary_diagnostics": boundary,
    }


def _prior_transform(b: np.ndarray):
    width = b[:, 1] - b[:, 0]
    low = b[:, 0]
    def transform(u: np.ndarray) -> np.ndarray:
        return low + np.asarray(u, dtype=float) * width
    return transform


def run_nested_once(
    g4: ModuleType,
    data: Any,
    model: str,
    *,
    seed: int,
    nlive: int,
    dlogz: float,
    maxiter: int,
    prior_override: dict[str, Sequence[float]] | None = None,
) -> dict[str, Any]:
    b = _bounds_array(g4, model, prior_override)
    ndim = b.shape[0]
    rng = np.random.default_rng(int(seed))
    loglike = lambda theta: _log_likelihood(g4, data, model, np.asarray(theta, dtype=float))
    sampler = dynesty.NestedSampler(
        loglike,
        _prior_transform(b),
        ndim,
        nlive=int(nlive),
        bound="multi",
        sample="rwalk",
        rstate=rng,
    )
    started = time.perf_counter()
    sampler.run_nested(dlogz=float(dlogz), maxiter=int(maxiter), print_progress=False)
    elapsed = time.perf_counter() - started
    results = sampler.results
    logz = float(results.logz[-1])
    logzerr = float(results.logzerr[-1])
    niter = int(results.niter)
    ncall = int(np.sum(results.ncall))
    finite = math.isfinite(logz) and math.isfinite(logzerr)
    return {
        "model": model,
        "seed": int(seed),
        "nlive": int(nlive),
        "dlogz": float(dlogz),
        "maxiter": int(maxiter),
        "niter": niter,
        "ncall": ncall,
        "logZ_common_MB_measure": logz,
        "logZerr": logzerr,
        "finite": finite,
        "hit_maxiter": bool(niter >= maxiter),
        "runtime_seconds": elapsed,
        "prior_override": prior_override or {},
    }


def _environment() -> dict[str, str]:
    return {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "emcee": getattr(emcee, "__version__", "unknown"),
        "dynesty": getattr(dynesty, "__version__", "unknown"),
    }


def build_report(g4_receipt_path: Path, g5_manifest_path: Path, root: Path = ROOT) -> dict[str, Any]:
    g4 = _module("rll_g4_for_g6", root / G4_MODULE.relative_to(ROOT))
    g5_builder = _module("rll_g5_for_g6", root / G5_BUILDER.relative_to(ROOT))
    contract = _json(root / G6_CONTRACT.relative_to(ROOT))
    g4_receipt = _json(g4_receipt_path)
    g5_manifest = _json(g5_manifest_path)

    expected_g5 = g5_builder.build_manifest(g4_receipt_path, root)
    if expected_g5.get("state") != "READY_G5_CANONICAL_BACKGROUND_LIKELIHOOD":
        raise RuntimeError("G5 prerequisite cannot be reconstructed from G4 receipt")
    for key in ("g4_receipt_sha256", "executor_sha256", "g4_contract_sha256", "g5_contract_sha256", "input_sha256", "models", "selection_registry", "covariance_registry"):
        if g5_manifest.get(key) != expected_g5.get(key):
            raise RuntimeError(f"G5 manifest mismatch in {key}")
    if g5_manifest.get("claim_allowed") is not False:
        raise RuntimeError("G5 claim_allowed drift")

    data = g4.load_data(integration_points=4096)
    best_by_model = {row["model"]: row for row in g4_receipt["rows"]}
    mcmc_cfg = contract["mcmc"]
    mcmc: dict[str, Any] = {}
    for model in MODELS:
        mcmc[model] = run_mcmc(
            g4,
            data,
            model,
            best_by_model[model],
            seeds=mcmc_cfg["seeds"],
            walkers=int(mcmc_cfg["walkers_per_ensemble"]),
            steps=int(mcmc_cfg["steps"]),
            burn=int(mcmc_cfg["burn"]),
        )

    nested_cfg = contract["nested"]
    nested: dict[str, list[dict[str, Any]]] = {model: [] for model in MODELS}
    for model in MODELS:
        for seed in nested_cfg["seeds"]:
            nested[model].append(
                run_nested_once(
                    g4,
                    data,
                    model,
                    seed=int(seed),
                    nlive=int(nested_cfg["nlive"]),
                    dlogz=float(nested_cfg["dlogz"]),
                    maxiter=int(nested_cfg["maxiter"]),
                )
            )
    ln_b10 = []
    for lcdm_run, rll_run in zip(nested["LCDM"], nested["RLL"], strict=True):
        ln_b10.append(
            {
                "seed_pair": [lcdm_run["seed"], rll_run["seed"]],
                "lnB10_RLL_minus_LCDM": rll_run["logZ_common_MB_measure"] - lcdm_run["logZ_common_MB_measure"],
                "sigma_independent_logZ": math.sqrt(lcdm_run["logZerr"] ** 2 + rll_run["logZerr"] ** 2),
            }
        )
    ln_values = [float(item["lnB10_RLL_minus_LCDM"]) for item in ln_b10]
    ln_span = max(ln_values) - min(ln_values)
    ln_mean = float(np.mean(ln_values))

    sensitivity_cfg = contract["prior_sensitivity"]
    sensitivity_seed = int(sensitivity_cfg["nested_seed"])
    lcdm_sensitivity = run_nested_once(
        g4, data, "LCDM", seed=sensitivity_seed,
        nlive=int(nested_cfg["nlive"]), dlogz=float(nested_cfg["dlogz"]), maxiter=int(nested_cfg["maxiter"]),
    )
    rll_sensitivity = run_nested_once(
        g4, data, "RLL", seed=sensitivity_seed,
        nlive=int(nested_cfg["nlive"]), dlogz=float(nested_cfg["dlogz"]), maxiter=int(nested_cfg["maxiter"]),
        prior_override=sensitivity_cfg["RLL_narrow_variant"],
    )
    sensitivity_ln_b10 = rll_sensitivity["logZ_common_MB_measure"] - lcdm_sensitivity["logZ_common_MB_measure"]

    mcmc_threshold = float(mcmc_cfg["convergence"]["max_split_Rhat"])
    mcmc_pass = all(result["max_Rhat"] <= mcmc_threshold for result in mcmc.values())
    nested_finite = all(run["finite"] for runs in nested.values() for run in runs)
    nested_not_maxed = all(not run["hit_maxiter"] for runs in nested.values() for run in runs)
    nested_span_pass = ln_span <= float(nested_cfg["stability"]["max_lnB10_span"])
    prior_sensitivity_finite = math.isfinite(float(sensitivity_ln_b10))
    pass_all = mcmc_pass and nested_finite and nested_not_maxed and nested_span_pass and prior_sensitivity_finite

    delta_bic = float(g4_receipt["deltas_vs_LCDM"]["RLL"]["delta_BIC"])
    bic_ln_proxy = -0.5 * delta_bic
    return {
        "schema": "rll.g6_canonical_inference_receipt.v1",
        "state": "PASS_LIMITED_G6_CANONICAL_INFERENCE" if pass_all else "BLOCKED_G6_CONVERGENCE_OR_EVIDENCE",
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "claim_allowed": False,
        "scientific_confirmation": False,
        "publication_effect": "NONE",
        "scope": contract["scope"],
        "g5_manifest_sha256": sha256_file(g5_manifest_path),
        "g5_manifest_event_id": g5_manifest.get("event_id"),
        "g4_receipt_sha256": g5_manifest["g4_receipt_sha256"],
        "executor_sha256": g5_manifest["executor_sha256"],
        "input_sha256": g5_manifest["input_sha256"],
        "environment_lock": _environment(),
        "mcmc": mcmc,
        "nested": nested,
        "bayes_factor": {
            "pairs": ln_b10,
            "lnB10_mean": ln_mean,
            "lnB10_span": float(ln_span),
            "interpretation_boundary": "relative evidence under common profiled/M_B flat-measure convention; not absolute universal logZ",
        },
        "prior_sensitivity": {
            "LCDM_base_prior_seed401": lcdm_sensitivity,
            "RLL_narrow_prior_seed401": rll_sensitivity,
            "lnB10_narrow_RLL_minus_LCDM": float(sensitivity_ln_b10),
            "delta_lnB10_narrow_minus_base_mean": float(sensitivity_ln_b10 - ln_mean),
            "posthoc_selection_forbidden": True,
        },
        "posterior_null_contact": mcmc["RLL"]["boundary_diagnostics"],
        "reconciliation": {
            "G4_delta_BIC_RLL_minus_LCDM": delta_bic,
            "G4_BIC_lnB10_proxy": bic_ln_proxy,
            "G6_nested_lnB10_mean": ln_mean,
            "same_sign_as_BIC_proxy": bool((bic_ln_proxy == 0.0 and ln_mean == 0.0) or bic_ln_proxy * ln_mean > 0.0),
            "historical_FASE20_role": "COMPARISON_ONLY_DIFFERENT_LIKELIHOOD_PRIORS_CALIBRATIONS",
        },
        "convergence": {
            "mcmc_pass": mcmc_pass,
            "nested_finite": nested_finite,
            "nested_not_maxiter": nested_not_maxed,
            "lnB10_span_pass": nested_span_pass,
            "prior_sensitivity_finite": prior_sensitivity_finite,
            "pass_all": pass_all,
        },
        "negative_results_preserved": True,
        "boundaries": [
            "G6 canonical inference != independent replication",
            "G6 background inference != G8 perturbation closure",
            "BIC proxy != nested evidence",
            "absolute logZ carries a common M_B-measure normalization; lnB10 is the intended comparison",
        ],
        "F_ok": [
            "MCMC and nested sampling consume the exact G5 hash-bound background likelihood",
            "multiple independent MCMC ensembles and nested seeds are recorded",
            "prior sensitivity is computed without selecting the preferred prior post-hoc",
        ],
        "F_gap": [] if pass_all else [
            item for item, ok in {
                "MCMC_CONVERGENCE": mcmc_pass,
                "NESTED_FINITE": nested_finite,
                "NESTED_MAXITER": nested_not_maxed,
                "NESTED_SEED_STABILITY": nested_span_pass,
                "PRIOR_SENSITIVITY": prior_sensitivity_finite,
            }.items() if not ok
        ],
        "F_next": "if PASS, execute G7 synthetic null/RLL recovery on the same G5 manifest and begin G10 clean-environment replay; G8 remains parallel physical-closure work",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run G6 canonical MCMC+nested inference")
    parser.add_argument("--g4-receipt", type=Path, required=True)
    parser.add_argument("--g5-manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--require-pass", action="store_true")
    args = parser.parse_args()
    try:
        report = build_report(args.g4_receipt, args.g5_manifest, ROOT)
    except Exception as exc:
        print(f"[rll] BLOCKED_G6_EXCEPTION: {exc}", file=sys.stderr)
        return 2
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    print(report["state"])
    print(f"lnB10_mean={report['bayes_factor']['lnB10_mean']:.6f} span={report['bayes_factor']['lnB10_span']:.6f}")
    print(f"RLL_max_Rhat={report['mcmc']['RLL']['max_Rhat']:.6f}")
    print("claim_allowed=false")
    if args.require_pass and report["state"] != "PASS_LIMITED_G6_CANONICAL_INFERENCE":
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
