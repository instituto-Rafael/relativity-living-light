import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "data/contracts/rll_multilayer_circle_polygon_geometry_v1.yml"
VALIDATOR = ROOT / "scripts/validate_multilayer_circle_polygon_geometry_v1.py"

class TestMultilayerCirclePolygonGeometryV1(unittest.TestCase):
    def test_contract_and_all_scenarios(self):
        with SPEC.open("r", encoding="utf-8") as f:
            spec = yaml.safe_load(f)
        self.assertEqual(len(spec["scenarios"]), 20)
        self.assertEqual(len(spec["formula_registry"]), 30)
        self.assertEqual(len(spec["index_registry"]), 8)

        with tempfile.TemporaryDirectory() as td:
            output = Path(td) / "result.json"
            subprocess.run(
                [sys.executable, str(VALIDATOR), "--spec", str(SPEC), "--output", str(output)],
                cwd=ROOT,
                check=True,
            )
            result = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["summary"]["tests_total"], 120)
        self.assertEqual(result["summary"]["passed"], 120)
        self.assertEqual(result["summary"]["failed"], 0)
        self.assertEqual(result["summary"]["scenarios"], 20)
        self.assertTrue(all(v["state"] == "PASS" for v in result["scenario_summary"].values()))

        k8 = result["key_invariants"]["K8"]
        self.assertEqual(k8["segments"], 28)
        self.assertEqual(k8["intersections"], 49)
        self.assertEqual(k8["planar"], {"V": 57, "E": 136, "F": 81})
        self.assertEqual(k8["cycle_rank"], 80)

        k16 = result["key_invariants"]["K16"]
        self.assertEqual(k16["vertices"], 16)
        self.assertEqual(k16["complete_edges"], 120)

if __name__ == "__main__":
    unittest.main()
