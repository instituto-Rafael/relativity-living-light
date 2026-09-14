from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_rll_multiphysics_filament_matrix.py"
MATRIX = ROOT / "data" / "manifests" / "rll_multiphysics_filament_matrix.v1.json"

spec = importlib.util.spec_from_file_location("multiphysics_validator", SCRIPT)
validator = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(validator)


class MultiphysicsFilamentMatrixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.base = json.loads(MATRIX.read_text(encoding="utf-8"))

    def test_valid_matrix_passes(self) -> None:
        report = validator.validate_matrix(copy.deepcopy(self.base), strict=True)
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["filaments"], 10)
        self.assertEqual(report["edges"], 7)
        self.assertFalse(report["claim_allowed"])
        self.assertFalse(report["new_workflow_required"])

    def test_filament_reordering_is_rejected(self) -> None:
        data = copy.deepcopy(self.base)
        data["filaments"][0], data["filaments"][1] = data["filaments"][1], data["filaments"][0]
        with self.assertRaises(validator.MatrixError):
            validator.validate_matrix(data)

    def test_frequency_match_cannot_define_mechanism(self) -> None:
        data = copy.deepcopy(self.base)
        data["coupling_policy"]["numeric_frequency_match_is_not_mechanism_identity"] = False
        with self.assertRaises(validator.MatrixError):
            validator.validate_matrix(data)

    def test_ambient_ions_cannot_be_promoted_to_neural_current(self) -> None:
        data = copy.deepcopy(self.base)
        neuro = next(item for item in data["filaments"] if item["id"] == "neuroionic_autonomic_state")
        neuro["blocked_inferences"].remove("AMBIENT_ION_COUNT_EQUALS_BRAIN_ION_SIGNALING")
        with self.assertRaises(validator.MatrixError):
            validator.validate_matrix(data)

    def test_emotion_cannot_be_promoted_to_blood_ph(self) -> None:
        data = copy.deepcopy(self.base)
        respiratory = next(item for item in data["filaments"] if item["id"] == "respiration_co2_acid_base")
        respiratory["blocked_inferences"].remove("EMOTION_HAS_AN_INTRINSIC_PH")
        with self.assertRaises(validator.MatrixError):
            validator.validate_matrix(data)

    def test_heart_field_cannot_encode_semantic_emotion(self) -> None:
        data = copy.deepcopy(self.base)
        cardiac = next(item for item in data["filaments"] if item["id"] == "cardiac_electric_magnetic_pressure")
        cardiac["blocked_inferences"].remove("HEART_MAGNETIC_FIELD_TRANSMITS_SEMANTIC_EMOTION")
        with self.assertRaises(validator.MatrixError):
            validator.validate_matrix(data)

    def test_wet_skin_cannot_be_classed_as_protection(self) -> None:
        data = copy.deepcopy(self.base)
        safety = next(item for item in data["filaments"] if item["id"] == "electrical_fault_lightning_safety")
        safety["blocked_inferences"].remove("WET_SKIN_IS_PROTECTIVE")
        with self.assertRaises(validator.MatrixError):
            validator.validate_matrix(data)

    def test_human_body_cannot_be_safe_lightning_rod(self) -> None:
        data = copy.deepcopy(self.base)
        hair = next(item for item in data["filaments"] if item["id"] == "hair_static_point_geometry")
        hair["blocked_inferences"].remove("HUMAN_BODY_IS_A_SAFE_LIGHTNING_ROD")
        with self.assertRaises(validator.MatrixError):
            validator.validate_matrix(data)

    def test_singing_ion_causality_remains_blocked(self) -> None:
        data = copy.deepcopy(self.base)
        voice = next(item for item in data["filaments"] if item["id"] == "voice_acoustics_joy_relaxation")
        voice["blocked_inferences"].remove("IONIZATION_CAUSES_SINGING")
        with self.assertRaises(validator.MatrixError):
            validator.validate_matrix(data)

    def test_correlation_edge_must_remain_token_vazio_causal(self) -> None:
        data = copy.deepcopy(self.base)
        edge = next(item for item in data["cross_filament_edges"] if item["type"] == "CORRELATION_CANDIDATE_ONLY")
        edge["state"] = "EVIDENCED_EXTERNALLY"
        with self.assertRaises(validator.MatrixError):
            validator.validate_matrix(data)

    def test_local_measurement_cannot_be_silently_promoted(self) -> None:
        data = copy.deepcopy(self.base)
        data["filaments"][0]["local_measurement_state"] = "LOCAL_PASS"
        with self.assertRaises(validator.MatrixError):
            validator.validate_matrix(data)

    def test_new_workflow_requirement_is_rejected(self) -> None:
        data = copy.deepcopy(self.base)
        data["new_workflow_required"] = True
        with self.assertRaises(validator.MatrixError):
            validator.validate_matrix(data)


if __name__ == "__main__":
    unittest.main()
