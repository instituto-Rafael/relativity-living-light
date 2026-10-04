#!/usr/bin/env python3
"""RLL geometric/dispersion falsification helpers.

This module is a mathematical/diagnostic layer only. It does not change the
RLL cosmology equations and it cannot promote a scientific claim.
"""

from __future__ import annotations

from fractions import Fraction
from math import cos, gcd, lcm, log, pi, sin, sqrt
from statistics import mean
from typing import Iterable

SQRT3_OVER_2 = sqrt(3.0) / 2.0
THREE_OVER_2 = 3.0 / 2.0
SQRT_THREE_OVER_TWO = sqrt(3.0 / 2.0)
PHI = (1.0 + sqrt(5.0)) / 2.0

MODULI = (3, 7, 14, 10, 30, 5, 50, 70)
JOINT_MOD_PERIOD = lcm(*MODULI)

CLAIM_ALLOWED = False
PHYSICAL_MAPPING_STATE = "TOKEN_VAZIO_PHYSICAL_MAPPING"
LOG_BASE_STATE = "TOKEN_VAZIO_LOG_BASE"


def _as_floats(values: Iterable[float]) -> tuple[float, ...]:
    return tuple(float(v) for v in values)


def sample_variance(values: Iterable[float]) -> float:
    """Unbiased sample variance, denominator n-1."""
    xs = _as_floats(values)
    if len(xs) < 2:
        raise ValueError("sample variance requires n >= 2")
    xbar = mean(xs)
    return sum((x - xbar) ** 2 for x in xs) / (len(xs) - 1)


def population_variance(values: Iterable[float]) -> float:
    """Population variance, denominator N."""
    xs = _as_floats(values)
    if not xs:
        raise ValueError("population variance requires N >= 1")
    mu = mean(xs)
    return sum((x - mu) ** 2 for x in xs) / len(xs)


def variance_of_sample_mean(values: Iterable[float]) -> float:
    """Estimated Var(mean) = s^2 / n for independent observations."""
    xs = _as_floats(values)
    return sample_variance(xs) / len(xs)


def variance_of_independent_mean_difference(
    left: Iterable[float], right: Iterable[float]
) -> float:
    """Estimated Var(mean(left)-mean(right)) for independent samples."""
    a = _as_floats(left)
    b = _as_floats(right)
    return sample_variance(a) / len(a) + sample_variance(b) / len(b)


def mean_safety_margin(values: Iterable[float], k: float = 1.96) -> float:
    """Analogy-only uncertainty reserve around a sample mean."""
    return float(k) * sqrt(variance_of_sample_mean(values))


def future_observation_margin(values: Iterable[float], k: float = 1.96) -> float:
    """Normal-model prediction margin for one future independent observation."""
    xs = _as_floats(values)
    return float(k) * sqrt(sample_variance(xs) * (1.0 + 1.0 / len(xs)))


def ols_line(xs: Iterable[float], ys: Iterable[float]) -> tuple[float, float]:
    """Return (intercept, slope) for a simple least-squares diagnostic line."""
    x = _as_floats(xs)
    y = _as_floats(ys)
    if len(x) != len(y) or len(x) < 2:
        raise ValueError("OLS requires equal-length x/y with n >= 2")
    xbar = mean(x)
    ybar = mean(y)
    sxx = sum((v - xbar) ** 2 for v in x)
    if sxx == 0.0:
        raise ValueError("OLS requires non-zero x dispersion")
    slope = sum((a - xbar) * (b - ybar) for a, b in zip(x, y)) / sxx
    return ybar - slope * xbar, slope


def pbip_discriminant(radius: float, perpendicular_distance: float) -> float:
    """PBIP-L1: Delta_B = 4(r^2-d_perp^2)."""
    r = float(radius)
    d = float(perpendicular_distance)
    if r < 0:
        raise ValueError("radius must be non-negative")
    return 4.0 * (r * r - d * d)


def pbip_intersection_class(radius: float, perpendicular_distance: float) -> str:
    delta = pbip_discriminant(radius, perpendicular_distance)
    eps = 1e-12
    if delta > eps:
        return "TWO_REAL_INTERSECTIONS"
    if delta < -eps:
        return "NO_REAL_INTERSECTION"
    return "TANGENCY"


