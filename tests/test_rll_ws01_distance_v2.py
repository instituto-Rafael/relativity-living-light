import math
import unittest
from rx import cosmology
from tools.rll_ws01_distance_v2 import accepts, build, load


class WS01V2Tests(unittest.TestCase):
    def test_protocol_preserves_negative_predecessor(self):
        c = load()
        self.assertEqual(c["predecessor"]["result"], "FAIL_PREREGISTERED_DISTANCE_TOLERANCE")
        self.assertFalse(c["claim_allowed"])
        self.assertEqual(c["tolerance"], {"rtol": 1e-6, "atol_mpc": .001})

    def test_negative_comparisons(self):
        for a,b in ((float("nan"), 1), (1, float("inf")), (0,0), (-1,-1), (100.01,100)):
            with self.subTest(a=a,b=b):
                self.assertFalse(accepts(a,b))
        self.assertTrue(accepts(100.0001,100))

    def test_full_successor_matrix_no_claim(self):
        before = cosmology.ORAD
        result = build()
        self.assertEqual(cosmology.ORAD, before)
        self.assertFalse(result["claim_allowed"])
        self.assertFalse(result["promotion_allowed"])
        self.assertEqual(result["row_count"], 51)
        self.assertEqual(result["replay_rows"], 33)
        self.assertEqual(result["additional_rows"], 18)
        self.assertEqual(result["failures"], [])
        self.assertEqual(result["state"], "PASS_V2_NUMERIC_SCOPED")
