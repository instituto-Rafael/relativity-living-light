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


def test_unified_shape_complex_keeps_maps_and_nonidentities_typed():
    from rx.toroidal_geodesic_stability import unified_shape_complex_contract
    c = unified_shape_complex_contract()
    assert c["state"] == "FORMAL_TYPED_COMPLEX"
    assert ["QxI", "C", "extrusion"] in c["relations"]
    assert ["Q", "T2", "opposite_edge_identification"] in c["relations"]
    assert "sphere != torus" in c["nonidentities"]


def test_equal_spheres_overlap_is_not_mislabeled_as_rigid_passage():
    from rx.toroidal_geodesic_stability import sphere_through_equal_sphere_gate
    out = sphere_through_equal_sphere_gate(1.0, 1.0)
    assert out["mathematical_interpenetration"] is True
    assert out["volume_relation"] == "equal_spheres_overlap"
    assert out["rigid_material_passage"].startswith("TOKEN_VAZIO")


def test_equal_sphere_requires_aperture_radius_at_least_its_radius():
    from rx.toroidal_geodesic_stability import equal_sphere_aperture_gate
    assert equal_sphere_aperture_gate(1.0, 1.0)["passes_without_deformation"] is True
    assert equal_sphere_aperture_gate(1.0, 0.999)["passes_without_deformation"] is False


def test_cut_fold_has_four_intrinsic_equilateral_triangles():
    from rx.toroidal_geodesic_stability import triangular_torus_cut_fold
    out = triangular_torus_cut_fold(side=2.0, twist_angle=math.radians(25.0))
    assert out["four_equilateral_intrinsic"] is True
    assert len(out["triangles"]) == 4
    assert out["intrinsic_max_deviation"] < 1e-12
    # A non-zero 3D twist is not silently claimed to preserve the xy projection.
    assert out["four_equilateral_in_xy_projection"] is False


def test_flat_bowtie_projection_recovers_four_equilateral_triangles():
    from rx.toroidal_geodesic_stability import triangular_torus_cut_fold
    out = triangular_torus_cut_fold(side=1.0, twist_angle=0.0)
    assert out["four_equilateral_intrinsic"] is True
    assert out["four_equilateral_in_xy_projection"] is True
    assert out["projected_max_deviation"] < 1e-12


def test_equal_tube_scale_sphere_passage_has_exact_R_ge_2r_gate():
    from rx.toroidal_geodesic_stability import sphere_through_torus_hole_gate
    tangent = sphere_through_torus_hole_gate(2.0, 1.0, 1.0)
    assert tangent["same_tube_scale"] is True
    assert tangent["passes_axially_without_deformation"] is True
    assert tangent["state"] == "PASS_TANGENT_LIMIT"
    assert abs(tangent["clearance"]) < 1e-12

    open_gate = sphere_through_torus_hole_gate(2.5, 1.0, 1.0)
    assert open_gate["state"] == "PASS_WITH_CLEARANCE"
    assert math.isclose(open_gate["clearance"], 0.5, abs_tol=1e-12)

    blocked = sphere_through_torus_hole_gate(1.9, 1.0, 1.0)
    assert blocked["passes_axially_without_deformation"] is False
    assert blocked["state"] == "BLOCKED_INTERSECTION"


def test_axis_flow_clearance_is_minimal_at_torus_midplane():
    from rx.toroidal_geodesic_stability import torus_axis_flow_clearance
    c0 = torus_axis_flow_clearance(0.0, 2.5, 1.0, 1.0)
    c1 = torus_axis_flow_clearance(1.0, 2.5, 1.0, 1.0)
    cm1 = torus_axis_flow_clearance(-1.0, 2.5, 1.0, 1.0)
    assert c1 > c0
    assert cm1 > c0
    assert math.isclose(c1, cm1, abs_tol=1e-12)


def test_full_shape_relation_state_keeps_torus_and_sphere_distinct():
    from rx.toroidal_geodesic_stability import shape_relation_state, torus_point
    p = torus_point(0.2, 0.4, 2.0, 1.0)
    out = shape_relation_state(p, 2.0, 1.0)
    assert out["torus_surface_residual"] < 1e-12
    assert out["objects"] == ["I","S1","Q","Delta_plus","Delta_minus","T2","S2","C","B"]
    assert out["claim_allowed"] is False


