from __future__ import annotations

import copy
import json
from pathlib import Path

import yaml

from tools.validate_rll_manifold_index_scaffolding import validate_manifest

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/navigation/rll_manifold_index_scaffolding_v1.yml"
SCHEMA = ROOT / "schemas/rll_manifold_index_scaffolding_v1.schema.json"


def load_inputs():
    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    return manifest, schema


def test_current_scaffold_is_reconstructible():
    manifest, schema = load_inputs()
    receipt = validate_manifest(manifest, schema)

    assert receipt["valid"] is True, receipt["errors"]
    assert receipt["claim_allowed"] is False
    assert receipt["resolved_nodes"] == receipt["declared_nodes"]
    assert receipt["unresolved_nodes"] == []
    assert receipt["unresolved_edges"] == []


def test_structural_cycle_is_rejected_without_touching_semantic_cycles():
    manifest, schema = load_inputs()
    broken = copy.deepcopy(manifest)

    root_id = broken["root_id"]
    leaf_id = "MIDX:RLL:MANIFOLD_DRIVE:v1"
    broken["nodes"][leaf_id]["structural_children"].append(root_id)

    receipt = validate_manifest(broken, schema)

    assert receipt["valid"] is False
    assert any(error.startswith("structural_cycle:") for error in receipt["errors"])


def test_summary_provenance_gap_is_rejected():
    manifest, schema = load_inputs()
    broken = copy.deepcopy(manifest)

    node = broken["nodes"]["MIDX:RLL:SCIENTIFIC_NAV:v1"]
    node["source_refs"] = []
    node["index_refs"] = []

    receipt = validate_manifest(broken, schema)

    assert receipt["valid"] is False
    assert "provenance:no_source_or_index_ref:MIDX:RLL:SCIENTIFIC_NAV:v1" in receipt["errors"]
