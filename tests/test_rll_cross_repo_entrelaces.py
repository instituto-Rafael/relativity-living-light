from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from scripts.build_session_grafo_current_state_overlay import build_overlay, canonical_text
from tools.validate_rll_cross_repo_entrelaces import (
    load_json,
    validate_g4_overlay,
    validate_relationships,
    validate_registry,
    validate_schema,
)

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "knowledge_ecosystem" / "rll_cross_repo_entrelaces_v2.json"
SCHEMA = ROOT / "schemas" / "rll_cross_repo_entrelace.schema.json"
OVERLAY = ROOT / "results" / "session_grafo_fase17_20" / "current_state_overlay.json"


def _data():
    return load_json(REGISTRY)


def test_registry_is_valid():
    report = validate_registry()
    assert report["claim_allowed"] is False
    assert report["relationships"] == 5
    assert report["g4_snapshot_preserved"] is True
    assert report["g4_current_state_synchronized"] is True


def test_schema_rejects_claim_promotion():
    data = _data()
    schema = load_json(SCHEMA)
    data["claim_allowed"] = True
    with pytest.raises(ValueError, match="schema validation failed"):
        validate_schema(data, schema)


def test_duplicate_relationship_id_is_rejected():
    data = _data()
    data["relationships"].append(copy.deepcopy(data["relationships"][0]))
    with pytest.raises(ValueError, match="duplicate relationship id"):
        validate_relationships(data)


def test_documentation_bridge_cannot_fake_runtime_completion():
    data = _data()
    relation = next(
        item for item in data["relationships"]
        if item["relation_type"] == "DOCUMENTATION_BRIDGE"
    )
    relation["required_artifact"]["status"] = "VERIFIED"
    with pytest.raises(ValueError, match="cannot claim runtime artifact completion"):
        validate_relationships(data)


def test_external_path_cannot_be_token_vazio_after_verification():
    data = _data()
    data["relationships"][0]["target"]["path"] = "TOKEN_VAZIO"
    with pytest.raises(ValueError, match="path cannot be TOKEN_VAZIO"):
        validate_relationships(data)


def test_overlay_is_deterministic_and_preserves_residual_gap():
    expected = build_overlay()
    actual = json.loads(OVERLAY.read_text(encoding="utf-8"))
    assert actual == expected
    assert canonical_text() == OVERLAY.read_text(encoding="utf-8")
    transition = actual["transitions"][0]
    assert transition["from_state"] == "TOKEN_VAZIO"
    assert transition["to_state"] == "VERIFIED_LIMITED"
    assert transition["residual_limitation"]["status"] == "TOKEN_VAZIO"
    validate_g4_overlay()
