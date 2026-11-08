"""Fail-closed structural checks for the 20 user-supplied news records.

Not a physical/cosmological model validation.
Run: python -m unittest tests/test_ccc_tl_news_manifest.py
"""
import json
from pathlib import Path
import unittest

MANIFEST = (Path(__file__).resolve().parents[1] /
            "NOVOexport/CCC_TL_RLL/20261107/news_manifest_v2.json")

class NewsCatalogIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(MANIFEST.read_text(encoding="utf-8"))
        cls.articles = cls.data["articles"]

    def test_exact_count_and_integrity(self):
        self.assertEqual(self.data["record_count"], 20)
        self.assertEqual(len(self.articles), 20)
        self.assertEqual([a["id"] for a in self.articles],
                         [f"N{i:02d}" for i in range(1, 21)])
        self.assertEqual(len({a["news_url"] for a in self.articles}), 20)

    def test_sources_and_dates(self):
        for a in self.articles:
            self.assertTrue(a["news_url"].startswith("https://phys.org/"))
            self.assertLessEqual(a["date"], self.data["reference_date"])
            self.assertTrue(a["headline"].strip())
            self.assertTrue(a["role"].strip())
            self.assertTrue(a["caveat"].strip())

    def test_no_scientific_claim_promotion(self):
        self.assertIs(self.data["claim_allowed"], False)
        for a in self.articles:
            self.assertIs(a["physical_claim_supported"], False)
            self.assertIs(a["primary_fulltext_reproduced"], False)

    def test_adversarial_and_orthogonal_retained(self):
        roles = {a["role"] for a in self.articles}
        self.assertIn("ADVERSARIAL_SPT", roles)
        self.assertIn("DISTINCT_LIEU_MODEL", roles)
        self.assertIn("AUTHOR_COMMENTARY", roles)
        self.assertEqual(sum(a["role"] == "METODOLOGIA" for a in self.articles), 5)

if __name__ == "__main__":
    unittest.main()
