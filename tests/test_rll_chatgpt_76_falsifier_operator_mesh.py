import copy,importlib.util,json
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/"tools/validate_rll_chatgpt_76_falsifier_operator_mesh.py"
spec=importlib.util.spec_from_file_location("mesh",P); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
M=json.loads((ROOT/"data/contracts/rll_chatgpt_76_falsifier_operator_mesh.v1.json").read_text())
class T(unittest.TestCase):
 def test_current_mesh_passes(self): self.assertEqual(m.validate(M),[])
 def test_requires_76(self):
  x=copy.deepcopy(M); x["operators"].pop()
  self.assertIn("operator_count",m.validate(x))
 def test_ordered_ids(self):
  x=copy.deepcopy(M); x["operators"][0]["id"]="OP76"
  self.assertIn("operator_ids",m.validate(x))
 def test_proposed_not_pass(self):
  x=copy.deepcopy(M); x["operators"][0]["state"]="PASS"
  self.assertTrue(any(v.startswith("premature_state") for v in m.validate(x)))
 def test_falsifier_required(self):
  x=copy.deepcopy(M); x["operators"][4]["falsifier"]=""
  self.assertTrue(any(v.startswith("missing_falsifier") for v in m.validate(x)))
 def test_void_typing_required(self):
  x=copy.deepcopy(M); x["typed_gaps"][0]["close_when"]=""
  self.assertIn("untyped_token_vazio",m.validate(x))
 def test_cannot_self_promote(self):
  x=copy.deepcopy(M); x["claim_allowed"]=True
  self.assertIn("premature_promotion",m.validate(x))
if __name__=="__main__": unittest.main()
