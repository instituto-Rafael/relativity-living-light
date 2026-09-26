#!/usr/bin/env python3
"""WS01 evidence generator for RX-PHYSICS-CANONICAL-V2.

This executor reduces uncertainty on three background-semantic axes:
- the 28-vs-33 H(z) surface;
- sensitivity to the two existing fixed Omega_r conventions;
- numerical convergence of log1p Simpson distances against scipy.quad.

It intentionally does NOT choose Omega_r and does NOT promote any growth proxy.
Selections from fit quality are forbidden by the preregistered contract.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

from scipy.integrate import quad

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import rx.cosmology as cosmo
CONTRACT_PATH = ROOT / "data/contracts/rll_ws01_background_decision_evidence.v1.json"
HZ_28 = ROOT / "data/real/cosmology/Hz_cosmic_chronometers_independent.csv"
HZ_33 = ROOT / "data/real/Hz_data_real.csv"

MODEL_VECTORS = {
    "LCDM": [70.0, 0.30, 0.02236, 0.80],
    "RLL": [70.0, 0.30, 0.010, 1.0, 0.30, 0.02236, 0.80],
}
RLL_NULL = [70.0, 0.30, 0.0, 1.0, 0.30, 0.02236, 0.80]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _contract() -> dict[str, Any]:
    payload = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    if payload.get("schema") != "rll.ws01_background_decision_evidence.v1":
        raise ValueError("unexpected WS01 evidence schema")
    if payload.get("claim_allowed") is not False:
        raise ValueError("WS01 evidence contract must remain fail-closed")
    return payload


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _pure_cc(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        row for row in rows
        if str(row["source"]).startswith("CC_") and "BAO" not in str(row["source"]).upper()
    ]


def _canonical_row(row: dict[str, str]) -> tuple[float, float, float, str]:
    return (
        float(row["z"]),
        float(row["H_obs"]),
        float(row["sigma_H"]),
        str(row["source"]),
    )


def _row_digest(rows: list[dict[str, str]]) -> str:
    payload = json.dumps(
        [_canonical_row(row) for row in rows],
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _hz_chi2(rows: list[dict[str, str]], model: str, vector: list[float]) -> float:
    total = 0.0
    for row in rows:
        pred = cosmo.hubble(model, float(row["z"]), vector)
        sigma = float(row["sigma_H"])
        total += ((float(row["H_obs"]) - pred) / sigma) ** 2
    return float(total)


def dataset_evidence() -> dict[str, Any]:
    rows28 = _rows(HZ_28)
    rows33 = _rows(HZ_33)
    selected33 = _pure_cc(rows33)
    excluded33 = [row for row in rows33 if row not in selected33]
    exact_rows = [_canonical_row(row) for row in rows28] == [_canonical_row(row) for row in selected33]

    original = cosmo.ORAD
    cosmo.ORAD = 9.0e-5
    try:
        chi = {}
        for model, vector in MODEL_VECTORS.items():
            a = _hz_chi2(rows28, model, vector)
            b = _hz_chi2(selected33, model, vector)
            chi[model] = {
                "independent_28": a,
                "selected_from_33": b,
                "absolute_delta": abs(a - b),
            }
    finally:
        cosmo.ORAD = original

    chi_identical = all(row["absolute_delta"] == 0.0 for row in chi.values())
    passed = len(rows28) == 28 and len(rows33) == 33 and len(selected33) == 28 and exact_rows and chi_identical
    return {
        "state": "PASS_IDENTICAL_PURE_CC_SURFACE" if passed else "FAIL_HZ_SURFACE_MISMATCH",
        "passed": passed,
        "files": {
            "independent_28": {"path": str(HZ_28.relative_to(ROOT)), "sha256": sha256_file(HZ_28), "rows": len(rows28)},
            "raw_33": {"path": str(HZ_33.relative_to(ROOT)), "sha256": sha256_file(HZ_33), "rows": len(rows33)},
        },
        "selected_from_33_rows": len(selected33),
        "selected_row_digest_28": _row_digest(rows28),
        "selected_row_digest_from_33": _row_digest(selected33),
        "row_level_exact_match": exact_rows,
        "fixed_vector_hz_chi2": chi,
        "excluded_rows": [
            {
                "z": float(row["z"]),
                "source": str(row["source"]),
                "reason": "BAO_OR_CC_PLUS_BAO_LABEL_EXCLUDED_FROM_PURE_CC_SURFACE",
            }
            for row in excluded33
        ],
        "decision_evidence": (
            "EVIDENCE_SUPPORTS_INDEPENDENT_COSMIC_CHRONOMETERS_28"
            if passed else "TOKEN_VAZIO_HZ_DATASET_DECISION"
        ),
        "boundary": (
            "The 33-row file is not a distinct pure-CC likelihood after the canonical anti-double-count filter: "
            "its 28 selected rows are exactly the independent 28-row file. The five excluded BAO-labelled rows "
            "remain available only in named legacy/freestanding projections."
        ),
    }


def _relative_delta(a: float, b: float) -> float:
    scale = max(abs(float(a)), abs(float(b)), 1.0e-300)
    return abs(float(b) - float(a)) / scale


def omega_r_evidence(contract: dict[str, Any]) -> dict[str, Any]:
    cfg = contract["axes"]["omega_r"]
    values = [float(x) for x in cfg["candidates"]]
    redshifts = [float(x) for x in cfg["redshifts"]]
    original = cosmo.ORAD
    evaluations: dict[str, Any] = {}
    null_limit: dict[str, Any] = {}
    try:
        for omega_r in values:
            cosmo.ORAD = omega_r
            key = format(omega_r, ".10g")
            evaluations[key] = {}
            for model, vector in MODEL_VECTORS.items():
                rows = []
                for z in redshifts:
                    rows.append({
                        "z": z,
                        "H_km_s_Mpc": cosmo.hubble(model, z, vector),
                        "DM_Mpc": cosmo.comoving_distance_mpc(model, z, vector, steps=2048, integration_mode="log1p"),
                    })
                evaluations[key][model] = rows

            deltas = []
            lcdm = MODEL_VECTORS["LCDM"]
            for z in redshifts:
                a = cosmo.e2("LCDM", z, lcdm)
                b = cosmo.e2("RLL", z, RLL_NULL)
                deltas.append(abs(a - b))
            null_limit[key] = {
                "max_abs_e2_delta_LCDM_vs_RLL_Omega_s0_0": max(deltas),
                "passed_1e_12": max(deltas) <= 1.0e-12,
            }
    finally:
        cosmo.ORAD = original

    low = evaluations[format(values[0], ".10g")]
    high = evaluations[format(values[1], ".10g")]
    sensitivity: dict[str, Any] = {}
    for model in MODEL_VECTORS:
        pairs = []
        for a, b in zip(low[model], high[model], strict=True):
            pairs.append({
                "z": a["z"],
                "relative_delta_H": _relative_delta(a["H_km_s_Mpc"], b["H_km_s_Mpc"]),
                "relative_delta_DM": _relative_delta(a["DM_Mpc"], b["DM_Mpc"]) if a["z"] > 0.0 else 0.0,
            })
        sensitivity[model] = {
            "rows": pairs,
            "max_relative_delta_H": max(row["relative_delta_H"] for row in pairs),
            "max_relative_delta_DM": max(row["relative_delta_DM"] for row in pairs),
        }

    return {
        "state": "MEASURED_NO_PHYSICAL_SELECTION",
        "candidate_values": values,
        "evaluations": evaluations,
        "sensitivity": sensitivity,
        "null_limit": null_limit,
        "null_limit_pass": all(row["passed_1e_12"] for row in null_limit.values()),
        "decision_evidence": "TOKEN_VAZIO_PHYSICAL_OMEGA_R_AUTHORITY_REQUIRED",
        "boundary": (
            "Both fixed conventions preserve the declared RLL null limit. Sensitivity is measured, "
            "but this executor cannot select a radiation-density convention from numerical fit or smallness."
        ),
    }


def _quad_distance(model: str, z: float, vector: list[float]) -> tuple[float, float]:
    if z <= 0.0:
        return 0.0, 0.0
    h0 = float(cosmo.unpack(model, vector)["H0"])
    value, err = quad(
        lambda zz: 1.0 / math.sqrt(max(cosmo.e2(model, zz, vector), 1.0e-300)),
        0.0,
        float(z),
        epsabs=1.0e-12,
        epsrel=1.0e-12,
        limit=500,
    )
    factor = cosmo.C_KMS / h0
    return factor * float(value), factor * float(err)


def distance_evidence(contract: dict[str, Any]) -> dict[str, Any]:
    cfg = contract["axes"]["distance_integration"]
    steps = [int(x) for x in cfg["step_sweep"]]
    candidate_steps = int(cfg["candidate_steps"])
    redshifts = [float(x) for x in cfg["redshifts"]]
    tol_rel = float(cfg["preregistered_tolerances"]["max_relative_error_vs_quad"])
    tol_refine = float(cfg["preregistered_tolerances"]["max_relative_refinement_delta_2048_to_4096"])

    original = cosmo.ORAD
    cases = []
    try:
        for omega_r in (9.0e-5, 9.18e-5):
            cosmo.ORAD = omega_r
            for model, vector in MODEL_VECTORS.items():
                for z in redshifts:
                    reference, quad_abs_error = _quad_distance(model, z, vector)
                    sweep = {}
                    for n in steps:
                        value = cosmo.comoving_distance_mpc(model, z, vector, steps=n, integration_mode="log1p")
                        sweep[str(n)] = {
                            "DM_Mpc": value,
                            "relative_error_vs_quad": _relative_delta(value, reference),
                        }
                    candidate = sweep[str(candidate_steps)]["DM_Mpc"]
                    refined = sweep["4096"]["DM_Mpc"]
                    cases.append({
                        "omega_r": omega_r,
                        "model": model,
                        "z": z,
                        "quad_DM_Mpc": reference,
                        "quad_reported_abs_error_Mpc": quad_abs_error,
                        "sweep": sweep,
                        "candidate_relative_error_vs_quad": _relative_delta(candidate, reference),
                        "relative_refinement_delta_2048_to_4096": _relative_delta(candidate, refined),
                    })
    finally:
        cosmo.ORAD = original

    max_rel = max(row["candidate_relative_error_vs_quad"] for row in cases)
    max_refine = max(row["relative_refinement_delta_2048_to_4096"] for row in cases)
    passed = max_rel <= tol_rel and max_refine <= tol_refine
    return {
        "state": "PASS_PREREGISTERED_DISTANCE_TOLERANCE" if passed else "FAIL_PREREGISTERED_DISTANCE_TOLERANCE",
        "passed": passed,
        "method": "log1p_simpson",
        "independent_reference": "scipy.integrate.quad_over_z",
        "candidate_steps": candidate_steps,
        "tolerances": {
            "max_relative_error_vs_quad": tol_rel,
            "max_relative_refinement_delta_2048_to_4096": tol_refine,
        },
        "observed": {
            "max_relative_error_vs_quad": max_rel,
            "max_relative_refinement_delta_2048_to_4096": max_refine,
        },
        "cases": cases,
        "decision_evidence": (
            "EVIDENCE_SUPPORTS_LOG1P_SIMPSON_2048_WITH_PREREGISTERED_TOLERANCE"
            if passed else "TOKEN_VAZIO_DISTANCE_TOLERANCE_DECISION"
        ),
    }


def build_report() -> dict[str, Any]:
    contract = _contract()
    hz = dataset_evidence()
    omega = omega_r_evidence(contract)
    distance = distance_evidence(contract)
    required_pass = bool(hz["passed"] and omega["null_limit_pass"] and distance["passed"])
    terminalizable = []
    if hz["passed"]:
        terminalizable.append("hz_dataset")
    if distance["passed"]:
        terminalizable.append("distance_integration")
    return {
        "schema": "rll.ws01_background_decision_evidence_receipt.v1",
        "state": "EVIDENCE_REDUCED_WS01_PARTIAL" if required_pass else "BLOCKED_WS01_DECISION_EVIDENCE",
        "claim_allowed": False,
        "scientific_confirmation": False,
        "contract_sha256": sha256_file(CONTRACT_PATH),
        "hz_dataset": hz,
        "omega_r": omega,
        "distance_integration": distance,
        "growth_mode": {
            "state": "TOKEN_VAZIO_UNTIL_WS06",
            "promotion_allowed": False,
        },
        "terminalizable_axes_from_this_evidence": terminalizable,
        "remaining_blocking_axes": ["omega_r", "growth_mode"],
        "required_measurement_pass": required_pass,
        "uncertainty_reduction": {
            "hz_dataset": "reduced_to_one_pure_CC_surface" if hz["passed"] else "not_reduced",
            "distance_integration": "bounded_by_preregistered_tolerance" if distance["passed"] else "not_reduced",
            "omega_r": "sensitivity_measured_physical_authority_still_open",
            "growth_mode": "unchanged_waiting_for_WS06",
        },
        "F_next": (
            "Persist terminal hz_dataset/distance_integration decisions only if this receipt passes; "
            "then derive or source-bind a physical Omega_r convention. Do not promote growth before WS06."
        ),
        "boundary": (
            "WS01 remains partial while Omega_r physical authority and perturbation-derived growth semantics are open. "
            "This receipt cannot make RX-PHYSICS-CANONICAL-V2 fully terminal."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--require-pass", action="store_true")
    args = parser.parse_args()
    report = build_report()
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "state": report["state"],
        "hz_dataset": report["hz_dataset"]["state"],
        "distance_integration": report["distance_integration"]["state"],
        "omega_r": report["omega_r"]["state"],
        "terminalizable_axes": report["terminalizable_axes_from_this_evidence"],
        "remaining_blocking_axes": report["remaining_blocking_axes"],
        "max_omega_r_H_delta": max(v["max_relative_delta_H"] for v in report["omega_r"]["sensitivity"].values()),
        "max_omega_r_DM_delta": max(v["max_relative_delta_DM"] for v in report["omega_r"]["sensitivity"].values()),
        "distance_max_relative_error": report["distance_integration"]["observed"]["max_relative_error_vs_quad"],
        "distance_max_refinement_delta": report["distance_integration"]["observed"]["max_relative_refinement_delta_2048_to_4096"],
        "claim_allowed": False,
    }, indent=2, sort_keys=True))
    if args.require_pass and not report["required_measurement_pass"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
