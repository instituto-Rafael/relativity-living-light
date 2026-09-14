from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATCH_SCRIPT = ROOT / "tools/audit_diverged_ref_patches_v1.py"
LINEAGE_SCRIPT = ROOT / "tools/audit_diverged_ref_pr_lineage_v1.py"

patch_spec = importlib.util.spec_from_file_location("patch_audit", PATCH_SCRIPT)
assert patch_spec and patch_spec.loader
patch_module = importlib.util.module_from_spec(patch_spec)
patch_spec.loader.exec_module(patch_module)

lineage_spec = importlib.util.spec_from_file_location("lineage_audit", LINEAGE_SCRIPT)
assert lineage_spec and lineage_spec.loader
lineage_module = importlib.util.module_from_spec(lineage_spec)
lineage_spec.loader.exec_module(lineage_module)


class DivergedRefPatchEquivalenceTests(unittest.TestCase):
    def test_file_categories_are_deterministic(self):
        self.assertEqual(
            patch_module.file_categories(["tools/a.py", "tests/test_a.py", "README.md", "tools/b.py"]),
            {"ROOT": 1, "tests": 1, "tools": 2},
        )

    def test_source_declares_semantic_boundary(self):
        source = PATCH_SCRIPT.read_text(encoding="utf-8")
        self.assertIn("patch-equivalence is narrower than semantic equivalence", source)
        self.assertIn("a plus patch is not automatically technical progress", source)
        self.assertIn("no forward-port is authorized automatically", source)

    def test_source_requires_frozen_cohort(self):
        source = PATCH_SCRIPT.read_text(encoding="utf-8")
        self.assertIn('COHORT_SCHEMA = "rll.diverged_ref_cohort.v1"', source)
        self.assertIn("duplicate ref in frozen cohort", source)

    def test_exact_merged_head_to_main_removes_forward_port_review(self):
        patch_receipt = {
            "schema": "rll.diverged_ref_patch_equivalence.v1",
            "summary": {"cohort_size": 1, "refs_with_unique_patches": 1, "refs_without_unique_patch_after_equivalence": 0},
            "rows": [{
                "ref": "refs/remotes/origin/feat/example",
                "head_sha": "abc123",
                "state": "UNIQUE_PATCHES_REQUIRE_REVIEW",
                "unique_patch_commit_count": 3,
                "patch_equivalent_commit_count": 0,
            }],
        }
        prs = [{
            "number": 99,
            "title": "example",
            "merged_at": "2026-08-01T00:00:00Z",
            "merge_commit_sha": "merge99",
            "head": {"sha": "abc123"},
            "base": {"ref": "main"},
        }]
        result = lineage_module.classify(patch_receipt, prs)
        self.assertEqual(result["summary"]["exact_head_merged_direct_to_main"], 1)
        self.assertEqual(result["summary"]["remaining_semantic_or_chain_review"], 0)
        self.assertFalse(result["rows"][0]["semantic_review_required"])

    def test_exact_merged_head_to_non_main_stays_open(self):
        patch_receipt = {
            "schema": "rll.diverged_ref_patch_equivalence.v1",
            "summary": {"cohort_size": 1, "refs_with_unique_patches": 1, "refs_without_unique_patch_after_equivalence": 0},
            "rows": [{
                "ref": "refs/remotes/origin/feat/example",
                "head_sha": "abc123",
                "state": "UNIQUE_PATCHES_REQUIRE_REVIEW",
                "unique_patch_commit_count": 3,
                "patch_equivalent_commit_count": 0,
            }],
        }
        prs = [{
            "number": 100,
            "title": "example",
            "merged_at": "2026-08-01T00:00:00Z",
            "merge_commit_sha": "merge100",
            "head": {"sha": "abc123"},
            "base": {"ref": "rll/lab"},
        }]
        result = lineage_module.classify(patch_receipt, prs)
        self.assertEqual(result["summary"]["exact_head_merged_to_non_main_requires_chain_audit"], 1)
        self.assertTrue(result["rows"][0]["semantic_review_required"])

    def test_no_exact_merged_head_stays_open(self):
        patch_receipt = {
            "schema": "rll.diverged_ref_patch_equivalence.v1",
            "summary": {"cohort_size": 1, "refs_with_unique_patches": 1, "refs_without_unique_patch_after_equivalence": 0},
            "rows": [{
                "ref": "refs/remotes/origin/feat/example",
                "head_sha": "abc123",
                "state": "UNIQUE_PATCHES_REQUIRE_REVIEW",
                "unique_patch_commit_count": 3,
                "patch_equivalent_commit_count": 0,
            }],
        }
        result = lineage_module.classify(patch_receipt, [])
        self.assertEqual(result["summary"]["unique_patch_no_exact_merged_pr_head"], 1)
        self.assertTrue(result["rows"][0]["semantic_review_required"])


if __name__ == "__main__":
    unittest.main()
