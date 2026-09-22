from __future__ import annotations

from pathlib import Path

from tools.ci import quality_execution_monitor as q


def test_high_risk_for_governance_or_workflow_change() -> None:
    r = q.classify(["data/governance/x.json", "docs/note.md"])
    assert r["risk_class"] == "HIGH"
    assert r["critical_file_count"] == 1


def test_docs_only_is_low_risk() -> None:
    r = q.classify(["docs/a.md", "README.md"])
    assert r["docs_only"] is True
    assert r["risk_class"] == "LOW"


def test_focused_boundary_tests_are_counted() -> None:
    r = q.classify(["tests/test_real_seed_utils.py", "tests/test_orbital_outputs.py"])
    assert r["focused_boundary_test_file_count"] == 2


def test_missing_ttl_evidence_is_token_vazio_and_never_skip() -> None:
    r = q.build_report(
        workflow="python-tests",
        paths=["docs/a.md"],
        junit=None,
        last_full_pass_epoch=None,
        now_epoch=None,
        ttl_seconds=21600,
    )
    assert r["ttl"]["state"] == "TOKEN_VAZIO_LAST_FULL_PASS"
    assert r["skip_full_suite_allowed"] is False
    assert r["decision"] == "FULL_CANONICAL_REQUIRED"


def test_claim_boundary_is_focused_authority_not_full_suite() -> None:
    r = q.build_report(
        workflow="claim-boundary",
        paths=["scripts/validation/check_claim_boundary.py"],
        junit=None,
        last_full_pass_epoch=None,
        now_epoch=None,
        ttl_seconds=21600,
    )
    assert r["decision"] == "FOCUSED_BOUNDARY_REQUIRED"
    assert r["authority"] == "focused_claim_boundary_gate"
    assert r["skip_full_suite_allowed"] is False


def test_junit_is_counted(tmp_path: Path) -> None:
    p = tmp_path / "junit.xml"
    p.write_text(
        '<testsuite tests="7" failures="1" errors="0" skipped="2" time="1.25"></testsuite>',
        encoding="utf-8",
    )
    r = q.parse_junit(p)
    assert r["state"] == "OBSERVED"
    assert r["tests"] == 7
    assert r["failures"] == 1
    assert r["skipped"] == 2
    assert r["time_seconds"] == 1.25


def test_ttl_is_advisory_even_when_fresh() -> None:
    r = q.ttl_state(100, 150, 100)
    assert r["fresh"] is True
    assert r["enforced"] is False
