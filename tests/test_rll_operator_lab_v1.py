#!/usr/bin/env python3
from __future__ import annotations
import json, pathlib, sys, unittest
from copy import deepcopy
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from rx.operator_lab import SUPPORTED, apply_operator, propagate, run_suite
sys.path.insert(0,str(ROOT/"tools"))
from rll_operator_lab_evidence_envelope import seal, validate

class OperatorLabTests(unittest.TestCase):
    def setUp(self):
        self.suite=json.loads((ROOT/"configs/rll_operator_lab_suite_v1.json").read_text(encoding="utf-8"))
    def test_contract_is_claim_disabled(self):
        c=json.loads((ROOT/"data/governance/RLL_OPERATOR_LAB_CONTRACT_V1.json").read_text(encoding="utf-8"))
        self.assertIs(c["claim_allowed"],False); self.assertIs(c["physics_binding"],False)
        self.assertEqual(c["scientific_gate_effect"],"NONE"); self.assertFalse(c["dynamic_eval"]); self.assertFalse(c["dynamic_exec"])
    def test_supported_operator_count(self):
        self.assertEqual(len(SUPPORTED),16)
    def test_negative_first_suite_passes(self):
        r=run_suite(self.suite)
        self.assertEqual(r["state"],"PASS"); self.assertEqual(r["negative_gate"],"PASS")
        self.assertEqual(r["negative_count"],10); self.assertEqual(r["positive_count"],10)
        self.assertIs(r["claim_allowed"],False); self.assertIs(r["physics_binding"],False)
    def test_negative_fixture_never_passes(self):
        for f in self.suite["negative"]:
            self.assertNotEqual(propagate(f)["state"],"PASS",f["fixture_id"])
    def test_positive_fixture_passes(self):
        for f in self.suite["positive"]:
            self.assertEqual(propagate(f)["state"],"PASS",f["fixture_id"])
    def test_unsupported_fails_closed(self):
        self.assertEqual(apply_operator("O017",{"value":4.0,"type":"real"})["state"],"BLOCKED_UNSUPPORTED")
    def test_no_eval_exec_symbols(self):
        src=(ROOT/"rx/operator_lab.py").read_text(encoding="utf-8")
        self.assertNotIn("eval(",src); self.assertNotIn("exec(",src)
    def test_envelope_mutation_fails(self):
        base={"schema_version":"rmr-zipraf-evidence-envelope-v1","envelope_id":"TEST","subject":{"kind":"RLL_OPERATOR_LAB_RECEIPT"},"artifact_digests":[],"manifest_digest":{},"receipt_chain_head":{},"policy_digest":{},"parent_envelope_root":None,"producer":{},"time_attestation":{},"external_anchors":[],"claim_allowed":False}
        sealed=seal(base); self.assertEqual(validate(sealed)["state"],"PASS")
        bad=deepcopy(sealed); bad["subject"]["kind"]="MUTATED"
        self.assertEqual(validate(bad)["state"],"FAIL")
if __name__=="__main__":
    unittest.main()
