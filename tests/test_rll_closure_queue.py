from __future__ import annotations

import unittest

from tools.rll_closure_queue import build


class RllClosureQueueTests(unittest.TestCase):
    def test_registry_is_acyclic_and_namespaces_are_qualified(self):
        payload = build()
        self.assertEqual(payload["schema"], "rll.closure_queue.v1")
        self.assertEqual(payload["namespace_contract"]["regime"], "REGIME:G0..G6")
        self.assertEqual(payload["namespace_contract"]["scientific_gate"], "SCI_GATE:G0..G11")
        self.assertFalse(payload["claim_allowed"])

    def test_workstream_ids_are_unique_and_dependencies_precede_children(self):
        payload = build()
        ids = [row["id"] for row in payload["queue"]]
        self.assertEqual(len(ids), len(set(ids)))
        positions = {value: index for index, value in enumerate(ids)}
        for row in payload["queue"]:
            for dep in row["dependencies"]:
                self.assertLess(positions[dep], positions[row["id"]])

    def test_scientific_decisions_remain_blocked(self):
        payload = build()
        by_id = {row["id"]: row for row in payload["queue"]}
        self.assertEqual(by_id["WS01"]["effective_state"], "BLOCKED_SCIENTIFIC_DECISION")
        self.assertEqual(by_id["WS03"]["effective_state"], "BLOCKED_SCIENTIFIC_DERIVATION")

    def test_termux_work_is_not_falsely_closed(self):
        payload = build()
        row = {item["id"]: item for item in payload["queue"]}["WS16"]
        self.assertNotEqual(row["effective_state"], "CLOSED")
        self.assertIn("TOKEN_VAZIO_PHYSICAL_EXECUTION", row["closes_tokens"])


if __name__ == "__main__":
    unittest.main()
