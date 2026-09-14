#!/usr/bin/env python3
"""Unit tests for the RLL observational topology fail-closed contract."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tools.validate_rll_observational_topology import ROOT, TOPOLOGY, validate


def load_topology() -> dict:
    return json.loads(TOPOLOGY.read_text(encoding="utf-8"))


def by_id(data: dict, node_id: str) -> dict:
    for item in data["nodes"]:
        if item["id"] == node_id:
            return item
    raise AssertionError(f"missing fixture node {node_id}")


class ObservationalTopologyTests(unittest.TestCase):
    def validate_mutated(self, data: dict):
        with tempfile.TemporaryDirectory() as temp_dir:
            candidate = Path(temp_dir) / "topology.json"
            candidate.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            return validate(root=ROOT, path=candidate)

    def test_canonical_topology_is_fail_closed_and_valid(self):
        result = validate()
        self.assertEqual(result.decision, "PASS_FAIL_CLOSED_CONTRACT")
        self.assertEqual(result.errors, [])
        self.assertFalse(result.claim_allowed)
        self.assertFalse(result.publication_ready)
        self.assertEqual(result.node_count, 17)
        self.assertEqual(result.invalidated_nodes, ["OBS-BAO-DESI-DR2"])
        self.assertIn("TOKEN_VAZIO_TOPOLOGY_HZ_SYSTEMATIC_COVARIANCE", result.topology_only_tokens)

    def test_global_claim_switch_is_rejected(self):
        data = load_topology()
        data["claim_allowed"] = True
        result = self.validate_mutated(data)
        self.assertIn("claim_allowed must remain false", result.errors)

    def test_desi_invalidated_node_requires_contradiction_receipt(self):
        data = load_topology()
        by_id(data, "OBS-BAO-DESI-DR2").pop("contradiction")
        result = self.validate_mutated(data)
        self.assertIn(
            "INVALIDATED node OBS-BAO-DESI-DR2 requires a contradiction record",
            result.errors,
        )

    def test_unbound_token_cannot_modify_existing_queue(self):
        data = load_topology()
        by_id(data, "OBS-HZ-COSMIC-CHRONOMETERS")["token_binding"]["queue_effect"] = "existing_queue"
        result = self.validate_mutated(data)
        self.assertIn(
            "OBS-HZ-COSMIC-CHRONOMETERS unbound token must be nonempty and topology_only",
            result.errors,
        )

    def test_required_propagation_node_cannot_disappear(self):
        data = load_topology()
        data["nodes"] = [node for node in data["nodes"] if node["id"] != "OBS-RM-POLARIZATION"]
        data["topological_edges"] = [
            edge
            for edge in data["topological_edges"]
            if edge["from"] != "OBS-RM-POLARIZATION" and edge["to"] != "OBS-RM-POLARIZATION"
        ]
        result = self.validate_mutated(data)
        self.assertTrue(
            any(error.startswith("missing required topology nodes:") for error in result.errors),
            result.errors,
        )

    def test_cycles_are_rejected(self):
        data = load_topology()
        mechanism = by_id(data, "MECH-RLL-LINEAR-PERTURBATION-CLOSURE")
        mechanism["dependencies"].append("OBS-H0-SHOES")
        data["topological_edges"].append(
            {
                "from": "OBS-H0-SHOES",
                "to": "MECH-RLL-LINEAR-PERTURBATION-CLOSURE",
                "relation": "must_precede",
                "why": "Mutation fixture creates a prohibited cycle.",
            }
        )
        result = self.validate_mutated(data)
        self.assertIn("topological_edges must be acyclic", result.errors)


if __name__ == "__main__":
    unittest.main()

