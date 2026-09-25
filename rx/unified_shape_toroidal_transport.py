"""Unified shape family + toroidal transport + 144->42 concentration.

This module extends the geometry-first RLL route with the pre-existing unified
shape family:
triangle, square, circle, cube, sphere, tetrahedron, square pyramid,
bipyramid and torus.

The objects share a common *radial envelope* when requested; they are not
silently declared identical in metric, area, volume or topology.

A same-size object may be transported through the same coordinate/field
region as another object in this mathematical model. That does not imply that
two impenetrable rigid solids can pass through one another without collision.
"""

from __future__ import annotations

import math
from collections import defaultdict

from rx.toroidal_geodesic_stability import (
    DU,
    DV,
    SIN30,
    TAU,
    icosphere_f2,
    six_toroidal_branches,
)


def _norm3(p):
    return math.sqrt(sum(float(x) * float(x) for x in p))


def _normalize3(p, radius):
    n = _norm3(p)
    if n == 0.0:
        raise ValueError("cannot normalize zero vector")
    s = float(radius) / n
    return tuple(float(x) * s for x in p)


def _dist3(a, b):
    return math.sqrt(sum((float(x)-float(y))**2 for x, y in zip(a,b)))


def _circumradius(points):
    if not points:
        raise ValueError("points required")
    return max(_norm3(p) for p in points)


def common_envelope_shape_family(radius=1.0, torus_minor_fraction=1.0/3.0):
    """Return canonical representatives sharing one radial envelope S.

    All finite vertex clouds have circumradius S.
    The circle and sphere have radius S.
    The ring torus uses R+r=S.
    """
    S = float(radius)
    if S <= 0.0:
        raise ValueError("radius must be positive")
    frac = float(torus_minor_fraction)
    if not (0.0 < frac < 0.5):
        raise ValueError("torus_minor_fraction must be in (0, 0.5)")

    triangle = [
        (S*math.cos(math.pi/2 + k*TAU/3), S*math.sin(math.pi/2 + k*TAU/3), 0.0)
        for k in range(3)
    ]
    square = [
        (S*math.cos(math.pi/4 + k*math.pi/2), S*math.sin(math.pi/4 + k*math.pi/2), 0.0)
        for k in range(4)
    ]
    circle = [
        (S*math.cos(k*TAU/24), S*math.sin(k*TAU/24), 0.0)
        for k in range(24)
    ]

    cube_raw = [
        (sx,sy,sz)
        for sx in (-1.0,1.0)
        for sy in (-1.0,1.0)
        for sz in (-1.0,1.0)
    ]
    cube = [_normalize3(p,S) for p in cube_raw]

    tetra_raw = [
        (1.0,1.0,1.0),
        (1.0,-1.0,-1.0),
        (-1.0,1.0,-1.0),
        (-1.0,-1.0,1.0),
    ]
    tetrahedron = [_normalize3(p,S) for p in tetra_raw]

    # Regular square pyramid with equal base and lateral edge lengths.
    # Initial coordinates use base side 2 and height sqrt(2), then the
    # complete object is recentered on its circumsphere and normalized.
    h = math.sqrt(2.0)
    raw_pyr = [
        (-1.0,-1.0,0.0),(1.0,-1.0,0.0),(1.0,1.0,0.0),(-1.0,1.0,0.0),
        (0.0,0.0,h),
    ]
    # Circumcenter lies on z axis. Solve equal distance from apex and base.
    zc = 0.0
    # 2 + zc^2 = (h-zc)^2 -> zc=(h^2-2)/(2h)=0 here.
    square_pyramid = [_normalize3(p,S) for p in raw_pyr]

    # Triangular bipyramid from an equilateral equatorial triangle and poles.
    bipyramid = [
        (S*math.cos(k*TAU/3), S*math.sin(k*TAU/3), 0.0)
        for k in range(3)
    ] + [(0.0,0.0,S),(0.0,0.0,-S)]

    sphere_axes = [
        (S,0.0,0.0),(-S,0.0,0.0),(0.0,S,0.0),(0.0,-S,0.0),(0.0,0.0,S),(0.0,0.0,-S)
    ]

    torus_r = S*frac
    torus_R = S-torus_r

    return {
        "radius": S,
        "triangle": triangle,
        "square": square,
        "circle": circle,
        "cube": cube,
        "tetrahedron": tetrahedron,
        "square_pyramid": square_pyramid,
        "bipyramid": bipyramid,
        "sphere_axes": sphere_axes,
        "torus": {"R": torus_R, "r": torus_r, "outer_radius": S},
        "relations": {
            "triangle_to_tetrahedron": "3D lift / simplicial family",
            "square_to_cube": "Q x I extrusion family",
            "circle_to_torus": "S1 x S1 periodic product / embedding",
            "cube_or_bipyramid_to_sphere": "radial projection",
            "all": "same relational matrix, distinct geometric objects",
        },
    }


