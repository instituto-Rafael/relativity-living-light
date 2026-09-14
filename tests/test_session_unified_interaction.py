from __future__ import annotations

import copy
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools import validate_session_unified_interaction as validator


def current_manifest() -> dict:
    return validator.load_manifest()


def test_current_unified_session_is_valid() -> None:
    report = validator.validate_manifest(current_manifest())
    assert report["valid"] is True
    assert report["claim_allowed"] is False
    assert report["lens_count"] == 4
    assert report["repository_route_count"] == 5
    assert report["private_content_copied"] is False
    assert report["automatic_cross_repo_write"] is False


def test_private_papers_must_remain_pointer_only() -> None:
    broken = copy.deepcopy(current_manifest())
    route = next(item for item in broken["repository_routes"] if item["repository"] == "rafaelmeloreisnovo/papers")
    route["write_state"] = "IMPLEMENTED_IN_BRANCH"
    with pytest.raises(ValueError, match="POINTER_ONLY"):
        validator.validate_manifest(broken)


def test_runtime_repositories_cannot_be_promoted_without_execution() -> None:
    broken = copy.deepcopy(current_manifest())
    route = next(
        item
        for item in broken["repository_routes"]
        if item["repository"] == "rafaelmeloreisnovo/termux-app-rafacodephi"
    )
    route["write_state"] = "VERIFIED"
    with pytest.raises(ValueError, match="must not claim a write"):
        validator.validate_manifest(broken)


def test_token_vazio_inference_remains_forbidden() -> None:
    broken = copy.deepcopy(current_manifest())
    broken["mandatory_invariants"]["token_vazio_can_be_inferred"] = True
    with pytest.raises(ValueError, match="mandatory invariants"):
        validator.validate_manifest(broken)


def test_temporal_state_resolution_cannot_be_removed() -> None:
    broken = copy.deepcopy(current_manifest())
    broken["contradictions_resolved"] = [
        item for item in broken["contradictions_resolved"] if item["resolution"] != "TEMPORAL_STATE_SPLIT"
    ]
    with pytest.raises(ValueError, match="contradiction resolutions|incomplete"):
        validator.validate_manifest(broken)
