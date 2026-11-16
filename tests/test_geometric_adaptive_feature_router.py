import math
from rx.geometric_features import (
    adaptive_numerical_policy, annulus_features, chebyshev_diagonal_ratios,
    circle_inversion, complex_divide_polar, complex_multiply_polar,
    complex_root_polar, projection_features, regular_polygon_features,
    spherical_shell_features,
)

def test_annulus_and_shell_exact_ratios():
    assert abs(annulus_features(1, 2)["annulus_area_fraction"] - 0.75) < 1e-12
    assert abs(spherical_shell_features(1, 2)["shell_volume_fraction"] - 0.875) < 1e-12

def test_circle_inversion_product():
    r = circle_inversion(3, 2)
    assert abs(r["product_invariant"] - 4.0) < 1e-12
    assert abs(r["product_invariant"] - r["expected_product"]) < 1e-12

def test_projection_identity():
    p = projection_features(math.pi / 3)
    assert abs(p["axis_ratio_b_over_a"] - 0.5) < 1e-12
    assert abs(p["unit_identity_residual"]) < 1e-12

def test_hexagon_and_diagonal_recurrence():
    h = regular_polygon_features(6)
    assert abs(h["inradius_over_circumradius"] - math.sqrt(3) / 2) < 1e-12
    assert abs(h["diagonal_recurrence_lambda"] - math.sqrt(3)) < 1e-12
    expected = [1.0, math.sqrt(3), 2.0]
    got = chebyshev_diagonal_ratios(6, 3)
    assert all(abs(a - b) < 1e-12 for a, b in zip(got, expected))

def test_complex_polar_operations():
    r, t = complex_multiply_polar(2, math.pi / 6, 3, math.pi / 3)
    assert abs(r - 6) < 1e-12 and abs(t - math.pi / 2) < 1e-12
    r, t = complex_divide_polar(6, math.pi / 2, 3, math.pi / 3)
    assert abs(r - 2) < 1e-12 and abs(t - math.pi / 6) < 1e-12
    r, t = complex_root_polar(4, 0, 2, 0)
    assert abs(r - 2) < 1e-12 and abs(t) < 1e-12

def test_adaptation_is_numerical_not_physical():
    f = {}
    f.update(annulus_features(1, 2))
    f.update(projection_features(math.pi / 3))
    f.update(regular_polygon_features(8))
    policy = adaptive_numerical_policy(f)
    assert policy["claim_allowed"] is False
    assert "numerical_resolution" in policy["allowed_adaptation"]
    for forbidden in ("H0", "Omega_m", "Omega_s0", "w0", "wa", "physical_constants"):
        assert forbidden in policy["blocked_adaptation"]
