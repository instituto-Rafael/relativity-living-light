from __future__ import annotations

import unittest

from tools.rll_closure_work_packets import build


class ClosureWorkPacketTests(unittest.TestCase):
    def test_every_packet_is_fail_closed_and_traceable(self):
        payload = build()
        self.assertFalse(payload["claim_allowed"])
        self.assertGreaterEqual(payload["workstream_count"], 29)
        self.assertGreater(payload["discipline_count"], 10)
        for rows in payload["packets"].values():
            for row in rows:
                self.assertFalse(row["claim_allowed"])
                self.assertTrue(row["workstream"].startswith("WS"))
                self.assertTrue(row["falsifier"])

    def test_closed_ws00_is_not_reassigned_as_ready_work(self):
        payload = build()
        ready_ws = {row["workstream"] for row in payload["ready_assignments"]}
        self.assertNotIn("WS00", ready_ws)


if __name__ == "__main__":
    unittest.main()
