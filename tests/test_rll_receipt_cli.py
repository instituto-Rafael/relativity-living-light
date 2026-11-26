"""Exercise the actual receipt CLI with isolated Python, not an import-only test."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class DirectReceiptCLITests(unittest.TestCase):
    def invoke(self, name, *args):
        env = os.environ.copy()
        env.pop("PYTHONPATH", None)
        return subprocess.run(
            [sys.executable, "-I", str(ROOT / "tools" / name), *map(str, args)],
            cwd=ROOT, env=env, text=True, capture_output=True, timeout=180,
        )

    def test_ws01_direct(self):
        result = self.invoke("rll_ws01_distance_v2.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        receipt = json.loads(result.stdout)
        self.assertEqual(receipt["row_count"], 51)
        self.assertEqual(receipt["failures"], [])
        self.assertEqual(receipt["predecessor_state"], "FAIL_PREREGISTERED_DISTANCE_TOLERANCE")
        self.assertFalse(receipt["claim_allowed"])
        self.assertFalse(receipt["promotion_allowed"])

    def test_loubser_direct(self):
        result = self.invoke("rll_literature_cc_loubser.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        receipt = json.loads(result.stdout)
        self.assertEqual(receipt["model_selection"], "NOT_RUN")
        self.assertEqual(receipt["joint_ingestion"], "BLOCKED_OVERLAP_AND_COVARIANCE_NOT_VERIFIED")
        self.assertFalse(receipt["claim_allowed"])
        self.assertFalse(receipt["promotion_allowed"])

    def test_publication_cross_direct_offline(self):
        with tempfile.TemporaryDirectory() as d:
            source = Path(d) / "catalog.json"
            output = Path(d) / "output.json"
            source.write_text('{"records": {}}', encoding="utf-8")
            original = source.read_bytes()
            result = self.invoke("rll_publication_cross.py", source, "--offline", "--output", output)
            self.assertEqual(result.returncode, 0, result.stderr)
            receipt = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(receipt["feed_status"], "NOT_RUN_OFFLINE")
            self.assertFalse(receipt["claim_allowed"])
            self.assertEqual(source.read_bytes(), original)
