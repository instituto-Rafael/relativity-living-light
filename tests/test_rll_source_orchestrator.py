"""Offline tests for Nature+Zenodo intake. No network, no external dependencies."""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import rll_source_orchestrator as src

CROSSREF = {"message": {"items": [
    {"DOI": "10.1234/EXAMPLE", "title": ["Research topic"],
     "author": [{"given": "A", "family": "Researcher"}],
     "published": {"date-parts": [[2026, 3, 1]]}, "container-title": ["Nature"],
     "license": [{"URL": "https://creativecommons.org/licenses/by/4.0/"}]},
    {"title": ["Missing DOI should be ignored"]},
]}}
ZENODO = {"hits": {"hits": [
    {"id": 12345, "doi": "https://doi.org/10.1234/example",
     "metadata": {"title": "Research topic", "creators": [{"name": "A Researcher"}],
                  "license": {"id": "cc-by-4.0"}, "publication_date": "2026-03-01"}},
    {"id": 12346, "metadata": {"title": "Dataset without DOI",
                               "license": {"id": "cc0-1.0"}}},
]}}


class Sources(unittest.TestCase):
    def test_normalization_and_records(self):
        r = src.crossref_records(CROSSREF, "nature")
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0]["doi"], "10.1234/example")
        self.assertEqual(r[0]["published"], "2026-03-01")
        self.assertFalse(r[0]["content_downloaded"])
        z = src.zenodo_records(ZENODO)
        self.assertEqual(len(z), 2)
        self.assertEqual(z[1]["doi"], None)

    def test_dedup_and_lineage(self):
        def fixture(url):
            return ZENODO if "zenodo.org" in url else CROSSREF
        result = src.collect("cosmology", 5, ["nature"], fixture, "2026-11-04T00:00:00Z")
        self.assertEqual(result["total_unique"], 2)
        self.assertTrue(result["all_sources_observed"])
        common = [r for r in result["records"] if r["doi"] == "10.1234/example"][0]
        self.assertEqual(len(common["observations"]), 2)
        self.assertTrue(common["cross_source_identity"])
        self.assertFalse(common["claim_allowed"])
        self.assertFalse(result["scientific_validation"])
        self.assertEqual([r for r in result["records"] if r["doi"] is None][0]["key"], "zenodo:12346")

    def test_bounded_inputs_and_no_network(self):
        for q in ("x", "a/b", " ", "p" * 81):
            with self.assertRaises(ValueError):
                src.endpoints(q, 5, ["nature"])
        for lim in (0, 21):
            with self.assertRaises(ValueError):
                src.endpoints("cosmology", lim, ["nature"])
        with self.assertRaises(ValueError):
            src.endpoints("cosmology", 2, ["other"])
        with self.assertRaises(ValueError):
            src.get_json("https://example.org/data")
        self.assertEqual(len(src.endpoints("cosmology", 5, ["nature", "nature-communications"])), 3)

    def test_partial_failure_is_visible(self):
        def fail_one(url):
            if "zenodo" in url:
                raise OSError("fixture offline")
            return CROSSREF
        out = src.collect("cosmology", 2, ["nature"], fail_one, "2026-11-04T00:00:00Z")
        self.assertFalse(out["all_sources_observed"])
        self.assertEqual(out["provider_status"]["zenodo"]["status"], "TOKEN_VAZIO")
        self.assertEqual(out["total_unique"], 1)
        self.assertFalse(out["claim_allowed"])

    def test_stable_fingerprint(self):
        self.assertEqual(src.sha256({"a": 1, "b": 2}), src.sha256({"b": 2, "a": 1}))
        self.assertIsNone(src.doi_key("not-doi"))


if __name__ == "__main__":
    unittest.main()
