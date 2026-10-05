import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/governance/RLL_CAPABILITY_SECRET_ROUTER_V1.json"
WORKFLOW = ROOT / ".github/workflows/rll-authorial-science-fabric-v1.yml"


class TestRllCapabilitySecretRouter(unittest.TestCase):
    def setUp(self):
        self.policy = json.loads(POLICY.read_text(encoding="utf-8"))
        self.workflow = WORKFLOW.read_text(encoding="utf-8")

    def test_canonical_profiles_and_legacy_alias(self):
        profiles = self.policy["profiles"]
        self.assertEqual(profiles["pat_actions"]["canonical_secret_name"], "PAT_ACTIONS")
        self.assertEqual(profiles["pat_agents"]["canonical_secret_name"], "PAT_AGENTS")
        self.assertEqual(profiles["pat_env"]["canonical_secret_name"], "PAT_ENV")
        self.assertEqual(
            profiles["pat_environments"]["canonical_secret_name"],
            "PAT_ENVIRONMENTS",
        )
        self.assertEqual(
            profiles["pat_environments"]["legacy_aliases"],
            ["PAT_ENVIOREMENTS"],
        )

    def test_secret_references_are_explicit(self):
        for name in [
            "PAT_ACTIONS",
            "PAT_AGENTS",
            "PAT_ENV",
            "PAT_ENVIRONMENTS",
            "PAT_ENVIOREMENTS",
        ]:
            self.assertIn(f"secrets.{name}", self.workflow)

    def test_secret_consumption_is_manual_only(self):
        self.assertNotIn("pull_request_target", self.workflow)
        self.assertIn("github.event_name == 'workflow_dispatch'", self.workflow)
        self.assertEqual(
            self.policy["workflow_boundary"]["allowed_event_for_secret_consumption"],
            "workflow_dispatch_only",
        )

    def test_no_remote_mutation_or_secret_dump(self):
        forbidden = [
            r"\bgit\s+push\b",
            r"\bprintenv\b",
            r"\bset\s+-x\b",
            r"(?:-X|--request|--method)\s*(?:POST|PUT|PATCH|DELETE)\b",
        ]
        for pattern in forbidden:
            self.assertIsNone(re.search(pattern, self.workflow, re.IGNORECASE))

    def test_value_equivalence_is_not_claimed(self):
        self.assertEqual(
            self.policy["same_value_across_names"],
            "TOKEN_VAZIO_EXTERNAL_SETTING_NOT_TESTED",
        )
        self.assertFalse(self.policy["claim_allowed"])


if __name__ == "__main__":
    unittest.main()
