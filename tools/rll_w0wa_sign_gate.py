#!/usr/bin/env python3
"""Fail-closed sign/falsifiability audit for the canonical RLL logistic sector.

This tool proves the local CPL sign domain implied by the current RLL ansatz.
It does not infer a cosmological posterior and does not declare RLL falsified.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BOUNDS = ROOT / "data/contracts/cosmology_model_family_shadow.v1.json"
DEFAULT_REGISTRY = ROOT / "data/governance/RLL_EXTERNAL_EVIDENCE_REGISTRY_V1.json"
DEFAULT_GATE = ROOT / "data/governance/RLL_W0WA_SIGN_FALSIFIABILITY_GATE_V1.json"
DEFAULT_OUTPUT = ROOT / "results/audit/rll_w0wa_sign_falsifiability.json"


def stable_f0(zt: float, wt: float) -> float:
    if wt <= 0.0:
        raise ValueError("wt must be positive")
    x = max(-700.0, min(700.0, -float(zt) / float(wt)))
    return 1.0 / (1.0 + math.exp(x))


def sector_local_cpl(zt: float, wt: float) -> tuple[float, float]:
    f0 = stable_f0(zt, wt)
    w0 = -f0
    wa = f0 * (1.0 - f0) * (3.0 + 1.0 / float(wt))
    return w0, wa


def total_dark_local_cpl(
    omega_lambda: float,
    omega_s0: float,
    zt: float,
    wt: float,
) -> tuple[float, float]:
    ol = float(omega_lambda)
    os0 = float(omega_s0)
    if ol < 0.0 or os0 < 0.0:
        raise ValueError("sign theorem requires non-negative Omega_Lambda and Omega_s0")
    if wt <= 0.0:
        raise ValueError("sign theorem requires wt>0")
    den = ol + os0
    if den <= 0.0:
        raise ValueError("total dark-sector density must be positive")

    f0 = stable_f0(zt, wt)
    present_pressure_term = ol + os0 * f0
    w0 = -present_pressure_term / den
    wa = (
        os0
        * (1.0 - f0)
        / (den * den)
        * (f0 * den / float(wt) + 3.0 * present_pressure_term)
    )
    return w0, wa


def total_dark_w_numeric(
    a: float,
    omega_lambda: float,
    omega_s0: float,
    zt: float,
    wt: float,
) -> float:
    z = 1.0 / float(a) - 1.0
    arg = max(-700.0, min(700.0, (z - float(zt)) / float(wt)))
    f = 1.0 / (1.0 + math.exp(arg))
    g = f + (1.0 - f) * float(a) ** -3
    rho = float(omega_lambda) + float(omega_s0) * g
    pressure = -(float(omega_lambda) + float(omega_s0) * f)
    return pressure / rho


def finite_difference_wa(
    omega_lambda: float,
    omega_s0: float,
    zt: float,
    wt: float,
    h: float = 1.0e-5,
) -> float:
    plus = total_dark_w_numeric(1.0 + h, omega_lambda, omega_s0, zt, wt)
    minus = total_dark_w_numeric(1.0 - h, omega_lambda, omega_s0, zt, wt)
    return -(plus - minus) / (2.0 * h)


def _bounds(model_contract: dict[str, Any], model_id: str, name: str) -> list[float]:
    model = next(m for m in model_contract["models"] if m["id"] == model_id)
    param = next(p for p in model["parameters"] if p["name"] == name)
    return [float(x) for x in param["bounds"]]


def _sample_points(lo: float, hi: float) -> list[float]:
    return [lo, (lo + hi) / 2.0, hi]


def source_by_id(registry: dict[str, Any], source_id: str) -> dict[str, Any]:
    return next(x for x in registry["sources"] if x["id"] == source_id)


def build_report(
    model_contract: dict[str, Any],
    registry: dict[str, Any],
    gate: dict[str, Any],
) -> dict[str, Any]:
    om_bounds = _bounds(model_contract, "RLL", "Om")
    os_bounds = _bounds(model_contract, "RLL", "Os0")
    zt_bounds = _bounds(model_contract, "RLL", "zt")
    wt_bounds = _bounds(model_contract, "RLL", "wt")

    orad = 9.0e-5
    samples: list[dict[str, float]] = []
    min_w0 = float("inf")
    max_w0 = float("-inf")
    min_wa = float("inf")
    max_wa = float("-inf")
    max_fd_error = 0.0

    for om in _sample_points(*om_bounds):
        for os0 in _sample_points(*os_bounds):
            omega_lambda = 1.0 - orad - om - os0
            if omega_lambda < 0.0:
                continue
            for zt in _sample_points(*zt_bounds):
                for wt in _sample_points(*wt_bounds):
                    w0, wa = total_dark_local_cpl(omega_lambda, os0, zt, wt)
                    wa_fd = finite_difference_wa(omega_lambda, os0, zt, wt)
                    error = abs(wa - wa_fd)
                    min_w0 = min(min_w0, w0)
                    max_w0 = max(max_w0, w0)
                    min_wa = min(min_wa, wa)
                    max_wa = max(max_wa, wa)
                    max_fd_error = max(max_fd_error, error)
                    samples.append({
                        "Om": om,
                        "Os0": os0,
                        "OmegaLambda": omega_lambda,
                        "zt": zt,
                        "wt": wt,
                        "w0_eff": w0,
                        "wa_eff": wa,
                        "wa_finite_difference": wa_fd,
                        "absolute_difference": error,
                    })

    sign_pass = bool(samples) and min_wa >= -1.0e-12
    w0_domain_pass = bool(samples) and min_w0 >= -1.0 - 1.0e-12 and max_w0 < 0.0
    derivative_crosscheck_pass = max_fd_error < 1.0e-7

    fs_bao = source_by_id(registry, "DESI_DR1_FS_DR2_BAO_2026")
    lya = source_by_id(registry, "DESI_DR2_LYA_FULLSHAPE_2026")
    review = source_by_id(registry, "TURYSHEV_DESI_DR2_REVIEW_2026")

    return {
        "schema": "rll.w0wa_sign_falsifiability.report.v1",
        "claim_allowed": False,
        "falsified": False,
        "status": (
            "STRUCTURAL_SIGN_TENSION_POSTERIOR_OVERLAP_REQUIRED"
            if sign_pass and derivative_crosscheck_pass
            else "MATH_GATE_FAILED"
        ),
        "canonical_sign_theorem": {
            "pass": sign_pass,
            "wa_domain": "wa_eff >= 0",
            "w0_domain": "-1 <= w0_eff < 0 under canonical positive bounds",
            "w0_domain_pass": w0_domain_pass,
            "sample_count": len(samples),
            "min_w0_eff": min_w0,
            "max_w0_eff": max_w0,
            "min_wa_eff": min_wa,
            "max_wa_eff": max_wa,
            "max_analytic_vs_finite_difference_error": max_fd_error,
            "derivative_crosscheck_pass": derivative_crosscheck_pass,
            "sector_formula": "wa_s=f0(1-f0)(3+1/wt)",
            "total_dark_formula": gate["exact_results"]["total_dark_wa"],
        },
        "external_context": {
            "joint_DR1_fullshape_DR2_BAO_2026": fs_bao["published_context"],
            "latest_DR2_Lya_fullshape_2026": lya["published_context"],
            "DESI_DR2_review_systematics": review["published_context"],
        },
        "interpretation": {
            "negative_wa_central_values_exist": True,
            "negative_wa_is_direct_observable": False,
            "central_value_sign_mismatch_is_falsification": False,
            "coarse_1d_gate": "P(wa>=0 | D)",
            "decisive_2d_gate": "posterior overlap/HPD distance to sampled or analytic RLL-accessible (w0_eff,wa_eff) domain",
            "required_decisive_test": gate["observational_gate"]["required_next_test"],
            "falsification_condition": gate["observational_gate"]["falsification_condition"],
        },
        "license_boundary": gate["license_boundary"],
        "invariants": gate["invariants"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bounds", type=Path, default=DEFAULT_BOUNDS)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--gate", type=Path, default=DEFAULT_GATE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--require-math-pass", action="store_true")
    args = parser.parse_args()

    def read(path: Path) -> dict[str, Any]:
        p = path if path.is_absolute() else ROOT / path
        return json.loads(p.read_text(encoding="utf-8"))

    report = build_report(read(args.bounds), read(args.registry), read(args.gate))
    out = args.output if args.output.is_absolute() else ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True))

    math_ok = (
        report["canonical_sign_theorem"]["pass"]
        and report["canonical_sign_theorem"]["w0_domain_pass"]
        and report["canonical_sign_theorem"]["derivative_crosscheck_pass"]
    )
    return 0 if (not args.require_math_pass or math_ok) else 2


if __name__ == "__main__":
    raise SystemExit(main())
