#!/usr/bin/env python3
"""Fail-closed preflight for the additive flat-closure successor."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

from data.pipelines.structure_d import joint_real_likelihood_flat as flat
from tools import rll_cosmology_e0_preflight as legacy_e0

BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = BASE_DIR / "results" / "audit" / "rll_cosmology_flat_closure_preflight.json"


def _sample_vector(model: str, fraction: float) -> np.ndarray:
    bounds = flat.FLAT_MODEL_BOUNDS[model]
    return np.asarray([lo + fraction * (hi - lo) for lo, hi in bounds], dtype=float)


def _closure_check(model: str) -> dict:
    samples = []
    for fraction in (0.0, 0.5, 1.0):
        vector = _sample_vector(model, fraction)
        e0_sq = flat.e0_squared(model, vector)
        ol = flat.derived_omega_lambda(model, vector)
        samples.append({
            "fraction": fraction,
            "Omega_Lambda": ol,
            "E0_squared": e0_sq,
            "pass": bool(ol > 0.0 and math.isclose(e0_sq, 1.0, rel_tol=0.0, abs_tol=1.0e-12)),
        })
    return {
        "model": model,
        "free_OL": False,
        "derived_OL": True,
        "samples": samples,
        "pass": all(item["pass"] for item in samples),
    }


def build_report() -> dict:
    closure = [_closure_check(model) for model in flat.MODEL_ORDER]
    growth = legacy_e0._growth_check()
    cmb = legacy_e0._cmb_check()
    closure_ready = all(item["pass"] for item in closure)
    ready = closure_ready and growth["pass"] and cmb["pass"]

    return {
        "schema": "rll.cosmology_flat_closure_preflight.v1",
        "status": "READY_FOR_INFERENCE_PREFLIGHT" if ready else (
            "CLOSURE_READY_OTHER_GATES_BLOCKED" if closure_ready else "BLOCKED_FAIL_CLOSED"
        ),
        "checks": {
            "z0_normalization_and_flat_closure": closure,
            "growth_likelihood": growth,
            "cmb_acoustic_scale": cmb,
        },
        "closure_claim_allowed": bool(closure_ready),
        "claim_allowed": bool(ready),
        "model_selection_claim_allowed": bool(ready),
        "historical_results_mutated": False,
        "open_tokens": [
            "TOKEN_VAZIO_IMPLEMENTATION: validated D(z)/perturbation growth backend",
            "TOKEN_VAZIO_IMPLEMENTATION: validated r_s(z_star) compressed-CMB implementation",
            "TOKEN_VAZIO_EXECUTION: robust posterior/model-selection rerun on successor",
        ],
        "invariants": [
            "SOURCE != ARTEFACT != EXECUTION != EVIDENCE != CLAIM",
            "TOKEN_VAZIO != 0",
            "IMPLEMENTED_UNTESTED != PASS",
            "CLOSURE_PASS != MODEL_SELECTION_PASS",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--require-ready", action="store_true")
    args = parser.parse_args()

    report = build_report()
    output = args.output if args.output.is_absolute() else BASE_DIR / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))

    if args.require_ready and not report["claim_allowed"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
