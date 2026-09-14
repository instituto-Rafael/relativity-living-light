"""Flat-closure successor for the RLL joint real-data likelihood.

This module is additive. It preserves the historical legacy pipeline and derives
Omega_Lambda by flat closure so that E(0)=1 by construction for every compared
background model.

It intentionally inherits the current growth-index and compressed-CMB
approximations from joint_real_likelihood. Therefore closure can pass while
growth/CMB promotion remains fail-closed.

SOURCE != ARTEFACT != EXECUTION != EVIDENCE != CLAIM.
TOKEN_VAZIO != 0.
"""

from __future__ import annotations

import json
import os
import time
from typing import Any

import numpy as np

from . import joint_real_likelihood as legacy

MODEL_LCDM = legacy.MODEL_LCDM
MODEL_WCDM = legacy.MODEL_WCDM
MODEL_CPL = legacy.MODEL_CPL
MODEL_RLL = legacy.MODEL_RLL
MODEL_ORDER = legacy.MODEL_ORDER

FLAT_MODEL_PARAM_NAMES = {
    MODEL_LCDM: ("H0", "Om", "Ob_h2", "sigma8"),
    MODEL_WCDM: ("H0", "Om", "w", "Ob_h2", "sigma8"),
    MODEL_CPL: ("H0", "Om", "w0", "wa", "Ob_h2", "sigma8"),
    MODEL_RLL: ("H0", "Om", "Os0", "zt", "wt", "Ob_h2", "sigma8"),
}

FLAT_MODEL_BOUNDS = {
    MODEL_LCDM: [(60.0, 80.0), (0.10, 0.60), (0.018, 0.026), (0.50, 1.10)],
    MODEL_WCDM: [(60.0, 80.0), (0.10, 0.60), (-2.0, -0.3), (0.018, 0.026), (0.50, 1.10)],
    MODEL_CPL: [(60.0, 80.0), (0.10, 0.60), (-2.0, -0.3), (-3.0, 3.0), (0.018, 0.026), (0.50, 1.10)],
    MODEL_RLL: [(60.0, 80.0), (0.10, 0.60), (0.0, 0.25), (0.1, 10.0), (0.05, 2.0), (0.018, 0.026), (0.50, 1.10)],
}

DEFAULT_OUTPUT_STEM = "joint_real_likelihood_flat_closure_v1"


def _as_mapping(model: str, vector: np.ndarray) -> dict[str, float]:
    names = FLAT_MODEL_PARAM_NAMES[model]
    values = np.asarray(vector, dtype=float)
    if len(values) != len(names):
        raise ValueError(f"{model}: expected {len(names)} parameters, got {len(values)}")
    return {name: float(value) for name, value in zip(names, values)}


def derived_omega_lambda(model: str, vector: np.ndarray) -> float:
    values = _as_mapping(model, vector)
    omega_extra_z0 = values.get("Os0", 0.0)
    return float(1.0 - legacy.ORAD - values["Om"] - omega_extra_z0)


def expand_flat_vector(model: str, vector: np.ndarray) -> np.ndarray:
    values = _as_mapping(model, vector)
    ol = derived_omega_lambda(model, vector)

    if model == MODEL_LCDM:
        ordered = [values["H0"], values["Om"], ol, values["Ob_h2"], values["sigma8"]]
    elif model == MODEL_WCDM:
        ordered = [values["H0"], values["Om"], ol, values["w"], values["Ob_h2"], values["sigma8"]]
    elif model == MODEL_CPL:
        ordered = [values["H0"], values["Om"], ol, values["w0"], values["wa"], values["Ob_h2"], values["sigma8"]]
    elif model == MODEL_RLL:
        ordered = [
            values["H0"], values["Om"], ol, values["Os0"], values["zt"], values["wt"],
            values["Ob_h2"], values["sigma8"],
        ]
    else:
        raise ValueError(f"unknown model: {model}")
    return np.asarray(ordered, dtype=float)


