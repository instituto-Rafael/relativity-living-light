#!/usr/bin/env python3
"""RLL session geometry closure V1.

Bounded executable helpers for the mathematical relations introduced in the
current longitudinal geometry session.  This module deliberately does not bind
these relations to RLL physics.
"""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from typing import Dict, List, Optional, Tuple

CLAIM_ALLOWED = False
PHYSICAL_BINDING = "TOKEN_VAZIO_PHYSICAL_BINDING"
IMAGE_METRIC_ROLE = "TOKEN_VAZIO_CALIBRATION"
DRAWING_ROLE = "DRAWING_TOPOLOGY_ONLY"


@dataclass(frozen=True)
class RotatedSquareFamily:
    n_orientations: int
    sides: int
    apothem: float
    central_angle: float
    side: float
    perimeter: float
    area: float
    normalized_area_outer_square: float


def phase_point(n: int, modulus: int) -> Tuple[int, float, float, float]:
    """Return residue, phase, cos phase and sin phase for a finite phase carrier."""
    if modulus <= 0:
        raise ValueError("modulus must be positive")
    residue = n % modulus
    theta = 2.0 * math.pi * residue / modulus
    return residue, theta, math.cos(theta), math.sin(theta)


def chord(radius: float, n: int, k: int = 1) -> float:
    if radius < 0 or n < 2:
        raise ValueError("radius must be nonnegative and n >= 2")
    return 2.0 * radius * math.sin(k * math.pi / n)


def chord_index(n: int, k: int) -> float:
    if n < 3:
        raise ValueError("n must be >= 3")
    den = math.sin(math.pi / n)
    return math.sin(k * math.pi / n) / den


def lambda_n(n: int) -> float:
    if n < 3:
        raise ValueError("n must be >= 3")
    return 2.0 * math.cos(math.pi / n)


def regular_polygon_perimeter(radius: float, n: int) -> float:
    return n * chord(radius, n, 1)


def regular_polygon_area(radius: float, n: int) -> float:
    if radius < 0 or n < 3:
        raise ValueError("radius must be nonnegative and n >= 3")
    return 0.5 * n * radius * radius * math.sin(2.0 * math.pi / n)


def circularity_regular_polygon(n: int) -> float:
    if n < 3:
        raise ValueError("n must be >= 3")
    x = math.pi / n
    return x / math.tan(x)


def isosceles_from_circle(radius: float, theta: float) -> Dict[str, float]:
    if radius < 0:
        raise ValueError("radius must be nonnegative")
    base = 2.0 * radius * math.sin(theta / 2.0)
    height = radius * math.cos(theta / 2.0)
    area = 0.5 * radius * radius * math.sin(theta)
    perimeter = 2.0 * radius + base
    return {
        "base": base,
        "height": height,
        "area": area,
        "perimeter": perimeter,
        "perimeter_over_radius": perimeter / radius if radius else math.nan,
    }


def arc_chord_index(theta: float) -> float:
    if theta == 0.0:
        return 1.0
    den = 2.0 * math.sin(theta / 2.0)
    if den == 0.0:
        raise ValueError("degenerate chord")
    return theta / den


def annular_sector(radius_outer: float, radius_inner: float, theta: float) -> Dict[str, float | bool]:
    """Return chord/sector/tangent models with K=(R^2-r^2)/2."""
    if radius_outer <= radius_inner or radius_inner < 0:
        raise ValueError("require R > r >= 0")
    k = (radius_outer * radius_outer - radius_inner * radius_inner) / 2.0
    chord_model = k * math.sin(theta)
    sector = k * theta
    tangent_model = k * math.tan(theta)
    acute = 0.0 < theta < math.pi / 2.0
    sandwich = acute and chord_model < sector < tangent_model
    return {
        "K": k,
        "chord_trapezoid": chord_model,
        "annular_sector": sector,
        "tangent_model": tangent_model,
        "acute_domain": acute,
        "sandwich_holds": sandwich,
        "curve_minus_chord": sector - chord_model,
        "tangent_minus_curve": tangent_model - sector,
    }


def rotate_point(x: float, y: float, theta: float) -> Tuple[float, float]:
    c, s = math.cos(theta), math.sin(theta)
    return x * c - y * s, x * s + y * c


def project_point(x: float, y: float, alpha: float) -> float:
    return x * math.cos(alpha) + y * math.sin(alpha)


def square_projection_width(side: float, theta: float) -> float:
    if side < 0:
        raise ValueError("side must be nonnegative")
    return side * (abs(math.cos(theta)) + abs(math.sin(theta)))


def inscribed_rotated_square_side(outer_side: float, theta: float) -> float:
    if outer_side < 0:
        raise ValueError("outer_side must be nonnegative")
    den = abs(math.cos(theta)) + abs(math.sin(theta))
    if den == 0.0:
        raise ValueError("invalid projection denominator")
    return outer_side / den


