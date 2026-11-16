from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from rx.dispersion import route_dispersion
from rx.formula_selector import load_formula_bindings, select_formulas
from rx.orchestrator import (
    ROOT, _enforce_executable_contract, _route_artifact_contracts, orchestrate,
)
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
        self.assertEqual(result["regime_namespace"], "REGIME")
        self.assertIn("REGIME:G5", result["qualified_regimes"])
        self.assertEqual(result["qualified_primary_regime"], "REGIME:G5")

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

    def test_nonactive_plan_contract_is_rejected_before_route_execution(self):
        with patch("rx.orchestrator.active_contract", return_value=(
            "RX-STRUCTURE-D-PARITY-V1", {},
        )):
            with self.assertRaisesRegex(ValueError, "plan_physics_contract_differs"):
                _enforce_executable_contract(
                    "RX-FREESTANDING65-PARITY-V1", ["rx_multiprobe"],
                )
            _enforce_executable_contract(
                "RX-STRUCTURE-D-PARITY-V1", ["rx_multiprobe", "structure_d_rx"],
            )

    def test_multiprobe_cannot_use_unimplemented_active_contract(self):
        with patch("rx.orchestrator.active_contract", return_value=(
            "RX-FREESTANDING65-PARITY-V1", {},
        )):
            with self.assertRaisesRegex(ValueError, "route_requires_rx_structure_d"):
                _enforce_executable_contract(
                    "RX-FREESTANDING65-PARITY-V1", ["rx_multiprobe"],
                )

    def test_artifact_contract_readback_requires_all_ids(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            out = root / "results" / "structure_d"
            out.mkdir(parents=True)
            (out / "joint_real_likelihood_rx.json").write_text(json.dumps({
                "physics_contract": {"id": "RX-STRUCTURE-D-PARITY-V1"},
                "structure_d_successor": {
                    "physics_contract_id": "INCOMPATIBLE_CONTRACT",
                },
            }), encoding="utf-8")
            (out / "joint_real_likelihood_rx_manifest.json").write_text(
                json.dumps({"physics_contract_id": "RX-STRUCTURE-D-PARITY-V1"}),
                encoding="utf-8",
            )
            with patch("rx.orchestrator.ROOT", root):
                ids = _route_artifact_contracts("structure_d_rx")
                self.assertEqual(len(ids), 3)
                self.assertIn("INCOMPATIBLE_CONTRACT", ids)
                self.assertFalse(all(x == "RX-STRUCTURE-D-PARITY-V1" for x in ids))
                self.assertEqual(
                    _route_artifact_contracts("rx_multiprobe"),
                    ["TOKEN_VAZIO_CONTRACT_ID"],
                )

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
                "scientific_gate_graph.json",
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
