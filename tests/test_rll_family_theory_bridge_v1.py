from __future__ import annotations

import math
import unittest

from tools import rll_family_theory_bridge_v1 as bridge


class RLLFamilyTheoryBridgeV1Tests(unittest.TestCase):
    def test_set_carriers_keep_zero_class_distinct_from_empty_set(self) -> None:
        carriers = bridge.set_carriers()
        self.assertTrue(carriers["prime_atoms"] <= carriers["integer_atoms"])
        self.assertEqual(len(frozenset()), 0)
        z7 = bridge.residue_class_window(7, 0, 3)
        self.assertEqual(z7, (-21, -14, -7, 0, 7, 14, 21))
        self.assertNotEqual(set(z7), set())

    def test_set_relations_and_equivalence_partition(self) -> None:
        rel = bridge.set_relation({3, 7}, {2, 3, 7})
        self.assertEqual(rel["intersection"], [3, 7])
        self.assertTrue(rel["left_subset_right"])
        self.assertEqual(rel["cartesian_product_cardinality"], 6)
        part = bridge.equivalence_partition(range(7), 3)
        self.assertEqual(part[0], (0, 3, 6))
        self.assertEqual(part[1], (1, 4))
        self.assertEqual(part[2], (2, 5))

    def test_prime_factorization_and_repunit_family(self) -> None:
        self.assertTrue(bridge.is_prime(7))
        self.assertTrue(bridge.is_prime(11))
        self.assertTrue(bridge.is_prime(13))
        self.assertFalse(bridge.is_prime(21))
        self.assertEqual(bridge.prime_factors(18), (2, 3, 3))
        self.assertEqual(bridge.prime_factors(21), (3, 7))
        self.assertEqual(bridge.prime_factors(42), (2, 3, 7))
        self.assertEqual(bridge.prime_factors(1001), (7, 11, 13))
        self.assertEqual(bridge.repunit(6), 111111)
        self.assertEqual(bridge.prime_factors(bridge.repunit(6)), (3, 7, 11, 13, 37))

    def test_base10_multiplicative_orders_explain_cycle_lengths(self) -> None:
        orders = bridge.prime_decimal_orders()
        self.assertIsNone(orders[2])
        self.assertEqual(orders[3], 1)
        self.assertIsNone(orders[5])
        self.assertEqual(orders[7], 6)
        self.assertEqual(orders[11], 2)
        self.assertEqual(orders[13], 6)
        self.assertEqual(orders[37], 3)
        self.assertEqual(tuple(p for p in bridge.PRIME_ATOMS if bridge.multiplicative_order(10, p) == p - 1), (7,))

    def test_base_representation_preserves_value_vs_word_boundary(self) -> None:
        self.assertEqual(bridge.int_to_base(10, 10), "10")
        self.assertEqual(bridge.int_to_base(7, 7), "10")
        self.assertEqual(bridge.census.positional_value_10(7), 7)
        self.assertEqual(bridge.int_to_base(42, 2), "101010")

    def test_crt_coordinates_reconstruct_21_and_42_carriers(self) -> None:
        for n in range(21):
            coords = bridge.crt_coordinates(n, bridge.CRT_21)
            self.assertEqual(bridge.crt_reconstruct(coords, bridge.CRT_21), n)
        for n in range(42):
            coords = bridge.crt_coordinates(n, bridge.CRT_42)
            self.assertEqual(bridge.crt_reconstruct(coords, bridge.CRT_42), n)

    def test_repdigit_functional_graphs_have_expected_cycles(self) -> None:
        g3 = bridge.functional_graph(7, 3)
        self.assertEqual(bridge.functional_cycles(g3), ((0, 1, 2),))
        g7 = bridge.functional_graph(3, 7)
        self.assertEqual(set(bridge.functional_cycles(g7)), {(0, 3, 5, 4, 1, 6), (2,)})

    def test_cayley_z7_is_one_cycle_and_factor_graph_is_bipartite(self) -> None:
        edges = bridge.cayley_cycle(7, 1)
        self.assertEqual(len(edges), 7)
        self.assertEqual(edges[0], (0, 1))
        self.assertEqual(edges[-1], (6, 0))
        fg = bridge.factor_incidence_graph((18, 21, 42, 1001))
        self.assertIn(("n:21", "p:3"), fg["edges"])
        self.assertIn(("n:21", "p:7"), fg["edges"])
        self.assertIn("p:11", fg["prime_nodes"])
        self.assertIn("p:13", fg["prime_nodes"])
        self.assertGreaterEqual(fg["invariants"]["components"], 1)

    def test_graph_flow_zero_balance_is_conservation_not_missingness(self) -> None:
        balance = bridge.graph_flow_balance((
            ("source", "junction", 2.0),
            ("junction", "a", 0.75),
            ("junction", "b", 1.25),
        ))
        self.assertAlmostEqual(balance["junction"], 0.0)
        self.assertAlmostEqual(balance["source"], -2.0)
        self.assertAlmostEqual(balance["a"] + balance["b"], 2.0)
        self.assertIn("junction", balance)

    def test_steady_continuity_is_exact_under_declared_fixture(self) -> None:
        residual = bridge.continuity_residual(1.0, 2.0, 3.0, 1.0, 1.0, 6.0)
        self.assertAlmostEqual(residual, 0.0)
        self.assertAlmostEqual(bridge.steady_mass_flux(1.0, 2.0, 3.0), 6.0)

    def test_bernoulli_and_ideal_venturi_helpers_are_consistent(self) -> None:
        rho = 1000.0
        a1 = 0.02
        a2 = 0.01
        dp = 1500.0
        q = bridge.venturi_ideal_equal_height_flow(a1, a2, rho, dp)
        v1 = q / a1
        v2 = q / a2
        self.assertAlmostEqual(a1 * v1, a2 * v2)
        self.assertAlmostEqual(0.5 * rho * (v2 * v2 - v1 * v1), dp)
        b1 = bridge.bernoulli_energy_density(100000.0, rho, v1)
        b2 = bridge.bernoulli_energy_density(100000.0 - dp, rho, v2)
        self.assertAlmostEqual(b1, b2)

    def test_reynolds_number_is_computable_but_regime_is_not_silently_claimed(self) -> None:
        re = bridge.reynolds_number(1000.0, 1.0, 0.02, 0.001)
        self.assertAlmostEqual(re, 20000.0)

    def test_fluid_physical_binding_is_fail_closed(self) -> None:
        missing = bridge.fluid_binding_gate({"geometry": "tube"})
        self.assertEqual(missing["state"], bridge.PHYSICAL_FLUID_BINDING_STATE)
        self.assertFalse(missing["claim_allowed"])
        complete = {key: f"declared:{key}" for key in missing["required"]}
        ready = bridge.fluid_binding_gate(complete)
        self.assertEqual(ready["state"], "READY_FOR_PHYSICAL_TEST")
        self.assertFalse(ready["claim_allowed"])
        self.assertEqual(ready["missing"], ())

    def test_family_manifest_covers_all_declared_domains_and_remains_fail_closed(self) -> None:
        receipt = bridge.family_manifest()
        domains = {f["domain"] for f in receipt["families"]}
        for domain in (
            "set_theory", "number_theory", "prime_theory", "functional_graphs",
            "factor_graphs", "continuity", "bernoulli_venturi", "graph_flow",
            "physical_binding",
        ):
            self.assertIn(domain, domains)
        self.assertFalse(receipt["claim_allowed"])
        self.assertEqual(receipt["physical_boundaries"]["fluid_binding"], "TOKEN_VAZIO_FLUID_BINDING")
        self.assertEqual(receipt["physical_boundaries"]["cosmology_binding"], "TOKEN_VAZIO_COSMOLOGY_BINDING")
        self.assertTrue(receipt["fluids"]["junction_zero_is_conservation_not_missing"])


if __name__ == "__main__":
    unittest.main()
