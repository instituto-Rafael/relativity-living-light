"""Exact static falsifiers for provider policy; no API calls, no secrets."""
import importlib.util
import pathlib
import unittest
ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("policy", ROOT / "scripts/ci/rafaelia_provider_ruleset_v1.py")
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)

class PolicyTests(unittest.TestCase):
    def test_profiles_are_allowlisted(self):
        self.assertEqual(set(p.PROFILES), {"instituto-Rafael/relativity-living-light", "rafaelmeloreisnovo/RafGitTools"})
    def test_no_bypass(self):
        for profile in p.PROFILES.values():
            self.assertEqual(p.policy(profile)["bypass_actors"], [])
    def test_approval_required(self):
        for profile in p.PROFILES.values():
            rules = {x["type"]:x for x in p.policy(profile)["rules"]}
            self.assertEqual(rules["pull_request"]["parameters"]["required_approving_review_count"], 1)
            self.assertTrue(rules["pull_request"]["parameters"]["require_last_push_approval"])
    def test_checks_bound_to_github_actions(self):
        for profile in p.PROFILES.values():
            status = {x["type"]:x for x in p.policy(profile)["rules"]}["required_status_checks"]["parameters"]
            self.assertTrue(status["strict_required_status_checks_policy"])
            self.assertTrue(all(x["integration_id"] == 15368 for x in status["required_status_checks"]))
    def test_bypass_falsifier(self):
        profile = next(iter(p.PROFILES.values()))
        x=p.policy(profile);x["bypass_actors"]=[{"actor_type":"Integration","bypass_mode":"always","actor_id":1}]
        self.assertFalse(p.compliant(x,p.policy(profile)))
    def test_missing_check_falsifier(self):
        profile = next(iter(p.PROFILES.values()))
        x=p.policy(profile)
        [r for r in x["rules"] if r["type"]=="required_status_checks"][0]["parameters"]["required_status_checks"]=[]
        self.assertFalse(p.compliant(x,p.policy(profile)))
    def test_rll_lab_covered(self):
        self.assertIn("refs/heads/rll/lab",p.PROFILES["instituto-Rafael/relativity-living-light"]["branches"])
    def test_rafgit_main_only(self):
        self.assertEqual(p.PROFILES["rafaelmeloreisnovo/RafGitTools"]["branches"],["~DEFAULT_BRANCH"])
    def test_preserve_unrelated_rule_types(self):
        profile=p.PROFILES["instituto-Rafael/relativity-living-light"]
        prev={"rules":[{"type":"required_signatures"}]}
        self.assertIn("required_signatures",[x["type"] for x in p.policy(profile,prev)["rules"]])
    def test_no_false_boolean_review(self):
        profile=next(iter(p.PROFILES.values()))
        x=p.policy(profile)
        [r for r in x["rules"] if r["type"]=="pull_request"][0]["parameters"]["required_approving_review_count"]=True
        self.assertFalse(p.compliant(x,p.policy(profile)))


# Adversarial cases: unexpected existing governance, duplicate checks,
# malformed provider payloads, ambiguous write outcomes, and privilege gates.
import copy
import os
import sys
from unittest import mock

