import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/validate_sustainment_provenance_bindings.py"
REGISTRY = ROOT / "governance/ethics_license_complexity_sustainment.v1.json"

spec = importlib.util.spec_from_file_location("sustainment_provenance", TOOL)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(mod)


def test_all_declared_provenance_matches_actual_git_blob_bytes():
    report = mod.build_report(ROOT)
    assert report["state"] == "PASS_EXACT_GIT_BLOB_BINDINGS"
    assert report["claim_allowed"] is False
    assert report["scientific_confirmation"] is False
    assert report["legal_effect_claim"] is False
    assert report["binding_count"] == 8
    assert report["F_gap"] == []
    for binding in report["bindings"]:
        assert binding["expected_git_blob_sha1"] == binding["actual_git_blob_sha1"]


def test_git_blob_hash_detects_content_mutation(tmp_path):
    path = tmp_path / "x.txt"
    path.write_text("one\n", encoding="utf-8")
    first = mod.git_blob_sha1(path)
    path.write_text("two\n", encoding="utf-8")
    second = mod.git_blob_sha1(path)
    assert first != second
    assert len(first) == len(second) == 40


def test_wrong_declared_binding_fails_closed(tmp_path):
    path = tmp_path / "bound.txt"
    path.write_text("evidence\n", encoding="utf-8")
    with pytest.raises(ValueError, match="provenance mismatch"):
        mod._verify("bound.txt", "0" * 40, "fixture", tmp_path)


def test_registry_bindings_are_not_just_hex_placeholders():
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    for binding in data["source_bindings"]:
        path = ROOT / binding["path"]
        assert mod.git_blob_sha1(path) == binding["git_blob_sha1"]
