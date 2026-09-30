import unittest
from tools.rll_ws01_background_decision_evidence import build

class WS01BackgroundDecisionEvidenceTests(unittest.TestCase):
 def test_fail_closed_and_finite(self):
  r=build()
  self.assertFalse(r["claim_allowed"])
  self.assertFalse(r["decision_selected"])
  self.assertEqual(r["promotion"],"BLOCKED")
  self.assertGreater(r["inputs"]["hz_surfaces"][0]["rows"],0)
  self.assertGreater(r["inputs"]["hz_surfaces"][1]["rows"],0)
  self.assertGreaterEqual(r["omega_r_sensitivity"]["max_relative_H_delta"],0.0)
  self.assertGreaterEqual(r["distance_integration"]["max_finest_simpson_vs_trapezoid_relative"],0.0)
  self.assertEqual(r["hz_overlap"]["shared_redshift_count"],28)
  self.assertEqual(r["hz_overlap"]["extra_row_count"],5)
  self.assertTrue(r["hz_overlap"]["extra_all_bao_labeled"])
  self.assertEqual(r["hz_overlap"]["pure_cc_projection_rows"],28)
  self.assertTrue(r["hz_overlap"]["pure_cc_projection_matches_independent_28_exactly"])
  self.assertEqual(
   r["axis_status"]["hz_dataset"],
   "EVIDENCE_SUPPORTS_PURE_CC28_FREEZE_BY_PREEXISTING_NO_DOUBLE_COUNT_POLICY",
  )
 def test_growth_remains_blocked(self):
  self.assertEqual(build()["axis_status"]["growth_mode"],"TOKEN_VAZIO_UNTIL_WS06")

if __name__=="__main__":unittest.main()
