"""Bounded contract tests: source typing and no unreviewed scientific promotion.

These tests validate metadata provenance and non-regression only.
They do not compute a DESI likelihood, RLL fit or physical prediction.
"""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "data/governance/RLL_CROSS_SCALE_EVIDENCE_GRAPH_20261028.json"
VALIDATOR = ROOT / "tools/validate_cross_scale_evidence_graph.py"


def invoke(path, self_test=False):
    cmd = [sys.executable, "-B", str(VALIDATOR), "--file", str(path)]
    if self_test:
        cmd.append("--self-test")
    result = subprocess.run(cmd, text=True, capture_output=True, check=False, timeout=20)
    try:
        parsed = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError("validator did not issue a machine-readable receipt: " + repr(result.stderr)) from exc
    return result, parsed


class CrossScaleEvidenceGate(unittest.TestCase):
    def test_clean_and_all_12_negative_mutations(self):
        result, receipt = invoke(GRAPH, self_test=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(receipt["status"], "PASS_SCOPED_METADATA_ONLY")
        self.assertEqual(receipt["negative_tests"], 12)
        self.assertIs(receipt["claim_allowed"], False)
        self.assertIs(receipt["data_fit_executed"], False)
        self.assertEqual(receipt["nodes"], 8)
        self.assertEqual(receipt["edges"], 11)

    def test_rejects_promotions_extra_edges_and_malformed_data(self):
        source = json.loads(GRAPH.read_text(encoding="utf-8"))

        def promote_preprint(g):
            next(x for x in g["edges"] if x["id"] == "E02")["status"] = "ESTABLISHED"

        def inject_new_established_link(g):
            g["edges"].append(dict(g["edges"][0], id="E12", status="ESTABLISHED"))

        def spoof_atomic_provenance(g):
            g["sources"][0]["id"] = ["non-hashable", "not-a-string"]

        def drop_measured_benchmark(g):
            g["benchmarks"][0]["measured"] = []

        def remove_source(g):
            g["sources"] = [x for x in g["sources"] if x["id"] != "CIV_BAO"]

        experiments = {
            "preprint_promotion": promote_preprint,
            "unversioned_established_edge": inject_new_established_link,
            "malformed_id": spoof_atomic_provenance,
            "malformed_measurement": drop_measured_benchmark,
            "missing_publication": remove_source,
        }
        with tempfile.TemporaryDirectory(prefix="rll_cross_scale_") as d:
            for name, modify in experiments.items():
                with self.subTest(counterexample=name):
                    candidate = copy.deepcopy(source)
                    modify(candidate)
                    path = Path(d) / (name + ".json")
                    path.write_text(json.dumps(candidate), encoding="utf-8")
                    result, receipt = invoke(path)
                    self.assertEqual(result.returncode, 2, (name, result.stderr))
                    self.assertEqual(receipt["status"], "HOLD_INVALID")
                    self.assertTrue(receipt["errors"], (name, receipt))
                    self.assertIs(receipt["claim_allowed"], False)

    def test_null_manifest_issues_structured_hold(self):
        with tempfile.TemporaryDirectory(prefix="rll_cross_scale_null_") as d:
            path = Path(d) / "null.json"
            path.write_text("null\n", encoding="utf-8")
            result, receipt = invoke(path)
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertIn("manifest_not_object", receipt["errors"])
            self.assertIs(receipt["claim_allowed"], False)


if __name__ == "__main__":
    unittest.main()
