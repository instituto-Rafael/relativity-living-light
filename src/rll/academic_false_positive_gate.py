"""Fail-closed diagnostics for academic false-positive control.

This module deliberately separates mathematical diagnostics from physical claims.
It may summarize dispersion, regression, modular/geometric structure and classical
reference equations, but none of those objects is evidence for RLL cosmology by
itself.

SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import cos, gcd, isfinite, log, pi, sin, sqrt
from typing import Iterable, Mapping, Sequence

TOKEN_VAZIO = "TOKEN_VAZIO"
DEFAULT_MODULI = (3, 5, 7, 10, 14, 30, 50, 70)
PHI = (1.0 + sqrt(5.0)) / 2.0


def _finite_values(values: Iterable[float]) -> tuple[float, ...]:
    out = tuple(float(v) for v in values)
    if not out:
        raise ValueError("at least one value is required")
    if not all(isfinite(v) for v in out):
        raise ValueError("all values must be finite")
    return out


def sample_mean(values: Iterable[float]) -> float:
    xs = _finite_values(values)
    return sum(xs) / len(xs)


def sample_variance(values: Iterable[float]) -> float | None:
    """Unbiased sample variance, using n-1; n<2 remains TOKEN_VAZIO/None."""
    xs = _finite_values(values)
    if len(xs) < 2:
        return None
    mean = sum(xs) / len(xs)
    return sum((x - mean) ** 2 for x in xs) / (len(xs) - 1)


def variance_of_mean(values: Iterable[float]) -> float | None:
    """Estimated variance of the sample mean: s^2/n."""
    xs = _finite_values(values)
    s2 = sample_variance(xs)
    return None if s2 is None else s2 / len(xs)


def difference_of_means(left: Iterable[float], right: Iterable[float]) -> dict[str, float | None]:
    """Welch-style variance estimate for a difference of two independent means."""
    a = _finite_values(left)
    b = _finite_values(right)
    va = sample_variance(a)
    vb = sample_variance(b)
    variance = None if va is None or vb is None else va / len(a) + vb / len(b)
    return {
        "mean_left": sum(a) / len(a),
        "mean_right": sum(b) / len(b),
        "mean_difference": sum(a) / len(a) - sum(b) / len(b),
        "variance_of_difference": variance,
        "standard_error_of_difference": None if variance is None else sqrt(variance),
    }


def ols_line(x: Iterable[float], y: Iterable[float]) -> dict[str, float | int | None]:
    """Ordinary least-squares line with residual variance when n>2."""
    xs = _finite_values(x)
    ys = _finite_values(y)
    if len(xs) != len(ys):
        raise ValueError("x and y must have equal length")
    if len(xs) < 2:
        raise ValueError("at least two paired observations are required")
    xbar = sum(xs) / len(xs)
    ybar = sum(ys) / len(ys)
    sxx = sum((xi - xbar) ** 2 for xi in xs)
    if sxx == 0.0:
        raise ValueError("regression requires non-zero x dispersion")
    sxy = sum((xi - xbar) * (yi - ybar) for xi, yi in zip(xs, ys))
    slope = sxy / sxx
    intercept = ybar - slope * xbar
    residuals = tuple(yi - (intercept + slope * xi) for xi, yi in zip(xs, ys))
    sse = sum(r * r for r in residuals)
    residual_variance = sse / (len(xs) - 2) if len(xs) > 2 else None
    return {
        "n": len(xs),
        "slope": slope,
        "intercept": intercept,
        "sse": sse,
        "residual_variance": residual_variance,
    }


def dispersion_buffer(values: Iterable[float], sigma_multiplier: float = 3.0) -> dict[str, float | str | None]:
    """Safety-stock *analogy* z*s, never a cosmological physical law."""
    xs = _finite_values(values)
    s2 = sample_variance(xs)
    if s2 is None:
        return {"buffer": None, "sample_std": None, "state": TOKEN_VAZIO}
    z = float(sigma_multiplier)
    if not isfinite(z) or z < 0.0:
        raise ValueError("sigma_multiplier must be finite and non-negative")
    std = sqrt(s2)
    return {
        "buffer": z * std,
        "sample_std": std,
        "state": "STATISTICAL_ANALOGY_ONLY",
    }


@dataclass(frozen=True)
class GeomRational:
    ratio: float
    primitive_p: int
    primitive_q: int
    scale_gcd: int
    orientation: int


def geometric_rational(p: int, q: int) -> GeomRational:
    """Preserve primitive direction and GCD scale instead of losing it in p/q."""
    p = int(p)
    q = int(q)
    if q == 0:
        raise ZeroDivisionError("q must be non-zero")
    scale = gcd(abs(p), abs(q))
    pp = p // scale
    qq = q // scale
    orientation = 1 if pp * qq >= 0 else -1
    if qq < 0:
        pp, qq = -pp, -qq
    return GeomRational(p / q, pp, qq, scale, orientation)


def modular_signature(n: int, moduli: Sequence[int] = DEFAULT_MODULI) -> dict[int, int]:
    n = int(n)
    out: dict[int, int] = {}
    for modulus in moduli:
        m = int(modulus)
        if m <= 0:
            raise ValueError("moduli must be positive")
        out[m] = n % m
    return out


def pythagorean_difference(a: float, b: float) -> dict[str, float]:
    """c^2=a^2+b^2=2ab+(a-b)^2, keeping the difference term explicit."""
    aa = float(a)
    bb = float(b)
    delta = abs(aa - bb)
    c2 = aa * aa + bb * bb
    return {"delta": delta, "c2": c2, "two_ab_plus_delta2": 2.0 * aa * bb + delta * delta}


def quadratic_discriminant(a: float, b: float, c: float) -> dict[str, float | str]:
    aa = float(a)
    bb = float(b)
    cc = float(c)
    if aa == 0.0:
        raise ValueError("quadratic coefficient a must be non-zero")
    delta = bb * bb - 4.0 * aa * cc
    state = "TWO_REAL_ROOTS" if delta > 0.0 else "TANGENT_DOUBLE_ROOT" if delta == 0.0 else "NO_REAL_ROOT"
    return {"delta": delta, "state": state}


def signed_quadratic(a: float, b: float, c: float, x: float) -> float:
    """Evaluate Ax^2+Bx+C without dropping negative coefficients/terms."""
    return float(a) * float(x) ** 2 + float(b) * float(x) + float(c)


def isosceles_projection(equal_side: float, alpha_deg: float = 30.0) -> dict[str, float]:
    """Declared isosceles construction: base=2L sin(alpha), h=L cos(alpha)."""
    side = float(equal_side)
    alpha = float(alpha_deg) * pi / 180.0
    if side < 0.0:
        raise ValueError("equal_side must be non-negative")
    return {
        "base": 2.0 * side * sin(alpha),
        "height": side * cos(alpha),
        "apex_angle_deg": 2.0 * float(alpha_deg),
    }


def leg_asymmetry(left: float, right: float) -> dict[str, float]:
    """Two-leg asymmetry diagnostic; it does NOT classify a triangle as isosceles."""
    l = float(left)
    r = float(right)
    lo = min(abs(l), abs(r))
    hi = max(abs(l), abs(r))
    return {
        "min_abs_leg": lo,
        "max_abs_leg": hi,
        "absolute_difference": abs(l - r),
        "relative_difference": 0.0 if hi == 0.0 else abs(l - r) / hi,
    }


def circular_section_width(radius: float, alpha_deg: float = 30.0) -> float:
    """w(alpha)=2 r sin(alpha); geometric section only, not a Venturi/vortex law."""
    r = float(radius)
    if r < 0.0:
        raise ValueError("radius must be non-negative")
    return 2.0 * r * sin(float(alpha_deg) * pi / 180.0)


def venturi_reference(area1: float, area2: float, velocity1: float, density: float) -> dict[str, float | str]:
    """Ideal incompressible same-height Venturi/Bernoulli reference model only."""
    a1, a2 = float(area1), float(area2)
    v1, rho = float(velocity1), float(density)
    if a1 <= 0.0 or a2 <= 0.0 or rho <= 0.0:
        raise ValueError("areas and density must be positive")
    v2 = v1 * a1 / a2
    pressure_drop_p1_minus_p2 = 0.5 * rho * (v2 * v2 - v1 * v1)
    return {
        "velocity2": v2,
        "pressure_drop_p1_minus_p2": pressure_drop_p1_minus_p2,
        "state": "REFERENCE_MODEL_ONLY",
    }


def exploratory_spiral_geodesic_features(n: int) -> dict[str, float | bool | str]:
    """Keep authorial scalar probes separate; no equality/physical binding is inferred."""
    nn = int(n)
    if nn < 0:
        raise ValueError("n must be non-negative")
    pg = (3.0 / 2.0) ** nn
    pi_phi = pi * PHI
    loglog999 = log(log(999.0))
    return {
        "pg_3_over_2_pow_n": pg,
        "pi_times_phi": pi_phi,
        "difference_pg_minus_pi_phi": pg - pi_phi,
        "log_log_999_natural": loglog999,
        "sqrt3_over_2": sqrt(3.0) / 2.0,
        "sin_30": 0.5,
        "equality_asserted": False,
        "state": "EXPLORATORY_FEATURE_ONLY",
    }


CONFIRMATORY_BOOLEAN_REQUIREMENTS = (
    "preregistered_before_result",
    "primary_metric_frozen",
    "negative_controls_passed",
    "baseline_family_complete",
    "robust_fit_complete",
    "uncertainty_quantified",
    "ablation_complete",
    "holdout_or_external_validation",
    "external_backend_or_equivalent",
    "independent_replication",
    "provenance_complete",
    "no_posthoc_parameter_change",
)
VALID_MULTIPLICITY_POLICIES = {
    "predefined_single_primary",
    "holm",
    "bonferroni",
    "fdr_bh",
    "bayesian_predeclared",
}


def academic_false_positive_gate(screening_positive: bool, evidence: Mapping[str, object] | None) -> dict[str, object]:
    """Require confirmatory evidence after a positive screening result.

    AIC/BIC/chi2 screening can nominate a result for confirmation; it cannot by
    itself establish an academic claim. This gate is intentionally strict.
    """
    evidence = evidence or {}
    missing = [name for name in CONFIRMATORY_BOOLEAN_REQUIREMENTS if evidence.get(name) is not True]
    multiplicity = str(evidence.get("multiplicity_policy", ""))
    if multiplicity not in VALID_MULTIPLICITY_POLICIES:
        missing.append("multiplicity_policy")
    ready = bool(screening_positive) and not missing
    return {
        "screening_positive": bool(screening_positive),
        "confirmatory_ready": ready,
        "missing_or_failed": missing,
        "multiplicity_policy": multiplicity or TOKEN_VAZIO,
        "boundary": "screening_positive != confirmatory_ready != scientific_truth",
    }
