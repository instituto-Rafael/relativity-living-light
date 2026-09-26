from __future__ import annotations
import copy
import unittest
from tools.validate_rll_section_retrofeedback import CONTRACT, ATLAS, load, receipt, validate

class SectionRetrofeedbackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract=load(CONTRACT)
        cls.atlas=load(ATLAS)

    def test_current_atlas_valid_and_fail_closed(self):
        errors=validate(self.contract,self.atlas)
        self.assertEqual(errors,[])
        r=receipt(self.contract,self.atlas,errors)
        self.assertTrue(r["valid"])
        self.assertFalse(r["claim_allowed"])
        self.assertEqual(r["authorized_promotion_count"],0)
        self.assertEqual(r["epistemic_evolution_count"],1)

    def test_fail_can_evolve_only_when_uncertainty_reduced(self):
        a=copy.deepcopy(self.atlas)
        ev=a["events"][0]
        ev["§INCERTEZA_DEPOIS"]["direction"]="UNCHANGED"
        errors=validate(self.contract,a)
        self.assertTrue(any("negative outcome can be epistemic evolution" in x for x in errors))

    def test_negative_outcome_cannot_promote(self):
        a=copy.deepcopy(self.atlas)
        a["events"][0]["§RESULTADO"]["promotion_authorized"]=True
        errors=validate(self.contract,a)
        self.assertTrue(any("negative outcome cannot authorize promotion" in x for x in errors))

    def test_token_vazio_is_required_for_missing_receipt(self):
        a=copy.deepcopy(self.atlas)
        a["events"][0]["§TOKEN_VAZIO"]=[]
        errors=validate(self.contract,a)
        self.assertTrue(any("requires TOKEN_VAZIO" in x for x in errors))

    def test_promotion_requires_nonregression_guards(self):
        a=copy.deepcopy(self.atlas)
        ev=a["events"][0]
        ev["§RESULTADO"].update({"outcome":"PASS","epistemic_evolution":True,"promotion_authorized":True})
        ev["§RECEIPT"]={"state":"PASS","ref":"receipt:x"}
        ev["§GATE"]={"state":"PASS","promotion":True}
        ev["§H"]["human_rights_regression"]=True
        errors=validate(self.contract,a)
        self.assertTrue(any("human-rights regression" in x for x in errors))

if __name__=="__main__": unittest.main()
