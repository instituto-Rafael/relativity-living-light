from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]


def load_module():
    path = ROOT / "scripts" / "rll_climate_engine_bridge.py"
    spec = importlib.util.spec_from_file_location("rll_climate_engine_bridge", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


bridge = load_module()


def args(**overrides):
    values = {
        "dataset": "GRIDMET",
        "variable": "pr",
        "start_date": "2026-09-01",
        "end_date": "2026-09-02",
        "coordinates": "[[-121.61,38.78]]",
        "area_reducer": "mean",
        "temporal_statistic": "mean",
        "colormap_opacity": 0.7,
        "colormap_type": "continuous",
    }
    values.update(overrides)
    return argparse.Namespace(**values)


class ClimateEngineBridgeTests(unittest.TestCase):
    def setUp(self):
        self.registry = json.loads(
            (ROOT / "data" / "climate" / "rll_external_compute_registry.v1.json").read_text(encoding="utf-8")
        )
        self.provider = bridge.provider_spec(self.registry)

    def test_provider_is_compute_not_primary_sensor(self):
        self.assertEqual(self.provider["role"], "EXTERNAL_COMPUTE_AND_VISUALIZATION")
        self.assertTrue(self.provider["epistemic_boundary"]["provider_is_not_primary_sensor"])
        self.assertFalse(self.provider["epistemic_boundary"]["claim_allowed"])

    def test_timeseries_request_is_https_and_allowlisted(self):
        url = bridge.build_request("timeseries_coordinates", args(), self.provider)
        self.assertTrue(url.startswith("https://api.climateengine.org/timeseries/native/coordinates?"))
        bridge.validate_allowed_url(url, "api.climateengine.org")
        self.assertIn("dataset=GRIDMET", url)
        self.assertIn("variable=pr", url)

    def test_map_request_is_https_and_allowlisted(self):
        url = bridge.build_request("map_values", args(), self.provider)
        self.assertTrue(url.startswith("https://api.climateengine.org/raster/mapid/values?"))
        self.assertIn("temporal_statistic=mean", url)

    def test_wrong_host_fails_closed(self):
        with self.assertRaises(ValueError):
            bridge.validate_allowed_url("https://example.com/raster/mapid/values", "api.climateengine.org")

    def test_sanitizer_redacts_tile_and_secret_like_fields(self):
        payload = {
            "tile_fetcher": "https://temporary.example/tiles/{z}/{x}/{y}",
            "token": "secret",
            "nested": {"api_key": "secret2", "value": 7},
        }
        clean = bridge.sanitize_json(payload)
        self.assertEqual(clean["tile_fetcher"], "TOKEN_VAZIO_EPHEMERAL_TILE_HANDLE")
        self.assertEqual(clean["token"], "REDACTED_SECRET_OR_EPHEMERAL")
        self.assertEqual(clean["nested"]["api_key"], "REDACTED_SECRET_OR_EPHEMERAL")
        self.assertEqual(clean["nested"]["value"], 7)

    def test_missing_api_key_is_typed_and_never_claims(self):
        url = bridge.build_request("metadata_dates", args(), self.provider)
        with tempfile.TemporaryDirectory() as temp:
            receipt, rc = bridge.execute_operation(
                "metadata_dates",
                url,
                self.provider,
                Path(temp),
                None,
                timeout=1,
                max_bytes=1024,
            )
        self.assertEqual(rc, 3)
        self.assertEqual(receipt["gate_status"], "BLOCKED_CREDENTIAL")
        self.assertEqual(receipt["credential_state"], "TOKEN_VAZIO_CLIMATE_ENGINE_API_KEY")
        self.assertFalse(receipt["claim_allowed"])

    def test_receipt_never_promotes_cross_domain_or_cause(self):
        receipt = bridge.build_receipt(
            operation="metadata_variables",
            request_url="https://api.climateengine.org/metadata/dataset_variables?dataset=GRIDMET",
            execute=False,
            credential_state="TOKEN_VAZIO_NOT_ACCESSED_IN_DRY_RUN",
            gate_status="DRY_RUN",
        )
        self.assertFalse(receipt["observed_cross_domain"])
        self.assertFalse(receipt["statistical_independence_established"])
        self.assertEqual(receipt["cause"], "TOKEN_VAZIO_CAUSA")
        self.assertFalse(receipt["claim_allowed"])


if __name__ == "__main__":
    unittest.main()
