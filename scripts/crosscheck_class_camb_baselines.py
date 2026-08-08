#!/usr/bin/env python3
from __future__ import annotations

"""Numerically cross-check standard LCDM/CPL baselines in CLASS and CAMB.

This script intentionally does not implement RLL perturbations. Its job is to
establish that the two independent Boltzmann engines receive a matched standard
parameter vector. It also cross-checks the baryon-drag sound horizon r_drag and
measures the current repository power-law approximation without promoting that
approximation to a full Boltzmann/recombination solution.
"""

import argparse
import importlib.metadata
import json
import os
import tempfile
import traceback
from pathlib import Path
from typing import Any, Sequence

import numpy as np

C_KM_S = 299792.458
SCHEMA = "rll.class_camb_baseline_crosscheck.v2"


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


def repository_rd_approximation_mpc(p: dict[str, float]) -> float:
    """Mirror the current joint-real-likelihood lightweight r_d approximation."""
    om_h2 = float(p["Omega_m"]) * float(p["h"]) ** 2
    ob_h2 = float(p["Omega_b"]) * float(p["h"]) ** 2
    return float(147.78 * (om_h2 / 0.1432) ** (-0.255) * (ob_h2 / 0.02236) ** (-0.134))


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
    z_for_power = np.asarray(sorted(set(map(float, z_values)), reverse=True), dtype=float)
    pars.set_matter_power(redshifts=z_for_power.tolist(), kmax=float(max(k_values) * 1.2))
    pars.NonLinear = camb_model.NonLinear_none
    results = camb.get_results(pars)
    spectra = results.get_cmb_power_spectra(pars, CMB_unit=None, raw_cl=True)
    unlensed = np.asarray(spectra["unlensed_scalar"], dtype=float)
    derived = results.get_derived_params()
    if "rdrag" not in derived:
        raise ValueError(f"CAMB derived parameters do not contain rdrag: {sorted(derived)}")
    r_drag = scalar(derived["rdrag"])

    z_array = np.asarray(list(map(float, z_values)), dtype=float)
    h_values = np.asarray(results.hubble_parameter(z_array), dtype=float).reshape(-1)
    if h_values.size != z_array.size:
        raise ValueError(f"CAMB H(z) shape mismatch: {h_values.shape} vs {z_array.shape}")

    positive_z = np.asarray([float(z) for z in z_values if float(z) > 0.0], dtype=float)
    da_values = np.asarray(results.angular_diameter_distance(positive_z), dtype=float).reshape(-1)
    if da_values.size != positive_z.size:
        raise ValueError(f"CAMB D_A(z) shape mismatch: {da_values.shape} vs {positive_z.shape}")

    pk_interp = camb.get_matter_power_interpolator(
        pars,
        nonlinear=False,
        hubble_units=False,
        k_hunit=False,
        kmax=float(max(k_values) * 1.2),
        zmax=float(max(z_values) + 0.2),
    )
    k_array = np.asarray(list(map(float, k_values)), dtype=float)
    pk_grid = np.asarray(pk_interp.P(z_array, k_array, grid=True), dtype=float)
    expected_shape = (z_array.size, k_array.size)
    if pk_grid.shape != expected_shape:
        raise ValueError(f"CAMB P(k,z) shape mismatch: {pk_grid.shape} vs {expected_shape}")

    return {
        "version": importlib.metadata.version("camb"),
        "H_km_s_Mpc": {str(float(z)): float(value) for z, value in zip(z_array, h_values)},
        "D_A_Mpc": {str(float(z)): float(value) for z, value in zip(positive_z, da_values)},
        "Pk_Mpc3": {
            f"z={float(z)},k={float(k)}": float(pk_grid[zi, ki])
            for zi, z in enumerate(z_array)
            for ki, k in enumerate(k_array)
        },
        "Cl_TT_dimensionless": {
            str(ell): scalar(unlensed[ell, 0]) for ell in (30, 100, 300, 700) if ell <= lmax
        },
        "r_drag_Mpc": {"drag_epoch": r_drag},
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
        "P_k_max_1/Mpc": float(max(k_values) * 1.2),
        "z_pk": ",".join(str(float(z)) for z in sorted(set(map(float, z_values)))),
        "non linear": "none",
    }
    if model_name == "cpl":
        params.update({
            "Omega_Lambda": 0.0,
            "w0_fld": p["w0"],
            "wa_fld": p["wa"],
            "fluid_equation_of_state": "CLP",
        })
    cosmo = Class()
    try:
        cosmo.set(params)
        cosmo.compute()
        raw_cl = cosmo.raw_cl(int(lmax))
        rd_attr = getattr(cosmo, "rs_drag")
        r_drag = scalar(rd_attr() if callable(rd_attr) else rd_attr)
        result = {
            "version": importlib.metadata.version("classy"),
            "H_km_s_Mpc": {str(float(z)): scalar(cosmo.Hubble(float(z)) * C_KM_S) for z in z_values},
            "D_A_Mpc": {str(float(z)): scalar(cosmo.angular_distance(float(z))) for z in z_values if z > 0.0},
            "Pk_Mpc3": {
                f"z={float(z)},k={float(k)}": scalar(cosmo.pk(float(k), float(z)))
                for z in z_values for k in k_values
            },
            "Cl_TT_dimensionless": {
                str(ell): scalar(raw_cl["tt"][ell]) for ell in (30, 100, 300, 700) if ell <= lmax
            },
            "r_drag_Mpc": {"drag_epoch": r_drag},
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
        "r_drag_Mpc": 5.0e-3,
    }
    all_pass = True
    for family, tolerance in tolerances.items():
        rows = []
        if set(camb_result[family]) != set(class_result[family]):
            raise ValueError(f"engine key mismatch for {model_name}/{family}")
        for key in sorted(camb_result[family], key=str):
            a = scalar(camb_result[family][key])
            b = scalar(class_result[family][key])
            error = relative_error(a, b)
            passed = error <= tolerance
            all_pass = all_pass and passed
            rows.append({"point": key, "CAMB": a, "CLASS": b, "relative_error": error, "tolerance": tolerance, "pass": passed})
        metrics[family] = {
            "tolerance": tolerance,
            "max_relative_error": max(row["relative_error"] for row in rows),
            "pass": all(row["pass"] for row in rows),
            "points": rows,
        }

    p = parameter_vector(model_name)
    approximation = repository_rd_approximation_mpc(p)
    camb_rd = scalar(camb_result["r_drag_Mpc"]["drag_epoch"])
    class_rd = scalar(class_result["r_drag_Mpc"]["drag_epoch"])
    approximation_diagnostic = {
        "repository_approximation_Mpc": approximation,
        "CAMB_rdrag_Mpc": camb_rd,
        "CLASS_rs_drag_Mpc": class_rd,
        "relative_error_vs_CAMB": relative_error(approximation, camb_rd),
        "relative_error_vs_CLASS": relative_error(approximation, class_rd),
        "claim_allowed": False,
        "interpretation": "Diagnostic only: this measures the existing lightweight r_d approximation against full Boltzmann/recombination backends; it does not replace the H0/r_d inference path.",
    }
    return {
        "model": model_name,
        "parameter_vector": p,
        "engines": {"CAMB": camb_result, "CLASS": class_result},
        "metrics": metrics,
        "rd_approximation_diagnostic": approximation_diagnostic,
        "pass": all_pass,
    }


