"""Exact geometry features for RLL diagnostic routing.

Geometry may adapt numerical resolution, synthetic fixture density and diagnostic
router priority. It MUST NOT adapt cosmological/physical parameters by itself.
Standard-library only; claim_allowed is always false at this layer.
"""
from __future__ import annotations
import math

TAU = 2.0 * math.pi

def _finite(x):
    x = float(x)
    if not math.isfinite(x):
        raise ValueError("non-finite input")
    return x

def _positive(x, name):
    x = _finite(x)
    if x <= 0:
        raise ValueError(f"{name} must be > 0")
    return x

def _clamp(x, lo, hi):
    return max(lo, min(hi, x))

def wrapped_angle(theta):
    theta = _finite(theta)
    return math.atan2(math.sin(theta), math.cos(theta))

def complex_rotate(z, phi):
    phi = _finite(phi)
    return z * complex(math.cos(phi), math.sin(phi))

def complex_multiply_polar(r1, t1, r2, t2):
    r1 = _positive(r1, "r1")
    r2 = _positive(r2, "r2")
    return r1 * r2, wrapped_angle(t1 + t2)

def complex_divide_polar(r1, t1, r2, t2):
    r1 = _positive(r1, "r1")
    r2 = _positive(r2, "r2")
    return r1 / r2, wrapped_angle(t1 - t2)

def complex_root_polar(r, theta, k, branch=0):
    r = _positive(r, "r")
    if k <= 0:
        raise ValueError("k must be positive")
    if not (0 <= branch < k):
        raise ValueError("branch out of range")
    return r ** (1.0 / k), wrapped_angle((theta + TAU * branch) / k)

def annulus_features(r_in, r_out):
    r_in = _positive(r_in, "r_in")
    r_out = _positive(r_out, "r_out")
    if not r_in < r_out:
        raise ValueError("require 0 < r_in < r_out")
    q = r_in / r_out
    return {
        "radius_ratio": q,
        "thickness_ratio": 1.0 - q,
        "area_ratio_inner_to_outer": q * q,
        "annulus_area_fraction": 1.0 - q * q,
        "circumference_ratio": q,
        "normalized_annulus_area": math.pi * (1.0 - q * q),
    }

def spherical_shell_features(r_in, r_out):
    r_in = _positive(r_in, "r_in")
    r_out = _positive(r_out, "r_out")
    if not r_in < r_out:
        raise ValueError("require 0 < r_in < r_out")
    q = r_in / r_out
    return {
        "radius_ratio": q,
        "volume_ratio_inner_to_outer": q ** 3,
        "shell_volume_fraction": 1.0 - q ** 3,
        "normalized_shell_volume": (4.0 * math.pi / 3.0) * (1.0 - q ** 3),
    }

def circle_inversion(radius, inversion_radius):
    radius = _positive(radius, "radius")
    a = _positive(inversion_radius, "inversion_radius")
    image = a * a / radius
    return {
        "radius": radius,
        "inversion_radius": a,
        "image_radius": image,
        "product_invariant": radius * image,
        "expected_product": a * a,
    }

def projection_features(inclination_rad):
    i = _finite(inclination_rad)
    q = abs(math.cos(i))
    e = abs(math.sin(i))
    return {
        "axis_ratio_b_over_a": q,
        "eccentricity_proxy": e,
        "unit_identity_residual": q * q + e * e - 1.0,
        "area_projection_factor": q,
    }

def regular_polygon_features(n):
    if int(n) != n or n < 3:
        raise ValueError("n must be integer >= 3")
    n = int(n)
    x = math.pi / n
    q = math.cos(x)
    return {
        "n": n,
        "inradius_over_circumradius": q,
        "side_over_2R": math.sin(x),
        "diagonal_recurrence_lambda": 2.0 * q,
        "compactness_4piA_over_P2": math.pi / (n * math.tan(x)),
        "central_angle_rad": 2.0 * math.pi / n,
    }

def chebyshev_diagonal_ratios(n, max_k=None):
    f = regular_polygon_features(n)
    n = f["n"]
    if max_k is None:
        max_k = n // 2
    if not (1 <= max_k <= n // 2):
        raise ValueError("max_k out of range")
    lam = 2.0 * math.cos(math.pi / n)
    seq = [0.0, 1.0]
    for _ in range(1, max_k):
        seq.append(lam * seq[-1] - seq[-2])
    return seq[1:max_k + 1]

def adaptive_numerical_policy(feature_vector):
    """Return fail-closed numerical-routing suggestions, never physical deltas."""
    anis = float(feature_vector.get("axis_ratio_b_over_a", 1.0))
    compact = float(feature_vector.get("compactness_4piA_over_P2", 1.0))
    shell = float(feature_vector.get("annulus_area_fraction", 0.0))
    if not (0.0 <= anis <= 1.0 and 0.0 < compact <= 1.05 and 0.0 <= shell <= 1.0):
        raise ValueError("feature vector outside declared diagnostic domain")
    complexity = _clamp(
        0.5 * (1.0 - anis) + 0.3 * max(0.0, 1.0 - compact) + 0.2 * shell,
        0.0, 1.0,
    )
    return {
        "geometry_complexity_score": complexity,
        "suggested_relative_step_scale": 1.0 / (1.0 + 4.0 * complexity),
        "suggested_subdivision_factor": 1 + int(math.floor(7.0 * complexity + 1e-15)),
        "allowed_adaptation": [
            "numerical_resolution",
            "synthetic_fixture_density",
            "diagnostic_router_priority",
        ],
        "blocked_adaptation": [
            "cosmological_density_parameters", "H0", "Omega_m", "Omega_s0",
            "w0", "wa", "physical_constants",
        ],
        "claim_allowed": False,
    }
