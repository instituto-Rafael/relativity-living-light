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


if __name__ == "__main__":
    unittest.main()
