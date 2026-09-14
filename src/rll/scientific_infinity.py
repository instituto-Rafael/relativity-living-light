"""Claim-bounded operators for finite scientific work over open-ended horizons.

The module makes one boundary explicit: scientific software can represent
mathematical or potentially unbounded processes, but every concrete execution
is finite and budgeted. No result from this module authorizes a physical or
cosmological claim by itself.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
import math
from typing import Any, Iterable, Mapping, Sequence


class InfinityClass(str, Enum):
    """Distinct meanings that must not be collapsed into one symbol."""

    MATHEMATICAL = "infinity_math"
    POTENTIAL = "infinity_potential"
    PHYSICAL = "infinity_physical"
    COMPUTATIONAL = "infinity_computational"
    EVOLUTIONARY = "infinity_evolutionary"
    EPISTEMIC_GAP = "TOKEN_VAZIO"


class CycleDecision(str, Enum):
    """Finite outcomes for one guarded evolution cycle."""

    CONTINUE = "continue"
    CONVERGED = "converged"
    CYCLE_DETECTED = "cycle_detected"
    BUDGET_EXHAUSTED = "budget_exhausted"
    TOKEN_VAZIO = "TOKEN_VAZIO"


@dataclass(frozen=True)
class GuardPolicy:
    """Budgets and evidence gates for an open-ended scientific process."""

    max_iterations: int = 100
    timeout_seconds: float = 60.0
    convergence_tolerance: float = 1.0e-6
    novelty_floor: float = 1.0e-3
    evidence_floor: float = 0.5
    max_duplication_ratio: float = 0.95
    max_unresolved_contradictions: int = 0

    def __post_init__(self) -> None:
        if self.max_iterations < 1:
            raise ValueError("max_iterations must be >= 1")
        if not math.isfinite(self.timeout_seconds) or self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be finite and > 0")
        if not math.isfinite(self.convergence_tolerance) or self.convergence_tolerance < 0:
            raise ValueError("convergence_tolerance must be finite and >= 0")
        for name in ("novelty_floor", "evidence_floor", "max_duplication_ratio"):
            value = float(getattr(self, name))
            if not math.isfinite(value) or not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be finite and within [0, 1]")
        if self.max_unresolved_contradictions < 0:
            raise ValueError("max_unresolved_contradictions must be >= 0")


@dataclass(frozen=True)
class EvolutionObservation:
    """Measured state for one finite iteration."""

    iteration: int
    state_digest: str
    novelty: float
    evidence_strength: float
    duplication_ratio: float
    unresolved_contradictions: int
    elapsed_seconds: float
    objective_value: float | None = None

    def __post_init__(self) -> None:
        if self.iteration < 0:
            raise ValueError("iteration must be >= 0")
        if not self.state_digest:
            raise ValueError("state_digest must be non-empty")
        for name in ("novelty", "evidence_strength", "duplication_ratio"):
            value = float(getattr(self, name))
            if not math.isfinite(value) or not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be finite and within [0, 1]")
        if self.unresolved_contradictions < 0:
            raise ValueError("unresolved_contradictions must be >= 0")
        if not math.isfinite(self.elapsed_seconds) or self.elapsed_seconds < 0:
            raise ValueError("elapsed_seconds must be finite and >= 0")
        if self.objective_value is not None and not math.isfinite(self.objective_value):
            raise ValueError("objective_value must be finite when provided")


@dataclass(frozen=True)
class EvolutionAssessment:
    """Claim-bounded decision emitted by :func:`assess_evolution`."""

    decision: CycleDecision
    reasons: tuple[str, ...]
    metrics: Mapping[str, float | int | str | None] = field(default_factory=dict)
    claim_allowed: bool = False
    claim_boundary: str = (
        "Structural convergence or open-endedness diagnostics do not establish "
        "physical truth, cosmological validity, consciousness or external replication."
    )

    def __post_init__(self) -> None:
        if self.claim_allowed:
            raise ValueError("claim_allowed must remain false for this structural layer")
        if not self.reasons:
            raise ValueError("at least one decision reason is required")


def stable_digest(payload: Any) -> str:
    """Return a deterministic SHA-256 digest for JSON-compatible state."""

    serialized = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(serialized).hexdigest()


def evolution_score(
    content_novelty: float,
    feedback_quality: float,
    evidence_strength: float,
    duplication_ratio: float,
    unresolved_contradictions: int,
    *,
    duplication_weight: float = 1.0,
    contradiction_weight: float = 1.0,
) -> float:
    """Compute a bounded evidence-weighted evolution score.

    The numerator rewards novelty, useful feedback and evidence. The denominator
    penalizes duplication and unresolved contradiction. This is a governance
    metric, not a physical observable.
    """

    unit_values = {
        "content_novelty": content_novelty,
        "feedback_quality": feedback_quality,
        "evidence_strength": evidence_strength,
        "duplication_ratio": duplication_ratio,
    }
    for name, value in unit_values.items():
        if not math.isfinite(float(value)) or not 0.0 <= float(value) <= 1.0:
            raise ValueError(f"{name} must be finite and within [0, 1]")
    if unresolved_contradictions < 0:
        raise ValueError("unresolved_contradictions must be >= 0")
    if duplication_weight < 0 or contradiction_weight < 0:
        raise ValueError("penalty weights must be >= 0")

    numerator = content_novelty * feedback_quality * evidence_strength
    denominator = (
        1.0
        + duplication_weight * duplication_ratio
        + contradiction_weight * unresolved_contradictions
    )
    return float(numerator / denominator)


def _last_objective(history: Sequence[EvolutionObservation]) -> float | None:
    for observation in reversed(history):
        if observation.objective_value is not None:
            return float(observation.objective_value)
    return None


def assess_evolution(
    history: Sequence[EvolutionObservation],
    current: EvolutionObservation,
    policy: GuardPolicy,
) -> EvolutionAssessment:
    """Assess one finite cycle without promoting structural success to science.

    Gate order is intentional: hard budgets and repeated states stop execution;
    unresolved contradiction or weak evidence produce ``TOKEN_VAZIO``; only then
    can numerical convergence be declared.
    """

    metrics: dict[str, float | int | str | None] = {
        "iteration": current.iteration,
        "elapsed_seconds": current.elapsed_seconds,
        "novelty": current.novelty,
        "evidence_strength": current.evidence_strength,
        "duplication_ratio": current.duplication_ratio,
        "unresolved_contradictions": current.unresolved_contradictions,
        "objective_value": current.objective_value,
    }

    if current.iteration >= policy.max_iterations:
        return EvolutionAssessment(
            CycleDecision.BUDGET_EXHAUSTED,
            ("maximum finite iteration budget reached",),
            metrics,
        )
    if current.elapsed_seconds >= policy.timeout_seconds:
        return EvolutionAssessment(
            CycleDecision.BUDGET_EXHAUSTED,
            ("finite wall-clock budget reached",),
            metrics,
        )

    previous_digests = {item.state_digest for item in history}
    if current.state_digest in previous_digests:
        return EvolutionAssessment(
            CycleDecision.CYCLE_DETECTED,
            ("state digest repeated; recursion is cycling rather than evolving",),
            metrics,
        )
    if current.duplication_ratio > policy.max_duplication_ratio:
        return EvolutionAssessment(
            CycleDecision.CYCLE_DETECTED,
            ("duplication ratio exceeded the configured anti-loop threshold",),
            metrics,
        )

    gap_reasons: list[str] = []
    if current.unresolved_contradictions > policy.max_unresolved_contradictions:
        gap_reasons.append("unresolved contradiction gate exceeded")
    if current.evidence_strength < policy.evidence_floor:
        gap_reasons.append("evidence strength is below the promotion floor")
    if gap_reasons:
        return EvolutionAssessment(
            CycleDecision.TOKEN_VAZIO,
            tuple(gap_reasons),
            metrics,
        )

    previous_objective = _last_objective(history)
    if previous_objective is not None and current.objective_value is not None:
        delta = abs(float(current.objective_value) - previous_objective)
        metrics["objective_delta"] = delta
        if delta <= policy.convergence_tolerance and current.novelty <= policy.novelty_floor:
            return EvolutionAssessment(
                CycleDecision.CONVERGED,
                ("objective stabilized and measured novelty fell below threshold",),
                metrics,
            )

    return EvolutionAssessment(
        CycleDecision.CONTINUE,
        ("finite budgets remain and no convergence, cycle or evidence gap was triggered",),
        metrics,
    )


def distinct_infinity_classes(values: Iterable[InfinityClass | str]) -> tuple[str, ...]:
    """Normalize and deduplicate infinity classes while preserving order."""

    normalized: list[str] = []
    seen: set[str] = set()
    for value in values:
        token = value.value if isinstance(value, InfinityClass) else InfinityClass(value).value
        if token not in seen:
            normalized.append(token)
            seen.add(token)
    return tuple(normalized)
