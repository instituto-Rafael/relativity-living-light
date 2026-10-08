import copy
import json
import unittest
from pathlib import Path
from scripts.latin.validate_latin_evidence_bridge import validate

ROOT=Path(__file__).resolve().parents[2]
BASE=json.loads((ROOT/"data/governance/latin-evidence-bridge.v1.json").read_text())

class TestLatinEvidenceBoundary(unittest.TestCase):
    def test_documented_pins_match_current_contract(self):
        doc = (ROOT / "docs/governance/LATIN_555_EVIDENCE_BRIDGE_V1.md").read_text(encoding="utf-8")
        self.assertIn(BASE["source_producers"]["graph"]["commit"], doc)
        self.assertIn(BASE["source_producers"]["governance"]["commit"], doc)

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

    def test_cannot_promote_source_class_or_relations(self):
        for field, value in (
            ("source_class", "SCIENTIFIC_EVIDENCE"),
            ("admissible_relation_types", ["PROVED_ISOMORPHISM"]),
            ("forbidden_claims", []),
        ):
            with self.subTest(field=field):
                o = copy.deepcopy(BASE); o[field] = value
                with self.assertRaises(ValueError): validate(o)

    def test_must_pin_complete_producer_locator(self):
        for change in ({"commit": "0" * 40}, {"path": ""},
                       {"workflow": "../invalid.yml"}, {"repo": "foreign/repo"}):
            with self.subTest(change=change):
                o = copy.deepcopy(BASE)
                o["source_producers"]["graph"].update(change)
                with self.assertRaises(ValueError): validate(o)

    def test_no_credential_boundary_escalation(self):
        for key in ("GITPAT", "CLIMA", "PAT_ENV", "K_SECRETS"):
            with self.subTest(key=key):
                o = copy.deepcopy(BASE)
                o["secrets_boundary"][key] = "ADMIN"
                with self.assertRaises(ValueError): validate(o)

    def test_replay_is_fail_fast(self):
        o = copy.deepcopy(BASE)
        self.assertIn(" && ", o["replay"])
        o["replay"] = o["replay"].replace(" && ", "; ")
        with self.assertRaises(ValueError): validate(o)

    def test_missing_claim_field_not_silently_accepted(self):
        o = copy.deepcopy(BASE)
        o.pop("forbidden_claims")
        with self.assertRaises(ValueError): validate(o)

    def test_traceability_index_routes_to_bridge(self):
        trace = (ROOT / "docs/RLL_TRACEABILITY_MAP.md").read_text(encoding="utf-8")
        self.assertIn("LATIN_555_EVIDENCE_BRIDGE_V1.md", trace)

if __name__=="__main__":unittest.main()
