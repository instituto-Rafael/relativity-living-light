#!/usr/bin/env python3
"""Audit Structure-D energy-momentum bridge dimensional consistency."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from rx.kernel import dump_json, load_json

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "data/contracts/RLL_ENERGY_MOMENTUM_BRIDGE_UNITS_V1.json"
SOURCE = ROOT / "data/pipelines/structure_d/energy_momentum_bridge.py"
OUT = ROOT / "results/rll_energy_momentum_dimension_gate.json"


def build():
    contract = load_json(CONTRACT)
    text = SOURCE.read_text(encoding="utf-8")
    if contract.get("schema") != "rll.energy_momentum_bridge_units.v1":
        raise ValueError("unexpected energy-momentum units contract")
    if contract.get("claim_allowed") is not False:
        raise ValueError("units contract must remain claim_allowed=false")

    observed = {
        "rho_declared_j_per_m3": '"rho_before": "J/m^3"' in text and '"rho_field": "J/m^3"' in text,
        "pressure_declared_pa": '"pressure": "Pa"' in text,
        "pressure_divided_by_c2": "return float(pressure_pa) / (float(c) ** 2)" in text,
        "pressure_density_added_to_energy_terms": "pressure_density(float(pressure), c)" in text,
    }
    mixed = all(observed.values())
    selected = str(contract.get("selected_convention", "TOKEN_VAZIO"))
    selected_terminal = not selected.startswith("TOKEN_VAZIO")

    state = (
        "BLOCKED_DIMENSIONAL_AUTHORITY_REQUIRED"
        if mixed and not selected_terminal
        else "READY_FOR_VERSIONED_MIGRATION"
        if selected_terminal
        else "FAIL_OBSERVED_IMPLEMENTATION_CHANGED_REAUDIT_REQUIRED"
    )
    return {
        "schema": "rll.energy_momentum_dimension_gate.v1",
        "state": state,
        "observed": observed,
        "dimensional_analysis": {
            "Pa": "kg m^-1 s^-2 = J/m^3",
            "Pa_over_c2": "kg/m^3",
            "rho_declared": "J/m^3",
            "current_sum_consistent": False if mixed else "TOKEN_VAZIO_REAUDIT"
        },
        "selected_convention": selected,
        "available_options": [row["id"] for row in contract.get("options", [])],
        "claim_allowed": False,
        "boundary": "The gate identifies dimensional inconsistency and admissible conventions. It does not choose which stress-energy quantity the author intends."
    }


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    payload = build()
    if args.write:
        dump_json(OUT, payload)
    print(json.dumps({
        "state": payload["state"],
        "selected_convention": payload["selected_convention"],
        "claim_allowed": False
    }, ensure_ascii=False, indent=2))
    if args.write:
        print("wrote", OUT.relative_to(ROOT))
    return 0 if payload["state"] != "FAIL_OBSERVED_IMPLEMENTATION_CHANGED_REAUDIT_REQUIRED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
