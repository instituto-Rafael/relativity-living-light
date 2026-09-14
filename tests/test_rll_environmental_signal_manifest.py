from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_rll_environmental_signal_manifest.py"
MANIFEST = ROOT / "data" / "manifests" / "rll_environmental_signal_manifest.v1.json"

spec = importlib.util.spec_from_file_location("envsig_validator", SCRIPT)
validator = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(validator)


class EnvironmentalSignalManifestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.base = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_valid_manifest_passes(self) -> None:
        report = validator.validate_manifest(copy.deepcopy(self.base), strict=True)
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["modules"], 12)
        self.assertFalse(report["claim_allowed"])

    def test_reordered_modules_are_rejected(self) -> None:
        data = copy.deepcopy(self.base)
        data["modules"][0], data["modules"][1] = data["modules"][1], data["modules"][0]
        with self.assertRaises(validator.ManifestError):
            validator.validate_manifest(data)

    def test_diesel_solid_only_is_rejected(self) -> None:
        data = copy.deepcopy(self.base)
        data["physical_facts"]["diesel_exhaust"]["solid_only"] = True
        with self.assertRaises(validator.ManifestError):
            validator.validate_manifest(data)

    def test_resistance_ionization_claim_is_rejected(self) -> None:
        data = copy.deepcopy(self.base)
        data["physical_facts"]["electric_shower"]["resistance_directly_ionizes_surroundings"] = True
        with self.assertRaises(validator.ManifestError):
            validator.validate_manifest(data)

    def test_singing_ionization_causality_is_rejected(self) -> None:
        data = copy.deepcopy(self.base)
        data["physical_facts"]["singing_context"]["ionization_causes_singing"] = True
        with self.assertRaises(validator.ManifestError):
            validator.validate_manifest(data)

    def test_promotion_without_gates_is_rejected(self) -> None:
        data = copy.deepcopy(self.base)
        data["decision_policy"]["promotion_allowed"] = True
        data["decision_policy"]["current_state"] = "PROMOTED_TO_SIGNAL"
        with self.assertRaises(validator.ManifestError):
            validator.validate_manifest(data)

    def test_new_workflow_requirement_is_rejected(self) -> None:
        data = copy.deepcopy(self.base)
        data["orchestration_policy"]["no_new_workflow_required"] = False
        with self.assertRaises(validator.ManifestError):
            validator.validate_manifest(data)


if __name__ == "__main__":
    unittest.main()
