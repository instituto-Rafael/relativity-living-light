from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "rll_dual_api_real_climate_calibration.py"

spec = importlib.util.spec_from_file_location("dualapi", SCRIPT)
dualapi = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(dualapi)


def ns(**overrides):
    values = {
        "repository": "instituto-Rafael/relativity-living-light",
        "ref": "main",
        "dataset": "GRIDMET",
        "variable": "pr",
        "coordinates": "[[-121.61,38.78]]",
        "area_reducer": "mean",
        "baseline_start_date": "2024-10-01",
        "baseline_end_date": "2024-10-03",
        "target_start_date": "2025-10-01",
        "target_end_date": "2025-10-03",
        "execute": False,
    }
    values.update(overrides)
    return argparse.Namespace(**values)


class DualApiCalibrationTests(unittest.TestCase):
    def test_selector_resolves_exact_named_secret(self):
        with patch.dict(os.environ, {
            "RLL_AGENT_CLIMATE_KEY_ENV": "MY_CLIMATE_SECRET",
            "MY_CLIMATE_SECRET": "opaque",
        }, clear=True):
            name, value = dualapi.resolve_secret(
                "RLL_AGENT_CLIMATE_KEY_ENV",
                ("CLIMATE_ENGINE_API_KEY",)
            )
        self.assertEqual(name, "MY_CLIMATE_SECRET")
        self.assertEqual(value, "opaque")

    def test_ambiguous_aliases_fail_closed(self):
        with patch.dict(os.environ, {"A":"1","B":"2"}, clear=True):
            with self.assertRaises(dualapi.CalibrationError):
                dualapi.resolve_secret("SELECTOR", ("A","B"))

    def test_dry_run_never_reads_secrets(self):
        with patch.dict(os.environ, {}, clear=True):
            receipt, rc = dualapi.run(ns())
        self.assertEqual(rc, 0)
        self.assertEqual(receipt["gate_status"], "DRY_RUN_READY")
        self.assertFalse(receipt["credential_receipt"]["secret_value_observed"])
        self.assertFalse(receipt["claim_allowed"])

    def test_known_climateengine_data_shape_is_parsed(self):
        payload = {
            "Data": [{
                "Data": [
                    {"Date":"2024-10-01","pr":1.5},
                    {"Date":"2024-10-02","pr":-9999.0},
                    {"Date":"2024-10-03","pr":2.5},
                ]
            }]
        }
        rows = dualapi.extract_rows(payload, "pr")
        values = dualapi.numeric_values(rows, "pr")
        self.assertEqual(values, [1.5, 2.5])
        summary = dualapi.stats(values)
        self.assertEqual(summary["n"], 2)
        self.assertAlmostEqual(summary["mean"], 2.0)

    def test_calibration_delta_and_z(self):
        base = dualapi.stats([1.0, 2.0, 3.0])
        target = dualapi.stats([2.0, 3.0, 4.0])
        c = dualapi.calibration_metrics(base, target)
        self.assertEqual(c["state"], "REAL_PROVIDER_CALIBRATION_SUMMARY")
        self.assertAlmostEqual(c["delta_mean"], 1.0)
        self.assertIsNotNone(c["z_shift_vs_baseline"])

    def test_github_is_explicitly_not_scientific_signal(self):
        receipt, _ = dualapi.run(ns())
        self.assertEqual(
            receipt["separation"]["github_api_role"],
            "CONTROL_PLANE_PROVENANCE_NOT_SCIENTIFIC_CALIBRATION",
        )

    def test_receipt_schema_contains_no_secret_material(self):
        secret = "never-persist-this-secret"
        with patch.dict(os.environ, {
            "RLL_AGENT_GITHUB_PAT_ENV": "GITHUB_TOKEN",
            "GITHUB_TOKEN": secret,
            "RLL_AGENT_CLIMATE_KEY_ENV": "RLL_CLIMATE_ENGINE_TRIAL_TOKEN",
            "RLL_CLIMATE_ENGINE_TRIAL_TOKEN": secret,
        }, clear=True):
            receipt, _ = dualapi.run(ns(execute=False))
        encoded = json.dumps(receipt)
        self.assertNotIn(secret, encoded)


if __name__ == "__main__":
    unittest.main()
