import copy
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from tools.agent import rll_agent_seven_guards as guards

ROOT = Path(__file__).resolve().parents[1]


class AgentSevenGuardsTests(unittest.TestCase):
    def test_owner_reported_agent_pair_is_observed_without_network_or_secret_output(self):
        values = {"PATGITHUB": "fixture-github-sensitive-value",
                  "CLIMATE": "fixture-climate-sensitive-value", "GIT": "unassigned-sensitive-value"}
        with mock.patch.dict(os.environ, values, clear=True):
            with mock.patch.object(guards.authority, "github_get", side_effect=AssertionError("network")):
                with mock.patch.object(guards.dualapi, "_json_request", side_effect=AssertionError("network")):
                    receipt = guards.build_receipt("agents", ROOT)
        self.assertEqual(receipt["guards"], list(guards.REQUIRED_GUARDS))
        self.assertEqual(receipt["structural_status"], "PASS")
        self.assertEqual(receipt["runtime_readiness"], "BINDINGS_PRESENT_AUTH_UNVERIFIED")
        self.assertFalse(receipt["claim_allowed"])
        self.assertEqual(receipt["evidence"]["network_requests"], 0)
        encoded = json.dumps(receipt)
        for secret in values.values():
            self.assertNotIn(secret, encoded)
            self.assertNotIn(hashlib.sha256(secret.encode()).hexdigest(), encoded)

    def test_actions_names_are_not_automatically_agent_credentials(self):
        with mock.patch.dict(os.environ, {"GITPAT": "fixture-git", "CLIMA": "fixture-climate"}, clear=True):
            receipt = guards.build_receipt("agents", ROOT)
        self.assertEqual(receipt["runtime_readiness"], "BLOCKED_BINDING")

    def test_agent_names_are_not_automatically_actions_credentials(self):
        with mock.patch.dict(os.environ, {"PATGITHUB": "fixture-git", "CLIMATE": "fixture-climate"}, clear=True):
            receipt = guards.build_receipt("actions", ROOT)
        self.assertEqual(receipt["runtime_readiness"], "BLOCKED_BINDING")

    def test_missing_binding_and_ambiguous_binding_do_not_promote_readiness(self):
        for values in ({}, {"PATGITHUB": "fixture-a", "GH_PAT": "fixture-b", "CLIMATE": "fixture-c"}):
            with self.subTest(names=sorted(values)), mock.patch.dict(os.environ, values, clear=True):
                receipt = guards.build_receipt("agents", ROOT)
            self.assertEqual(receipt["runtime_readiness"], "BLOCKED_BINDING")
            self.assertTrue(receipt["uncertainty"]["open_items"])
            self.assertFalse(receipt["claim_allowed"])

    def test_explicit_selector_disambiguates_known_aliases(self):
        with mock.patch.dict(os.environ, {
            "PATGITHUB": "fixture-a", "GH_PAT": "fixture-b", "CLIMATE": "fixture-c",
            "RLL_AGENT_GITHUB_PAT_ENV": "PATGITHUB",
        }, clear=True):
            receipt = guards.build_receipt("agents", ROOT)
        self.assertEqual(receipt["runtime_readiness"], "BINDINGS_PRESENT_AUTH_UNVERIFIED")

    def test_missing_source_or_invalid_matrix_is_structural_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for path in guards.SOURCES:
                dest = root / path
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes((ROOT / path).read_bytes())
            path = root / "data/governance/RLL_EVIDENCE_EVOLUTION_MATRIX_V1.json"
            data = json.loads(path.read_text())
            data["claim_allowed"] = True
            path.write_text(json.dumps(data))
            self.assertEqual(guards.build_receipt("offline", root)["structural_status"], "FAIL")
            path.unlink()
            self.assertEqual(guards.build_receipt("offline", root)["structural_status"], "FAIL")

    def test_receipts_cannot_overwrite_history_and_hash_is_reproducible(self):
        receipt = guards.build_receipt("offline", ROOT)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "receipt.json"
            guards.write_receipt(receipt, path)
            original = path.read_bytes()
            with self.assertRaises(FileExistsError):
                guards.write_receipt(copy.deepcopy(receipt), path)
            self.assertEqual(path.read_bytes(), original)
            data = json.loads(original)
        digest = data.pop("payload_sha256")
        canonical = json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
        self.assertEqual(digest, hashlib.sha256(canonical.encode()).hexdigest())

    def test_offline_preflight_never_claims_runtime_or_rollback_execution(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            receipt = guards.build_receipt("offline", ROOT)
        self.assertEqual(receipt["runtime_readiness"], "NOT_CHECKED")
        self.assertFalse(receipt["rollback"]["executed"])
        self.assertEqual(receipt["reproduction"]["state"], "LOCAL_PREFLIGHT_ONLY")


if __name__ == "__main__":
    unittest.main()
