#!/usr/bin/env python3
"""Deterministic validator for Appendix B: matrix/torus/sphere projection."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

SQRT3 = math.sqrt(3.0)
TAU = 2.0 * math.pi


def close(a: float, b: float, tol: float = 1e-12) -> bool:
    return math.isclose(a, b, rel_tol=0.0, abs_tol=tol)


def project(column: float, row: float) -> tuple[float, float]:
    return column + 0.5 * row, SQRT3 * 0.5 * row


def distance(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.hypot(b[0] - a[0], b[1] - a[1])


def torus(u: float, v: float, major_radius: float, minor_radius: float) -> tuple[float, float, float]:
    ring = major_radius + minor_radius * math.cos(v)
    return ring * math.cos(u), ring * math.sin(u), minor_radius * math.sin(v)


def norm3(point: tuple[float, float, float]) -> float:
    return math.sqrt(sum(value * value for value in point))


def line_discriminant(
    slope: float,
    intercept: float,
    major_radius: float,
    minor_radius: float,
) -> float:
    a = 1.0 + slope * slope
    b = 2.0 * (slope * intercept - major_radius)
    c = major_radius * major_radius + intercept * intercept - minor_radius * minor_radius
    return b * b - 4.0 * a * c


def validate() -> dict[str, object]:
    basis = ((1.0, 0.5), (0.0, SQRT3 / 2.0))
    determinant = basis[0][0] * basis[1][1] - basis[0][1] * basis[1][0]
    metric = ((1.0, 0.5), (0.5, 1.0))
    directions = ((1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1))
    triangle = (project(0, 0), project(1, 0), project(0, 1))

    major_radius, minor_radius = 3.0, 1.0
    meridian = [
        (
            major_radius + minor_radius * math.cos(math.pi / 2.0 + k * TAU / 3.0),
            minor_radius * math.sin(math.pi / 2.0 + k * TAU / 3.0),
        )
        for k in range(3)
    ]
    meridian_lengths = [
        distance(meridian[index], meridian[(index + 1) % 3])
        for index in range(3)
    ]

    slope_30 = 1.0 / SQRT3
    tangent_discriminants = []
    for slope in (slope_30, -slope_30):
        offset = minor_radius * math.sqrt(1.0 + slope * slope)
        for intercept in (
            -slope * major_radius + offset,
            -slope * major_radius - offset,
        ):
            tangent_discriminants.append(
                line_discriminant(slope, intercept, major_radius, minor_radius)
            )

    frequency = 3
    vertices = 10 * frequency * frequency + 2
    edges = 30 * frequency * frequency
    faces = 20 * frequency * frequency

    checks = {
        "basis_determinant": close(determinant, SQRT3 / 2.0),
        "metric": metric == ((1.0, 0.5), (0.5, 1.0)),
        "six_unit_neighbors": all(
            close(distance(project(0, 0), project(column, row)), 1.0)
            for column, row in directions
        ),
        "equilateral_cell": all(
            close(distance(triangle[index], triangle[(index + 1) % 3]), 1.0)
            for index in range(3)
        ),
        "matrix_A_40": 8 * 5 == 40,
        "matrix_B_21": 7 * 3 == 21,
        "tensor_840": 8 * 5 * 7 * 3 == 840,
        "torus_radial_inner": close(
            norm3(torus(0.0, math.pi, major_radius, minor_radius)),
            major_radius - minor_radius,
        ),
        "torus_radial_outer": close(
            norm3(torus(0.0, 0.0, major_radius, minor_radius)),
            major_radius + minor_radius,
        ),
        "meridian_triangle": all(
            close(length, SQRT3 * minor_radius) for length in meridian_lengths
        ),
        "square_common_radius": close(2.0 / 2.0, 1.0),
        "square_swept_radius": close(2.0 / math.sqrt(2.0), math.sqrt(2.0)),
        "thirty_degree_tangency": all(
            close(value, 0.0) for value in tangent_discriminants
        ),
        "icosphere_euler": vertices - edges + faces == 2,
        "poincare_half_turn": close((TAU * (1.0 / 2.0)) % TAU, math.pi),
    }

    passed = sum(bool(value) for value in checks.values())
    return {
        "schema": "rll.appendix.hex_matrix_projection.v1",
        "status": "PASS" if passed == len(checks) else "FAIL",
        "checks_total": len(checks),
        "checks_passed": passed,
        "checks_failed": len(checks) - passed,
        "checks": checks,
        "exact_geometry_state": "PASS" if passed == len(checks) else "FAIL",
        "physical_claims_state": "TOKEN_VAZIO",
        "claim_allowed": False,
        "guards": [
            "upper/lower meridian branches are semicircles, not parabolas",
            "R-r and R+r are Euclidean radial bounds, not torus geodesic distances",
            "30 degrees is an imposed tangent condition",
            "Poincare map is for declared linear T^2 flow, not the Poincare conjecture",
            "physical vortex, Venturi and cosmology remain outside validated scope",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output")
    args = parser.parse_args()
    report = validate()
    payload = json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
