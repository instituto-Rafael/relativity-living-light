"""Geometric stability engine for the RLL torus/sphere/Poincare route.

The primary state is geometry. No cosmological parameter is fitted here.

Authority chain:
- Pitagoras/Bhaskara/isosceles/Poincare crosswalk
- 15/30/45 crown and geodesic reflection crosswalk
- torus Poincare return-map paper
- HETE fixed-point stability rule |2z| < 1

The module keeps three objects distinct:
1. torus surface / geodesic sphere geometry;
2. Poincare return map on the torus flow;
3. quadratic fixed-point stability in the complex c-plane.

A 7D Poincare-ball lift is not inferred here because the repository's 7D paper
requires an explicit channel map before a new input can be lifted.
"""
from __future__ import annotations

import cmath
import math


TAU = 2.0 * math.pi
SIN30 = 0.5
COS30 = math.sqrt(3.0) / 2.0
TAN30 = 1.0 / math.sqrt(3.0)
SPIRAL_Q = COS30
DU = math.pi / 6.0       # 30 degrees
DV = math.pi / 4.0       # 45 degrees
RETURN_STEPS = 12
PERIOD_STEPS = 24
STABILITY_EPS = 1.0e-12
COS45 = math.sqrt(2.0) / 2.0


def _check_torus(major_radius, minor_radius):
    R = float(major_radius)
    r = float(minor_radius)
    if not (R > r > 0.0):
        raise ValueError("require major_radius > minor_radius > 0")
    return R, r


def _norm3(p):
    return math.sqrt(sum(float(x) * float(x) for x in p))


def _normalize3(p, radius=1.0):
    n = _norm3(p)
    if n == 0.0:
        raise ValueError("cannot normalize zero vector")
    s = float(radius) / n
    return tuple(float(x) * s for x in p)


def _dot3(a, b):
    return sum(float(x) * float(y) for x, y in zip(a, b))


def torus_point(u, v, major_radius, minor_radius):
    """Standard T^2 embedding in R^3."""
    R, r = _check_torus(major_radius, minor_radius)
    ring = R + r * math.cos(float(v))
    return (
        ring * math.cos(float(u)),
        ring * math.sin(float(u)),
        r * math.sin(float(v)),
    )


def meridian_point(angle, major_radius, minor_radius, side="outer"):
    """Point on the torus meridian circle in (rho,z) coordinates."""
    R, r = _check_torus(major_radius, minor_radius)
    sign = 1.0 if side == "outer" else -1.0
    if side not in {"outer", "inner"}:
        raise ValueError("side must be outer or inner")
    a = float(angle)
    return (R + sign * r * math.cos(a), r * math.sin(a))


def equilateral_gate_30(major_radius, minor_radius, side="outer"):
    """The +/-30 degree radial pair closes an exact equilateral triangle.

    The apex is the meridian-circle center C=(R,0).  The two boundary points
    are at +/-30 degrees from the chosen radial median.
    """
    R, r = _check_torus(major_radius, minor_radius)
    center = (R, 0.0)
    p_plus = meridian_point(math.pi / 6.0, R, r, side=side)
    p_minus = meridian_point(-math.pi / 6.0, R, r, side=side)

    def d2(a, b):
        return math.hypot(a[0] - b[0], a[1] - b[1])

    return {
        "center": center,
        "plus30": p_plus,
        "minus30": p_minus,
        "side_lengths": (
            d2(center, p_plus),
            d2(center, p_minus),
            d2(p_plus, p_minus),
        ),
        "height": COS30 * r,
        "half_base": SIN30 * r,
        "state": "MATH_FORMAL",
    }


def tangent_family_30(major_radius, minor_radius, slope_sign=1):
    """Two parallel tangents to the meridian circle at +/-30-degree slope family.

    The line convention is z = m*rho + b with m = +/-tan(30 deg).
    Their perpendicular separation is exactly 2r.
    """
    R, r = _check_torus(major_radius, minor_radius)
    if slope_sign not in (-1, 1):
        raise ValueError("slope_sign must be -1 or 1")
    m = float(slope_sign) * TAN30
    root = math.sqrt(1.0 + m * m)
    b_plus = -m * R + r * root
    b_minus = -m * R - r * root
    gap = abs(b_plus - b_minus) / root
    return {
        "slope": m,
        "intercepts": (b_minus, b_plus),
        "midline_intercept": -m * R,
        "perpendicular_gap": gap,
        "expected_gap": 2.0 * r,
        "state": "MATH_FORMAL",
    }


