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


    def test_integer_and_zero_fraction_notation(self):
        self.assertEqual(m.fraction_expansion(1,1,10)["notation"],"1")
        self.assertEqual(m.fraction_expansion(0,7,10)["notation"],"0")
        self.assertEqual(m.fraction_expansion(1,12,10)["notation"],"0.08(3)")

    def test_crt_construction_and_incompatibility(self):
        self.assertEqual(m.crt_pairwise(((3,7),(4,10))),(24,70))
        self.assertEqual(m.crt_pairwise(((3,7),(4,50))),(304,350))
        self.assertEqual(m.crt_general(((3,14),(17,35))),(17,70))
        with self.assertRaises(ValueError):
            m.crt_general(((3,14),(16,35)))
        with self.assertRaises(ValueError):
            m.crt_pairwise(((3,14),(17,35)))

    def test_factorization_totient_dynamic(self):
        self.assertEqual(m.factorization(350),{2:1,5:2,7:1})
        self.assertEqual(m.factorization(210),{2:1,3:1,5:1,7:1})
        self.assertEqual(m.totient(210),48)
        self.assertEqual(m.totient(350),120)
        self.assertEqual(m.factorization_string(350),"2 * 5^2 * 7")

    def test_certified_eighth_bounds(self):
        from fractions import Fraction
        for base in (2,3):
            bounds=m.certified_step_bounds(base,Decimal("7"))
            self.assertEqual(len(bounds),9)
            self.assertEqual(Fraction(bounds[0]["lower_exact"]),7)
            self.assertEqual(Fraction(bounds[8]["lower_exact"]),7*base)
            for j,row in enumerate(bounds):
                low=Fraction(row["lower_exact"])/7
                high=Fraction(row["upper_exact"])/7
                self.assertLessEqual(low**8,base**j)
                self.assertGreaterEqual(high**8,base**j)
                self.assertLessEqual(low,high)

    def test_claim_boundary_with_extended_validation(self):
        report=m.compute()
        self.assertIs(report["claim_allowed"],False)
        self.assertEqual(report["crt_verified"]["pair_7_10"],(24,70))
        self.assertTrue(report["scale_eighth_root_2"]["certified_step_bounds"][8]["exact"])


if __name__=="__main__":
    unittest.main()
