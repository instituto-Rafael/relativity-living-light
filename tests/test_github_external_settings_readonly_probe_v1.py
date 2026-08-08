from __future__ import annotations

import unittest

from tools.github_external_settings_readonly_probe_v1 import build


class ExternalSettingsReadonlyProbeTests(unittest.TestCase):
    def fetcher_full(self, url, token):
        if url.endswith("/rulesets?includes_parents=true"):
            return 200, [{"id": 1, "name": "release topology", "target": "branch", "enforcement": "active", "rules": [{"type": "pull_request"}], "bypass_actors": []}]
        if url.endswith("/protection"):
            return 200, {"required_status_checks": {"strict": True, "contexts": ["test"], "checks": [{"context": "test"}]}, "enforce_admins": {"enabled": True}, "allow_force_pushes": {"enabled": False}, "allow_deletions": {"enabled": False}}
        return 200, {"protected": True}

    def test_full_authority_is_resolution_eligible_but_does_not_change_token(self):
        result = build("org/repo", token="opaque", fetcher=self.fetcher_full)
        self.assertEqual(result["state"], "VERIFIED_EXTERNAL_SETTINGS_READONLY")
        self.assertTrue(result["summary"]["resolution_eligible"])
        self.assertEqual(result["resolution_candidate"], "TOKEN_VAZIO_EXTERNAL_SETTINGS")
        self.assertIsNone(result["resolved_token"])
        self.assertFalse(result["claim_allowed"])
        self.assertNotIn("opaque", str(result))

    def test_protected_branch_detail_denied_remains_partial(self):
        def fetcher(url, token):
            if url.endswith("/rulesets?includes_parents=true"):
                return 200, []
            if url.endswith("/protection"):
                return 403, {"message": "Resource not accessible by integration"}
            return 200, {"protected": True}
        result = build("org/repo", token="opaque", fetcher=fetcher)
        self.assertEqual(result["state"], "PARTIAL_EXTERNAL_SETTINGS_OBSERVED")
        self.assertFalse(result["summary"]["protection_detail_complete"])
        self.assertFalse(result["summary"]["resolution_eligible"])
        self.assertIsNone(result["resolution_candidate"])

    def test_unprotected_branch_does_not_require_protection_endpoint_200(self):
        def fetcher(url, token):
            if url.endswith("/rulesets?includes_parents=true"):
                return 200, []
            if url.endswith("/protection"):
                return 404, {"message": "Branch not protected"}
            return 200, {"protected": False}
        result = build("org/repo", fetcher=fetcher)
        self.assertTrue(result["summary"]["resolution_eligible"])
        self.assertTrue(all(row["detail_complete"] for row in result["branches"]))

    def test_ruleset_denial_blocks_resolution_even_when_branch_details_exist(self):
        def fetcher(url, token):
            if url.endswith("/rulesets?includes_parents=true"):
                return 403, {"message": "denied"}
            if url.endswith("/protection"):
                return 200, {}
            return 200, {"protected": True}
        result = build("org/repo", fetcher=fetcher)
        self.assertFalse(result["summary"]["rulesets_observed"])
        self.assertFalse(result["summary"]["resolution_eligible"])


if __name__ == "__main__":
    unittest.main()
