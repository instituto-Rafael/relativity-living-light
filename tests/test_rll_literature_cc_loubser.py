import math
import unittest
from rx import cosmology
from tools.rll_literature_cc_loubser import build, chi2, covariance


class LiteratureCCScreenTests(unittest.TestCase):
    def test_fixed_screen_and_null_equivalence(self):
        before = cosmology.ORAD
        r = build()
        self.assertEqual(cosmology.ORAD,before)
        self.assertFalse(r["claim_allowed"])
        self.assertFalse(r["promotion_allowed"])
        self.assertEqual(r["model_selection"],"NOT_RUN")
        self.assertEqual(r["joint_ingestion"],"BLOCKED_OVERLAP_AND_COVARIANCE_NOT_VERIFIED")
        self.assertEqual(r["results"]["LCDM"],r["results"]["RLL_NULL"])
        self.assertAlmostEqual(r["results"]["LCDM"]["chi2"]["reported_total_correlation"],8.339544344362523,places=9)
        self.assertAlmostEqual(r["results"]["RLL_PROBE"]["chi2"]["reported_total_correlation"],8.188780751060529,places=9)
        self.assertAlmostEqual(r["results"]["LCDM"]["chi2"]["systematic_only_sensitivity"],4.542278355903113,places=9)
        self.assertAlmostEqual(r["results"]["RLL_PROBE"]["chi2"]["diagonal_diagnostic"],1.2954817560877085,places=9)

    def test_covariance_failure(self):
        for c in ([[1,1,1],[1,1,1],[1,1,1]],[[1,2,0],[0,1,0],[0,0,1]],[[1,0,0],[0,-1,0],[0,0,1]]):
            with self.subTest(c=c), self.assertRaises(ValueError):
                chi2([1,2,3],c)
        with self.assertRaises(ValueError):
            chi2([math.nan,0,0],[[1,0,0],[0,1,0],[0,0,1]])

    def test_invalid_errors_and_correlation(self):
        rows = [{"stat":1,"syst":1} for _ in range(3)]
        with self.assertRaises(ValueError):
            covariance(rows,[[1,.1,0],[.2,1,0],[0,0,1]],"reported_total_correlation")
        rows[0]["stat"]=0
        with self.assertRaises(ValueError):
            covariance(rows,[[1,0,0],[0,1,0],[0,0,1]],"diagonal_diagnostic")
