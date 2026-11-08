"""A true six-type taxonomy is not an evidential staircase."""
from __future__ import annotations
import copy
import importlib.util
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FILE=ROOT/"tools/ci/rll_epistemic_taxonomy_gate_v2.py"
S=importlib.util.spec_from_file_location("rll_taxonomy_v2",FILE)
gate=importlib.util.module_from_spec(S)
assert S and S.loader
S.loader.exec_module(gate)


class SixTypesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec=gate.load(gate.TAX)
        cls.graph=gate.load(gate.V1)
        cls.states=gate.load(gate.STATES)

    def result(self,spec):
        return gate.validate(spec,self.graph,self.states,check_source_hash=False)

    def case(self,spec,name):
        return next(x for x in spec["case_bindings"] if x["id"]==name)

    def expect(self,spec,error):
        v=self.result(spec)
        self.assertTrue(any(error in e for e in v["errors"]),v)

    def test_exact_source_git_hashes_and_schema(self):
        r=gate.validate(self.spec,self.graph,self.states)
        self.assertEqual(r["status"],"PASS_SCOPED_TAXONOMY_ONLY")
        self.assertEqual((r["classes"],r["mapped_cases"],r["typed_relations"]),(6,5,6))
        self.assertFalse(r["claim_allowed"])

    def test_nonordinal_six_types_and_unknown_not_seventh(self):
        self.assertEqual(set(t["id"] for t in self.spec["types"]),set(gate.SIX))
        self.assertTrue(all(t["ordinal"] is None for t in self.spec["types"]))
        self.assertNotIn(gate.UNKNOWN,gate.SIX)

    def test_formal_theorem_not_empirical_law(self):
        x=copy.deepcopy(self.spec)
        self.case(x,"EUCLIDEAN_DIAGONAL")["type"]="EMPIRICAL_LAW"
        self.expect(x,"MATH_THEOREM_CAST_AS_EMPIRICAL_LAW")

    def test_reference_not_law_or_theory(self):
        x=copy.deepcopy(self.spec)
        self.case(x,"MITO_ATP")["type"]="SCIENTIFIC_THEORY"
        self.expect(x,"REFERENCE_FALSELY_ELEVATED_TO_LAW_OR_THEORY")

    def test_bio_xray_not_testable_without_observable(self):
        x=copy.deepcopy(self.spec)
        self.case(x,"TRIBO_XRAY_CELL")["type"]="SCIENTIFIC_HYPOTHESIS"
        self.expect(x,"UNTYPED_EXPLORATION_FALSELY_TESTABLE")

    def test_bio_xray_must_not_be_verified(self):
        x=copy.deepcopy(self.spec)
        self.case(x,"TRIBO_XRAY_CELL")["evidence_state"]="VERIFIED_REPRODUCIBLE"
        self.expect(x,"SPECULATIVE_BIOLOGY_FALSELY_VERIFIED")

    def test_lcdm_not_automatically_scientific_theory_in_local_map(self):
        x=copy.deepcopy(self.spec)
        self.case(x,"LCDM_BACKGROUND")["type"]="SCIENTIFIC_THEORY"
        self.expect(x,"COSMOLOGICAL_MODEL_FALSELY_PROMOTED_TO_THEORY")

    def test_reject_unregistered_evidence_state(self):
        x=copy.deepcopy(self.spec)
        self.case(x,"RLL_BACKGROUND")["evidence_state"]="I_THINK_IT_WORKS"
        self.expect(x,"UNDECLARED_EVIDENCE_STATE")

    def test_no_auto_claim_promotion(self):
        x=copy.deepcopy(self.spec)
        x["claim_allowed"]=True
        self.expect(x,"CLAIM_BOUNDARY_BROKEN")

    def test_relations_never_imply_truth(self):
        x=copy.deepcopy(self.spec)
        x["type_relations"][0]["implies_validity"]=True
        self.expect(x,"RELATION_AS_IMPLICIT_SCIENTIFIC_PROMOTION")

    def test_missing_source_case_fails(self):
        x=copy.deepcopy(self.spec)
        x["case_bindings"].pop()
        self.expect(x,"CASE_MAPPING_INCOMPLETE")

    def test_verified_state_requires_receipt_review(self):
        x=copy.deepcopy(self.spec)
        self.case(x,"RLL_BACKGROUND")["evidence_state"]="VERIFIED_LIMITED"
        self.expect(x,"CLAIMED_VERIFIED_WITHOUT_BINDING_AND_REVIEW")

    def test_promotion_without_receipt_blocks(self):
        x=self.case(self.spec,"RLL_BACKGROUND")
        self.assertTrue(gate.promotion_readiness(self.spec,x,"VERIFIED_LIMITED",{}).startswith("BLOCKED_TOKEN_VAZIO"))

    def test_promotion_bad_hash_blocks(self):
        x=self.case(self.spec,"EUCLIDEAN_DIAGONAL")
        receipt={key:("bad" if key.endswith("_sha256") else "reviewed")
                 for key in self.spec["promotion_policy"]["required_provenance"]+
                            self.spec["promotion_policy"]["evidence_requirements"][x["type"]]}
        receipt["reviewer_verified"]=True
        receipt["source_verified"]=True
        self.assertIn("BLOCKED_INVALID_SHA256",gate.promotion_readiness(self.spec,x,"VERIFIED_LIMITED",receipt))

    def test_even_full_receipt_only_ready_for_manual_review(self):
        x=self.case(self.spec,"EUCLIDEAN_DIAGONAL")
        fields=self.spec["promotion_policy"]["required_provenance"]+self.spec["promotion_policy"]["evidence_requirements"][x["type"]]
        receipt={k:("a"*64 if k.endswith("_sha256") else "reviewed") for k in fields}
        receipt["reviewer_verified"]=True
        receipt["source_verified"]=True
        self.assertEqual(gate.promotion_readiness(self.spec,x,"VERIFIED_LIMITED",receipt),
                         "READY_FOR_HUMAN_REVIEW_NOT_A_CLAIM_OR_STATUS_MUTATION")

    def test_reproducible_requires_independent_replication(self):
        x=self.case(self.spec,"EUCLIDEAN_DIAGONAL")
        fields=self.spec["promotion_policy"]["required_provenance"]+self.spec["promotion_policy"]["evidence_requirements"][x["type"]]+["independent_replication_sha256"]
        receipt={k:("a"*64 if k.endswith("_sha256") else "reviewed") for k in fields}
        receipt["reviewer_verified"]=True
        receipt["source_verified"]=True
        self.assertIn("BLOCKED_REPLICATION_INDEPENDENCE_NOT_VERIFIED",
                      gate.promotion_readiness(self.spec,x,"VERIFIED_REPRODUCIBLE",receipt))

    def test_matrix_preserves_all_cases_and_zero_claims(self):
        m=gate.compose_matrix(self.spec)
        self.assertEqual(len(m),5)
        self.assertTrue(all(not x["claim_allowed"] and not x["ready_for_scientific_promotion"] for x in m))
        self.assertEqual(next(x for x in m if x["id"]=="MITO_ATP")["epistemic_type"],gate.UNKNOWN)

    def test_model_cannot_be_labeled_proven_from_ci(self):
        x=copy.deepcopy(self.spec)
        x["promotion_policy"]["effect"]="AUTOMATIC_VERIFIED"
        self.expect(x,"PROMOTION_POLICY_NOT_FAIL_CLOSED")

    def test_type_enum_is_complete(self):
        x=copy.deepcopy(self.spec)
        x["types"].pop()
        self.expect(x,"SIX_TYPE_SET_MISMATCH")


if __name__=="__main__":
    unittest.main()