def meridian_line_bhaskara(major_radius, minor_radius, slope, intercept):
    """Bhaskara discriminant for z=m*rho+b against torus meridian circle."""
    R, r = _check_torus(major_radius, minor_radius)
    m = float(slope)
    b = float(intercept)
    A = 1.0 + m * m
    B = 2.0 * (m * b - R)
    C = R * R + b * b - r * r
    delta = B * B - 4.0 * A * C
    roots = []
    if delta >= 0.0:
        sq = math.sqrt(max(delta, 0.0))
        roots = [(-B - sq) / (2.0 * A), (-B + sq) / (2.0 * A)]
    return {
        "A": A,
        "B": B,
        "C": C,
        "discriminant": delta,
        "rho_roots": roots,
        "classification": (
            "two_intersections" if delta > 1.0e-12
            else "tangent" if abs(delta) <= 1.0e-12
            else "no_real_intersection"
        ),
    }


def derived_quadratic_mouths_30(major_radius, minor_radius):
    """Symmetric quadratic mouths derived from the +/-30 meridian gate.

    We use rho(z)=a*z^2+c and require:
      - symmetry around z=0;
      - passage through the torus boundary at z=+/-r/2;
      - local line angle dz/drho = +/-tan(30 deg) at those points.

    This fixes the coefficients; they are not fitted.
    """
    R, r = _check_torus(major_radius, minor_radius)
    a = math.sqrt(3.0) / r
    c_outer = R + math.sqrt(3.0) * r / 4.0
    c_inner = R - math.sqrt(3.0) * r / 4.0
    return {
        "outer": {"a": a, "b": 0.0, "c": c_outer},
        "inner": {"a": -a, "b": 0.0, "c": c_inner},
        "mouth_z": r / 2.0,
        "outer_boundary_rho": R + COS30 * r,
        "inner_boundary_rho": R - COS30 * r,
        "state": "DERIVED_GEOMETRIC_MODEL",
        "physical_vortex_claim": False,
    }


def quadratic_mouth_rho(coeffs, z):
    return (
        float(coeffs["a"]) * float(z) * float(z)
        + float(coeffs["b"]) * float(z)
        + float(coeffs["c"])
    )


def line_sphere_bhaskara(origin, direction, sphere_radius):
    """Exact line/sphere intersection using a quadratic discriminant."""
    S = float(sphere_radius)
    if S <= 0.0:
        raise ValueError("sphere_radius must be positive")
    x0 = tuple(float(x) for x in origin)
    d = tuple(float(x) for x in direction)
    A = _dot3(d, d)
    if A == 0.0:
        raise ValueError("direction must be nonzero")
    B = 2.0 * _dot3(x0, d)
    C = _dot3(x0, x0) - S * S
    delta = B * B - 4.0 * A * C
    roots = []
    points = []
    if delta >= 0.0:
        sq = math.sqrt(max(delta, 0.0))
        roots = [(-B - sq) / (2.0 * A), (-B + sq) / (2.0 * A)]
        points = [
            tuple(x0[i] + t * d[i] for i in range(3))
            for t in roots
        ]
    return {
        "discriminant": delta,
        "roots": roots,
        "points": points,
        "classification": (
            "two_impacts" if delta > 1.0e-12
            else "tangent" if abs(delta) <= 1.0e-12
            else "no_real_impact"
        ),
    }


def specular_reflection(direction, impact_point, sphere_radius):
    """Reflect direction in the tangent plane of the sphere."""
    S = float(sphere_radius)
    d = tuple(float(x) for x in direction)
    n = tuple(float(x) / S for x in impact_point)
    scale = 2.0 * _dot3(d, n)
    return tuple(d[i] - scale * n[i] for i in range(3))


def radial_projection_to_sphere(point, sphere_radius):
    return _normalize3(point, radius=float(sphere_radius))


def geodesic_distance_sphere(a, b, sphere_radius):
    S = float(sphere_radius)
    cosang = _dot3(a, b) / (S * S)
    cosang = max(-1.0, min(1.0, cosang))
    return S * math.acos(cosang)


def _icosahedron():
    phi = (1.0 + math.sqrt(5.0)) / 2.0
    raw = [
        (-1, phi, 0), (1, phi, 0), (-1, -phi, 0), (1, -phi, 0),
        (0, -1, phi), (0, 1, phi), (0, -1, -phi), (0, 1, -phi),
        (phi, 0, -1), (phi, 0, 1), (-phi, 0, -1), (-phi, 0, 1),
    ]
    vertices = [_normalize3(v) for v in raw]
    faces = [
        (0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11),
        (1, 5, 9), (5, 11, 4), (11, 10, 2), (10, 7, 6), (7, 1, 8),
        (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9),
        (4, 9, 5), (2, 4, 11), (6, 2, 10), (8, 6, 7), (9, 8, 1),
    ]
    return vertices, faces


