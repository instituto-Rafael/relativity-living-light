from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools/rll_atlas_g234_evidence_reconciliation.py"
SPEC = importlib.util.spec_from_file_location("g234_reconcile", MODULE_PATH)
assert SPEC and SPEC.loader
MOD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)


def current():
    return MOD.load(MOD.DEFAULT_RECORD)


def errors(candidate):
    return MOD.validate(candidate)


def test_current_reconciliation_is_valid_and_fail_closed():
    record = current()
    assert errors(record) == []
    receipt = MOD.build_receipt(record, [])
    assert receipt["valid"] is True
    assert receipt["claim_allowed"] is False
    assert receipt["effective_maturity_fraction"] == 0.333333
    assert receipt["negative_g6_state"] == "BLOCKED_G6_CONVERGENCE_OR_EVIDENCE"


def test_verified_promotion_is_rejected():
    record = current()
    record["effective_projection"][0]["status"] = "VERIFIED"
    record["effective_projection"][0]["maturity"] = 3
    assert any("only TOKEN_VAZIO -> PARTIAL" in e for e in errors(record))


def test_claim_promotion_is_rejected():
    record = current()
    record["claim_allowed"] = True
    assert any("claim_allowed" in e for e in errors(record))


def test_g6_blocked_negative_evidence_cannot_be_erased():
    record = current()
    record["negative_evidence"]["g6"]["state"] = "PASS"
    record["negative_evidence"]["g6"]["convergence_pass_all"] = True
    assert any("G6 blocked state" in e for e in errors(record))
    assert any("convergence_pass_all" in e for e in errors(record))


def test_failed_rhat_cannot_be_rewritten_below_threshold():
    record = current()
    record["negative_evidence"]["g6"]["rll_max_Rhat"] = 1.01
    assert any("Rhat failure" in e for e in errors(record))


def test_mandatory_blocker_cannot_disappear():
    record = current()
    record["mandatory_open_blockers"].remove("TOKEN_VAZIO_INDEPENDENT_REPLICATION")
    assert any("blocker set incomplete" in e for e in errors(record))


def test_runtime_digest_mismatch_is_rejected():
    record = current()
    record["runtime_evidence"]["artifact_digest"] = "sha256:" + "0" * 64
    assert any("artifact_digest mismatch" in e for e in errors(record))


def test_maturity_cannot_be_inflated():
    record = current()
    record["effective_maturity"]["effective_total"] = 8
    assert any("maturity accounting" in e for e in errors(record))
