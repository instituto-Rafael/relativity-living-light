from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from scripts.validate_cosmological_matter_manifest import (
    classify_wavelength_m,
    to_wavelength_m,
    validate,
)

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "data/synthetic/cosmological_matter_observation.example.json"

class CosmologicalMatterManifestTests(unittest.TestCase):
    def fixture(self):
        return json.loads(EXAMPLE.read_text(encoding="utf-8"))

    def test_valid_synthetic_manifest(self):
        validate(self.fixture())

    def test_claim_true_fails(self):
        data = self.fixture()
        data["claim_allowed"] = True
        with self.assertRaises(ValueError):
            validate(data)

    def test_missing_systematics_fails(self):
        data = self.fixture()
        data["uncertainty"]["systematics_declared"] = False
        with self.assertRaises(ValueError):
            validate(data)

    def test_missing_falsifier_fails(self):
        data = self.fixture()
        data["retrieval"]["falsifier"] = ""
        with self.assertRaises(ValueError):
            validate(data)

    def test_private_path_fails(self):
        data = self.fixture()
        data["provenance"]["source"] = "/storage/emulated/0/private/export.json"
        with self.assertRaises(ValueError):
            validate(data)

    def test_350_nm_is_ultraviolet(self):
        self.assertEqual("ultraviolet", classify_wavelength_m(to_wavelength_m(350, "nm")))

    def test_450_nm_is_visible(self):
        self.assertEqual("visible", classify_wavelength_m(to_wavelength_m(450, "nm")))

    def test_350_um_is_far_ir_submillimeter(self):
        self.assertEqual(
            "far_infrared_submillimeter",
            classify_wavelength_m(to_wavelength_m(350, "um")),
        )

if __name__ == "__main__":
    unittest.main()
