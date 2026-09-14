import math

import pytest

from data.pipelines.geomagnetism.trajectory_geometry import (
    circumcircle_2d,
    kinematic_turn_operator,
    local_osculating_circle_from_geographic_triplet,
    signed_turn_angle_local,
    tangent_xy_km,
    triangle_circumradius_identity,
)


def test_circumcircle_and_abc_over_4a_identity_agree():
    a = (1.0, 0.0)
    b = (0.0, 1.0)
    c = (-1.0, 0.0)
    circle = circumcircle_2d(a, b, c)
    independent = triangle_circumradius_identity(a, b, c)
    assert circle.center_x == pytest.approx(0.0, abs=1e-15)
    assert circle.center_y == pytest.approx(0.0, abs=1e-15)
    assert circle.radius == pytest.approx(1.0, abs=1e-15)
    assert circle.curvature == pytest.approx(1.0, abs=1e-15)
    assert independent == pytest.approx(circle.radius, abs=1e-15)


def test_kinematic_turn_preserves_norm_without_energy_claim():
    result = kinematic_turn_operator((3.0, 4.0), math.pi / 3.0)
    assert result["norm_before"] == pytest.approx(5.0)
    assert result["norm_after"] == pytest.approx(5.0)
    assert result["norm_abs_error"] < 1e-12
    assert result["interpretation"] == "KINEMATIC_ROTATION_ONLY_NOT_GRAVITY_ASSIST"
    assert result["claim_allowed"] is False


def test_signed_turn_angle_quarter_turn():
    assert signed_turn_angle_local((1.0, 0.0), (0.0, 1.0)) == pytest.approx(math.pi / 2.0)
    assert signed_turn_angle_local((0.0, 1.0), (1.0, 0.0)) == pytest.approx(-math.pi / 2.0)


def test_tangent_projection_uses_middle_sample_as_fixed_center():
    origin = (80.0, 0.0)
    eastish = (80.0, 1.0)
    xy = tangent_xy_km(origin, eastish)
    assert math.hypot(*xy) > 0.0


def test_geographic_triplet_osculating_circle_is_finite_and_cross_checked():
    receipt = local_osculating_circle_from_geographic_triplet(
        previous=(80.0, -1.0),
        current=(80.1, 0.0),
        following=(80.0, 1.0),
    )
    circle = receipt["circle"]
    assert circle["radius"] > 0.0
    assert circle["curvature"] > 0.0
    assert receipt["radius_identity_abs_error_km"] < 1e-10
    assert receipt["projection"] == "AZIMUTHAL_EQUIDISTANT_CENTERED_ON_MIDDLE_SAMPLE"
    assert receipt["claim_allowed"] is False


def test_collinear_triplet_fails_closed():
    with pytest.raises(ValueError):
        circumcircle_2d((0.0, 0.0), (1.0, 0.0), (2.0, 0.0))