def icosphere_f2(sphere_radius=1.0):
    """Frequency-2 icosphere vertex set: 12 originals + 30 edge midpoints = 42."""
    S = float(sphere_radius)
    base, faces = _icosahedron()
    vertices = [tuple(S * x for x in v) for v in base]
    labels = ["base_vertex"] * len(vertices)
    edge_index = {}

    for face in faces:
        for i, j in ((face[0], face[1]), (face[1], face[2]), (face[2], face[0])):
            edge = tuple(sorted((i, j)))
            if edge in edge_index:
                continue
            midpoint = tuple((base[i][k] + base[j][k]) / 2.0 for k in range(3))
            edge_index[edge] = len(vertices)
            vertices.append(_normalize3(midpoint, radius=S))
            labels.append("edge_midpoint_vertex")

    face_centroids = []
    for face in faces:
        c = tuple(sum(base[i][k] for i in face) / 3.0 for k in range(3))
        face_centroids.append(_normalize3(c, radius=S))

    axes = [
        (S, 0.0, 0.0), (-S, 0.0, 0.0),
        (0.0, S, 0.0), (0.0, -S, 0.0),
        (0.0, 0.0, S), (0.0, 0.0, -S),
    ]
    return {
        "vertices": vertices,
        "vertex_labels": labels,
        "faces": faces,
        "face_centroids": face_centroids,
        "axes_90": axes,
        "counts": {"V": len(vertices), "E": 30 * 4, "F": 20 * 4},
    }


def nearest_geodesic_landmark(point, sphere_radius):
    """Classify a sphere point against f=2 vertices, face-centres and cardinal axes."""
    mesh = icosphere_f2(sphere_radius)
    candidates = []
    for i, p in enumerate(mesh["vertices"]):
        candidates.append(("icosphere_f2_" + mesh["vertex_labels"][i], i, p))
    for i, p in enumerate(mesh["face_centroids"]):
        candidates.append(("face_median_intersection", i, p))
    for i, p in enumerate(mesh["axes_90"]):
        candidates.append(("axis_90", i, p))

    best = None
    for kind, idx, p in candidates:
        d = geodesic_distance_sphere(point, p, sphere_radius)
        row = (d, kind, idx, p)
        if best is None or row[0] < best[0]:
            best = row
    return {
        "distance": best[0],
        "kind": best[1],
        "index": best[2],
        "point": best[3],
    }


def geometric_c(point_u, point_v, major_radius, minor_radius):
    """Map one torus point to the HETE quadratic c-plane without a fitted kappa.

    The current session declares sin(30 deg) as the toroidal pulse entry.
    We therefore bind kappa geometrically as sin30/(R+r), so:
        c = sin30 * ((R+r cos v)/(R+r)) * exp(i u)
    This is a versioned model choice, not a universal physical constant.
    """
    R, r = _check_torus(major_radius, minor_radius)
    u = float(point_u)
    v = float(point_v)
    s = R + r * math.cos(v)
    amplitude = SIN30 * s / (R + r)
    return amplitude * complex(math.cos(u), math.sin(u))


def quadratic_fixed_point_stability(c):
    """HETE stability: z=z^2+c; a fixed point is attractive iff |2z|<1."""
    c = complex(c)
    D = 1.0 - 4.0 * c
    rootD = cmath.sqrt(D)
    z_plus = (1.0 + rootD) / 2.0
    z_minus = (1.0 - rootD) / 2.0
    multipliers = (abs(2.0 * z_plus), abs(2.0 * z_minus))
    minimum = min(multipliers)
    return {
        "c": c,
        "D": D,
        "roots": (z_plus, z_minus),
        "multipliers": multipliers,
        "min_multiplier": minimum,
        "stable_any": minimum < 1.0 - STABILITY_EPS,
        "on_stability_boundary": abs(minimum - 1.0) <= STABILITY_EPS,
        "stability_margin": 1.0 - minimum,
    }


def poincare_return(v):
    """Return map for DU=30 deg, |DV|=45 deg after 12 DU steps."""
    return (float(v) + math.pi) % TAU


def six_toroidal_branches(major_radius, minor_radius, steps=PERIOD_STEPS):
    """3 phase families x 2 chiralities = 6 torus-surface branches.

    u advances by 30 deg and v by +/-45 deg.  The three phase copies are
    separated by 120 deg.  This produces a 6x24 geometry matrix at one exact
    period, i.e. 144 spatial cells.  144 is a derived cell count only.
    """
    R, r = _check_torus(major_radius, minor_radius)
    if int(steps) <= 0:
        raise ValueError("steps must be positive")
    S = R + r
    branches = []
    for phase_index in range(3):
        phase = phase_index * TAU / 3.0
        for chirality in (1, -1):
            cells = []
            for n in range(int(steps)):
                u = phase + n * DU
                v = chirality * n * DV
                point = torus_point(u, v, R, r)
                c = geometric_c(u, v, R, r)
                stability = quadratic_fixed_point_stability(c)
                sphere_point = radial_projection_to_sphere(point, S)
                landmark = nearest_geodesic_landmark(sphere_point, S)
                cells.append({
                    "n": n,
                    "u": u % TAU,
                    "v": v % TAU,
                    "point": point,
                    "spiral_weight": SPIRAL_Q ** n,
                    "c": (c.real, c.imag),
                    "stable_any": stability["stable_any"],
                    "min_multiplier": stability["min_multiplier"],
                    "stability_margin": stability["stability_margin"],
                    "sphere_point": sphere_point,
                    "nearest_landmark": {
                        "kind": landmark["kind"],
                        "index": landmark["index"],
                        "geodesic_distance": landmark["distance"],
                    },
                })
            branches.append({
                "phase_index": phase_index,
                "chirality": chirality,
                "cells": cells,
            })
    return {
        "schema": "rll.toroidal_geodesic_stability_matrix.v1",
        "shape": [6, int(steps)],
        "derived_cell_count": 6 * int(steps),
        "torus": {"R": R, "r": r},
        "sphere_radius": S,
        "du": DU,
        "dv_abs": DV,
        "return_steps": RETURN_STEPS,
        "period_steps": PERIOD_STEPS,
        "branches": branches,
        "claim_allowed": False,
    }


