import math

from rx.toroidal_geodesic_stability import (
    COS30,
    DU,
    DV,
    PERIOD_STEPS,
    RETURN_STEPS,
    SIN30,
    central_triangle_components,
    complementary_angle_routes,
    derived_quadratic_mouths_30,
    equilateral_gate_30,
    geometric_c,
    icosphere_f2,
    line_sphere_bhaskara,
    meridian_line_bhaskara,
    poincare_return,
    quadratic_fixed_point_stability,
    quadratic_mouth_rho,
    radial_projection_to_sphere,
    six_toroidal_branches,
    specular_reflection,
    tangent_family_30,
    torus_point,
)


def test_30_degree_gate_is_exact_equilateral_geometry():
    gate = equilateral_gate_30(2.0, 1.0)
    for side in gate["side_lengths"]:
        assert math.isclose(side, 1.0, rel_tol=0.0, abs_tol=1e-12)
    assert math.isclose(gate["height"], math.sqrt(3.0) / 2.0, abs_tol=1e-15)
    assert math.isclose(gate["half_base"], 0.5, abs_tol=1e-15)
    assert math.isclose(SIN30, 0.5, abs_tol=1e-15)
    assert math.isclose(COS30, math.sqrt(3.0) / 2.0, abs_tol=1e-15)


def test_parallel_tangent_gap_is_torus_tube_diameter():
    family = tangent_family_30(3.0, 0.7, slope_sign=1)
    assert math.isclose(family["perpendicular_gap"], 1.4, abs_tol=1e-12)

    for b in family["intercepts"]:
        cut = meridian_line_bhaskara(3.0, 0.7, family["slope"], b)
        assert abs(cut["discriminant"]) < 1e-10
        assert cut["classification"] == "tangent"


def test_quadratic_mouth_coefficients_are_derived_from_torus_gate():
    R, r = 2.0, 1.0
    mouths = derived_quadratic_mouths_30(R, r)
    z = mouths["mouth_z"]

    outer = quadratic_mouth_rho(mouths["outer"], z)
    inner = quadratic_mouth_rho(mouths["inner"], z)

    assert math.isclose(outer, mouths["outer_boundary_rho"], abs_tol=1e-12)
    assert math.isclose(inner, mouths["inner_boundary_rho"], abs_tol=1e-12)

    # Mirrored vertices around rho=R.
    c_out = mouths["outer"]["c"]
    c_in = mouths["inner"]["c"]
    assert math.isclose((c_out + c_in) / 2.0, R, abs_tol=1e-12)

    # Local line angle convention dz/drho = tan(30 deg) at z=+r/2.
    drho_dz = 2.0 * mouths["outer"]["a"] * z
    assert math.isclose(1.0 / drho_dz, math.tan(math.pi / 6.0), abs_tol=1e-12)


def test_f2_icosphere_has_42_120_80_combinatorics():
    mesh = icosphere_f2(5.0)
    assert mesh["counts"] == {"V": 42, "E": 120, "F": 80}
    assert len(mesh["vertices"]) == 42
    assert mesh["vertex_labels"].count("base_vertex") == 12
    assert mesh["vertex_labels"].count("edge_midpoint_vertex") == 30
    for p in mesh["vertices"]:
        assert math.isclose(math.sqrt(sum(x * x for x in p)), 5.0, abs_tol=1e-12)


def test_line_sphere_bhaskara_and_reflection_preserve_norm():
    hit = line_sphere_bhaskara((0.0, 0.0, 0.0), (1.0, 1.0, 0.0), 2.0)
    assert hit["classification"] == "two_impacts"
    assert len(hit["points"]) == 2
    positive = max(hit["points"], key=lambda p: p[0])
    assert math.isclose(math.sqrt(sum(x * x for x in positive)), 2.0, abs_tol=1e-12)

    direction = (1.0, 1.0, 0.0)
    reflected = specular_reflection(direction, positive, 2.0)
    n0 = math.sqrt(sum(x * x for x in direction))
    n1 = math.sqrt(sum(x * x for x in reflected))
    assert math.isclose(n0, n1, abs_tol=1e-12)


def test_hete_fixed_point_stability_is_computed_from_geometry():
    c = geometric_c(0.9, 0.4, 2.0, 1.0)
    out = quadratic_fixed_point_stability(c)
    for z in out["roots"]:
        residual = z * z - z + c
        assert abs(residual) < 1e-12
    expected = min(abs(2.0 * z) for z in out["roots"]) < 1.0
    assert out["stable_any"] is expected


def test_six_branches_form_6x24_spatial_matrix_and_mirror_stability():
    matrix = six_toroidal_branches(2.0, 1.0)
    assert matrix["shape"] == [6, PERIOD_STEPS]
    assert matrix["derived_cell_count"] == 144
    assert math.isclose(matrix["du"], DU, abs_tol=1e-15)
    assert math.isclose(matrix["dv_abs"], DV, abs_tol=1e-15)

    by_phase = {}
    for branch in matrix["branches"]:
        by_phase.setdefault(branch["phase_index"], {})[branch["chirality"]] = branch

    for phase, pair in by_phase.items():
        up = pair[1]["cells"]
        down = pair[-1]["cells"]
        assert [c["stable_any"] for c in up] == [c["stable_any"] for c in down]
        # Spatial mirror: x,y equal, z changes sign.
        for a, b in zip(up, down):
            assert math.isclose(a["point"][0], b["point"][0], abs_tol=1e-12)
            assert math.isclose(a["point"][1], b["point"][1], abs_tol=1e-12)
            assert math.isclose(a["point"][2], -b["point"][2], abs_tol=1e-12)


def test_poincare_half_turn_and_full_period():
    assert RETURN_STEPS == 12
    assert PERIOD_STEPS == 24

    v0 = 0.37
    returned = (v0 + RETURN_STEPS * DV) % (2.0 * math.pi)
    assert math.isclose(returned, poincare_return(v0), abs_tol=1e-12)
    returned_down = (v0 - RETURN_STEPS * DV) % (2.0 * math.pi)
    assert math.isclose(returned_down, poincare_return(v0), abs_tol=1e-12)

    u0 = 0.71
    assert math.isclose((u0 + PERIOD_STEPS * DU) % (2.0 * math.pi), u0, abs_tol=1e-12)
    assert math.isclose((v0 + PERIOD_STEPS * DV) % (2.0 * math.pi), v0, abs_tol=1e-12)


def test_torus_points_project_to_minimal_enclosing_sphere():
    R, r = 2.0, 1.0
    S = R + r
    for n in range(24):
        p = torus_point(n * DU, n * DV, R, r)
        q = radial_projection_to_sphere(p, S)
        assert math.isclose(math.sqrt(sum(x * x for x in q)), S, abs_tol=1e-12)


def test_pythagorean_cathetus_difference_and_complements():
    tri = central_triangle_components(2.0, math.pi / 3.0)
    assert math.isclose(tri["q"], 1.0, abs_tol=1e-12)
    assert math.isclose(tri["d"], math.sqrt(3.0), abs_tol=1e-12)
    assert tri["pythagoras_residual"] < 1e-12

    theta = math.radians(1.0 / 3600.0)
    routes = complementary_angle_routes(theta)
    assert math.isclose(routes["theta"] + routes["to_60"], math.pi / 3.0, abs_tol=1e-15)
    assert math.isclose(routes["theta"] + routes["to_90"], math.pi / 2.0, abs_tol=1e-15)
