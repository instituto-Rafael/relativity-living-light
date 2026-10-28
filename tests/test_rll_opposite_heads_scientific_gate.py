"""Scientific adversarial micro-gates: synthetic, not model internals or experimental evidence."""
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
GATE=ROOT/"tools/rll_opposite_heads_science_gate.py"
GRAPH=ROOT/"data/governance/RLL_OPPOSITE_HEADS_SCIENTIFIC_DUALITY_20261028.json"

class OppositeHeadsScientificGates(unittest.TestCase):
    def test_mathematical_contrasts_exact_script(self):
        p=subprocess.run([sys.executable,"-B",str(GATE),"--self-test"],capture_output=True,text=True,timeout=20)
        self.assertEqual(p.returncode,0,p.stderr)
        r=json.loads(p.stdout)
        self.assertEqual(r["status"],"PASS_SYNTHETIC_ONLY")
        self.assertEqual(r["n_pass"],14)
        self.assertEqual(r["n_total"],14)
        self.assertEqual(r["synthetic_forward"],r["synthetic_co_permuted"])
        self.assertNotEqual(r["synthetic_forward"],r["synthetic_unpaired"])
        self.assertFalse(r["claim_allowed"])
        self.assertFalse(r["scientific_fit_executed"])
        self.assertFalse(r["hidden_heads_observed"])

    def test_all_oppositions_have_sources_and_negative_controls(self):
        g=json.loads(GRAPH.read_text(encoding="utf-8"))
        self.assertEqual(g["schema"],"rll.opposite_heads_scientific_duality.v1")
        self.assertFalse(g["claim_allowed"])
        self.assertFalse(g["measured_gpt6_heads"])
        self.assertFalse(g["physical_cmb_bao_likelihood_executed"])
        ids=[s["id"] for s in g["sources"]]
        self.assertEqual(len(set(ids)),len(ids))
        edges=[e["id"] for e in g["contrasts"]]
        self.assertEqual(len(set(edges)),14)
        for e in g["contrasts"]:
            with self.subTest(edge=e["id"]):
                self.assertIn(e["source"],ids)
                self.assertTrue(e["null_test"])
                self.assertTrue(e["status"])
                self.assertTrue(e["scope"])
                self.assertTrue(e["mechanism"])
        self.assertEqual(next(e for e in g["contrasts"] if e["id"]=="O12")["status"],"TOKEN_VAZIO_PHYSICAL_LIKELIHOOD_NOT_EXECUTED")

    def test_must_never_confuse_opposites_with_physically_identical_mechanisms(self):
        spec=importlib.util.spec_from_file_location("opposite",GATE)
        mod=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        r=mod.check()
        self.assertEqual(r["status"],"PASS_SYNTHETIC_ONLY")
        self.assertAlmostEqual(r["hi_hyperfine_eV_reference"],5.87432618412e-6,places=12)
        self.assertTrue(all(t["pass"] for t in r["tests"]))
        # This experiment has no external data and must remain fail-closed for new physics.
        self.assertIs(r["claim_allowed"],False)

if __name__=="__main__":
    unittest.main()
