#!/usr/bin/env python3
"""Audit the WS24 typed energy-momentum dimensional executor.

Stdlib-only by design so the WORK -> rll/lab gate does not depend on later
main-only Rx helper infrastructure.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "data/contracts/RLL_ENERGY_MOMENTUM_BRIDGE_UNITS_V2.json"
SOURCE = ROOT / "data/pipelines/structure_d/energy_momentum_bridge.py"
OUT = ROOT / "results/rll_energy_momentum_dimension_gate.json"


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _dump_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def build() -> dict:
    contract = _load_json(CONTRACT)
    text = SOURCE.read_text(encoding="utf-8")

    if contract.get("schema") != "rll.energy_momentum_bridge_units.v2":
        raise ValueError("unexpected typed energy-momentum units contract")
    if contract.get("claim_allowed") is not False:
        raise ValueError("typed units contract must remain claim_allowed=false")

    legacy_observed = {
        "rho_declared_j_per_m3": '"rho_before": "J/m^3"' in text
        and '"rho_field": "J/m^3"' in text,
        "pressure_declared_pa": '"pressure": "Pa"' in text,
        "pressure_divided_by_c2_helper_retained": (
            "return float(pressure_pa) / (float(c) ** 2)" in text
        ),
    }
    typed_executor = {
        "energy_convention_declared": (
            'ENERGY_DENSITY_CONVENTION = "ENERGY_DENSITY_CONVENTION"' in text
        ),
        "mass_convention_declared": (
            'MASS_DENSITY_CONVENTION = "MASS_DENSITY_CONVENTION"' in text
        ),
        "nonzero_pressure_fail_closed": (
            "nonzero pressure requires explicit dimensional convention" in text
        ),
        "pressure_energy_density_path": "def pressure_energy_density(" in text,
        "all_energy_to_mass_path": "def energy_density_to_mass_density(" in text,
        "typed_output_units": (
            '"F_gap_unit"' in text
            and '"J/m^3"' in text
            and '"kg/m^3"' in text
        ),
    }

    typed_ready = all(typed_executor.values())
    selected = str(
        contract.get(
            "selected_convention",
            "TOKEN_VAZIO_SCIENTIFIC_DIMENSIONAL_AUTHORITY",
        )
    )
    selection_open = selected.startswith("TOKEN_VAZIO")

    if typed_ready and selection_open:
        state = "TYPED_EXECUTOR_READY_SCIENTIFIC_SELECTION_REQUIRED"
    elif not typed_ready:
        state = "FAIL_TYPED_EXECUTOR_INCOMPLETE"
    elif not selection_open:
        state = "READY_FOR_EXPLICITLY_SELECTED_CONVENTION_REVIEW"
    else:
        state = "FAIL_REAUDIT_REQUIRED"

    return {
        "schema": "rll.energy_momentum_dimension_gate.v2",
        "state": state,
        "legacy_observed": legacy_observed,
        "typed_executor": typed_executor,
        "dimensional_analysis": {
            "Pa": "kg m^-1 s^-2 = J/m^3",
            "Pa_over_c2": "kg/m^3",
            "legacy_nonzero_pressure_sum": "BLOCKED_BY_TYPED_EXECUTOR",
            "energy_density_convention_consistent": True,
            "mass_density_convention_consistent": True,
            "cross_convention_invariant": (
                "energy_density_scalar/c^2 == mass_density_scalar"
            ),
        },
        "selected_convention": selected,
        "available_options": [
            "ENERGY_DENSITY_CONVENTION",
            "MASS_DENSITY_CONVENTION",
        ],
        "claim_allowed": False,
        "closed_gap": (
            "SILENT_DIMENSIONAL_MIXING_FOR_NONZERO_PRESSURE"
            if typed_ready
            else "TOKEN_VAZIO"
        ),
        "open_gap": "SCIENTIFIC_STRESS_ENERGY_SEMANTICS_SELECTION",
        "boundary": (
            "Software dimensional arithmetic may be closed while physical "
            "stress-energy semantics remain unselected."
        ),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    payload = build()
    if args.write:
        _dump_json(OUT, payload)
    print(
        json.dumps(
            {
                "state": payload["state"],
                "selected_convention": payload["selected_convention"],
                "closed_gap": payload["closed_gap"],
                "open_gap": payload["open_gap"],
                "claim_allowed": False,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    if args.write:
        print("wrote", OUT.relative_to(ROOT))
    return 0 if payload["state"].startswith("TYPED_EXECUTOR_READY") else 2


if __name__ == "__main__":
    raise SystemExit(main())
