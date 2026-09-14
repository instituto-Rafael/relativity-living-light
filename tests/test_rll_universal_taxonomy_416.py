"""Tests for the additive RLL Universal Taxonomy 416 registry and overlay."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent.resolve()
REGISTRY = ROOT / "data/knowledge_taxonomy/rll_universal_taxonomy_416.v1.json"
BUILDER = ROOT / "tools/build_universal_taxonomy_overlay.py"
VALIDATOR = ROOT / "scripts/validate_rll_universal_taxonomy_416.py"


def load_registry():
    spec = importlib.util.spec_from_file_location("ut416_validator", VALIDATOR)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.load_registry(REGISTRY)


def test_strict_validator_passes():
    result = subprocess.run(
        [sys.executable, str(VALIDATOR), str(REGISTRY)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "modules=386" in result.stdout


def test_count_identity_and_cluster_reconciliation():
    data, modules = load_registry()
    assert data["source_provenance"]["baseline_macrothemes"] == 30
    assert len(modules) == 386
    assert 30 + len(modules) == 416
    computed = {}
    for module in modules:
        computed[module["cluster_id"]] = computed.get(module["cluster_id"], 0) + 1
    assert computed == {
        "I": 48,
        "II": 48,
        "III": 48,
        "IV": 48,
        "V": 48,
        "VI": 48,
        "VII": 47,
        "VIII": 51,
    }


def test_source_order_and_unique_ids():
    _, modules = load_registry()
    assert [module["source_index"] for module in modules] == list(range(1, 387))
    assert len({module["module_id"] for module in modules}) == 386


def test_claim_boundary_and_token_vazio():
    _, modules = load_registry()
    for module in modules:
        assert module["claim_allowed"] is False
        assert module["completion_state"].startswith("TOKEN_VAZIO")


def test_profiles_are_resolvable_and_nonempty():
    data, modules = load_registry()
    profiles = data["completion_profiles"]
    for module in modules:
        profile = profiles[module["completion_profile"]]
        assert profile["required_fields"]
        assert profile["description"]


def test_declared_count_mismatches_are_preserved_not_hidden():
    data, _ = load_registry()
    audit = data["count_audit"]
    by_cluster = {
        entry["cluster_id"]: entry for entry in audit["discrepancies"]
    }
    assert by_cluster["VII"]["declared"] == 48
    assert by_cluster["VII"]["computed"] == 47
    assert by_cluster["VIII"]["declared"] == 50
    assert by_cluster["VIII"]["computed"] == 51
    assert audit["global_count_consistent"] is True


def test_known_duplicate_is_linked():
    _, modules = load_registry()
    indexed = {module["module_id"]: module for module in modules}
    assert indexed["UTM-239"]["relations"] == [
        {"type": "DUPLICATE_OF", "target": "UTM-194"}
    ]


def test_overlay_build_and_item_compatibility(tmp_path):
    output = tmp_path / "overlay.json"
    result = subprocess.run(
        [
            sys.executable,
            str(BUILDER),
            "--registry",
            str(REGISTRY),
            "--output",
            str(output),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    overlay = json.loads(output.read_text(encoding="utf-8"))
    assert overlay["taxonomy_module_count"] == 386
    assert overlay["taxonomy_total"] == 416
    assert overlay["claim_allowed"] is False
    assert len(overlay["items"]) == 386
    for item in overlay["items"]:
        assert item["item_id"].startswith("KMIT-")
        assert item["kind"] in {"concept", "gap"}
        assert item["claim_allowed"] is False
        assert len(item["D_vector"]) == 7


def test_open_problem_and_explicit_gap_stay_void_in_overlay(tmp_path):
    output = tmp_path / "overlay.json"
    subprocess.run(
        [
            sys.executable,
            str(BUILDER),
            "--registry",
            str(REGISTRY),
            "--output",
            str(output),
        ],
        check=True,
    )
    items = json.loads(output.read_text(encoding="utf-8"))["items"]
    for item in items:
        if item["cluster_id"] in {"V", "VIII"}:
            assert item["maturity_class"] == "void"
            assert item["queue_state"] == "void"


def test_taxonomy_count_is_not_main_matrix_count():
    data, _ = load_registry()
    assert data["invariants"]["taxonomy_count_is_not_knowledge_matrix_count"] is True
