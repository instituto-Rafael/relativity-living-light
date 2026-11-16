"""Scoped offline tests for the read-only RLL PR readiness guard."""
import copy
import json
import unittest
from pathlib import Path

from tools.ci.rll_pr_merge_guard_offline_v1 import (
    evaluate_snapshot, reasons_for_hold, validate_snapshot,
)

SNAPSHOT_PATH = (
    Path(__file__).resolve().parents[1]
    / "data/governance/rll_pr_merge_readiness_20261115.v1.json"
)


class RLLMergeReadinessGuardV1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))

    def test_frozen_snapshot_accounts_for_all_12_prs(self):
        self.assertTrue(validate_snapshot(self.snapshot))
        self.assertEqual(set(x["number"] for x in self.snapshot["prs"]), {
            1200, 1203, 1204, 1205, 1206, 1207, 1208, 1209, 1210, 1211, 1212, 1213
        })

    def test_no_pr_is_merge_authorized_on_observed_evidence(self):
        report = evaluate_snapshot(self.snapshot)
        self.assertEqual(report["snapshot_count"], 12)
        self.assertEqual(report["blocked"], 12)
        self.assertEqual(report["eligible_automatic_merge"], 0)
        self.assertFalse(report["live_head_rechecked"])
        self.assertTrue(all(not x["automatic_merge_allowed"] for x in report["results"]))

    def test_clean_metadata_alone_never_implies_merge_authority(self):
        x = copy.deepcopy(self.snapshot["prs"][0])
        x.update({
            "draft": False, "manual_hold": False, "mergeable_state": "clean",
            "failed_checks": [], "base_ref": "main",
            "base_sha": self.snapshot["branch_heads"]["main"]["sha"],
            "approval_status": "APPROVED_CURRENT_HEAD",
            "required_check_suite_attested": True,
            "dependency_ancestry_verified": True,
            "regression_evidence_confirmed": True,
        })
        out = reasons_for_hold(x, self.snapshot["branch_heads"])
        self.assertEqual(out, [])
        # Readiness means HUMAN_REVIEW_ONLY. There is deliberately NO merge API.
        copy_data = copy.deepcopy(self.snapshot)
        copy_data["prs"] = [x]
        report = evaluate_snapshot(copy_data)
        self.assertEqual(report["results"][0]["status"], "HUMAN_REVIEW_ONLY")
        self.assertIs(report["results"][0]["automatic_merge_allowed"], False)

    def test_stale_base_ref_blocks_even_when_checks_pass(self):
        x = copy.deepcopy(self.snapshot["prs"][0])
        x.update({"draft":False,"manual_hold":False,"mergeable_state":"clean",
                  "failed_checks":[],"base_ref":"main",
                  "base_sha":"0"*40})
        self.assertIn("BASE_SHA_STALE", reasons_for_hold(x, self.snapshot["branch_heads"]))

    def test_unknown_check_state_is_not_empty_success(self):
        x = copy.deepcopy(self.snapshot["prs"][0])
        x["failed_checks"] = None
        self.assertIn("EXACT_HEAD_CHECKS_UNVERIFIED",
                      reasons_for_hold(x, self.snapshot["branch_heads"]))

    def test_org_missing_does_not_create_branch(self):
        self.assertEqual(self.snapshot["branch_heads"]["org"]["state"],
                         "NOT_FOUND_GITHUB_BRANCH_404")
        self.assertIsNone(self.snapshot["branch_heads"]["org"]["sha"])

    def test_duplicate_pr_identity_fails(self):
        data = copy.deepcopy(self.snapshot)
        data["prs"].append(copy.deepcopy(data["prs"][0]))
        with self.assertRaisesRegex(ValueError, "PR_IDENTITY_COLLISION"):
            validate_snapshot(data)


if __name__ == "__main__":
    unittest.main()
