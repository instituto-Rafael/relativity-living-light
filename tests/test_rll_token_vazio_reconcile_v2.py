from __future__ import annotations

import unittest
from pathlib import Path

from tools.rll_token_vazio_reconcile import apply_rule_overrides, load_json, reconcile
from tools.rll_token_vazio_reconcile_v2 import (
    DEFAULT_INPUT,
    DEFAULT_OVERRIDES,
    DEFAULT_RULES,
    build_current_view,
    merge_input_delta,
)

ROOT = Path(__file__).resolve().parents[1]


def v1_view():
    base = load_json(ROOT / DEFAULT_RULES)
    v1 = apply_rule_overrides(base, load_json(ROOT / DEFAULT_OVERRIDES))
    return reconcile(ROOT, load_json(ROOT / DEFAULT_INPUT), v1, "2026-08-08T00:15:00Z")


def v2_view():
    return build_current_view(ROOT, generated_at="2026-08-08T04:30:00Z")


class TokenVazioReconciliationV2Tests(unittest.TestCase):
    def test_v1_historical_view_is_unchanged(self):
        receipt = v1_view()
        self.assertEqual(receipt["summary"]["input_tokens"], 30)
        self.assertEqual(receipt["summary"]["terminal_resolved"], 9)
        self.assertEqual(receipt["summary"]["reduced_generic"], 7)
        self.assertEqual(receipt["summary"]["open"], 14)
        self.assertIn("TOKEN_VAZIO_ACT_DR6_CMBONLY_MATERIALIZATION_REPRODUCTION", receipt["canonical_open_tokens"])
        self.assertIn("TOKEN_VAZIO_H0_RD_FULL_BOLTZMANN_REPRODUCTION", receipt["canonical_open_tokens"])
        self.assertIn("TOKEN_VAZIO_NOT_YET_CLASSIFIED_ALL_582_REFS", receipt["canonical_open_tokens"])

    def test_v2_adds_three_successors_without_hiding_open_work(self):
        receipt = v2_view()
        self.assertFalse(receipt["claim_allowed"])
        self.assertFalse(receipt["publication_ready"])
        self.assertEqual(receipt["summary"]["input_tokens"], 33)
        self.assertEqual(receipt["summary"]["terminal_resolved"], 10)
        self.assertEqual(receipt["summary"]["reduced_generic"], 9)
        self.assertEqual(receipt["summary"]["open"], 14)
        self.assertFalse(any(row["state"] == "OPEN_EVIDENCE_MISSING" for row in receipt["results"]))

    def test_act_materialization_resolves_only_to_posterior_successor(self):
        rows = {row["token"]: row for row in v2_view()["results"]}
        materialization = rows["TOKEN_VAZIO_ACT_DR6_CMBONLY_MATERIALIZATION_REPRODUCTION"]
        posterior = rows["TOKEN_VAZIO_ACT_DR6_LCDM_POSTERIOR_CHAIN_REPRODUCTION"]
        self.assertEqual(materialization["state"], "RESOLVED")
        self.assertTrue(materialization["evidence_verified"])
        self.assertEqual(posterior["state"], "OPEN_INTERNAL")
        self.assertIn("posterior", posterior["next_action"].lower())

    def test_h0_rd_is_reduced_not_falsely_resolved(self):
        rows = {row["token"]: row for row in v2_view()["results"]}
        crosscheck = rows["TOKEN_VAZIO_H0_RD_FULL_BOLTZMANN_REPRODUCTION"]
        integration = rows["TOKEN_VAZIO_H0_RD_FULL_BOLTZMANN_INFERENCE_INTEGRATION"]
        self.assertEqual(crosscheck["state"], "REDUCED")
        self.assertTrue(crosscheck["evidence_verified"])
        self.assertIn("0.596-0.599%", crosscheck["resolved_fact"])
        self.assertEqual(integration["state"], "OPEN_INTERNAL")
        self.assertIn("24", integration["next_action"])

    def test_582_label_is_reduced_to_current_35_ref_semantic_review(self):
        rows = {row["token"]: row for row in v2_view()["results"]}
        historical = rows["TOKEN_VAZIO_NOT_YET_CLASSIFIED_ALL_582_REFS"]
        successor = rows["TOKEN_VAZIO_DIVERGED_OR_DESCENDANT_REF_SEMANTIC_REVIEW"]
        self.assertEqual(historical["state"], "REDUCED")
        self.assertTrue(historical["evidence_verified"])
        self.assertIn("599", historical["resolved_fact"])
        self.assertIn("35", historical["resolved_fact"])
        self.assertEqual(successor["state"], "OPEN_INTERNAL")
        self.assertIn("35", successor["next_action"])

    def test_input_delta_rejects_duplicate_existing_token(self):
        base = load_json(ROOT / DEFAULT_INPUT)
        delta = {
            "schema": "rll.gap_closure_input_delta.v1",
            "claim_allowed": False,
            "tokens": [dict(base["tokens"][0])],
        }
        with self.assertRaisesRegex(ValueError, "duplicate input delta token"):
            merge_input_delta(base, delta)

    def test_v2_chain_metadata_is_explicit_and_ordered(self):
        receipt = v2_view()
        self.assertEqual(receipt["view"], "RLL_TOKEN_VAZIO_RECONCILIATION_V2_APPEND_ONLY")
        self.assertEqual([row["ordinal"] for row in receipt["override_chain"]], [1, 2])
        self.assertTrue(receipt["override_chain"][0]["path"].endswith("RLL_TOKEN_VAZIO_CLOSURE_OVERRIDES_20260807_V1.json"))
        self.assertTrue(receipt["override_chain"][1]["path"].endswith("RLL_TOKEN_VAZIO_CLOSURE_OVERRIDES_20260808_V2.json"))
        self.assertEqual(len(receipt["input_deltas"]), 1)
        self.assertTrue(receipt["policy"]["input_deltas_preserve_prior_denominator_history"])
        self.assertTrue(receipt["policy"]["override_order_is_explicit"])


if __name__ == "__main__":
    unittest.main()