def test_144_to_42_projection_conserves_all_source_states():
    from rx.toroidal_geodesic_stability import stability_concentration_144_to_42
    out = stability_concentration_144_to_42(2.0, 1.0)
    assert out["source_state_count"] == 144
    assert out["target_vertex_count"] == 42
    assert out["assigned_state_count"] == 144
    assert out["stable_state_count"] + out["unstable_state_count"] == 144
    assert 1 <= out["active_vertex_count"] <= 42
    assert sum(row["total"] for row in out["bins"]) == 144
    assert out["claim_allowed"] is False


def test_144_to_42_stability_is_source_preserving_not_vertex_recomputed():
    from rx.toroidal_geodesic_stability import stability_concentration_144_to_42
    out = stability_concentration_144_to_42(2.0, 1.0)
    for row in out["bins"]:
        assert row["stable"] + row["unstable"] == row["total"]
        if row["total"]:
            assert 0.0 <= row["stable_fraction"] <= 1.0


def test_exact_ratio_regimes_include_canonical_q2_as_seven_eighths_stable():
    from rx.toroidal_geodesic_stability import (
        canonical_ratio_stability_regimes,
        expected_canonical_stability_counts,
    )
    regimes = canonical_ratio_stability_regimes()
    assert math.isclose(regimes["critical_c_radius_u0"], 0.25, abs_tol=1e-15)
    assert math.isclose(
        regimes["critical_c_radius_u30"], math.sqrt(3.0) / 4.0, abs_tol=1e-15
    )
    out = expected_canonical_stability_counts(2.0, 1.0)
    assert out["unstable"] == 18
    assert out["stable"] == 126
    assert math.isclose(out["stable_fraction"], 7.0 / 8.0, abs_tol=1e-15)


def test_ratio_regimes_change_only_at_derived_geometry_thresholds():
    from rx.toroidal_geodesic_stability import expected_canonical_stability_counts
    assert expected_canonical_stability_counts(1.1, 1.0)["unstable"] == 6
    assert expected_canonical_stability_counts(1.2, 1.0)["unstable"] == 18
    assert expected_canonical_stability_counts(4.0, 1.0)["unstable"] == 24
    assert expected_canonical_stability_counts(12.0, 1.0)["unstable"] == 36


def test_q2_instability_support_is_five_positions_and_not_torus_throat():
    from rx.toroidal_geodesic_stability import instability_geometry_report
    out = instability_geometry_report(2.0, 1.0)
    assert out["count_parity"] is True
    assert out["observed_counts"]["unstable"] == 18
    assert out["observed_counts"]["stable"] == 126
    assert out["unique_unstable_position_count"] == 5
    assert out["outer_side_unstable_count"] == 18
    assert out["inner_throat_unstable_count"] == 0
    assert out["geometric_findings"]["coincides_with_torus_throat"] is False
    assert out["geometric_findings"]["coincides_with_meridian_30_tangency"] is False
    assert out["geometric_findings"]["centered_on_outer_radial_median"] is True


def test_each_q2_branch_has_exactly_three_cyclic_unstable_steps():
    from rx.toroidal_geodesic_stability import instability_geometry_report
    out = instability_geometry_report(2.0, 1.0)
    expected = {
        0: [0, 1, 23],
        1: [0, 1, 23],
        2: [7, 8, 9],
        3: [7, 8, 9],
        4: [15, 16, 17],
        5: [15, 16, 17],
    }
    for row in out["branch_unstable_arcs"]:
        assert sorted(row["unstable_n"]) == expected[row["branch"]]
        assert row["count"] == 3


def test_q2_unstable_support_is_rectangular_pyramid_not_square_pyramid():
    from rx.toroidal_geodesic_stability import instability_geometry_report
    out = instability_geometry_report(2.0, 1.0)
    shape = out["five_point_support_shape"]
    assert shape["classification"] == "right_rectangular_pyramid_support"
    assert shape["square_base"] is False
    assert shape["square_condition_compatible_with_ring_torus"] is False
    assert shape["base_side_y"] > shape["base_side_z"]


def test_mixed_icosphere_vertices_are_projection_aliases_not_source_identity():
    from rx.toroidal_geodesic_stability import instability_geometry_report
    out = instability_geometry_report(2.0, 1.0)
    mixed = {row["vertex"]: row for row in out["mixed_projection_vertices"]}
    assert set(mixed) == {23, 30, 32, 40, 41}
    for row in mixed.values():
        assert row["projection_alias"] is True
        assert row["stable"] > 0
        assert row["unstable"] > 0
