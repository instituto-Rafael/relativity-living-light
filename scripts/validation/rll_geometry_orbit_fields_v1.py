"""RLL geometry/orbit/field reference oracle (opt-in; no likelihood binding).

Units: SI unless noted; all angles radians; logs dimensionless.
Classical Euclidean geometry, Newtonian point mass and static far-field magnetic
dipole are separate physical/math domains. This is NOT RLL dark-energy physics.
No imports of H(z), no global state, no file writes. claim_allowed = False.
"""
from __future__ import annotations

import math

CLAIM_ALLOWED = False
MU0_OVER_4PI_SI_APPROX = 1.0e-7  # T*m/A, ideal vacuum dipole reference


def _finite(value: float, name: str) -> float:
    try:
        x = float(value)
    except (ValueError, TypeError) as exc:
        raise ValueError(f"{name} must be a finite real number") from exc
    if not math.isfinite(x):
        raise ValueError(f"{name} must be finite")
    return x


def _positive(value: float, name: str) -> float:
    x = _finite(value, name)
    if x <= 0.0:
        raise ValueError(f"{name} must be positive")
    return x


def _vec3(v: tuple[float, float, float], name: str) -> tuple[float, float, float]:
    if len(v) != 3:
        raise ValueError(f"{name} must have three components")
    return tuple(_finite(x, name) for x in v)


def rotate2(point: tuple[float, float], theta_rad: float) -> tuple[float, float]:
    """Rigid planar rotation (angles in radians)."""
    x, y = map(float, point)
    x, y = _finite(x, "x"), _finite(y, "y")
    t = _finite(theta_rad, "theta_rad")
    c, s = math.cos(t), math.sin(t)
    return (c * x - s * y, s * x + c * y)


def wrapped_angle_rad(theta_from: float, theta_to: float) -> float:
    a, b = _finite(theta_from, "theta_from"), _finite(theta_to, "theta_to")
    return math.atan2(math.sin(b - a), math.cos(b - a))


def circle_chord_m(radius_m: float, central_angle_rad: float) -> float:
    r, t = _positive(radius_m, "radius_m"), _finite(central_angle_rad, "central_angle_rad")
    return 2.0 * r * abs(math.sin(t / 2.0))


def circle_apothem_signed_m(radius_m: float, central_angle_rad: float) -> float:
    r, t = _positive(radius_m, "radius_m"), _finite(central_angle_rad, "central_angle_rad")
    return r * math.cos(t / 2.0)


def tangent_to_circle_normal(
    point_m: tuple[float, float], center_m: tuple[float, float], radius_m: float,
    atol_m: float = 1e-9,
) -> tuple[float, float]:
    """Normal (x-cx,y-cy) to a line tangent at point; only on circle."""
    px, py = map(lambda a: _finite(a, "point_m"), point_m)
    cx, cy = map(lambda a: _finite(a, "center_m"), center_m)
    r = _positive(radius_m, "radius_m")
    tol = _positive(atol_m, "atol_m")
    dx, dy = px - cx, py - cy
    if abs(math.hypot(dx, dy) - r) > tol:
        raise ValueError("point is not on the circle to tolerance")
    return dx, dy


def orthographic_project2_m(
    point_m: tuple[float, float, float], inclination_rad: float,
) -> tuple[float, float]:
    """Rotate about x then discard z; not an orbital ellipse fit."""
    x, y, z = _vec3(point_m, "point_m")
    t = _finite(inclination_rad, "inclination_rad")
    return x, y * math.cos(t) - z * math.sin(t)


def log_similarity_ratios(length_ratio: float) -> dict[str, float]:
    """Dimensionless similarity: ln L, ln area, ln volume."""
    q = _positive(length_ratio, "length_ratio")
    x = math.log(q)
    return {"ln_length": x, "ln_area": 2.0 * x, "ln_volume": 3.0 * x}


def log_of_log(x: float) -> float:
    """Natural ln(ln x); this is NOT a log-log scatterplot."""
    x = _finite(x, "dimensionless_x")
    if x <= 1.0:
        raise ValueError("ln(ln x) requires dimensionless x > 1")
    return math.log(math.log(x))


def vertex_covariance2(
    points: tuple[tuple[float, float], ...],
) -> tuple[tuple[float, float], tuple[tuple[float, float], tuple[float, float]]]:
    """Population covariance of equally weighted coordinates (not sensor error)."""
    if len(points) < 2:
        raise ValueError("at least two points required")
    pairs = [(_finite(p[0], "x"), _finite(p[1], "y")) for p in points]
    n = len(pairs)
    mx = sum(p[0] for p in pairs) / n
    my = sum(p[1] for p in pairs) / n
    xx = sum((x - mx) ** 2 for x, _ in pairs) / n
    yy = sum((y - my) ** 2 for _, y in pairs) / n
    xy = sum((x - mx) * (y - my) for x, y in pairs) / n
    return (mx, my), ((xx, xy), (xy, yy))


