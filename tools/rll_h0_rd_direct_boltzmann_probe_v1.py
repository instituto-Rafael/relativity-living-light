#!/usr/bin/env python3
from __future__ import annotations

"""Evaluate full CAMB r_drag on the selected H0/r_d matrix fit vectors.

This is the next evidence layer after the two-vector CLASS/CAMB baseline check.
It evaluates every standard-model selected vector from the current six-cell
ablation receipt with a direct CAMB background calculation. RLL vectors are
*not* coerced into CDM: they remain explicitly blocked until the early-time
mapping of the RLL effective component is versioned.

This probe does not re-optimize with CAMB inside the objective. Therefore it
reduces, but cannot resolve, TOKEN_VAZIO_H0_RD_FULL_BOLTZMANN_INFERENCE_INTEGRATION.
"""

import argparse
import importlib.metadata
import json
import math
import os
import tempfile
from pathlib import Path
from typing import Any, Callable, Sequence

SCHEMA = "rll.h0_rd_direct_boltzmann_probe.v1"
MODEL_LCDM = "LCDM_joint_real"
MODEL_WCDM = "wCDM_joint_real"
MODEL_CPL = "CPL_w0waCDM_joint_real"
MODEL_RLL = "RLL_joint_real"
STANDARD_MODELS = (MODEL_LCDM, MODEL_WCDM, MODEL_CPL)


def relative_error(a: float, b: float) -> float:
    return abs(float(a) - float(b)) / max(abs(float(a)), abs(float(b)), 1.0e-30)


def camb_rdrag(parameters: dict[str, float], model: str) -> float:
    import camb

    h0 = float(parameters["H0"])
    om = float(parameters["Om"])
    obh2 = float(parameters["Ob_h2"])
    h = h0 / 100.0
    omch2 = om * h * h - obh2
    if not (math.isfinite(omch2) and omch2 > 0.0):
        raise ValueError(f"nonphysical omch2={omch2} from H0={h0}, Om={om}, Ob_h2={obh2}")

    pars = camb.CAMBparams()
    pars.set_cosmology(H0=h0, ombh2=obh2, omch2=omch2, mnu=0.0, omk=0.0)
    if model == MODEL_WCDM:
        pars.set_dark_energy(w=float(parameters["w"]), wa=0.0, dark_energy_model="ppf")
    elif model == MODEL_CPL:
        pars.set_dark_energy(
            w=float(parameters["w0"]),
            wa=float(parameters["wa"]),
            dark_energy_model="ppf",
        )
    elif model != MODEL_LCDM:
        raise ValueError(f"unsupported standard-model mapping: {model}")

    background = camb.get_background(pars)
    derived = background.get_derived_params()
    if "rdrag" not in derived:
        raise ValueError(f"CAMB derived parameters missing rdrag: {sorted(derived)}")
    value = float(derived["rdrag"])
    if not (math.isfinite(value) and value > 0.0):
        raise ValueError(f"invalid CAMB rdrag={value}")
    return value


