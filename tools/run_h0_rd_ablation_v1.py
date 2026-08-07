#!/usr/bin/env python3
from __future__ import annotations

"""Execute the six-cell H0/r_d sensitivity matrix with claim boundaries.

This is an ablation/sensitivity authority, not a publication likelihood. The
Planck H0 Gaussian is correlated with the compressed Planck CMB term already in
the joint objective, and the current derived-r_d function is an approximation.
Both facts are preserved explicitly in the receipt.
"""

import argparse
import contextlib
import csv
import hashlib
import json
import math
import os
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Iterator, Sequence

import numpy as np
from scipy.optimize import minimize

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data.pipelines.structure_d import joint_real_likelihood as joint  # noqa: E402

MATRIX = ROOT / "data/inputs/cosmology_joint/h0_rd_ablation_matrix.json"
SCHEMA = "rll.h0_rd_ablation_execution.v1"

CANONICAL_STARTS: dict[str, np.ndarray] = {
    joint.MODEL_LCDM: np.asarray([68.0, 0.30, 0.70, 0.0224, 0.80]),
    joint.MODEL_WCDM: np.asarray([68.0, 0.30, 0.70, -1.0, 0.0224, 0.80]),
    joint.MODEL_CPL: np.asarray([68.0, 0.30, 0.70, -1.0, 0.0, 0.0224, 0.80]),
    joint.MODEL_RLL: np.asarray([68.0, 0.30, 0.70, 0.01, 1.0, 0.30, 0.0224, 0.80]),
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        tmp = Path(handle.name)
        json.dump(payload, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    try:
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)


def parse_h0_bounds(text: str) -> tuple[float, float]:
    parts = str(text).replace(" ", "").split("..")
    if len(parts) != 2:
        raise ValueError(f"invalid H0 bounds: {text!r}")
    lower, upper = map(float, parts)
    if not (math.isfinite(lower) and math.isfinite(upper) and 0.0 < lower < upper):
        raise ValueError(f"invalid H0 interval: {text!r}")
    return lower, upper


def load_matrix(path: Path = MATRIX) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema") != "rll.h0_rd_ablation_matrix.v1":
        raise ValueError("unexpected H0/r_d matrix schema")
    runs = payload.get("runs")
    if not isinstance(runs, list) or len(runs) != 6:
        raise ValueError("H0/r_d matrix must declare exactly six runs")
    ids = [row.get("run_id") for row in runs]
    if len(set(ids)) != 6:
        raise ValueError("H0/r_d run ids must be unique")
    for row in runs:
        parse_h0_bounds(row["H0_bounds"])
        if row["rd_policy"] not in {"fixed_for_all", "derived_for_all"}:
            raise ValueError(f"unsupported rd policy: {row['rd_policy']}")
        if row["H0_policy"] not in {"broad_free", "planck_prior", "shoes_local_prior"}:
            raise ValueError(f"unsupported H0 policy: {row['H0_policy']}")
    return payload


@contextlib.contextmanager
def rd_policy_context(policy: str, fixed_value: float | None) -> Iterator[None]:
    original = joint.rd_drag_mpc
    if policy == "fixed_for_all":
        if fixed_value is None or not math.isfinite(float(fixed_value)) or float(fixed_value) <= 0.0:
            raise ValueError("fixed r_d policy requires a positive finite value")
        value = float(fixed_value)
        joint.rd_drag_mpc = lambda h0, om, ob_h2: value  # type: ignore[assignment]
    elif policy != "derived_for_all":
        raise ValueError(f"unsupported r_d policy: {policy}")
    try:
        yield
    finally:
        joint.rd_drag_mpc = original  # type: ignore[assignment]


def h0_penalty(h0: float, spec: dict[str, Any]) -> float:
    mean = spec.get("H0_prior_mean")
    sigma = spec.get("H0_prior_sigma")
    if mean is None and sigma is None:
        return 0.0
    if mean is None or sigma is None or float(sigma) <= 0.0:
        raise ValueError(f"invalid H0 prior in {spec['run_id']}")
    return ((float(h0) - float(mean)) / float(sigma)) ** 2


def policy_role(spec: dict[str, Any]) -> dict[str, Any]:
    if spec["H0_policy"] == "planck_prior":
        return {
            "role": "conditioning_sensitivity_correlated_with_existing_CMB",
            "independent_external_likelihood": False,
            "information_criteria_authoritative": False,
            "reason": "Planck-derived H0 information overlaps the Planck compressed CMB-shift term already in the joint objective.",
        }
    if spec["H0_policy"] == "shoes_local_prior":
        return {
            "role": "external_local_ladder_candidate_pending_primary_source_receipt",
            "independent_external_likelihood": True,
            "information_criteria_authoritative": False,
            "reason": "The Gaussian is declared numerically, but this runner does not freeze/hash its primary-source artifact.",
        }
    return {
        "role": "no_external_H0_conditioning",
        "independent_external_likelihood": True,
        "information_criteria_authoritative": True,
        "reason": "No external H0 Gaussian is added.",
    }


def model_bounds(model: str, spec: dict[str, Any]) -> list[tuple[float, float]]:
    bounds = [tuple(map(float, pair)) for pair in joint.MODEL_BOUNDS[model]]
    bounds[0] = parse_h0_bounds(spec["H0_bounds"])
    return bounds


def objective(
    model: str,
    vector: np.ndarray,
    inputs: dict[str, Any],
    spec: dict[str, Any],
) -> tuple[float, dict[str, float]]:
    components = joint.evaluate_components(model, np.asarray(vector, dtype=float), inputs)
    data_total = float(components["total"])
    if not math.isfinite(data_total):
        return math.inf, {**components, "H0_conditioning": math.inf, "objective_total": math.inf}
    penalty = float(h0_penalty(float(vector[0]), spec))
    return data_total + penalty, {
        **{key: float(value) for key, value in components.items()},
        "H0_conditioning": penalty,
        "objective_total": data_total + penalty,
    }


def starts_for(model: str, spec: dict[str, Any]) -> list[np.ndarray]:
    bounds = model_bounds(model, spec)
    primary = CANONICAL_STARTS[model].copy()
    candidates: list[np.ndarray] = []
    h0_values = [float(spec["H0_prior_mean"])] if spec.get("H0_prior_mean") is not None else [68.0]
    h0_values += [55.0, 67.4, 73.04, 82.0]
    for h0 in h0_values:
        candidate = primary.copy()
        candidate[0] = h0
        clipped = np.asarray([
            min(max(float(value), lower), upper)
            for value, (lower, upper) in zip(candidate, bounds)
        ])
        candidates.append(clipped)
    unique: list[np.ndarray] = []
    seen: set[tuple[float, ...]] = set()
    for candidate in candidates:
        key = tuple(np.round(candidate, 10))
        if key not in seen:
            seen.add(key)
            unique.append(candidate)
    return unique


def fit_model(
    model: str,
    inputs: dict[str, Any],
    spec: dict[str, Any],
    *,
    maxiter: int,
    ftol: float,
) -> dict[str, Any]:
    bounds = model_bounds(model, spec)
    attempts: list[dict[str, Any]] = []
    for index, start in enumerate(starts_for(model, spec)):
        began = time.perf_counter()
        result = minimize(
            lambda values: objective(model, np.asarray(values, dtype=float), inputs, spec)[0],
            start,
            method="L-BFGS-B",
            bounds=bounds,
            options={"maxiter": int(maxiter), "ftol": float(ftol), "maxls": 40},
        )
        total, components = objective(model, np.asarray(result.x, dtype=float), inputs, spec)
        attempts.append({
            "start_index": index,
            "success": bool(result.success),
            "message": str(result.message),
            "iterations": int(result.nit),
            "function_evaluations": int(result.nfev),
            "runtime_seconds": float(time.perf_counter() - began),
            "vector": [float(x) for x in result.x],
            "objective_total": float(total),
            "components": components,
        })
    finite = [row for row in attempts if math.isfinite(row["objective_total"])]
    if not finite:
        raise RuntimeError(f"no finite optimization result for {spec['run_id']} {model}")
    best = min(finite, key=lambda row: row["objective_total"])
    vector = np.asarray(best["vector"], dtype=float)
    runtime = joint._model_runtime(model, vector)
    ob_h2 = float(runtime[3])
    rd = (
        float(spec["rd_fixed_value_mpc"])
        if spec["rd_policy"] == "fixed_for_all"
        else float(joint.rd_drag_mpc(vector[0], vector[1], ob_h2))
    )
    names = joint.MODEL_PARAM_NAMES[model]
    params = {name: float(value) for name, value in zip(names, vector)}
    boundary_hits = []
    for name, value, (lower, upper) in zip(names, vector, bounds):
        scale = max(1.0, abs(lower), abs(upper))
        if abs(float(value) - lower) <= 1.0e-5 * scale:
            boundary_hits.append({"parameter": name, "side": "lower", "bound": lower, "value": float(value)})
        if abs(float(value) - upper) <= 1.0e-5 * scale:
            boundary_hits.append({"parameter": name, "side": "upper", "bound": upper, "value": float(value)})
    return {
        "model": model,
        "parameters": params,
        "rd_mpc": rd,
        "chi2_data": float(best["components"]["total"]),
        "chi2_H0_conditioning": float(best["components"]["H0_conditioning"]),
        "objective_total": float(best["objective_total"]),
        "boundary_hits": boundary_hits,
        "best_attempt_success": bool(best["success"]),
        "converged_attempts": sum(bool(row["success"]) for row in attempts),
        "attempt_count": len(attempts),
        "attempts": attempts,
    }


def n_data(inputs: dict[str, Any]) -> int:
    cmb = inputs["cmb"]
    cmb_n = 3 if cmb.get("parameter_order") == ["R", "la", "ob_h2"] and cmb.get("covariance") is not None else 2
    return len(inputs["hz"]) + len(inputs["desi"]) + len(inputs["fs8"]) + cmb_n


def run_cell(
    spec: dict[str, Any],
    inputs: dict[str, Any],
    *,
    maxiter: int,
    ftol: float,
) -> dict[str, Any]:
    role = policy_role(spec)
    with rd_policy_context(spec["rd_policy"], spec.get("rd_fixed_value_mpc")):
        models = {
            model: fit_model(model, inputs, spec, maxiter=maxiter, ftol=ftol)
            for model in joint.MODEL_ORDER
        }
    cpl = models[joint.MODEL_CPL]
    rll = models[joint.MODEL_RLL]
    return {
        "run_id": spec["run_id"],
        "H0_policy": spec["H0_policy"],
        "H0_prior_label": spec["H0_prior_label"],
        "H0_prior_mean": spec.get("H0_prior_mean"),
        "H0_prior_sigma": spec.get("H0_prior_sigma"),
        "H0_bounds": list(parse_h0_bounds(spec["H0_bounds"])),
        "rd_policy": spec["rd_policy"],
        "rd_fixed_value_mpc": spec.get("rd_fixed_value_mpc"),
        "policy_role": role,
        "models": models,
        "delta_objective_RLL_minus_CPL": float(rll["objective_total"] - cpl["objective_total"]),
        "delta_chi2_data_RLL_minus_CPL": float(rll["chi2_data"] - cpl["chi2_data"]),
        "claim_allowed": False,
    }


def write_csvs(output_dir: Path, cells: list[dict[str, Any]], nobs: int) -> list[str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths: list[str] = []
    fields = [
        "model", "chi2", "AIC", "AICc", "BIC", "N", "k", "dof",
        "H0_policy", "rd_policy", "H0", "rd", "Os0", "Delta_AICc_RLL_CPL",
        "Delta_BIC_RLL_CPL", "claim_status", "chi2_data", "chi2_H0_conditioning",
        "information_criteria_authoritative",
    ]
    for cell in cells:
        path = output_dir / f"{cell['run_id']}.csv"
        rows: list[dict[str, Any]] = []
        for model in joint.MODEL_ORDER:
            result = cell["models"][model]
            k = len(joint.MODEL_PARAM_NAMES[model])
            chi2 = result["objective_total"]
            aic = chi2 + 2.0 * k
            aicc = aic + 2.0 * k * (k + 1) / (nobs - k - 1)
            bic = chi2 + k * math.log(nobs)
            rows.append({
                "model": model,
                "chi2": chi2,
                "AIC": aic,
                "AICc": aicc,
                "BIC": bic,
                "N": nobs,
                "k": k,
                "dof": nobs - k,
                "H0_policy": cell["H0_policy"],
                "rd_policy": cell["rd_policy"],
                "H0": result["parameters"]["H0"],
                "rd": result["rd_mpc"],
                "Os0": result["parameters"].get("Os0", ""),
                "Delta_AICc_RLL_CPL": "",
                "Delta_BIC_RLL_CPL": "",
                "claim_status": "SENSITIVITY_ONLY",
                "chi2_data": result["chi2_data"],
                "chi2_H0_conditioning": result["chi2_H0_conditioning"],
                "information_criteria_authoritative": cell["policy_role"]["information_criteria_authoritative"],
            })
        cpl = next(row for row in rows if row["model"] == joint.MODEL_CPL)
        rll = next(row for row in rows if row["model"] == joint.MODEL_RLL)
        rll["Delta_AICc_RLL_CPL"] = float(rll["AICc"] - cpl["AICc"])
        rll["Delta_BIC_RLL_CPL"] = float(rll["BIC"] - cpl["BIC"])
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
        paths.append(str(path.relative_to(ROOT)))
    return paths


def build(output: Path, output_dir: Path, *, maxiter: int = 60, ftol: float = 1.0e-8) -> dict[str, Any]:
    matrix = load_matrix()
    inputs = joint.load_joint_inputs()
    began = time.perf_counter()
    cells = [run_cell(spec, inputs, maxiter=maxiter, ftol=ftol) for spec in matrix["runs"]]
    nobs = n_data(inputs)
    csv_paths = write_csvs(output_dir, cells, nobs)
    all_finite = all(
        math.isfinite(cell["models"][model]["objective_total"])
        for cell in cells for model in joint.MODEL_ORDER
    )
    payload = {
        "schema": SCHEMA,
        "state": "VERIFIED_INTERNAL_H0_RD_SENSITIVITY" if all_finite else "TOKEN_VAZIO_NUMERICAL_EXECUTION",
        "claim_allowed": False,
        "publication_ready": False,
        "matrix_path": str(MATRIX.relative_to(ROOT)),
        "matrix_sha256": sha256_file(MATRIX),
        "joint_likelihood_path": "data/pipelines/structure_d/joint_real_likelihood.py",
        "joint_likelihood_sha256": sha256_file(ROOT / "data/pipelines/structure_d/joint_real_likelihood.py"),
        "n_joint_data_coordinates": nobs,
        "cells": cells,
        "csv_outputs": csv_paths,
        "runtime_seconds": float(time.perf_counter() - began),
        "interpretation": {
            "six_cells_executed": len(cells) == 6,
            "models_per_cell": len(joint.MODEL_ORDER),
            "planck_h0_is_independent_of_planck_cmb_shift": False,
            "primary_external_h0_source_receipts_frozen": False,
            "derived_rd_is_full_boltzmann_recombination_solution": False,
        },
        "scientific_boundary": "This closes only the internal six-cell sensitivity computation. Planck H0 conditioning overlaps the existing Planck CMB-shift term, external H0 primary-source receipts are not frozen here, and derived r_d uses the repository approximation rather than a full recombination/Boltzmann solver. No H0-tension-resolution or model-evidence claim is authorized.",
        "reduces_token": "TOKEN_VAZIO_H0_RD_ABLATION_EXECUTION_PROVENANCE",
        "successor_tokens": [
            "TOKEN_VAZIO_H0_PRIOR_PRIMARY_SOURCE_PROVENANCE",
            "TOKEN_VAZIO_H0_RD_FULL_BOLTZMANN_REPRODUCTION",
        ],
        "F_ok": [
            "All six H0/r_d cells are evaluated under one model/data implementation.",
            "Data chi2 and H0-conditioning chi2 are stored separately.",
            "Planck overlap and derived-r_d approximation are explicit."
        ],
        "F_gap": [
            "TOKEN_VAZIO_H0_PRIOR_PRIMARY_SOURCE_PROVENANCE",
            "TOKEN_VAZIO_H0_RD_FULL_BOLTZMANN_REPRODUCTION",
        ],
        "F_next": [
            "Freeze/hash primary H0 source artifacts and classify correlated versus independent terms.",
            "Replace the calibrated r_d approximation with a pinned CLASS/CAMB recombination calculation before formal H0/r_d inference."
        ],
    }
    atomic_json(output, payload)
    return payload


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--maxiter", type=int, default=60)
    parser.add_argument("--ftol", type=float, default=1.0e-8)
    args = parser.parse_args(argv)
    try:
        payload = build(args.output, args.output_dir, maxiter=args.maxiter, ftol=args.ftol)
    except Exception as exc:
        print(f"ERROR: {type(exc).__name__}: {exc}")
        return 2
    print(json.dumps({"state": payload["state"], "cells": len(payload["cells"]), "claim_allowed": False}, sort_keys=True))
    return 0 if payload["state"] == "VERIFIED_INTERNAL_H0_RD_SENSITIVITY" else 3


if __name__ == "__main__":
    raise SystemExit(main())
