from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "manifests" / "rll_edge_science_water_chem_bio.v1.json"
VALIDATOR_PATH = ROOT / "scripts" / "validate_rll_edge_science_water_matrix.py"
OPERATORS_PATH = ROOT / "scripts" / "rll_edge_science_operators.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


validator = load_module("edge_validator", VALIDATOR_PATH)
operators = load_module("edge_operators", OPERATORS_PATH)


class WaterEdgeScienceMatrixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.base = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_valid_manifest_passes(self) -> None:
        report = validator.validate(copy.deepcopy(self.base))
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["filaments"], 18)
        self.assertGreaterEqual(report["edges"], 12)
        self.assertGreaterEqual(report["vector_components"], 20)
        self.assertFalse(report["claim_allowed"])
        self.assertFalse(report["training_allowed"])
        self.assertFalse(report["new_workflow_required"])

    def test_forest_stream_cannot_imply_high_nitrate(self) -> None:
        data = copy.deepcopy(self.base)
        item = next(x for x in data["filaments"] if x["id"] == "catchment_source_context")
        item["blocked_inferences"].remove("FOREST_STREAM_IMPLIES_HIGH_NITRATE")
        with self.assertRaises(validator.MatrixError):
            validator.validate(data)

    def test_red_orange_lodo_cannot_identify_iron(self) -> None:
        data = copy.deepcopy(self.base)
        item = next(x for x in data["filaments"] if x["id"] == "iron_manganese_mineralogy")
        item["blocked_inferences"].remove("RED_ORANGE_BIOFILM_EQUALS_HIGH_IRON")
        with self.assertRaises(validator.MatrixError):
            validator.validate(data)

    def test_natural_zeolite_cannot_be_promoted_for_nitrate_by_name(self) -> None:
        data = copy.deepcopy(self.base)
        item = next(x for x in data["filaments"] if x["id"] == "zeolite_and_volcanic_media_identity")
        item["blocked_inferences"].remove("NATURAL_ZEOLITE_EFFECTIVELY_REMOVES_NITRATE_BY_DEFAULT")
        with self.assertRaises(validator.MatrixError):
            validator.validate(data)

    def test_below_detection_is_not_zero(self) -> None:
        data = copy.deepcopy(self.base)
        item = next(x for x in data["filaments"] if x["id"] == "analytical_measurement_and_qa_qc")
        item["blocked_inferences"].remove("BELOW_DETECTION_EQUALS_ZERO")
        with self.assertRaises(validator.MatrixError):
            validator.validate(data)

    def test_regulatory_limits_are_fail_closed(self) -> None:
        data = copy.deepcopy(self.base)
        data["regulatory_anchors"]["brazil_portaria_gm_ms_888_2021"]["nitrate_as_N_mg_L_vmp"] = 50.0
        with self.assertRaises(validator.MatrixError):
            validator.validate(data)

    def test_derivative_requires_units_and_reports_rate_only(self) -> None:
        result = operators.finite_derivative([0, 1, 3], [0, 2, 8], axis_unit="h", value_unit="mg/L")
        self.assertEqual(result["values"], [2.0, 3.0])
        self.assertEqual(result["unit"], "mg/L/h")
        self.assertEqual(result["claim"], "CHANGE_RATE_ONLY_NOT_CAUSAL_PROOF")
        with self.assertRaises(operators.OperatorDomainError):
            operators.finite_derivative([0, 1], [0, 1], axis_unit="", value_unit="mg/L")

    def test_antiderivative_requires_boundary_and_reconstructs_fixture(self) -> None:
        integral = operators.cumulative_trapezoid(
            [0, 1, 2], [1, 1, 1], boundary_value=5, axis_unit="h", value_unit="mg/L/h"
        )
        self.assertEqual(integral["values"], [5.0, 6.0, 7.0])
        self.assertIn("BOUNDARY", integral["claim"])

    def test_reverse_path_measures_error(self) -> None:
        result = operators.reconstruction_error([1, 2, 3], [1, 2, 3.1])
        self.assertGreater(result["rmse"], 0)
        self.assertEqual(result["claim"], "RECONSTRUCTION_QUALITY_NOT_ORIGIN_PROOF")

    def test_reciprocal_abstains_on_zero(self) -> None:
        result = operators.reciprocal([1, 0, 2])
        self.assertEqual(result["state"], "ABSTAIN_TOKEN_VAZIO_DOMAIN")

    def test_log1p_roundtrip(self) -> None:
        result = operators.log1p_roundtrip([0, 1, 9])
        self.assertLess(result["max_abs_error"], 1e-12)

    def test_log_log_requires_positive_domain_and_competing_models(self) -> None:
        result = operators.log_log_model_competition([1, 2, 4, 8], [2, 4, 8, 16])
        self.assertEqual(len(result["models"]), 2)
        self.assertIn(result["aic_preferred_candidate"], {"LINEAR", "POWER_LAW_LOG_LOG"})
        self.assertIn("NOT_POWER_LAW_PROOF", result["claim"])
        with self.assertRaises(operators.OperatorDomainError):
            operators.log_log_model_competition([0, 1, 2], [1, 2, 3])

    def test_nested_log_log_requires_x_greater_than_one_and_purpose(self) -> None:
        result = operators.nested_log_log([2, 10], purpose="scale exploration")
        self.assertEqual(result["operator"], "NESTED_LOG_LOG")
        with self.assertRaises(operators.OperatorDomainError):
            operators.nested_log_log([1, 2], purpose="bad domain")

    def test_brazil_combined_nitrate_nitrite_rule(self) -> None:
        passing = operators.combined_nitrate_nitrite_ratio(5.0, 0.5)
        failing = operators.combined_nitrate_nitrite_ratio(9.0, 0.2)
        self.assertTrue(passing["passes"])
        self.assertFalse(failing["passes"])
        self.assertAlmostEqual(passing["ratio"], 1.0)


if __name__ == "__main__":
    unittest.main()
