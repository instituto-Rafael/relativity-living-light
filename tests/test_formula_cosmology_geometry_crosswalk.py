from tools.check_formula_cosmology_geometry_crosswalk import (
    registry_gate,
    desi_geometry_gate,
    cone_annulus_gate,
    model_null_gate,
)


def test_all_251_formulas_are_imported_and_routed():
    result = registry_gate()
    assert result["status"] == "PASS"
    assert result["count"] == 251
    assert result["missing"] == []
    assert result["duplicates"] == []
    assert result["unclassified_routes"] == []


def test_desi_dr2_observation_geometry_and_covariance():
    result = desi_geometry_gate()
    assert result["status"] == "PASS"
    assert result["point_count"] == 13
    assert result["anisotropic_pair_count"] == 6
    assert result["covariance_min_eigenvalue"] > 0


def test_circle_triangle_cone_annulus_exact_geometry():
    result = cone_annulus_gate()
    assert result["status"] == "PASS"


def test_rll_null_limit_matches_flat_lcdm_geometry():
    result = model_null_gate()
    assert result["status"] == "PASS"
