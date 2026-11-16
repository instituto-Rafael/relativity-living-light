"""Dispersion/covariance routing for the Rx Execution Fabric."""
from __future__ import annotations

_ALLOWED_MODES = {
    "full",
    "diagonal",
    "dataset_contract",
    "none",
    "TOKEN_VAZIO",
}

_OPERATOR = {
    "full": "full_covariance_quadratic_form",
    "diagonal": "diagonal_chi2",
    "dataset_contract": "dataset_declared_covariance_operator",
    "none": "descriptive_only_no_likelihood",
    "TOKEN_VAZIO": "TOKEN_VAZIO_OPERATOR",
}


def route_dispersion(context):
    if not isinstance(context, dict):
        raise ValueError("dispersion must be a mapping")

    mode = str(context.get("covariance_mode", "TOKEN_VAZIO"))
    if mode not in _ALLOWED_MODES:
        raise ValueError("unsupported covariance_mode: %s" % mode)

    correlation_flags = {
        "heteroscedasticity": bool(context.get("heteroscedasticity", False)),
        "spatial_correlation": bool(context.get("spatial_correlation", False)),
        "temporal_correlation": bool(context.get("temporal_correlation", False)),
        "anisotropy": bool(context.get("anisotropy", False)),
        "outliers": bool(context.get("outliers", False)),
        "measurement_error": bool(context.get("measurement_error", False)),
        "selection_function": bool(context.get("selection_function", False)),
    }

    blocked = []
    if mode == "diagonal" and (
        correlation_flags["spatial_correlation"]
        or correlation_flags["temporal_correlation"]
    ):
        blocked.append("diagonal_covariance_forbidden_when_declared_correlations_exist")

    readiness = "ROUTABLE"
    if mode == "TOKEN_VAZIO":
        readiness = "BLOCKED_TOKEN_VAZIO"
        blocked.append("covariance_mode_not_declared")
    elif blocked:
        readiness = "BLOCKED_CONTRACT"

    return {
        "schema": "rll.rx.dispersion_context.v1",
        "covariance_mode": mode,
        "operator": _OPERATOR[mode],
        "distribution": str(context.get("distribution", "TOKEN_VAZIO")),
        "correlation_flags": correlation_flags,
        "readiness": readiness,
        "blocked_reasons": blocked,
        "boundary": (
            "Covariance routing is selected from declared data structure, never from "
            "which operator gives a preferred scientific result."
        ),
        "claim_allowed": False,
    }
