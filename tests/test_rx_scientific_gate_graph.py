from __future__ import annotations

import unittest

from rx.scientific_gates import build_scientific_gate_graph


class ScientificGateGraphTests(unittest.TestCase):
    def test_all_scientific_gates_are_qualified_and_fail_closed(self):
        graph = build_scientific_gate_graph()
        self.assertEqual(graph["gate_count"], 12)
        self.assertFalse(graph["claim_allowed"])
        self.assertFalse(graph["arbitrary_command_execution"])
        ids = {node["qualified_id"] for node in graph["nodes"]}
        self.assertEqual(ids, {"SCI_GATE:G%d" % i for i in range(12)})
        self.assertTrue(all(node["evidence_state"].startswith("TOKEN_VAZIO") for node in graph["nodes"]))

    def test_perturbation_gate_maps_only_to_blocking_derivation_executors(self):
        graph = build_scientific_gate_graph()
        by_id = {node["id"]: node for node in graph["nodes"]}
        g8 = by_id["G8"]
        self.assertEqual(g8["executor_state"], "BLOCKING_DERIVATION_AND_REGULARITY_EXECUTORS")
        self.assertEqual(
            [row["path"] for row in g8["executor_paths"]],
            [
                "tools/rll_perturbation_a1_linear_fluid_regularity_v1.py",
                "tools/rll_perturbation_solver_readiness.py",
            ],
        )
        self.assertTrue(all(row["present"] for row in g8["executor_paths"]))

    def test_g10_independent_replication_has_no_fake_executor(self):
        graph = build_scientific_gate_graph()
        g10 = {node["id"]: node for node in graph["nodes"]}["G10"]
        self.assertEqual(g10["mapping_state"], "TOKEN_VAZIO_EXECUTOR")
        self.assertEqual(g10["executor_paths"], [])


if __name__ == "__main__":
    unittest.main()
