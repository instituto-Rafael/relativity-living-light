"""RLL comparator source-invariant guards; no new fit."""
import tempfile,unittest
from pathlib import Path
from tools.ci.rll_comparator_evidence_matrix_v1 import audit,ic,FILES
ROOT=Path(__file__).resolve().parents[1]
class EvidenceMatrix(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=audit(ROOT)
 def test_five_regimes(self):
    self.assertEqual(set(self.r["regimes"]),{"joint64_scan","desi13","joint64_other","legacy45","growth16"})
 def test_joint_penalty_and_Os0(self):
    d=self.r["regimes"]["joint64_scan"]
    self.assertEqual(d["RLL_Os0"],0.0)
    self.assertGreater(d["delta_rll_minus_models"]["LCDM"]["AICc"],0)
    self.assertGreater(d["delta_rll_minus_models"]["CPL"]["AICc"],0)
 def test_two_64_not_merged(self):
    d=self.r["regimes"]
    self.assertNotAlmostEqual(d["joint64_scan"]["delta_rll_minus_models"]["LCDM"]["chi2"],d["joint64_other"]["delta_rll_minus_lcdm"]["chi2"],places=1)
    self.assertTrue(d["joint64_other"]["different_parameterization"])
 def test_desi_legacy_are_negative_for_rll(self):
    d=self.r["regimes"]
    self.assertGreater(d["desi13"]["delta_rll_minus_lcdm"]["chi2"],0)
    self.assertGreater(d["legacy45"]["delta_rll_minus_lcdm"]["AIC"],0)
 def test_growth_limited(self):
    d=self.r["regimes"]["growth16"]
    self.assertLess(d["delta_chi2_rll_minus_lcdm"],0)
    self.assertEqual(d["covariance"],"diagonal_only")
 def test_physics_not_promoted(self):
    self.assertFalse(self.r["claim_allowed"])
    for k in ("full_CMB_TT_TE_EE_Cl","nonlinear_Pk","RLL_perturbation_CLASS_CAMB_closure"):
        self.assertEqual(self.r["features"][k],"TOKEN_VAZIO")
 def test_aicc_formula(self):
    self.assertAlmostEqual(ic(93.95983068903539,64,8)["AICc"],112.57801250721721)
    with self.assertRaises(ValueError):ic(1,8,8)
 def test_missing_data_fails_closed(self):
    with tempfile.TemporaryDirectory() as d:
        with self.assertRaises(FileNotFoundError):audit(Path(d))
 def test_source_sha256_receipts(self):
    self.assertEqual(set(FILES),set(self.r["sources"]))
    self.assertTrue(all(len(x["sha256"])==64 and x["bytes"]>0 for x in self.r["sources"].values()))
if __name__=="__main__":unittest.main(verbosity=2)