def build(output: Path, *, lmax: int = 700) -> dict[str, Any]:
    z_values = [0.0, 0.5, 1.0, 2.0]
    k_values = [0.01, 0.05, 0.10]
    models = {name: compare_model(name, z_values, k_values, lmax) for name in ("lcdm", "cpl")}
    passed = all(row["pass"] for row in models.values())
    payload = {
        "schema": SCHEMA,
        "state": "VERIFIED_BASELINE_ENGINE_CROSSCHECK_WITH_RDRAG" if passed else "TOKEN_VAZIO_ENGINE_MISMATCH",
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
            "rd_engine_agreement_tolerance": 5.0e-3,
        },
        "scientific_boundary": "This receipt validates matched standard LCDM/CPL backend plumbing and cross-engine r_drag only. It does not define or validate RLL perturbations and it does not by itself replace the repository H0/r_d approximation in inference.",
        "reduces_token": "TOKEN_VAZIO_H0_RD_FULL_BOLTZMANN_REPRODUCTION" if passed else None,
        "resolves_token": "TOKEN_VAZIO_LCDM_CPL_CLASS_CAMB_BASELINE_CROSSCHECK" if passed else None,
        "F_ok": [
            "Independent CLASS and CAMB engines receive the same standard-model parameter vectors.",
            "Background, linear matter power, unlensed TT and baryon-drag sound horizon are compared pointwise with predeclared tolerances.",
            "The existing lightweight repository r_d approximation is measured against both full engines without being silently promoted."
        ],
        "F_gap": [
            "The actual H0/r_d inference route still calls the lightweight approximation; replacement requires a separately validated integration strategy.",
            "RLL perturbation closure and independent CLASS/CAMB RLL implementations remain absent."
        ] if passed else ["TOKEN_VAZIO_LCDM_CPL_CLASS_CAMB_BASELINE_CROSSCHECK", "TOKEN_VAZIO_H0_RD_FULL_BOLTZMANN_REPRODUCTION"],
        "F_next": [
            "If cross-engine r_drag agrees, use this receipt to quantify approximation bias and design a cached/grid or direct Boltzmann H0/r_d route before formal inference.",
            "Do not use this baseline receipt as RLL perturbation evidence."
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
        traceback.print_exc()
        print(f"ERROR: {type(exc).__name__}: {exc}")
        return 2
    worst = {}
    for model, model_data in payload["models"].items():
        worst[model] = {}
        for family, metric in model_data["metrics"].items():
            point = max(metric["points"], key=lambda row: row["relative_error"])
            worst[model][family] = point
    print(json.dumps({"state": payload["state"], "claim_allowed": False, "worst_points": worst}, sort_keys=True))
    return 0 if payload["state"] == "VERIFIED_BASELINE_ENGINE_CROSSCHECK_WITH_RDRAG" else 3


if __name__ == "__main__":
    raise SystemExit(main())
