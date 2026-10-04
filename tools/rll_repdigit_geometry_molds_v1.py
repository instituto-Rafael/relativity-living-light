#!/usr/bin/env python3
"""Exact repdigit/division and polygon/star molds for the RLL diagnostic branch.

Mathematical/representation layer only. No physical or cosmological claim is
created by these identities.
"""

from __future__ import annotations

from fractions import Fraction
from math import cos, gcd, pi, sin, sqrt

CLAIM_ALLOWED = False
PHYSICAL_ROLE = "TOKEN_VAZIO_PHYSICAL_ROLE"

INTEGER_MOLDS = (11, 18, 13, 21, 42)
SQRT5 = sqrt(5.0)
PHI = (1.0 + SQRT5) / 2.0
SQRT5_OVER_PI = SQRT5 / pi
SQRT_PI_OVER_5 = sqrt(pi / 5.0)
SQRT_PI_OVER_12 = sqrt(pi / 12.0)


def repdigit(digit: int, length: int) -> int:
    d = int(digit)
    n = int(length)
    if not 0 <= d <= 9:
        raise ValueError("digit must be in [0,9]")
    if n < 1:
        raise ValueError("length must be >= 1")
    return d * (10**n - 1) // 9


def division_mold(digit: int, length: int, divisor: int) -> dict[str, object]:
    numerator = repdigit(digit, length)
    d = int(divisor)
    if d == 0:
        raise ZeroDivisionError("divisor cannot be zero")
    q, r = divmod(numerator, abs(d))
    exact = Fraction(numerator, d)
    return {
        "digit": int(digit),
        "length": int(length),
        "numerator": numerator,
        "divisor": d,
        "integer_quotient_abs_divisor": q,
        "remainder_abs_divisor": r,
        "exact": str(exact),
        "fractional_remainder": str(Fraction(r, abs(d))),
    }


def seven_over_three_family(max_length: int = 6) -> tuple[dict[str, object], ...]:
    return tuple(division_mold(7, n, 3) for n in range(1, int(max_length) + 1))


def three_over_seven_family(max_length: int = 6) -> tuple[dict[str, object], ...]:
    return tuple(division_mold(3, n, 7) for n in range(1, int(max_length) + 1))


def seven_repdigit_mod3_orbit() -> tuple[int, ...]:
    """Remainders for 7,77,777,... modulo 3; period 3."""
    return tuple(repdigit(7, n) % 3 for n in range(1, 4))


def three_repdigit_mod7_orbit() -> tuple[int, ...]:
    """Six-cycle for 3,33,333,... modulo 7."""
    return tuple(repdigit(3, n) % 7 for n in range(1, 7))


def mod7_repdigit_transition(residue: int) -> int:
    """Appending digit 3: r -> (10r+3) mod 7 = (3r+3) mod 7."""
    return (3 * int(residue) + 3) % 7


def mod3_repdigit_transition(residue: int) -> int:
    """Appending digit 7: r -> (10r+7) mod 3 = r+1 mod 3."""
    return (int(residue) + 1) % 3


def regular_polygon_mold(n: int, radius: float = 1.0) -> dict[str, float | int]:
    sides = int(n)
    R = float(radius)
    if sides < 3 or R <= 0.0:
        raise ValueError("regular polygon requires n>=3 and radius>0")
    half = pi / sides
    return {
        "n": sides,
        "radius": R,
        "central_angle": 2.0 * half,
        "half_central_angle": half,
        "side": 2.0 * R * sin(half),
        "apothem": R * cos(half),
        "sector_area": pi * R * R / sides,
        "polygon_area": (sides / 2.0) * R * R * sin(2.0 * half),
    }


def integer_polygon_molds(radius: float = 1.0) -> dict[int, dict[str, float | int]]:
    return {n: regular_polygon_mold(n, radius) for n in INTEGER_MOLDS}


def star_polygon_mold(n: int, step: int, radius: float = 1.0) -> dict[str, float | int | bool]:
    sides = int(n)
    k = int(step)
    R = float(radius)
    if sides < 3 or not 1 <= k < sides or R <= 0.0:
        raise ValueError("invalid star-polygon parameters")
    cycles = gcd(sides, k)
    half_chord_angle = pi * k / sides
    return {
        "n": sides,
        "step": k,
        "radius": R,
        "component_count": cycles,
        "orbit_length": sides // cycles,
        "connected_single_cycle": cycles == 1,
        "step_angle": 2.0 * half_chord_angle,
        "half_chord_angle": half_chord_angle,
        "edge": 2.0 * R * sin(half_chord_angle),
        "chord_apothem_abs": abs(R * cos(half_chord_angle)),
    }


def pentagram_mold(radius: float = 1.0) -> dict[str, object]:
    base = regular_polygon_mold(5, radius)
    star = star_polygon_mold(5, 2, radius)
    ratio = float(star["edge"]) / float(base["side"])
    return {
        "base": base,
        "star_5_2": star,
        "diagonal_over_side": ratio,
        "phi": PHI,
        "sqrt5": SQRT5,
    }


def dodeca_mold(radius: float = 1.0) -> dict[str, object]:
    """Keep the 12-gon base separate from the connected dodecagram {12/5}."""
    return {
        "base_12_gon": regular_polygon_mold(12, radius),
        "dodecagram_12_5": star_polygon_mold(12, 5, radius),
    }


def area_root_molds() -> dict[str, object]:
    """Exact area-root/half-angle molds already present in the Crown crosswalk."""
    s5 = SQRT_PI_OVER_5
    s12 = SQRT_PI_OVER_12
    return {
        "sqrt5": SQRT5,
        "sqrt5_over_pi": SQRT5_OVER_PI,
        "s5_sqrt_pi_over_5": s5,
        "s12_sqrt_pi_over_12": s12,
        "s5_squared": s5 * s5,
        "s12_squared": s12 * s12,
        "s5_over_s12": s5 / s12,
        "expected_s5_over_s12": sqrt(12.0 / 5.0),
        "crown_bridge": (cos(pi / 6.0) * s12) / (sin(pi / 6.0) * s5),
        "expected_crown_bridge": SQRT5 / 2.0,
        "pentagon_half_central_angle": pi / 5.0,
        "dodecagon_half_central_angle": pi / 12.0,
        "physical_role": PHYSICAL_ROLE,
    }


def factor_molds() -> dict[int | str, tuple[int, ...] | int]:
    return {
        11: (11,),
        13: (13,),
        18: (2, 3, 3),
        21: (3, 7),
        42: (2, 3, 7),
        "1001=7*11*13": 7 * 11 * 13,
    }


def contract_receipt() -> dict[str, object]:
    return {
        "schema": "rll.repdigit_geometry_molds.v1",
        "claim_allowed": CLAIM_ALLOWED,
        "physical_role": PHYSICAL_ROLE,
        "seven_over_three_first6": seven_over_three_family(6),
        "three_over_seven_first6": three_over_seven_family(6),
        "seven_mod3_orbit": seven_repdigit_mod3_orbit(),
        "three_mod7_orbit": three_repdigit_mod7_orbit(),
        "mod7_fixed_point": 2,
        "integer_polygon_molds": integer_polygon_molds(),
        "factor_molds": factor_molds(),
        "area_root_molds": area_root_molds(),
        "pentagram": pentagram_mold(),
        "dodeca": dodeca_mold(),
        "boundary": "representation/geometric identity != physical cosmological mechanism",
    }


if __name__ == "__main__":
    import json

    print(json.dumps(contract_receipt(), indent=2, sort_keys=True))
