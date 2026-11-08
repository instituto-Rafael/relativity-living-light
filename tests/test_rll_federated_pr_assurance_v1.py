"""Adversarial offline tests for cross-repository assurance; no GitHub calls."""
from __future__ import annotations
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "tools/ci/rll_federated_pr_assurance_v1.py"
spec = importlib.util.spec_from_file_location("federated_pr", PATH)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(mod)
FIXTURE = ROOT / "data/contracts/rll_federated_pr_assurance_v1.json"

class FederatedPrAssuranceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = json.loads(FIXTURE.read_text(encoding="utf-8"))
    def mutate(self):
        return copy.deepcopy(self.base)
    def test_scoped_structure_is_not_merge(self):
        r = mod.verify(self.base)
        self.assertEqual(r["state"], "PASS_SCOPED_SCHEMA_ONLY")
        self.assertEqual(r["gate"], "HOLD_ALL_OBSERVED_PR")
        self.assertIs(r["claim_allowed"], False)
        self.assertIs(r["merge_allowed"], False)
    def test_open_pr_inventory_not_full_ci(self):
        r = mod.verify(self.base)
        self.assertEqual(r["inventory_personal_plus_institute"], 57)
        self.assertEqual(r["not_individually_assessed"], 57-len(self.base["records"]))
        self.assertEqual(r["full_ci_on_all_57"], "NOT_RUN")
    def test_exact_head_tamper_rejected(self):
        d = self.mutate(); d["records"][0]["ci"]["head_sha"] = "a"*40
        with self.assertRaisesRegex(ValueError, "EXACT_HEAD"): mod.verify(d)
    def test_non_hex_head_rejected(self):
        d = self.mutate();d["records"][0]["head_sha"] = "TOKEN_VAZIO"
        with self.assertRaises(ValueError): mod.verify(d)
    def test_failed_ci_cannot_disappear(self):
        d = self.mutate();d["records"][1]["risk_codes"].remove("CI_FAILURE")
        with self.assertRaisesRegex(ValueError, "FAILED_CI_PROMOTED"): mod.verify(d)
    def test_pending_requires_typed_gap(self):
        d = self.mutate();d["records"][0]["ci"]["pending"] = 1
        with self.assertRaisesRegex(ValueError, "PENDING_CI"): mod.verify(d)
    def test_quota_gap_cannot_disappear(self):
        d = self.mutate();d["records"][2]["missing_evidence"].remove("REMOTE_ARTIFACT_CUSTODY")
        with self.assertRaisesRegex(ValueError, "GAP_ERASED"): mod.verify(d)
    def test_device_receipt_cannot_be_inferred_from_apk(self):
        d = self.mutate();d["records"][0]["missing_evidence"].remove("DEVICE_OAUTH_INDEXER_RECEIPT")
        with self.assertRaisesRegex(ValueError, "GAP_ERASED"): mod.verify(d)
    def test_priority_cannot_be_understated(self):
        d = self.mutate();d["records"][0]["priority"] = "P2"
        with self.assertRaisesRegex(ValueError, "PRIORITY"): mod.verify(d)
    def test_external_pr_not_in_owned_inventory(self):
        d = self.mutate();d["records"][0]["repo"] = "FirebirdSQL/firebird"
        with self.assertRaisesRegex(ValueError, "OUT_OF_SCOPE"): mod.verify(d)
    def test_malformed_source_url_rejected(self):
        d = self.mutate();d["records"][0]["source_url"] += "?wrong=1"
        with self.assertRaisesRegex(ValueError, "SOURCE_URL"): mod.verify(d)
    def test_no_secrets_or_network_promoted(self):
        d = self.mutate();d["security"]["network_ci"] = "ALLOWED"
        with self.assertRaisesRegex(ValueError, "SECURITY"): mod.verify(d)
    def test_claim_not_auto_approved_on_all_success(self):
        d = self.mutate();d["records"][0]["claim_allowed"] = True
        with self.assertRaisesRegex(ValueError, "AUTOPROMOTION"): mod.verify(d)
    def test_duplicate_pr_rejected(self):
        d = self.mutate();d["records"].append(copy.deepcopy(d["records"][0]));d["reviewed_subset_count"] += 1
        with self.assertRaisesRegex(ValueError, "DUPLICATE"): mod.verify(d)
    def test_snapshot_staleness_visible_not_hidden(self):
        r = mod.verify(self.base, "2026-11-20")
        self.assertEqual(r["snapshot_freshness"], "STALE")
        self.assertEqual(r["gate"], "HOLD_ALL_OBSERVED_PR")
    def test_future_snapshot_rejected(self):
        with self.assertRaisesRegex(ValueError, "FUTURE"):mod.verify(self.base, "2026-11-07")
    def test_frozen_snapshot_digest(self):
        self.assertEqual(mod.verify(self.base)["snapshot_sha256_canonical_json"],
                         mod.verify(self.mutate())["snapshot_sha256_canonical_json"])
    def test_no_posterior_claim(self):
        self.assertEqual(mod.verify(self.base)["bayesian_science_posterior"],"TOKEN_VAZIO")

if __name__ == "__main__":
    unittest.main()
