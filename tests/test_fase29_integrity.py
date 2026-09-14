from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "fase29_integrity", ROOT / "tools" / "validate_fase29_integrity.py")
assert SPEC and SPEC.loader
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


def fixtures():
    return (
        module.read_json(ROOT, module.LENSES_PATH),
        module.read_json(ROOT, module.BUNDLE_PATH),
        module.read_json(ROOT, module.RIGHTS_PATH),
        module.read_ledger(ROOT),
    )


class Fase29IntegrityTests(unittest.TestCase):

    def errors(self, lenses, bundle, rights, ledger):
        return module.validate_documents(lenses, bundle, rights, ledger, ROOT)

    def assert_lens_fails(self, word, lenses, bundle, rights, ledger):
        errors = self.errors(lenses, bundle, rights, ledger)
        self.assertTrue(errors[word], f"expected lens {word} to fail")

    def test_repository_contract_passes(self):
        report = module.validate_root(ROOT)
        self.assertEqual("PASS", report["status"], report)
        self.assertEqual(30, len(report["passed_lenses"]))

    def test_summary_vote_mismatch_is_rejected(self):
        lenses, bundle, rights, ledger = fixtures()
        bundle["summary"]["pass"] = 2
        self.assert_lens_fails("proporcionalidade", lenses, bundle, rights, ledger)

    def test_delta_aic_formula_is_recomputed(self):
        lenses, bundle, rights, ledger = fixtures()
        bundle["falsifiers"][0]["result"] = 2.0
        self.assert_lens_fails("aritmética", lenses, bundle, rights, ledger)

    def test_parameter_count_cannot_be_relabelled_as_dof(self):
        lenses, bundle, rights, ledger = fixtures()
        del bundle["falsifiers"][0]["parameter_count_rll"]
        self.assert_lens_fails("ambiguidade", lenses, bundle, rights, ledger)

    def test_threshold_status_mismatch_is_rejected(self):
        lenses, bundle, rights, ledger = fixtures()
        bundle["falsifiers"][2]["status"] = "PASS"
        self.assert_lens_fails("desvio", lenses, bundle, rights, ledger)

    def test_missing_real_source_is_rejected(self):
        lenses, bundle, rights, ledger = fixtures()
        bundle["falsifiers"][3]["source"] = "results/does-not-exist.json"
        self.assert_lens_fails("observabilidade", lenses, bundle, rights, ledger)

    def test_weak_pass_cannot_promote_claim(self):
        lenses, bundle, rights, ledger = fixtures()
        bundle["falsifiers"][4]["promotion_effect"] = "PROMOTE"
        self.assert_lens_fails("saturação", lenses, bundle, rights, ledger)

    def test_bayes_uncertainty_is_required(self):
        lenses, bundle, rights, ledger = fixtures()
        bundle["falsifiers"][3]["result_uncertainty"] = 0
        self.assert_lens_fails("fragilidade", lenses, bundle, rights, ledger)

    def test_license_cannot_be_verified_without_evidence(self):
        lenses, bundle, rights, ledger = fixtures()
        rights["datasets"][0]["license_verified"] = True
        rights["datasets"][0]["rights_complete"] = True
        self.assert_lens_fails("licença", lenses, bundle, rights, ledger)

    def test_unknown_rights_cannot_be_null(self):
        lenses, bundle, rights, ledger = fixtures()
        rights["datasets"][1]["license_evidence"] = None
        self.assert_lens_fails("silêncio", lenses, bundle, rights, ledger)

    def test_training_cannot_be_enabled_without_holdout(self):
        lenses, bundle, rights, ledger = fixtures()
        rights["datasets"][2]["training_allowed"] = True
        self.assert_lens_fails("independência", lenses, bundle, rights, ledger)

    def test_gap_requires_owner_action_and_exit(self):
        lenses, bundle, rights, ledger = fixtures()
        del rights["gaps"][0]["owner"]
        self.assert_lens_fails("reparabilidade", lenses, bundle, rights, ledger)

    def test_ledger_payload_tamper_breaks_hash(self):
        lenses, bundle, rights, ledger = fixtures()
        ledger[5]["description"] += " tampered"
        self.assert_lens_fails("conservação", lenses, bundle, rights, ledger)

    def test_ledger_previous_hash_tamper_breaks_genealogy(self):
        lenses, bundle, rights, ledger = fixtures()
        ledger[6]["previous_event_sha256"] = "0" * 64
        self.assert_lens_fails("genealogia", lenses, bundle, rights, ledger)

    def test_recorded_time_cannot_precede_effective_time(self):
        lenses, bundle, rights, ledger = fixtures()
        ledger[0]["recorded_at"] = "2025-01-01T00:00:00Z"
        self.assert_lens_fails("latência", lenses, bundle, rights, ledger)

    def test_recording_order_must_be_monotonic(self):
        lenses, bundle, rights, ledger = fixtures()
        ledger[2]["recorded_at"] = ledger[1]["recorded_at"]
        self.assert_lens_fails("monotonicidade", lenses, bundle, rights, ledger)

    def test_unknown_supersedes_event_is_rejected(self):
        lenses, bundle, rights, ledger = fixtures()
        ledger[4]["supersedes"] = "EVT-NOT-PRESENT"
        self.assert_lens_fails("genealogia", lenses, bundle, rights, ledger)

    def test_missing_lens_is_rejected(self):
        lenses, bundle, rights, ledger = fixtures()
        lenses["lenses"].pop()
        self.assert_lens_fails("cobertura", lenses, bundle, rights, ledger)

    def test_global_claim_promotion_is_rejected(self):
        lenses, bundle, rights, ledger = fixtures()
        bundle["claim_allowed"] = True
        self.assert_lens_fails("fronteira", lenses, bundle, rights, ledger)


if __name__ == "__main__":
    unittest.main()
