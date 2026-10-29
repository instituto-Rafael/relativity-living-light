"""Offline geometric invariants and cultural boundary tests."""
import unittest
from scripts.rll_archaeoastronomy_clock_v1 import azimuth,calibration
class TestClock(unittest.TestCase):
 def test_symmetry(self):
  self.assertAlmostEqual(azimuth(0,0),90)
  self.assertAlmostEqual(azimuth(0,23.44)+azimuth(0,-23.44),180)
  self.assertAlmostEqual(azimuth(51.178869,0),90)
 def test_sites(self):
  r=calibration()
  self.assertFalse(r["claim_allowed"])
  self.assertFalse(r["sky_reconstruction"])
  self.assertEqual(len(r["sites"]),6)
  self.assertAlmostEqual(r["sites"][2]["events"]["north_solstice"]["sunrise_deg"],50.614,places=3)
  self.assertAlmostEqual(r["sites"][3]["events"]["south_solstice"]["sunrise_deg"],116.669,places=3)
  self.assertTrue(all(x["source"].startswith("https://") for x in r["sites"]))
if __name__=="__main__":unittest.main()
