"""Fail-closed latent-population/transport dispersion layer for RLL.

This module does not add physical parameters to the canonical likelihood by itself.
It validates a hypothesis context and reports which declared parameters are
source-bound enough to enter a later preregistered experiment.
"""
from __future__ import annotations


_REQUIRED_LATENTS = (
    "origin",
    "age",
    "velocity",
    "residence_time",
    "transport_history",
)

_REQUIRED_PARAMETER_FIELDS = (
    "id",
    "domain",
    "unit",
    "state",
    "source_ref",
    "prior",
    "falsifier",
)

_ALLOWED_STATES = {
    "MEASURED",
    "SOURCE_BOUND",
    "MODEL_DEFINED",
    "HYPOTHESIS",
    "TOKEN_VAZIO",
}

_ALLOWED_COVARIANCE = {
    "full",
    "dataset_contract",
    "diagonal",
    "none",
    "TOKEN_VAZIO",
}


def _present(value):
    return value not in (None, "", "TOKEN_VAZIO", "TOKEN_VAZIO_SOURCE")


def _validate_parameter(row):
    if not isinstance(row, dict):
        raise ValueError("each parameter must be a mapping")
    missing = [name for name in _REQUIRED_PARAMETER_FIELDS if name not in row]
    if missing:
        raise ValueError("parameter missing fields: %s" % ",".join(missing))
    state = str(row["state"])
    if state not in _ALLOWED_STATES:
        raise ValueError("unsupported parameter state: %s" % state)

    gate_fields = ("unit", "source_ref", "prior", "falsifier")
    gate_ok = state in {"MEASURED", "SOURCE_BOUND", "MODEL_DEFINED"} and all(
        _present(row.get(name)) for name in gate_fields
    )
    return {
        "id": str(row["id"]),
        "domain": str(row["domain"]),
        "state": state,
        "gate_ok": bool(gate_ok),
        "blocked_reasons": [] if gate_ok else [
            "parameter_not_source_bound_or_missing_unit_prior_falsifier"
        ],
    }


def route_population_dispersion(context):
    """Validate a latent population/transport hypothesis without promoting claims."""
    if not isinstance(context, dict):
        raise ValueError("population_dispersion must be a mapping")

    enabled = bool(context.get("enabled", False))
    if not enabled:
        return {
            "schema": "rll.rx.population_dispersion.v1",
            "state": "NOT_APPLICABLE",
            "readiness": "NOT_APPLICABLE",
            "claim_allowed": False,
        }

    covariance_mode = str(context.get("covariance_mode", "TOKEN_VAZIO"))
    if covariance_mode not in _ALLOWED_COVARIANCE:
        raise ValueError("unsupported covariance_mode: %s" % covariance_mode)

    latents = context.get("latents") or {}
    if not isinstance(latents, dict):
        raise ValueError("latents must be a mapping")
    latent_state = {
        name: str(latents.get(name, "TOKEN_VAZIO"))
        for name in _REQUIRED_LATENTS
    }

    populations = context.get("populations") or []
    if not isinstance(populations, list):
        raise ValueError("populations must be a list")

    parameters = context.get("parameters") or []
    if not isinstance(parameters, list):
        raise ValueError("parameters must be a list")
    parameter_rows = [_validate_parameter(row) for row in parameters]

    source_bound_ids = [row["id"] for row in parameter_rows if row["gate_ok"]]
    blocked_parameter_ids = [row["id"] for row in parameter_rows if not row["gate_ok"]]

    flags = {
        "age_mixture": bool(context.get("age_mixture", False)),
        "origin_mixture": bool(context.get("origin_mixture", False)),
        "velocity_mixture": bool(context.get("velocity_mixture", False)),
        "residence_or_capture": bool(context.get("residence_or_capture", False)),
        "intervening_medium": bool(context.get("intervening_medium", False)),
        "projection_effects": bool(context.get("projection_effects", False)),
        "selection_function": bool(context.get("selection_function", False)),
    }

    blocked = []
    if len(populations) < 2 and any(
        (flags["age_mixture"], flags["origin_mixture"], flags["velocity_mixture"])
    ):
        blocked.append("mixture_declared_without_at_least_two_population_components")
    if covariance_mode == "TOKEN_VAZIO":
        blocked.append("covariance_mode_not_declared")
    if covariance_mode == "diagonal" and (
        flags["origin_mixture"] or flags["intervening_medium"] or flags["projection_effects"]
    ):
        blocked.append("diagonal_covariance_requires_explicit_independence_justification")
    if flags["selection_function"] and not _present(context.get("selection_ref")):
        blocked.append("selection_function_declared_without_selection_ref")

    latent_tokens = [
        name for name, value in latent_state.items()
        if value == "TOKEN_VAZIO"
    ]

    readiness = "ROUTABLE_HYPOTHESIS"
    if blocked:
        readiness = "BLOCKED_QUANTITATIVE"
    elif latent_tokens or blocked_parameter_ids:
        readiness = "ROUTABLE_WITH_TOKEN_VAZIO"

    return {
        "schema": "rll.rx.population_dispersion.v1",
        "state": "HYPOTHESIS_LAYER",
        "readiness": readiness,
        "population_count": len(populations),
        "latent_state": latent_state,
        "latent_token_vazio": latent_tokens,
        "flags": flags,
        "covariance_mode": covariance_mode,
        "source_bound_parameter_ids": source_bound_ids,
        "blocked_parameter_ids": blocked_parameter_ids,
        "blocked_reasons": blocked,
        "selection_boundary": (
            "Selection belongs in the likelihood/normalization model and must not be "
            "silently absorbed into covariance."
        ),
        "physics_boundary": (
            "Observed dispersion can be decomposed into measurement, intrinsic, "
            "population-origin, transport, medium and projection contributions, but "
            "the terms are not assumed independent unless an explicit covariance "
            "contract justifies that approximation."
        ),
        "claim_allowed": False,
    }
