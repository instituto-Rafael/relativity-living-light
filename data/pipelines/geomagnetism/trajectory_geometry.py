"""Intrinsic/local trajectory geometry for geomagnetic pole paths.

This module supplies the circle/turning bridge requested by the three-spiral
work without importing gravity-assist dynamics into geomagnetism.

A sequence of magnetic-pole positions is treated kinematically. Three nearby
surface positions are projected into the tangent plane at the middle sample;
the Euclidean circumcircle of that local triplet defines a discrete osculating
radius and curvature. This is a local geometric diagnostic, not an exact global
small-circle fit on the sphere and not an energy-transfer model.

claim_allowed = False
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from typing import Tuple

EARTH_MEAN_RADIUS_KM = 6371.0088
Point2 = Tuple[float, float]
GeoPoint = Tuple[float, float]  # latitude_deg, longitude_deg


def _finite(value: float, name: str) -> None:
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")


def _positive(value: float, name: str) -> None:
    _finite(value, name)
    if value <= 0.0:
        raise ValueError(f"{name} must be positive")


def norm2(v: Point2) -> float:
    return math.hypot(v[0], v[1])


def rotate2(v: Point2, angle_rad: float) -> Point2:
    """Pure kinematic 2-D rotation; vector norm is preserved."""
    _finite(angle_rad, "angle_rad")
    c, s = math.cos(angle_rad), math.sin(angle_rad)
    return (c * v[0] - s * v[1], s * v[0] + c * v[1])


def great_circle_distance_km(
    a: GeoPoint,
    b: GeoPoint,
    radius_km: float = EARTH_MEAN_RADIUS_KM,
) -> float:
    """Haversine great-circle distance on a sphere."""
    _positive(radius_km, "radius_km")
    lat1, lon1 = a
    lat2, lon2 = b
    for name, value in (("lat1", lat1), ("lon1", lon1), ("lat2", lat2), ("lon2", lon2)):
        _finite(value, name)
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = p2 - p1
    dl = math.radians(lon2 - lon1)
    h = math.sin(dp / 2.0) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2.0) ** 2
    h = min(1.0, max(0.0, h))
    return 2.0 * radius_km * math.asin(math.sqrt(h))


def initial_bearing_rad(a: GeoPoint, b: GeoPoint) -> float:
    """Initial great-circle bearing from a to b, measured east of north."""
    lat1, lon1 = a
    lat2, lon2 = b
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dl = math.radians(lon2 - lon1)
    y = math.sin(dl) * math.cos(p2)
    x = math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dl)
    if abs(x) < 1.0e-15 and abs(y) < 1.0e-15:
        raise ValueError("bearing is undefined for coincident/degenerate points")
    return math.atan2(y, x)


def tangent_xy_km(
    origin: GeoPoint,
    point: GeoPoint,
    radius_km: float = EARTH_MEAN_RADIUS_KM,
) -> Point2:
    """Azimuthal-equidistant local coordinates around origin.

    x is east, y is north. Radial distance from the origin equals the spherical
    great-circle distance, while pairwise distances away from the origin are
    only locally Euclidean.
    """
    d = great_circle_distance_km(origin, point, radius_km)
    if d == 0.0:
        return (0.0, 0.0)
    bearing = initial_bearing_rad(origin, point)
    return (d * math.sin(bearing), d * math.cos(bearing))


@dataclass(frozen=True)
class Circumcircle2D:
    center_x: float
    center_y: float
    radius: float
    signed_double_area: float

    @property
    def curvature(self) -> float:
        return 1.0 / self.radius

    def to_dict(self) -> dict[str, float]:
        payload = asdict(self)
        payload["curvature"] = self.curvature
        return payload


def circumcircle_2d(a: Point2, b: Point2, c: Point2, eps: float = 1.0e-14) -> Circumcircle2D:
    """Circumcircle through three non-collinear Cartesian points.

    Equivalent radius identity:
        R = |AB| |BC| |CA| / (4 * triangle_area).
    """
    _positive(eps, "eps")
    ax, ay = a
    bx, by = b
    cx, cy = c
    for name, value in (
        ("ax", ax), ("ay", ay), ("bx", bx), ("by", by), ("cx", cx), ("cy", cy)
    ):
        _finite(value, name)

    signed_double_area = (bx - ax) * (cy - ay) - (by - ay) * (cx - ax)
    det = 2.0 * signed_double_area
    scale = max(1.0, norm2((bx - ax, by - ay)), norm2((cx - ax, cy - ay)))
    if abs(det) <= eps * scale * scale:
        raise ValueError("triplet is collinear or numerically degenerate")

    a2 = ax * ax + ay * ay
    b2 = bx * bx + by * by
    c2 = cx * cx + cy * cy
    ux = (a2 * (by - cy) + b2 * (cy - ay) + c2 * (ay - by)) / det
    uy = (a2 * (cx - bx) + b2 * (ax - cx) + c2 * (bx - ax)) / det
    radius = math.hypot(ax - ux, ay - uy)
    _positive(radius, "radius")
    return Circumcircle2D(ux, uy, radius, signed_double_area)


def triangle_circumradius_identity(a: Point2, b: Point2, c: Point2) -> float:
    """Independent R=abc/(4A) implementation for cross-checking."""
    ab = norm2((b[0] - a[0], b[1] - a[1]))
    bc = norm2((c[0] - b[0], c[1] - b[1]))
    ca = norm2((a[0] - c[0], a[1] - c[1]))
    signed_double_area = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    area = 0.5 * abs(signed_double_area)
    if area <= 1.0e-14:
        raise ValueError("triplet is collinear or numerically degenerate")
    return ab * bc * ca / (4.0 * area)


def local_osculating_circle_from_geographic_triplet(
    previous: GeoPoint,
    current: GeoPoint,
    following: GeoPoint,
    radius_km: float = EARTH_MEAN_RADIUS_KM,
) -> dict[str, object]:
    """Discrete local osculating circle for three nearby surface samples.

    The tangent-plane origin is fixed *a priori* to the middle trajectory sample,
    so there is no free projection-center parameter to tune for a preferred
    geometric constant.
    """
    previous_xy = tangent_xy_km(current, previous, radius_km)
    current_xy = (0.0, 0.0)
    following_xy = tangent_xy_km(current, following, radius_km)
    circle = circumcircle_2d(previous_xy, current_xy, following_xy)
    independent_radius = triangle_circumradius_identity(previous_xy, current_xy, following_xy)
    return {
        "schema": "rll.geomagnetism.local_osculating_circle.v1",
        "projection": "AZIMUTHAL_EQUIDISTANT_CENTERED_ON_MIDDLE_SAMPLE",
        "claim_allowed": False,
        "points_xy_km": {
            "previous": previous_xy,
            "current": current_xy,
            "following": following_xy,
        },
        "circle": circle.to_dict(),
        "independent_radius_km": independent_radius,
        "radius_identity_abs_error_km": abs(circle.radius - independent_radius),
        "boundary": "local tangent-plane discrete curvature; not a global spherical small-circle identity and not a gravity-assist energy model",
    }


def signed_turn_angle_local(a: Point2, b: Point2) -> float:
    """Signed smallest rotation carrying direction a to direction b."""
    if norm2(a) <= 0.0 or norm2(b) <= 0.0:
        raise ValueError("turn-angle vectors must be nonzero")
    cross = a[0] * b[1] - a[1] * b[0]
    dot = a[0] * b[0] + a[1] * b[1]
    return math.atan2(cross, dot)


def kinematic_turn_operator(incoming_tangent: Point2, delta_psi_rad: float) -> dict[str, object]:
    """Rotate a trajectory tangent without assigning a force/energy mechanism."""
    before = norm2(incoming_tangent)
    if before <= 0.0:
        raise ValueError("incoming_tangent must be nonzero")
    outgoing = rotate2(incoming_tangent, delta_psi_rad)
    after = norm2(outgoing)
    return {
        "incoming": incoming_tangent,
        "outgoing": outgoing,
        "delta_psi_rad": delta_psi_rad,
        "norm_before": before,
        "norm_after": after,
        "norm_abs_error": abs(after - before),
        "interpretation": "KINEMATIC_ROTATION_ONLY_NOT_GRAVITY_ASSIST",
        "claim_allowed": False,
    }
