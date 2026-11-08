"""Structural fault injection; manual semantic tags are NOT text understanding."""
import copy
import importlib.util
import json
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location("multilingual",ROOT/"tools/ci/rll_multilingual_compression_v1.py")
mod=importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(mod)

class MultilingualCompression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc=json.loads((ROOT/"data/contracts/rll_multilingual_semantic_compression_trial.v1.json").read_text(encoding="utf-8"))
    def test_baseline_four_languages(self):
        r=mod.assess(self.doc)
        self.assertEqual(r["state"],"PASS_SCOPED_MANUAL_ANNOTATIONS")
        self.assertEqual((len(r["languages"]),r["records"]),(4,4))
    def test_lossless_roundtrip(self):
        self.assertEqual(len(mod.assess(self.doc)["per_language"]),4)
    def test_no_automatic_semantic_claim(self):
        r=mod.assess(self.doc)
        self.assertFalse(r["claim_allowed"])
        self.assertEqual(r["automatic_semantic_extraction"],"NOT_RUN")
        self.assertEqual(r["bayesian_posterior"],"TOKEN_VAZIO")
    def test_flip_negation_detected(self):
        x=copy.deepcopy(self.doc)
        x["records"][2]["translations"]["es"]["annotated_atoms"]["claim"]="demonstrated"
        self.assertEqual(mod.assess(x)["state"],"BLOCKED_ANNOTATED_FACT_MISMATCH")
    def test_vacuum_to_air_detected(self):
        x=copy.deepcopy(self.doc)
        x["records"][0]["translations"]["fr"]["annotated_atoms"]["condition"]="ambient_air"
        self.assertEqual(mod.assess(x)["state"],"BLOCKED_ANNOTATED_FACT_MISMATCH")
    def test_year_mismatch_detected(self):
        x=copy.deepcopy(self.doc)
        x["records"][0]["translations"]["en"]["annotated_atoms"]["study_year"]="2018"
        self.assertEqual(mod.assess(x)["state"],"BLOCKED_ANNOTATED_FACT_MISMATCH")
    def test_order_does_not_change_annotated_fidelity(self):
        x=copy.deepcopy(self.doc)
        x["records"].reverse()
        self.assertEqual(mod.assess(self.doc)["worst_annotated_recall"],
                         mod.assess(x)["worst_annotated_recall"])
    def test_repetition_changes_bytes_not_facts(self):
        x=copy.deepcopy(self.doc)
        b=mod.assess(x)
        for r in x["records"]:
            r["translations"]["pt"]["text"]+=" repetição"*400
        a=mod.assess(x)
        self.assertGreater(a["per_language"]["pt"]["fraction_saved"],
                           b["per_language"]["pt"]["fraction_saved"])
        self.assertEqual(a["worst_annotated_recall"],b["worst_annotated_recall"])
    def test_missing_language_fails(self):
        x=copy.deepcopy(self.doc)
        del x["records"][0]["translations"]["fr"]
        with self.assertRaises(ValueError):mod.assess(x)
    def test_source_provenance_cannot_be_promoted(self):
        x=copy.deepcopy(self.doc)
        x["translation_source"]="INDEPENDENT_REPLICATION"
        with self.assertRaises(ValueError):mod.assess(x)
    def test_annotated_fact_is_not_experimental_replication(self):
        r=mod.assess(self.doc)
        self.assertEqual(r["independent_scientific_replication"],"NOT_RUN")
    def test_output_of_short_string_may_expand(self):
        result=mod.compress("a")
        self.assertGreater(result["bytes_zlib"],result["bytes_original"])

if __name__=="__main__":
    unittest.main()
