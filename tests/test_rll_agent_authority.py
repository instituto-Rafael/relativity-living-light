from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "agent" / "rll_agent_authority.py"

spec = importlib.util.spec_from_file_location("rll_agent_authority", MODULE_PATH)
authority = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(authority)


class RLLAgentAuthorityTests(unittest.TestCase):
    def clean_env(self):
        keys = {
            authority.PAT_SELECTOR,
            authority.PAT_PRIMARY,
            *authority.PAT_ALIASES,
        }
        return mock.patch.dict(os.environ, {key: "" for key in keys}, clear=False)

    def test_missing_pat_is_token_vazio(self):
        with self.clean_env():
            receipt, rc = authority.probe("instituto-Rafael/relativity-living-light")
        self.assertEqual(rc, 3)
        self.assertFalse(receipt["auth_present"])
        self.assertIn("TOKEN_VAZIO_AGENT_GITHUB_PAT", receipt["gaps"])
        self.assertFalse(receipt["claim_allowed"])

    def test_ambiguous_aliases_fail_closed(self):
        with self.clean_env():
            with mock.patch.dict(
                os.environ,
                {"GH_PAT": "one-secret", "PAT_GIT": "another-secret"},
                clear=False,
            ):
                with self.assertRaisesRegex(
                    authority.AuthorityError,
                    "TOKEN_VAZIO_AMBIGUOUS_AGENT_PAT",
                ):
                    authority.resolve_pat()

    def test_explicit_selector_resolves_without_guessing(self):
        with self.clean_env():
            with mock.patch.dict(
                os.environ,
                {
                    authority.PAT_SELECTOR: "MY_AGENT_PAT",
                    "MY_AGENT_PAT": "secret-value",
                },
                clear=False,
            ):
                source, token = authority.resolve_pat()
        self.assertEqual(source, "MY_AGENT_PAT")
        self.assertEqual(token, "secret-value")

    def test_patgithub_is_canonical_agent_pat(self):
        with self.clean_env():
            with mock.patch.dict(
                os.environ,
                {authority.PAT_PRIMARY: "opaque-patgithub"},
                clear=False,
            ):
                source, token = authority.resolve_pat()
        self.assertEqual(source, "PATGITHUB")
        self.assertEqual(token, "opaque-patgithub")

    def test_patgithub_wins_over_legacy_alias_without_guessing(self):
        with self.clean_env():
            with mock.patch.dict(
                os.environ,
                {
                    authority.PAT_PRIMARY: "canonical",
                    "GH_PAT": "legacy",
                },
                clear=False,
            ):
                source, token = authority.resolve_pat()
        self.assertEqual(source, "PATGITHUB")
        self.assertEqual(token, "canonical")

    def test_probe_receipt_never_contains_secret(self):
        secret = "never-persist-this-token"
        with self.clean_env():
            with mock.patch.dict(os.environ, {"RLL_AGENT_PAT": secret}, clear=False):
                with mock.patch.object(
                    authority,
                    "github_get",
                    side_effect=[
                        (200, {"login": "agent-user"}),
                        (200, {"permissions": {"pull": True, "push": True}}),
                    ],
                ):
                    receipt, rc = authority.probe(
                        "instituto-Rafael/relativity-living-light"
                    )
        self.assertEqual(rc, 0)
        blob = json.dumps(receipt)
        self.assertNotIn(secret, blob)
        self.assertTrue(receipt["authenticated"])
        self.assertEqual(receipt["credential_role_map"]["github_control_plane"], "PATGITHUB")
        self.assertEqual(receipt["credential_role_map"]["git_transport_candidate"], "GIT")
        self.assertEqual(receipt["credential_role_map"]["climate_provider"], "CLIMATE")
        self.assertEqual(
            receipt["token_scope_claim"],
            "TOKEN_VAZIO_FINE_GRAINED_SCOPE_NOT_INFERRED",
        )

    def test_protected_branch_push_denied(self):
        allowed, reason = authority.classify_command(
            ["git", "push", "origin", "HEAD"],
            branch="rll/lab",
        )
        self.assertFalse(allowed)
        self.assertEqual(reason, "PUSH_REQUIRES_AGENT_OR_WORK_BRANCH")

    def test_force_push_denied(self):
        allowed, reason = authority.classify_command(
            ["git", "push", "--force", "origin", "HEAD"],
            branch="work/test",
        )
        self.assertFalse(allowed)
        self.assertEqual(reason, "FORCE_PUSH_FORBIDDEN")

    def test_work_branch_push_allowed(self):
        allowed, reason = authority.classify_command(
            ["git", "push", "origin", "HEAD"],
            branch="agent/test",
        )
        self.assertTrue(allowed)
        self.assertEqual(reason, "ALLOW_WORK_BRANCH_PUSH")

    def test_pr_merge_denied(self):
        allowed, reason = authority.classify_command(["gh", "pr", "merge", "42"])
        self.assertFalse(allowed)
        self.assertEqual(reason, "PR_MERGE_FORBIDDEN")

    def test_pr_create_requires_explicit_rll_lab_base(self):
        allowed, reason = authority.classify_command(
            ["gh", "pr", "create", "--title", "x"],
            branch="agent/test",
        )
        self.assertFalse(allowed)
        self.assertEqual(reason, "PR_CREATE_REQUIRES_EXPLICIT_RLL_LAB_BASE")

    def test_pr_create_rejects_main_base(self):
        allowed, reason = authority.classify_command(
            ["gh", "pr", "create", "--base", "main", "--title", "x"],
            branch="agent/test",
        )
        self.assertFalse(allowed)
        self.assertEqual(reason, "PR_CREATE_BASE_FORBIDDEN")

    def test_pr_create_requires_work_branch(self):
        allowed, reason = authority.classify_command(
            ["gh", "pr", "create", "--base", "rll/lab", "--title", "x"],
            branch="rll/lab",
        )
        self.assertFalse(allowed)
        self.assertEqual(reason, "PR_CREATE_REQUIRES_WORK_BRANCH")

    def test_pr_create_allowed_from_work_branch_to_rll_lab(self):
        allowed, reason = authority.classify_command(
            [
                "gh", "pr", "create",
                "--base", "rll/lab",
                "--head", "agent/test",
                "--title", "x",
            ],
            branch="agent/test",
        )
        self.assertTrue(allowed)
        self.assertEqual(reason, "ALLOW_PR_CREATE_TO_RLL_LAB")

    def test_pr_create_rejects_mismatched_head(self):
        allowed, reason = authority.classify_command(
            [
                "gh", "pr", "create",
                "--base", "rll/lab",
                "--head", "agent/other",
                "--title", "x",
            ],
            branch="agent/test",
        )
        self.assertFalse(allowed)
        self.assertEqual(reason, "PR_CREATE_HEAD_MUST_MATCH_CURRENT_WORK_BRANCH")

    def test_secret_mutation_denied(self):
        allowed, reason = authority.classify_command(
            ["gh", "secret", "set", "SOME_SECRET"]
        )
        self.assertFalse(allowed)
        self.assertEqual(reason, "SECRET_OR_VARIABLE_MUTATION_FORBIDDEN")

    def test_mutating_raw_api_denied(self):
        allowed, reason = authority.classify_command(
            ["gh", "api", "--method", "DELETE", "/repos/o/r/git/refs/heads/x"]
        )
        self.assertFalse(allowed)
        self.assertEqual(reason, "MUTATING_GH_API_FORBIDDEN")

    def test_dispatch_and_rerun_allowed_by_contract(self):
        dispatch = authority.classify_command(
            ["gh", "workflow", "run", "rll-governance-quality-gate.yml"]
        )
        rerun = authority.classify_command(["gh", "run", "rerun", "123"])
        self.assertTrue(dispatch[0])
        self.assertTrue(rerun[0])

    def test_guard_denial_receipt_has_no_token(self):
        with self.clean_env():
            with mock.patch.dict(os.environ, {"RLL_AGENT_PAT": "top-secret"}, clear=False):
                with tempfile.TemporaryDirectory() as tmp:
                    receipt_path = Path(tmp) / "receipt.json"
                    rc = authority.guarded_exec(
                        ["gh", "pr", "merge", "1"],
                        receipt_path,
                    )
                    text = receipt_path.read_text(encoding="utf-8")
        self.assertEqual(rc, 126)
        self.assertNotIn("top-secret", text)
        self.assertIn("PR_MERGE_FORBIDDEN", text)

    def test_delete_force_and_remote_override_push_forms_are_denied(self):
        cases = [
            ["git", "push", "--delete", "origin", "work/x"],
            ["git", "push", "-d", "origin", "work/x"],
            ["git", "push", "origin", ":refs/heads/work/x"],
            ["git", "push", "origin", "+HEAD:refs/heads/work/x"],
            ["git", "push", "--mirror", "origin"],
            ["git", "push", "--prune", "origin", "HEAD"],
            ["git", "push", "--force-with-lease=refs/heads/work/x:abc", "origin", "HEAD"],
            ["git", "push", "origin", "HEAD:rll/release"],
            ["git", "push", "origin", "refs/tags/x"],
            ["git", "push", "--receive-pack=other-command", "origin", "HEAD"],
            ["git", "push", "https://example.invalid/repo", "HEAD"],
        ]
        for argv in cases:
            with self.subTest(argv=argv):
                self.assertFalse(authority.classify_command(argv, branch="work/x")[0])

    def test_same_branch_explicit_refspec_is_allowed(self):
        for argv in (
            ["git", "push", "-u", "origin", "HEAD:refs/heads/work/x"],
            ["git", "push", "origin", "work/x:work/x"],
        ):
            with self.subTest(argv=argv):
                self.assertTrue(authority.classify_command(argv, branch="work/x")[0])

    def test_implicit_post_compact_delete_and_auth_overrides_are_denied(self):
        cases = [
            ["gh", "api", "/repos/o/r", "-f", "name=x"],
            ["gh", "api", "/repos/o/r", "-Fname=x"],
            ["gh", "api", "/repos/o/r", "--input=body.json"],
            ["gh", "api", "/repos/o/r", "-XDELETE"],
            ["gh", "api", "/repos/o/r", "--method=PATCH"],
            ["gh", "api", "/repos/o/r", "--hostname=example.invalid"],
            ["gh", "api", "https://example.invalid/api"],
            ["gh", "api", "/repos/o/r", "-HAuthorization: other"],
            ["gh", "api", "/repos/o/r/actions/secrets"],
            ["gh", "auth", "status", "--show-token"],
        ]
        for argv in cases:
            with self.subTest(argv=argv):
                self.assertFalse(authority.classify_command(argv)[0])

    def test_explicit_readonly_api_is_allowed(self):
        for argv in (
            ["gh", "api", "/user"],
            ["gh", "api", "/repos/o/r/commits", "--method", "GET"],
            ["gh", "api", "/repos/o/r/branches", "-XGET", "--paginate"],
        ):
            with self.subTest(argv=argv):
                self.assertTrue(authority.classify_command(argv)[0])

    def test_owner_reported_pat_alias_and_unassigned_git(self):
        with mock.patch.dict(os.environ, {"PATGITHUB": "fixture-value", "GIT": "unassigned"}, clear=True):
            name, _ = authority.resolve_pat()
        self.assertEqual(name, "PATGITHUB")
        with mock.patch.dict(os.environ, {"GIT": "unassigned"}, clear=True):
            self.assertEqual(authority.resolve_pat(), (None, None))


if __name__ == "__main__":
    unittest.main()
