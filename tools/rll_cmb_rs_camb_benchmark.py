#!/usr/bin/env python3
from __future__ import annotations

"""Benchmark bounded RLL recombination helpers against CAMB.

The benchmark deliberately decomposes disagreement into two layers:

1. z_star fitting error: RLL Hu-Sugiyama z_star versus CAMB zstar.
2. sound-horizon integration error:
   a) RLL integral evaluated at the RLL fitted z_star;
   b) the same RLL integral evaluated at CAMB zstar.

This distinguishes an approximate decoupling-redshift error from an integration
or background mismatch. It does not validate an RLL perturbation model and does
not promote any cosmological claim.
"""

import argparse
import importlib.metadata
import json
import math
import os
import tempfile
import traceback
from pathlib import Path
from typing import Any, Sequence

from rll.cosmology_radiation import NEFF_STANDARD, TCMB_REF_K, omega_r_from_h0
from rll.cosmology_recombination import (
    flat_lcdm_e_of_a,
    sound_horizon_mpc,
    z_star_hu_sugiyama,
)

SCHEMA = "rll.cmb_rs_camb_benchmark.v1"
ZSTAR_REL_TOL = 1.0e-2
RS_FIT_ZSTAR_REL_TOL = 1.0e-2
RS_CAMB_ZSTAR_REL_TOL = 5.0e-3


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".part",
        delete=False,
    ) as handle:
        tmp = Path(handle.name)
        json.dump(payload, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    try:
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)


def relative_error(a: float, b: float, floor: float = 1.0e-30) -> float:
    return abs(float(a) - float(b)) / max(abs(float(a)), abs(float(b)), floor)


def benchmark_cases() -> list[dict[str, float | str]]:
    return [
        {
            "id": "baseline",
            "H0": 67.4,
            "Omega_m": 0.315,
            "omega_b_h2": 0.02237,
            "Tcmb_K": TCMB_REF_K,
            "Neff": NEFF_STANDARD,
        },
        {
            "id": "lower_background",
            "H0": 64.0,
            "Omega_m": 0.280,
            "omega_b_h2": 0.02150,
            "Tcmb_K": TCMB_REF_K,
            "Neff": NEFF_STANDARD,
        },
        {
            "id": "upper_background",
            "H0": 72.0,
            "Omega_m": 0.360,
            "omega_b_h2": 0.02350,
            "Tcmb_K": TCMB_REF_K,
            "Neff": NEFF_STANDARD,
        },
    ]


def run_camb_reference(case: dict[str, float | str]) -> dict[str, float | str]:
    import camb

    h0 = float(case["H0"])
    h = h0 / 100.0
    omega_m = float(case["Omega_m"])
    omega_b_h2 = float(case["omega_b_h2"])
    omega_m_h2 = omega_m * h * h
    omega_c_h2 = omega_m_h2 - omega_b_h2
    if omega_c_h2 <= 0.0:
        raise ValueError(f"{case['id']}: omega_c_h2 must be positive")

    pars = camb.CAMBparams()
    pars.set_cosmology(
        H0=h0,
        ombh2=omega_b_h2,
        omch2=omega_c_h2,
        mnu=0.0,
        omk=0.0,
        tau=0.054,
        nnu=float(case["Neff"]),
        TCMB=float(case["Tcmb_K"]),
    )
    pars.InitPower.set_params(As=2.1e-9, ns=0.965)
    results = camb.get_background(pars)
    derived = results.get_derived_params()
    required = {"zstar", "rstar"}
    missing = sorted(required - set(derived))
    if missing:
        raise ValueError(
            f"CAMB derived parameters missing {missing}; available={sorted(derived)}"
        )
    return {
        "version": importlib.metadata.version("camb"),
        "zstar": float(derived["zstar"]),
        "rstar_Mpc": float(derived["rstar"]),
    }


