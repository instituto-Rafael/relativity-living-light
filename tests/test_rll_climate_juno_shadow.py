import json
import tempfile
import unittest
from pathlib import Path

from scripts.rll_climate_juno_shadow import build_shadow, contains_secret_field

ROOT = Path(__file__).resolve().parents[1]

class ClimateJunoShadowTests(unittest.TestCase):
    def setUp(self):
        self.contract = json.loads((ROOT / "data/contracts/rll_climate_juno_shadow.v1.json").read_text())
        self.juno = json.loads((ROOT / "data/juno/rll_juno_atmospheric_reference.v1.json").read_text())

    def test_juno_manifest_has_distinct_light_channels(self):
        classes = {x["quantity_class"] for x in self.juno["observations"]}
        self.assertIn("spectral_radiance", classes)
        self.assertIn("electrical_discharge", classes)
        self.assertIn("particle_precipitation_emission", classes)

    def test_without_climate_receipt_stays_token_vazio(self):
        receipt = build_shadow(self.contract, self.juno, None)
        self.assertEqual(receipt["gate_status"], "SHADOW_TOKEN_VAZIO")
        self.assertIn("TOKEN_VAZIO_CLIMATE_RUNTIME_RECEIPT", receipt["gaps"])
        self.assertFalse(receipt["claim_allowed"])

    def test_sanitized_climate_receipt_can_open_shadow(self):
        climate = {
            "schema": "rll.climate_engine_bridge.receipt.v1",
            "gate_status": "EXTERNAL_COMPUTE_RESPONSE_OBSERVED",
            "response_sha256": "a" * 64,
            "claim_allowed": False,
        }
        receipt = build_shadow(self.contract, self.juno, climate)
        self.assertEqual(receipt["gate_status"], "SHADOW_READY")
        self.assertEqual(receipt["gaps"], [])

    def test_secret_material_is_rejected(self):
        climate = {"gate_status": "OK", "api_key": "must-not-enter-receipt"}
        self.assertTrue(contains_secret_field(climate))
        receipt = build_shadow(self.contract, self.juno, climate)
        self.assertIn("FORBIDDEN_SECRET_MATERIAL_IN_CLIMATE_RECEIPT", receipt["gaps"])

    def test_direct_cross_planet_equivalence_is_forbidden(self):
        self.assertIn(
            "CLIMATE_ENGINE_OUTPUT_IS_JUNO_EVIDENCE",
            self.contract["forbidden_promotions"],
        )
        self.assertTrue(all(not axis["direct_value_equivalence"] for axis in self.contract["comparison_axes"]))

if __name__ == "__main__":
    unittest.main()
