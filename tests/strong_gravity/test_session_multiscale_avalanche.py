import importlib.util, math, sys
from pathlib import Path
import unittest
MODULE_PATH = Path(__file__).parents[2] / "data/pipelines/strong_gravity/session_multiscale_avalanche.py"
SPEC = importlib.util.spec_from_file_location("session_multiscale_avalanche", MODULE_PATH)
m = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = m
assert SPEC.loader
SPEC.loader.exec_module(m)
class T(unittest.TestCase):
 def test_pair(self): self.assertEqual(m.SECOND_HARMONIC_HZ,2*m.FUNDAMENTAL_HZ)
 def test_photon(self): self.assertLess(m.photon_energy_ev(m.SECOND_HARMONIC_HZ),1e-8)
 def test_thz(self):
  for e in m.LIGHT_MATTER_MODES_MEV: self.assertGreater(m.mode_frequency_hz(e),1e11)
 def test_spiral(self):
  r,p=m.ordered_infall_step(1,0); self.assertLess(r,1); self.assertAlmostEqual(p,math.pi/3)
 def test_conserve(self):
  x=m.damping_partition(10,2,.1,transport_fraction=.2,radiation_fraction=.15)
  self.assertAlmostEqual(x.conservation_error_j_m3,0,places=12); self.assertGreater(x.heat_j_m3,0)
 def test_order_and_heat(self):
  self.assertLess(m.ordered_infall_step(1,0)[0],1)
  self.assertGreater(m.damping_partition(10,2,.1,transport_fraction=0,radiation_fraction=0).heat_j_m3,0)
 def test_below(self): self.assertEqual(m.avalanche_multiplier(40,50,100,.01),1)
 def test_bound(self): self.assertLessEqual(m.avalanche_multiplier(60,50,1e9,1,cap=1e6),1e6*(1+1e-12))
 def test_diamond(self): self.assertFalse(m.carbon_phase_admissible("diamond_sp3","fully_ionized")[0])
 def test_recond(self):
  self.assertFalse(m.carbon_phase_admissible("recondensing_carbon","heating")[0])
  self.assertTrue(m.carbon_phase_admissible("recondensing_carbon","quench")[0])
 def test_co(self): self.assertFalse(m.carbon_phase_admissible("compact_co_crystal","cooling")[0])
 def test_grid(self):
  a=m.finite_permutation_grid(); self.assertEqual(a,m.finite_permutation_grid()); self.assertEqual(len(a),288)
 def test_blocked(self):
  x=m.build_report(); self.assertGreater(x.candidates_blocked,0); self.assertGreater(x.candidates_admissible,0)
 def test_claim(self): self.assertFalse(m.build_report().claim_allowed); self.assertFalse(m.baseline()["boundaries"]["claim_allowed"])
if __name__=="__main__": unittest.main()
