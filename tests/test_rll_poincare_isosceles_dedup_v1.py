#!/usr/bin/env python3
"""RLL cross-domain *synthetic mathematical* regression tests (not physics).

Producer: instituto-Rafael/relativity-living-light.
Independent reference: docs/science/RLL_MATH_LITERATURE_COHERENCE_AUDIT_20260808.md
Poincare gate: PapersPub/09_poincare_ball_7d_freestanding/scripts/validate_poincare_7d_emergents.py
No DESI fit, hardware execution, physical measurement, Poincare-conjecture proof,
or claim promotion is performed. Only Python standard library is used.
"""
import math
import unittest


def isosceles(L, half_apex):
    assert L > 0 and 0 < half_apex < math.pi / 2
    return 2 * L * math.sin(half_apex), L * math.cos(half_apex)


def logistic(z, z_t, w_t):
    assert z > -1 and w_t > 0
    x = (z - z_t) / w_t
    return 1 / (1 + math.exp(x))


def rll_dimensionless(z, z_t, w_t):
    a = 1 / (1 + z)
    f = logistic(z, z_t, w_t)
    f_prime = (1 + z) * f * (1 - f) / w_t  # df/dln(a)
    R = f + (1 - f) * a**-3
    R_prime = f_prime * (1 - a**-3) - 3 * (1 - f) * a**-3
    documented_pressure = -f
    conserved_pressure = -R - R_prime / 3
    documented_continuity = R_prime + 3 * (R + documented_pressure)
    conserved_continuity = R_prime + 3 * (R + conserved_pressure)
    return f, R, documented_continuity, conserved_continuity, f_prime * (1-a**-3)


def hyperboloid_ball(q):
    assert len(q) == 7 and all(math.isfinite(v) for v in q)
    x0 = math.sqrt(1 + sum(x*x for x in q))
    p = [x / (x0 + 1) for x in q]
    radius2 = sum(v*v for v in p)
    return x0, p, radius2


class MathAndScopeGates(unittest.TestCase):
    def test_pythagoras_difference_identity(self):
        for a,b in [(3,4), (1.5,2.0), (0,7), (13,5)]:
            self.assertAlmostEqual(a*a + b*b, 2*a*b + (a-b)**2)

    def test_law_of_cosines_right_angle_specialization(self):
        a,b = 3.4, 6.5
        self.assertAlmostEqual(a*a+b*b-2*a*b*math.cos(math.pi/2),a*a+b*b)

    def test_isosceles_altitude_pythagoras(self):
        for deg in [5,10,30,45,70]:
            base,height=isosceles(13,math.radians(deg))
            self.assertAlmostEqual(height**2+(base/2)**2,13**2,places=10)

    def test_isosceles_ten_degree_apex_not_ten_degree_half_apex(self):
        b10,h10=isosceles(1,math.radians(5))
        b20,h20=isosceles(1,math.radians(10))
        self.assertAlmostEqual(b10,2*math.sin(math.radians(5)))
        self.assertNotAlmostEqual(b10,b20,places=6)
        self.assertNotAlmostEqual(h10,h20,places=6)

    def test_30_degree_half_apex_equilateral_gate(self):
        L=8
        b,h=isosceles(L,math.radians(30))
        self.assertAlmostEqual(b,L)
        self.assertAlmostEqual(h, math.sqrt(3)*L/2)

    def test_two_distinct_inscribed_and_radial_heights(self):
        r=7
        radial=math.sqrt(3)*r/2
        maximal_inscribed=3*r/2
        self.assertNotAlmostEqual(radial,maximal_inscribed)

    def test_sqrt3_over_two_is_not_sqrt_three_halves(self):
        self.assertNotAlmostEqual(math.sqrt(3)/2,math.sqrt(3/2),places=7)

    def test_gram_determinant_triangle_area(self):
        u,v=(3.0,0.0),(1.0,4.0)
        gram_det=(u[0]**2+u[1]**2)*(v[0]**2+v[1]**2)-(u[0]*v[0]+u[1]*v[1])**2
        self.assertAlmostEqual(math.sqrt(gram_det)/2, abs(u[0]*v[1]-u[1]*v[0])/2)

    def test_circle_chord_discriminant_unit_speed_only(self):
        r,d=10.0,6.0
        q2=r*r-d*d
        self.assertAlmostEqual(4*q2,4*(r*r-d*d))
        speed=3.0
        self.assertNotAlmostEqual(4*q2,4*speed*speed*q2)

    def test_hyperboloid_lift_ball_identity_and_inverse(self):
        x0,p,r2=hyperboloid_ball([0.5,-0.3,0.2,0.1,0.0,0.0,1.1])
        self.assertLess(r2,1)
        xr=(1+r2)/(1-r2)
        q_back=[2*v/(1-r2) for v in p]
        self.assertAlmostEqual(x0,xr,places=12)
        for actual,expected in zip(q_back,[.5,-.3,.2,.1,0,0,1.1]):
            self.assertAlmostEqual(actual,expected,places=12)

    def test_torus_is_not_7_sphere_fundamental_group(self):
        torus_pi1_rank=7
        sphere7_pi1_rank=0
        self.assertNotEqual(torus_pi1_rank,sphere7_pi1_rank)

    def test_rll_documented_pressure_fails_nonzero_redshift(self):
        for z in (0.2,0.5,1.5):
            f,R,residual,closed,expected=rll_dimensionless(z,0.75,0.5)
            self.assertAlmostEqual(residual, expected,places=10)
            self.assertGreater(abs(residual),1e-7)
            self.assertLess(abs(closed),1e-10)

    def test_rll_documented_pressure_zero_at_a_one_is_not_global_closure(self):
        f,R,residual,closed,expected=rll_dimensionless(0,0.75,0.5)
        self.assertAlmostEqual(residual,0,places=12)

    def test_rll_conserved_pressure_closes_by_construction(self):
        for z in (0,0.01,0.1,0.5,2.0):
            self.assertLess(abs(rll_dimensionless(z,.75,.5)[3]),1e-10)

    def test_rll_numerical_derivative_reproduces_exact_residual(self):
        z,zt,wt=0.5,.75,.5
        x=-math.log1p(z)
        def R_of_x(x):
            a=math.exp(x); z=1/a-1
            f=logistic(z,zt,wt)
            return f+(1-f)*a**-3
        h=1e-6
        diff=(R_of_x(x+h)-R_of_x(x-h))/(2*h)
        f,R,res,closed,_=rll_dimensionless(z,zt,wt)
        self.assertAlmostEqual(diff+3*(R-f),res,delta=1e-8)

    def test_scoped_claim_remains_false(self):
        claim_allowed=False
        self.assertIs(claim_allowed,False)

if __name__ == '__main__':
    unittest.main(verbosity=2)
