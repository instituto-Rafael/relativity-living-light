from __future__ import annotations

import importlib.util
import json
from copy import deepcopy
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "tools" / "validate_mpemba_horizon_closure.py"
SPEC = importlib.util.spec_from_file_location("validate_mpemba_horizon_closure", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def load(relpath: str):
    with (ROOT / relpath).open("r", encoding="utf-8") as handle:
        return json.load(handle)


class MpembaHorizonClosureTests(unittest.TestCase):
    def test_current_repository_closure_passes(self):
        result = MODULE.validate_all()
        self.assertEqual(result["status"], "PASS")
        self.assertTrue(result["no_untracked_gaps"])
        self.assertEqual(result["closure_items"], 8)
        self.assertFalse(result["global_scientific_claim_allowed"])

    def test_every_gap_has_operational_fields(self):
        closure = load("data/registries/rll_mpemba_horizon_closure_registry.v1.json")
        for item in closure["items"]:
            self.assertFalse(MODULE.REQUIRED_ITEM_KEYS - item.keys(), item["id"])
            self.assertTrue(item["urgency"])
            self.assertTrue(item["owner_class"])
            self.assertTrue(item["provenance"])
            self.assertTrue(item["verification"])
            self.assertTrue(item["falsifier"])
            self.assertTrue(item["close_when"])
        self.assertEqual(closure["priority_summary"]["untracked"], 0)

    def test_external_bytes_cannot_be_promoted_without_sha256(self):
        manifest = load("data/real/strong_gravity/eht_2026_d01_01_manifest.json")
        broken = deepcopy(manifest)
        broken["custody"]["sha256_verified"] = True
        with self.assertRaises(ValueError):
            MODULE.validate_manifest(broken)

    def test_unmaterialized_manifest_cannot_invent_file_inventory(self):
        manifest = load("data/real/strong_gravity/eht_2026_d01_01_manifest.json")
        broken = deepcopy(manifest)
        broken["custody"]["file_inventory"] = [
            {"name": "invented.uvfits", "sha256": "0" * 64}
        ]
        with self.assertRaises(ValueError):
            MODULE.validate_manifest(broken)

    def test_published_epochs_are_not_relabelled_preregistered(self):
        protocol = load("data/contracts/eht_mpemba_observational_protocol.v1.json")
        self.assertFalse(protocol["existing_public_data_scope"]["prospective_preregistration"])
        broken = deepcopy(protocol)
        broken["existing_public_data_scope"]["prospective_preregistration"] = True
        with self.assertRaises(ValueError):
            MODULE.validate_protocol(broken)

    def test_sparse_eht_epochs_do_not_auto_promote_mpemba_claim(self):
        protocol = load("data/contracts/eht_mpemba_observational_protocol.v1.json")
        self.assertFalse(
            protocol["current_decision"]["EHT_2026_D01_01_is_sufficient_for_BH_MP_06"]
        )
        self.assertEqual(protocol["current_decision"]["BH_MP_06"], "TOKEN_VAZIO")

    def test_hawking_thermometry_stays_token_vazio(self):
        contract = load("data/contracts/mpemba_horizon_falsifier.v1.json")
        states = {item["id"]: item["state"] for item in contract["claim_ledger"]}
        self.assertEqual(states["BH-MP-08"], "TOKEN_VAZIO")

    def test_priority_counts_are_exact(self):
        closure = load("data/registries/rll_mpemba_horizon_closure_registry.v1.json")
        MODULE.validate_closure(closure)
        broken = deepcopy(closure)
        broken["priority_summary"]["P0"] += 1
        with self.assertRaises(ValueError):
            MODULE.validate_closure(broken)

    def test_independent_replication_cannot_be_self_closed(self):
        closure = load("data/registries/rll_mpemba_horizon_closure_registry.v1.json")
        item = next(x for x in closure["items"] if x["id"] == "B10-CLOSE-P0-005")
        self.assertEqual(item["state"], "BLOCKED_EXTERNAL_INDEPENDENT_AUTHORITY")
        self.assertIn("cannot be self-closed", item["claim_boundary"])

    def test_source_registry_preserves_checksum_boundary(self):
        registry = load("data/registries/rll_recent_primary_sources_2026.json")
        MODULE.validate_source_registry(registry)


if __name__ == "__main__":
    unittest.main()
