"""Tests for UTM-185 explicit void-mask attention."""
from __future__ import annotations

import importlib.util
import math
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).parent.parent.resolve()
MODULE_PATH = ROOT / "tools" / "utm185_void_mask_attention.py"
SPEC = importlib.util.spec_from_file_location("utm185_void_mask_attention", MODULE_PATH)
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mod
SPEC.loader.exec_module(mod)

masked_hyperbolic_attention = mod.masked_hyperbolic_attention
poincare_distance = mod.poincare_distance


class UTM185Tests(unittest.TestCase):
    def test_origin_is_valid_and_finite(self):
        q = (0.3, 0.4)
        got = poincare_distance((0.0, 0.0), q)
        expected = 2.0 * math.atanh(0.5)
        self.assertAlmostEqual(got, expected, places=12)
        self.assertTrue(math.isfinite(got))

    def test_masked_position_gets_exact_zero_weight(self):
        result = masked_hyperbolic_attention(
            query=(0.0, 0.0),
            keys=((0.1, 0.0), (0.2, 0.0)),
            values=((1.0,), (9999.0,)),
            valid_mask=(True, False),
        )
        self.assertEqual(result.weights, (1.0, 0.0))
        self.assertEqual(result.context, (1.0,))

    def test_zero_key_is_not_missing(self):
        result = masked_hyperbolic_attention(
            query=(0.0, 0.0),
            keys=((0.0, 0.0), (0.8, 0.0)),
            values=((7.0,), (11.0,)),
            valid_mask=(True, True),
        )
        self.assertGreater(result.weights[0], result.weights[1])
        self.assertEqual(result.state, "VALID_MASK_APPLIED")

    def test_all_masked_fails_closed(self):
        result = masked_hyperbolic_attention(
            query=(0.0, 0.0),
            keys=((0.1, 0.0), (0.2, 0.0)),
            values=((1.0, 2.0), (3.0, 4.0)),
            valid_mask=(False, False),
        )
        self.assertEqual(result.weights, (0.0, 0.0))
        self.assertEqual(result.context, (0.0, 0.0))
        self.assertEqual(result.state, "TOKEN_VAZIO_ALL_MASKED")

    def test_weights_sum_to_one_over_valid_positions(self):
        result = masked_hyperbolic_attention(
            query=(0.1, 0.1),
            keys=((0.2, 0.1), (0.1, 0.2), (0.0, 0.0)),
            values=((1.0,), (2.0,), (3.0,)),
            valid_mask=(True, False, True),
        )
        self.assertAlmostEqual(sum(result.weights), 1.0, places=15)
        self.assertEqual(result.weights[1], 0.0)

    def test_rejects_boundary_or_outside_points(self):
        with self.assertRaises(ValueError):
            poincare_distance((1.0, 0.0), (0.0, 0.0))

    def test_rejects_shape_mismatch(self):
        with self.assertRaises(ValueError):
            masked_hyperbolic_attention(
                query=(0.0, 0.0),
                keys=((0.1, 0.0),),
                values=((1.0,), (2.0,)),
                valid_mask=(True,),
            )


if __name__ == "__main__":
    unittest.main()
