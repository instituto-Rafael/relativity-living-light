import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "validate_drive_formula_index.py"
MANIFEST = ROOT / "data" / "provenance" / "drive_formula_index_20260808.json"


def _module():
    spec = importlib.util.spec_from_file_location("drive_formula_validator", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_drive_formula_provenance_receipt_passes():
    module = _module()
    data = module.load_manifest(MANIFEST)
    assert module.validate_manifest(data) == []


def test_drive_formula_gap_is_explicit_and_fail_closed():
    module = _module()
    data = module.load_manifest(MANIFEST)
    assert data["claim_allowed"] is False
    assert data["counts"]["formula_hashes_unique"] == 320
    assert data["counts"]["graph_formula_nodes"] == 198
    assert data["counts"]["graph_missing_formula_nodes"] == 122
    assert len(data["missing_graph_formula_hashes"]) == 122


def test_hash_presence_never_promotes_mathematical_truth():
    module = _module()
    data = module.load_manifest(MANIFEST)
    inv = data["invariants"]
    assert inv["formula_hash_does_not_imply_mathematical_validity"] is True
    assert inv["hypothesis_tag_does_not_imply_proof"] is True
