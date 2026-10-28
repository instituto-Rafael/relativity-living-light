"""RLL typed chemistry context: adversarial and reversible source guard.

These tests do NOT measure chemistry, CMB spectra or transformer internals.
"""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/"data/governance/RLL_TYPED_CHEM_WATER_SESSION_TOKENS_V1.json"
SCRIPT=ROOT/"tools/rll_chem_context_tokenizer.py"

def call(*extra):
    out=subprocess.run([sys.executable,"-B",str(SCRIPT),"--manifest",str(MANIFEST),*extra],
                       capture_output=True,text=True,check=False,timeout=12)
    return out, json.loads(out.stdout)

class TypedChemistryContext(unittest.TestCase):
    def test_15_mutations_and_8_context_checks(self):
        process,receipt=call("--self-test")
        self.assertEqual(process.returncode,0,process.stderr)
        self.assertEqual(receipt["negative_mutations"],15)
        self.assertEqual(receipt["resolver_tests"],8)
        self.assertEqual(receipt["status"],"PASS_SCOPED_METADATA_ONLY")
        self.assertFalse(receipt["claim_allowed"])
        self.assertEqual(receipt["physical_validation"],"NOT_RUN")
        self.assertEqual(receipt["hidden_model_heads"],"NOT_ACCESSIBLE")

    def test_chemical_isotope_and_model_head_distinctions(self):
        examples={
          "H3":"TOKEN_VAZIO_AMBIGUOUS",
          "He3":"TOKEN_VAZIO_AMBIGUOUS",
          "He2":"TOKEN_VAZIO_AMBIGUOUS",
          "head":"TOKEN_VAZIO_AMBIGUOUS",
          "H2O3":"RESOLVED_TYPED_REFERENCE",
          "H2O":"RESOLVED_TYPED_REFERENCE",
          "O3":"RESOLVED_TYPED_REFERENCE",
          "C3":"RESOLVED_TYPED_REFERENCE",
          "C3+":"RESOLVED_TYPED_REFERENCE",
          "³He":"RESOLVED_TYPED_REFERENCE",
          "empty-physics-token":"TOKEN_VAZIO_UNKNOWN",
        }
        for token,state in examples.items():
            with self.subTest(surface=token):
                r, receipt = call("--token",token)
                self.assertEqual(r.returncode,0,r.stderr)
                self.assertEqual(receipt["resolution"]["status"],state)
                self.assertEqual(receipt["resolution"]["raw"],token)
                self.assertFalse(receipt["resolution"]["claim_allowed"])
        r,receipt=call("--token","He3","--kind","isotope")
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertEqual(receipt["resolution"]["candidates"][0]["id"],"nuclear:isotope:He-3")
        r,receipt=call("--token","C3","--canonical-id","chem:ion:C+3")
        self.assertEqual(receipt["resolution"]["status"],"TOKEN_VAZIO_CONTEXT_CONTRADICTORY")

    def test_full_manifest_requires_provenance_and_protects_molecules(self):
        m=json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(len(m["invariant_of_invariants"]),14)
        self.assertFalse(m["raw_conversation_dump_materialized"])
        self.assertFalse(m["model_hidden_attention_heads_accessible"])
        c={record["surface"]:record["candidates"] for record in m["surface_records"]}
        self.assertEqual(c["H2O"][0]["stoichiometry"],{"H":2,"O":1})
        self.assertEqual(c["H2O3"][0]["stoichiometry"],{"H":2,"O":3})
        self.assertEqual(c["HO3"][0]["stoichiometry"],{"H":1,"O":3})
        self.assertNotEqual(c["C3"][0]["id"],c["C3+"][0]["id"])

    def test_structured_hold_on_null_manifest(self):
        with tempfile.TemporaryDirectory(prefix="rll_chem_token_") as tmp:
            path=Path(tmp)/"null.json"
            path.write_text("null\n",encoding="utf-8")
            out=subprocess.run([sys.executable,"-B",str(SCRIPT),"--manifest",str(path)],
                               capture_output=True,text=True,check=False,timeout=12)
            self.assertEqual(out.returncode,2,out.stderr)
            receipt=json.loads(out.stdout)
            self.assertEqual(receipt["status"],"HOLD_INVALID")
            self.assertIn("manifest_not_an_object",receipt["validation_errors"])
            self.assertFalse(receipt["claim_allowed"])

if __name__=="__main__":
    unittest.main()
