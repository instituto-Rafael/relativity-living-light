#!/usr/bin/env python3
"""Classify M87* process-timescale readiness without inventing rate laws.

The preregistered registry stays immutable/unresolved. This executor consumes
source evidence plus the executed source-regime receipt and emits only a
readiness receipt. It computes gravitational units from the sourced mass but
never substitutes them for process-specific tau_i.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "evidence" / "m87" / "source_state_evidence.v1.json"
REGISTRY = ROOT / "data" / "contracts" / "m87" / "process_timescale_registry.v1.json"
TOKEN = "TOKEN_VAZIO"

G = 6.67430e-11
C = 299_792_458.0
M_SUN = 1.98847e30


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate(source: dict, registry: dict) -> dict:
    require(source.get("claim_allowed") is False, "source claim boundary weakened")
    require(registry.get("claim_allowed") is False, "timescale registry claim boundary weakened")
    require(registry.get("status") == "LOCKED_UNRESOLVED", "preregistered timescale registry must remain locked/unresolved")
    for name, process in registry.get("processes", {}).items():
        for field in ("tau", "units", "rate_model", "source", "domain", "receipt"):
            require(process.get(field) == TOKEN, f"{name}.{field} was filled outside a source-bound execution receipt")

    m_msun = float(source["observational_or_published_bindings"]["M"]["value"])
    m_kg = m_msun * M_SUN
    r_g_m = G * m_kg / C**2
    t_g_s = G * m_kg / C**3

    readiness = {
        "inflow": {
            "state": "TOKEN_VAZIO_GEOMETRY_AND_RADIAL_VELOCITY_NOT_FROZEN",
            "requires": ["source_radius_or_radial_grid", "v_r_or_GRMHD_trajectory"],
            "tau_filled": False,
        },
        "outflow": {
            "state": "TOKEN_VAZIO_OUTFLOW_GEOMETRY_AND_VELOCITY_NOT_FROZEN",
            "requires": ["outflow_launch_region", "velocity_field"],
            "tau_filled": False,
        },
        "cooling": {
            "state": "TOKEN_VAZIO_ENERGY_DENSITY_AND_COOLING_FUNCTION_NOT_FROZEN",
            "requires": ["internal_energy_or_enthalpy", "emissivity_absorption_Compton_closure"],
            "tau_filled": False,
        },
        "heating": {
            "state": "TOKEN_VAZIO_DISSIPATION_AND_ELECTRON_HEATING_PARTITION_NOT_FROZEN",
            "requires": ["dissipation_model", "electron_ion_heating_partition"],
            "tau_filled": False,
        },
        "Alfven": {
            "state": "TOKEN_VAZIO_RELATIVISTIC_ENTHALPY_AND_LENGTH_SCALE_NOT_FROZEN",
            "requires": ["relativistic_enthalpy", "field_geometry_length_scale"],
            "tau_filled": False,
        },
        "reconnection": {
            "state": "TOKEN_VAZIO_CURRENT_SHEET_SCALE_AND_RECONNECTION_RATE_NOT_FROZEN",
            "requires": ["current_sheet_length", "v_A", "reconnection_rate_or_resistive_kinetic_closure"],
            "tau_filled": False,
        },
        "ionization": {
            "state": "NOT_REQUIRED_FOR_BASELINE_STATE_ALREADY_MODELED_AS_HOT_IONIZED_PLASMA",
            "requires": [],
            "tau_filled": False,
            "boundary": "A transient ionization calculation would require a separate nonequilibrium-ionization preregistration."
        },
        "pair_creation": {
            "state": "TOKEN_VAZIO_COMPACTNESS_PHOTON_FIELD_AND_PAIR_BALANCE_NOT_FROZEN",
            "requires": ["compactness", "photon_distribution", "source_size", "pair_kinetic_closure"],
            "tau_filled": False,
        },
        "pair_annihilation": {
            "state": "TOKEN_VAZIO_PAIR_DENSITY_AND_DISTRIBUTION_NOT_FROZEN",
            "requires": ["n_e_plus", "n_e_minus", "pair_distribution"],
            "tau_filled": False,
        },
        "nuclear": {
            "state": "TOKEN_VAZIO_ION_TEMPERATURE_COMPOSITION_AND_NETWORK_NOT_FROZEN",
            "requires": ["T_i", "composition_or_Y_e", "nuclear_network"],
            "tau_filled": False,
        },
        "electron_capture": {
            "state": "TOKEN_VAZIO_COMPOSITION_CHEMICAL_POTENTIAL_AND_WEAK_NETWORK_NOT_FROZEN",
            "requires": ["composition", "electron_chemical_potential", "weak_rate_network"],
            "tau_filled": False,
        },
        "phase_change": {
            "state": "NOT_REQUIRED_FOR_CONVENTIONAL_SOLID_LIQUID_GAS_BASELINE_HOT_PLASMA",
            "requires": [],
            "tau_filled": False,
            "boundary": "Any plasma phase transition or critical phenomenon would require its own EOS/order-parameter definition."
        },
        "collisional_thermalization": {
            "state": "TOKEN_VAZIO_SPECIES_TEMPERATURES_COMPOSITION_AND_COLLISION_CLOSURE_NOT_FROZEN",
            "requires": ["T_i", "composition", "Coulomb_log_or_collision_operator"],
            "tau_filled": False,
        },
    }

    require(set(readiness) == set(registry["processes"]), "readiness process set drift")
    require(not any(v["tau_filled"] for v in readiness.values()), "no process-specific tau may be fabricated")

    return {
        "schema": "rll.sgpt.m87.timescale-readiness-receipt/v1",
        "status": "PASS_TIMESCALE_READINESS_NO_PROCESS_RATE_PROMOTION",
        "source": "M87*",
        "source_mass_Msun": m_msun,
        "derived_gravitational_units": {
            "r_g_m": r_g_m,
            "t_g_s": t_g_s,
            "t_g_hours": t_g_s / 3600.0,
            "boundary": "r_g and t_g are gravitational units derived from M, not process-specific timescales."
        },
        "process_readiness": readiness,
        "Da_i_execution": "TOKEN_VAZIO_NO_PROCESS_HAS_BOTH_TAU_RESIDENCE_AND_TAU_I_FROZEN",
        "G4_baseline": "TOKEN_VAZIO",
        "scientific_validation": "TOKEN_VAZIO",
        "claim_allowed": False,
    }


def validate(receipt: dict) -> None:
    require(receipt["status"] == "PASS_TIMESCALE_READINESS_NO_PROCESS_RATE_PROMOTION", "status drift")
    require(receipt["Da_i_execution"].startswith("TOKEN_VAZIO"), "Da_i cannot be promoted yet")
    require(receipt["G4_baseline"] == TOKEN, "G4 cannot be promoted")
    require(receipt["scientific_validation"] == TOKEN, "scientific validation cannot be promoted")
    require(receipt["claim_allowed"] is False, "claim boundary weakened")
    require(receipt["process_readiness"]["reconnection"]["tau_filled"] is False, "reconnection tau fabricated")
    require(receipt["process_readiness"]["pair_creation"]["tau_filled"] is False, "pair tau fabricated")
    require(receipt["process_readiness"]["nuclear"]["tau_filled"] is False, "nuclear tau fabricated")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--source", type=Path, default=SOURCE)
    p.add_argument("--registry", type=Path, default=REGISTRY)
    p.add_argument("--receipt", type=Path)
    args = p.parse_args()
    receipt = evaluate(read(args.source), read(args.registry))
    validate(receipt)
    text = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.receipt:
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
