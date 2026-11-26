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

    def test_age_against_scale_factor_midpoint(self):
        radiation = report()["omega_r"]
        panels = 65536
        for sector in (0.0, 0.02):
            for z in (0, 1, 10):
                with self.subTest(sector=sector, z=z):
                    width = 1 / ((1 + z) * panels)
                    def integrand(a):
                        exponent = (2 - 1 / a) / 0.3
                        decay = math.exp(-abs(exponent))
                        late_fraction = (1 if exponent >= 0 else decay) / (1 + decay)
                        matter = MATTER + sector * (1 - late_fraction)
                        vacuum = 1 - MATTER - radiation - sector * (1 - late_fraction)
                        return a / math.sqrt(radiation + matter * a + vacuum * a**4)

                    expected = HUBBLE_GYR * width * math.fsum(
                        integrand((i + 0.5) * width) for i in range(panels)
                    )
                    self.assertAlmostEqual(
                        interval_gyr(z, math.inf, sector, radiation), expected, places=7
                    )

    def test_positive_formation_delay_can_falsify_central_screen(self):
        result = report()
        age_gyr = result["source"]["age_gyr"]
        for row in result["results"]:
            with self.subTest(sector=row["omega_s0"]):
                self.assertGreater(row["age_gyr"], age_gyr)
                self.assertLess(row["age_gyr"], age_gyr + 0.5)
