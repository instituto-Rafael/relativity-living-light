from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "tools" / "blake3_rll_falsifiability.py"


def load_target():
    spec = importlib.util.spec_from_file_location("blake3_rll_falsifiability", TARGET)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Blake3RllFalsifiabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load_target()
        cls.report = cls.mod.build_report()

    def test_blake3_structural_counts_are_typed_not_conflated(self):
        b3 = self.report["blake3_observed_structure"]
        self.assertEqual(b3["tree_arity"], 2)
        self.assertEqual(b3["user_facing_modes"], 3)
        self.assertEqual(b3["g_parallel_width"], 4)
        self.assertEqual(b3["rounds"], 7)
        self.assertEqual(b3["internal_flags"], 7)
        self.assertEqual(b3["g_calls_per_round"], 8)
        self.assertEqual(b3["cv_words"], 8)
        self.assertEqual(b3["rotation_constants"], [16, 12, 8, 7])
        self.assertEqual(b3["rotation_sum"], 43)
        self.assertEqual(b3["g_calls_across_7_rounds"], 56)

    def test_counts_five_and_six_remain_token_vazio(self):
        signatures = self.report["falsifiability"]["count_signatures_3_to_8"]
        self.assertEqual(signatures["3"]["state"], "PASS_CANONICAL")
        self.assertEqual(signatures["4"]["state"], "PASS_CANONICAL")
        self.assertEqual(signatures["5"]["state"], "TOKEN_VAZIO_NO_CANONICAL_BINDING")
        self.assertEqual(signatures["6"]["state"], "TOKEN_VAZIO_NO_CANONICAL_BINDING")
        self.assertEqual(signatures["7"]["state"], "PASS_CANONICAL")
        self.assertEqual(signatures["8"]["state"], "PASS_CANONICAL")

    def test_depth_three_through_eight_is_input_dependent_not_tree_arity(self):
        branch = self.report["falsifiability"]
        self.assertEqual(branch["tree_branching_factor_3_to_8"]["observed_tree_arity"], 2)
        examples = branch["input_dependent_depth_3_to_8"]["examples"]
        self.assertEqual([row["depth"] for row in examples], [3, 4, 5, 6, 7, 8])
        self.assertEqual([row["chunks"] for row in examples], [8, 16, 32, 64, 128, 256])
        self.assertEqual(
            [row["bytes"] for row in examples],
            [8192, 16384, 32768, 65536, 131072, 262144],
        )

    def test_current_rll_float_recurrence_falsifies_period_42(self):
        result = self.report["falsifiability"]["rll_real_recurrence_period_42"]
        self.assertEqual(result["state"], "FAIL_FALSIFIED")
        self.assertFalse(result["cycle_42_verified"])
        self.assertEqual(result["step_42_mod1"], 0.106130777368)
        self.assertEqual(result["step_43_mod1"], 0.113410671216)

    def test_bitomega_blake3_link_fails_closed_without_generating_evidence(self):
        result = self.report["falsifiability"]["bitomega_period_42_attributed_to_blake3_rmr"]
        self.assertEqual(result["state"], "TOKEN_VAZIO_PROVENANCE_CONFLICT")
        self.assertFalse(result["claim_allowed"])

    def test_global_claim_gate_stays_closed(self):
        self.assertFalse(self.report["claim_allowed"])


if __name__ == "__main__":
    unittest.main()
