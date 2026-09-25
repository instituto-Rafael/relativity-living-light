import math
from rx.adaptive_geometry import (
    bao_observable_geometry,
    covariance_ellipse_2d,
    local_curve_invariants_3d,
    mahalanobis2_2d,
)


def test_bao_geometry_is_invertible_and_redundancy_is_explicit():
    g = bao_observable_geometry(13.588, 21.863)
    assert abs(g["F_AP"] - 0.6215066550793578) < 1e-15
    assert abs(g["reconstruction"]["DM_over_rd"] - 13.588) < 1e-12
    assert abs(g["reconstruction"]["DH_over_rd"] - 21.863) < 1e-12
    assert abs(g["redundancy_identities"]["phi_equals_atan_F_AP"]) < 1e-15
    assert abs(g["redundancy_identities"]["ellipse_area_minus_2pi_triangle_area"]) < 1e-12
    assert abs(g["redundancy_identities"]["rho2_minus_product_times_ratio_plus_inverse"]) < 1e-12
    assert g["claim_allowed"] is False


def test_covariance_ellipse_and_mahalanobis_are_standard_diagnostics():
    c = covariance_ellipse_2d(4.0, 0.0, 1.0)
    assert abs(c["axis_major_1sigma"] - 2.0) < 1e-15
    assert abs(c["axis_minor_1sigma"] - 1.0) < 1e-15
    assert abs(c["axis_ratio_q"] - 0.5) < 1e-15
    assert abs(c["condition_number"] - 4.0) < 1e-15
    assert abs(mahalanobis2_2d(2.0, 1.0, 4.0, 0.0, 1.0) - 2.0) < 1e-15


def test_local_curve_invariants_recover_unit_circle_geometry():
    k = local_curve_invariants_3d((0, 1, 0), (-1, 0, 0), (0, -1, 0))
    assert abs(k["curvature"] - 1.0) < 1e-15
    assert abs(k["torsion"]) < 1e-15
    assert abs(k["normal_acceleration"] - 1.0) < 1e-15
    assert k["claim_allowed"] is False