def mean_cross_squared_distance2(
    first: tuple[tuple[float, float], ...],
    second: tuple[tuple[float, float], ...],
) -> float:
    """Finite Cartesian-product identity, not probabilistic independence claim."""
    mu1, c1 = vertex_covariance2(first)
    mu2, c2 = vertex_covariance2(second)
    return ((mu1[0] - mu2[0]) ** 2 + (mu1[1] - mu2[1]) ** 2
            + c1[0][0] + c1[1][1] + c2[0][0] + c2[1][1])


def kepler_ellipse_state_si(
    mu_m3_s2: float, semi_major_m: float, eccentricity: float,
    true_anomaly_rad: float, inclination_rad: float = 0.0,
) -> dict[str, object]:
    """Point-mass TWO-BODY focus-centered state; no N-body/GR/J2/plasma."""
    mu = _positive(mu_m3_s2, "mu_m3_s2")
    a = _positive(semi_major_m, "semi_major_m")
    e = _finite(eccentricity, "eccentricity")
    nu = _finite(true_anomaly_rad, "true_anomaly_rad")
    inc = _finite(inclination_rad, "inclination_rad")
    if not 0.0 <= e < 1.0:
        raise ValueError("ellipse requires eccentricity in [0,1)")
    if not 0.0 <= inc <= math.pi:
        raise ValueError("inclination must be in [0, pi] radians")
    p = a * (1.0 - e * e)
    if p <= 0.0:
        raise ValueError("degenerate semi-latus rectum")
    c, s = math.cos(nu), math.sin(nu)
    r = p / (1.0 + e * c)
    vscale = math.sqrt(mu / p)
    # Perifocal components, then rotate around x (fixed node convention).
    x, y = r * c, r * s
    vx, vy = -vscale * s, vscale * (e + c)
    ci, si = math.cos(inc), math.sin(inc)
    pos = (x, y * ci, y * si)
    vel = (vx, vy * ci, vy * si)
    energy = 0.5 * sum(v * v for v in vel) - mu / r
    h = (pos[1] * vel[2] - pos[2] * vel[1],
         pos[2] * vel[0] - pos[0] * vel[2],
         pos[0] * vel[1] - pos[1] * vel[0])
    return {
        "position_m": pos,
        "velocity_m_s": vel,
        "radius_m": r,
        "specific_energy_m2_s2": energy,
        "specific_h_m2_s": math.sqrt(sum(t * t for t in h)),
        "expected_specific_energy_m2_s2": -mu / (2.0 * a),
        "expected_specific_h_m2_s": math.sqrt(mu * p),
        "model": "NEWTONIAN_TWO_BODY_REFERENCE",
        "claim_allowed": False,
    }


def newton_gravity_m_s2(
    mu_m3_s2: float, position_m: tuple[float, float, float],
) -> tuple[float, float, float]:
    mu = _positive(mu_m3_s2, "mu_m3_s2")
    p = _vec3(position_m, "position_m")
    r = math.sqrt(sum(v * v for v in p))
    if r <= 0.0:
        raise ValueError("point-mass gravitational field singular at origin")
    return tuple(-mu * v / (r ** 3) for v in p)


def vacuum_dipole_tesla(
    position_m: tuple[float, float, float],
    moment_A_m2: tuple[float, float, float],
) -> tuple[float, float, float]:
    """Ideal static vacuum far-field dipole; NOT general magnetic/plasma field."""
    p = _vec3(position_m, "position_m")
    m = _vec3(moment_A_m2, "moment_A_m2")
    r = math.sqrt(sum(v * v for v in p))
    if r <= 0.0:
        raise ValueError("dipole field singular at origin")
    n = tuple(v / r for v in p)
    m_dot_n = sum(x * y for x, y in zip(m, n))
    fac = MU0_OVER_4PI_SI_APPROX / (r ** 3)
    return tuple(fac * (3.0 * m_dot_n * ni - mi) for ni, mi in zip(n, m))


def separate_field_probe(
    mu_m3_s2: float, semi_major_m: float, eccentricity: float,
    true_anomaly_rad: float, inclination_rad: float,
    moment_A_m2: tuple[float, float, float],
) -> dict[str, object]:
    """Diagnostic only: shared geometry, separate forces, zero H(z) binding."""
    orbit = kepler_ellipse_state_si(
        mu_m3_s2, semi_major_m, eccentricity, true_anomaly_rad, inclination_rad
    )
    p = orbit["position_m"]
    return {
        "orbit": orbit,
        "gravity_m_s2": newton_gravity_m_s2(mu_m3_s2, p),
        "dipole_B_tesla": vacuum_dipole_tesla(p, moment_A_m2),
        "mechanisms": ("NEWTON_POINT_MASS", "VACUUM_STATIC_DIPOLE"),
        "cosmological_likelihood_binding": "BLOCKED",
        "measurement_covariance": "TOKEN_VAZIO",
        "claim_allowed": False,
    }
