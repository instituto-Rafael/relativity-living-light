#!/usr/bin/env python3
"""Deterministic reference evaluator for RLL stratified-reservoir/aurora bridge.

This module validates mathematical witnesses only. It does not ingest Lake Nyos,
Juno, Climate Engine, or auroral instrument data and cannot promote a physical claim.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path

G = 9.80665
P0 = 101_325.0
RHO_WATER = 1000.0
H = 6.62607015e-34
C = 299_792_458.0
E_CHARGE = 1.602176634e-19


def hydrostatic_pressure(depth_m: float, rho: float = RHO_WATER, p0: float = P0) -> float:
    if depth_m < 0 or rho <= 0 or p0 <= 0:
        raise ValueError("depth must be >=0 and rho,p0 >0")
    return p0 + rho * G * depth_m


def saturation_ratio(dissolved: float, saturation: float) -> float:
    if dissolved < 0 or saturation <= 0:
        raise ValueError("dissolved must be >=0 and saturation >0")
    return dissolved / saturation


def stable_stratification(n2_s2: float) -> bool:
    return n2_s2 > 0.0


def photon_energy_ev(wavelength_nm: float) -> float:
    if wavelength_nm <= 0:
        raise ValueError("wavelength must be >0")
    return H * C / (wavelength_nm * 1e-9) / E_CHARGE


def synthetic_receipt() -> dict:
    p_200 = hydrostatic_pressure(200.0)
    green = photon_energy_ev(557.7)
    red = photon_energy_ev(630.0)
    return {
        "schema": "rll.stratified_reservoir_aurora.reference_receipt.v1",
        "claim_allowed": False,
        "input_class": "SYNTHETIC_REFERENCE_ONLY",
        "witnesses": {
            "hydrostatic_pressure_200m_pa": p_200,
            "hydrostatic_pressure_monotonic": hydrostatic_pressure(201.0) > p_200,
            "supersaturation_example": saturation_ratio(1.05, 1.0) > 1.0,
            "stable_n2_example": stable_stratification(1e-4),
            "oxygen_557_7nm_energy_ev": green,
            "oxygen_630_0nm_energy_ev": red,
            "shorter_wavelength_higher_energy": green > red,
        },
        "boundaries": [
            "SYNTHETIC_REFERENCE != OBSERVATION",
            "STRUCTURAL_ANALOGY != MECHANISM_EQUIVALENCE",
            "LAKE_DEGASSING != AURORA",
            "PHOTON_WITNESS != RLL_COSMOLOGY_VALIDATION",
        ],
        "gaps": [
            "TOKEN_VAZIO_LAKE_PROFILE_DATA",
            "TOKEN_VAZIO_AURORAL_PARTICLE_FIELD_DATA",
            "TOKEN_VAZIO_CROSS_DOMAIN_FIT",
            "TOKEN_VAZIO_INDEPENDENT_REPRODUCTION",
        ],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path)
    ns = ap.parse_args()
    receipt = synthetic_receipt()
    text = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if ns.output:
        ns.output.parent.mkdir(parents=True, exist_ok=True)
        ns.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