def common_envelope_residuals(family):
    """Measure whether every declared representative respects the same envelope."""
    S = float(family["radius"])
    rows = {}
    for name in ("triangle","square","circle","cube","tetrahedron","square_pyramid","bipyramid","sphere_axes"):
        points = family[name]
        radii = [_norm3(p) for p in points]
        rows[name] = {
            "min_radius": min(radii),
            "max_radius": max(radii),
            "max_abs_residual": max(abs(x-S) for x in radii),
        }
    torus = family["torus"]
    rows["torus"] = {
        "outer_radius": torus["R"]+torus["r"],
        "max_abs_residual": abs((torus["R"]+torus["r"])-S),
    }
    return rows


def four_equilateral_cross_fold(radius=1.0, phase=0.0):
    """Explicit fold candidate: square-axis cross x +/-30-degree pulse.

    Four axis directions are separated by 90 degrees. Around each axis,
    two circle points are selected at +/-30 degrees. Together with the
    common center, each pair is tested as a triangle.

    This proves four equilateral wedges for this operator. It does NOT by
    itself prove that a physical torus twists into a figure-eight.
    """
    S=float(radius)
    if S<=0.0:
        raise ValueError("radius must be positive")
    center=(0.0,0.0)
    triangles=[]
    for j in range(4):
        axis=float(phase)+j*math.pi/2.0
        a=axis-math.pi/6.0
        b=axis+math.pi/6.0
        p=(S*math.cos(a),S*math.sin(a))
        q=(S*math.cos(b),S*math.sin(b))
        sides=(
            math.hypot(p[0],p[1]),
            math.hypot(q[0],q[1]),
            math.hypot(p[0]-q[0],p[1]-q[1]),
        )
        residual=max(abs(x-S) for x in sides)
        triangles.append({
            "axis": axis%TAU,
            "minus30": p,
            "plus30": q,
            "sides": sides,
            "equilateral_residual": residual,
            "equilateral": residual < 1e-12,
        })
    return {
        "operator": "square_axis_cross_x_plusminus30_pulse",
        "radius": S,
        "triangles": triangles,
        "all_four_equilateral": all(t["equilateral"] for t in triangles),
        "figure8_topology_claim": False,
    }


def translate_cloud(points, center):
    """Rigid translation. Pairwise distances and size are preserved."""
    c=tuple(float(x) for x in center)
    return [tuple(float(p[i])+c[i] for i in range(3)) for p in points]


def pairwise_distance_signature(points):
    sig=[]
    for i in range(len(points)):
        for j in range(i+1,len(points)):
            sig.append(_dist3(points[i],points[j]))
    return tuple(sorted(sig))


def rigid_transport_invariant(points, center_a, center_b):
    """Transport one shape between two centers and verify no rescaling."""
    a=translate_cloud(points,center_a)
    b=translate_cloud(points,center_b)
    sa=pairwise_distance_signature(a)
    sb=pairwise_distance_signature(b)
    max_res=max((abs(x-y) for x,y in zip(sa,sb)), default=0.0)
    return {
        "size_preserved": max_res < 1e-12,
        "max_pairwise_residual": max_res,
        "from_center": tuple(center_a),
        "to_center": tuple(center_b),
    }