def compare_case(case: dict[str, float | str]) -> dict[str, Any]:
    h0 = float(case["H0"])
    h = h0 / 100.0
    omega_m = float(case["Omega_m"])
    omega_b_h2 = float(case["omega_b_h2"])
    tcmb = float(case["Tcmb_K"])
    neff = float(case["Neff"])
    omega_m_h2 = omega_m * h * h

    camb_ref = run_camb_reference(case)
    zstar_rll = z_star_hu_sugiyama(omega_b_h2, omega_m_h2)
    omega_r = omega_r_from_h0(h0, tcmb_k=tcmb, neff=neff)
    e_of_a = flat_lcdm_e_of_a(omega_m=omega_m, omega_r=omega_r)

    rs_at_rll_zstar = sound_horizon_mpc(
        z_star=zstar_rll,
        h0_km_s_mpc=h0,
        e_of_a=e_of_a,
        omega_b_h2=omega_b_h2,
        tcmb_k=tcmb,
        intervals=8192,
    )
    rs_at_camb_zstar = sound_horizon_mpc(
        z_star=float(camb_ref["zstar"]),
        h0_km_s_mpc=h0,
        e_of_a=e_of_a,
        omega_b_h2=omega_b_h2,
        tcmb_k=tcmb,
        intervals=8192,
    )

    z_error = relative_error(zstar_rll, float(camb_ref["zstar"]))
    rs_fit_error = relative_error(rs_at_rll_zstar, float(camb_ref["rstar_Mpc"]))
    rs_camb_z_error = relative_error(rs_at_camb_zstar, float(camb_ref["rstar_Mpc"]))

    metrics = {
        "zstar": {
            "RLL": zstar_rll,
            "CAMB": float(camb_ref["zstar"]),
            "relative_error": z_error,
            "tolerance": ZSTAR_REL_TOL,
            "pass": z_error <= ZSTAR_REL_TOL,
        },
        "rstar_at_rll_zstar_Mpc": {
            "RLL": rs_at_rll_zstar,
            "CAMB": float(camb_ref["rstar_Mpc"]),
            "relative_error": rs_fit_error,
            "tolerance": RS_FIT_ZSTAR_REL_TOL,
            "pass": rs_fit_error <= RS_FIT_ZSTAR_REL_TOL,
        },
        "rstar_at_camb_zstar_Mpc": {
            "RLL": rs_at_camb_zstar,
            "CAMB": float(camb_ref["rstar_Mpc"]),
            "relative_error": rs_camb_z_error,
            "tolerance": RS_CAMB_ZSTAR_REL_TOL,
            "pass": rs_camb_z_error <= RS_CAMB_ZSTAR_REL_TOL,
        },
    }
    return {
        "case": case,
        "CAMB": camb_ref,
        "RLL": {
            "omega_r": omega_r,
            "zstar_fit": zstar_rll,
            "rstar_at_rll_zstar_Mpc": rs_at_rll_zstar,
            "rstar_at_camb_zstar_Mpc": rs_at_camb_zstar,
        },
        "metrics": metrics,
        "pass": all(row["pass"] for row in metrics.values()),
    }


def build(output: Path) -> dict[str, Any]:
    cases = [compare_case(case) for case in benchmark_cases()]
    passed = all(case["pass"] for case in cases)
    payload = {
        "schema": SCHEMA,
        "state": (
            "VERIFIED_RLL_RS_CAMB_REFERENCE_BENCHMARK"
            if passed
            else "TOKEN_VAZIO_CMB_RS_CAMB_MISMATCH"
        ),
        "claim_allowed": False,
        "publication_ready": False,
        "scope": {
            "background": "flat LCDM reference only",
            "massive_neutrinos": "disabled",
            "Tcmb_K": TCMB_REF_K,
            "Neff": NEFF_STANDARD,
            "cases": [case["case"]["id"] for case in cases],
            "tolerances": {
                "zstar_relative": ZSTAR_REL_TOL,
                "rstar_at_rll_zstar_relative": RS_FIT_ZSTAR_REL_TOL,
                "rstar_at_camb_zstar_relative": RS_CAMB_ZSTAR_REL_TOL,
            },
        },
        "cases": cases,
        "scientific_boundary": (
            "This benchmark validates the bounded standard-background RLL "
            "recombination helper against CAMB for zstar/rstar only. It does "
            "not validate RLL perturbations, growth, an RLL Boltzmann backend, "
            "or model selection."
        ),
        "reduces_token": "TOKEN_VAZIO_CMB_RS_CAMB_BENCHMARK",
        "resolves_gap": "CMB-BENCH-001" if passed else None,
        "F_ok": [
            "Three pinned background cosmologies are compared.",
            "zstar fitting and sound-horizon integration errors are separated.",
            "r_d(z_drag) is not substituted for r_s(zstar).",
        ],
        "F_gap": (
            [
                "TOKEN_VAZIO_RLL_PERTURBATION_CLOSURE_RELATIONS",
                "TOKEN_VAZIO_RLL_CLASS_CAMB_IMPLEMENTATION",
                "TOKEN_VAZIO_GROWTH_DZ_IMPLEMENTATION",
            ]
            if passed
            else ["TOKEN_VAZIO_CMB_RS_CAMB_MISMATCH"]
        ),
        "F_next": (
            [
                "Promote the CMB helper gaps to evidence-backed bounded status.",
                "Make GROWTH-THEORY-001 the next scientific bottleneck.",
            ]
            if passed
            else [
                "Use the decomposed zstar/integration residuals to localize the mismatch.",
                "Do not modify downstream likelihoods before this benchmark is resolved.",
            ]
        ),
    }
    atomic_json(output, payload)
    return payload


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        payload = build(args.output)
    except Exception as exc:
        traceback.print_exc()
        print(f"ERROR: {type(exc).__name__}: {exc}")
        return 2

    summary = {
        row["case"]["id"]: {
            name: {
                "relative_error": metric["relative_error"],
                "pass": metric["pass"],
            }
            for name, metric in row["metrics"].items()
        }
        for row in payload["cases"]
    }
    print(
        json.dumps(
            {
                "state": payload["state"],
                "claim_allowed": False,
                "cases": summary,
            },
            sort_keys=True,
        )
    )
    return 0 if payload["state"] == "VERIFIED_RLL_RS_CAMB_REFERENCE_BENCHMARK" else 3


if __name__ == "__main__":
    raise SystemExit(main())
