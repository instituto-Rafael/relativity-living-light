import math
import itertools
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

    def test_influence_reversal_is_preserved(self):
        r = build()
        self.assertEqual(r["model_source_git_blob"], "f60b5f895061b91f7f47913dde0952c5760d07a7")
        self.assertEqual(r["influence_boundary"], "EXPLORATORY_NO_REFIT_NO_MODEL_SELECTION")
        total = r["leave_one_out"]["reported_total_correlation"]
        self.assertFalse(total["sign_robust"])
        self.assertAlmostEqual(total["full_delta_chi2"], -0.15076359330199, places=9)
        for row, z, delta in zip(total["omissions"], (.46,.67,.83),
                                 (.06210591810584232,.02946458954876048,-.18684886835491987)):
            self.assertEqual(row["excluded_z"], z)
            self.assertAlmostEqual(row["delta_chi2"], delta, places=9)
        self.assertEqual([row["sign_reversal"] for row in total["omissions"]], [True,True,False])
        self.assertTrue(all(not v["sign_robust"] for v in r["leave_one_out"].values()))

    def test_metamorphic_permutation_and_units(self):
        r = build()
        for name, cov in r["covariance"].items():
            for model in ("LCDM", "RLL_PROBE"):
                values = r["results"][model]["residual"]
                original = chi2(values,cov)
                for perm in itertools.permutations(range(3)):
                    with self.subTest(variant=name, model=model, perm=perm):
                        self.assertAlmostEqual(chi2([values[i] for i in perm],
                            [[cov[i][j] for j in perm] for i in perm]), original, places=10)
                for scale in (.001,1000):
                    self.assertAlmostEqual(chi2([x*scale for x in values],
                        [[x*scale**2 for x in row] for row in cov]), original, places=10)

    def test_marginal_covariance_negative(self):
        for matrix in ([[1,1],[1,1]],[[1,0],[0,-1]],[[1,2],[0,1]]):
            with self.subTest(matrix=matrix), self.assertRaises(ValueError):
                chi2([1,2],matrix)
