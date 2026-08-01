#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "validate_rare_events_registry.py"
SPEC = importlib.util.spec_from_file_location("rare_gate", MODULE_PATH)
assert SPEC and SPEC.loader
rare_gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(rare_gate)


class RareEventsRegistryGateTests(unittest.TestCase):
    def test_repository_registry_passes(self) -> None:
        registry = ROOT / "data" / "knowledge_forest" / "rare_events_claim_registry_v1.yml"
        self.assertEqual([], rare_gate.validate_text(registry.read_text(encoding="utf-8")))

    def test_rejects_claim_promotion_without_falsifier(self) -> None:
        invalid = """
schema_version: "1.0"
registry_id: TEST
claim_allowed: false
publication_ready: false
classification:
  allowed: [EVIDENCIADO, TOKEN_VAZIO]
invariants:
  - evidence_before_claim
  - preserve_unknowns
  - use_intervals_without_telemetry
  - declare_falsifiers
  - no_victim_as_proof_of_unrelated_theory
events:
  - event_id: E-1
    claims:
      - id: C-1
        state: EVIDENCIADO
metrics:
  explainability_index: {}
"""
        errors = rare_gate.validate_text(invalid)
        self.assertTrue(any("no falsifier" in error for error in errors), errors)

    def test_rejects_release_flags(self) -> None:
        invalid = """
schema_version: "1.0"
registry_id: TEST
claim_allowed: true
publication_ready: true
classification:
invariants:
  - evidence_before_claim
  - preserve_unknowns
  - use_intervals_without_telemetry
  - declare_falsifiers
  - no_victim_as_proof_of_unrelated_theory
events:
  - event_id: E-1
    claims:
      - id: C-1
        state: TOKEN_VAZIO
metrics:
"""
        errors = rare_gate.validate_text(invalid)
        self.assertTrue(any("claim_allowed" in error for error in errors), errors)
        self.assertTrue(any("publication_ready" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
