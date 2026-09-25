import math

from rx.unified_shape_toroidal_transport import (
    aggregate_144_to_42,
    common_envelope_residuals,
    common_envelope_shape_family,
    equal_sphere_overlap,
    four_equilateral_cross_fold,
    rigid_transport_invariant,
)


def test_full_shape_family_shares_one_radial_envelope_without_object_identity():
    family = common_envelope_shape_family(3.0)
    residuals = common_envelope_residuals(family)

    for name, row in residuals.items():
        assert row["max_abs_residual"] < 1e-12, name

    assert set(
        [
            "triangle",
            "square",
            "circle",
            "cube",
            "tetrahedron",
            "square_pyramid",
            "bipyramid",
            "sphere_axes",
            "torus",
        ]
    ).issubset(family.keys())
    assert family["relations"]["all"] == "same relational matrix, distinct geometric objects"


def test_square_cross_times_plusminus30_produces_four_equilateral_triangles():
    fold = four_equilateral_cross_fold(2.5)
    assert fold["all_four_equilateral"] is True
    assert fold["figure8_topology_claim"] is False
    assert len(fold["triangles"]) == 4

    for tri in fold["triangles"]:
        for side in tri["sides"]:
            assert math.isclose(side, 2.5, abs_tol=1e-12)
        assert tri["equilateral_residual"] < 1e-12


def test_rigid_transport_preserves_shape_scale():
    family = common_envelope_shape_family(1.0)
    for name in ("triangle", "square", "cube", "tetrahedron", "square_pyramid", "bipyramid"):
        out = rigid_transport_invariant(
            family[name],
            center_a=(0.0, 0.0, 0.0),
            center_b=(1.25, -0.75, 2.0),
        )
        assert out["size_preserved"] is True
        assert out["max_pairwise_residual"] < 1e-12


def test_equal_sphere_transport_separates_geometric_overlay_from_rigid_collision():
    S = 3.0

    # Two equal spheres centered on orthogonal points of a carrier sphere.
    overlap = equal_sphere_overlap((S, 0.0, 0.0), (0.0, S, 0.0), S)
    assert overlap["relation"] == "intersecting"
    assert overlap["shell_or_field_overlay_allowed"] is True
    assert overlap["impenetrable_rigid_pass_without_collision"] is False

    # Antipodal centers are exactly externally tangent for equal radius S.
    tangent = equal_sphere_overlap((S, 0.0, 0.0), (-S, 0.0, 0.0), S)
    assert tangent["relation"] == "externally_tangent"
    assert tangent["impenetrable_rigid_pass_without_collision"] is True


def test_144_cells_project_to_42_vertex_lattice_and_measure_stability_concentration():
    out = aggregate_144_to_42(2.0, 1.0)

    assert out["input_shape"] == [6, 24]
    assert out["input_cells"] == 144
    assert out["sphere_vertices"] == 42
    assert out["occupied_vertices"] == 21
    assert out["stable_cells"] == 126
    assert math.isclose(out["stable_fraction"], 0.875, abs_tol=1e-15)

    # Highest occupancy is a three-way tie: 12 visits each.
    assert [(r["vertex"], r["visits"]) for r in out["top_by_visits"][:3]] == [
        (0, 12),
        (2, 12),
        (41, 12),
    ]

    by_vertex = {r["vertex"]: r for r in out["vertices"]}
    assert by_vertex[0]["stable"] == 12
    assert by_vertex[2]["stable"] == 12
    assert by_vertex[41]["stable"] == 6
    assert math.isclose(by_vertex[41]["stable_fraction"], 0.5, abs_tol=1e-15)
