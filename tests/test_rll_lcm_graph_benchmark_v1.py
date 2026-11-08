"""Adversarial exact MMC properties; no astrophysics claim."""
import math
import random
import unittest
from tools.rll_lcm_graph_benchmark_v1 import (
    gcd_euclid, gcd_complement, gcd_repeated_complement_bounded,
    lcm_euclid, lcm_complement,
    lcm_graph, run_cases, GRAPH_STEP_CAP,
)

class LcmGraphSuite(unittest.TestCase):
    def test_examples_70_350(self):
        self.assertEqual(lcm_euclid((7,10,14)),70)
        self.assertEqual(lcm_euclid((7,35,50,70)),350)
        self.assertEqual(lcm_graph((7,10,14)),(70,70))
        self.assertEqual(lcm_graph((7,35,50,70)),(350,350))
    def test_zero_is_defined_not_missing(self):
        self.assertEqual(lcm_graph((0,7,10)),(0,0))
        self.assertEqual(lcm_euclid((0,7,10)),0)
    def test_empty_tuple_rejected(self):
        for f in (lcm_euclid,lcm_complement,lcm_graph):
            with self.assertRaises(ValueError): f(())
    def test_sign_symmetry(self):
        for tup in ((-7,14),(-35,-50,70),(7,0,-13)):
            self.assertEqual(lcm_euclid(tup),math.lcm(*tup))
            self.assertEqual(lcm_complement(tup),math.lcm(*tup))
    def test_lcm_is_positive_for_nonzero(self):
        for values in ((7,10,14), (13,17), (1009,1013)):
            self.assertGreater(lcm_euclid(values),0)
    def test_coprime_prime_cases(self):
        self.assertEqual(lcm_euclid((13,17)),221)
        self.assertEqual(lcm_complement((1009,1013)),1009*1013)
    def test_graph_is_cycle_length(self):
        for tup in ((2,3),(5,6),(7,10,14),(7,35,50,70),(8,12,16)):
            actual,k=lcm_graph(tup)
            self.assertEqual(actual,math.lcm(*tup))
            self.assertEqual(k,actual)
    def test_graph_is_bounded_not_claimed(self):
        self.assertEqual(lcm_graph((1009,1013)),(None,GRAPH_STEP_CAP))
    def test_naive_repeated_complement_pathology(self):
        # A mathematically valid alternate remainder has disastrous steps.
        self.assertEqual(gcd_repeated_complement_bounded(1_000_004,1_000_003),
                         (None,5000))
        self.assertEqual(gcd_complement(1_000_003,1_000_004),1)
    def test_complement_gcd_identity(self):
        for a in range(-43,44):
            for b in range(-43,44):
                self.assertEqual(gcd_euclid(a,b),gcd_complement(a,b))
    def test_random_same_answers(self):
        rng=random.Random(20261108)
        for _ in range(200):
            tup=tuple(rng.randint(1,500) for _ in range(rng.randint(2,5)))
            self.assertEqual(math.lcm(*tup),lcm_euclid(tup))
            self.assertEqual(math.lcm(*tup),lcm_complement(tup))
    def test_case_corpus_exact(self):
        rows=run_cases()
        self.assertEqual(len(rows),72)
        self.assertTrue(all(r['euclid']==r['expected_lcm'] for r in rows))
        self.assertTrue(all(r['complement']==r['expected_lcm'] for r in rows))
        self.assertTrue(all(r['graph']==r['expected_lcm'] for r in rows if r['graph_status']=='PASS_SCOPED'))
    def test_multiply_not_formal_novelty(self):
        self.assertEqual(7*70,(7+3)*70-3*70)
        self.assertEqual(7*70,490)

if __name__=='__main__':unittest.main()