def central_triangle_components(radius, central_angle):
    """Half-chord q and perpendicular d for an isosceles central triangle."""
    R = float(radius)
    theta = float(central_angle)
    q = R * math.sin(theta / 2.0)
    d = R * math.cos(theta / 2.0)
    return {
        "q": q,
        "d": d,
        "cathetus_difference": abs(d - q),
        "pythagoras_residual": abs(q * q + d * d - R * R),
    }


def complementary_angle_routes(theta):
    """Complement one angular seed toward right or equilateral closure."""
    value = float(theta)
    return {
        "theta": value,
        "to_60": math.pi / 3.0 - value,
        "to_90": math.pi / 2.0 - value,
    }


def unified_shape_complex_contract():
    """Typed PG-Omega7 family: maps relate shapes without declaring them identical."""
    return {
        "objects": ["I","S1","Q","Delta_plus","Delta_minus","T2","S2","C","B"],
        "relations": [
            ["I","S1","boundary_quotient"],
            ["S1xS1","T2","product"],
            ["Q","T2","opposite_edge_identification"],
            ["QxI","C","extrusion"],
            ["Delta_plus_union_Delta_minus","T2","triangular_lattice_quotient"],
            ["C","S2","radial_projection"],
            ["B","S2","radial_projection"],
        ],
        "nonidentities": [
            "sphere != torus",
            "projection != equivalence",
            "square != two_equilateral_triangles_in_euclidean_metric",
        ],
        "state": "FORMAL_TYPED_COMPLEX",
    }


def sphere_through_equal_sphere_gate(center_distance, radius):
    """Separate equal-sphere overlap from passage through a physical aperture."""
    d = float(center_distance)
    r = float(radius)
    if r <= 0.0 or d < 0.0:
        raise ValueError("require radius > 0 and center_distance >= 0")
    if d == 0.0:
        relation = "coincident_equal_spheres"
    elif d < 2.0 * r:
        relation = "equal_spheres_overlap"
    elif math.isclose(d, 2.0 * r, rel_tol=0.0, abs_tol=1e-12):
        relation = "externally_tangent"
    else:
        relation = "disjoint"
    return {
        "center_distance": d,
        "radius": r,
        "volume_relation": relation,
        "mathematical_interpenetration": d < 2.0 * r,
        "rigid_material_passage": "TOKEN_VAZIO_APERTURE_RADIUS_AND_DEFORMATION_MODEL",
    }


def equal_sphere_aperture_gate(sphere_radius, aperture_radius):
    """Rigid-size gate for a sphere crossing a planar circular aperture."""
    r = float(sphere_radius)
    a = float(aperture_radius)
    if r <= 0.0 or a < 0.0:
        raise ValueError("require sphere_radius > 0 and aperture_radius >= 0")
    return {
        "sphere_radius": r,
        "aperture_radius": a,
        "passes_without_deformation": a >= r,
        "clearance": a - r,
    }


def _rotate_x(point, angle):
    x, y, z = (float(v) for v in point)
    c = math.cos(float(angle))
    s = math.sin(float(angle))
    return (x, y * c - z * s, y * s + z * c)


def _triangle_side_lengths3(vertices, tri):
    a, b, c = (vertices[i] for i in tri)
    def dist(p, q):
        return math.sqrt(sum((p[k] - q[k]) ** 2 for k in range(3)))
    return (dist(a, b), dist(b, c), dist(c, a))


