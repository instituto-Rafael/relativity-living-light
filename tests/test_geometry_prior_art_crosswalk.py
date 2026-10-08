"""Unit tests for scoped geometric-prior-art chronology. No external dependencies."""
import copy
import json
import pathlib
import unittest
from tools.validate_geometry_prior_art_crosswalk import validate

ROOT = pathlib.Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/governance/RLL_GEOMETRY_PRIOR_ART_CROSSWALK_20261008_V1.json"

class PriorArtChronologyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_expected_chronology_and_claim_boundary(self):
        result = validate(self.source)
        self.assertEqual(result["validation_state"], "PASS_SCOPED_CHRONOLOGY_ONLY")
        self.assertEqual([x["chronology"] for x in result["papers"]],
                         ["USER_TOKEN_BEFORE_PAPER", "PAPER_BEFORE_USER_TOKEN"])
        self.assertFalse(result["claim_allowed"])
        self.assertFalse(result["publication_ready"])

    def test_wrong_chronology_fails_closed(self):
        x = copy.deepcopy(self.source)
        x["papers"][0]["chronology"] = "PAPER_BEFORE_USER_TOKEN"
        with self.assertRaises(ValueError):
            validate(x)

    def test_raw_private_content_fails_closed(self):
        x = copy.deepcopy(self.source)
        x["private_excerpt"] = "must never be public"
        with self.assertRaises(ValueError):
            validate(x)

    def test_false_publication_promotion_fails_closed(self):
        x = copy.deepcopy(self.source)
        x["publication_ready"] = True
        with self.assertRaises(ValueError):
            validate(x)

if __name__ == "__main__":
    unittest.main()