class AdversarialPolicyTests(unittest.TestCase):
    RLL = p.PROFILES["instituto-Rafael/relativity-living-light"]
    RAF = p.PROFILES["rafaelmeloreisnovo/RafGitTools"]

    def rule(self, doc, name):
        return next(x for x in doc["rules"] if x["type"] == name)

    def test_existing_review_count_is_never_lowered(self):
        existing = {"rules": [{"type": "pull_request", "parameters": {
            "required_approving_review_count": 3, "require_code_owner_review": True,
            "require_extra_approval_for_unattributed_changes": True,
            "allowed_merge_methods": ["squash"]}}]}
        result = p.policy(self.RLL, existing)
        pr = self.rule(result, "pull_request")["parameters"]
        self.assertEqual(pr["required_approving_review_count"], 3)
        self.assertTrue(pr["require_code_owner_review"])
        self.assertTrue(pr["require_extra_approval_for_unattributed_changes"])
        self.assertEqual(pr["allowed_merge_methods"], ["squash"])

    def test_original_required_reviewers_are_preserved(self):
        reviewers = [{"file_pattern": "src/*", "minimum_approvals": 2, "reviewer": [{"id": 1234, "type": "Team"}]}]
        existing = {"rules": [{"type": "pull_request",
                               "parameters": {"required_reviewers": reviewers}}]}
        result = p.policy(self.RLL, existing)
        self.assertEqual(self.rule(result, "pull_request")["parameters"]["required_reviewers"], reviewers)

    def test_existing_other_security_rules_preserved_bitwise(self):
        sig = {"type": "required_signatures", "parameters": {"unknown_parameter": [5, {"x": "y"}]}}
        code = {"type": "code_scanning", "parameters": {"code_scanning_tools": [{"tool": "CodeQL"}]}}
        original = {"rules": [sig, code]}
        new = p.policy(self.RLL, original)
        self.assertIn(sig, new["rules"])
        self.assertIn(code, new["rules"])

    def test_existing_checks_are_unioned_without_dropping_producer(self):
        original = {"rules": [{"type": "required_status_checks", "parameters": {
            "strict_required_status_checks_policy": True,
            "required_status_checks": [{"context": "upstream-ci", "integration_id": 999}]}}]}
        status = self.rule(p.policy(self.RLL, original), "required_status_checks")["parameters"]
        self.assertIn({"context": "upstream-ci", "integration_id": 999}, status["required_status_checks"])
        self.assertIn({"context": "test", "integration_id": 15368}, status["required_status_checks"])

    def test_existing_conflicting_app_id_fail_closed(self):
        original = {"rules": [{"type": "required_status_checks", "parameters": {
            "required_status_checks": [{"context": "test", "integration_id": 9}]}}]}
        with self.assertRaisesRegex(p.Blocked, "CHECK_APP_ID_CONFLICT"):
            p.policy(self.RLL, original)

    def test_existing_duplicate_check_context_fail_closed(self):
        original = {"rules": [{"type": "required_status_checks", "parameters": {
            "required_status_checks": [{"context": "a", "integration_id": 1},
                                        {"context": "a", "integration_id": 1}]}}]}
        with self.assertRaisesRegex(p.Blocked, "DUPLICATED_EXISTING_CHECK"):
            p.policy(self.RLL, original)

    def test_duplicate_rule_types_fail_closed(self):
        with self.assertRaisesRegex(p.Blocked, "DUPLICATED_RULE_TYPES"):
            p.policy(self.RLL, {"rules": [{"type": "deletion"}, {"type": "deletion"}]})

    def test_existing_exclusion_fail_closed_not_silently_dropped(self):
        original = {"conditions": {"ref_name": {
            "include": ["~DEFAULT_BRANCH"], "exclude": ["refs/heads/rll/lab"]}}}
        with self.assertRaisesRegex(p.Blocked, "EXCLUSION"):
            p.policy(self.RLL, original)

    def test_extra_inclusions_preserved(self):
        original = {"conditions": {"ref_name": {"include": ["refs/heads/experimental"], "exclude": []}}}
        include = p.policy(self.RLL, original)["conditions"]["ref_name"]["include"]
        self.assertIn("refs/heads/experimental", include)
        self.assertIn("refs/heads/rll/lab", include)

    def test_missing_or_malformed_rules_fails(self):
        for value in ("not-a-list", [None], [{"bogus": 5}]):
            with self.subTest(value=value):
                with self.assertRaises(p.Blocked):
                    p.policy(self.RLL, {"rules": value})

    def test_corrupt_review_count_fails_without_bool_true_shortcut(self):
        for value in (-1, True, "3", 1.5, None):
            with self.subTest(value=value):
                with self.assertRaises(p.Blocked):
                    p.policy(self.RLL, {"rules": [{
                        "type": "pull_request", "parameters": {
                            "required_approving_review_count": value}}]})

    def test_missing_checks_fail(self):
        expected = p.policy(self.RLL)
        got = copy.deepcopy(expected)
        self.rule(got, "required_status_checks")["parameters"]["required_status_checks"] = []
        self.assertFalse(p.compliant(got, expected))

    def test_readback_cannot_weaken_review_count(self):
        old = {"rules": [{"type": "pull_request",
                          "parameters": {"required_approving_review_count": 2}}]}
        expected = p.policy(self.RLL, old)
        got = copy.deepcopy(expected)
        self.rule(got, "pull_request")["parameters"]["required_approving_review_count"] = 1
        self.assertFalse(p.compliant(got, expected))

    def test_readback_cannot_remove_code_owner(self):
        old = {"rules": [{"type": "pull_request",
                          "parameters": {"require_code_owner_review": True}}]}
        expected = p.policy(self.RLL, old)
        got = copy.deepcopy(expected)
        self.rule(got, "pull_request")["parameters"]["require_code_owner_review"] = False
        self.assertFalse(p.compliant(got, expected))

    def test_readback_cannot_remove_extra_unattributed_approval(self):
        old = {"rules": [{"type": "pull_request",
                          "parameters": {"require_extra_approval_for_unattributed_changes": True}}]}
        expected = p.policy(self.RLL, old)
        got = copy.deepcopy(expected)
        self.rule(got, "pull_request")["parameters"]["require_extra_approval_for_unattributed_changes"] = False
        self.assertFalse(p.compliant(got, expected))

    def test_readback_cannot_lose_original_required_reviewers(self):
        old = {"rules": [{"type": "pull_request",
                          "parameters": {"required_reviewers": [{"file_pattern": "*", "minimum_approvals": 2}]}}]}
        expected = p.policy(self.RLL, old)
        got = copy.deepcopy(expected)
        self.rule(got, "pull_request")["parameters"]["required_reviewers"] = []
        self.assertFalse(p.compliant(got, expected))

    def test_readback_cannot_widen_merge_methods(self):
        old = {"rules": [{"type": "pull_request",
                          "parameters": {"allowed_merge_methods": ["squash"]}}]}
        expected = p.policy(self.RLL, old)
        got = copy.deepcopy(expected)
        self.rule(got, "pull_request")["parameters"]["allowed_merge_methods"] = ["squash", "merge"]
        self.assertFalse(p.compliant(got, expected))

    def test_readback_cannot_drop_existing_signature_rule(self):
        expected = p.policy(self.RLL, {"rules": [{"type": "required_signatures"}]})
        got = copy.deepcopy(expected)
        got["rules"] = [r for r in got["rules"] if r["type"] != "required_signatures"]
        self.assertFalse(p.compliant(got, expected))

    def test_readback_duplicate_rule_type_is_false(self):
        expected = p.policy(self.RLL)
        got = copy.deepcopy(expected)
        got["rules"].append(copy.deepcopy(got["rules"][0]))
        self.assertFalse(p.compliant(got, expected))

    def test_readback_duplicate_status_is_false(self):
        expected = p.policy(self.RLL)
        got = copy.deepcopy(expected)
        status = self.rule(got, "required_status_checks")["parameters"]
        status["required_status_checks"].append(copy.deepcopy(status["required_status_checks"][0]))
        self.assertFalse(p.compliant(got, expected))

    def test_readback_bad_integration_id_is_false(self):
        expected = p.policy(self.RLL)
        got = copy.deepcopy(expected)
        self.rule(got, "required_status_checks")["parameters"]["required_status_checks"][0]["integration_id"] = 5
        self.assertFalse(p.compliant(got, expected))

    def test_readback_inactive_or_bypass_false(self):
        expected = p.policy(self.RLL)
        for mutation in ("evaluate", "disabled"):
            got = copy.deepcopy(expected)
            got["enforcement"] = mutation
            self.assertFalse(p.compliant(got, expected))
        got = copy.deepcopy(expected)
        got["bypass_actors"].append({"actor_type": "OrganizationAdmin", "bypass_mode": "always"})
        self.assertFalse(p.compliant(got, expected))

    def test_readback_missing_main_or_lab_is_false(self):
        expected = p.policy(self.RLL)
        for missing in ("~DEFAULT_BRANCH", "refs/heads/rll/lab"):
            got = copy.deepcopy(expected)
            got["conditions"]["ref_name"]["include"].remove(missing)
            self.assertFalse(p.compliant(got, expected))

    def test_no_redirects_to_external_hosts(self):
        with self.assertRaisesRegex(p.Blocked, "HTTP_REDIRECT_DENIED"):
            p.NoRedirect().redirect_request(None, None, 302, "moved", {}, "https://evil.example/")

    def test_live_rejects_forged_repo_identity(self):
        meta = {"full_name": "instituto-Rafael/relativity-living-light", "id": 9,
                "default_branch": "main", "private": False}
        with mock.patch.object(p, "api", return_value=meta):
            with self.assertRaisesRegex(p.Blocked, "IDENTITY"):
                p.live("instituto-Rafael/relativity-living-light", self.RLL, "fake")

    def test_live_rejects_unknown_ruleset_count(self):
        meta = {"full_name": "instituto-Rafael/relativity-living-light", "id": 1046495816,
                "default_branch": "main", "private": False}
        def fake(method, path, token, payload=None):
            if path.endswith("/branches/main"):
                return {"commit": {"sha": "a" * 40}}
            if path.endswith("/rulesets"):
                return [{"id": 23116926, "name": self.RLL["name"]},
                        {"id": 999, "name": "other"}]
            return meta
        with mock.patch.object(p, "api", side_effect=fake):
            with self.assertRaisesRegex(p.Blocked, "UNRECONCILED_ADDITIONAL_RULESETS"):
                p.live("instituto-Rafael/relativity-living-light", self.RLL, "fake")

    def test_apply_rejects_missing_reviewer_evidence_before_writes(self):
        argv = ["gate", "--mode", "apply", "--repo",
                "rafaelmeloreisnovo/RafGitTools",
                "--expected-main-sha", "a" * 40,
                "--reviewer-login", "trusted-reviewer",
                "--confirm", "APPLY-P0:rafaelmeloreisnovo/RafGitTools"]
        env = {"GH_API_TOKEN": "fake", "GITHUB_REPOSITORY": "rafaelmeloreisnovo/RafGitTools",
               "GITHUB_EVENT_NAME": "workflow_dispatch", "GITHUB_REF": "refs/heads/main",
               "GITHUB_ACTOR": p.ACTOR}
        with mock.patch.object(sys, "argv", argv), \
             mock.patch.dict(os.environ, env, clear=True), \
             mock.patch.object(p, "live", return_value=("a" * 40, None)), \
             mock.patch.object(p, "api", return_value={"permission": "write"}) as api_mock:
            with self.assertRaisesRegex(p.Blocked, "REVIEWER_AND_ROLLBACK_NOT_VERIFIED"):
                p.main()
            self.assertTrue(all(call.args[0] == "GET" for call in api_mock.call_args_list))

    def test_apply_rejects_self_review_even_with_manual_evidence(self):
        argv = ["gate", "--mode", "apply", "--repo",
                "rafaelmeloreisnovo/RafGitTools",
                "--expected-main-sha", "a" * 40,
                "--reviewer-login", p.ACTOR,
                "--confirm", "APPLY-P0:rafaelmeloreisnovo/RafGitTools"]
        env = {"GH_API_TOKEN": "fake", "GITHUB_REPOSITORY": "rafaelmeloreisnovo/RafGitTools",
               "GITHUB_EVENT_NAME": "workflow_dispatch", "GITHUB_REF": "refs/heads/main",
               "GITHUB_ACTOR": p.ACTOR, "RAFAELIA_REVIEWER_GATE_EVIDENCE":
               "REVIEWED_INDEPENDENT_REVIEWER_AND_ROLLBACK"}
        with mock.patch.object(sys, "argv", argv), \
             mock.patch.dict(os.environ, env, clear=True), \
             mock.patch.object(p, "live", return_value=("a" * 40, None)), \
             mock.patch.object(p, "api") as api_mock:
            with self.assertRaisesRegex(p.Blocked, "REVIEWER_LOGIN_INVALID"):
                p.main()
            api_mock.assert_not_called()

    def test_apply_rejects_unqualified_reviewer_read_only(self):
        argv = ["gate", "--mode", "apply", "--repo",
                "rafaelmeloreisnovo/RafGitTools", "--expected-main-sha", "a" * 40,
                "--reviewer-login", "other-human",
                "--confirm", "APPLY-P0:rafaelmeloreisnovo/RafGitTools"]
        env = {"GH_API_TOKEN": "fake", "GITHUB_REPOSITORY": "rafaelmeloreisnovo/RafGitTools",
               "GITHUB_EVENT_NAME": "workflow_dispatch", "GITHUB_REF": "refs/heads/main",
               "GITHUB_ACTOR": p.ACTOR, "RAFAELIA_REVIEWER_GATE_EVIDENCE":
               "REVIEWED_INDEPENDENT_REVIEWER_AND_ROLLBACK"}
        with mock.patch.object(sys, "argv", argv), \
             mock.patch.dict(os.environ, env, clear=True), \
             mock.patch.object(p, "live", return_value=("a" * 40, None)), \
             mock.patch.object(p, "api", return_value={"permission": "read"}) as api_mock:
            with self.assertRaisesRegex(p.Blocked, "REVIEWER_PERMISSION_NOT_VERIFIED"):
                p.main()
            self.assertTrue(all(call.args[0] == "GET" for call in api_mock.call_args_list))

    def test_apply_rejects_old_head_even_with_reviewer_evidence(self):
        argv = ["gate", "--mode", "apply", "--repo",
                "rafaelmeloreisnovo/RafGitTools", "--expected-main-sha", "b" * 40,
                "--confirm", "APPLY-P0:rafaelmeloreisnovo/RafGitTools"]
        env = {"GH_API_TOKEN": "fake", "GITHUB_REPOSITORY": "rafaelmeloreisnovo/RafGitTools",
               "GITHUB_EVENT_NAME": "workflow_dispatch", "GITHUB_REF": "refs/heads/main",
               "GITHUB_ACTOR": p.ACTOR, "RAFAELIA_REVIEWER_GATE_EVIDENCE":
               "REVIEWED_INDEPENDENT_REVIEWER_AND_ROLLBACK"}
        with mock.patch.object(sys, "argv", argv), \
             mock.patch.dict(os.environ, env, clear=True), \
             mock.patch.object(p, "live", return_value=("a" * 40, None)), \
             mock.patch.object(p, "api") as api_mock:
            with self.assertRaisesRegex(p.Blocked, "HEAD_MOVED_STOP"):
                p.main()
            api_mock.assert_not_called()

    def test_no_admin_secret_read_in_validate_mode(self):
        argv = ["gate", "--mode", "validate", "--repo", "rafaelmeloreisnovo/RafGitTools"]
        with mock.patch.object(sys, "argv", argv), \
             mock.patch.dict(os.environ, {}, clear=True), \
             mock.patch.object(p, "api") as api_mock, \
             mock.patch.object(p, "receipt"):
            self.assertEqual(p.main(), 0)
            api_mock.assert_not_called()

    def test_uncertain_write_state_is_latched_on_exception(self):
        argv = ["gate", "--mode", "apply", "--repo",
                "rafaelmeloreisnovo/RafGitTools", "--expected-main-sha", "a" * 40,
                "--reviewer-login", "verified-human",
                "--confirm", "APPLY-P0:rafaelmeloreisnovo/RafGitTools"]
        env = {"GH_API_TOKEN": "fake", "GITHUB_REPOSITORY": "rafaelmeloreisnovo/RafGitTools",
               "GITHUB_EVENT_NAME": "workflow_dispatch", "GITHUB_REF": "refs/heads/main",
               "GITHUB_ACTOR": p.ACTOR, "RAFAELIA_REVIEWER_GATE_EVIDENCE":
               "REVIEWED_INDEPENDENT_REVIEWER_AND_ROLLBACK"}
        def fake_api(method, path, token, payload=None):
            if method == "GET" and path.endswith("/permission"):
                return {"permission": "write"}
            raise p.Blocked("PROVIDER_NETWORK_ERROR")
        p.WRITE_ATTEMPTED = False
        with mock.patch.object(sys, "argv", argv), \
             mock.patch.dict(os.environ, env, clear=True), \
             mock.patch.object(p, "live", return_value=("a" * 40, None)), \
             mock.patch.object(p, "api", side_effect=fake_api), \
             mock.patch.object(p, "receipt"):
            with self.assertRaisesRegex(p.Blocked, "PROVIDER_NETWORK_ERROR"):
                p.main()
            self.assertTrue(p.WRITE_ATTEMPTED)
        p.WRITE_ATTEMPTED = False

if __name__ == "__main__":
    unittest.main()
