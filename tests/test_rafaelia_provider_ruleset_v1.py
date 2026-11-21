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

if __name__ == "__main__":
    unittest.main()
