import unittest
import numpy as np
from data.pipelines.structure_d.background_likelihood_v1 import Background, Row, GaussianBlock, BackgroundLikelihood, fit_background

def block(rows,cov,groups=('bao',),axis=None,sn=None):
    return GaussianBlock(rows,cov,[r.key for r in rows] if axis is None else axis,source_ref='SYNTHETIC_TEST_ONLY',overlap_groups=groups,sn_catalog=sn)

class TestBackground(unittest.TestCase):
    def setUp(self):
        self.lcdm=Background('lcdm',70,.3,147)
        self.rll=Background('rll',70,.3,147)
        self.rows=[Row('dm','DM_over_rd',.5,13.),Row('dh','DH_over_rd',.5,22.)]
    def test_null(self):
        for z in (0,.01,.5,2.33,10):
            self.assertEqual(self.lcdm.h(z),self.rll.h(z))
            self.assertEqual(self.lcdm.h(z),Background('cpl',70,.3,147).h(z))
        b=block(self.rows,[[1,.3],[.3,1]])
        self.assertEqual(b.chi2(self.lcdm),b.chi2(self.rll))
    def test_covariance(self):
        cov=np.array([[1,.3],[.3,1]])
        b=block(self.rows,cov)
        r=np.array([p.value-self.lcdm.predict(p.obs,p.z) for p in self.rows])
        self.assertAlmostEqual(b.chi2(self.lcdm),r@np.linalg.solve(cov,r))
    def test_wrong_axis(self):
        with self.assertRaises(ValueError): block(self.rows,np.eye(2),axis=['dh','dm'])
    def test_bad_covariance(self):
        for c in ([[1,2],[2,1]],[[1,.1],[.2,1]],[[1,0],[0,float('nan')]],None):
            with self.assertRaises((ValueError,np.linalg.LinAlgError)): block(self.rows,c)
    def test_overlap(self):
        a=block(self.rows,np.eye(2)); b=block(self.rows,np.eye(2))
        with self.assertRaises(ValueError): BackgroundLikelihood([a,b])
    def test_sn_offset(self):
        rows=[Row('s1','SN_mu',.2,40,.201),Row('s2','SN_mu',.5,43,.501)]
        shifted=[Row(r.key,r.obs,r.z,r.value+4,r.zhel) for r in rows]
        self.assertAlmostEqual(block(rows,np.eye(2),('sn1',),sn='one').chi2(self.lcdm),block(shifted,np.eye(2),('sn1',),sn='one').chi2(self.lcdm))
        with self.assertRaises(ValueError): BackgroundLikelihood([block(rows,np.eye(2),('sn1',),sn='one'),block(rows,np.eye(2),('sn2',),sn='two')])
    def test_fail_closed(self):
        for name in ('fsigma8','Cl'):
            self.assertTrue(self.rll.physical_outputs()[name].startswith('TOKEN_VAZIO'))
            with self.assertRaises(ValueError): self.rll.predict(name,1.)
        with self.assertRaises(ValueError): Background('rll',70,.8,147,os0=.3)
        with self.assertRaises(ValueError): Background('lcdm',float('nan'),.3,147)
    def test_holdout(self):
        a=block(self.rows,np.eye(2)); b=block([Row('h','H',.2,80.)],[[25]],('cc',))
        train,test=BackgroundLikelihood([a,b]).split(1)
        self.assertEqual(train.blocks,(a,)); self.assertIs(test,b)
        self.assertFalse(train.evaluate(self.lcdm)['claim_allowed'])
    def test_matterlike_not_vanishing(self):
        m=Background('rll',70,.3,147,os0=.02)
        self.assertAlmostEqual((m.h(100)/self.lcdm.h(100))**2, .32/.3,places=5)

    def test_fit_scale_degeneracy(self):
        a=BackgroundLikelihood([block(self.rows,np.eye(2))])
        with self.assertRaises(ValueError): fit_background(a,'lcdm',{'h0':(60,80),'om':(.1,.6),'rd':(100,200)})
    def test_fit_does_not_promote(self):
        a=BackgroundLikelihood([block(self.rows,np.eye(2))])
        result=fit_background(a,'lcdm',{'rd':(100,200)},fixed={'h0':70,'om':.3},maxiter=2,seeds=(42,43))
        self.assertFalse(result['claim_allowed'])
        self.assertEqual(len(result['runs']),2)
    def test_duplicate_key_across_distinct_groups(self):
        with self.assertRaises(ValueError): BackgroundLikelihood([block(self.rows,np.eye(2),('a',)),block(self.rows,np.eye(2),('b',))])