def equal_sphere_overlap(center_a, center_b, radius):
    """Classify two equal-radius spheres.

    For geometric shells/fields, overlap is an allowed relation.
    For impenetrable rigid solids, center distance < 2r is a collision.
    """
    r=float(radius)
    if r<=0.0:
        raise ValueError("radius must be positive")
    d=_dist3(center_a,center_b)
    eps=1e-12
    if d < eps:
        relation="coincident"
    elif d < 2.0*r-eps:
        relation="intersecting"
    elif abs(d-2.0*r)<=eps:
        relation="externally_tangent"
    else:
        relation="disjoint"
    return {
        "center_distance": d,
        "radius": r,
        "relation": relation,
        "shell_or_field_overlay_allowed": True,
        "impenetrable_rigid_pass_without_collision": d >= 2.0*r-eps,
    }


def nearest_icosphere_vertex(point, vertices, sphere_radius):
    """Deterministic nearest-vertex assignment with a geometric tie tolerance.

    Symmetric source points can be equidistant from two mesh vertices.  Raw
    libm acos rounding may differ by a few ulps across runners, so exact float
    tuple ordering can split one canonical bin into two.  Distances within a
    scale-aware tolerance are treated as the same geometric tie and the lower
    vertex index wins deterministically.
    """
    S=float(sphere_radius)
    tol=max(1.0,abs(S))*1.0e-12
    best_distance=None
    best_index=None
    for i,q in enumerate(vertices):
        cosang=sum(float(a)*float(b) for a,b in zip(point,q))/(S*S)
        cosang=max(-1.0,min(1.0,cosang))
        distance=S*math.acos(cosang)
        if (
            best_distance is None
            or distance < best_distance - tol
            or (abs(distance-best_distance) <= tol and i < best_index)
        ):
            best_distance=distance
            best_index=i
    return {"index":best_index,"geodesic_distance":best_distance}


def aggregate_144_to_42(major_radius=2.0, minor_radius=1.0):
    """Project the six-branch 24-step matrix onto the 42 f=2 sphere vertices."""
    matrix=six_toroidal_branches(major_radius,minor_radius)
    S=matrix["sphere_radius"]
    mesh=icosphere_f2(S)
    vertices=mesh["vertices"]

    agg=defaultdict(lambda:{
        "visits":0,
        "stable":0,
        "margin_sum":0.0,
        "min_multiplier_sum":0.0,
        "distance_sum":0.0,
    })

    for branch in matrix["branches"]:
        for cell in branch["cells"]:
            hit=nearest_icosphere_vertex(cell["sphere_point"],vertices,S)
            a=agg[hit["index"]]
            a["visits"]+=1
            a["stable"]+=1 if cell["stable_any"] else 0
            a["margin_sum"]+=float(cell["stability_margin"])
            a["min_multiplier_sum"]+=float(cell["min_multiplier"])
            a["distance_sum"]+=float(hit["geodesic_distance"])

    rows=[]
    for idx in range(42):
        a=agg[idx]
        n=a["visits"]
        rows.append({
            "vertex":idx,
            "visits":n,
            "stable":a["stable"],
            "stable_fraction":(a["stable"]/n if n else None),
            "mean_margin":(a["margin_sum"]/n if n else None),
            "mean_min_multiplier":(a["min_multiplier_sum"]/n if n else None),
            "mean_geodesic_distance":(a["distance_sum"]/n if n else None),
        })

    occupied=[r for r in rows if r["visits"]]
    top_visits=sorted(occupied,key=lambda x:(-x["visits"],x["vertex"]))
    top_stable=sorted(occupied,key=lambda x:(-x["stable"],-x["visits"],x["vertex"]))
    total_visits=sum(r["visits"] for r in rows)
    total_stable=sum(r["stable"] for r in rows)

    return {
        "schema":"rll.144_to_42_stability_concentration.v1",
        "input_shape":[6,24],
        "input_cells":total_visits,
        "sphere_vertices":42,
        "occupied_vertices":len(occupied),
        "stable_cells":total_stable,
        "stable_fraction":total_stable/total_visits,
        "top_by_visits":top_visits[:8],
        "top_by_stable":top_stable[:8],
        "vertices":rows,
        "claim_allowed":False,
    }


