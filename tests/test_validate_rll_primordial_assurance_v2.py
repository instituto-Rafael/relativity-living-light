from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "validate_rll_primordial_assurance_v2.py"
SPEC = importlib.util.spec_from_file_location("validate_rll_primordial_assurance_v2", MODULE_PATH)
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mod
SPEC.loader.exec_module(mod)


def test_current_artifacts_pass_fail_closed_validator():
    result = mod.run()
    assert result["errors"] == [], json.dumps(result["errors"], ensure_ascii=False, indent=2)
    assert result["status"] == "PASS"
    assert result["claim_allowed"] is False
    assert result["negative_fixture_count"] == 8


def test_claim_promotion_is_rejected():
    base = {"receipt": mod.load(mod.RECEIPT), "hotqcd": mod.load(mod.HOTQCD), "evidence": mod.load(mod.EVIDENCE), "attention": mod.load(mod.ATTENTION)}
    base["receipt"]["claim_allowed"] = True
    assert "claim_allowed must remain false" in mod.validate(base["receipt"], base["hotqcd"], base["evidence"], base["attention"])


def test_documented_censorship_without_provenance_is_rejected():
    base = {"receipt": mod.load(mod.RECEIPT), "hotqcd": mod.load(mod.HOTQCD), "evidence": mod.load(mod.EVIDENCE), "attention": mod.load(mod.ATTENTION)}
    row = mod._attention(base["attention"], "CENSORSHIP_CLASSIFICATION")
    row["epistemic_status"] = "DOCUMENTED_CENSORSHIP"
    row["provenance"] = None
    assert "censorship promotion requires provenance" in mod.validate(base["receipt"], base["hotqcd"], base["evidence"], base["attention"])


def test_superseded_hotqcd_activation_is_rejected():
    base = {"receipt": mod.load(mod.RECEIPT), "hotqcd": mod.load(mod.HOTQCD), "evidence": mod.load(mod.EVIDENCE), "attention": mod.load(mod.ATTENTION)}
    base["hotqcd"]["superseded_provenance"]["active_use"] = True
    assert "superseded HotQCD result cannot be active" in mod.validate(base["receipt"], base["hotqcd"], base["evidence"], base["attention"])
