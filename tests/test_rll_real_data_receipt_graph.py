"""Fail-closed static regression for the auxiliary Rx aggregate receipt graph."""
from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RealDataReceiptGraphTests(unittest.TestCase):
    def test_required_producers_precede_aggregate_gate(self):
        content = (ROOT / ".github/workflows/validacao_real.yml").read_text(
            encoding="utf-8",
        )
        gate = content.index("run: python3 tools/rx_development_gate.py")
        required = (
            "rx_physics_v2_decision_packet.py",
            "rll_perturbation_a1_linear_fluid_regularity_v1.py",
            "rll_perturbation_solver_readiness.py",
            "rll_current_rx_source_freeze.py",
            "rll_ws01_ws02_ws21_ws23_bridge.py",
        )
        locations = []
        for producer in required:
            marker = "python3 tools/" + producer + " --write"
            self.assertEqual(content.count(marker), 1)
            at = content.index(marker)
            self.assertLess(at, gate, producer)
            locations.append(at)
        self.assertEqual(locations, sorted(locations))
        self.assertIn("RLL_AUTHORITY_MODE: reviewed_ci_workflow", content)


if __name__ == "__main__":
    unittest.main()