def triangular_torus_cut_fold(side=1.0, twist_angle=0.0):
    """Explicit cut/fold candidate from two 60-degree rhombi.

    Each rhombus is a fundamental domain for a triangular-lattice torus before
    opposite-edge identification. Cutting each rhombus along its short diagonal
    gives two exact equilateral triangles. Two congruent copies meet at one
    vertex to form a bow-tie/figure-eight cell complex (four triangles total).

    The +/- copies may then be twisted rigidly by +/-twist_angle about the x
    axis. Rigid 3D folding preserves triangle side lengths. The 2D orthogonal
    projection need not preserve equilateral shape for nonzero twist.

    This is a cellular cut/fold model, not a claim that the smooth embedded
    torus is homeomorphic to a figure eight.
    """
    s = float(side)
    phi = float(twist_angle)
    if s <= 0.0:
        raise ValueError("side must be positive")

    h = COS30 * s
    O = (0.0, 0.0, 0.0)

    # Right 60-degree rhombus: O-A-C-B, cut by A-B.
    A = (s, 0.0, 0.0)
    B = (0.5 * s, h, 0.0)
    C = (1.5 * s, h, 0.0)
    right0 = [O, A, B, C]
    right = [_rotate_x(p, +phi) for p in right0]

    # Left congruent rhombus, reflected through O, twisted oppositely.
    D = (-s, 0.0, 0.0)
    E = (-0.5 * s, -h, 0.0)
    F = (-1.5 * s, -h, 0.0)
    left0 = [O, D, E, F]
    left = [_rotate_x(p, -phi) for p in left0]

    vertices = right + left
    # right: (O,A,B) and (A,C,B); left: (O,D,E) and (D,F,E)
    triangles = [(0, 1, 2), (1, 3, 2), (4, 5, 6), (5, 7, 6)]
    lengths = [_triangle_side_lengths3(vertices, tri) for tri in triangles]
    deviations = [max(ls) - min(ls) for ls in lengths]

    projected = [(p[0], p[1], 0.0) for p in vertices]
    projected_lengths = [_triangle_side_lengths3(projected, tri) for tri in triangles]
    projected_deviations = [max(ls) - min(ls) for ls in projected_lengths]

    return {
        "schema": "rll.triangular_torus_cut_fold.v1",
        "side": s,
        "twist_angle": phi,
        "vertices": vertices,
        "triangles": triangles,
        "intrinsic_side_lengths": lengths,
        "intrinsic_max_deviation": max(deviations),
        "four_equilateral_intrinsic": max(deviations) <= 1.0e-12,
        "projected_side_lengths": projected_lengths,
        "projected_max_deviation": max(projected_deviations),
        "four_equilateral_in_xy_projection": max(projected_deviations) <= 1.0e-12,
        "topology_boundary": (
            "cut/fold cell complex; not a homeomorphism T2 -> figure-eight"
        ),
        "claim_allowed": False,
    }


def sphere_through_torus_hole_gate(major_radius, minor_radius, sphere_radius):
    """Exact axial rigid-sphere passage gate through the hole of a solid torus.

    The torus tube is the set of points within minor_radius r of the centre
    circle of radius R. A sphere of radius s whose centre moves on the torus
    symmetry axis has minimum separation from that centre circle at z=0.

    Nonintersection for the whole axial passage is therefore:
        R >= r + s.
    In particular, for a sphere with s=r ("same size" as the torus tube),
        R >= 2r.
    """
    R, r = _check_torus(major_radius, minor_radius)
    s = float(sphere_radius)
    if s <= 0.0:
        raise ValueError("sphere_radius must be positive")
    clearance = R - (r + s)
    if clearance > 1.0e-12:
        state = "PASS_WITH_CLEARANCE"
    elif abs(clearance) <= 1.0e-12:
        state = "PASS_TANGENT_LIMIT"
    else:
        state = "BLOCKED_INTERSECTION"
    return {
        "major_radius": R,
        "minor_radius": r,
        "sphere_radius": s,
        "inner_hole_radius": R - r,
        "clearance": clearance,
        "passes_axially_without_deformation": clearance >= -1.0e-12,
        "state": state,
        "same_tube_scale": math.isclose(s, r, rel_tol=0.0, abs_tol=1e-12),
        "same_tube_scale_condition": "R >= 2r",
        "physical_boundary": (
            "rigid Euclidean geometry only; no matter interpenetration, wormhole, "
            "or physical spacetime mechanism is inferred"
        ),
    }


def torus_axis_flow_clearance(z, major_radius, minor_radius, sphere_radius):
    """Clearance along the exact axial passage path at coordinate z."""
    R, r = _check_torus(major_radius, minor_radius)
    s = float(sphere_radius)
    zz = float(z)
    if s <= 0.0:
        raise ValueError("sphere_radius must be positive")
    centreline_distance = math.sqrt(R * R + zz * zz)
    return centreline_distance - (r + s)


def shape_relation_state(point, major_radius, minor_radius, sphere_radius=None):
    """Attach the full PG-Omega7 typed geometry context to one torus state."""
    R, r = _check_torus(major_radius, minor_radius)
    p = tuple(float(x) for x in point)
    S = float(sphere_radius) if sphere_radius is not None else R + r
    rho_xy = math.hypot(p[0], p[1])
    torus_meridian_residual = abs((rho_xy - R) ** 2 + p[2] ** 2 - r * r)
    sphere_radial_residual = abs(_dot3(p, p) - S * S)
    return {
        "point": p,
        "objects": unified_shape_complex_contract()["objects"],
        "relations": unified_shape_complex_contract()["relations"],
        "torus_surface_residual": torus_meridian_residual,
        "sphere_surface_residual_before_projection": sphere_radial_residual,
        "sphere_projection": radial_projection_to_sphere(p, S),
        "claim_allowed": False,
    }


