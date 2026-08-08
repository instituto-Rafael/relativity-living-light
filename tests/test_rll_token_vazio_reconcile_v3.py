from __future__ import annotations

import unittest

from tools.rll_token_vazio_reconcile_v3 import ROOT, build_current_view


class TokenVazioReconcileV3Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = build_current_view(ROOT, generated_at="2026-08-08T05:44:00Z")
        cls.by_token = {row["token"]: row for row in cls.receipt["results"]}

    def test_v3_preserves_denominator_and_closes_only_asserted_late_evidence(self):
        summary = self.receipt["summary"]
        self.assertEqual(summary["input_tokens"], 33)
        self.assertEqual(summary["terminal_resolved"], 12)
        self.assertEqual(summary["reduced_generic"], 9)
        self.assertEqual(summary["open"], 12)
        self.assertFalse(any(row["state"] == "OPEN_EVIDENCE_MISSING" for row in self.receipt["results"]))
        self.assertIs(self.receipt["claim_allowed"], False)
        self.assertIs(self.receipt["publication_ready"], False)
        self.assertEqual(self.receipt["view"], "RLL_TOKEN_VAZIO_RECONCILIATION_V3_APPEND_ONLY")

    def test_ref_semantic_review_is_resolved_by_complete_disposition(self):
        row = self.by_token["TOKEN_VAZIO_DIVERGED_OR_DESCENDANT_REF_SEMANTIC_REVIEW"]
        self.assertEqual(row["state"], "RESOLVED")
        self.assertEqual(row["classification"], "FROZEN_35_REF_SEMANTIC_DISPOSITION_COMPLETE")

    def test_h0_primary_source_provenance_is_resolved_narrowly(self):
        row = self.by_token["TOKEN_VAZIO_H0_PRIOR_PRIMARY_SOURCE_PROVENANCE"]
        self.assertEqual(row["state"], "RESOLVED")
        self.assertEqual(row["classification"], "PRIMARY_PAPER_NUMERIC_PROVENANCE_AND_MATRIX_MAPPING_VERIFIED")

    def test_scientific_successors_remain_open(self):
        expected_open = {
            "TOKEN_VAZIO_REAL_BAYES_JOINT_MULTI_PROBE",
            "TOKEN_VAZIO_INDEPENDENT_REPLICATION",
            "TOKEN_VAZIO_DESI_DR2_OFFICIAL_JOINT_CROSSBLOCK_REPRODUCTION",
            "TOKEN_VAZIO_PHYSICAL_EXECUTION",
            "TOKEN_VAZIO_ACT_DR6_LCDM_POSTERIOR_CHAIN_REPRODUCTION",
            "TOKEN_VAZIO_DES_Y6_3X2PT_LIKELIHOOD",
            "TOKEN_VAZIO_RLL_PERTURBATION_CLOSURE_RELATIONS",
            "TOKEN_VAZIO_RLL_CLASS_CAMB_IMPLEMENTATION",
            "TOKEN_VAZIO_H0_RD_FULL_BOLTZMANN_INFERENCE_INTEGRATION",
            "TOKEN_VAZIO_EXTERNAL_SETTINGS",
            "TOKEN_VAZIO_UTM185_TERMUX_EXECUTION",
            "TOKEN_VAZIO_UTM185_REAL_MODEL_TRAINING",
        }
        actual_open = {
            token
            for token, row in self.by_token.items()
            if row["state"].startswith("OPEN_")
        }
        self.assertEqual(actual_open, expected_open)


if __name__ == "__main__":
    unittest.main()
