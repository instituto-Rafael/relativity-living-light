"""Fail-closed spatial/physical regime router for the Rx Execution Fabric.

The router classifies only from declared context. It never infers a physical
mechanism from numerical fit quality.
"""
from __future__ import annotations

REGIME_NAMES = {
    "G0": "euclidean_local_diagnostic",
    "G1": "newtonian_nbody_weak_field",
    "G2": "post_newtonian_relativistic_local",
    "G3": "strong_gravity",
    "G4": "plasma_mhd_grmhd",
    "G5": "cosmological_flrw_background",
    "G6": "observation_projection",
}


def _yes(value):
    return value is True or str(value).strip().lower() in {"1", "true", "yes", "on"}


def _text(value):
    return str(value or "").strip().lower()


def _finite_number(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if number != number or number in (float("inf"), float("-inf")):
        return None
    return number


def classify_region(region):
    if not isinstance(region, dict):
        raise ValueError("region must be a mapping")

    domain = _text(region.get("domain"))
    metric = _text(region.get("metric_or_approximation"))
    reasons = {}
    regimes = []

    thresholds = region.get("thresholds") or {}
    if not isinstance(thresholds, dict):
        raise ValueError("region.thresholds must be a mapping")

    gm_over_rc2 = _finite_number(region.get("gm_over_rc2"))
    v_over_c = _finite_number(region.get("v_over_c"))
    weak_g_limit = float(thresholds.get("weak_field_gm_over_rc2_max", 1.0e-2))
    weak_v_limit = float(thresholds.get("weak_field_v_over_c_max", 1.0e-2))

    explicit_g0 = _yes(region.get("euclidean_local_diagnostic"))
    weak_numeric = (
        gm_over_rc2 is not None
        and v_over_c is not None
        and gm_over_rc2 < weak_g_limit
        and v_over_c < weak_v_limit
    )
    weak = _yes(region.get("weak_field")) or weak_numeric
    post_newtonian = _yes(region.get("post_newtonian"))
    strong = _yes(region.get("strong_gravity")) or metric in {
        "schwarzschild", "kerr", "numerical_relativity", "strong_gravity"
    }
    plasma = (
        _yes(region.get("plasma"))
        or _yes(region.get("mhd"))
        or _yes(region.get("grmhd"))
        or domain in {"plasma", "mhd", "grmhd"}
    )
    cosmological = (
        _yes(region.get("cosmological"))
        or domain in {"cosmology", "cosmological"}
        or metric in {"flrw", "friedmann-lemaitre-robertson-walker"}
        or _text(region.get("characteristic_scale")) == "cosmological"
    )
    projection = (
        _yes(region.get("observational_projection"))
        or bool(region.get("line_of_sight"))
        or bool(region.get("selection_function"))
        or bool(region.get("instrument"))
    )

    if explicit_g0:
        regimes.append("G0")
        reasons["G0"] = "explicit euclidean local diagnostic"
    if weak:
        regimes.append("G1")
        reasons["G1"] = (
            "explicit weak-field flag"
            if _yes(region.get("weak_field"))
            else "declared GM/(rc^2) and v/c are below declared weak-field thresholds"
        )
    if post_newtonian:
        regimes.append("G2")
        reasons["G2"] = "explicit post-Newtonian regime"
    if strong:
        regimes.append("G3")
        reasons["G3"] = "explicit strong-gravity context or declared strong-gravity metric"
    if plasma:
        regimes.append("G4")
        reasons["G4"] = "declared plasma/MHD/GRMHD context"
    if cosmological:
        regimes.append("G5")
        reasons["G5"] = "declared cosmological/FLRW context"
    if projection:
        regimes.append("G6")
        reasons["G6"] = "declared observational projection/selection/instrument context"

    if not regimes:
        regimes.append("G0")
        reasons["G0"] = "no stronger physical regime was declared; diagnostic-only fallback"

    requested_primary = str(region.get("primary_regime") or "").upper()
    if requested_primary:
        if requested_primary not in regimes:
            raise ValueError(
                "declared primary_regime %s is not supported by declared context" % requested_primary
            )
        primary = requested_primary
    else:
        primary = next(
            (candidate for candidate in ("G5", "G4", "G3", "G2", "G1", "G0") if candidate in regimes),
            "G0",
        )

    return {
        "schema": "rll.rx.region_classification.v1",
        "regime_namespace": "REGIME",
        "regimes": regimes,
        "qualified_regimes": ["REGIME:" + key for key in regimes],
        "primary_regime": primary,
        "qualified_primary_regime": "REGIME:" + primary,
        "projection_wrapper": "G6" in regimes,
        "regime_names": {key: REGIME_NAMES[key] for key in regimes},
        "reasons": reasons,
        "declared_diagnostics": {
            "gm_over_rc2": gm_over_rc2,
            "v_over_c": v_over_c,
            "weak_field_gm_over_rc2_max": weak_g_limit,
            "weak_field_v_over_c_max": weak_v_limit,
        },
        "boundary": (
            "Classification expresses declared applicability only; it is not evidence "
            "that a physical mechanism is true."
        ),
        "claim_allowed": False,
    }
