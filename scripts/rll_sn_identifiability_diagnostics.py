#!/usr/bin/env python3
"""Diagnose boundary sensitivity and SN-only parameter identifiability.

This diagnostic consumes already materialized Pantheon+/DES-Dovekie fit results.
It does not refit, promote claims, or reinterpret information criteria as evidence.
Its purpose is to turn optimizer boundary hits and null-nested flat directions into
explicit, auditable uncertainties/TOKEN_VAZIO states.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PRODUCT_SRC = ROOT / "products" / "rll-evidence-runner" / "src"
sys.path.insert(0, str(PRODUCT_SRC))

from rll_evidence import pantheon_fit as pantheon_core  # noqa: E402
from rll_evidence import pantheon_fit_three_model as pantheon_three  # noqa: E402
from rll_evidence import dovekie_fit_three_model as dovekie_three  # noqa: E402

SCHEMA = "rll_sn_identifiability_diagnostics_v1"


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: JSON root must be an object")
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
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


def boundary_hits(parameters: dict[str, Any], names: tuple[str, ...], bounds: tuple[tuple[float, float], ...]) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    for name, (lower, upper) in zip(names, bounds):
        if name not in parameters:
            continue
        value = float(parameters[name])
        tolerance = 1.0e-5 * max(1.0, float(upper - lower))
        side = None
        if abs(value - float(lower)) <= tolerance:
            side = "lower"
        elif abs(value - float(upper)) <= tolerance:
            side = "upper"
        if side:
            hits.append(
                {
                    "parameter": name,
                    "value": value,
                    "side": side,
                    "bound": float(lower if side == "lower" else upper),
                    "tolerance": tolerance,
                }
            )
    return hits


def model_diagnostic(
    result: dict[str, Any],
    model: str,
    spec: dict[str, Any],
    *,
    z_max: float,
    baseline_model: str,
) -> dict[str, Any]:
    fit = result["models"][model]
    best = fit["best"]
    names = tuple(spec["parameter_names"])
    bounds = tuple(tuple(pair) for pair in spec["bounds"])
    parameters = {name: best[name] for name in names if name in best}
    hits = boundary_hits(parameters, names, bounds)
    runs = list(fit.get("runs", []))
    chi2_span = float(fit.get("stability", {}).get("chi2_span", 0.0))
    run_parameter_ranges: dict[str, dict[str, float]] = {}
    for name in names:
        values = [float(run["parameters"][name]) for run in runs if name in run.get("parameters", {})]
        if values:
            run_parameter_ranges[name] = {
                "min": min(values),
                "max": max(values),
                "span": max(values) - min(values),
            }

    baseline_chi2 = float(result["models"][baseline_model]["best"]["chi2"])
    delta_chi2 = float(best["chi2"]) - baseline_chi2
    diagnostic: dict[str, Any] = {
        "model": model,
        "best_parameters": parameters,
        "best_chi2": float(best["chi2"]),
        "delta_chi2_vs_baseline": delta_chi2,
        "boundary_hits": hits,
        "multiseed_chi2_span": chi2_span,
        "run_parameter_ranges": run_parameter_ranges,
        "observed_z_max": float(z_max),
        "token_vazio": [],
        "uncertainties": [],
    }

    if hits:
        diagnostic["uncertainties"].append("BEST_FIT_ON_PARAMETER_BOUNDARY")
        diagnostic["token_vazio"].append(f"TOKEN_VAZIO_{model.upper()}_BOUNDARY_SENSITIVITY")
    if chi2_span > 0.05:
        diagnostic["uncertainties"].append("MULTISTART_CHI2_SPAN_GT_0P05")

    if "z_t" in parameters and "Omega_s0" in parameters:
        z_t = float(parameters["z_t"])
        omega_s0 = float(parameters["Omega_s0"])
        outside = z_t > float(z_max)
        null_nested_runs = sum(
            abs(float(run.get("parameters", {}).get("Omega_s0", 1.0))) <= 1.0e-8 for run in runs
        )
        near_baseline = abs(delta_chi2) <= 1.0e-4
        diagnostic["rll_identifiability"] = {
            "transition_outside_observed_support": outside,
            "best_z_t": z_t,
            "observed_z_max": float(z_max),
            "best_Omega_s0": omega_s0,
            "null_nested_runs": null_nested_runs,
            "delta_chi2_near_zero": near_baseline,
        }
        if near_baseline and (outside or null_nested_runs > 0):
            diagnostic["uncertainties"].append("RLL_SN_ONLY_NULL_NESTED_OR_OUTSIDE_SUPPORT")
            diagnostic["token_vazio"].append("TOKEN_VAZIO_RLL_SN_ONLY_PARAMETER_IDENTIFIABILITY")

    diagnostic["token_vazio"] = sorted(set(diagnostic["token_vazio"]))
    diagnostic["uncertainties"] = sorted(set(diagnostic["uncertainties"]))
    return diagnostic


def pantheon_zmax(path: Path) -> float:
    catalog = pantheon_core.load_catalog(path, z_min=0.01)
    return float(np.max(np.asarray(catalog["z_hd"], dtype=float)))


def dovekie_zmax(path: Path) -> float:
    hd = dovekie_three.load_hd(path)
    return float(np.max(np.asarray(hd["z_hd"], dtype=float)))


def build_receipt(
    pantheon_result_path: Path,
    pantheon_catalog_path: Path,
    dovekie_result_path: Path,
    dovekie_hd_path: Path,
) -> dict[str, Any]:
    pantheon = load_json(pantheon_result_path)
    dovekie = load_json(dovekie_result_path)
    p_zmax = pantheon_zmax(pantheon_catalog_path)
    d_zmax = dovekie_zmax(dovekie_hd_path)

    p_specs = {
        pantheon_three.CPL: pantheon_core.MODEL_SPECS[pantheon_three.CPL],
        pantheon_three.RLL: pantheon_core.MODEL_SPECS[pantheon_three.RLL],
    }
    d_specs = {
        dovekie_three.CPL: dovekie_three.MODEL_SPECS[dovekie_three.CPL],
        dovekie_three.RLL: dovekie_three.MODEL_SPECS[dovekie_three.RLL],
    }

    diagnostics = {
        "Pantheon+SH0ES": {
            model: model_diagnostic(
                pantheon,
                model,
                spec,
                z_max=p_zmax,
                baseline_model=pantheon_three.LCDM,
            )
            for model, spec in p_specs.items()
        },
        "DES-Dovekie": {
            model: model_diagnostic(
                dovekie,
                model,
                spec,
                z_max=d_zmax,
                baseline_model=dovekie_three.LCDM,
            )
            for model, spec in d_specs.items()
        },
    }
    tokens = sorted(
        {
            token
            for dataset in diagnostics.values()
            for model in dataset.values()
            for token in model["token_vazio"]
        }
    )
    uncertainties = sorted(
        {
            uncertainty
            for dataset in diagnostics.values()
            for model in dataset.values()
            for uncertainty in model["uncertainties"]
        }
    )
    return {
        "schema": SCHEMA,
        "state": "VERIFIED_DIAGNOSTIC",
        "claim_allowed": False,
        "publication_ready": False,
        "scientific_boundary": (
            "Optimizer convergence is not parameter identifiability. Boundary hits, flat directions, "
            "or transitions outside observed redshift support remain explicit uncertainties."
        ),
        "diagnostics": diagnostics,
        "token_vazio": tokens,
        "uncertainties": uncertainties,
        "decision": (
            "BLOCK_PARAMETER_INTERPRETATION"
            if any("IDENTIFIABILITY" in token or "BOUNDARY" in token for token in tokens)
            else "NO_IDENTIFIABILITY_BLOCK_DETECTED"
        ),
        "F_ok": [
            "Both SN likelihoods have materialized full matrix information and converged multiseed fits.",
            "Boundary and support diagnostics are computed from stored fit runs rather than inferred from prose.",
        ],
        "F_gap": [
            "SN-only RLL parameters are not identified when the fit collapses to the nested LCDM behavior.",
            "A CPL optimum on a declared bound requires a bound/prior sensitivity run before parameter interpretation.",
        ],
        "F_next": [
            "Run explicit CPL bound-sensitivity and profile-likelihood scans for wa.",
            "Add BAO/CMB/growth data before attempting to identify RLL transition parameters.",
            "Keep model-selection evidence separate from optimizer identifiability diagnostics.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pantheon-result", type=Path, required=True)
    parser.add_argument("--pantheon-catalog", type=Path, required=True)
    parser.add_argument("--dovekie-result", type=Path, required=True)
    parser.add_argument("--dovekie-hd", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        receipt = build_receipt(
            args.pantheon_result,
            args.pantheon_catalog,
            args.dovekie_result,
            args.dovekie_hd,
        )
        atomic_json(args.output, receipt)
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 2
    print(
        f"{receipt['state']} decision={receipt['decision']} "
        f"token_vazio={len(receipt['token_vazio'])} claim_allowed=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
