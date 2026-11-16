"""Deterministic geometry/field gates; no physical inference or likelihood mutation."""
import math
import unittest

from scripts.validation.rll_geometry_orbit_fields_v1 import (
    CLAIM_ALLOWED, circle_apothem_signed_m, circle_chord_m,
    kepler_ellipse_state_si, log_of_log, log_similarity_ratios,
    mean_cross_squared_distance2, newton_gravity_m_s2,
    orthographic_project2_m, rotate2, separate_field_probe,
    tangent_to_circle_normal, vacuum_dipole_tesla, vertex_covariance2,
    wrapped_angle_rad,
)


def _regular(n, radius, offset=0.0):
    return tuple(
        (radius * math.cos(offset + 2.0 * math.pi * k / n),
         radius * math.sin(offset + 2.0 * math.pi * k / n))
        for k in range(n)
    )


class GeometryFieldsV1(unittest.TestCase):
    def test_science_claim_never_raised(self):
        self.assertIs(CLAIM_ALLOWED, False)

    def test_chord_apothem_tangent_half_angle(self):
        theta = math.pi / 3.0
        chord = circle_chord_m(2, theta)
        apothem = circle_apothem_signed_m(2, theta)
        self.assertAlmostEqual(chord, 2.0)
        self.assertAlmostEqual(apothem, math.sqrt(3))
        self.assertAlmostEqual(chord / (2.0 * apothem), math.tan(theta / 2.0))

    def test_wrapped_radians(self):
        self.assertAlmostEqual(
            wrapped_angle_rad(math.radians(350), math.radians(10)), math.pi / 9
        )

    def test_2d_rotation_norm_invariant(self):
        p = (3.0, 4.0)
        q = rotate2(p, math.pi / 5)
        self.assertAlmostEqual(math.hypot(*q), 5.0)

    def test_circle_tangent_has_radial_normal(self):
        n = tangent_to_circle_normal((0, 2), (0, 0), 2)
        self.assertEqual(n, (0.0, 2.0))
        with self.assertRaises(ValueError):
            tangent_to_circle_normal((0, 1), (0, 0), 2)

    def test_orthographic_projection_not_orbit_fit(self):
        p = orthographic_project2_m((0, 3, 0), math.pi / 3)
        self.assertAlmostEqual(p[0], 0)
        self.assertAlmostEqual(p[1], 1.5)

    def test_logs_dimensionless_and_domain(self):
        q = math.sqrt(3) / 2
        logs = log_similarity_ratios(q)
        self.assertAlmostEqual(logs["ln_area"], 2 * logs["ln_length"])
        self.assertAlmostEqual(logs["ln_volume"], 3 * logs["ln_length"])
        self.assertAlmostEqual(log_of_log(math.exp(math.e)), 1)
        for x in (1, 0.9, 0, -1, float("nan")):
            with self.subTest(x=x), self.assertRaises(ValueError):
                log_of_log(x)
        with self.assertRaises(ValueError):
            log_similarity_ratios(0)

    def test_square_triangle_equal_second_moments_not_same_shape(self):
        r = math.sqrt(2)
        square = _regular(4, r, math.pi / 4)
        triangle = _regular(3, r)
        _, qs = vertex_covariance2(square)
        _, ts = vertex_covariance2(triangle)
        self.assertEqual(len(square), 4)
        self.assertEqual(len(triangle), 3)
        for i in range(2):
            for j in range(2):
                self.assertAlmostEqual(qs[i][j], 1.0 if i == j else 0.0, places=12)
                self.assertAlmostEqual(ts[i][j], 1.0 if i == j else 0.0, places=12)

    def test_covariance_rotation_equivariance(self):
        points = ((0, 0), (2, 0), (0, 1), (2, 3))
        theta = 0.37
        _, cov = vertex_covariance2(points)
        transformed = tuple(rotate2(p, theta) for p in points)
        _, actual = vertex_covariance2(transformed)
        c, s = math.cos(theta), math.sin(theta)
        R = ((c, -s), (s, c))
        expected = tuple(tuple(
            sum(R[i][k] * cov[k][l] * R[j][l] for k in range(2) for l in range(2))
            for j in range(2)) for i in range(2))
        for i in range(2):
            for j in range(2):
                self.assertAlmostEqual(actual[i][j], expected[i][j], places=12)

    def test_cross_pairs_mean_sq_distance_identity(self):
        a = _regular(4, math.sqrt(2), math.pi / 4)
        b = _regular(3, math.sqrt(2))
        direct = sum((x-u)**2 + (y-v)**2 for x,y in a for u,v in b)/(len(a)*len(b))
        self.assertAlmostEqual(direct, 4.0)
        self.assertAlmostEqual(mean_cross_squared_distance2(a, b), direct)

    def test_covariance_input_guards(self):
        with self.assertRaises(ValueError):
            vertex_covariance2(((0, 0),))
        with self.assertRaises(ValueError):
            vertex_covariance2(((0, 0), (float("inf"), 0)))

    def test_orbit_circular_and_vis_viva(self):
        mu, a = 8.0, 4.0
        result = kepler_ellipse_state_si(mu, a, 0, math.pi/3)
        self.assertAlmostEqual(result["radius_m"], a)
        self.assertAlmostEqual(result["specific_energy_m2_s2"], -mu/(2*a))
        self.assertAlmostEqual(result["specific_h_m2_s"], math.sqrt(mu*a))
        self.assertIs(result["claim_allowed"], False)

    def test_orbit_elliptical_energy_h_all_true_anomalies(self):
        mu, a, e, inc = 3.986004418e14, 9e6, 0.4, math.pi/6
        expected_e = -mu/(2*a)
        expected_h = math.sqrt(mu*a*(1-e*e))
        for deg in range(0, 360, 15):
            with self.subTest(deg=deg):
                result = kepler_ellipse_state_si(mu, a, e, math.radians(deg), inc)
                self.assertAlmostEqual(result["specific_energy_m2_s2"]/expected_e, 1.0, places=12)
                self.assertAlmostEqual(result["specific_h_m2_s"]/expected_h, 1.0, places=12)
        self.assertAlmostEqual(kepler_ellipse_state_si(mu,a,e,0)["radius_m"], a*(1-e))
        self.assertAlmostEqual(kepler_ellipse_state_si(mu,a,e,math.pi)["radius_m"], a*(1+e))

    def test_orbit_rejects_nonellipse_or_invalid_mu(self):
        for e in (-0.1, 1.0, 1.1, float("nan")):
            with self.subTest(e=e), self.assertRaises(ValueError):
                kepler_ellipse_state_si(10, 10, e, 0)
        with self.assertRaises(ValueError):
            kepler_ellipse_state_si(0, 10, 0.2, 0)

    def test_gravity_inverse_square_and_singularity(self):
        near = newton_gravity_m_s2(8, (2,0,0))[0]
        far = newton_gravity_m_s2(8, (4,0,0))[0]
        self.assertAlmostEqual(near, -2)
        self.assertAlmostEqual(far, -0.5)
        with self.assertRaises(ValueError):
            newton_gravity_m_s2(8, (0,0,0))

    def test_dipole_inverse_cube_axis_vs_equator(self):
        m = (0,0,1)
        near = vacuum_dipole_tesla((0,0,2),m)[2]
        far = vacuum_dipole_tesla((0,0,4),m)[2]
        equator = vacuum_dipole_tesla((2,0,0),m)[2]
        self.assertAlmostEqual(near, 2.5e-8)
        self.assertAlmostEqual(near/far, 8.0)
        self.assertAlmostEqual(equator, -1.25e-8)
        with self.assertRaises(ValueError):
            vacuum_dipole_tesla((0,0,0),m)

    def test_independent_field_models_not_background_likelihood(self):
        out = separate_field_probe(8,4,0.2,0.5,0.2,(0,0,1))
        self.assertEqual(out["cosmological_likelihood_binding"], "BLOCKED")
        self.assertEqual(out["measurement_covariance"], "TOKEN_VAZIO")
        self.assertFalse(out["claim_allowed"])
        self.assertEqual(out["mechanisms"], ("NEWTON_POINT_MASS", "VACUUM_STATIC_DIPOLE"))
        self.assertEqual(len(out["gravity_m_s2"]), 3)
        self.assertEqual(len(out["dipole_B_tesla"]), 3)


if __name__ == "__main__":
    unittest.main()
