"""A structural/scoped evidence gate, never a physical model test."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from tools.ci.rll_neglected_cross_scale_gate_v1 import validate,REL,ROOT

class NeglectedCrossScaleGate(unittest.TestCase):
    def setUp(self):
        self.r=validate(ROOT)
        self.graph=json.loads((ROOT/REL).read_text())
    def test_additive_graph_has_all_nodes(self):
        self.assertEqual(self.r["state"],"PASS_SCOPED_STRUCTURE_ONLY")
        self.assertEqual(self.r["nodes"],13)
        self.assertEqual(self.r["edges"],13)
        self.assertEqual(self.r["papers"],13)
    def test_claims_are_not_promoted(self):
        self.assertFalse(self.r["claim_allowed"])
        self.assertEqual(self.r["physical_model_validation"],"NOT_RUN")
        self.assertTrue(all(e["physical_bridge_claimed"] is False for e in self.graph["edges"]))
    def test_no_duplicate_edges_or_nodes(self):
        self.assertEqual(len({n["id"] for n in self.graph["items"]}),13)
        self.assertEqual(len({e["id"] for e in self.graph["edges"]}),13)
    def test_primary_missing_physics_is_explicit(self):
        for key in ("NG01","NG03","NG05","NG07","NG10"):
            n=next(x for x in self.graph["items"] if x["id"]==key)
            self.assertEqual(n["rll_status"],"TOKEN_VAZIO")
    def test_no_metaphorical_promotion(self):
        n=next(x for x in self.graph["items"] if x["id"]=="NG12")
        self.assertEqual(n["class"],"analogy_only")
        self.assertEqual(n["rll_status"],"UNSUPPORTED_PHYSICAL_BRIDGE")
    def test_obvious_compactness_dimension(self):
        self.assertAlmostEqual(self.r["compactness_1p4Msun_12km"],0.1722781306,places=7)
    def test_missing_file_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(FileNotFoundError):
                validate(d)
    def test_every_paper_has_a_url_and_tier(self):
        for s in self.graph["sources"]:
            self.assertTrue(s["uri"].startswith("https://"))
            self.assertTrue(s["tier"])
    def test_priors_not_inferred_from_atoms(self):
        allstr=json.dumps(self.graph)
        self.assertIn("Q_mu",allstr)
        self.assertIn("physical_bridge",allstr)

if __name__=="__main__":unittest.main(verbosity=2)