def nearest_icosphere_vertex(point, sphere_radius, mesh=None):
    """Nearest f=2 vertex with deterministic tie-breaking for symmetric points."""
    S = float(sphere_radius)
    mesh = mesh or icosphere_f2(S)
    tol = max(1.0, abs(S)) * 1.0e-12
    best = None
    for idx, p in enumerate(mesh["vertices"]):
        d = geodesic_distance_sphere(point, p, S)
        row = (d, idx, p, mesh["vertex_labels"][idx])
        if (
            best is None
            or d < best[0] - tol
            or (abs(d - best[0]) <= tol and idx < best[1])
        ):
            best = row
    return {
        "distance": best[0],
        "index": best[1],
        "point": best[2],
        "label": best[3],
    }


def stability_concentration_144_to_42(major_radius=2.0, minor_radius=1.0):
    """Project the exact 6x24 torus matrix onto 42 geodesic vertices.

    The assignment is nearest-neighbour on S^2 using geodesic distance.
    Stability is not recomputed from the vertex; it remains the HETE value
    generated by the original torus cell. This preserves SOURCE -> PROJECTION
    -> AGGREGATE rather than replacing source geometry by the mesh.
    """
    R, r = _check_torus(major_radius, minor_radius)
    S = R + r
    matrix = six_toroidal_branches(R, r, steps=PERIOD_STEPS)
    mesh = icosphere_f2(S)
    bins = [
        {
            "vertex": i,
            "label": mesh["vertex_labels"][i],
            "total": 0,
            "stable": 0,
            "unstable": 0,
            "margin_sum": 0.0,
            "geodesic_distance_sum": 0.0,
            "source_cells": [],
        }
        for i in range(42)
    ]

    stable_total = 0
    for branch_idx, branch in enumerate(matrix["branches"]):
        for cell in branch["cells"]:
            hit = nearest_icosphere_vertex(cell["sphere_point"], S, mesh=mesh)
            row = bins[hit["index"]]
            row["total"] += 1
            is_stable = bool(cell["stable_any"])
            row["stable"] += int(is_stable)
            row["unstable"] += int(not is_stable)
            row["margin_sum"] += float(cell["stability_margin"])
            row["geodesic_distance_sum"] += float(hit["distance"])
            row["source_cells"].append({
                "branch": branch_idx,
                "phase_index": branch["phase_index"],
                "chirality": branch["chirality"],
                "n": cell["n"],
            })
            stable_total += int(is_stable)

    active = []
    for row in bins:
        if row["total"]:
            row["stable_fraction"] = row["stable"] / row["total"]
            row["mean_margin"] = row["margin_sum"] / row["total"]
            row["mean_assignment_distance"] = row["geodesic_distance_sum"] / row["total"]
            active.append(row)
        else:
            row["stable_fraction"] = None
            row["mean_margin"] = None
            row["mean_assignment_distance"] = None

    ranked = sorted(
        active,
        key=lambda row: (
            row["stable_fraction"],
            row["stable"],
            -row["mean_assignment_distance"],
        ),
        reverse=True,
    )

    return {
        "schema": "rll.torus144_to_icosphere42_stability.v1",
        "torus": {"R": R, "r": r},
        "sphere_radius": S,
        "source_state_count": 144,
        "target_vertex_count": 42,
        "assigned_state_count": sum(row["total"] for row in bins),
        "stable_state_count": stable_total,
        "unstable_state_count": 144 - stable_total,
        "active_vertex_count": len(active),
        "bins": bins,
        "ranking": [
            {
                "vertex": row["vertex"],
                "total": row["total"],
                "stable": row["stable"],
                "stable_fraction": row["stable_fraction"],
                "mean_margin": row["mean_margin"],
                "mean_assignment_distance": row["mean_assignment_distance"],
            }
            for row in ranked
        ],
        "shape_complex": unified_shape_complex_contract(),
        "projection_boundary": (
            "nearest-vertex projection does not identify torus and sphere; "
            "HETE stability remains sourced from the torus cell"
        ),
        "claim_allowed": False,
    }


