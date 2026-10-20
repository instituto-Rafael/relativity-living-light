import copy,importlib.util,json
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/"tools/validate_rll_observer_observation_science_routing.py"
spec=importlib.util.spec_from_file_location("v",P); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
C=json.loads((ROOT/"data/contracts/rll_observer_observation_science_routing.v1.json").read_text())
O=json.loads((ROOT/"data/observations/2026-10-20_observer_science_closure.v1.json").read_text())
class T(unittest.TestCase):
 def test_current(self): self.assertEqual(m.validate(C,O),[])
 def test_observer_is_not_observation(self):
  x=copy.deepcopy(O); x["observer_id"]=x["observation_id"]; self.assertIn("observer_observation_collision",m.validate(C,x))
 def test_new_requires_science_route(self):
  x=copy.deepcopy(O); x["science_routes"]=[]; self.assertIn("science_routes_empty",m.validate(C,x))
 def test_unknown_requires_gap(self):
  x=copy.deepcopy(O); x["epistemic_state"]="UNKNOWN"; x["typed_gaps"]=[]; self.assertIn("unknown_without_typed_gap",m.validate(C,x))
 def test_gap_requires_closure(self):
  x=copy.deepcopy(O); x["typed_gaps"][0]["closure"]=""; self.assertIn("untyped_gap",m.validate(C,x))
 def test_raw_session_boundary(self):
  x=copy.deepcopy(O); x["raw_session_text_stored"]=True; self.assertIn("raw_session_text_boundary",m.validate(C,x))
if __name__=="__main__": unittest.main()