def figure8_torus_immersion(u, v, major_radius, loop_radius):
    """Continuous figure-eight torus *immersion* F:T2->R3.

    Meridian curve is a translated Gerono lemniscate:
        rho(v) = R + a cos(v)
        z(v)   = (a/2) sin(2v)

    Sweeping it by azimuth u gives a continuous periodic map from T2 into R3.
    It is intentionally an immersion with self-intersection; it is not an
    embedding and does not model material interpenetration.
    """
    R=float(major_radius)
    a=float(loop_radius)
    if not (R>a>0.0):
        raise ValueError("require major_radius > loop_radius > 0")
    uu=float(u)
    vv=float(v)
    rho=R+a*math.cos(vv)
    z=0.5*a*math.sin(2.0*vv)
    return (rho*math.cos(uu),rho*math.sin(uu),z)


def figure8_double_point(major_radius, loop_radius, u=0.0):
    """Return the two parameter values that map to the same crossing point."""
    p1=figure8_torus_immersion(u,math.pi/2.0,major_radius,loop_radius)
    p2=figure8_torus_immersion(u,3.0*math.pi/2.0,major_radius,loop_radius)
    return {
        "v1":math.pi/2.0,
        "v2":3.0*math.pi/2.0,
        "p1":p1,
        "p2":p2,
        "coincident_residual":_dist3(p1,p2),
    }


def figure8_sheet_tangent_cross(major_radius, loop_radius, u=0.0):
    """Exact local crossing geometry at the self-intersection circle.

    At v=pi/2 and 3pi/2 the two meridian-sheet tangent vectors are
      t1=(-a cos u,-a sin u,-a)
      t2=(+a cos u,+a sin u,-a)
    and t1.t2=0, so the two sheets cross orthogonally.
    """
    R=float(major_radius)
    a=float(loop_radius)
    if not (R>a>0.0):
        raise ValueError("require major_radius > loop_radius > 0")
    uu=float(u)
    t1=(-a*math.cos(uu),-a*math.sin(uu),-a)
    t2=(+a*math.cos(uu),+a*math.sin(uu),-a)
    dot=sum(x*y for x,y in zip(t1,t2))
    n1=_norm3(t1)
    n2=_norm3(t2)
    cosang=dot/(n1*n2)
    cosang=max(-1.0,min(1.0,cosang))
    angle=math.acos(cosang)
    return {
        "t1":t1,
        "t2":t2,
        "dot":dot,
        "angle":angle,
        "angle_deg":math.degrees(angle),
        "orthogonal":abs(dot)<1e-12,
        "crossing_circle_radius":R,
        "state":"PASS_FORMAL_IMMERSED_GEOMETRY",
        "physical_interpenetration_claim":False,
    }


def figure8_cross_equilateral_bridge(major_radius, loop_radius, pulse_radius=1.0, u=0.0):
    """Bridge the figure-eight crossing to the four-equilateral cross-fold.

    The two sheet tangent *lines* at the figure-eight double point are
    orthogonal, hence they produce four oriented rays separated by 90 degrees.
    Those four rays become the axes of four_equilateral_cross_fold, which then
    applies the already declared +/-30-degree pulse.

    This proves:
      figure8 local sheet crossing -> 90-degree cross -> 4 equilateral wedges.
    It does not prove a physical torus must adopt this immersed state.
    """
    cross=figure8_sheet_tangent_cross(major_radius,loop_radius,u=u)
    t1=cross["t1"]
    # Use the meridian radial-z plane orientation of the first tangent.
    # In that local 2D plane its angle is sufficient; all four axes are
    # generated by 90-degree increments.
    phase=math.atan2(t1[2], math.hypot(t1[0],t1[1]))
    fold=four_equilateral_cross_fold(radius=pulse_radius,phase=phase)
    return {
        "figure8_cross":cross,
        "cross_fold":fold,
        "all_four_equilateral":fold["all_four_equilateral"],
        "bridge_state":"PASS_FORMAL_LOCAL_GEOMETRY",
        "global_embedding_claim":False,
    }
