from fractions import Fraction
import unittest

from tools.rll_median_multicarrier_theorem_lab_v1 import (
    area_ratio,
    centroid,
    cyclic_area_factor,
    cyclic_side_division,
    digits_in_base,
    lcm_many,
    medial_closed_form,
    medial_iterate,
    point,
    product_carrier_state,
    residue_signature,
    signed_double_area,
    stroboscopic_medial_relation,
    theorem_registry,
    value_from_digits,
)


class TestMedianMulticarrierTheoremLabV1(unittest.TestCase):
    def setUp(self):
        self.t = (point(0, 0), point(6, 0), point(2, 4))

    def test_medial_closed_form_matches_iteration(self):
        for k in range(8):
            self.assertEqual(medial_iterate(self.t, k), medial_closed_form(self.t, k))

    def test_centroid_is_invariant(self):
        g = centroid(self.t)
        for k in range(10):
            self.assertEqual(centroid(medial_closed_form(self.t, k)), g)

    def test_area_contracts_by_four_each_generation(self):
        for k in range(8):
            self.assertEqual(area_ratio(self.t, medial_closed_form(self.t, k)), Fraction(1, 4**k))

    def test_signed_vertex_factor_alternates(self):
        g = centroid(self.t)
        for k in range(7):
            tk = medial_closed_form(self.t, k)
            q = Fraction((-1) ** k, 2**k)
            self.assertEqual(tk[0][0] - g[0], q * (self.t[0][0] - g[0]))
            self.assertEqual(tk[0][1] - g[1], q * (self.t[0][1] - g[1]))

    def test_cyclic_side_division_preserves_centroid(self):
        for u in (Fraction(1, 2), Fraction(1, 3), Fraction(1, 4), Fraction(2, 3)):
            out = cyclic_side_division(self.t, u)
            self.assertEqual(centroid(out), centroid(self.t))
            self.assertEqual(
                abs(signed_double_area(out)) / abs(signed_double_area(self.t)),
                cyclic_area_factor(u),
            )

    def test_known_cyclic_area_factors(self):
        expected = {
            Fraction(1, 2): Fraction(1, 4),
            Fraction(1, 3): Fraction(1, 3),
            Fraction(1, 4): Fraction(7, 16),
            Fraction(2, 3): Fraction(1, 3),
        }
        for u, q in expected.items():
            self.assertEqual(cyclic_area_factor(u), q)

    def test_modular_carrier_period(self):
        mods = (3, 7, 14, 10, 30, 5, 50, 70)
        self.assertEqual(lcm_many(mods), 1050)
        for k in (0, 1, 42, 777, 999):
            self.assertEqual(residue_signature(k, mods), residue_signature(k + 1050, mods))

    def test_stroboscopic_relation_1050(self):
        rel = stroboscopic_medial_relation(37, (3, 7, 14, 10, 30, 5, 50, 70))
        self.assertTrue(rel["same_residue_signature"])
        self.assertTrue(rel["orientation_parity_same"])
        self.assertEqual(rel["signed_vertex_factor"], Fraction(1, 2**1050))
        self.assertEqual(rel["area_factor"], Fraction(1, 4**1050))

    def test_base_representation_preserves_value(self):
        for n in (0, 7, 21, 42, 777, 999):
            for b in (2, 3, 7, 10, 13):
                digs = digits_in_base(n, b)
                self.assertEqual(value_from_digits(digs, b), n)

    def test_product_carrier_keeps_domains_typed(self):
        state = product_carrier_state(self.t, 21, (3, 7, 11, 13), (7, 10))
        self.assertEqual(state.residue_signature, (0, 0, 10, 8))
        self.assertEqual(state.graph_signature[0], "BOUNDARY_C3")
        self.assertIn("NONEMPTY", state.set_signature)

    def test_registry_does_not_promote_novelty(self):
        reg = theorem_registry()
        self.assertTrue(all(item["claim_allowed"] is False for item in reg))
        states = {item["id"]: item["state"] for item in reg}
        self.assertEqual(states["T1"], "KNOWN_CLASSICAL")
        self.assertEqual(states["T4"], "CANDIDATE_NEW_COMPOSITION")


if __name__ == "__main__":
    unittest.main()
