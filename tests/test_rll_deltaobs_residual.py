from __future__ import annotations

import importlib.util
from datetime import datetime, timedelta, timezone
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


def load_module():
    path = ROOT / "scripts" / "rll_deltaobs_residual.py"
    spec = importlib.util.spec_from_file_location("rll_deltaobs_residual", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


deltaobs = load_module()


def sample(ts, family, value, uncertainty=0.1):
    return {
        "timestamp_utc": ts.isoformat(),
        "measurement_family": family,
        "value": value,
        "uncertainty": uncertainty,
    }


def make_doc(families=("A", "B", "C"), jump=1.0, z_threshold=3.0, min_families=3):
    anchor = datetime(2026, 9, 10, 12, 0, tzinfo=timezone.utc)
    rows = []
    for family in families:
        for hours, value in [
            (-5.0, 0.0), (-3.0, 0.0), (-1.0, 0.0),
            (0.5, jump), (1.5, jump), (2.5, jump),
            (3.5, 0.5 * jump), (4.5, 0.5 * jump), (5.5, 0.5 * jump),
        ]:
            rows.append(sample(anchor + timedelta(hours=hours), family, value))
    return {
        "schema": "rll.deltaobs.normalized_input.v1",
        "anchor_time_utc": anchor.isoformat(),
        "preregistration": {
            "z_threshold": z_threshold,
            "min_families": min_families,
            "min_samples_per_window": 2,
        },
        "samples": rows,
    }


class DeltaObsResidualTests(unittest.TestCase):
    def test_windows_are_exactly_6_3_3(self):
        anchor = datetime(2026, 9, 10, 12, 0, tzinfo=timezone.utc)
        self.assertEqual(deltaobs.classify_window(anchor - timedelta(hours=6), anchor), "baseline")
        self.assertEqual(deltaobs.classify_window(anchor - timedelta(microseconds=1), anchor), "baseline")
        self.assertEqual(deltaobs.classify_window(anchor, anchor), "challenge")
        self.assertEqual(deltaobs.classify_window(anchor + timedelta(hours=3), anchor), "feedback")
        self.assertIsNone(deltaobs.classify_window(anchor + timedelta(hours=6), anchor))

    def test_preregistration_is_mandatory(self):
        doc = make_doc()
        del doc["preregistration"]
        with self.assertRaises(ValueError):
            deltaobs.evaluate(doc)

    def test_three_family_numeric_candidate_never_promotes_claim(self):
        receipt = deltaobs.evaluate(make_doc())
        self.assertTrue(receipt["deltaobs_candidate"])
        self.assertEqual(receipt["numeric_deltaobs_state"], "NUMERIC_CROSS_FAMILY_CANDIDATE")
        self.assertEqual(len(receipt["families_exceeding_preregistered_threshold"]), 3)
        self.assertFalse(receipt["observed_cross_domain"])
        self.assertFalse(receipt["statistical_independence_established"])
        self.assertEqual(receipt["cause"], "TOKEN_VAZIO_CAUSA")
        self.assertFalse(receipt["claim_allowed"])

    def test_one_family_cannot_satisfy_three_family_gate(self):
        receipt = deltaobs.evaluate(make_doc(families=("A",), min_families=3))
        self.assertFalse(receipt["deltaobs_candidate"])
        self.assertEqual(receipt["numeric_deltaobs_state"], "NO_NUMERIC_CANDIDATE")

    def test_zero_scale_fails_closed_per_family(self):
        doc = make_doc(families=("A",), jump=0.0, min_families=1)
        for row in doc["samples"]:
            row["uncertainty"] = 0.0
        receipt = deltaobs.evaluate(doc)
        result = receipt["family_results"]["A"]
        self.assertEqual(result["challenge_residual"]["state"], "TOKEN_VAZIO_ZERO_SCALE")
        self.assertFalse(receipt["deltaobs_candidate"])

    def test_common_mode_controls_do_not_create_causal_claim(self):
        doc = make_doc()
        doc["common_mode_controls"] = [
            {"id": "clock_shift_negative_control", "status": "DOCUMENTED"}
        ]
        receipt = deltaobs.evaluate(doc)
        self.assertEqual(receipt["common_mode_controls_state"], "DOCUMENTED_NOT_CAUSAL")
        self.assertEqual(receipt["cause"], "TOKEN_VAZIO_CAUSA")
        self.assertFalse(receipt["claim_allowed"])


if __name__ == "__main__":
    unittest.main()
