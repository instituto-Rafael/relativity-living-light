from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRIAGE = ROOT / "data/governance/RLL_DIVERGED_REF_TRIAGE_20260808_V1.json"
CUSTODY = ROOT / "data/governance/RLL_TO_ADD_LEGACY_CUSTODY_20260225_V1.json"
ARCHIVE = ROOT / "docs/archive/2026-07-09/REPO_SESSION_ARTIFACT_MAP_RAFAELIA.branch-573dd27.md"


class DivergedRefTriageTests(unittest.TestCase):
    def load_triage(self):
        return json.loads(TRIAGE.read_text(encoding="utf-8"))

    def test_frozen_35_have_complete_non_overlapping_disposition(self):
        d = self.load_triage()
        self.assertEqual(d["schema"], "rll.diverged_ref_triage.v1")
        self.assertFalse(d["claim_allowed"])
        self.assertEqual(d["summary"]["frozen_cohort_size"], 35)
        self.assertEqual(d["summary"]["patch_equivalent_no_action"], 3)
        self.assertEqual(d["summary"]["exact_head_merged_direct_main"], 17)
        self.assertEqual(d["summary"]["promotion_chain_recovered"], 1)
        self.assertEqual(d["summary"]["semantically_classified"], 14)
        self.assertEqual(d["summary"]["anonymous_remainder"], 0)
        self.assertEqual(d["summary"]["unclassified_remainder"], 0)

        refs = []
        refs.extend(d["patch_equivalent_no_action"])
        refs.extend(d["exact_head_merged_direct_main"])
        refs.extend(row["ref"] for row in d["promotion_chain_recovered"])
        refs.extend(row["ref"] for row in d["semantic_classifications"])
        self.assertEqual(len(refs), 35)
        self.assertEqual(len(set(refs)), 35)

    def test_only_two_frozen_refs_are_active_recovery_items(self):
        d = self.load_triage()
        active = {
            row["ref"]: row["next_action"]
            for row in d["semantic_classifications"]
            if row["state"] in {"ACTIVE_RECOVERY_PR", "SUPERSEDED_BY_ACTIVE_HOTFIX"}
        }
        self.assertEqual(
            active,
            {
                "audit/all-ref-topology-census-20260808-v1": "REVIEW_PR_685",
                "copilot/connect-scan-rll-model-evidence": "REVIEW_PR_688",
                "fix/ref-census-postmerge-governance-20260808-v1": "REVIEW_PR_685",
            },
        )
        self.assertEqual(d["summary"]["active_recovery_refs"], 2)

    def test_to_add_custody_has_nine_valid_sha256_and_no_destructive_authority(self):
        d = json.loads(CUSTODY.read_text(encoding="utf-8"))
        self.assertEqual(d["state"], "LEGACY_CUSTODY_PRESERVED_DESTRUCTIVE_MERGE_REJECTED")
        self.assertFalse(d["claim_allowed"])
        self.assertFalse(d["comparison"]["destructive_reorganization_authorized"])
        self.assertTrue(d["comparison"]["branch_58_and_57_hash_sets_identical"])
        self.assertEqual(len(d["observed_hashes"]), 9)
        for row in d["observed_hashes"]:
            self.assertRegex(row["sha256"], r"^[0-9a-f]{64}$")

    def test_historical_doc_snapshot_is_explicitly_non_authoritative(self):
        text = ARCHIVE.read_text(encoding="utf-8")
        self.assertIn("Historical custody snapshot; not current authority.", text)
        self.assertIn("Source head: 573dd27efbc6dec63b332b38bcf81cb2dfe2e88b", text)
        self.assertIn("Source blob: 1494cb4e65e1831c7464b33c26d6640db85b68eb", text)
        self.assertIn("claim_allowed=false", text)


if __name__ == "__main__":
    unittest.main()
