from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Sequence

EPS = 1e-12


class ResidualClass(str, Enum):
    PHYSICS = "R_PHYSICS"
    TRANSPORT = "R_TRANSPORT"
    MATTER_FIELD = "R_MATTER_FIELD"
    INSTRUMENT = "R_INSTRUMENT"
    CALIBRATION = "R_CALIBRATION"
    NUMERICAL = "R_NUMERICAL"
    OUT_OF_DOMAIN = "R_OUT_OF_DOMAIN"
    TOKEN_VAZIO = "R_TOKEN_VAZIO"


class OppositionState(str, Enum):
    SUPPORTED_ONLY = "SUPPORTED_ONLY"
    REFUTED_ONLY = "REFUTED_ONLY"
    BOTH = "BOTH"
    NEITHER = "NEITHER"
    SCOPE_SPLIT = "SCOPE_SPLIT"
    TOKEN_VAZIO = "TOKEN_VAZIO"


@dataclass(frozen=True)
class ResidualChecks:
    provenance_complete: bool
    uncertainty_known: bool
    in_domain: bool
    numerical_check_passed: bool
    calibration_check_passed: bool
    instrument_check_passed: bool
    transport_check_passed: bool
    matter_field_check_passed: bool
    physics_candidate: bool = False


@dataclass(frozen=True)
class ResidualScreen:
    sample_size: int
    threshold: float
    exceedance_count: int
    exceedance_fraction: float
    max_abs_normalized_residual: float | None
    classification: str
    warning: str


@dataclass(frozen=True)
class GateResult:
    state: str
    scope_overlap: float
    next_gate: str


def normalized_residual(
    observed: float,
    predicted: float,
    sigma_observed: float,
    sigma_model: float = 0.0,
) -> float:
    values = (observed, predicted, sigma_observed, sigma_model)
    if not all(math.isfinite(float(value)) for value in values):
        raise ValueError("residual inputs must be finite")
    if sigma_observed < 0 or sigma_model < 0:
        raise ValueError("uncertainties must be non-negative")
    denominator = math.sqrt(sigma_observed**2 + sigma_model**2)
    if denominator <= EPS:
        raise ValueError("combined uncertainty must be positive")
    return (observed - predicted) / denominator


def classify_residual(checks: ResidualChecks) -> ResidualClass:
    if not checks.provenance_complete or not checks.uncertainty_known:
        return ResidualClass.TOKEN_VAZIO
    if not checks.in_domain:
        return ResidualClass.OUT_OF_DOMAIN
    if not checks.numerical_check_passed:
        return ResidualClass.NUMERICAL
    if not checks.calibration_check_passed:
        return ResidualClass.CALIBRATION
    if not checks.instrument_check_passed:
        return ResidualClass.INSTRUMENT
    if not checks.transport_check_passed:
        return ResidualClass.TRANSPORT
    if not checks.matter_field_check_passed:
        return ResidualClass.MATTER_FIELD
    if checks.physics_candidate:
        return ResidualClass.PHYSICS
    return ResidualClass.TOKEN_VAZIO


def screen_residuals(
    normalized_values: Sequence[float],
    *,
    threshold: float,
    checks: ResidualChecks,
) -> ResidualScreen:
    if threshold <= 0 or not math.isfinite(threshold):
        raise ValueError("threshold must be finite and positive")
    finite_values = [
        float(value)
        for value in normalized_values
        if math.isfinite(float(value))
    ]
    classification = classify_residual(checks)
    exceedance_count = sum(abs(value) >= threshold for value in finite_values)
    sample_size = len(finite_values)
    return ResidualScreen(
        sample_size=sample_size,
        threshold=threshold,
        exceedance_count=exceedance_count,
        exceedance_fraction=(
            exceedance_count / sample_size if sample_size else 0.0
        ),
        max_abs_normalized_residual=(
            max(abs(value) for value in finite_values)
            if finite_values
            else None
        ),
        classification=classification.value,
        warning=(
            "Residual magnitude alone never promotes R_PHYSICS; classification "
            "depends on provenance, domain and ordered exclusion checks."
        ),
    )


def opposition_gate(
    *,
    support_weight: float,
    refutation_weight: float,
    scope_overlap: float,
    evidence_complete: bool,
    scope_split_threshold: float = 0.5,
) -> GateResult:
    for name, value in {
        "support_weight": support_weight,
        "refutation_weight": refutation_weight,
    }.items():
        if value < 0 or not math.isfinite(value):
            raise ValueError(f"{name} must be finite and non-negative")
    if not 0.0 <= scope_overlap <= 1.0:
        raise ValueError("scope_overlap must be between 0 and 1")
    if not 0.0 <= scope_split_threshold <= 1.0:
        raise ValueError(
            "scope_split_threshold must be between 0 and 1"
        )
    if not evidence_complete:
        state = OppositionState.TOKEN_VAZIO
    elif support_weight > EPS and refutation_weight > EPS:
        state = (
            OppositionState.SCOPE_SPLIT
            if scope_overlap < scope_split_threshold
            else OppositionState.BOTH
        )
    elif support_weight > EPS:
        state = OppositionState.SUPPORTED_ONLY
    elif refutation_weight > EPS:
        state = OppositionState.REFUTED_ONLY
    else:
        state = OppositionState.NEITHER
    next_gate = {
        OppositionState.SUPPORTED_ONLY: (
            "run matched-scope refutation and negative controls"
        ),
        OppositionState.REFUTED_ONLY: (
            "inspect measurement model and narrower domain"
        ),
        OppositionState.BOTH: (
            "partition by band, redshift, instrument or operator version"
        ),
        OppositionState.NEITHER: (
            "acquire evidence or preserve abstention"
        ),
        OppositionState.SCOPE_SPLIT: (
            "test the proposed boundary in matched scopes"
        ),
        OppositionState.TOKEN_VAZIO: (
            "complete provenance, uncertainty and domain metadata"
        ),
    }[state]
    return GateResult(state.value, scope_overlap, next_gate)


def photonic_invariant_errors(
    *,
    intensity: float,
    q: float = 0.0,
    u: float = 0.0,
    v: float = 0.0,
) -> list[str]:
    values = (intensity, q, u, v)
    if not all(math.isfinite(float(value)) for value in values):
        return ["photonic state values must be finite"]
    errors: list[str] = []
    if intensity < 0:
        errors.append("intensity must be non-negative")
    if q * q + u * u + v * v > intensity * intensity + EPS:
        errors.append("polarization magnitude exceeds intensity")
    return errors


def report_dict(
    screen: ResidualScreen,
    gate: GateResult | None = None,
) -> dict:
    return {
        "schema": "rll.omega_residual_audit.v1",
        "screen": asdict(screen),
        "gate": None if gate is None else asdict(gate),
        "claim_boundary": (
            "This report classifies residual handling only. It does not "
            "validate RLL, establish new physics or replace observational "
            "likelihood analysis."
        ),
    }
