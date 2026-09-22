import json
import unittest
from pathlib import Path

from tools.validate_rll_recent_observations_crosswalk import validate

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "data/real_sources/rll_recent_observations_crosswalk_20260825.v1.json"


class RecentObservationCrosswalkTests(unittest.TestCase):
    def test_crosswalk_contract(self) -> None:
        data = validate(PATH)
        self.assertEqual(len(data["observations"]), 5)
        self.assertFalse(data["claim_allowed"])

    def test_every_observation_is_primary_and_claim_closed(self) -> None:
        data = json.loads(PATH.read_text(encoding="utf-8"))
        self.assertTrue(all(item["primary_source"] for item in data["observations"]))
        self.assertTrue(all(item["claim_allowed"] is False for item in data["observations"]))

    def test_scientific_decision_remains_blocked(self) -> None:
        data = json.loads(PATH.read_text(encoding="utf-8"))
        decision = next(g for g in data["execution_gates"] if g["gate_id"] == "G7_CLAIM_DECISION")
        self.assertEqual(decision["state"], "BLOCKED_BY_G0_TO_G6")


if __name__ == "__main__":
    unittest.main()
