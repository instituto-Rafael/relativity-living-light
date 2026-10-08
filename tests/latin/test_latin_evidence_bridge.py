import copy
import json
import unittest
from pathlib import Path
from scripts.latin.validate_latin_evidence_bridge import validate

ROOT=Path(__file__).resolve().parents[2]
BASE=json.loads((ROOT/"data/governance/latin-evidence-bridge.v1.json").read_text())

class TestLatinEvidenceBoundary(unittest.TestCase):
    def test_scope(self):
        self.assertEqual(validate(BASE)["state"],"PASS_EVIDENCE_BOUNDARY_STRUCTURE_ONLY")
    def test_science_promotion_denied(self):
        o=copy.deepcopy(BASE);o["claim_allowed"]=True
        with self.assertRaises(ValueError):validate(o)
    def test_bypass_admin_denied(self):
        o=copy.deepcopy(BASE);o["secrets_boundary"]["administration_called"]=True
        with self.assertRaises(ValueError):validate(o)
    def test_unpinned_source_denied(self):
        o=copy.deepcopy(BASE);o["source_producers"]["graph"]["commit"]="main"
        with self.assertRaises(ValueError):validate(o)
    def test_missing_falsifier_denied(self):
        o=copy.deepcopy(BASE);o["outstanding_gates"].pop("independent_rll_falsifier")
        with self.assertRaises(ValueError):validate(o)
    def test_fake_gate_pass_denied(self):
        o=copy.deepcopy(BASE);o["outstanding_gates"]["human_approval"]="PASS"
        with self.assertRaises(ValueError):validate(o)

if __name__=="__main__":unittest.main()
