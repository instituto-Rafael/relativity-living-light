import csv
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
INTAKE = ROOT / "data" / "inputs" / "cosmology_joint" / "rll_successor_hypotheses_20260827.v1.csv"
EXPECTED_IDS = {f"H{i}" for i in range(51, 58)}


class RllSuccessorHypothesisIntakeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with INTAKE.open("r", encoding="utf-8", newline="") as fh:
            cls.rows = list(csv.DictReader(fh))

    def test_successor_ids_are_separate_and_unique(self):
        ids = [row["id"] for row in self.rows]
        self.assertEqual(EXPECTED_IDS, set(ids))
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(int(identifier[1:]) > 50 for identifier in ids))

    def test_fail_closed_claim_boundary(self):
        self.assertTrue(self.rows)
        self.assertTrue(all(row["claim_allowed"].lower() == "false" for row in self.rows))
        self.assertTrue(all(row["evidence_state"].startswith("TOKEN_VAZIO") for row in self.rows))

    def test_every_candidate_has_null_falsifier_and_next_gate(self):
        for row in self.rows:
            self.assertTrue(row["null_model"].strip(), row["id"])
            self.assertTrue(row["falsifier"].strip(), row["id"])
            self.assertTrue(row["next_gate"].strip(), row["id"])
            self.assertTrue(row["observables"].strip(), row["id"])

    def test_post_hoc_candidate_is_explicit(self):
        h51 = next(row for row in self.rows if row["id"] == "H51")
        self.assertEqual("POST_HOC_CANDIDATE", h51["kind"])
        self.assertIn("held-out/future", h51["next_gate"])


if __name__ == "__main__":
    unittest.main()
