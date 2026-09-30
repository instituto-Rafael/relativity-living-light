from __future__ import annotations

from tools import rll_safe_expansion_gate as gate


def test_safe_expansion_contract_passes() -> None:
    report = gate.build_report()
    assert report["pass"] is True
    assert report["claim_allowed"] is False


def test_required_actionable_roots_are_visible() -> None:
    report = gate.build_report()
    assert "CMB-RADIATION-001" not in report["actionable_now"]
    assert "GROWTH-CS2-001" in report["actionable_now"]
    assert "GROWTH-GAUGE-001" in report["actionable_now"]
    assert "GROWTH-IC-001" in report["actionable_now"]
    assert "GROWTH-QMU-001" in report["actionable_now"]
    assert "GROWTH-SIGMA-001" in report["actionable_now"]
    assert "MAG-C09-001" in report["actionable_now"]
    assert "MAG-C10-001" in report["actionable_now"]
    assert "MAG-C11-001" in report["actionable_now"]
    assert "MAG-C12-001" in report["actionable_now"]
    assert "MAG-C14-001" in report["actionable_now"]
    assert "ALPHAXIV-SCHEMA-001" in report["actionable_now"]
    assert "ALPHAXIV-LICENSE-001" in report["actionable_now"]


def test_claim_stays_fail_closed() -> None:
    gaps = gate.load_json(gate.GAPS)
    assert gaps["claim_allowed"] is False
    assert all(item["claim_allowed"] is False for item in gaps["items"])