def canonical_ratio_stability_regimes():
    """Exact ratio thresholds for the canonical 30/45 discrete HETE lattice.

    Let q=R/r>1.  Because the pulse amplitude is at most 1/2 and the azimuth
    grid is in 30-degree steps, only u=0 and u=+/-30 can ever leave the
    attracting-fixed-point cardioid.

    Along u=0 the cardioid radial boundary is 1/4.
    Along u=+/-30 it is sqrt(3)/4.

    Combining these exact c-plane boundaries with v in 45-degree steps gives
    three q thresholds. Boundary points are classified non-stable because
    HETE requires the strict inequality |2z|<1.
    """
    q_outer_30 = (COS30 - COS45) / (1.0 - COS30)
    q_inner_equator = 3.0
    q_inner_30 = (COS30 + COS45) / (1.0 - COS30)
    return {
        "q_outer_30": q_outer_30,
        "q_inner_equator": q_inner_equator,
        "q_inner_30": q_inner_30,
        "critical_c_radius_u0": 0.25,
        "critical_c_radius_u30": math.sqrt(3.0) / 4.0,
        "regimes": [
            {
                "q_min": 1.0,
                "q_min_open": True,
                "q_max": q_outer_30,
                "q_max_open": True,
                "unstable": 6,
                "stable": 138,
                "stable_fraction": 23.0 / 24.0,
            },
            {
                "q_min": q_outer_30,
                "q_min_open": False,
                "q_max": q_inner_equator,
                "q_max_open": True,
                "unstable": 18,
                "stable": 126,
                "stable_fraction": 7.0 / 8.0,
            },
            {
                "q_min": q_inner_equator,
                "q_min_open": False,
                "q_max": q_inner_30,
                "q_max_open": True,
                "unstable": 24,
                "stable": 120,
                "stable_fraction": 5.0 / 6.0,
            },
            {
                "q_min": q_inner_30,
                "q_min_open": False,
                "q_max": None,
                "q_max_open": None,
                "unstable": 36,
                "stable": 108,
                "stable_fraction": 3.0 / 4.0,
            },
        ],
        "claim_allowed": False,
    }


def expected_canonical_stability_counts(major_radius, minor_radius):
    R, r = _check_torus(major_radius, minor_radius)
    q = R / r
    regimes = canonical_ratio_stability_regimes()
    for row in regimes["regimes"]:
        lo_ok = q > row["q_min"] if row["q_min_open"] else q >= row["q_min"]
        if row["q_max"] is None:
            hi_ok = True
        else:
            hi_ok = q < row["q_max"] if row["q_max_open"] else q <= row["q_max"]
        if lo_ok and hi_ok:
            return {
                "q": q,
                "unstable": row["unstable"],
                "stable": row["stable"],
                "stable_fraction": row["stable_fraction"],
                "regime": row,
            }
    raise AssertionError("ring-torus ratio was not classified")


def _canonical_angle_deg(angle):
    value = (math.degrees(float(angle)) % 360.0 + 360.0) % 360.0
    if abs(value - 360.0) <= 1.0e-9 or abs(value) <= 1.0e-9:
        return 0.0
    return round(value, 9)


def _torus_meridian_class(v):
    cv = math.cos(float(v))
    if abs(cv - 1.0) <= 1.0e-9:
        return "outer_equator"
    if abs(cv + 1.0) <= 1.0e-9:
        return "inner_equator"
    if cv > 1.0e-9:
        return "outer_half"
    if cv < -1.0e-9:
        return "inner_half"
    return "top_bottom"


