"""UTM-185: explicit void-mask attention over the Poincaré ball.

The geometric origin is a valid point. Missingness is represented by an
independent boolean validity mask, never by a special coordinate.
claim_allowed = False
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence

Vector = Sequence[float]


@dataclass(frozen=True)
class AttentionResult:
    weights: tuple[float, ...]
    context: tuple[float, ...]
    state: str


def _norm_sq(x: Vector) -> float:
    return math.fsum(float(v) * float(v) for v in x)


def _validate_same_dimension(a: Vector, b: Vector) -> None:
    if len(a) != len(b):
        raise ValueError("vectors must have the same dimension")
    if not a:
        raise ValueError("vectors must be non-empty")


def poincare_distance(x: Vector, y: Vector, *, eps: float = 1e-15) -> float:
    """Distance in the unit-curvature Poincaré ball."""
    _validate_same_dimension(x, y)
    nx = _norm_sq(x)
    ny = _norm_sq(y)
    if nx >= 1.0 or ny >= 1.0:
        raise ValueError("all points must satisfy norm < 1")
    diff = math.fsum((float(a) - float(b)) ** 2 for a, b in zip(x, y))
    denom = max((1.0 - nx) * (1.0 - ny), eps)
    arg = 1.0 + (2.0 * diff / denom)
    return math.acosh(max(1.0, arg))


def masked_hyperbolic_attention(
    query: Vector,
    keys: Sequence[Vector],
    values: Sequence[Vector],
    valid_mask: Sequence[bool],
    *,
    temperature: float = 1.0,
) -> AttentionResult:
    """Compute attention from negative hyperbolic distances.

    Invalid positions receive exactly zero weight. If every position is
    invalid, fail closed with a zero context and typed TOKEN_VAZIO state.
    """
    if temperature <= 0.0 or not math.isfinite(temperature):
        raise ValueError("temperature must be finite and > 0")
    if not (len(keys) == len(values) == len(valid_mask)):
        raise ValueError("keys, values, and valid_mask must have equal length")
    if not keys:
        raise ValueError("at least one key is required")

    value_dim = len(values[0])
    if value_dim == 0 or any(len(v) != value_dim for v in values):
        raise ValueError("values must be non-empty and share one dimension")

    valid_indices = [i for i, valid in enumerate(valid_mask) if bool(valid)]
    if not valid_indices:
        return AttentionResult(
            weights=tuple(0.0 for _ in keys),
            context=tuple(0.0 for _ in range(value_dim)),
            state="TOKEN_VAZIO_ALL_MASKED",
        )

    logits = {i: -poincare_distance(query, keys[i]) / temperature for i in valid_indices}
    max_logit = max(logits.values())
    exp_scores = {i: math.exp(logits[i] - max_logit) for i in valid_indices}
    total = math.fsum(exp_scores.values())
    weights = [(exp_scores[i] / total) if i in exp_scores else 0.0 for i in range(len(keys))]
    context = tuple(
        math.fsum(weights[i] * float(values[i][j]) for i in range(len(values)))
        for j in range(value_dim)
    )
    return AttentionResult(weights=tuple(weights), context=context, state="VALID_MASK_APPLIED")
