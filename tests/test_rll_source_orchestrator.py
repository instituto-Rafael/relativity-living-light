"""Offline tests for Nature+Zenodo intake. No network, no external dependencies."""
import hashlib
import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

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

    def test_doi_suffix_punctuation_is_identity(self):
        dois = ["10.1234/topic" + ending for ending in ("", ".", ",", ";")]
        rows = src.crossref_records({"message": {"items": [{"DOI": d} for d in dois]}}, "nature")
        self.assertEqual([r["record_url"] for r in rows], ["https://doi.org/" + d for d in dois])
        rows += src.zenodo_records({"hits": {"hits": [
            {"id": 7, "doi": "https://doi.org/10.1234/TOPIC."}
        ]}})
        merged = {r["doi"]: r for r in src.merge(rows)}
        self.assertEqual(set(merged), set(dois))
        self.assertEqual(len(merged[dois[1]]["observations"]), 2)
        self.assertTrue(merged[dois[1]]["cross_source_identity"])

    def read_outputs(self, path):
        data = path.read_bytes()
        catalog = json.loads(data)
        receipt = json.loads((path.parent / "receipt.json").read_bytes())
        self.assertEqual(receipt["catalog_sha256"], hashlib.sha256(data).hexdigest())
        for output in (catalog, receipt):
            self.assertFalse(output["all_sources_observed"])
            self.assertFalse(output["claim_allowed"])
        return catalog

    def test_invalid_envelope_writes_partial_catalog_and_receipt(self):
        for invalid in (None, [], "unexpected"):
            for failed, healthy, responses, expected in (
                ("crossref:nature", "zenodo", [{"message": invalid}, ZENODO], 2),
                ("zenodo", "crossref:nature", [CROSSREF, {"hits": invalid}], 1),
            ):
                with self.subTest(failed=failed, invalid=invalid), TemporaryDirectory() as tmp:
                    path = Path(tmp) / "catalog.json"
                    with patch.object(src, "get_json", side_effect=responses):
                        code = src.main(["--mode", "live", "--journal", "nature", "--output", str(path)])
                    self.assertEqual(code, 2)
                    catalog = self.read_outputs(path)
                    status = catalog["provider_status"]
                    self.assertEqual(status[failed]["status"], "TOKEN_VAZIO")
                    self.assertEqual(status[failed]["error_type"], "ValueError")
                    self.assertEqual(status[healthy]["status"], "OBSERVED")
                    self.assertEqual(catalog["total_unique"], expected)

    def test_malformed_nested_creator_writes_partial_receipt(self):
        malformed = {"hits": {"hits": [
            {"id": 12347, "metadata": {"creators": [
                {"person_or_org": "invalid-nested-object"}]}}
        ]}}
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "catalog.json"
            with patch.object(src, "get_json", side_effect=[CROSSREF, malformed]):
                code = src.main(["--mode", "live", "--journal", "nature",
                                 "--output", str(path)])
            self.assertEqual(code, 2)
            catalog = self.read_outputs(path)
            self.assertEqual(catalog["provider_status"]["zenodo"]["status"], "TOKEN_VAZIO")
            self.assertEqual(catalog["provider_status"]["zenodo"]["error_type"], "ValueError")
            self.assertEqual(catalog["provider_status"]["crossref:nature"]["status"], "OBSERVED")
            self.assertEqual(catalog["total_unique"], 1)
            self.assertFalse(catalog["claim_allowed"])

    def test_default_offline_writes_receipt_without_fetch(self):
        with TemporaryDirectory() as tmp, patch.object(src, "get_json") as fetch:
            path = Path(tmp) / "catalog.json"
            self.assertEqual(src.main(["--output", str(path)]), 0)
            fetch.assert_not_called()
            catalog = self.read_outputs(path)
            self.assertEqual(catalog["mode"], "OFFLINE_CONTRACT_TEST")
            self.assertEqual(catalog["records"], [])
            self.assertEqual({v["status"] for v in catalog["provider_status"].values()}, {"NOT_RUN"})

    def test_stable_fingerprint(self):
        self.assertEqual(src.sha256({"a": 1, "b": 2}), src.sha256({"b": 2, "a": 1}))
        self.assertIsNone(src.doi_key("not-doi"))


if __name__ == "__main__":
    unittest.main()