def instability_geometry_report(major_radius=2.0, minor_radius=1.0):
    """Locate HETE instability and separate source geometry from projection aliasing."""
    R, r = _check_torus(major_radius, minor_radius)
    matrix = six_toroidal_branches(R, r, steps=PERIOD_STEPS)
    expected = expected_canonical_stability_counts(R, r)
    S = R + r
    mesh = icosphere_f2(S)

    unstable = []
    all_assignments = []
    for branch_idx, branch in enumerate(matrix["branches"]):
        for cell in branch["cells"]:
            hit = nearest_icosphere_vertex(cell["sphere_point"], S, mesh=mesh)
            row = {
                "branch": branch_idx,
                "phase_index": branch["phase_index"],
                "chirality": branch["chirality"],
                "n": cell["n"],
                "u_deg": _canonical_angle_deg(cell["u"]),
                "v_deg": _canonical_angle_deg(cell["v"]),
                "point": cell["point"],
                "c": cell["c"],
                "min_multiplier": cell["min_multiplier"],
                "stability_margin": cell["stability_margin"],
                "stable_any": cell["stable_any"],
                "meridian_class": _torus_meridian_class(cell["v"]),
                "nearest_vertex": hit["index"],
                "assignment_distance": hit["distance"],
            }
            all_assignments.append(row)
            if not cell["stable_any"]:
                unstable.append(row)

    # Canonicalize geometrically repeated source positions.
    support = {}
    for row in unstable:
        key = (
            row["u_deg"],
            row["v_deg"],
        )
        support.setdefault(key, {
            "u_deg": row["u_deg"],
            "v_deg": row["v_deg"],
            "point": row["point"],
            "nearest_vertex": row["nearest_vertex"],
            "multiplicity": 0,
            "meridian_class": row["meridian_class"],
            "min_multiplier": row["min_multiplier"],
        })
        support[key]["multiplicity"] += 1

    # A mixed sphere vertex can result from projection aliasing of different
    # torus source classes. Record those classes explicitly.
    by_vertex = {}
    for row in all_assignments:
        slot = by_vertex.setdefault(row["nearest_vertex"], {
            "vertex": row["nearest_vertex"],
            "stable": 0,
            "unstable": 0,
            "source_classes": set(),
            "source_uv": set(),
        })
        slot["stable"] += int(row["stable_any"])
        slot["unstable"] += int(not row["stable_any"])
        slot["source_classes"].add(row["meridian_class"])
        slot["source_uv"].add((row["u_deg"], row["v_deg"]))

    mixed_vertices = []
    for slot in by_vertex.values():
        if slot["stable"] and slot["unstable"]:
            mixed_vertices.append({
                "vertex": slot["vertex"],
                "stable": slot["stable"],
                "unstable": slot["unstable"],
                "source_classes": sorted(slot["source_classes"]),
                "source_uv": sorted(slot["source_uv"]),
                "projection_alias": len(slot["source_uv"]) > 1,
            })
    mixed_vertices.sort(key=lambda row: row["vertex"])

    # The five unique unstable positions form one axial apex plus four
    # sign-symmetric corners. Measure their actual embedded base.
    apex = (R + r, 0.0, 0.0)
    corner_ring = R + r * COS45
    corner_x = corner_ring * COS30
    corner_y = corner_ring * SIN30
    corner_z = r * COS45
    base_y = 2.0 * corner_y
    base_z = 2.0 * corner_z
    apex_edge = math.sqrt(
        (R + r - corner_x) ** 2 + corner_y ** 2 + corner_z ** 2
    )
    square_residual = abs(base_y - base_z)

    branch_arcs = []
    for branch_idx, branch in enumerate(matrix["branches"]):
        bad = [cell["n"] for cell in branch["cells"] if not cell["stable_any"]]
        branch_arcs.append({
            "branch": branch_idx,
            "phase_index": branch["phase_index"],
            "chirality": branch["chirality"],
            "unstable_n": bad,
            "count": len(bad),
        })

    outer_unstable = sum(
        row["meridian_class"] in {"outer_equator", "outer_half"}
        for row in unstable
    )
    throat_unstable = sum(row["meridian_class"] == "inner_equator" for row in unstable)

    return {
        "schema": "rll.instability_geometry_report.v1",
        "torus": {"R": R, "r": r, "q": R / r},
        "expected_counts": expected,
        "observed_counts": {
            "unstable": len(unstable),
            "stable": 144 - len(unstable),
            "stable_fraction": (144 - len(unstable)) / 144.0,
        },
        "count_parity": len(unstable) == expected["unstable"],
        "unique_unstable_position_count": len(support),
        "unique_unstable_positions": sorted(
            support.values(), key=lambda row: (row["u_deg"], row["v_deg"])
        ),
        "support_signature": (
            "{(0,0)} union {(+-30,+-45)} for q=2 canonical geometry"
            if math.isclose(R / r, 2.0, rel_tol=0.0, abs_tol=1.0e-12)
            else "ratio-dependent; inspect unique_unstable_positions"
        ),
        "branch_unstable_arcs": branch_arcs,
        "outer_side_unstable_count": outer_unstable,
        "inner_throat_unstable_count": throat_unstable,
        "meridian_30_mouth_coincidence_count": sum(
            min(abs(row["v_deg"] - 30.0), abs(row["v_deg"] - 330.0)) <= 1.0e-9
            for row in unstable
        ),
        "five_point_support_shape": {
            "apex": apex,
            "corner_plane_x": corner_x,
            "base_side_y": base_y,
            "base_side_z": base_z,
            "base_aspect_y_over_z": base_y / base_z,
            "apex_to_corner_edge": apex_edge,
            "square_residual": square_residual,
            "square_base": square_residual <= 1.0e-12,
            "square_condition_q": 1.0 / math.sqrt(2.0),
            "square_condition_compatible_with_ring_torus": False,
            "classification": "right_rectangular_pyramid_support",
        },
        "mixed_projection_vertices": mixed_vertices,
        "projection_alias_boundary": (
            "mixed 42-vertex bins do not imply mixed stability at one torus point; "
            "radial projection and nearest-vertex quantization can merge distinct "
            "inner/outer torus source states"
        ),
        "geometric_findings": {
            "coincides_with_torus_throat": throat_unstable > 0,
            "coincides_with_meridian_30_tangency": False,
            "centered_on_outer_radial_median": any(
                row["u_deg"] == 0.0 and row["v_deg"] == 0.0 for row in unstable
            ),
            "flow_boundary": (
                "for q=2 each branch has a 3-step cyclic unstable arc centered "
                "on the outer-equator crossing; the next +/- step is stable"
            ),
        },
        "claim_allowed": False,
    }
