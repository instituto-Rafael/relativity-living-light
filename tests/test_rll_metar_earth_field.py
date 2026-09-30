from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


def load_module():
    path = ROOT / "scripts" / "rll_metar_earth_field.py"
    spec = importlib.util.spec_from_file_location("rll_metar_earth_field", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


metar = load_module()


class MetarEarthFieldTests(unittest.TestCase):
    def test_wind_components_use_meteorological_from_direction(self):
        u, v, speed = metar.wind_components(90, 10)
        self.assertAlmostEqual(speed, 5.14444, places=5)
        self.assertAlmostEqual(u, -5.14444, places=5)
        self.assertAlmostEqual(v, 0.0, places=5)

    def test_pressure_prefers_sea_level_hpa(self):
        value, source = metar.pressure_hpa({"slp": 1016.2, "altim": 1016.3})
        self.assertAlmostEqual(value, 1016.2)
        self.assertEqual(source, "slp_hpa")

    def test_pressure_accepts_legacy_inhg_shape(self):
        value, source = metar.pressure_hpa({"altim": 30.00})
        self.assertAlmostEqual(value, 1015.9166, places=3)
        self.assertEqual(source, "altim_inHg_converted_to_hpa")

    def test_synthetic_fixture_builds_diagnostic_grid(self):
        rows = json.loads((ROOT / "tests/fixtures/rll_metar_synthetic.json").read_text(encoding="utf-8"))
        selected = metar.latest_per_station(rows)
        observations = [metar.normalize_observation(x) for x in selected]
        observations = [x for x in observations if x is not None]
        grid = metar.build_grid(observations, 12, 10)
        self.assertEqual(grid["nx"], 12)
        self.assertEqual(grid["ny"], 10)
        self.assertEqual(len(grid["cells"]), 120)
        center = grid["cells"][60]
        self.assertIsNotNone(center["u_m_s"])
        self.assertIsNotNone(center["v_m_s"])
        self.assertIsNotNone(center["temperature_c"])
        self.assertIsNotNone(center["pressure_hpa"])
        self.assertIsNotNone(center["vertical_vorticity_s_1"])
        self.assertIsNotNone(center["divergence_s_1"])

    def test_svg_and_csv_are_materialized(self):
        rows = json.loads((ROOT / "tests/fixtures/rll_metar_synthetic.json").read_text(encoding="utf-8"))
        observations = [metar.normalize_observation(x) for x in metar.latest_per_station(rows)]
        observations = [x for x in observations if x is not None]
        grid = metar.build_grid(observations, 8, 8)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            csv_path = root / "field.csv"
            svg_path = root / "field.svg"
            metar.write_csv(csv_path, grid["cells"])
            metar.write_svg(svg_path, grid, observations, "SYNTHETIC_FIXTURE_NOT_OBSERVATION")
            self.assertIn("vertical_vorticity_s_1", csv_path.read_text(encoding="utf-8").splitlines()[0])
            svg = svg_path.read_text(encoding="utf-8")
            self.assertIn("IDW diagnostic, not CFD/assimilation", svg)
            self.assertIn("<svg", svg)

    def test_request_is_bounded_and_allowlisted(self):
        url = metar.build_metar_url(
            "https://aviationweather.gov/api/data/metar",
            "aviationweather.gov",
            ["SBGR", "SBSP", "SBKP"],
            2,
        )
        self.assertTrue(url.startswith("https://aviationweather.gov/api/data/metar?"))
        self.assertIn("format=json", url)
        self.assertIn("hours=2", url)


if __name__ == "__main__":
    unittest.main()
