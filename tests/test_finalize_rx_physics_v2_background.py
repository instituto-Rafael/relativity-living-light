import unittest
from tools.finalize_rx_physics_v2_background import build

class FinalizeRxPhysicsV2BackgroundTests(unittest.TestCase):
 def test_finalizer_passes_only_bounded_background_scope(self):
  r=build()
  self.assertTrue(r["passed"])
  self.assertEqual(r["state"],"PASS_VERSIONED_CANONICAL_V2_BACKGROUND_CONTRACT")
  self.assertEqual(r["decision_packet_blocking_axes"],[])
  self.assertFalse(r["claim_allowed"])
  self.assertFalse(r["scientific_confirmation"])
  self.assertIn("TOKEN_VAZIO_RLL_PERTURBATION_CLOSURE_RELATIONS",r["downstream_tokens_preserved"])
  self.assertIn("OGB-FS8-001:BLOCKED_UNTIL_PERTURBATION_BACKEND",r["downstream_tokens_preserved"])
  self.assertNotEqual(r["active_contract_unchanged"],"RX-PHYSICS-CANONICAL-V2")

if __name__=="__main__":unittest.main()
