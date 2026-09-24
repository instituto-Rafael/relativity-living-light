"""Fail-closed Dark Dimension benchmark primitives for RLL.

This module is intentionally small and stdlib-only.  It does not implement the
full Dark Dimension cosmology or a DESI/SN likelihood.  Its job is to expose
model-independent routing diagnostics that can be tested before any comparator
is admitted to the canonical RLL model tournament.

SOURCE != IMPLEMENTATION != EXECUTION != EVIDENCE != CLAIM.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any, Dict


CLAIM_ALLOWED = False


@dataclass(frozen=True)
class DimensionRegime:
    chi: float
    state: str
    interpretation: str
    claim_allowed: bool = False


def _positive_finite(name: str, value: float) -> float:
    value = float(value)
    if not isfinite(value) or value <= 0.0:
        raise ValueError(f"{name} must be positive and finite")
    return value


def dimensionless_crossover_ratio(r_h_m: float, compact_radius_m: float) -> float:
    """Return chi = r_h / R_perp using any common length unit.

    The caller is responsible for supplying a horizon scale appropriate to the
    physical model.  This function does not infer a Schwarzschild/Kerr radius.
    """
    r_h = _positive_finite("r_h_m", r_h_m)
    radius = _positive_finite("compact_radius_m", compact_radius_m)
    return r_h / radius


def classify_dimension_regime(
    r_h_m: float,
    compact_radius_m: float,
    *,
    separation_factor: float = 10.0,
) -> DimensionRegime:
    """Classify only asymptotic regimes; keep the order-one crossover unresolved.

    separation_factor avoids pretending that chi ~= 1 has a universal sharp
    threshold.  The actual transition depends on the full higher-dimensional
    solution and Gregory-Laflamme stability analysis.
    """
    factor = _positive_finite("separation_factor", separation_factor)
    if factor <= 1.0:
        raise ValueError("separation_factor must be > 1")

    chi = dimensionless_crossover_ratio(r_h_m, compact_radius_m)
    if chi >= factor:
        return DimensionRegime(
            chi=chi,
            state="EFFECTIVE_4D_ASYMPTOTIC",
            interpretation="horizon scale is much larger than compactification scale",
        )
    if chi <= 1.0 / factor:
        return DimensionRegime(
            chi=chi,
            state="FIVE_D_SENSITIVE_ASYMPTOTIC",
            interpretation="horizon scale is much smaller than compactification scale",
        )
    return DimensionRegime(
        chi=chi,
        state="CROSSOVER_TOKEN_VAZIO",
        interpretation=(
            "order-one scale ratio; full model-specific higher-dimensional "
            "stability calculation required"
        ),
    )


def gregory_laflamme_mass_ratio(pbh_mass: float, gl_threshold_mass: float) -> float:
    """Return M_PBH / M_GL without assigning a universal threshold constant."""
    mass = _positive_finite("pbh_mass", pbh_mass)
    threshold = _positive_finite("gl_threshold_mass", gl_threshold_mass)
    return mass / threshold


def build_benchmark_receipt(
    *,
    r_h_m: float,
    compact_radius_m: float,
    separation_factor: float = 10.0,
) -> Dict[str, Any]:
    regime = classify_dimension_regime(
        r_h_m,
        compact_radius_m,
        separation_factor=separation_factor,
    )
    return {
        "schema": "rll.dark_dimension_benchmark.receipt.v1",
        "benchmark": "DARK_DIMENSION_BENCHMARK_V1",
        "chi": regime.chi,
        "regime_state": regime.state,
        "interpretation": regime.interpretation,
        "structural_limit_tested": True,
        "likelihood_parity": "TOKEN_VAZIO_NOT_EXECUTED",
        "desi_dr2_sn_fit": "TOKEN_VAZIO_NOT_EXECUTED",
        "rll_plus_dark_dimension": "BLOCKED_UNTIL_G5_PARITY",
        "claim_allowed": False,
        "boundary": (
            "This receipt proves only deterministic routing of asymptotic "
            "dimension regimes. It is not observational evidence for a dark "
            "dimension, PBHs, or RLL."
        ),
    }
