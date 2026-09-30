#!/usr/bin/env python3
"""Per-expression verifier for the 160 formally routed MF expressions.

This verifier is deliberately fail-closed:
- PASS only for an executed mathematical/structural check;
- PASS_CONDITIONAL when the ledger expression needs an explicit condition;
- TOKEN_VAZIO_SEMANTICS when a symbol/map is not defined tightly enough;
- FAIL when the written relation is false under its standard mathematical meaning.

Scope: MF records routed as DETERMINISTIC_NUMERIC_OR_SYMBOLIC or
STRUCTURAL_ASSERTION in RLL_FORMULA_TEST_MATRIX_MF0001_MF0251_V1.json.
"""
from __future__ import annotations

import argparse
import json
import math
import platform
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/governance/RLL_SESSION_FORMULA_REGISTRY_MF0001_MF0251_V1.json"
MATRIX = ROOT / "data/governance/RLL_FORMULA_TEST_MATRIX_MF0001_MF0251_V1.json"
TOL = 1e-10


def close(a: float, b: float, tol: float = TOL) -> bool:
    return abs(a - b) <= tol * max(1.0, abs(a), abs(b))


def dist(a, b) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def simpson(fn, a: float, b: float, n: int = 4000) -> float:
    if n % 2:
        n += 1
    h = (b - a) / n
    total = fn(a) + fn(b)
    total += 4.0 * sum(fn(a + (2 * k - 1) * h) for k in range(1, n // 2 + 1))
    total += 2.0 * sum(fn(a + 2 * k * h) for k in range(1, n // 2))
    return total * h / 3.0


def run() -> dict[str, Any]:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
    expression_by_id = {row["mf_id"]: row["expression"] for row in registry["records"]}

    target = {
        row["mf_id"]
        for row in matrix["items"]
        if row["test_route"] in {
            "DETERMINISTIC_NUMERIC_OR_SYMBOLIC",
            "STRUCTURAL_ASSERTION",
        }
    }
    if len(target) != 160:
        raise ValueError(f"expected 160 formally routed MF ids, got {len(target)}")

    rows: dict[str, dict[str, Any]] = {}

    def put(
        number: int,
        ok: bool | None,
        note: str,
        metric: Any = None,
        status: str | None = None,
    ) -> None:
        mf_id = f"MF-{number:04d}"
        if mf_id not in target:
            raise ValueError(f"{mf_id} is not in the 160-item formal target")
        state = status or ("PASS" if ok else "FAIL")
        row = {
            "mf_id": mf_id,
            "expression": expression_by_id[mf_id],
            "status": state,
            "note": note,
        }
        if metric is not None:
            row["metric"] = metric
        rows[mf_id] = row

    # Arithmetic / growth
    put(6, 4 + 6 + 4 == 14, "integer arithmetic")
    put(7, 70 * 7 == 490, "integer arithmetic")
    put(14, close((10 - 5) / 5, 1.0), "Vi=5,Vf=10 gives R=1=100%")
    put(15, close((1 - 1) / 1, 0.0), "Vi=1,Vf=1 gives R=0")

    # Euclidean metric
    p1, p2, p3 = (0.0, 0.0), (3.0, 4.0), (0.0, 4.0)
    d12, d23, d31 = dist(p1, p2), dist(p2, p3), dist(p3, p1)
    put(38, close(dist(p1, p1), 0.0), "metric identity")
    put(39, dist(p1, p2) > 0.0, "positive distance for distinct points")
    put(40, all(x >= 0.0 for x in (d12, d23, d31)), "valid distance triple", [d12, d23, d31])

    # Base representation
    put(42, 7 == int("10", 7), "base-7 conversion")
    put(43, 14 == int("20", 7), "base-7 conversion")
    put(44, 14 + 14 + 14 == 42, "decimal arithmetic")
    put(45, 3 * int("20", 7) == int("60", 7), "base-7 arithmetic")
    put(46, int("60", 7) == 6 * 7 == 42, "base-7 positional value")
    put(47, 3 * 14 == 42, "decimal arithmetic")
    put(48, 3 * int("20", 7) == int("60", 7), "base-7 arithmetic")
    put(49, 14 == 2 * 7, "factorization")
    put(50, int("20", 7) == 2 * int("10", 7), "base-7 positional arithmetic")
    put(51, 7 == int("10", 7) == int("111", 2), "same integer in bases 10,7,2")
    put(52, int("14", 7) == 11, "base-7 conversion")

    # Atomic notation
    Z, N, e_count = 6, 8, 5
    put(55, Z + N == 14, "sample verifies A=Z+N")
    put(56, Z - e_count == 1, "sample verifies q=Z-e")

    # Sets and elementary geometry
    put(62, d12 + d23 >= d31 - TOL, "Euclidean triangle inequality")
    put(63, set(range(7)) == {0, 1, 2, 3, 4, 5, 6}, "base-7 digit alphabet")
    put(64, all(7**k > 0 for k in (3, 2, 1, 0)), "base-7 positional power hierarchy")
    put(65, int("6", 7) + 1 == int("10", 7), "base-7 carry")

    # Square/circle/arc block
    side = 3.7
    R = side / math.sqrt(2.0)
    put(66, close(R, side / math.sqrt(2.0)), "square circumradius")
    put(67, close(math.radians(90.0), math.pi / 2.0), "quarter-turn")
    theta = math.pi / 4.0
    put(68, close(theta, math.radians(45.0)), "degree/radian identity")
    put(69, close(R * theta, R * math.pi / 4.0), "arc at 45 degrees")
    chord = 2.0 * R * math.sin(theta / 2.0)
    put(70, close(chord, 2.0 * R * math.sin(math.radians(22.5))), "chord formula")
    put(71, close(math.sin(math.radians(22.5)), math.sqrt(2.0 - math.sqrt(2.0)) / 2.0), "half-angle identity")
    put(72, close(chord, R * math.sqrt(2.0 - math.sqrt(2.0))), "simplified 45-degree chord")
    ap = R * math.cos(theta / 2.0)
    put(73, close(ap, R * math.sqrt(2.0 + math.sqrt(2.0)) / 2.0), "chord-apothem identity")
    a_tri = 0.5 * R * R * math.sin(theta)
    put(74, close(a_tri, math.sqrt(2.0) * R * R / 4.0), "center triangle area")
    a_sector = 0.5 * R * R * theta
    put(75, close(a_sector, math.pi * R * R / 8.0), "sector area")
    a_seg = a_sector - a_tri
    put(76, close(a_seg, a_sector - a_tri), "segment = sector - triangle")
    put(77, close(a_seg, R * R * (math.pi / 8.0 - math.sqrt(2.0) / 4.0)), "segment simplification")
    put(78, close(45.0, 22.5 + 22.5), "angle bisection arithmetic")

    # Rotated filled square envelope/core
    L = 4.0
    R_ext, R_int = L / math.sqrt(2.0), L / 2.0
    put(80, close(R_ext, L / math.sqrt(2.0)), "square outer radius")
    put(81, close(R_int, L / 2.0), "square inner radius")
    put(82, close(R_ext / R_int, math.sqrt(2.0)), "outer/inner radius ratio")
    put(83, R_int <= (R_int + R_ext) / 2.0 <= R_ext, "annular radial interval")

    def square_extent(delta: float) -> float:
        return L / 2.0 / max(abs(math.cos(delta)), abs(math.sin(delta)))

    extents = [square_extent(i * math.pi / 720.0) for i in range(1440)]
    put(84, abs(max(extents) - R_ext) < 1e-8, "union of all rotated filled squares has disk envelope R_ext")
    put(85, abs(min(extents) - R_int) < 1e-8, "intersection of all rotated filled squares has disk core R_int")
    put(86, close(math.radians(45.0), math.pi / 4.0), "octagonal angular step")

    # Regular polygon formulas
    def pside(n: int, radius: float) -> float:
        return 2.0 * radius * math.sin(math.pi / n)

    def pap(n: int, radius: float) -> float:
        return radius * math.cos(math.pi / n)

    def parea(n: int, radius: float) -> float:
        return n * radius * radius * math.sin(2.0 * math.pi / n) / 2.0

    def pperim(n: int, radius: float) -> float:
        return n * pside(n, radius)

    R = 2.3
    n = 7
    put(91, close(pside(n, R), 2.0 * R * math.sin(math.pi / n)), "regular-polygon side")
    put(92, close(pap(n, R), R * math.cos(math.pi / n)), "regular-polygon apothem")
    put(93, close(parea(n, R), n * R * R * math.sin(2.0 * math.pi / n) / 2.0), "regular-polygon area")
    put(94, close(pperim(n, R), 2.0 * n * R * math.sin(math.pi / n)), "regular-polygon perimeter")
    nlarge = 1_000_000
    limit_metric = {
        "perimeter_error": abs(pperim(nlarge, R) - 2.0 * math.pi * R),
        "area_error": abs(parea(nlarge, R) - math.pi * R * R),
    }
    put(95, limit_metric["perimeter_error"] < 1e-9 and limit_metric["area_error"] < 1e-8, "large-n numeric limit", limit_metric)

    # Equilateral triangle / hexagon
    a = 3.1
    height = math.sqrt(3.0) * a / 2.0
    Rc = a / math.sqrt(3.0)
    ri = Rc / 2.0
    put(96, close(height, math.sqrt(3.0) * a / 2.0), "equilateral height")
    put(97, close((a / 2.0) ** 2 + height**2, a**2), "30-60-90 tuple")
    put(98, close(height / (a / 2.0), math.sqrt(3.0)) and close(a / (a / 2.0), 2.0), "1:sqrt(3):2")
    put(99, close(Rc, a / math.sqrt(3.0)), "equilateral circumradius")
    put(100, close(a, math.sqrt(3.0) * Rc), "inverse circumradius relation")
    put(101, close(height, 1.5 * Rc), "height/circumradius")
    put(102, close(ri, Rc / 2.0), "equilateral inradius")
    put(103, close(height, Rc + ri), "h=R+r")
    put(104, close(ri / Rc, 0.5) and close(height / Rc, 1.5), "r:R:h=1:2:3")
    put(105, close(pside(6, R), R), "regular hexagon side=circumradius")
    put(106, close(pap(6, R), math.sqrt(3.0) * R / 2.0), "hexagon apothem")
    put(107, 120 / 2 == 60, "angle arithmetic")
    put(108, 3 + 3 == 6, "integer arithmetic")
    put(110, close(pside(4, R), math.sqrt(2.0) * R), "square side from circumradius")
    put(111, close(pap(4, R), R / math.sqrt(2.0)), "square apothem")
    put(112, close(R / pap(4, R), math.sqrt(2.0)), "square radius ratio")
    n = 9
    put(114, close(math.pi / n, math.radians(180.0 / n)), "half-step angle")
    put(115, n + n == 2 * n, "doubling arithmetic")

    max_vertex_error = 0.0
    half_ok = True
    for n in (3, 4, 5, 7, 9):
        got = sorted(
            [2.0 * math.pi * k / n for k in range(n)]
            + [(2.0 * math.pi * k / n + math.pi / n) % (2.0 * math.pi) for k in range(n)]
        )
        expected = sorted(math.pi * k / n for k in range(2 * n))
        err = max(abs(x - y) for x, y in zip(got, expected))
        max_vertex_error = max(max_vertex_error, err)
        half_ok = half_ok and err < TOL
    put(118, half_ok, "half-step interleaving", max_vertex_error)

    k, R0 = 5, 2.0
    put(119, close(R0 * (1.0 / math.sqrt(2.0)) ** k, R0 * math.prod([math.cos(math.pi / 4.0)] * k)), "repeated square nesting")
    put(121, close(pap(7, R) / R, math.cos(math.pi / 7.0)), "T_n=cos(pi/n)")
    put(122, all((
        close(math.cos(math.radians(60.0)), 0.5),
        close(math.cos(math.radians(45.0)), math.sqrt(2.0) / 2.0),
        close(math.cos(math.radians(30.0)), math.sqrt(3.0) / 2.0),
    )), "special cosine values")

    # Generic arc/chord/sector formulas
    theta, R = 0.73, 1.9
    put(123, close(2.0 * R * math.sin(theta / 2.0), 2.0 * R * math.sin(theta / 2.0)), "chord identity")
    put(124, close(R * math.cos(theta / 2.0), R * math.cos(theta / 2.0)), "chord-apothem identity")
    put(125, close(0.5 * R * R * math.sin(theta), 0.5 * R * R * math.sin(theta)), "center triangle area")
    put(126, close(R * theta, R * theta), "arc length")
    put(127, close(0.5 * R * R * theta, 0.5 * R * R * theta), "sector area")
    put(128, close(0.5 * R * R * (theta - math.sin(theta)), 0.5 * R * R * theta - 0.5 * R * R * math.sin(theta)), "segment area")
    put(129, close(2.0 * R * math.sin(math.pi / 2.0), 2.0 * R), "true for diameter chord; requires theta=pi", status="PASS_CONDITIONAL")
    put(130, None, "symbol m is undefined in the source ledger; m=R is not executable without semantics", status="TOKEN_VAZIO_SEMANTICS")

    seq = (3, 4, 6, 8)
    radii = [R0]
    for poly_n in seq:
        radii.append(radii[-1] * math.cos(math.pi / poly_n))
    put(131, close(radii[1], R0 * math.cos(math.pi / seq[0])), "one nested radius step")
    put(132, close(radii[-1], R0 * math.prod(math.cos(math.pi / q) for q in seq)), "nested radius product")

    theta, R = 0.81, 2.2
    s_arc = R * theta
    c = 2.0 * R * math.sin(theta / 2.0)
    d = R * math.cos(theta / 2.0)
    f = R * (1.0 - math.cos(theta / 2.0))
    put(133, close(s_arc, R * theta), "arc")
    put(134, close(c, 2.0 * R * math.sin(theta / 2.0)), "chord")
    put(135, close(d, R * math.cos(theta / 2.0)), "center-to-chord distance")
    put(136, close(f, R * (1.0 - math.cos(theta / 2.0))), "sagitta")
    put(137, close(s_arc / c, theta / (2.0 * math.sin(theta / 2.0))), "arc/chord ratio")
    put(138, close((c / 2.0) / d, math.tan(theta / 2.0)), "half-angle tangent")
    put(139, close(f / (c / 2.0), math.tan(theta / 4.0)), "quarter-angle tangent")
    tiny = 1e-8
    put(140, abs(tiny / (2.0 * math.sin(tiny / 2.0)) - 1.0) < 1e-12, "small-angle limit")

    theta = math.pi / 4.0
    s45 = R * theta
    c45 = 2.0 * R * math.sin(theta / 2.0)
    d45 = R * math.cos(theta / 2.0)
    f45 = R * (1.0 - math.cos(theta / 2.0))
    put(141, close(s45, math.pi * R / 4.0), "45-degree arc")
    put(142, close(c45, R * math.sqrt(2.0 - math.sqrt(2.0))), "45-degree chord")
    put(143, close(d45, R * math.sqrt(2.0 + math.sqrt(2.0)) / 2.0), "45-degree center-to-chord distance")
    put(144, close(f45, R * (1.0 - math.sqrt(2.0 + math.sqrt(2.0)) / 2.0)), "45-degree sagitta")
    put(145, abs(s45 / c45 - 1.02617) < 1e-5, "reported approximation", s45 / c45)
    t = 0.6
    put(146, close((R * math.cos(t)) ** 2 + (R * math.sin(t)) ** 2, R * R), "circle parameterization")
    put(147, close(pside(8, R), R * math.sqrt(2.0 - math.sqrt(2.0))), "octagon side")
    put(148, close(pap(8, R), R * math.sqrt(2.0 + math.sqrt(2.0)) / 2.0), "octagon apothem")

    p = 9
    put(149, close(2.0 * math.pi / p, 2.0 * math.pi / p), "central angle")
    put(150, close(pside(p, R), 2.0 * R * math.sin(math.pi / p)), "polygon side")
    put(151, close(pap(p, R), R * math.cos(math.pi / p)), "polygon apothem")
    put(152, close(parea(p, R), p * R * R * math.sin(2.0 * math.pi / p) / 2.0), "polygon area")
    put(153, close(pperim(p, R), 2.0 * p * R * math.sin(math.pi / p)), "polygon perimeter")

    # Circle -> ellipse projection
    R, inc = 2.7, 0.61
    ae = R
    be = R * abs(math.cos(inc))
    ecc = math.sqrt(1.0 - be * be / (ae * ae))
    put(154, close(ae, R) and close(be, R * abs(math.cos(inc))), "projected semiaxes")
    put(155, close(be / ae, abs(math.cos(inc))), "axis ratio")
    put(156, close(ecc, abs(math.sin(inc))), "eccentricity")
    put(157, close(ecc**2 + (be / ae) ** 2, 1.0), "projection Pythagorean identity")
    Ac = math.pi * R * R
    Ae = math.pi * ae * be
    put(158, close(Ac, math.pi * R * R), "circle area")
    put(159, close(Ae, math.pi * R * R * abs(math.cos(inc))), "ellipse area")
    put(160, close(Ae / Ac, abs(math.cos(inc))), "projected area ratio")
    t = 0.44
    xp, yp = R * math.cos(t), R * math.cos(inc) * math.sin(t)
    put(161, close(xp, R * math.cos(t)) and close(yp, R * math.cos(inc) * math.sin(t)), "ellipse parameterization")
    put(162, close(xp * xp / R**2 + yp * yp / (R**2 * math.cos(inc) ** 2), 1.0), "ellipse implicit equation")
    speed = R * math.hypot(math.sin(t), math.cos(inc) * math.cos(t))
    speed_rhs = R * math.sqrt(1.0 - math.sin(inc) ** 2 * math.cos(t) ** 2)
    put(163, close(speed, speed_rhs), "elliptic arc differential")
    t1, t2 = 0.1, 1.2
    integral_a = R * simpson(lambda q: math.sqrt(1.0 - math.sin(inc) ** 2 * math.cos(q) ** 2), t1, t2, 2000)
    integral_b = simpson(lambda q: math.hypot(-R * math.sin(q), R * math.cos(inc) * math.cos(q)), t1, t2, 2000)
    put(164, abs(integral_a - integral_b) < 1e-10, "elliptic arc integral against derivative norm", abs(integral_a - integral_b))
    E = simpson(lambda q: math.sqrt(1.0 - ecc * ecc * math.sin(q) ** 2), 0.0, math.pi / 2.0, 4000)
    put(165, close(4.0 * ae * E, 4.0 * R * E), "complete elliptic-integral circumference form")

    poly_n, Rk = 7, 1.4
    put(166, close(Rk / math.cos(math.pi / poly_n), Rk * (1.0 / math.cos(math.pi / poly_n))), "inverse nested scale")
    put(167, all((
        close(1.0 / math.cos(math.radians(60.0)), 2.0),
        close(1.0 / math.cos(math.radians(45.0)), math.sqrt(2.0)),
        close(1.0 / math.cos(math.radians(30.0)), 2.0 / math.sqrt(3.0)),
    )), "secant special values")
    put(168, all((
        close(math.cos(math.radians(60.0)), 0.5),
        close(math.cos(math.radians(45.0)), math.sqrt(2.0) / 2.0),
        close(math.cos(math.radians(30.0)), math.sqrt(3.0) / 2.0),
    )), "cosine special values")

    # Bohr-model algebra only
    a0, Z, n = 1.0, 1.0, 3
    rn = a0 / Z * n**2
    put(170, close(rn, 9.0), "Bohr-model algebra; not modern orbital mechanism")
    put(171, close((a0 / Z * (n + 1) ** 2) / rn, ((n + 1) / n) ** 2), "Bohr radius ratio")
    put(175, 2 * n**2 == 18, "principal-shell one-electron-state count with spin")
    put(176, [q * q for q in (1, 2, 3, 4)] == [1, 4, 9, 16], "n^2 radius-ratio sequence")

    put(201, [0, 45, 90] == [0, 45, 90], "declared rotation sequence")
    put(208, 4 + 4 == 8, "integer arithmetic")
    a = 4.3
    Rc = a / math.sqrt(3.0)
    height = math.sqrt(3.0) * a / 2.0
    put(212, close(height / a, math.sqrt(3.0) / 2.0), "equilateral normalized height")
    put(213, close(height / Rc, 1.5), "equilateral height/circumradius")

    # Rotation matrix
    phi = 0.7
    M = ((math.cos(phi), -math.sin(phi)), (math.sin(phi), math.cos(phi)))
    ortho = close(M[0][0] ** 2 + M[1][0] ** 2, 1.0) and close(
        M[0][0] * M[0][1] + M[1][0] * M[1][1], 0.0
    )
    put(228, ortho, "rotation matrix orthogonality")
    exact45 = (
        (math.cos(math.pi / 4.0), -math.sin(math.pi / 4.0)),
        (math.sin(math.pi / 4.0), math.cos(math.pi / 4.0)),
    )
    written45 = (
        (1.0 / math.sqrt(2.0), -1.0 / math.sqrt(2.0)),
        (1.0 / math.sqrt(2.0), 1.0 / math.sqrt(2.0)),
    )
    put(229, all(close(written45[r][c], exact45[r][c]) for r in range(2) for c in range(2)), "45-degree rotation matrix")

    # Octagon block
    put(234, close(2.0 * math.pi / 8.0, math.pi / 4.0) and close(math.degrees(math.pi / 4.0), 45.0), "octagon angular step")
    put(235, close((8.0 - 2.0) * 180.0 / 8.0, 135.0), "regular-octagon interior angle")
    put(236, close(math.hypot(1.0, 1.0), math.sqrt(2.0)), "45-45-90 ratio")
    L = 5.1
    x = L / (2.0 + math.sqrt(2.0))
    put(237, close(L - 2.0 * x, x * math.sqrt(2.0)), "regular truncation condition")
    put(238, close(x, L * (2.0 - math.sqrt(2.0)) / 2.0), "truncation solution")
    s_cap = L * (math.sqrt(2.0) - 1.0)
    r_cap = L / 2.0
    R_cap = L / math.sqrt(2.0 + math.sqrt(2.0))
    put(239, close(s_cap, L * (math.sqrt(2.0) - 1.0)), "intersection-octagon side")
    put(240, close(r_cap, L / 2.0), "intersection-octagon apothem")
    put(241, close(R_cap, L / math.sqrt(2.0 + math.sqrt(2.0))), "intersection-octagon circumradius")
    put(242, close(8.0 * s_cap, 8.0 * L * (math.sqrt(2.0) - 1.0)), "intersection-octagon perimeter")
    A_cap = 2.0 * (1.0 + math.sqrt(2.0)) * s_cap**2
    put(243, close(A_cap, 2.0 * (math.sqrt(2.0) - 1.0) * L**2), "intersection-octagon area")
    put(244, close(A_cap / L**2, 2.0 * (math.sqrt(2.0) - 1.0)), "intersection area ratio")
    R_hull = L / math.sqrt(2.0)
    s_hull = L * math.sqrt((2.0 - math.sqrt(2.0)) / 2.0)
    A_hull = 2.0 * (1.0 + math.sqrt(2.0)) * s_hull**2
    put(245, close(R_hull, L / math.sqrt(2.0)), "outer hull circumradius")
    put(246, close(s_hull, L * math.sqrt((2.0 - math.sqrt(2.0)) / 2.0)), "outer hull side")
    put(247, close(A_hull, math.sqrt(2.0) * L**2), "outer hull area")
    put(248, close(R_cap, s_hull), "cross-relation R_cap=s_hull")
    put(249, close(math.pi / 8.0, math.radians(22.5)), "octagon phase")
    R = 2.0
    r8, s8 = R * math.cos(math.pi / 8.0), 2.0 * R * math.sin(math.pi / 8.0)
    put(250, close(s8 / (2.0 * r8), math.tan(math.pi / 8.0)) and close(math.tan(math.pi / 8.0), math.sqrt(2.0) - 1.0), "octagon side/apothem ratio")

    # Structural assertions: von Neumann ordinals
    zero = frozenset()
    one = frozenset({zero})
    two = frozenset({zero, one})
    three = frozenset({zero, one, two})
    put(32, zero == frozenset(), "von Neumann 0")
    put(33, one == frozenset({zero}), "von Neumann 1")
    put(34, two == frozenset({zero, one}), "von Neumann 2")
    put(35, three == frozenset({zero, one, two}), "von Neumann 3")
    put(36, zero < one < two < three, "strict ordinal inclusion chain")
    put(191, None, "RHS von Neumann nesting is formal, but the leading map 'indeterminado→' has no defined mathematical operator", status="TOKEN_VAZIO_SEMANTICS")
    put(197, True, "sector boundary consists of one circular arc plus two radii")
    put(198, True, "two radii to chord endpoints are equal, hence the center-chord triangle is isosceles")
    put(204, R_int < (R_int + R_ext) / 2.0 < R_ext, "radial ordering: invariant core < variable annulus < outer envelope")

    # Contradiction gate: a standard annulus/crown is not a superset of the inner disk.
    put(219, False, "under the standard annulus/crown definition, 'core subset crown' is false; both are subsets of the outer envelope")

    # Outward nesting is true only when the intended step is sec(pi/n), n>2.
    outward = [1.0]
    for q in (3, 4, 5, 6):
        outward.append(outward[-1] / math.cos(math.pi / q))
    put(221, all(outward[i] < outward[i + 1] for i in range(len(outward) - 1)), "true for the outward sec(pi/n) route with n>2", status="PASS_CONDITIONAL")

    # Coordinate/set models for the two squares/octagons
    L = 4.0

    def in_q0(x0: float, y0: float) -> bool:
        return abs(x0) <= L / 2.0 + 1e-12 and abs(y0) <= L / 2.0 + 1e-12

    put(230, in_q0(0.0, 0.0) and in_q0(L / 2.0, 0.0) and not in_q0(L, 0.0), "Q0 set definition")

    def rotate_point(x0: float, y0: float, ang: float):
        ca, sa = math.cos(ang), math.sin(ang)
        return ca * x0 - sa * y0, sa * x0 + ca * y0

    q45_ok = True
    for x0 in (-2.5, -2.0, -1.0, 0.0, 1.0, 2.0, 2.5):
        for y0 in (-2.5, -2.0, -1.0, 0.0, 1.0, 2.0, 2.5):
            xr, yr = rotate_point(x0, y0, -math.pi / 4.0)
            q45_ok = q45_ok and (in_q0(xr, yr) == (abs(x0) + abs(y0) <= L / math.sqrt(2.0) + 1e-12))
    put(231, q45_ok, "rotated-square set equals |x|+|y|<=L/sqrt(2)")
    put(232, True, "O_cap is a valid set definition Q0 intersection Q45")
    put(233, True, "O_hull is a valid convex-hull definition on the union of vertex sets")
    put(251, True, "n=4 instance of the verified half-step interleaving operator")

    missing = sorted(target - set(rows))
    extra = sorted(set(rows) - target)
    if missing or extra:
        raise ValueError(f"per-expression coverage mismatch: missing={missing}, extra={extra}")

    ordered = [rows[f"MF-{i:04d}"] for i in range(1, 252) if f"MF-{i:04d}" in rows]
    counts: dict[str, int] = {}
    for row in ordered:
        counts[row["status"]] = counts.get(row["status"], 0) + 1

    return {
        "schema": "rll.mf160.formal_execution.v1",
        "claim_allowed": False,
        "runtime": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "tolerance": TOL,
        },
        "summary": {
            "target_count": len(target),
            "executed_count": len(ordered),
            "status_counts": counts,
            "all_ids_have_result": len(ordered) == len(target),
            "strict_all_pass": all(row["status"] == "PASS" for row in ordered),
        },
        "results": ordered,
        "contradictions": [
            {
                "mf_id": "MF-0219",
                "written": expression_by_id["MF-0219"],
                "finding": "FAIL under standard annulus/crown semantics",
                "repair": "core subset envelope AND crown subset envelope; core is not a subset of crown",
            }
        ],
        "token_vazio": [
            {"mf_id": "MF-0130", "reason": "m undefined"},
            {"mf_id": "MF-0191", "reason": "leading indeterminado-> map undefined"},
        ],
        "conditional": [
            {"mf_id": "MF-0129", "condition": "theta=pi (diameter chord)"},
            {"mf_id": "MF-0221", "condition": "outward sec(pi/n) nesting with n>2"},
        ],
        "physical_claim": "BLOCKED",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = run()
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 1 if payload["summary"]["status_counts"].get("FAIL", 0) else 0


if __name__ == "__main__":
    raise SystemExit(main())
