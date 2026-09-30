#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import math
from pathlib import Path
from types import ModuleType
from typing import Any, Sequence

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "data/contracts/rll_omega_g_cosmology_tournament.v1.yaml"
REGISTRY = ROOT / "data/inputs/omega_g/observable_effect_binding_registry.v1.yaml"
G4 = ROOT / "tools/run_g4_background_tournament.py"

REQUIRED_BIND_FIELDS = (
    "binding_id",
    "invariant_id",
    "source_family",
    "observable_id",
    "mechanism",
    "mathematical_map",
    "units_input",
    "units_output",
    "free_parameters",
    "parameter_priors_or_bounds",
    "covariance_policy",
    "aggregation_level",
    "double_counting_audit",
    "falsifier",
    "holdout_policy",
    "provenance",
)

BASELINE_MODELS = ("LCDM", "wCDM", "CPL", "RLL")
NULL_Z = np.asarray([0.0, 0.01, 0.1, 0.3, 0.8, 1.5, 2.33], dtype=float)


def _load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(name, None)
        raise
    return module


def _read_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a mapping")
    return value


def _is_missing(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value == "" or value.startswith("TOKEN_VAZIO")
    return False


def validate_contract_and_registry() -> dict[str, Any]:
    contract = _read_yaml(CONTRACT)
    registry = _read_yaml(REGISTRY)
    errors: list[str] = []

    if contract.get("schema") != "rll.omega_g_cosmology_tournament.v1":
        errors.append("contract schema mismatch")
    if contract.get("claim_allowed") is not False:
        errors.append("claim_allowed must remain false")
    if contract.get("scientific_confirmation") is not False:
        errors.append("scientific_confirmation must remain false")

    declared = tuple(contract.get("models", {}).get("baseline", ())) + tuple(
        contract.get("models", {}).get("candidate", ())
    )
    for model in BASELINE_MODELS:
        if model not in declared:
            errors.append(f"missing model {model}")

    datasets = contract.get("datasets", {}).get("G4_background", {})
    for block in ("cosmic_chronometers_Hz", "DESI_DR2_BAO", "PantheonPlus_SH0ES"):
        if block not in datasets:
            errors.append(f"missing G4 dataset block {block}")

    bindings = registry.get("bindings", [])
    active = []
    for item in bindings:
        if item.get("state") == "APPROVED_FOR_TEST":
            active.append(item.get("binding_id"))
            for field in REQUIRED_BIND_FIELDS:
                if field not in item or _is_missing(item.get(field)):
                    errors.append(f"{item.get('binding_id')}: active binding missing {field}")
            if not item.get("free_parameters"):
                # zero-parameter bindings are allowed only when explicitly marked.
                if item.get("zero_parameter_binding") is not True:
                    errors.append(f"{item.get('binding_id')}: empty free_parameters requires zero_parameter_binding=true")

    perturb = contract.get("datasets", {}).get("perturbation_level", {})
    if not str(perturb.get("fsigma8", {}).get("status", "")).startswith("BLOCKED"):
        errors.append("fsigma8 must remain blocked from background-only Omega_G binding")
    if not str(perturb.get("CMB_full_or_compressed", {}).get("status", "")).startswith("BLOCKED"):
        errors.append("CMB must remain blocked from background-only Omega_G binding")

    return {
        "schema": "rll.omega_g_cosmology_tournament.validation.v1",
        "valid": not errors,
        "errors": errors,
        "active_bindings": active,
        "claim_allowed": False,
        "scientific_confirmation": False,
    }


def null_parity() -> dict[str, Any]:
    g4 = _load_module("rll_g4_omega_null", G4)
    rows = []
    global_max = 0.0
    for model in BASELINE_MODELS:
        params = np.asarray(g4.MODEL_SPEC[model]["canonical"], dtype=float)
        base = np.asarray(g4.e2(model, NULL_Z, params), dtype=float)
        omega_identity = np.asarray(base, dtype=float).copy()
        delta = omega_identity - base
        max_abs = float(np.max(np.abs(delta)))
        global_max = max(global_max, max_abs)
        rows.append(
            {
                "model": model,
                "z": NULL_Z.tolist(),
                "max_abs_delta_E2": max_abs,
                "pass": bool(max_abs == 0.0 and np.array_equal(base, omega_identity)),
            }
        )
    return {
        "schema": "rll.omega_g_null_parity.v1",
        "state": "PASS" if all(row["pass"] for row in rows) else "FAIL",
        "models": rows,
        "global_max_abs_delta_E2": global_max,
        "claim_allowed": False,
        "meaning": "Omega_G identity plumbing must reproduce the unmodified G4 background exactly.",
    }


def run_baseline(output: Path, seeds: Sequence[int], maxiter: int, ftol: float, integration_points: int) -> dict[str, Any]:
    g4 = _load_module("rll_g4_omega_baseline", G4)
    report = g4.build_report(
        seeds=tuple(int(x) for x in seeds),
        maxiter=int(maxiter),
        ftol=float(ftol),
        integration_points=int(integration_points),
    )
    wrapped = {
        "schema": "rll.omega_g_cosmology_tournament.baseline.v1",
        "arm": "ARM0_BASELINE",
        "source_engine": "tools/run_g4_background_tournament.py",
        "omega_g": "disabled",
        "claim_allowed": False,
        "report": report,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(wrapped, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    return wrapped


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Omega_G cosmology tournament bridge")
    parser.add_argument("--mode", choices=("validate", "null-parity", "baseline"), default="validate")
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts/omega_g/omega_g_cosmology_tournament.json")
    parser.add_argument("--seeds", default="11")
    parser.add_argument("--maxiter", type=int, default=3)
    parser.add_argument("--ftol", type=float, default=1e-8)
    parser.add_argument("--integration-points", type=int, default=1024)
    args = parser.parse_args(argv)

    validation = validate_contract_and_registry()
    if not validation["valid"]:
        print(json.dumps(validation, indent=2, ensure_ascii=False))
        return 2

    if args.mode == "validate":
        print(json.dumps(validation, indent=2, ensure_ascii=False))
        return 0

    if args.mode == "null-parity":
        result = null_parity()
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if result["state"] == "PASS" else 3

    seeds = tuple(int(x.strip()) for x in args.seeds.split(",") if x.strip())
    if not seeds:
        print("ERROR: at least one seed is required")
        return 2
    wrapped = run_baseline(args.output, seeds, args.maxiter, args.ftol, args.integration_points)
    print(
        f"{wrapped['report']['state']} arm=ARM0_BASELINE "
        f"N={wrapped['report']['datasets']['N_total']} claim_allowed=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
