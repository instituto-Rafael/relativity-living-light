from __future__ import annotations

import copy

import pytest

from tools import validate_session_packet_public_mirror as validator


def current_mirror() -> tuple[dict, object]:
    return validator.load_mirror(), validator.FORMULA_BRIDGE


def test_current_public_mirror_is_valid() -> None:
    data, bridge = current_mirror()
    report = validator.validate_mirror(data, validator.MIRROR, bridge)
    assert report["valid"] is True
    assert report["claim_allowed"] is False
    assert report["private_content_copied"] is False
    assert report["private_commit_count"] == 20
    assert report["private_updated_path_count"] >= 1
    assert report["private_validator_execution_proven"] is False
    assert len(report["mirror_sha256"]) == 64
    assert len(report["formula_bridge_sha256"]) == 64


def test_wrapped_markdown_marker_is_normalized() -> None:
    wrapped = "Shared mathematical forms\ndo not imply shared physical ontology."
    expected = "Shared mathematical forms do not imply shared physical ontology."
    assert validator.normalize_text(wrapped) == expected


def test_private_content_copy_is_rejected() -> None:
    data, bridge = current_mirror()
    broken = copy.deepcopy(data)
    broken["private_source"]["private_content_copied"] = True
    with pytest.raises(ValueError, match="private_content_copied"):
        validator.validate_mirror(broken, validator.MIRROR, bridge)


def test_duplicate_commit_is_rejected() -> None:
    data, bridge = current_mirror()
    broken = copy.deepcopy(data)
    broken["private_commit_sequence"][1]["commit"] = (
        broken["private_commit_sequence"][0]["commit"]
    )
    with pytest.raises(ValueError, match="duplicate commit"):
        validator.validate_mirror(broken, validator.MIRROR, bridge)


def test_sequential_updates_to_same_path_are_allowed() -> None:
    data, bridge = current_mirror()
    paths = [entry["path"] for entry in data["private_commit_sequence"]]
    assert paths.count(".github/workflows/ci.yml") == 2
    report = validator.validate_mirror(data, validator.MIRROR, bridge)
    assert report["private_updated_path_count"] >= 1


def test_noncontiguous_order_is_rejected() -> None:
    data, bridge = current_mirror()
    broken = copy.deepcopy(data)
    broken["private_commit_sequence"][2]["order"] = 99
    with pytest.raises(ValueError, match="not contiguous"):
        validator.validate_mirror(broken, validator.MIRROR, bridge)


def test_private_validator_cannot_be_promoted() -> None:
    data, bridge = current_mirror()
    broken = copy.deepcopy(data)
    broken["private_ci"]["validator_execution_proven"] = True
    with pytest.raises(ValueError, match="must remain unproven"):
        validator.validate_mirror(broken, validator.MIRROR, bridge)


def test_sensitive_key_is_rejected() -> None:
    data, bridge = current_mirror()
    broken = copy.deepcopy(data)
    broken["private_source"]["private_key"] = "must-not-appear"
    with pytest.raises(ValueError, match="sensitive key"):
        validator.validate_mirror(broken, validator.MIRROR, bridge)
