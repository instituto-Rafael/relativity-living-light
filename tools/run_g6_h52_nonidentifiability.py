#!/usr/bin/env python3
"""Controlled H52 diagnostic for G6 null non-identifiability.

This successor does not rewrite the historical G6 receipt. It reruns the exact
G5 background likelihood with a longer, explicitly seeded MCMC in two arms:

1. free-shape RLL: H0, Omega_m, omega_b_h2, Omega_s0, z_t, w_t;
2. fixed-shape diagnostic: the same likelihood while z_t=1 and w_t=0.30 are
   frozen to the repository's pre-existing canonical defaults.

The two arms use identical seeds, walkers, steps, burn and Rhat threshold.
The fixed arm is diagnostic only. It cannot be used as an RLL model-selection
claim and it does not close nested evidence, perturbations, or CLASS/CAMB.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import sys
import time
from pathlib import Path
from types import ModuleType
from typing import Any, Sequence

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
G4_PATH = ROOT / "tools/run_g4_background_tournament.py"
G5_PATH = ROOT / "tools/build_g5_canonical_background_manifest.py"
G6_PATH = ROOT / "tools/run_g6_canonical_inference.py"
CONTRACT_PATH = ROOT / "data/contracts/rll_g6_h52_nonidentifiability.v1.json"


def _module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected JSON object")
    return value


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _validate_manifest(g4_receipt_path: Path, g5_manifest_path: Path, root: Path):
    g5 = _module("rll_h52_g5_builder", root / G5_PATH.relative_to(ROOT))
    observed = _json(g5_manifest_path)
    expected = g5.build_manifest(g4_receipt_path, root)
    if expected.get("state") != "READY_G5_CANONICAL_BACKGROUND_LIKELIHOOD":
        raise RuntimeError("G5 prerequisite cannot be reconstructed")
    keys = (
        "g4_receipt_sha256",
        "executor_sha256",
        "g4_contract_sha256",
        "g5_contract_sha256",
        "input_sha256",
        "models",
        "selection_registry",
        "covariance_registry",
    )
    for key in keys:
        if observed.get(key) != expected.get(key):
            raise RuntimeError(f"G5 manifest mismatch in {key}")
    if observed.get("claim_allowed") is not False:
        raise RuntimeError("G5 claim_allowed drift")
    return observed


def _sampled_bounds(g4: ModuleType, g6: ModuleType, names: Sequence[str]) -> np.ndarray:
    full_names = list(g4.parameter_names("RLL"))
    full_bounds = g6._bounds_array(g4, "RLL")
    mapping = {name: full_bounds[index] for index, name in enumerate(full_names)}
    return np.asarray([mapping[name] for name in names], dtype=float)


def _pack_full(
    g4: ModuleType,
    sampled_names: Sequence[str],
    sampled: np.ndarray,
    fixed: dict[str, float],
) -> np.ndarray:
    values = {name: float(value) for name, value in zip(sampled_names, sampled, strict=True)}
    values.update({str(name): float(value) for name, value in fixed.items()})
    full_names = list(g4.parameter_names("RLL"))
    missing = [name for name in full_names if name not in values]
    if missing:
        raise ValueError(f"projected RLL vector missing parameters: {missing}")
    return np.asarray([values[name] for name in full_names], dtype=float)


def run_projected_mcmc(
    g4: ModuleType,
    g6: ModuleType,
    data: Any,
    best: dict[str, Any],
    *,
    sampled_names: Sequence[str],
    fixed: dict[str, float],
    seeds: Sequence[int],
    walkers: int,
    steps: int,
    burn: int,
) -> dict[str, Any]:
    names = list(sampled_names)
    bounds = _sampled_bounds(g4, g6, names)
    ndim = len(names)
    if walkers < 2 * ndim:
        raise ValueError(f"walkers={walkers} < 2*ndim={2*ndim}")
    center = np.asarray([float(best[name]) for name in names], dtype=float)
    widths = bounds[:, 1] - bounds[:, 0]
    eps = 1.0e-8 * widths

    def log_prob(theta: np.ndarray) -> float:
        arr = np.asarray(theta, dtype=float)
        if not g6._inside(arr, bounds):
            return -np.inf
        full = _pack_full(g4, names, arr, fixed)
        value = g6._log_likelihood(g4, data, "RLL", full)
        return value if value > -1.0e299 else -np.inf

    ensemble_records: list[dict[str, Any]] = []
    chains: list[np.ndarray] = []
    samples: list[np.ndarray] = []
    for seed in seeds:
        rng = np.random.default_rng(int(seed))
        p0 = center + rng.normal(0.0, 0.02, size=(walkers, ndim)) * widths
        p0 = np.clip(p0, bounds[:, 0] + eps, bounds[:, 1] - eps)
        sampler = g6.emcee.EnsembleSampler(walkers, ndim, log_prob)
        fingerprint = g6._seed_emcee_sampler(sampler, int(seed))
        started = time.perf_counter()
        sampler.run_mcmc(p0, steps, progress=False, skip_initial_state_check=True)
        elapsed = time.perf_counter() - started
        post = np.asarray(sampler.get_chain(discard=burn), dtype=float)
        flat = post.reshape(-1, ndim)
        if not np.all(np.isfinite(flat)):
            raise RuntimeError(f"fixed-shape arm: non-finite samples seed={seed}")
        chains.append(flat)
        samples.append(flat)
        ensemble_records.append({
            "seed": int(seed),
            "proposal_rng_policy": "explicit_verified_emcee_internal_random_state",
            "proposal_rng_state_sha256": fingerprint,
            "postburn_samples": int(flat.shape[0]),
            "mean_acceptance_fraction": float(np.mean(sampler.acceptance_fraction)),
            "runtime_seconds": float(elapsed),
        })

    rhats = g6._split_rhat(chains)
    combined = np.concatenate(samples, axis=0)
    quantiles: dict[str, dict[str, float]] = {}
    for index, name in enumerate(names):
        q16, q50, q84, q95 = np.quantile(combined[:, index], [0.16, 0.50, 0.84, 0.95])
        quantiles[name] = {
            "q16": float(q16),
            "q50": float(q50),
            "q84": float(q84),
            "q95": float(q95),
        }
    idx = names.index("Omega_s0")
    prior_width = bounds[idx, 1] - bounds[idx, 0]
    boundary = {
        "Omega_s0_fraction_within_1pct_prior_width_of_zero": float(
            np.mean(combined[:, idx] <= bounds[idx, 0] + 0.01 * prior_width)
        ),
        "Omega_s0_q95": quantiles["Omega_s0"]["q95"],
    }
    return {
        "model": "RLL_FIXED_SHAPE_DIAGNOSTIC",
        "sampled_parameter_names": names,
        "fixed_parameters": {str(k): float(v) for k, v in fixed.items()},
        "ensembles": ensemble_records,
        "total_postburn_samples": int(combined.shape[0]),
        "Rhat": dict(zip(names, [float(x) for x in rhats], strict=True)),
        "max_Rhat": float(max(rhats)),
        "quantiles": quantiles,
        "boundary_diagnostics": boundary,
    }


def _excess_over_one(value: float) -> float:
    return max(0.0, float(value) - 1.0)


def _classify(free_rhat: float, fixed_rhat: float, threshold: float) -> str:
    free_pass = free_rhat <= threshold
    fixed_pass = fixed_rhat <= threshold
    if not free_pass and fixed_pass:
        return "SUPPORTED_LIMITED_H52_NONIDENTIFIABILITY"
    if free_pass and fixed_pass:
        return "LONGER_CHAIN_SUFFICIENT_H52_NOT_REQUIRED_FOR_CONVERGENCE"
    if not free_pass and not fixed_pass:
        return "H52_NOT_RESOLVED_BOTH_ARMS_NONCONVERGED"
    return "H52_ANOMALOUS_FIXED_SHAPE_WORSE"


def build_report(g4_receipt_path: Path, g5_manifest_path: Path, root: Path = ROOT) -> dict[str, Any]:
    g4 = _module("rll_h52_g4", root / G4_PATH.relative_to(ROOT))
    g6 = _module("rll_h52_g6", root / G6_PATH.relative_to(ROOT))
    contract = _json(root / CONTRACT_PATH.relative_to(ROOT))
    if contract.get("claim_allowed") is not False:
        raise RuntimeError("H52 contract claim_allowed drift")

    g5 = _validate_manifest(g4_receipt_path, g5_manifest_path, root)
    g4_receipt = _json(g4_receipt_path)
    best = next(row for row in g4_receipt["rows"] if row["model"] == "RLL")
    data = g4.load_data(integration_points=4096)

    cfg = contract["mcmc"]
    seeds = [int(value) for value in cfg["seeds"]]
    walkers = int(cfg["walkers_per_ensemble"])
    steps = int(cfg["steps"])
    burn = int(cfg["burn"])
    threshold = float(cfg["convergence"]["max_split_Rhat"])
    minimum = int(cfg["convergence"]["minimum_postburn_samples_per_ensemble"])

    free = g6.run_mcmc(
        g4,
        data,
        "RLL",
        best,
        seeds=seeds,
        walkers=walkers,
        steps=steps,
        burn=burn,
    )
    fixed_spec = contract["fixed_shape_diagnostic_arm"]
    fixed = run_projected_mcmc(
        g4,
        g6,
        data,
        best,
        sampled_names=fixed_spec["sampled"],
        fixed={str(k): float(v) for k, v in fixed_spec["fixed"].items()},
        seeds=seeds,
        walkers=walkers,
        steps=steps,
        burn=burn,
    )

    if any(int(row["postburn_samples"]) < minimum for row in free["ensembles"]):
        raise RuntimeError("free arm violates preregistered minimum postburn samples")
    if any(int(row["postburn_samples"]) < minimum for row in fixed["ensembles"]):
        raise RuntimeError("fixed arm violates preregistered minimum postburn samples")

    free_rhat = float(free["max_Rhat"])
    fixed_rhat = float(fixed["max_Rhat"])
    state = _classify(free_rhat, fixed_rhat, threshold)
    shared = list(fixed_spec["sampled"])
    shared_delta = {
        name: float(free["Rhat"][name] - fixed["Rhat"][name])
        for name in shared
    }
    free_excess = _excess_over_one(free_rhat)
    fixed_excess = _excess_over_one(fixed_rhat)
    excess_reduction = free_excess - fixed_excess
    fraction = None if free_excess == 0.0 else float(excess_reduction / free_excess)
    os_q95_free = float(free["quantiles"]["Omega_s0"]["q95"])
    os_q95_fixed = float(fixed["quantiles"]["Omega_s0"]["q95"])

    return {
        "schema": "rll.g6_h52_nonidentifiability_receipt.v1",
        "state": state,
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "claim_allowed": False,
        "scientific_confirmation": False,
        "publication_effect": "NONE",
        "hypothesis_id": "H52",
        "contract_sha256": sha256_file(root / CONTRACT_PATH.relative_to(ROOT)),
        "g4_receipt_sha256": sha256_file(g4_receipt_path),
        "g5_manifest_sha256": sha256_file(g5_manifest_path),
        "g5_event_id": g5.get("event_id"),
        "likelihood_identity_preserved": True,
        "threshold_Rhat": threshold,
        "mcmc_settings": {
            "seeds": seeds,
            "walkers_per_ensemble": walkers,
            "steps": steps,
            "burn": burn,
            "minimum_postburn_samples_per_ensemble": minimum,
        },
        "free_shape": free,
        "fixed_shape_diagnostic": fixed,
        "comparison": {
            "free_max_Rhat": free_rhat,
            "fixed_max_Rhat": fixed_rhat,
            "absolute_max_Rhat_reduction": float(free_rhat - fixed_rhat),
            "free_excess_over_one": free_excess,
            "fixed_excess_over_one": fixed_excess,
            "excess_over_one_reduction": float(excess_reduction),
            "excess_over_one_reduction_fraction": fraction,
            "shared_parameter_Rhat_reduction_free_minus_fixed": shared_delta,
            "Omega_s0_q95_free": os_q95_free,
            "Omega_s0_q95_fixed": os_q95_fixed,
            "Omega_s0_q95_abs_shift": abs(os_q95_free - os_q95_fixed),
            "free_convergence_pass": bool(free_rhat <= threshold),
            "fixed_convergence_pass": bool(fixed_rhat <= threshold),
            "uncertainty_reduction_observed": bool(fixed_rhat < free_rhat),
            "convergence_gate_recovered_by_fixed_shape": bool(free_rhat > threshold and fixed_rhat <= threshold),
        },
        "interpretation": {
            "supported_limited": state == "SUPPORTED_LIMITED_H52_NONIDENTIFIABILITY",
            "meaning": (
                "If supported_limited=true, the controlled removal of z_t/w_t null-only shape freedom "
                "restored the preregistered MCMC convergence gate under identical data, likelihood, seeds, "
                "walkers, chain length and threshold. This narrows the cause of the G6 mixing pathology."
            ),
            "not_claimed": [
                "RLL is physically validated",
                "G6 nested evidence is stable",
                "RLL perturbations are closed",
                "CLASS/CAMB RLL implementation is unlocked",
                "fixed-shape diagnostic is a preferred physical model",
            ],
        },
        "negative_results_preserved": True,
        "F_ok": [
            "exact G4/G5 hash-bound likelihood reused",
            "same MCMC controls in both diagnostic arms",
            "explicit verified emcee proposal RNG retained",
            "historical G6 receipt not overwritten",
        ],
        "F_gap": [
            "NESTED_SEED_STABILITY remains separately open",
            "RLL perturbation closure remains blocked",
            "RLL CLASS/CAMB implementation remains blocked",
            "independent replication remains open",
        ],
        "F_next": (
            "If H52 is supported, version a nonregular-inference strategy before rerunning nested evidence; "
            "if not supported, investigate multimodality/likelihood geometry without relaxing thresholds."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run controlled H52 G6 non-identifiability diagnostic")
    parser.add_argument("--g4-receipt", type=Path, required=True)
    parser.add_argument("--g5-manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        report = build_report(args.g4_receipt, args.g5_manifest, ROOT)
    except Exception as exc:
        print(f"[rll] BLOCKED_H52_EXCEPTION: {exc}", file=sys.stderr)
        return 2
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(report["state"])
    print(
        "free_max_Rhat=%.6f fixed_max_Rhat=%.6f reduction=%.6f"
        % (
            report["comparison"]["free_max_Rhat"],
            report["comparison"]["fixed_max_Rhat"],
            report["comparison"]["absolute_max_Rhat_reduction"],
        )
    )
    print("claim_allowed=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
