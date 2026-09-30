#!/usr/bin/env python3
"""Deterministic verifier for RLL geometric weave invariants V1.

Stdlib only. The verifier checks the mathematical scope declared in
docs/invariants/geometric_weave_invariants_v1.md and includes negative
controls for properties explicitly declared non-invariant.
"""
from __future__ import annotations

import json
import math
import platform
import sys
from typing import Any

TOL = 1e-12


def matmul(a, v):
    return (
        a[0][0] * v[0] + a[0][1] * v[1],
        a[1][0] * v[0] + a[1][1] * v[1],
    )


def add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1])


def norm(v):
    return math.hypot(v[0], v[1])


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1]


def det(a, b):
    return a[0] * b[1] - a[1] * b[0]


def rot(phi):
    c, s = math.cos(phi), math.sin(phi)
    return ((c, -s), (s, c))


def normang(x):
    return x % (2.0 * math.pi)


def pairwise_angle_diffs(xs):
    ds = []
    for i in range(len(xs)):
        for j in range(i + 1, len(xs)):
            d = abs(xs[j] - xs[i]) % (2.0 * math.pi)
            ds.append(min(d, 2.0 * math.pi - d))
    return sorted(ds)


def record(identifier: str, ok: bool, metrics: dict[str, Any], note: str):
    return {
        "id": identifier,
        "status": "PASS" if ok else "FAIL",
        "metrics": metrics,
        "note": note,
    }


