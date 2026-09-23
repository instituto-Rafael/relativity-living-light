#!/usr/bin/env python3
"""Stdlib-only tests for the RLL development security envelope."""

from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from internal.governance.development_guard import authorize_url, evaluate_operation

POLICY = json.loads(
    (ROOT / "data" / "governance" / "RLL_DEVELOPMENT_SECURITY_ENVELOPE_V1.json").read_text(
        encoding="utf-8"
    )
)
OPERATION = json.loads(
    (ROOT / "validacao_real" / "rx_operation.json").read_text(encoding="utf-8")
)


class DevelopmentGuardTests(unittest.TestCase):
    def test_rx_operation_is_allowed(self):
        receipt = evaluate_operation(POLICY, OPERATION)
        self.assertEqual(receipt["decision"], "ALLOW")
        self.assertFalse(receipt["claim_allowed"])

    def test_unknown_capability_is_blocked(self):
        op = copy.deepcopy(OPERATION)
        op["capabilities"].append("process.exec.arbitrary")
        receipt = evaluate_operation(POLICY, op)
        self.assertEqual(receipt["decision"], "BLOCK")
        self.assertTrue(any("forbidden_capabilities" in x for x in receipt["reasons"]))

    def test_personal_data_is_blocked(self):
        op = copy.deepcopy(OPERATION)
        op["personal_data_expected"] = True
        op["data_classes"].append("PERSONAL_DATA")
        receipt = evaluate_operation(POLICY, op)
        self.assertEqual(receipt["decision"], "BLOCK")

    def test_secret_requirement_is_blocked(self):
        op = copy.deepcopy(OPERATION)
        op["secrets_required"] = True
        receipt = evaluate_operation(POLICY, op)
        self.assertEqual(receipt["decision"], "BLOCK")

    def test_path_traversal_is_blocked(self):
        op = copy.deepcopy(OPERATION)
        op["writes"] = ["../outside/"]
        receipt = evaluate_operation(POLICY, op)
        self.assertEqual(receipt["decision"], "BLOCK")

    def test_autonomous_goal_setting_is_blocked(self):
        op = copy.deepcopy(OPERATION)
        op["autonomy"]["goal_setting"] = True
        receipt = evaluate_operation(POLICY, op)
        self.assertEqual(receipt["decision"], "BLOCK")

    def test_arbitrary_host_is_blocked(self):
        op = copy.deepcopy(OPERATION)
        op["network"]["hosts"].append("example.com")
        receipt = evaluate_operation(POLICY, op)
        self.assertEqual(receipt["decision"], "BLOCK")

    def test_authorize_declared_https_url(self):
        host = authorize_url(POLICY, "https://arxiv.org/abs/2503.14738")
        self.assertEqual(host, "arxiv.org")

    def test_reject_query_userinfo_and_custom_port(self):
        bad = [
            "https://arxiv.org/abs/2503.14738?x=1",
            "https://user@arxiv.org/abs/2503.14738",
            "https://arxiv.org:444/abs/2503.14738",
        ]
        for url in bad:
            with self.subTest(url=url):
                with self.assertRaises(ValueError):
                    authorize_url(POLICY, url)


if __name__ == "__main__":
    unittest.main()
