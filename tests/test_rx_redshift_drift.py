"""Adversarial tests; synthetic/analytic, no observational claim."""
import math
import unittest
from decimal import Decimal, localcontext
from unittest.mock import patch

from rx import cosmology
from rx.redshift_drift import drift_rate_per_second, velocity_drift_cm_s

L = (67.4, .315, .02236, .8)
R0 = (67.4, .315, 0.0, 1., .3, .02236, .8)
R = (67.4, .315, .02, 1., .3, .02236, .8)
W = (67.4, .315, -1., .02236, .8)
C = (67.4, .315, -1., 0., .02236, .8)


def independent_reference(z, os0, years):
    # Independent high-precision closed expression, not a call to producer H.
    with localcontext() as ctx:
        ctx.prec = 60
        d = lambda x: Decimal(str(x))
        zp = 1 + d(z)
        f = 1 / (1 + ((d(z) - 1) / d(.3)).exp())
        e2 = d(.315)*zp**3 + d(.00009)*zp**4 + 1-d(.315)-d(.00009) \
             + d(os0)*(1-f)*(zp**3-1)
        return float(d(299792.458)*d(1e5)*d(67.4) *
                     (1-e2.sqrt()/zp) * d(years)*d(31557600) /
                     d("3.0856775814913673e19"))


class RedshiftDriftTests(unittest.TestCase):
    def test_independent_reference_and_units(self):
        for z in (0., 1e-9, .01, .5, 1., 2., 3., 4., 5., 10.):
            for model, v, os0 in (("LCDM", L, 0), ("RLL", R, .02)):
                with self.subTest(z=z, model=model):
                    got = velocity_drift_cm_s(model, z, v, 10.)
                    want = independent_reference(z, os0, 10.)
                    self.assertTrue(math.isclose(got, want, rel_tol=1e-12,
                                                 abs_tol=1e-10))
        self.assertGreater(velocity_drift_cm_s("LCDM", .5, L, 10), 0)
        self.assertLess(velocity_drift_cm_s("LCDM", 5, L, 10), 0)
        delta = velocity_drift_cm_s("RLL", 5, R, 10) - velocity_drift_cm_s("LCDM", 5, L, 10)
        self.assertAlmostEqual(delta, -.87895576234595, places=10)

    def test_nested_null_and_time_scaling(self):
        for z in (0., .5, 1., 2., 3., 5., 10.):
            l = velocity_drift_cm_s("LCDM", z, L, 10)
            for model, v in (("RLL", R0), ("wCDM", W), ("CPL", C)):
                self.assertAlmostEqual(velocity_drift_cm_s(model, z, v, 10), l, places=10)
            self.assertEqual(velocity_drift_cm_s("RLL", z, R, 0), 0)
            self.assertAlmostEqual(velocity_drift_cm_s("RLL", z, R, 20),
                                   2*velocity_drift_cm_s("RLL", z, R, 10), places=10)
        self.assertEqual(drift_rate_per_second("RLL", 0, R), 0.)

    def test_reject_invalid_domain_and_parameters(self):
        for z in (-1, 10.01, float("nan"), float("inf"), True):
            with self.assertRaises(ValueError):
                velocity_drift_cm_s("LCDM", z, L, 10)
        for t in (-1, 101, float("nan"), float("inf"), True):
            with self.assertRaises(ValueError):
                velocity_drift_cm_s("LCDM", 1, L, t)
        for model, v in (("bad", L), ("LCDM", L[:-1]), ("LCDM", L+(1,)),
                         ("LCDM", (0,)+L[1:]), ("LCDM", (float("nan"),)+L[1:]),
                         ("LCDM", (True,)+L[1:]), ("RLL", R[:4]+(0,)+R[5:])):
            with self.assertRaises(ValueError):
                drift_rate_per_second(model, 1, v)

    def test_producer_failure_is_not_zero(self):
        for hz in (0, -1, float("nan"), float("inf")):
            with patch.object(cosmology, "hubble", return_value=hz):
                with self.assertRaises(ValueError):
                    drift_rate_per_second("LCDM", 1, L)
        with patch.object(cosmology, "hubble", return_value=70.):
            with self.assertRaises(ValueError):
                drift_rate_per_second("LCDM", 0, L)
