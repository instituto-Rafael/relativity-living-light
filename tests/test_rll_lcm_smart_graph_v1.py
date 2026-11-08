"""RLL event-jump and factor-lattice adversarial exact checks; no physics."""
import math
import random
import unittest
from tools.rll_lcm_graph_benchmark_v1 import gcd_euclid
from tools.rll_lcm_smart_graph_v1 import (
    jump_graph, prime_trial_factors, prime_lattice_trial, SmallestPrimeFactorGraph
)


class SmartLcmGraph(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spf = SmallestPrimeFactorGraph(1_000_100)

    def test_user_examples(self):
        self.assertEqual(jump_graph((7,10,14)),70)
        self.assertEqual(jump_graph((7,35,50,70)),350)
        for v in ((7,10,14),(7,35,50,70),(7,10,14,35,50,70)):
            self.assertEqual(prime_lattice_trial(v), math.lcm(*v))
            self.assertEqual(self.spf.lcm(v), math.lcm(*v))

    def test_edges_prove_cycle(self):
        total,edges=jump_graph((7,10,14),trace=True)
        self.assertEqual(total,70)
        self.assertEqual([e[-1] for e in edges],[7,70,70])
        for before,n,g,k,after in edges:
            self.assertEqual(g,math.gcd(before,n))
            self.assertEqual(after,before*k)
            self.assertEqual(k,n//g)
            self.assertEqual(after%n,0)

    def test_zero_not_token_vazio(self):
        for v in ((0,),(0,7,10),(7,0,-14)):
            self.assertEqual(jump_graph(v),0)
            self.assertEqual(prime_lattice_trial(v),0)
            self.assertEqual(self.spf.lcm(v),0)

    def test_sign_and_unit(self):
        for v in ((-1,),(1,),(1,1,1),(-7,14),(-35,-50,70)):
            self.assertEqual(jump_graph(v),math.lcm(*v))
            self.assertEqual(prime_lattice_trial(v),math.lcm(*v))
            self.assertEqual(self.spf.lcm(v),math.lcm(*v))

    def test_input_types(self):
        for v in ((),(7,1.5),(True,7),("7",10)):
            for fn in (jump_graph,prime_lattice_trial,self.spf.lcm):
                with self.assertRaises((TypeError,ValueError)):fn(v)

    def test_sieve_no_implicit_fallback(self):
        with self.assertRaises(ValueError):
            self.spf.lcm((1_000_101,))
        with self.assertRaises(ValueError):
            self.spf.factors(0)

    def test_factorization(self):
        for n in (1,2,3,7,13,49,70,100,1024,99991,1000003):
            f=prime_trial_factors(n)
            self.assertEqual(f,self.spf.factors(n))
            self.assertEqual(math.prod(p**e for p,e in f.items()),n)

    def test_primes_and_powers(self):
        for v in ((13,17),(1009,1013),(1000003,1000033),
                  (2**16,3**10,5**3),(7**5,7**3),(2**14,2**12,2**9)):
            expected=math.lcm(*v)
            self.assertEqual(jump_graph(v),expected)
            self.assertEqual(prime_lattice_trial(v),expected)
            if max(abs(n) for n in v)<=self.spf.limit:
                self.assertEqual(self.spf.lcm(v),expected)

    def test_random_seeded(self):
        rng=random.Random(20261108)
        for _ in range(350):
            v=tuple(rng.randint(-100000,100000) for j in range(rng.randint(1,6)))
            expected=math.lcm(*v)
            self.assertEqual(jump_graph(v),expected)
            self.assertEqual(prime_lattice_trial(v),expected)
            self.assertEqual(self.spf.lcm(v),expected)

    def test_sieve_payload(self):
        self.assertEqual(self.spf.payload_bytes,4*(1_000_100+1))

    def test_small_exhaustive(self):
        g=SmallestPrimeFactorGraph(60)
        for a in range(61):
            for b in range(61):
                expected=math.lcm(a,b)
                self.assertEqual(jump_graph((a,b)),expected)
                self.assertEqual(prime_lattice_trial((a,b)),expected)
                self.assertEqual(g.lcm((a,b)),expected)

    def test_large_semiprime_exact(self):
        v=(1000000007,1000000009)
        self.assertEqual(jump_graph(v),math.lcm(*v))
        with self.assertRaises(ValueError): self.spf.lcm(v)

    def test_python_gcd_backend_equivalence(self):
        for v in ((7,10,14),(7,35,50,70),(1009,1013),(0,7,-14)):
            self.assertEqual(jump_graph(v),jump_graph(v,gcd_fn=gcd_euclid))

    def test_not_independent_of_euclid(self):
        self.assertEqual(jump_graph((7,70),trace=True)[1][-1][2],7)


if __name__ == "__main__":
    unittest.main(verbosity=2)
