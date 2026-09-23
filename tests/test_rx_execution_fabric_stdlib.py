from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from rx.dispersion import route_dispersion
from rx.formula_selector import load_formula_bindings, select_formulas
from rx.orchestrator import ROOT, orchestrate
from rx.region_router import classify_region


class RxExecutionFabricTests(unittest.TestCase):
    def test_cosmology_projection_routes_g5_g6(self):
        result = classify_region({
            "domain": "cosmology",
            "metric_or_approximation": "FLRW",
            "cosmological": True,
            "observational_projection": True,
        })
        self.assertIn("G5", result["regimes"])
        self.assertIn("G6", result["regimes"])
        self.assertEqual(result["primary_regime"], "G5")

    def test_correlated_data_blocks_diagonal_mode(self):
        result = route_dispersion({
            "covariance_mode": "diagonal",
            "spatial_correlation": True,
        })
        self.assertEqual(result["readiness"], "BLOCKED_CONTRACT")
        self.assertIn(
            "diagonal_covariance_forbidden_when_declared_correlations_exist",
            result["blocked_reasons"],
        )

    def test_formula_selection_is_regime_and_covariance_bound(self):
        registry = load_formula_bindings(
            ROOT / "data" / "governance" / "RLL_RX_FORMULA_BINDINGS_V1.json"
        )
        dispersion = route_dispersion({"covariance_mode": "dataset_contract"})
        selection = select_formulas(
            registry,
            ["G5", "G6"],
            ["H", "BAO", "CMB"],
            dispersion,
        )
        selected = {row["formula_id"] for row in selection["selected"]}
        rejected = {row["formula_id"] for row in selection["rejected"]}
        self.assertIn("RXF-G5-E2-H-V1", selected)
        self.assertIn("RXF-G5-BAO-V1", selected)
        self.assertIn("RXF-STAT-COVARIANCE-V1", selected)
        self.assertIn("MF-GEOMETRY-DIRECT-COSMOLOGY", rejected)
        self.assertNotIn("RXF-STAT-DIAGONAL-V1", selected)

    def test_dry_run_materializes_auditable_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = orchestrate(
                "configs/rll_execution_plan.v1.yml",
                execute=False,
                output_root=Path(tmp),
            )
            self.assertEqual(result["status"], "PASS")
            out = Path(result["output_dir"])
            required = {
                "execution_plan.json",
                "region_classification.json",
                "selected_formulas.json",
                "rejected_formulas.json",
                "covariance_contract.json",
                "metrics.json",
                "negative_results.json",
                "manifest.json",
                "receipt.json",
                "checksums.sha256",
            }
            self.assertTrue(required.issubset({p.name for p in out.iterdir()}))
            receipt = json.loads((out / "receipt.json").read_text(encoding="utf-8"))
            self.assertFalse(receipt["claim_allowed"])
            self.assertFalse(receipt["execute"])


if __name__ == "__main__":
    unittest.main()
