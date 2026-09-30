#!/usr/bin/env python3
"""WS01 physical authority test for the canonical Omega_r background semantics.

The purpose is to replace two fixed engineering snapshots with one source-bound
physical-density convention. It does not implement massive-neutrino transition
physics or a Boltzmann hierarchy.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
for item in (ROOT, SRC):
    if str(item) not in sys.path:
        sys.path.insert(0, str(item))

import rx.cosmology as cosmo
from rll.cosmology_radiation import (
    NEFF_STANDARD,
    OMEGA_GAMMA_H2_REF,
    TCMB_REF_K,
    omega_r_from_h0,
    omega_r_h2,
    relativistic_neutrino_factor,
)

CONTRACT_PATH = ROOT / "data/contracts/rll_ws01_omega_r_physical_authority.v1.json"
LEGACY = (9.0e-5, 9.18e-5)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_contract() -> dict[str, Any]:
    data = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    if data.get("schema") != "rll.ws01_omega_r_physical_authority.v1":
        raise ValueError("unexpected contract schema")
    if data.get("claim_allowed") is not False:
        raise ValueError("claim boundary drift")
    return data


def _rll_null_delta(h0: float, omega_r: float) -> float:
    lcdm = [h0, 0.30, 0.02236, 0.80]
    rll = [h0, 0.30, 0.0, 1.0, 0.30, 0.02236, 0.80]
    old = cosmo.ORAD
    try:
        cosmo.ORAD = float(omega_r)
        redshifts = (0.0, 0.5, 1.0, 2.33, 10.0, 1100.0)
        return max(abs(cosmo.e2("LCDM", z, lcdm) - cosmo.e2("RLL", z, rll)) for z in redshifts)
    finally:
        cosmo.ORAD = old


def build_report() -> dict[str, Any]:
    contract = _load_contract()
    cand = contract["candidate_semantics"]
    if not math.isclose(float(cand["tcmb_k"]), TCMB_REF_K, rel_tol=0.0, abs_tol=0.0):
        raise ValueError("T_CMB contract/implementation drift")
    if not math.isclose(float(cand["neff"]), NEFF_STANDARD, rel_tol=0.0, abs_tol=0.0):
        raise ValueError("N_eff contract/implementation drift")
    if not math.isclose(float(cand["omega_gamma_h2_ref"]), OMEGA_GAMMA_H2_REF, rel_tol=0.0, abs_tol=0.0):
        raise ValueError("Omega_gamma h2 contract/implementation drift")

    h0_grid = [float(x) for x in contract["reference_h0_grid_km_s_mpc"]]
    physical_h2 = omega_r_h2(TCMB_REF_K, NEFF_STANDARD)
    rows = []
    null_deltas = []
    reconstructed_h2 = []
    for h0 in h0_grid:
        omega_r = omega_r_from_h0(h0, TCMB_REF_K, NEFF_STANDARD)
        h = h0 / 100.0
        recovered = omega_r * h * h
        reconstructed_h2.append(recovered)
        null_delta = _rll_null_delta(h0, omega_r)
        null_deltas.append(null_delta)
        rows.append({
            "H0_km_s_Mpc": h0,
            "h": h,
            "Omega_r": omega_r,
            "omega_r_h2_reconstructed": recovered,
            "RLL_LCDM_null_max_abs_e2_delta": null_delta,
            "legacy_relative_delta": {
                "vs_9.0e-5": abs(omega_r - LEGACY[0]) / omega_r,
                "vs_9.18e-5": abs(omega_r - LEGACY[1]) / omega_r,
            },
        })

    span = max(reconstructed_h2) - min(reconstructed_h2)
    rel_span = span / max(abs(physical_h2), 1e-300)
    monotonic = all(rows[i]["Omega_r"] > rows[i + 1]["Omega_r"] for i in range(len(rows) - 1))
    null_max = max(null_deltas)

    snapshot_h0 = {}
    for fixed in LEGACY:
        h = math.sqrt(physical_h2 / fixed)
        snapshot_h0[format(fixed, ".8g")] = {
            "fixed_Omega_r": fixed,
            "equivalent_H0_km_s_Mpc_under_derived_physical_density": 100.0 * h,
        }

    limits = contract["pass_when"]
    passed = (
        rel_span <= float(limits["physical_density_relative_span_max"])
        and null_max <= float(limits["rll_lcdm_null_e2_max_abs_delta"])
        and monotonic
        and physical_h2 > 0.0
        and math.isclose(
            relativistic_neutrino_factor(),
            (7.0 / 8.0) * (4.0 / 11.0) ** (4.0 / 3.0),
            rel_tol=0.0,
            abs_tol=1e-15,
        )
    )

    return {
        "schema": "rll.ws01_omega_r_physical_authority_receipt.v1",
        "state": "PASS_DERIVED_STANDARD_RADIATION_AUTHORITY" if passed else "BLOCKED_OMEGA_R_PHYSICAL_AUTHORITY",
        "claim_allowed": False,
        "scientific_confirmation": False,
        "contract_sha256": sha256_file(CONTRACT_PATH),
        "authority": {
            "semantics": "DERIVED_STANDARD_RELATIVISTIC_RADIATION",
            "Tcmb_K": TCMB_REF_K,
            "N_eff": NEFF_STANDARD,
            "Omega_gamma_h2_ref": OMEGA_GAMMA_H2_REF,
            "rho_nu_over_rho_gamma_per_Neff": relativistic_neutrino_factor(),
            "omega_r_h2": physical_h2,
            "formula": "Omega_r = omega_r_h2 / h^2",
        },
        "reference_grid": rows,
        "legacy_fixed_snapshots": snapshot_h0,
        "checks": {
            "omega_r_h2_relative_span": rel_span,
            "omega_r_monotonic_decreasing_with_H0": monotonic,
            "RLL_LCDM_null_max_abs_e2_delta": null_max,
            "full_massive_neutrino_transition_modelled": False,
        },
        "passed": passed,
        "selected_semantics_if_pass": "derived_standard_relativistic_radiation",
        "legacy_fixed_values_promoted": False,
        "remaining_boundary": "Full massive-neutrino transition and Boltzmann thermodynamics remain downstream; this closes only the bounded WS01 background convention.",
        "claim_boundary": "No observational preference or RLL confirmation follows from this authority choice.",
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
        "omega_r_h2": report["authority"]["omega_r_h2"],
        "relative_span": report["checks"]["omega_r_h2_relative_span"],
        "null_max_delta": report["checks"]["RLL_LCDM_null_max_abs_e2_delta"],
        "legacy_fixed_snapshots": report["legacy_fixed_snapshots"],
        "claim_allowed": False,
    }, indent=2, sort_keys=True))
    return 0 if (not args.require_pass or report["passed"]) else 2


if __name__ == "__main__":
    raise SystemExit(main())
