"""RAFAELIA V1 regression and negative controls (synthetic only)."""
import importlib.util
from pathlib import Path
import unittest

SCRIPT=Path(__file__).resolve().parents[1]/"tools/math/prime_geometry_v1.py"
spec=importlib.util.spec_from_file_location("rll_prime_geom_v1",SCRIPT)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class GeometryTests(unittest.TestCase):
    def test_m_and_totient(self):
        self.assertEqual(mod.GLOBAL_MODULUS,54600)
        self.assertEqual(len(mod.units(54600)),11520)
        self.assertEqual(len(mod.units(70)),24)
        self.assertEqual(len(mod.units(210)),48)
        self.assertEqual(len(mod.units(350)),120)

    def test_coprime_full_cycle_and_composite_split(self):
        self.assertEqual(len(mod.orbit_vertices(7,2)),7)
        self.assertEqual(len(mod.orbit_vertices(8,2)),4)
        self.assertEqual(len(mod.orbit_vertices(1400,7)),200)

    def test_negative_coprime_is_not_necessarily_prime(self):
        self.assertEqual(mod.math.gcd(121,54600),1)
        self.assertFalse(mod.is_prime_trial(121))
        self.assertNotEqual(mod.math.gcd(169,54600),1)

    def test_exceptional_primes_and_bad_inputs(self):
        self.assertEqual([p for p in (2,3,5,7,13) if mod.is_prime_trial(p)],[2,3,5,7,13])
        with self.assertRaises(ValueError):
            mod.orbit_vertices(7,0)
        with self.assertRaises(ValueError):
            mod.compute(999)

    def test_finite_full_protocol(self):
        r=mod.compute(10000)
        self.assertEqual(r["prime_filter"]["all_primes_count"],1229)
        self.assertEqual(r["projection"]["70"]["fiber_count_per_unit"],480)
        self.assertEqual(r["projection"]["1400"]["fiber_count_per_unit"],24)
        self.assertTrue(r["prime_filter"]["negative_control_121_is_coprime_and_composite"])
        self.assertFalse(r["claim_allowed"])
        self.assertEqual(r["cosmological_model_test"],"NOT_EXECUTED")

if __name__=="__main__":
    unittest.main()
