import math
import unittest

from tools.rll_session_geometry_closure_v1 import (
    CLAIM_ALLOWED,
    DRAWING_ROLE,
    IMAGE_METRIC_ROLE,
    PHYSICAL_BINDING,
    annular_sector,
    arc_chord_index,
    circularity_regular_polygon,
    inscribed_rotated_square_side,
    isosceles_from_circle,
    iterated_log,
    kappa_from_lambda,
    kappa_regular_polygon,
    lambda_n,
    phase_point,
    project_point,
    receipt,
    regular_polygon_area,
    regular_polygon_perimeter,
    rotate_point,
    rotated_square_family,
    square_projection_width,
    star_winding,
)


class SessionGeometryClosureV1Tests(unittest.TestCase):
    def test_claim_and_image_boundaries_are_fail_closed(self):
        self.assertFalse(CLAIM_ALLOWED)
        self.assertEqual(PHYSICAL_BINDING, "TOKEN_VAZIO_PHYSICAL_BINDING")
        self.assertEqual(DRAWING_ROLE, "DRAWING_TOPOLOGY_ONLY")
        self.assertEqual(IMAGE_METRIC_ROLE, "TOKEN_VAZIO_CALIBRATION")

    def test_residue_zero_is_defined_phase_point(self):
        residue, theta, x, y = phase_point(21, 7)
        self.assertEqual(residue, 0)
        self.assertAlmostEqual(theta, 0.0)
        self.assertAlmostEqual(x, 1.0)
        self.assertAlmostEqual(y, 0.0)

    def test_lambda_family(self):
        phi = (1.0 + math.sqrt(5.0)) / 2.0
        self.assertAlmostEqual(lambda_n(3), 1.0)
        self.assertAlmostEqual(lambda_n(4), math.sqrt(2.0))
        self.assertAlmostEqual(lambda_n(5), phi)
        self.assertAlmostEqual(lambda_n(6), math.sqrt(3.0))
        self.assertAlmostEqual(lambda_n(8), math.sqrt(2.0 + math.sqrt(2.0)))
        self.assertAlmostEqual(lambda_n(12), math.sqrt(2.0 + math.sqrt(3.0)))

    def test_kappa_is_same_family_as_lambda(self):
        phi = (1.0 + math.sqrt(5.0)) / 2.0
        for n in (3, 4, 5, 6, 8, 12, 1000):
            self.assertAlmostEqual(kappa_regular_polygon(n), kappa_from_lambda(lambda_n(n)), places=12)
        self.assertAlmostEqual(kappa_regular_polygon(3), 1.0 / 4.0)
        self.assertAlmostEqual(kappa_regular_polygon(4), 1.0 / 3.0)
        self.assertAlmostEqual(kappa_regular_polygon(5), (phi + 3.0) / 12.0)
        self.assertAlmostEqual(kappa_regular_polygon(6), 5.0 / 12.0)
        self.assertAlmostEqual(kappa_regular_polygon(100000), 0.5, places=8)

    def test_isosceles_pentagonal_relation(self):
        phi = (1.0 + math.sqrt(5.0)) / 2.0
        data = isosceles_from_circle(1.0, math.pi / 5.0)
        self.assertAlmostEqual(data["base"], 1.0 / phi, places=12)
        self.assertAlmostEqual(1.0 / data["base"], phi, places=12)

    def test_regular_polygon_circle_limits(self):
        radius = 2.0
        for n in (100, 1000, 10000):
            perimeter = regular_polygon_perimeter(radius, n)
            area = regular_polygon_area(radius, n)
            self.assertLess(perimeter, 2.0 * math.pi * radius)
            self.assertLess(area, math.pi * radius * radius)
        self.assertAlmostEqual(regular_polygon_perimeter(radius, 100000), 2.0 * math.pi * radius, places=7)
        self.assertAlmostEqual(regular_polygon_area(radius, 100000), math.pi * radius * radius, places=7)
        self.assertLess(circularity_regular_polygon(4), circularity_regular_polygon(5))
        self.assertAlmostEqual(circularity_regular_polygon(100000), 1.0, places=8)

    def test_arc_chord_index(self):
        for theta in (0.1, 0.5, 1.0):
            self.assertGreater(arc_chord_index(theta), 1.0)
        self.assertAlmostEqual(arc_chord_index(1e-8), 1.0, places=12)

    def test_annular_sin_rad_tan_sandwich(self):
        data = annular_sector(3.0, 1.0, math.pi / 6.0)
        self.assertAlmostEqual(data["K"], 4.0)
        self.assertTrue(data["acute_domain"])
        self.assertTrue(data["sandwich_holds"])
        self.assertGreater(data["curve_minus_chord"], 0.0)
        self.assertGreater(data["tangent_minus_curve"], 0.0)

    def test_rotation_projection_covariance_identity(self):
        x, y = 2.0, -1.0
        theta = 0.37
        alpha = 1.2
        xr, yr = rotate_point(x, y, theta)
        left = project_point(xr, yr, alpha)
        right = project_point(x, y, alpha - theta)
        self.assertAlmostEqual(left, right, places=12)

    def test_square_projection_and_inscribed_square(self):
        side = 2.0
        theta = math.pi / 4.0
        self.assertAlmostEqual(square_projection_width(side, theta), side * math.sqrt(2.0))
        inner = inscribed_rotated_square_side(side, theta)
        self.assertAlmostEqual(inner, side / math.sqrt(2.0))
        self.assertAlmostEqual((inner * inner) / (side * side), 0.5)

    def test_rotated_square_family_1_2_3_and_limits(self):
        f1 = rotated_square_family(1)
        f2 = rotated_square_family(2)
        f3 = rotated_square_family(3)
        self.assertEqual((f1.sides, f2.sides, f3.sides), (4, 8, 12))
        self.assertAlmostEqual(f1.normalized_area_outer_square, 1.0)
        self.assertAlmostEqual(f2.normalized_area_outer_square, 2.0 * (math.sqrt(2.0) - 1.0), places=12)
        self.assertAlmostEqual(f3.normalized_area_outer_square, 3.0 * (2.0 - math.sqrt(3.0)), places=12)
        self.assertGreater(f1.area, f2.area)
        self.assertGreater(f2.area, f3.area)
        f_large = rotated_square_family(100000)
        self.assertGreater(f_large.area, math.pi)
        self.assertGreater(f_large.perimeter, 2.0 * math.pi)
        self.assertAlmostEqual(f_large.area, math.pi, places=8)
        self.assertAlmostEqual(f_large.perimeter, 2.0 * math.pi, places=8)

    def test_pentagram_winding_is_not_phi(self):
        data = star_winding(5, 2)
        self.assertEqual(data["components"], 1)
        self.assertEqual(data["orbit_length"], 5)
        self.assertEqual(data["winding_per_connected_orbit"], 2)
        self.assertAlmostEqual(data["step_angle"], 4.0 * math.pi / 5.0)

    def test_iterated_log_base_is_explicit_and_domain_stops(self):
        natural = iterated_log(999.0, math.e, 8)
        base10 = iterated_log(999.0, 10.0, 8)
        self.assertEqual(natural["state"], "STOP_REAL_DOMAIN")
        self.assertEqual(base10["state"], "STOP_REAL_DOMAIN")
        self.assertAlmostEqual(natural["values"][0], math.log(999.0), places=12)
        self.assertAlmostEqual(base10["values"][0], math.log10(999.0), places=12)
        self.assertNotAlmostEqual(natural["values"][1], base10["values"][1])
        self.assertLess(natural["values"][-1], 0.0)
        self.assertLess(base10["values"][-1], 0.0)

    def test_receipt_gates_all_pass(self):
        data = receipt()
        self.assertFalse(data["claim_allowed"])
        self.assertTrue(all(data["gates"].values()))


if __name__ == "__main__":
    unittest.main()
