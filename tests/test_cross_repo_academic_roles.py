import json
import unittest
from pathlib import Path


class CrossRepoAcademicRolesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = Path(__file__).resolve().parents[1] / "configs" / "cross_repo_academic_roles.v1.json"
        cls.data = json.loads(path.read_text(encoding="utf-8"))

    def test_single_scientific_authority(self):
        self.assertEqual(self.data["scientific_authority"], "instituto-Rafael/relativity-living-light")
        self.assertFalse(self.data["claim_allowed"])

    def test_exact_three_supporting_repositories(self):
        repositories = {item["repository"] for item in self.data["repositories"]}
        self.assertEqual(repositories, {"rafaelmeloreisnovo/GAIA_phi", "rafaelmeloreisnovo/ZIPRAF_OMEGA_FULL", "rafaelmeloreisnovo/Rafaelia_Private"})

    def test_no_blockchain_overclaim(self):
        boundary = self.data["ledger_boundary"]
        self.assertTrue(boundary["hash_chain"])
        self.assertFalse(boundary["blockchain_consensus"])
        self.assertEqual(len(boundary["triple_digest_profiles"]), 3)

    def test_promotion_gate_is_substantial(self):
        self.assertGreaterEqual(len(self.data["promotion_gate"]), 10)
        self.assertIn("independent_reproduction", self.data["promotion_gate"])
        self.assertIn("human_review", self.data["promotion_gate"])

    def test_proposed_heads_are_pinned(self):
        for item in self.data["repositories"]:
            self.assertEqual(len(item["base_commit"]), 40)
            self.assertEqual(len(item["proposed_head"]), 40)
            self.assertIn("/pull/", item["pull_request"])


if __name__ == "__main__":
    unittest.main()
