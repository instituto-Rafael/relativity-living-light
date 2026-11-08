"""Fail-closed structural tests: science headlines metadata ONLY, never a physics gate."""
import json
from pathlib import Path
import unittest
import unicodedata

M = Path(__file__).resolve().parents[1] / "NOVOexport/SCIENCEX_ATLAS/20261107/news_titles_routes_v3.json"

def key(title):
    return " ".join(unicodedata.normalize("NFKC", title).casefold().split())

class ScienceXCatalogV3(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = json.loads(M.read_text(encoding="utf-8"))
        cls.rows = cls.m["news"]

    def test_counts_and_deduplication(self):
        c = self.m["counts"]
        self.assertEqual((c["snapshot_cards"], c["snapshot_unique"], c["snapshot_duplicates"]), (276, 268, 8))
        self.assertEqual((c["unique_paste_additions"], c["unique_previous20_only"], c["unique_total"]), (87, 9, 364))
        self.assertEqual(len(self.rows), 364)
        self.assertEqual(len({key(r["title"]) for r in self.rows}), 364)
        self.assertEqual(len({r["uid"] for r in self.rows}), 364)

    def test_source_and_route_types(self):
        for row in self.rows:
            self.assertTrue(row["sources"])
            self.assertTrue(row["outlet"])
            self.assertTrue(row["title"].strip())
            self.assertTrue(row["category_suggestion"])
            self.assertIn(row["evidence_type"], {"NEWS_HEADLINE_AND_EXCERPT", "USER_PASTED_HEADLINE_ONLY", "PRIOR_NEWS_CATALOG"})
            if row["news_url"] is not None:
                self.assertTrue(row["news_url"].startswith("https://phys.org/news/"))

    def test_no_claim_promotion_or_private_excerpts(self):
        c = self.m["epistemic_contract"]
        self.assertIs(c["claim_allowed"], False)
        self.assertEqual(c["physical_validation"], "NOT_RUN")
        self.assertEqual(c["urls_for_paste_only"], "TOKEN_VAZIO_UNRESOLVED")
        self.assertFalse(any("excerpt_as_captured" in row for row in self.rows))
        self.assertFalse(any("document_id" in row for row in self.rows))

    def test_adversarial_paper_anchors(self):
        ids = {p["arxiv"] for p in self.m["papers"]}
        self.assertTrue({"2604.21895", "2507.19588", "2610.00685", "2610.00663", "2603.13461"} <= ids)

if __name__ == "__main__":
    unittest.main()
