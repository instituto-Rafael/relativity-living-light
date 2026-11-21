"""RAFAELIA V2 multibase, coprime, octic-scale tests."""
import importlib.util
from pathlib import Path
from decimal import Decimal
import unittest

P=Path(__file__).resolve().parents[1]/"tools/math/multibase_octice_roots_v2.py"
spec=importlib.util.spec_from_file_location("rll_multibase_v2",P)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class MultibaseV2(unittest.TestCase):
    def test_coprime_pairs_lcm(self):
        r=m.compute()
        self.assertEqual(r["common_lcm"],350)
        self.assertEqual(r["global_phi"],120)
        self.assertEqual({(x["a"],x["b"]) for x in r["coprime_radix_pairs"]},{(7,10),(7,50)})
        self.assertEqual(m.gcd(14,35),7)
        self.assertEqual(m.gcd(35,50),5)

    def test_350_same_value_not_same_symbols(self):
        r=m.compute()["integer_representation_table"]["350"]
        self.assertEqual(r["50"]["literal"],"70")
        self.assertEqual(r["70"]["literal"],"50")
        self.assertEqual(r["7"]["literal"],"1010")
        self.assertTrue(all(x["back_decoded"]==350 for x in r.values()))

    def test_digit_range_enforced(self):
        with self.assertRaises(ValueError):
            m.numeric_value((7,0),7)
        with self.assertRaises(ValueError):
            m.digits(7,1)
        with self.assertRaises(ValueError):
            m.numeric_value((1,70),70)

    def test_fraction_periods(self):
        f=m.compute()["fraction_one_seventh"]
        self.assertEqual(f["7"]["notation"],"0.1")
        self.assertEqual(f["14"]["notation"],"0.2")
        self.assertEqual(f["35"]["notation"],"0.5")
        self.assertEqual(f["10"]["period"],6)
        self.assertFalse(f["50"]["terminating"])
        self.assertTrue(f["70"]["terminating"])
        g=m.compute()["fraction_one_over_350"]
        self.assertEqual(g["70"]["notation"],"0.0[14]")
        self.assertFalse(g["35"]["terminating"])

    def test_eighth_root_eight_steps(self):
        for n in (2,3):
            r=m.scale_eighth(n,Decimal("7"))
            v=list(map(Decimal,r["steps_side_approx"]))
            self.assertEqual(len(v),9)
            self.assertEqual(v[0],Decimal(7))
            self.assertEqual(v[8],Decimal(7*n))
            self.assertEqual(r["area_after_8_over_initial_exact"],n*n)
            self.assertEqual(r["volume_after_8_over_initial_exact"],n**3)

    def test_octagonal_coprime_spiral_vs_split_step(self):
        x=m.compute()["octagonal_coprime_spiral"]
        self.assertEqual(x["angle_indices_0_through_8"],[0,3,6,1,4,7,2,5,0])
        self.assertEqual(x["unique_directions_first_8"],8)
        self.assertEqual(x["angular_step_2_negative_unique_directions"],4)
        self.assertTrue(x["radial_not_closed_for_multipliers_2_or_3"])

    def test_empty_is_not_zero(self):
        self.assertEqual(m.digits(0,7),(0,))
        with self.assertRaises(ValueError):
            m.numeric_value((),7)
        self.assertFalse(m.compute()["claim_allowed"])

if __name__=="__main__":
    unittest.main()
