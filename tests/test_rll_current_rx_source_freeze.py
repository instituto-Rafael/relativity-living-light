from __future__ import annotations

import unittest

from tools.rll_current_rx_source_freeze import build


class CurrentRxSourceFreezeTests(unittest.TestCase):
    def test_current_bytes_are_frozen_but_g0_is_not_falsely_closed(self):
        receipt = build()
        self.assertEqual(receipt["scientific_gate"], "SCI_GATE:G0")
        self.assertFalse(receipt["scientific_gate_closed"])
        self.assertFalse(receipt["claim_allowed"])
        self.assertEqual(len(receipt["inputs"]), 5)
        self.assertTrue(all(row.get("sha256") for row in receipt["inputs"]))
        self.assertGreater(len(receipt["blockers"]), 0)

    def test_expected_current_data_surface_counts_match(self):
        receipt = build()
        by_id = {row["id"]: row for row in receipt["inputs"]}
        self.assertEqual(by_id["HZ_CC_28"]["observed"]["rows"], 28)
        self.assertEqual(by_id["DESI_DR2_BAO_13"]["observed"]["rows"], 13)
        self.assertEqual(by_id["DESI_DR2_BAO_COV_13"]["observed"]["rows"], 13)
        self.assertEqual(by_id["FSIGMA8_16"]["observed"]["rows"], 16)
        self.assertTrue(all(
            row.get("row_count_matches", True)
            for row in receipt["inputs"]
        ))


if __name__ == "__main__":
    unittest.main()
