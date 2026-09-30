#!/usr/bin/env python3
"""Deterministic QCD-era consistency gate for Relativity Living Light (RLL).

This tool does not infer a cosmological preference from collider v2/v3 data.
It consumes a temperature-indexed thermal-background energy-density table and
an explicitly separated RLL contribution, then computes H(T), a radiation-era
time proxy, entropy-corrected a(T)/a_ref, and Delta_H.

Scientific claim propagation is fail-closed:
- PASS permits only the local result to be used as a descendant input.
- FALSIFIED quarantines the local hypothesis from descendant calculations.
- TOKEN_VAZIO holds propagation until provenance/constraint evidence exists.

The gate never authorizes a global RLL > LambdaCDM claim by itself.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

G_SI = 6.67430e-11
C_SI = 299_792_458.0
GEV_TO_J = 1.602176634e-10
FM3_TO_M3 = 1.0e-45
GEV_FM3_TO_J_M3 = GEV_TO_J / FM3_TO_M3

INPUT_SCHEMA = "rll.qcd_primordial_input.v1"
RECEIPT_SCHEMA = "rll.qcd_primordial_gate_receipt.v1"

# A single total non-RLL thermal background avoids double counting QCD if a
# caller has already folded QCD degrees of freedom into "radiation".
FORBIDDEN_SPLIT_KEYS = {
    "rho_rad_GeV_fm3",
    "rho_QCD_GeV_fm3",
    "epsilon_rad_GeV_fm3",
    "epsilon_QCD_GeV_fm3",
    "epsilon_qcd_GeV_fm3",
}


class GateInputError(ValueError):
    """Raised when the input contract is structurally unsafe."""


def _finite_number(value: Any, name: str) -> float:
    if isinstance(value, bool):
        raise GateInputError(f"{name} must be numeric, not bool")
    try:
        out = float(value)
    except (TypeError, ValueError) as exc:
        raise GateInputError(f"{name} must be numeric") from exc
    if not math.isfinite(out):
        raise GateInputError(f"{name} must be finite")
    return out


def hubble_from_energy_density(epsilon_gev_fm3: float) -> float:
    """Return H [s^-1] from total energy density epsilon [GeV/fm^3]."""
    epsilon = _finite_number(epsilon_gev_fm3, "epsilon_gev_fm3")
    if epsilon <= 0.0:
        raise GateInputError("total energy density must be > 0")
    epsilon_j_m3 = epsilon * GEV_FM3_TO_J_M3
    return math.sqrt((8.0 * math.pi * G_SI * epsilon_j_m3) / (3.0 * C_SI**2))


def radiation_time_proxy_s(hubble_s_inv: float) -> float:
    """Radiation-era proxy t ~= 1/(2H); not a full numerical integration."""
    h = _finite_number(hubble_s_inv, "hubble_s_inv")
    if h <= 0.0:
        raise GateInputError("H must be > 0")
    return 0.5 / h


def entropy_scale_factor_ratio(
    temperature_mev: float,
    g_star_s: float,
    reference_temperature_mev: float,
    reference_g_star_s: float,
) -> float:
    """Use a*T*g_*s^(1/3)=const to return a(T)/a(T_ref)."""
    t = _finite_number(temperature_mev, "T_MeV")
    gs = _finite_number(g_star_s, "g_star_s")
    tref = _finite_number(reference_temperature_mev, "reference.T_MeV")
    gsref = _finite_number(reference_g_star_s, "reference.g_star_s")
    if min(t, gs, tref, gsref) <= 0.0:
        raise GateInputError("T and g_star_s values must be > 0")
    return (tref / t) * ((gsref / gs) ** (1.0 / 3.0))


def _validate_row_contract(row: dict[str, Any], index: int) -> None:
    if not isinstance(row, dict):
        raise GateInputError(f"rows[{index}] must be an object")
    forbidden = sorted(FORBIDDEN_SPLIT_KEYS.intersection(row))
    if forbidden:
        raise GateInputError(
            "unsafe split background keys found at "
            f"rows[{index}]: {', '.join(forbidden)}; "
            "use epsilon_background_GeV_fm3 as the complete non-RLL thermal "
            "background to avoid QCD/radiation double counting"
        )
    for key in (
        "T_MeV",
        "epsilon_background_GeV_fm3",
        "epsilon_rll_GeV_fm3",
        "g_star_s",
    ):
        if key not in row:
            raise GateInputError(f"rows[{index}].{key} is required")


def evaluate_gate(payload: dict[str, Any], *, input_sha256: str = "TOKEN_VAZIO") -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise GateInputError("input root must be an object")
    if payload.get("schema") != INPUT_SCHEMA:
        raise GateInputError(f"schema must be {INPUT_SCHEMA!r}")

    rows = payload.get("rows")
    if not isinstance(rows, list) or not rows:
        raise GateInputError("rows must be a non-empty array")

    reference = payload.get("reference")
    if not isinstance(reference, dict):
        raise GateInputError("reference must be an object")
    ref_t = _finite_number(reference.get("T_MeV"), "reference.T_MeV")
    ref_gs = _finite_number(reference.get("g_star_s"), "reference.g_star_s")

    evidence = payload.get("evidence")
    if not isinstance(evidence, dict):
        evidence = {}
    source_kind = str(evidence.get("source_kind", "TOKEN_VAZIO")).strip()
    checksum_verified = evidence.get("checksum_verified") is True
    baseline_equivalent = evidence.get("baseline_equivalent") is True
    eos_provenance_verified = evidence.get("eos_provenance_verified") is True

    constraint = payload.get("constraint")
    if not isinstance(constraint, dict):
        constraint = {}
    bound_raw = constraint.get("max_abs_delta_h")
    constraint_verified = constraint.get("verified") is True
    max_abs_delta_h: float | None = None
    if bound_raw is not None:
        max_abs_delta_h = _finite_number(bound_raw, "constraint.max_abs_delta_h")
        if max_abs_delta_h < 0.0:
            raise GateInputError("constraint.max_abs_delta_h must be >= 0")

    computed_rows: list[dict[str, Any]] = []
    for i, row in enumerate(rows):
        _validate_row_contract(row, i)
        t_mev = _finite_number(row["T_MeV"], f"rows[{i}].T_MeV")
        epsilon_background = _finite_number(
            row["epsilon_background_GeV_fm3"],
            f"rows[{i}].epsilon_background_GeV_fm3",
        )
        epsilon_rll = _finite_number(
            row["epsilon_rll_GeV_fm3"],
            f"rows[{i}].epsilon_rll_GeV_fm3",
        )
        g_star_s = _finite_number(row["g_star_s"], f"rows[{i}].g_star_s")
        if t_mev <= 0.0 or epsilon_background <= 0.0 or g_star_s <= 0.0:
            raise GateInputError(f"rows[{i}] requires T, background epsilon and g_star_s > 0")
        epsilon_total_rll = epsilon_background + epsilon_rll
        if epsilon_total_rll <= 0.0:
            raise GateInputError(f"rows[{i}] RLL total energy density must be > 0")

        h_baseline = hubble_from_energy_density(epsilon_background)
        h_rll = hubble_from_energy_density(epsilon_total_rll)
        delta_h = (h_rll - h_baseline) / h_baseline
        a_over_ref = entropy_scale_factor_ratio(t_mev, g_star_s, ref_t, ref_gs)

        computed_rows.append(
            {
                "T_MeV": t_mev,
                "epsilon_background_GeV_fm3": epsilon_background,
                "epsilon_rll_GeV_fm3": epsilon_rll,
                "H_baseline_s_inv": h_baseline,
                "H_rll_s_inv": h_rll,
                "delta_h": delta_h,
                "t_baseline_proxy_s": radiation_time_proxy_s(h_baseline),
                "t_rll_proxy_s": radiation_time_proxy_s(h_rll),
                "a_over_a_ref": a_over_ref,
                "approximation_note": "t_proxy=1/(2H); a(T) uses entropy conservation, not full Friedmann integration",
            }
        )

    max_observed = max(abs(row["delta_h"]) for row in computed_rows)

    reason_codes: list[str] = []
    ready_for_decision = True
    if source_kind != "real_data":
        ready_for_decision = False
        reason_codes.append("SOURCE_NOT_REAL_DATA")
    if not checksum_verified:
        ready_for_decision = False
        reason_codes.append("CHECKSUM_NOT_VERIFIED")
    if not baseline_equivalent:
        ready_for_decision = False
        reason_codes.append("BASELINE_EQUIVALENCE_NOT_VERIFIED")
    if not eos_provenance_verified:
        ready_for_decision = False
        reason_codes.append("EOS_PROVENANCE_NOT_VERIFIED")
    if max_abs_delta_h is None:
        ready_for_decision = False
        reason_codes.append("CONSTRAINT_BOUND_TOKEN_VAZIO")
    if not constraint_verified:
        ready_for_decision = False
        reason_codes.append("CONSTRAINT_NOT_VERIFIED")

    if not ready_for_decision:
        status = "TOKEN_VAZIO"
        pspi_action = "HOLD_MISSING_EVIDENCE"
        descendant_input_allowed = False
    elif max_observed > max_abs_delta_h:
        status = "FALSIFIED"
        pspi_action = "QUARANTINE_FROM_DESCENDANTS"
        descendant_input_allowed = False
        reason_codes.append("DELTA_H_EXCEEDS_VERIFIED_BOUND")
    else:
        status = "PASS"
        pspi_action = "ALLOW_LOCAL_RESULT_ONLY"
        descendant_input_allowed = True
        reason_codes.append("DELTA_H_WITHIN_VERIFIED_BOUND")

    return {
        "schema": RECEIPT_SCHEMA,
        "input_sha256": input_sha256,
        "local_gate_status": status,
        "pspi_action": pspi_action,
        "descendant_input_allowed": descendant_input_allowed,
        "global_scientific_claim_allowed": False,
        "global_claim_boundary": (
            "This QCD-era consistency gate alone cannot establish RLL preference "
            "over LambdaCDM/CPL or convert collider flow measurements into a cosmological likelihood."
        ),
        "decision_basis": {
            "source_kind": source_kind,
            "checksum_verified": checksum_verified,
            "baseline_equivalent": baseline_equivalent,
            "eos_provenance_verified": eos_provenance_verified,
            "constraint_verified": constraint_verified,
            "max_abs_delta_h_bound": max_abs_delta_h,
            "max_abs_delta_h_observed": max_observed,
            "reason_codes": reason_codes,
        },
        "physics_contract": {
            "background_definition": (
                "epsilon_background_GeV_fm3 is the complete non-RLL thermal background "
                "for each T; do not add a separate QCD term if it is already included."
            ),
            "friedmann_energy_density_form": "H^2 = 8*pi*G*epsilon/(3*c^2)",
            "delta_h": "(H_RLL-H_baseline)/H_baseline",
            "entropy_relation": "a*T*g_star_s^(1/3)=constant",
            "collider_bridge": "reference/validation context only; v2,v3 are not direct RLL likelihood inputs",
        },
        "rows": computed_rows,
    }


def run_gate(input_path: Path, output_path: Path) -> dict[str, Any]:
    raw = input_path.read_bytes()
    payload = json.loads(raw.decode("utf-8"))
    receipt = evaluate_gate(payload, input_sha256=hashlib.sha256(raw).hexdigest())
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return receipt


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the RLL QCD primordial consistency gate.")
    parser.add_argument("input", type=Path)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/audit/rll_qcd_primordial_gate.json"),
    )
    parser.add_argument(
        "--require-pass",
        action="store_true",
        help="exit nonzero unless local_gate_status is PASS",
    )
    args = parser.parse_args(argv)

    try:
        receipt = run_gate(args.input, args.output)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, GateInputError) as exc:
        print(f"FAIL: {exc}")
        return 2

    print(f"status={receipt['local_gate_status']}")
    print(f"pspi_action={receipt['pspi_action']}")
    print(f"output={args.output}")
    if args.require_pass and receipt["local_gate_status"] != "PASS":
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
