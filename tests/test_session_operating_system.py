from __future__ import annotations

import copy
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools import validate_session_operating_system as validator


def current_contract() -> tuple[dict, dict]:
    return validator.load_contract()


def test_current_session_operating_system_is_valid() -> None:
    data, schema = current_contract()
    report = validator.validate_contract(data, schema)
    assert report["claim_allowed"] is False
    assert report["private_sources_pointer_only"] is True
    assert report["automatic_cross_repo_write"] is False
    assert report["organizational_syntropy_count"]["explicit_rollbacks"] == len(data["commit_plan"])


def test_private_source_content_must_be_pointer_only() -> None:
    data, schema = current_contract()
    broken = copy.deepcopy(data)
    private_source = next(
        source
        for group in broken["session_groups"]
        for source in group["source_links"]
        if source["visibility"] == "private"
    )
    private_source["content_mode"] = "source_content"
    with pytest.raises(ValueError, match="private source must be pointer_only"):
        validator.validate_contract(broken, schema)


def test_automatic_cross_repo_write_is_rejected() -> None:
    data, schema = current_contract()
    broken = copy.deepcopy(data)
    broken["execution_policy"]["automatic_cross_repo_write"] = True
    with pytest.raises(ValueError, match="schema validation failed|automatic_cross_repo_write"):
        validator.validate_contract(broken, schema)


def test_duplicate_session_group_is_rejected() -> None:
    data, schema = current_contract()
    broken = copy.deepcopy(data)
    broken["session_groups"].append(copy.deepcopy(broken["session_groups"][0]))
    with pytest.raises(ValueError, match="duplicate session group"):
        validator.validate_contract(broken, schema)


def test_commit_plan_requires_explicit_rollback() -> None:
    data, schema = current_contract()
    broken = copy.deepcopy(data)
    broken["commit_plan"][0]["rollback"] = ""
    with pytest.raises(ValueError, match="schema validation failed|rollback"):
        validator.validate_contract(broken, schema)


def test_report_can_be_materialized(tmp_path: Path) -> None:
    data, schema = current_contract()
    report = validator.validate_contract(data, schema)
    target = tmp_path / "report.json"
    target.write_text(__import__("json").dumps(report), encoding="utf-8")
    assert target.exists()
    assert report["organizational_syntropy_count"]["explicit_rollbacks"] == len(data["commit_plan"])
