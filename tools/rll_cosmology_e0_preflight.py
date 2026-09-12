#!/usr/bin/env python3
"""Fail-closed E0 preflight for the RLL joint cosmology likelihood.

This tool does not refit data and does not alter committed results.  It audits
whether the current joint-likelihood parameterization is safe to promote to
scientific model-selection claims.

SOURCE != ARTEFACT != EXECUTION != EVIDENCE != CLAIM.
"""

from __future__ import annotations

import argparse
import inspect
import json
import math
from pathlib import Path
from typing import Any

from data.pipelines.structure_d import joint_real_likelihood as joint

BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = BASE_DIR / "results" / "audit" / "rll_cosmology_e0_preflight.json"


def _parameter_bound(model: str, name: str) -> tuple[float, float] | None:
    names = joint.MODEL_PARAM_NAMES[model]
    if name not in names:
        return None
    idx = names.index(name)
    lo, hi = joint.MODEL_BOUNDS[model][idx]
    return float(lo), float(hi)


def _e0_interval(model: str) -> tuple[float, float] | None:
    """Return the E(0)^2 interval admitted by the current optimizer bounds.

    For LCDM/wCDM/CPL at z=0, E^2(0)=Om+Or+OL.
    For the current RLL ansatz the superposition shape is exactly one at z=0,
    therefore E^2(0)=Om+Or+OL+Os0.
    """

    om = _parameter_bound(model, "Om")
    ol = _parameter_bound(model, "OL")
    if om is None or ol is None:
        return None
    lo = om[0] + float(joint.ORAD) + ol[0]
    hi = om[1] + float(joint.ORAD) + ol[1]
    os0 = _parameter_bound(model, "Os0")
    if os0 is not None:
        lo += os0[0]
        hi += os0[1]
    return float(lo), float(hi)


def _closure_check(model: str) -> dict[str, Any]:
    names = joint.MODEL_PARAM_NAMES[model]
    interval = _e0_interval(model)
    free_ol = "OL" in names
    curvature_free = "Ok" in names
    if interval is None:
        normalized_by_construction = not free_ol
        return {
            "model": model,
            "free_OL": free_ol,
            "free_Ok": curvature_free,
            "e0_squared_interval_from_bounds": None,
            "normalized_by_construction": normalized_by_construction,
            "pass": normalized_by_construction,
            "reason": (
                "No independent OL bound detected; normalization must be verified numerically."
                if normalized_by_construction
                else "Unable to establish the z=0 closure contract."
            ),
        }

    lo, hi = interval
    singleton_one = math.isclose(lo, 1.0, rel_tol=0.0, abs_tol=1.0e-12) and math.isclose(
        hi, 1.0, rel_tol=0.0, abs_tol=1.0e-12
    )
    return {
        "model": model,
        "free_OL": free_ol,
        "free_Ok": curvature_free,
        "e0_squared_interval_from_bounds": [lo, hi],
        "normalized_by_construction": singleton_one,
        "pass": singleton_one,
        "reason": (
            "E(0)^2 is fixed to unity by the fitted parameterization."
            if singleton_one
            else "Optimizer bounds admit E(0)^2 != 1 while H(z)=H0*E(z); physical H0 is therefore not identified by construction."
        ),
    }


def _growth_check() -> dict[str, Any]:
    source = inspect.getsource(joint.fsigma8_prediction)
    proxy_markers = ("omega_m_z_from_e2", "** 0.55")
    is_proxy = any(marker in source for marker in proxy_markers)
    return {
        "function": "joint_real_likelihood.fsigma8_prediction",
        "mode": "growth_index_proxy" if is_proxy else "non_proxy_or_unknown",
        "uses_D_of_z": "linear_growth_dplus" in source or "fsigma8_linear" in source,
        "pass": not is_proxy,
        "reason": (
            "Current likelihood uses sigma8_0 * Omega_m(z)^0.55 without D(z); treat fσ8 as a proxy, not a precision growth likelihood."
            if is_proxy
            else "No current growth-index proxy marker detected; implementation still requires benchmark validation."
        ),
    }


def _cmb_check() -> dict[str, Any]:
    source = inspect.getsource(joint.cmb_shift_prediction)
    uses_rd_for_acoustic_scale = "rd_drag_mpc" in source and "acoustic_scale" in source
    return {
        "function": "joint_real_likelihood.cmb_shift_prediction",
        "acoustic_scale_uses_rd_drag": uses_rd_for_acoustic_scale,
        "requires_rs_at_recombination": True,
        "pass": not uses_rd_for_acoustic_scale,
        "reason": (
            "l_A currently substitutes the drag horizon r_d for the recombination sound horizon r_s(z*); compressed-CMB model-selection claims remain blocked."
            if uses_rd_for_acoustic_scale
            else "No r_d substitution detected; verify the implemented r_s(z*) calculation and covariance contract before promotion."
        ),
    }


def _h0_check() -> dict[str, Any]:
    bounds: dict[str, list[float] | None] = {}
    for model in joint.MODEL_ORDER:
        bound = _parameter_bound(model, "H0")
        bounds[model] = list(bound) if bound is not None else None
    closure_gap = any(not _closure_check(model)["pass"] for model in joint.MODEL_ORDER)
    return {
        "optimizer_bounds": bounds,
        "physical_identification_pass": not closure_gap,
        "reason": (
            "Do not interpret an optimizer-boundary H0 as physical H0 while E(0)=1 is not enforced."
            if closure_gap
            else "E(0) normalization gate passes; H0 bound sensitivity can be tested independently."
        ),
    }


def build_report() -> dict[str, Any]:
    closure = [_closure_check(model) for model in joint.MODEL_ORDER]
    growth = _growth_check()
    cmb = _cmb_check()
    h0 = _h0_check()

    closure_ready = all(item["pass"] for item in closure)
    ready = closure_ready and growth["pass"] and cmb["pass"]

    return {
        "schema": "rll.cosmology_e0_preflight.v1",
        "status": "READY_FOR_INFERENCE_PREFLIGHT" if ready else "BLOCKED_FAIL_CLOSED",
        "source_module": "data/pipelines/structure_d/joint_real_likelihood.py",
        "checks": {
            "z0_normalization_and_closure": closure,
            "growth_likelihood": growth,
            "cmb_acoustic_scale": cmb,
            "h0_identification": h0,
        },
        "claim_allowed": bool(ready),
        "model_selection_claim_allowed": bool(ready),
        "historical_results_mutated": False,
        "recommended_actions": [
            "Reparameterize the flat comparison so Omega_DE is derived by closure (or add Omega_k consistently to every model and curved distance branches).",
            "Separate the current fσ8 growth-index proxy from claim-bearing likelihoods until D(z) / perturbation treatment is benchmarked.",
            "Replace r_d in l_A with a validated r_s(z*) implementation before using the compressed CMB term for model selection.",
        ],
        "invariants": [
            "SOURCE != ARTEFACT != EXECUTION != EVIDENCE != CLAIM",
            "TOKEN_VAZIO != 0",
            "IMPLEMENTED_UNTESTED != PASS",
            "E(0)=1 before interpreting fitted H0 as the present-day Hubble constant",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--require-ready",
        action="store_true",
        help="Return non-zero unless all E0 scientific-promotion gates pass.",
    )
    args = parser.parse_args()

    report = build_report()
    output = args.output
    if not output.is_absolute():
        output = BASE_DIR / output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))

    if args.require_ready and not report["claim_allowed"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
