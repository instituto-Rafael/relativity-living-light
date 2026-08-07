#!/usr/bin/env python3
from __future__ import annotations

"""Numerically cross-check standard LCDM/CPL baselines in CLASS and CAMB.

This script intentionally does not implement RLL perturbations. Its only job is
to establish that the two independent Boltzmann engines are being called with a
matched standard-model parameter vector before any future RLL extension is
allowed to inherit those backends.
"""

import argparse
import importlib.metadata
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Sequence

import numpy as np

C_KM_S = 299792.458
SCHEMA = "rll.class_camb_baseline_crosscheck.v1"


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", suffix=".part", delete=False
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


def scalar(value: Any) -> float:
    array = np.asarray(value, dtype=float)
    if array.size != 1:
        raise ValueError(f"expected scalar-like engine result, got shape={array.shape}")
    return float(array.reshape(-1)[0])


def relative_error(a: float, b: float, floor: float = 1.0e-30) -> float:
    return abs(float(a) - float(b)) / max(abs(float(a)), abs(float(b)), floor)


def parameter_vector(model: str) -> dict[str, float]:
    common = {
        "h": 0.674,
        "Omega_m": 0.315,
        "Omega_b": 0.049,
        "A_s": 2.1e-9,
        "n_s": 0.965,
        "tau": 0.054,
        "w0": -1.0,
        "wa": 0.0,
    }
    if model == "cpl":
        common.update({"w0": -0.90, "wa": 0.20})
    elif model != "lcdm":
        raise ValueError(f"unsupported model {model}")
    return common


def run_camb(model_name: str, z_values: Sequence[float], k_values: Sequence[float], lmax: int) -> dict[str, Any]:
    import camb
    from camb import model as camb_model

    p = parameter_vector(model_name)
    pars = camb.CAMBparams()
    ombh2 = p["Omega_b"] * p["h"] ** 2
    omch2 = (p["Omega_m"] - p["Omega_b"]) * p["h"] ** 2
    pars.set_cosmology(H0=100.0 * p["h"], ombh2=ombh2, omch2=omch2, mnu=0.0, omk=0.0, tau=p["tau"])
    pars.InitPower.set_params(As=p["A_s"], ns=p["n_s"])
    if model_name == "cpl":
        pars.set_dark_energy(w=p["w0"], wa=p["wa"], dark_energy_model="ppf")
    pars.set_for_lmax(int(lmax), lens_potential_accuracy=0)
    pars.set_matter_power(redshifts=sorted(set(map(float, z_values)), reverse=True), kmax=max(k_values) * 1.2)
    pars.NonLinear = camb_model.NonLinear_none
    results = camb.get_results(pars)
    spectra = results.get_cmb_power_spectra(pars, CMB_unit=None, raw_cl=True)
    unlensed = np.asarray(spectra["unlensed_scalar"], dtype=float)
    pk_interp = camb.get_matter_power_interpolator(
        pars,
        nonlinear=False,
        hubble_units=False,
        k_hunit=False,
        kmax=max(k_values) * 1.2,
        zmax=max(z_values) + 0.2,
    )
    return {
        "version": importlib.metadata.version("camb"),
        "H_km_s_Mpc": {str(z): scalar(results.hubble_parameter(z)) for z in z_values},
        "D_A_Mpc": {str(z): scalar(results.angular_diameter_distance(z)) for z in z_values if z > 0.0},
        "Pk_Mpc3": {f"z={z},k={k}": scalar(pk_interp.P(z, k)) for z in z_values for k in k_values},
        "Cl_TT_dimensionless": {str(ell): scalar(unlensed[ell, 0]) for ell in (30, 100, 300, 700) if ell <= lmax},
    }


def run_class(model_name: str, z_values: Sequence[float], k_values: Sequence[float], lmax: int) -> dict[str, Any]:
    from classy import Class

    p = parameter_vector(model_name)
    params: dict[str, Any] = {
        "h": p["h"],
        "Omega_b": p["Omega_b"],
        "Omega_cdm": p["Omega_m"] - p["Omega_b"],
        "A_s": p["A_s"],
        "n_s": p["n_s"],
        "tau_reio": p["tau"],
        "output": "tCl,pCl,mPk",
        "l_max_scalars": int(lmax),
        "P_k_max_1/Mpc": max(k_values) * 1.2,
        "z_pk": ",".join(str(z) for z in sorted(set(map(float, z_values)))),
        "non linear": "none",
    }
    if model_name == "cpl":
        params.update(
            {
                "Omega_Lambda": 0.0,
                "Omega_fld": 1.0 - p["Omega_m"],
                "w0_fld": p["w0"],
                "wa_fld": p["wa"],
                "fluid_equation_of_state": "CLP",
            }
        )
    cosmo = Class()
    try:
        cosmo.set(params)
        cosmo.compute()
        raw_cl = cosmo.raw_cl(int(lmax))
        result = {
            "version": importlib.metadata.version("classy"),
            "H_km_s_Mpc": {str(z): scalar(cosmo.Hubble(z) * C_KM_S) for z in z_values},
            "D_A_Mpc": {str(z): scalar(cosmo.angular_distance(z)) for z in z_values if z > 0.0},
            "Pk_Mpc3": {f"z={z},k={k}": scalar(cosmo.pk(k, z)) for z in z_values for k in k_values},
            "Cl_TT_dimensionless": {str(ell): scalar(raw_cl["tt"][ell]) for ell in (30, 100, 300, 700) if ell <= lmax},
        }
    finally:
        try:
            cosmo.struct_cleanup()
        finally:
            cosmo.empty()
    return result


