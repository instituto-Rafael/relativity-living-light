#!/usr/bin/env python3
"""Evaluate bounded M87* source-regime admissibility from published ranges.

This is a domain-admissibility calculation, not an SGPT validation. It uses only
values bound in data/evidence/m87/source_state_evidence.v1.json and emits a
receipt whose unresolved regimes remain TOKEN_VAZIO.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EVIDENCE = ROOT / "data" / "evidence" / "m87" / "source_state_evidence.v1.json"
TOKEN = "TOKEN_VAZIO"

HBAR = 1.054_571_817e-34
M_E = 9.109_383_7015e-31
M_P = 1.672_621_923_69e-27
K_B = 1.380_649e-23
MU_B = 9.274_010_0783e-24
E_CHARGE = 1.602_176_634e-19
B_Q = 4.414e9
EV = E_CHARGE


def require(cond: bool, msg: str) -> None:
    if not cond:
        raise ValueError(msg)


def load(path: Path) -> dict:
    doc = json.loads(path.read_text(encoding="utf-8"))
    require(doc.get("schema") == "rll.sgpt.m87.source-state-evidence/v1", "wrong evidence schema")
    require(doc.get("claim_allowed") is False, "source evidence cannot promote claim")
    return doc


def fermi_energy_nr_joule(n_m3: float) -> float:
    p_f = HBAR * (3.0 * math.pi**2 * n_m3) ** (1.0 / 3.0)
    return p_f * p_f / (2.0 * M_E)


def evaluate(doc: dict) -> dict:
    b = doc["observational_or_published_bindings"]
    B_min_T = float(b["B"]["min"]) * 1e-4
    B_max_T = float(b["B"]["max"]) * 1e-4
    T_min = float(b["T_e"]["min"])
    T_max = float(b["T_e"]["max"])
    ne_min_m3 = float(b["n_e"]["min"]) * 1e6
    ne_max_m3 = float(b["n_e"]["max"]) * 1e6

    rho_min_kg_m3 = ne_min_m3 * M_P
    rho_max_kg_m3 = ne_max_m3 * M_P
    rho_min_g_cm3 = rho_min_kg_m3 * 1e-3
    rho_max_g_cm3 = rho_max_kg_m3 * 1e-3

    ef_max = fermi_energy_nr_joule(ne_max_m3)
    theta_deg_min = K_B * T_min / ef_max

    chi_spin_min = MU_B * B_min_T / (K_B * T_max)
    chi_spin_max = MU_B * B_max_T / (K_B * T_min)
    omega_c_min = E_CHARGE * B_min_T / M_E
    omega_c_max = E_CHARGE * B_max_T / M_E
    chi_L_min = HBAR * omega_c_min / (K_B * T_max)
    chi_L_max = HBAR * omega_c_max / (K_B * T_min)
    bq_min = B_min_T / B_Q
    bq_max = B_max_T / B_Q

    pyc_ref = float(doc["domain_references"]["pycnonuclear_density_lower_reference"]["value"])
    pyc_gap_min = pyc_ref / rho_max_g_cm3

    regimes = {
        "ionized_plasma": {
            "state": "APPLICABLE",
            "rationale": "Published EHT development models describe hot ionized emitting plasma; T_e is 1e10--1.2e11 K.",
        },
        "MAD_reconnection": {
            "state": "APPLICABLE",
            "rationale": "MAD is supported as a viable/favored GRMHD model family by EHT polarimetric comparisons; reconnection timescale itself remains unresolved.",
        },
        "pair_relevant": {
            "state": TOKEN,
            "rationale": "T_e can exceed m_e c^2/k_B, but compactness, pair balance and source size are not frozen; pair dominance cannot be inferred from temperature alone.",
        },
        "electron_degenerate": {
            "state": "OUT_OF_DOMAIN",
            "rationale": f"Minimum kT/E_F over the sourced n_e,T_e box is {theta_deg_min:.3e} >> 1.",
        },
        "electron_capture": {
            "state": TOKEN,
            "rationale": "Composition, ion temperature and weak-interaction rate network are not frozen; thermal electron energy alone is insufficient to promote this channel.",
        },
        "nuclear_network": {
            "state": TOKEN,
            "rationale": "No source-bound ion composition/temperature or nuclear reaction network has been frozen.",
        },
        "pycnonuclear": {
            "state": "OUT_OF_DOMAIN",
            "rationale": f"Pure-H density proxy upper bound is {rho_max_g_cm3:.3e} g/cm^3; reference pycnonuclear crust scale is ~1e12 g/cm^3, a gap >= {pyc_gap_min:.3e}.",
        },
        "spin_Landau_QED": {
            "state": "OUT_OF_DOMAIN",
            "rationale": f"max chi_spin={chi_spin_max:.3e}, max chi_L={chi_L_max:.3e}, max B/B_Q={bq_max:.3e}; all are far below unity.",
        },
    }

    return {
        "schema": "rll.sgpt.m87.source-regime-execution-receipt/v1",
        "status": "PARTIAL_REGIME_EXECUTION_EVIDENCE_BOUND",
        "source": "M87*",
        "input_evidence": str(DEFAULT_EVIDENCE.relative_to(ROOT)),
        "source_values": {
            "M_Msun": b["M"]["value"],
            "dot_M_Msun_per_yr": [b["dot_M"]["min"], b["dot_M"]["max"]],
            "B_G": [b["B"]["min"], b["B"]["max"]],
            "T_e_K": [b["T_e"]["min"], b["T_e"]["max"]],
            "n_e_cm3": [b["n_e"]["min"], b["n_e"]["max"]],
            "a_star": TOKEN,
            "T_i": TOKEN,
            "Y_e": TOKEN,
            "compactness": TOKEN,
        },
        "derived_diagnostics": {
            "rho_proxy_pure_H_kg_m3": [rho_min_kg_m3, rho_max_kg_m3],
            "rho_proxy_pure_H_g_cm3": [rho_min_g_cm3, rho_max_g_cm3],
            "fermi_energy_max_eV": ef_max / EV,
            "theta_deg_min_kT_over_EF": theta_deg_min,
            "chi_spin_range": [chi_spin_min, chi_spin_max],
            "chi_L_range": [chi_L_min, chi_L_max],
            "B_over_B_Q_range": [bq_min, bq_max],
            "pycnonuclear_density_gap_min_factor": pyc_gap_min,
        },
        "regimes": regimes,
        "scientific_boundaries": {
            "model_inferred_ranges_are_direct_measurements": False,
            "MAD_applicability_proves_reconnection_rate": False,
            "pair_dominance_claimed": False,
            "nuclear_network_claimed": False,
            "SGPT_validated": False,
            "claim_allowed": False,
        },
    }


def validate_receipt(r: dict) -> None:
    require(r["status"] == "PARTIAL_REGIME_EXECUTION_EVIDENCE_BOUND", "status drift")
    require(r["regimes"]["ionized_plasma"]["state"] == "APPLICABLE", "plasma applicability lost")
    require(r["regimes"]["electron_degenerate"]["state"] == "OUT_OF_DOMAIN", "degeneracy boundary lost")
    require(r["regimes"]["pycnonuclear"]["state"] == "OUT_OF_DOMAIN", "pycnonuclear boundary lost")
    require(r["regimes"]["spin_Landau_QED"]["state"] == "OUT_OF_DOMAIN", "spin/QED boundary lost")
    require(r["regimes"]["pair_relevant"]["state"] == TOKEN, "pair state must remain unresolved")
    require(r["regimes"]["nuclear_network"]["state"] == TOKEN, "nuclear network must remain unresolved")
    d = r["derived_diagnostics"]
    require(d["theta_deg_min_kT_over_EF"] > 1e12, "degeneracy margin unexpectedly small")
    require(d["B_over_B_Q_range"][1] < 1e-10, "strong-QED margin unexpectedly small")
    require(d["chi_spin_range"][1] < 1e-10, "spin thermal-ordering margin unexpectedly small")
    require(d["chi_L_range"][1] < 1e-10, "Landau thermal-smearing margin unexpectedly small")
    require(d["pycnonuclear_density_gap_min_factor"] > 1e20, "pycnonuclear density separation unexpectedly small")
    require(r["scientific_boundaries"]["claim_allowed"] is False, "claim boundary weakened")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--evidence", type=Path, default=DEFAULT_EVIDENCE)
    p.add_argument("--receipt", type=Path)
    args = p.parse_args()
    doc = load(args.evidence)
    receipt = evaluate(doc)
    validate_receipt(receipt)
    text = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.receipt:
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
