import math
import unittest

from tools.rll_age_gate import HUBBLE_GYR, MATTER, interval_gyr, report


class AgeGateTests(unittest.TestCase):
    def test_null_and_order(self):
        for z in (0, 1, 4.658, 12):
            vacuum = 1 - MATTER
            expected = 2 * HUBBLE_GYR / (3 * math.sqrt(vacuum)) * math.asinh(
                math.sqrt(vacuum / MATTER) / (1 + z)**1.5)
            self.assertAlmostEqual(interval_gyr(z, math.inf, 0, 0), expected, places=8)
            self.assertLess(interval_gyr(z, math.inf, 0.02, 0), expected)

    def test_closure(self):
        radiation = report()["omega_r"]
        total = interval_gyr(0, math.inf, 0.02, radiation)
        parts = interval_gyr(0, 1, 0.02, radiation) + interval_gyr(1, math.inf, 0.02, radiation)
        self.assertAlmostEqual(parts, total, places=8)

    def test_observed_margin(self):
        result = report()
        self.assertFalse(result["claim_allowed"])
        self.assertAlmostEqual(result["results"][1]["formation_margin_gyr"], 0.238816, places=5)

    def test_invalid_interval(self):
        with self.assertRaises(ValueError):
            interval_gyr(2, 1, 0, 0)