def compare_model(model_name: str, z_values: Sequence[float], k_values: Sequence[float], lmax: int) -> dict[str, Any]:
    camb_result = run_camb(model_name, z_values, k_values, lmax)
    class_result = run_class(model_name, z_values, k_values, lmax)
    metrics: dict[str, Any] = {}
    tolerances = {
        "H_km_s_Mpc": 5.0e-3,
        "D_A_Mpc": 5.0e-3,
        "Pk_Mpc3": 8.0e-2,
        "Cl_TT_dimensionless": 8.0e-2,
    }
    all_pass = True
    for family, tolerance in tolerances.items():
        rows = []
        for key in sorted(camb_result[family], key=str):
            a = scalar(camb_result[family][key])
            b = scalar(class_result[family][key])
            error = relative_error(a, b)
            passed = error <= tolerance
            all_pass = all_pass and passed
            rows.append({
                "point": key,
                "CAMB": a,
                "CLASS": b,
                "relative_error": error,
                "tolerance": tolerance,
                "pass": passed,
            })
        metrics[family] = {
            "tolerance": tolerance,
            "max_relative_error": max(row["relative_error"] for row in rows),
            "pass": all(row["pass"] for row in rows),
            "points": rows,
        }
    return {
        "model": model_name,
        "parameter_vector": parameter_vector(model_name),
        "engines": {"CAMB": camb_result, "CLASS": class_result},
        "metrics": metrics,
        "pass": all_pass,
    }


def build(output: Path, *, lmax: int = 700) -> dict[str, Any]:
    z_values = [0.0, 0.5, 1.0, 2.0]
    k_values = [0.01, 0.05, 0.10]
    models = {name: compare_model(name, z_values, k_values, lmax) for name in ("lcdm", "cpl")}
    passed = all(row["pass"] for row in models.values())
    payload = {
        "schema": SCHEMA,
        "state": "VERIFIED_BASELINE_ENGINE_CROSSCHECK" if passed else "TOKEN_VAZIO_ENGINE_MISMATCH",
        "claim_allowed": False,
        "publication_ready": False,
        "models": models,
        "scope": {
            "z_values": z_values,
            "k_values_1_Mpc": k_values,
            "ell_values": [30, 100, 300, 700],
            "lmax": lmax,
            "massive_neutrinos": "disabled in both engines for this baseline crosscheck",
            "nonlinear": False,
        },
        "scientific_boundary": "This receipt validates matched standard LCDM/CPL backend plumbing only. It does not define or validate RLL perturbations and cannot authorize RLL CMB/growth claims.",
        "resolves_token": "TOKEN_VAZIO_LCDM_CPL_CLASS_CAMB_BASELINE_CROSSCHECK" if passed else None,
        "F_ok": [
            "Independent CLASS and CAMB engines receive the same standard-model parameter vectors.",
            "Background, linear matter power and dimensionless unlensed TT spectra are compared pointwise with declared tolerances."
        ],
        "F_gap": [] if passed else ["TOKEN_VAZIO_LCDM_CPL_CLASS_CAMB_BASELINE_CROSSCHECK"],
        "F_next": [
            "Do not use this baseline receipt as evidence for RLL until RLL perturbation closure relations are explicit and implemented independently in both engines."
        ],
    }
    atomic_json(output, payload)
    return payload


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--lmax", type=int, default=700)
    args = parser.parse_args(argv)
    try:
        payload = build(args.output, lmax=args.lmax)
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 2
    print(json.dumps({"state": payload["state"], "claim_allowed": False}, sort_keys=True))
    return 0 if payload["state"] == "VERIFIED_BASELINE_ENGINE_CROSSCHECK" else 3


if __name__ == "__main__":
    raise SystemExit(main())
