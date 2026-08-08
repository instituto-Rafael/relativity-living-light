from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/audit_all_git_refs_v1.py"
spec = importlib.util.spec_from_file_location("ref_census", SCRIPT)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class AllGitRefsTopologyCensusTests(unittest.TestCase):
    def test_classify_identical(self):
        self.assertEqual(module.classify_counts(0, 0), "IDENTICAL_TO_BASELINE")

    def test_classify_absorbed_ahead_zero(self):
        self.assertEqual(module.classify_counts(12, 0), "ANCESTOR_OF_BASELINE_AHEAD_ZERO")

    def test_classify_descendant(self):
        self.assertEqual(module.classify_counts(0, 3), "DESCENDANT_OF_BASELINE")

    def test_classify_diverged(self):
        self.assertEqual(module.classify_counts(7, 2), "DIVERGED_FROM_BASELINE")

    def test_historical_denominator_is_measurement_reference_not_asserted_current_count(self):
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("HISTORICAL_DENOMINATOR = 582", source)
        self.assertIn("observed == HISTORICAL_DENOMINATOR", source)
        self.assertIn("current_observed_ref_count", source)
        self.assertIn("no ref may disappear from the census", source)


if __name__ == "__main__":
    unittest.main()