def e0_squared(model: str, vector: np.ndarray) -> float:
    expanded = expand_flat_vector(model, vector)
    e2_fn, params, *_ = legacy._model_runtime(model, expanded)
    return float(e2_fn(0.0, *params))


def evaluate_components(model: str, vector: np.ndarray, inputs: dict) -> dict[str, float]:
    ol = derived_omega_lambda(model, vector)
    if not np.isfinite(ol) or ol <= 0.0:
        return {"total": float("inf")}
    return legacy.evaluate_components(model, expand_flat_vector(model, vector), inputs)


def fit_model(model: str, inputs: dict, seed: int, maxiter: int, tol: float) -> tuple[np.ndarray, dict[str, float]]:
    try:
        bounds = FLAT_MODEL_BOUNDS[model]
    except KeyError as exc:
        raise ValueError(f"unknown model: {model}") from exc

    result = legacy.differential_evolution(
        lambda values: evaluate_components(model, values, inputs)["total"],
        bounds,
        seed=seed,
        maxiter=maxiter,
        tol=tol,
        workers=1,
        polish=True,
    )
    vector = np.asarray(result.x, dtype=float)
    return vector, evaluate_components(model, vector, inputs)


def _model_row(
    model: str,
    vector: np.ndarray,
    components: dict[str, float],
    n_obs: int,
    registry: dict,
    commit_sha: str | None,
) -> dict[str, Any]:
    expanded = expand_flat_vector(model, vector)
    row = legacy._model_row(model, expanded, components, n_obs, registry=None, commit_sha=commit_sha)

    k = legacy.k_from_registry(FLAT_MODEL_PARAM_NAMES[model], registry)
    row["k"] = k
    row["dof"] = n_obs - k
    row["AIC"] = legacy.aic(components["total"], k)
    row["AICc"] = legacy.aicc(components["total"], k, n_obs)
    row["BIC"] = legacy.bic(components["total"], k, n_obs)
    row["OL"] = derived_omega_lambda(model, vector)
    row["closure_mode"] = "flat_derived_Omega_Lambda"
    row["e0_squared"] = e0_squared(model, vector)
    return row


