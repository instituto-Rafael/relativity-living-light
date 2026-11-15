"""Synthetic non-regression controls for authority graph v2; no GitHub API required."""
import copy
import json
from pathlib import Path

from tools.validate_rll_current_state_authority_graph_v2 import validate_graph

ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = ROOT / "data/governance/RLL_CURRENT_STATE_AUTHORITY_GRAPH_20261115_V2.json"
MD_PATH = ROOT / "docs/governance/RLL_CURRENT_STATE_AUTHORITY_GRAPH_20261115_V2.md"


def _sources():
    return json.loads(JSON_PATH.read_text(encoding="utf-8")), MD_PATH.read_text(encoding="utf-8")


def test_current_graph_human_machine_consistency_scoped():
    graph, md = _sources()
    assert validate_graph(graph, md) == []
    assert graph["claim_allowed"] is False
    assert graph["auto_merge"] is False
    assert graph["root_authority"] == "rll/lab"
    assert graph["source_method"].startswith("GitHub ")
    assert graph["refs"][0]["workflow_files"] == 135
    assert graph["refs"][1]["workflow_files"] == 120


def test_tampering_provider_sha_fails_closed():
    graph, md = _sources()
    candidate = copy.deepcopy(graph)
    candidate["refs"][1]["sha"] = "0" * 40
    assert "HUMAN_MACHINE_REF_MISMATCH" in validate_graph(candidate, md)


def test_false_merge_or_scientific_claim_rejected():
    graph, md = _sources()
    for key in ("auto_merge", "claim_allowed"):
        candidate = copy.deepcopy(graph)
        candidate[key] = True
        assert "UNAUTHORIZED_CLAIM_OR_MERGE" in validate_graph(candidate, md)


def test_swapping_ahead_behind_rejected_by_typed_topology():
    graph, md = _sources()
    candidate = copy.deepcopy(graph)
    edge = candidate["compare_edges"][2]
    edge["left_only_commits"], edge["right_only_commits"] = (
        edge["right_only_commits"], edge["left_only_commits"]
    )
    assert "TOPOLOGY_CLASSIFICATION_MISMATCH" in validate_graph(candidate, md)


def test_missing_gap_next_is_not_silently_filled():
    graph, md = _sources()
    candidate = copy.deepcopy(graph)
    candidate["gaps"][0].pop("next")
    assert "GAP_NOT_TYPED" in validate_graph(candidate, md)


def test_missing_empirical_layer_rejected():
    graph, md = _sources()
    candidate = copy.deepcopy(graph)
    candidate["layers"] = [x for x in candidate["layers"] if x["layer"] != "EMPIRICAL"]
    assert "EPISTEMIC_LAYERS_MISMATCH" in validate_graph(candidate, md)


def test_reported_workflow_count_cannot_be_negative():
    graph, md = _sources()
    candidate = copy.deepcopy(graph)
    candidate["refs"][0]["workflow_files"] = -1
    assert "INVALID_WORKFLOW_COUNT" in validate_graph(candidate, md)


def test_static_success_is_not_provider_freshness_or_scientific_pass():
    graph, md = _sources()
    assert validate_graph(graph, md) == []
    assert graph["kind"] == "PROVIDER_REF_SNAPSHOT_NOT_RUNTIME_OR_SCIENTIFIC_ATTESTATION"
    assert "NO_AUTO_MERGE" in [layer["claim"] for layer in graph["layers"]]
