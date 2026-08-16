import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/validate_rll_formula_test_matrix_24.py"

spec = importlib.util.spec_from_file_location("validator24", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class FormulaMatrix24Tests(unittest.TestCase):
    def test_validator_passes(self):
        self.assertEqual(mod.validate(), [])

    def test_exact_cardinality_and_ids(self):
        rows = mod.load_rows()
        self.assertEqual(len(rows), 24)
        self.assertEqual({r["source_id"] for r in rows}, mod.EXPECTED_IDS)

    def test_fail_closed_claims(self):
        rows = mod.load_rows()
        self.assertTrue(all(r["claim_allowed"].lower() == "false" for r in rows))

    def test_family_distribution(self):
        from collections import Counter
        rows = mod.load_rows()
        self.assertEqual(dict(Counter(r["family"] for r in rows)), mod.EXPECTED_FAMILIES)

    def test_graph_refs_exist_or_are_explicitly_empty(self):
        rows = mod.load_rows()
        for row in rows:
            ref = row["graph_ref"]
            if ref == mod.TOKEN_VAZIO_GRAPH:
                continue
            for path in ref.split(";"):
                self.assertTrue((ROOT / path).is_file(), path)

if __name__ == "__main__":
    unittest.main()
