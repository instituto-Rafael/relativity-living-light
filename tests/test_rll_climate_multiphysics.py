from __future__ import annotations

import importlib.util
import json
import math
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


validator = load_module("validator", ROOT / "scripts" / "validate_rll_climate_multiphysics_registry.py")
scheduler = load_module("scheduler", ROOT / "scripts" / "rll_climate_fibonacci_scheduler.py")
fetcher = load_module("fetcher", ROOT / "scripts" / "fetch_rll_climate_sources.py")


class ClimateRegistryTests(unittest.TestCase):
    def test_registry_is_exactly_8x8(self):
        data = validator.load_json(ROOT / "data" / "climate" / "rll_climate_multiphysics_registry.v1.json")
        receipt = validator.validate_registry(data)
        self.assertEqual(receipt["status"], "PASS")
        self.assertEqual(receipt["matrix_cells"], 64)
        self.assertEqual(receipt["physical_variables"], 56)
        self.assertEqual(receipt["temporal_gates"], 8)

    def test_sources_are_https_and_opt_in(self):
        data = validator.load_json(ROOT / "data" / "climate" / "rll_climate_source_registry.v1.json")
        receipt = validator.validate_sources(data)
        self.assertEqual(receipt["status"], "PASS")
        self.assertGreaterEqual(receipt["sources"], 10)

    def test_canonical_lift_stays_inside_ball(self):
        point, radius = scheduler.canonical_lift([10.0, -5.0, 2.0, 1.0, 0.0, 3.0, -7.0])
        self.assertEqual(len(point), 7)
        self.assertLess(radius, 1.0)
        self.assertAlmostEqual(radius, math.sqrt(sum(x * x for x in point)))

    def test_high_priority_has_shorter_multiplier(self):
        self.assertLessEqual(scheduler.fibonacci_multiplier(0.95), scheduler.fibonacci_multiplier(0.05))
        self.assertEqual(scheduler.fibonacci_multiplier(1.0), 1)
        self.assertEqual(scheduler.fibonacci_multiplier(0.0), 34)

    def test_synthetic_cycle_has_eight_sectors(self):
        receipt = scheduler.run(
            ROOT / "data" / "climate" / "rll_climate_multiphysics_registry.v1.json",
            ROOT / "tests" / "fixtures" / "rll_climate_tile.synthetic.v1.json"
        )
        self.assertEqual(len(receipt["sectors"]), 8)
        self.assertFalse(receipt["forecast_generated"])
        self.assertFalse(receipt["claim_allowed"])
        for sector in receipt["sectors"]:
            self.assertLess(sector["metrics"]["radius"], 1.0)
            self.assertIn(sector["fibonacci_multiplier"], scheduler.FIB)

    def test_missing_data_increases_acquisition_priority(self):
        complete = scheduler.score_sector([0.0] * 7, [0.0] * 7, [True] * 7, [3.0] * 7, 0.0)
        missing = scheduler.score_sector([0.0] * 7, [0.0] * 7, [False] * 7, [3.0] * 7, 0.0)
        self.assertGreater(missing["acquisition_priority"], complete["acquisition_priority"])

    def test_fetcher_rejects_domain_mismatch(self):
        source = {"id": "x", "sample_url": "https://example.org/data", "domain": "noaa.gov"}
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                fetcher.fetch(source, Path(temp), 1.0, 10)

    def test_fetcher_dry_registry_has_no_default_fetch(self):
        data = json.loads((ROOT / "data" / "climate" / "rll_climate_source_registry.v1.json").read_text(encoding="utf-8"))
        self.assertTrue(all(source["fetch_by_default"] is False for source in data["sources"]))

    def test_fetcher_receipt_with_mocked_https_response(self):
        class Response:
            status = 200
            headers = {"Content-Type": "application/json"}
            def __enter__(self): return self
            def __exit__(self, *args): return False
            def read(self, size=-1):
                if hasattr(self, "done"): return b""
                self.done = True
                return b"{}"
            def geturl(self): return "https://example.org/data"
        source = {"id": "mock", "sample_url": "https://example.org/data", "domain": "example.org"}
        with tempfile.TemporaryDirectory() as temp, mock.patch.object(fetcher.urllib.request, "urlopen", return_value=Response()):
            receipt = fetcher.fetch(source, Path(temp), 1.0, 100)
            self.assertEqual(receipt["status"], 200)
            self.assertEqual(receipt["bytes"], 2)
            self.assertFalse(receipt["claim_allowed"])


if __name__ == "__main__":
    unittest.main()
