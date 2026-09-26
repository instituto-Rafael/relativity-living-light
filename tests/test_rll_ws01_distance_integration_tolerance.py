import unittest
from tools.rll_ws01_distance_integration_tolerance import build, load

class WS01DistanceToleranceTests(unittest.TestCase):
 def test_contract_is_fail_closed_and_preregistered(self):
  c=load()
  self.assertEqual(c["state"],"PREREGISTERED_BEFORE_SUCCESSOR_EXECUTION")
  self.assertFalse(c["claim_allowed"])
  self.assertEqual(c["tolerance"]["rtol"],1e-6)
  self.assertEqual(c["tolerance"]["atol_mpc"],0.001)
 def test_execution_is_all_or_nothing(self):
  r=build()
  self.assertFalse(r["claim_allowed"])
  self.assertEqual(r["row_count"],33)
  if r["failures"]:
   self.assertEqual(r["state"],"FAIL_PREREGISTERED_DISTANCE_TOLERANCE")
  else:
   self.assertEqual(r["state"],"PASS_PREREGISTERED_DISTANCE_TOLERANCE")

if __name__=="__main__":unittest.main()