def run() -> dict[str, Any]:
    checks = []

    errors = []
    vectors = [((1.2, -0.7), (-2.0, 3.1)), ((0.3, 2.2), (4.1, -1.3))]
    for u, v in vectors:
        for phi in (0.0, math.pi / 7.0, math.pi / 4.0, 1.2345):
            m = rot(phi)
            ru, rv = matmul(m, u), matmul(m, v)
            errors.extend(
                (
                    abs(norm(ru) - norm(u)),
                    abs(norm(sub(ru, rv)) - norm(sub(u, v))),
                    abs(dot(ru, rv) - dot(u, v)),
                    abs(abs(det(ru, rv)) - abs(det(u, v))),
                )
            )
    e = max(errors)
    checks.append(record("RLL-GWI-001", e < TOL, {"max_abs_error": e},
                         "rotation metric/angle/area invariants"))

    e = 0.0
    for n in (3, 4, 5, 6, 8):
        radius, scale = 2.7, 3.4
        apothem = radius * math.cos(math.pi / n)
        side = 2.0 * radius * math.sin(math.pi / n)
        e = max(
            e,
            abs((scale * apothem) / (scale * radius) - math.cos(math.pi / n)),
            abs((scale * side) / (2.0 * scale * radius) - math.sin(math.pi / n)),
        )
    a = 2.3
    radius = a / math.sqrt(3.0)
    height = math.sqrt(3.0) * a / 2.0
    inradius = radius / 2.0
    e = max(e, abs(height / a - math.sqrt(3.0) / 2.0),
            abs(height / radius - 1.5), abs(inradius / radius - 0.5))
    checks.append(record("RLL-GWI-002", e < TOL, {"max_abs_error": e},
                         "dimensionless ratios survive uniform scale"))

    e = 0.0
    for n in (3, 4, 5, 7, 8, 11):
        base = [2.0 * math.pi * k / n for k in range(n)]
        shifted = [normang(x + math.pi / n) for x in base]
        got = sorted(base + shifted)
        expected = sorted(math.pi * k / n for k in range(2 * n))
        e = max(e, max(abs(x - y) for x, y in zip(got, expected)))
    checks.append(record("RLL-GWI-003", e < TOL, {"max_angle_error_rad": e},
                         "V(P_n) union Rot(pi/n)V(P_n) gives 2n directions"))

    sequence = (3, 4, 6, 8, 5)
    product = 1.0
    for n in sequence:
        product *= math.cos(math.pi / n)
    r0, rm = 7.3, 7.3
    for n in sequence:
        rm *= math.cos(math.pi / n)
    e4 = abs(rm / r0 - product)
    e5 = abs((rm / r0) ** 2 - product ** 2)
    checks.append(record("RLL-GWI-004", e4 < TOL, {"abs_error": e4},
                         "normalized nested radius product"))
    checks.append(record("RLL-GWI-005", e5 < TOL, {"abs_error": e5},
                         "normalized nested area product"))

    affine = ((2.0, 0.5), (0.25, 1.5))
    p, d = (1.0, -2.0), (3.0, 1.0)
    q = add(p, (2.5 * d[0], 2.5 * d[1]))
    ap, ad, aq = matmul(affine, p), matmul(affine, d), matmul(affine, q)
    col_det = abs(det(sub(aq, ap), ad))
    parallel_det = abs(det(ad, matmul(affine, (12.0, 4.0))))
    ae1, ae2 = matmul(affine, (1.0, 0.0)), matmul(affine, (0.0, 1.0))
    angle_counterexample_cos = dot(ae1, ae2) / (norm(ae1) * norm(ae2))
    length_ratio_counterexample = norm(ae1) / norm(ae2)
    ok = (
        col_det < TOL
        and parallel_det < TOL
        and abs(angle_counterexample_cos) > 1e-3
        and abs(length_ratio_counterexample - 1.0) > 1e-3
    )
    checks.append(record(
        "RLL-GWI-006",
        ok,
        {
            "collinearity_det": col_det,
            "parallel_det": parallel_det,
            "angle_negative_control_cos": angle_counterexample_cos,
            "length_ratio_negative_control": length_ratio_counterexample,
        },
        "affine map preserves incidence/parallelism but not Euclidean angle/length ratio generally",
    ))

    e7 = e8 = 0.0
    for deg in (0, 15, 30, 45, 60, 75):
        inc = math.radians(deg)
        major = 3.7
        minor = major * abs(math.cos(inc))
        ecc = abs(math.sin(inc))
        e7 = max(e7, abs(minor / major - abs(math.cos(inc))),
                 abs(ecc * ecc + (minor / major) ** 2 - 1.0))
        for radius in (1.0, 2.5, 7.3):
            e8 = max(e8, abs((radius * abs(math.cos(inc))) / radius
                             - abs(math.cos(inc))))
    checks.append(record("RLL-GWI-007", e7 < TOL, {"max_abs_error": e7},
                         "orthographic circle-to-ellipse signature"))
    checks.append(record("RLL-GWI-008", e8 < TOL, {"max_abs_error": e8},
                         "shared b/a anisotropy for concentric circles"))

    length = 5.2
    r_cap = length / math.sqrt(2.0 + math.sqrt(2.0))
    s_hull = length * math.sqrt((2.0 - math.sqrt(2.0)) / 2.0)
    phi, scale = 0.731, 2.9
    m = rot(phi)
    radial = (r_cap * math.cos(math.pi / 8.0), r_cap * math.sin(math.pi / 8.0))
    hull_side = (s_hull * math.cos(5.0 * math.pi / 8.0),
                 s_hull * math.sin(5.0 * math.pi / 8.0))
    radial_sim = tuple(scale * x for x in matmul(m, radial))
    hull_sim = tuple(scale * x for x in matmul(m, hull_side))
    base_diff = abs(r_cap - s_hull)
    similarity_diff = abs(norm(radial_sim) - norm(hull_sim))
    anisotropic = ((2.0, 0.0), (0.0, 1.0))
    anisotropic_ratio = norm(matmul(anisotropic, radial)) / norm(
        matmul(anisotropic, hull_side)
    )
    ok = base_diff < TOL and similarity_diff < TOL and abs(anisotropic_ratio - 1.0) > 1e-3
    checks.append(record(
        "RLL-GWI-009",
        ok,
        {
            "base_abs_diff": base_diff,
            "similarity_abs_diff": similarity_diff,
            "anisotropic_negative_control_ratio": anisotropic_ratio,
        },
        "R_cap=s_hull survives similarities; anisotropic scaling breaks it in this counterexample",
    ))

    classes = (0.0, math.pi / 4.0, math.pi / 2.0, 3.0 * math.pi / 4.0)
    phi = 0.317
    before = pairwise_angle_diffs(classes)
    after = pairwise_angle_diffs([normang(x + phi) for x in classes])
    e10 = max(abs(x - y) for x, y in zip(before, after))
    checks.append(record("RLL-GWI-010", e10 < TOL,
                         {"max_pairwise_angle_diff_error": e10},
                         "relative direction classes survive global rotation"))

    passed = sum(x["status"] == "PASS" for x in checks)
    return {
        "schema": "rll.geometric_weave_invariants.execution.v1",
        "tolerance": TOL,
        "runtime": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
        },
        "summary": {
            "checks": len(checks),
            "pass": passed,
            "fail": len(checks) - passed,
            "claim_allowed": False,
            "scope": "mathematical invariant checks only",
        },
        "checks": checks,
        "external_gates": {
            "prior_art": "TOKEN_VAZIO",
            "image_calibration": "TOKEN_VAZIO",
            "independent_reproduction": "NOT_RUN",
            "physical_binding": "TOKEN_VAZIO_BLOCKED",
        },
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