def run_joint_likelihood_flat(output_stem: str = DEFAULT_OUTPUT_STEM) -> dict:
    if output_stem == "joint_real_likelihood":
        raise ValueError("flat successor must not overwrite the historical canonical output stem")

    start = time.perf_counter()
    inputs = legacy.load_joint_inputs()
    seed = int(os.environ.get("STRUCTURE_D_FLAT_SEED", os.environ.get("STRUCTURE_D_JOINT_SEED", "42")))
    tol = float(os.environ.get("STRUCTURE_D_FLAT_TOL", os.environ.get("STRUCTURE_D_JOINT_TOL", "1e-6")))
    default_maxiter = int(os.environ.get("STRUCTURE_D_FLAT_MAXITER", "140"))

    fitted: dict[str, tuple[np.ndarray, dict[str, float]]] = {}
    for offset, model in enumerate(MODEL_ORDER):
        fitted[model] = fit_model(model, inputs, seed + offset, default_maxiter, tol)

    registry = inputs["parameter_registry"]
    commit_sha = legacy._git_sha()
    n_obs = int(len(inputs["hz"]) + len(inputs["desi"]) + len(inputs["fs8"]) + 2)
    rows = [
        _model_row(model, fitted[model][0], fitted[model][1], n_obs, registry, commit_sha)
        for model in MODEL_ORDER
    ]
    rows_by_model = {row["model"]: row for row in rows}
    model_deltas = {
        model: legacy._delta_against(rows_by_model, model)
        for model in (MODEL_WCDM, MODEL_CPL, MODEL_RLL)
    }

    outputs = []
    outputs.append(
        legacy._atomic_write_text(
            legacy.RESULTS / f"{output_stem}.csv",
            legacy._rows_to_csv(rows),
        )
    )

    payload = {
        "schema": "rll.joint_real_likelihood.flat_closure.v1",
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "runtime_seconds": time.perf_counter() - start,
        "historical_pipeline_mutated": False,
        "closure": {
            "mode": "flat_derived_Omega_Lambda",
            "formula_standard": "Omega_Lambda = 1 - Omega_r - Omega_m",
            "formula_rll": "Omega_Lambda = 1 - Omega_r - Omega_m - Omega_s0",
            "e0_requirement": "E(0)=1",
            "pass_by_construction": all(
                np.isclose(row["e0_squared"], 1.0, rtol=0.0, atol=1.0e-12)
                for row in rows
            ),
        },
        "optimizer": {
            "name": "scipy.optimize.differential_evolution",
            "seed": seed,
            "tol": tol,
            "maxiter": default_maxiter,
            "models": list(MODEL_ORDER),
        },
        "datasets": {
            "Hz": str(legacy.HZ_PATH.relative_to(legacy.BASE_DIR)),
            "DESI_DR2_BAO_primary": str(legacy.DESI_POINTS_PATH.relative_to(legacy.BASE_DIR)),
            "fsigma8": str(legacy.FSIGMA8_PATH.relative_to(legacy.BASE_DIR)),
            "CMB_shift": str(legacy.CMB_SHIFT_PATH.relative_to(legacy.BASE_DIR)),
            "parameter_origin_registry": str(legacy.PARAMETER_REGISTRY_PATH.relative_to(legacy.BASE_DIR)),
        },
        "inherited_open_gates": {
            "growth": "TOKEN_VAZIO_IMPLEMENTATION: current f_sigma8 remains growth-index proxy without validated D(z)",
            "cmb": "TOKEN_VAZIO_IMPLEMENTATION: current l_A still requires validated r_s(z_star) rather than r_d(z_drag)",
            "posterior": "TOKEN_VAZIO_EXECUTION: robust posterior/MCMC is not promoted by closure alone",
        },
        "claim_allowed": False,
        "model_selection_claim_allowed": False,
        "rows": legacy._json_safe(rows),
        "model_deltas_vs_lcdm": legacy._json_safe(model_deltas),
        "invariants": [
            "SOURCE != ARTEFACT != EXECUTION != EVIDENCE != CLAIM",
            "TOKEN_VAZIO != 0",
            "IMPLEMENTED_UNTESTED != PASS",
            "CLOSURE_PASS != GROWTH_PASS != CMB_PASS != MODEL_SELECTION_PASS",
        ],
    }
    outputs.append(
        legacy._atomic_write_text(
            legacy.RESULTS / f"{output_stem}.json",
            json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        )
    )

    manifest = {
        "schema": "rll.joint_real_likelihood.flat_closure_manifest.v1",
        "output_stem": output_stem,
        "historical_outputs_overwritten": False,
        "input_sha256": {
            str(path.relative_to(legacy.BASE_DIR)): legacy._sha256_file(path)
            for path in [
                legacy.HZ_PATH,
                legacy.DESI_POINTS_PATH,
                legacy.FSIGMA8_PATH,
                legacy.CMB_SHIFT_PATH,
                legacy.PARAMETER_REGISTRY_PATH,
            ]
        },
        "claim_allowed": False,
    }
    outputs.append(
        legacy._atomic_write_text(
            legacy.RESULTS / f"{output_stem}_manifest.json",
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        )
    )

    payload["outputs"] = outputs
    return payload


def main() -> dict:
    output_stem = os.environ.get("STRUCTURE_D_FLAT_OUTPUT_STEM", DEFAULT_OUTPUT_STEM).strip() or DEFAULT_OUTPUT_STEM
    payload = run_joint_likelihood_flat(output_stem=output_stem)
    print(payload["schema"])
    for row in payload["rows"]:
        print(
            row["model"],
            "E0^2=", row["e0_squared"],
            "OL=", row["OL"],
            "chi2=", row["chi2"],
        )
    for output in payload["outputs"]:
        print("Wrote:", output["path"])
    return payload


if __name__ == "__main__":
    main()
