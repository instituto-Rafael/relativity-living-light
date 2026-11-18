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


def test_covariance_rejects_indefinite_even_at_tiny_scale():
    for values in ((0.0, 1e-8, 0.0), (1.0, 2.0, 1.0), (-1.0, 0.0, 1.0)):
        try:
            covariance_ellipse_2d(*values)
        except ValueError:
            pass
        else:
            raise AssertionError("indefinite covariance was accepted")


def test_covariance_and_mahalanobis_are_scale_invariant():
    for scale in (1e-20, 1e-6, 1.0, 1e8, 1e20):
        c = covariance_ellipse_2d(4.0 * scale, 0.0, scale)
        assert math.isclose(c["axis_ratio_q"], 0.5, rel_tol=1e-13)
        assert math.isclose(c["condition_number"], 4.0, rel_tol=1e-13)
        dx, dy = 2.0 * math.sqrt(scale), math.sqrt(scale)
        assert math.isclose(
            mahalanobis2_2d(dx, dy, 4.0 * scale, 0.0, scale),
            2.0, rel_tol=1e-13)


def test_covariance_zero_and_invalid_values_fail_closed():
    zero = covariance_ellipse_2d(0.0, 0.0, 0.0)
    assert zero["lambda_major"] == zero["lambda_minor"] == 0.0
    assert zero["claim_allowed"] is False
    for args in ((math.nan, 0.0, 1.0), (math.inf, 0.0, 1.0)):
        try:
            covariance_ellipse_2d(*args)
        except ValueError:
            pass
        else:
            raise AssertionError("nonfinite covariance was accepted")
    for args in ((1.0, 0.0, 0.0, 0.0, 0.0),
                 (1.0, 0.0, 1.0, 1.0, 1.0),
                 (math.nan, 0.0, 1.0, 0.0, 1.0)):
        try:
            mahalanobis2_2d(*args)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid Mahalanobis residual was accepted")


def test_local_curve_rejects_nonfinite_inputs():
    import pytest
    for v,a,j in (
        ((math.nan,1,0),(1,0,0),None),
        ((1,0,0),(math.inf,0,0),None),
        ((1,0,0),(0,1,0),(math.nan,0,0)),
        ((1,0,0),(0,1,0),(0,0,math.inf)),
    ):
        with pytest.raises(ValueError):
            local_curve_invariants_3d(v,a,j)


def test_local_curve_rejects_nonfinite_intermediate_results():
    import pytest
    for v,a,j in (
        ((1e200,0,0),(0,0,0),None),
        ((1,0,0),(0,1e200,0),(0,0,1e200)),
        ((1e150,0,0),(0,1e150,0),None),
    ):
        with pytest.raises(ValueError):
            local_curve_invariants_3d(v,a,j)
    valid = local_curve_invariants_3d((1.,0.,0.),(0.,1.,0.),(0.,0.,1.))
    assert valid["curvature"] == 1.0
    assert valid["torsion"] == 1.0


def test_bao_extreme_magnitudes_fail_closed_without_silent_inf():
    import pytest
    for x, y in (
        (1e300, 1e-300),  # finite inputs, ratio overflows
        (1e-300, 1e-300), # finite inputs, product underflows
        (1e160, 1e160),   # finite inputs, product overflows
        (1e155, 1e-155),  # derived ellipse/metric not representable
        (1e-320, 1e308), # derived ratio underflows
    ):
        with pytest.raises(ValueError):
            bao_observable_geometry(x, y)


def test_bao_log_coordinates_stable_at_representable_scales():
    for x, y in (
        (1e-150, 1e-150), (1e150, 1e150),
        (1e-200, 1e100), (0.0001, 100.0),
    ):
        g = bao_observable_geometry(x, y)
        assert math.isclose(g["reconstruction"]["DM_over_rd"], x, rel_tol=1e-12)
        assert math.isclose(g["reconstruction"]["DH_over_rd"], y, rel_tol=1e-12)
        assert math.isfinite(g["log_scale"])
        assert math.isfinite(g["anisotropy_log_ratio"])
        assert g["claim_allowed"] is False
