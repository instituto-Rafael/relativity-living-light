import unittest
import numpy as np
from data.pipelines.structure_d.background_likelihood_v1 import Background, GaussianBlock, Row
from data.pipelines.structure_d.background_scale_profile_v1 import profile_scale, split_lya, fit_profile


def block(rows, covariance):
    return GaussianBlock(rows,covariance,[r.key for r in rows],source_ref="SYNTHETIC_TEST_ONLY",overlap_groups=("test",))


class TestScaleProfile(unittest.TestCase):
    def setUp(self):
        self.model=Background("lcdm",70.,.3,147.)
        self.rows=[Row(str(i),obs,z,self.model.predict(obs,z)) for i,(obs,z) in enumerate(
            (("DM_over_rd",.5),("DH_over_rd",.5),("DM_over_rd",2.33),("DH_over_rd",2.33)))]

    def test_exact_recovery_and_scale_degeneracy(self):
        sample=block(self.rows,np.eye(4))
        fit, report=profile_scale(sample,self.model)
        self.assertAlmostEqual(fit.rd,147.,places=10)
        self.assertLess(report["chi2"],1e-20)
        fit2, report2=profile_scale(sample,Background("lcdm",75.,.3,147.))
        self.assertAlmostEqual(report["H0_rd"],report2["H0_rd"],places=8)
        self.assertFalse(report2["claim_allowed"])

    def test_correlated_covariance(self):
        c=np.eye(4); c[0,1]=c[1,0]=.3
        sample=block(self.rows,c)
        fit,report=profile_scale(sample,self.model)
        self.assertAlmostEqual(sample.chi2(fit),report["chi2"],places=12)

    def test_reject_correlated_holdout(self):
        c=np.eye(4); c[0,2]=c[2,0]=.1
        with self.assertRaises(ValueError):
            split_lya(block(self.rows,c),(2,3))

    def test_no_holdout_refit(self):
        rows=self.rows[:2]+[Row(r.key,r.obs,r.z,r.value*1.1) for r in self.rows[2:]]
        train,test=split_lya(block(rows,np.eye(4)),(2,3))
        fit,report=profile_scale(train,self.model)
        self.assertAlmostEqual(fit.rd,147.,places=10)
        self.assertGreater(test.chi2(fit),0.)
        self.assertAlmostEqual(profile_scale(test,self.model)[1]["chi2"],0.,places=10)

    def test_bound_and_non_bao(self):
        fit,report=profile_scale(block(self.rows,np.eye(4)),self.model,(150.,200.))
        self.assertTrue(report["scale_boundary"])
        self.assertAlmostEqual(fit.rd,150.)
        with self.assertRaises(ValueError):
            profile_scale(block([Row("h","H",.5,80.)],[[1.]]),self.model)

    def test_no_promotion(self):
        _,report=fit_profile(block(self.rows,np.eye(4)),"lcdm",seeds=(42,43),maxiter=2)
        self.assertFalse(report["claim_allowed"])
        self.assertEqual(len(report["runs"]),2)