def isosceles_gate(equal_side: float, half_apex_deg: float) -> tuple[float, float]:
    """Return (base, height) for b=2L sin(alpha), h=L cos(alpha)."""
    L = float(equal_side)
    alpha = float(half_apex_deg) * pi / 180.0
    return 2.0 * L * sin(alpha), L * cos(alpha)


def right_leg_difference_identity(a: float, b: float) -> tuple[float, float, float]:
    """Return lhs=a^2+b^2, rhs=2ab+|a-b|^2, delta=|a-b|."""
    aa = float(a)
    bb = float(b)
    delta = abs(aa - bb)
    return aa * aa + bb * bb, 2.0 * aa * bb + delta * delta, delta


def canonical_spiral_point(n: int, r0: float = 1.0) -> tuple[float, float, float]:
    """Historical source: z_n=r0*(sqrt(3)/2)^n*exp(i*n*pi*phi)."""
    if n < 0:
        raise ValueError("n must be non-negative")
    radius = float(r0) * (SQRT3_OVER_2 ** int(n))
    phase = int(n) * pi * PHI
    return radius * cos(phase), radius * sin(phase), radius


def adversarial_three_over_two_radius(n: int, r0: float = 1.0) -> float:
    """Deliberately non-canonical expansion control: r0*(3/2)^n."""
    if n < 0:
        raise ValueError("n must be non-negative")
    return float(r0) * (THREE_OVER_2 ** int(n))


def modular_phase(n: int, modulus: int) -> float:
    """theta_m(n)=2*pi*(n mod m)/m."""
    m = int(modulus)
    if m <= 0:
        raise ValueError("modulus must be positive")
    return 2.0 * pi * (int(n) % m) / m


def modular_signature(n: int) -> tuple[int, ...]:
    return tuple(int(n) % m for m in MODULI)


def reduced_ratio(numerator: int, denominator: int) -> Fraction:
    if int(denominator) == 0:
        raise ZeroDivisionError("ratio denominator cannot be zero")
    return Fraction(int(numerator), int(denominator))


def ratio_reduction_receipt() -> dict[str, object]:
    r1 = reduced_ratio(77, 33)
    r2 = reduced_ratio(777, 333)
    return {
        "77_over_33": str(r1),
        "777_over_333": str(r2),
        "gcd_77_33": gcd(77, 33),
        "gcd_777_333": gcd(777, 333),
        "representation_invariant": r1 == r2 == Fraction(7, 3),
    }


def square_area(side: float | None) -> float | None:
    """None models TOKEN_VAZIO/absence; side=0 models a defined degenerate square."""
    if side is None:
        return None
    s = float(side)
    return s * s


def nested_log_999(base: float) -> float:
    """Compute log_base(log_base(999)); base must be explicitly declared."""
    b = float(base)
    if b <= 0.0 or b == 1.0:
        raise ValueError("log base must be positive and != 1")
    inner = log(999.0, b)
    if inner <= 0.0:
        raise ValueError("nested logarithm is outside the real domain")
    return log(inner, b)


def contract_receipt() -> dict[str, object]:
    b30, h30 = isosceles_gate(1.0, 30.0)
    return {
        "schema": "rll.geometric_dispersion_false_positive_gate.receipt.v1",
        "claim_allowed": CLAIM_ALLOWED,
        "physical_mapping_state": PHYSICAL_MAPPING_STATE,
        "log_base_state": LOG_BASE_STATE,
        "canonical_spiral_q": SQRT3_OVER_2,
        "distinct_three_over_two": THREE_OVER_2,
        "distinct_sqrt_three_over_two": SQRT_THREE_OVER_TWO,
        "pi_phi": pi * PHI,
        "moduli": list(MODULI),
        "joint_mod_period": JOINT_MOD_PERIOD,
        "ratio_reduction": ratio_reduction_receipt(),
        "isosceles_alpha30": {"base_over_L": b30, "height_over_L": h30},
        "void_square_area": square_area(None),
        "zero_side_square_area": square_area(0.0),
        "boundary": (
            "Mathematical identities and diagnostic statistics do not establish "
            "a cosmological mechanism. Correlated RLL data must use the declared "
            "covariance/GLS likelihood; OLS here is diagnostic only."
        ),
    }


if __name__ == "__main__":
    import json

    print(json.dumps(contract_receipt(), indent=2, sort_keys=True))
