from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/audit_diverged_ref_patches_v1.py"
spec = importlib.util.spec_from_file_location("patch_audit", SCRIPT)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class DivergedRefPatchEquivalenceTests(unittest.TestCase):
    def test_file_categories_are_deterministic(self):
        self.assertEqual(
            module.file_categories(["tools/a.py", "tests/test_a.py", "README.md", "tools/b.py"]),
            {"ROOT": 1, "tests": 1, "tools": 2},
        )

    def test_source_declares_semantic_boundary(self):
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("patch-equivalence is narrower than semantic equivalence", source)
        self.assertIn("a plus patch is not automatically technical progress", source)
        self.assertIn("no forward-port is authorized automatically", source)

    def test_source_requires_frozen_cohort(self):
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertIn('COHORT_SCHEMA = "rll.diverged_ref_cohort.v1"', source)
        self.assertIn("duplicate ref in frozen cohort", source)


if __name__ == "__main__":
    unittest.main()
