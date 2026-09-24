from __future__ import annotations

import unittest

from tools.rll_current_rx_source_freeze import build as build_source_freeze
from tools.rll_ws01_ws02_ws21_ws23_bridge import (
    FREEZE_SPEC,
    _ws02_consistency,
    build,
)


class Ws01Ws02Ws21Ws23BridgeTests(unittest.TestCase):
    def test_ws02_surface_matches_g4_g5_and_hashes_source_custody(self):
        result = _ws02_consistency()
        self.assertEqual(result["state"], "PASS_WS02_SURFACE_CONSISTENCY")
        self.assertEqual(result["blockers"], [])
        self.assertEqual(len(result["input_sha256"]), 5)
        self.assertTrue(all(len(digest) == 64 for digest in result["input_sha256"].values()))
        self.assertFalse(result["claim_allowed"])

    def test_background_source_freeze_is_surface_specific_and_fail_closed(self):
        receipt = build_source_freeze(FREEZE_SPEC)
        self.assertEqual(receipt["scope"], "WS02/G4/G5 canonical background input surface")
        self.assertEqual(len(receipt["inputs"]), 5)
        self.assertFalse(receipt["scientific_gate_closed"])
        self.assertGreater(len(receipt["blockers"]), 0)
        self.assertTrue(all(row.get("sha256") for row in receipt["inputs"]))
        self.assertFalse(receipt["claim_allowed"])

    def test_pantheon_covariance_is_receipt_bound_when_not_committed(self):
        receipt = build_source_freeze(FREEZE_SPEC)
        by_id = {row["id"]: row for row in receipt["inputs"]}
        cov = by_id["PANTHEON_PLUS_STAT_SYS_COV"]
        self.assertFalse(cov["local_present"])
        self.assertEqual(
            cov["sha256"],
            "abf806d966485e64afdb359c87bffc0ecc00d05eff0a31ced66f247385df0fdc",
        )
        materialization = cov["observed"]["runtime_materialization"]
        self.assertTrue(materialization["valid"])
        self.assertEqual(
            materialization["source_file_key"],
            "Pantheon+SH0ES_STAT+SYS.cov",
        )
        self.assertNotIn(
            "PANTHEON_PLUS_STAT_SYS_COV:missing_local_input",
            receipt["blockers"],
        )
        self.assertIn("PANTHEON_PLUS_STAT_SYS_COV:rights", receipt["blockers"])

    def test_bridge_keeps_ws23_blocked_while_ws01_or_g0_is_open(self):
        receipt = build()
        self.assertEqual(receipt["state"], "BLOCKED_WS23_BACKGROUND_BINDINGS")
        self.assertFalse(receipt["workstreams"]["WS21"]["scientific_gate_closed"])
        self.assertGreater(len(receipt["workstreams"]["WS01"]["blocking_axes"]), 0)
        self.assertEqual(receipt["workstreams"]["WS23"]["ready_count"], 0)
        self.assertEqual(receipt["workstreams"]["WS23"]["total_count"], 3)
        self.assertEqual(
            receipt["workstreams"]["WS02"]["state"],
            "PASS_WS02_SURFACE_CONSISTENCY",
        )
        for row in receipt["workstreams"]["WS23"]["bindings"]:
            self.assertNotIn("WS02_SURFACE_NOT_VALID", row["blockers"])
        self.assertFalse(receipt["claim_allowed"])

    def test_no_perturbative_observable_is_promoted_by_background_bridge(self):
        receipt = build()
        self.assertFalse(receipt["growth_cmb_lensing_promotion"])
        ids = [row["binding_id"] for row in receipt["workstreams"]["WS23"]["bindings"]]
        self.assertEqual(ids, ["OGB-HZ-001", "OGB-BAO-001", "OGB-SN-001"])

    def test_ws01_axes_are_propagated_per_binding(self):
        receipt = build()
        by_id = {row["binding_id"]: row for row in receipt["workstreams"]["WS23"]["bindings"]}
        self.assertIn("WS01_AXIS:hz_dataset", by_id["OGB-HZ-001"]["blockers"])
        self.assertIn("WS01_AXIS:omega_r", by_id["OGB-BAO-001"]["blockers"])
        self.assertIn("WS01_AXIS:distance_integration", by_id["OGB-SN-001"]["blockers"])


if __name__ == "__main__":
    unittest.main()