def rotated_square_family(n_orientations: int, apothem: float = 1.0) -> RotatedSquareFamily:
    """Intersection of N equally rotated centered squares of common apothem.

    Orientations are k*pi/(2N), k=0..N-1. Their union of support normals
    defines a regular 4N-gon circumscribed about the apothem circle.
    """
    if n_orientations < 1 or apothem <= 0:
        raise ValueError("N >= 1 and apothem > 0 required")
    n = n_orientations
    half_sector = math.pi / (4.0 * n)
    side = 2.0 * apothem * math.tan(half_sector)
    perimeter = 4.0 * n * side
    area = 4.0 * n * apothem * apothem * math.tan(half_sector)
    outer_square_side = 2.0 * apothem
    return RotatedSquareFamily(
        n_orientations=n,
        sides=4 * n,
        apothem=apothem,
        central_angle=math.pi / (2.0 * n),
        side=side,
        perimeter=perimeter,
        area=area,
        normalized_area_outer_square=area / (outer_square_side * outer_square_side),
    )


def kappa_regular_polygon(n: int) -> float:
    """I_z/(M R^2) for a uniform regular n-gon plate, circumradius R."""
    if n < 3:
        raise ValueError("n must be >= 3")
    return (2.0 + math.cos(2.0 * math.pi / n)) / 6.0


def kappa_from_lambda(lam: float) -> float:
    return (lam * lam + 2.0) / 12.0


def iterated_log(x: float, base: float, max_steps: int = 32) -> Dict[str, object]:
    """Iterate real log until the next real-domain input is unavailable."""
    if x <= 0.0:
        raise ValueError("x must start positive")
    if base <= 0.0 or base == 1.0:
        raise ValueError("log base must be positive and != 1")
    if max_steps < 1:
        raise ValueError("max_steps must be positive")
    values: List[float] = []
    value = x
    state = "MAX_STEPS"
    for _ in range(max_steps):
        if value <= 0.0:
            state = "STOP_REAL_DOMAIN"
            break
        value = math.log(value, base)
        values.append(value)
        if value <= 0.0:
            state = "STOP_REAL_DOMAIN"
            break
    return {"base": base, "values": values, "state": state}


def star_winding(n: int, k: int) -> Dict[str, int | float]:
    if n < 3 or k <= 0 or k >= n:
        raise ValueError("require n >= 3 and 0 < k < n")
    g = math.gcd(n, k)
    return {
        "n": n,
        "k": k,
        "components": g,
        "orbit_length": n // g,
        "step_angle": 2.0 * math.pi * k / n,
        "winding_per_connected_orbit": k // g,
    }


def receipt() -> Dict[str, object]:
    phi = (1.0 + math.sqrt(5.0)) / 2.0
    square2 = rotated_square_family(2)
    square3 = rotated_square_family(3)
    return {
        "contract": "RLL_SESSION_GEOMETRY_CLOSURE_V1",
        "claim_allowed": CLAIM_ALLOWED,
        "physical_binding": PHYSICAL_BINDING,
        "drawing_role": DRAWING_ROLE,
        "image_metric_role": IMAGE_METRIC_ROLE,
        "gates": {
            "lambda4_sqrt2": math.isclose(lambda_n(4), math.sqrt(2.0), rel_tol=1e-12),
            "lambda5_phi": math.isclose(lambda_n(5), phi, rel_tol=1e-12),
            "lambda6_sqrt3": math.isclose(lambda_n(6), math.sqrt(3.0), rel_tol=1e-12),
            "kappa_lambda_square": math.isclose(kappa_regular_polygon(4), kappa_from_lambda(lambda_n(4)), rel_tol=1e-12),
            "square2_exact": math.isclose(square2.normalized_area_outer_square, 2.0 * (math.sqrt(2.0) - 1.0), rel_tol=1e-12),
            "square3_exact": math.isclose(square3.normalized_area_outer_square, 3.0 * (2.0 - math.sqrt(3.0)), rel_tol=1e-12),
            "annular_sandwich": bool(annular_sector(2.0, 1.0, math.pi / 6.0)["sandwich_holds"]),
            "pentagram_winding2": star_winding(5, 2)["winding_per_connected_orbit"] == 2,
            "zero_residue_is_defined": phase_point(21, 7)[0] == 0,
        },
        "snapshots": {
            "rotated_square_N2": asdict(square2),
            "rotated_square_N3": asdict(square3),
            "natural_log_999": iterated_log(999.0, math.e, 8),
            "base10_log_999": iterated_log(999.0, 10.0, 8),
        },
    }


def main() -> None:
    data = receipt()
    if not all(data["gates"].values()):
        raise SystemExit("closure gate failure")
    print(json.dumps(data, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