def probe(ablation: dict[str, Any], evaluator: Callable[[dict[str, float], str], float] = camb_rdrag) -> dict[str, Any]:
    cells = ablation.get("cells")
    if not isinstance(cells, list) or len(cells) != 6:
        raise ValueError("ablation receipt must contain exactly six cells")

    rows: list[dict[str, Any]] = []
    blocked_rll: list[dict[str, Any]] = []
    for cell in cells:
        run_id = str(cell["run_id"])
        models = cell.get("models") or {}
        for model in STANDARD_MODELS:
            row = models.get(model)
            if not isinstance(row, dict):
                raise ValueError(f"{run_id}: missing {model}")
            parameters = {str(k): float(v) for k, v in (row.get("parameters") or {}).items()}
            direct = float(evaluator(parameters, model))
            former = float(row["rd_mpc"])
            rows.append({
                "run_id": run_id,
                "H0_policy": cell.get("H0_policy"),
                "rd_policy": cell.get("rd_policy"),
                "model": model,
                "parameters": parameters,
                "former_inference_rd_mpc": former,
                "direct_camb_rdrag_mpc": direct,
                "absolute_delta_mpc": direct - former,
                "relative_error_former_vs_direct": relative_error(former, direct),
                "best_attempt_success": bool(row.get("best_attempt_success")),
            })

        rll = models.get(MODEL_RLL)
        if not isinstance(rll, dict):
            raise ValueError(f"{run_id}: missing {MODEL_RLL}")
        blocked_rll.append({
            "run_id": run_id,
            "model": MODEL_RLL,
            "parameters": rll.get("parameters"),
            "state": "BLOCKED_RLL_EARLY_TIME_MAPPING",
            "reason": (
                "The versioned RLL background makes the effective component matter-like at high z, "
                "but no validated mapping says that Omega_s may be injected into CAMB as cold dark matter. "
                "Doing so here would invent pre-recombination microphysics."
            ),
        })

    if len(rows) != 18 or len(blocked_rll) != 6:
        raise AssertionError("expected 18 standard direct evaluations and 6 RLL mapping blocks")
    worst = max(rows, key=lambda row: row["relative_error_former_vs_direct"])
    return {
        "schema": SCHEMA,
        "state": "STANDARD_18_OF_24_DIRECT_CAMB_RDRAG_EVALUATED_RLL_6_BLOCKED",
        "claim_allowed": False,
        "publication_ready": False,
        "token": "TOKEN_VAZIO_H0_RD_FULL_BOLTZMANN_INFERENCE_INTEGRATION",
        "input_ablation_state": ablation.get("state"),
        "standard_model_direct_evaluations": rows,
        "rll_blocked_vectors": blocked_rll,
        "summary": {
            "declared_fit_vectors": 24,
            "direct_camb_evaluated": 18,
            "rll_mapping_blocked": 6,
            "max_relative_error_former_vs_direct": float(worst["relative_error_former_vs_direct"]),
            "worst_case": {
                "run_id": worst["run_id"],
                "model": worst["model"],
                "former_inference_rd_mpc": worst["former_inference_rd_mpc"],
                "direct_camb_rdrag_mpc": worst["direct_camb_rdrag_mpc"],
            },
        },
        "backend": {
            "engine": "CAMB",
            "version": importlib.metadata.version("camb") if evaluator is camb_rdrag else "INJECTED_TEST_EVALUATOR",
            "neutrino_policy": "mnu=0.0, matching the existing standard baseline crosscheck",
            "dark_energy_mapping": {
                MODEL_LCDM: "Lambda",
                MODEL_WCDM: "CAMB PPF with fitted w and wa=0",
                MODEL_CPL: "CAMB PPF with fitted w0,wa",
                MODEL_RLL: "BLOCKED; no substitution into CDM or standard fluid",
            },
        },
        "resolved_token": None,
        "reduces_token": "TOKEN_VAZIO_H0_RD_FULL_BOLTZMANN_INFERENCE_INTEGRATION",
        "remaining_close_conditions": [
            "make the formal derived-r_d objective backend-selectable",
            "rerun optimization with direct CAMB/CLASS or a prevalidated cache/interpolator rather than probing only selected vectors",
            "version and test the RLL pre-recombination/early-time mapping before evaluating RLL r_drag in a standard Boltzmann engine",
            "all 24 selected best fits must pass the unchanged convergence/fairness policy under the integrated backend",
        ],
        "scientific_boundary": (
            "Direct full-Boltzmann evaluation at selected standard-model vectors measures the numerical r_drag gap. "
            "It is not yet full-Boltzmann inference integration and does not justify an RLL early-time mapping."
        ),
    }


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


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ablation", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    ablation = json.loads(args.ablation.read_text(encoding="utf-8"))
    payload = probe(ablation)
    atomic_json(args.output, payload)
    print(json.dumps({
        "state": payload["state"],
        **payload["summary"],
        "claim_allowed": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
