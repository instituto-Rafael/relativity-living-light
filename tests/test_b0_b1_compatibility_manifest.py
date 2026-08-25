import json
from pathlib import Path


MANIFEST = Path("data/governance/RLL_B0_B1_COMPATIBILITY_MANIFEST_20260816_V1.json")
GRAPH = Path("data/governance/RLL_B0_B1_DEPENDENCY_GRAPH_20260816_V1.json")
ARTIFACT_FLOW = Path("data/governance/RLL_B0_B1_ARTIFACT_FLOW_GRAPH_20260816_V1.json")


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_manifest_is_fail_closed_before_forward_port() -> None:
    payload = _load(MANIFEST)
    assert payload["state"] == "FROZEN_CANDIDATES_NOT_FORWARDED"
    assert payload["mode"] == "AUDIT_ONLY"
    assert payload["forward_port_authorized"] is False
    assert payload["claim_allowed"] is False
    assert payload["auto_merge"] is False
    assert payload["batches"]["B0"]["forwarded"] is False
    assert payload["batches"]["B1"]["forwarded"] is False


def test_manifest_freeze_matches_dependency_graph_sources() -> None:
    manifest = _load(MANIFEST)
    graph = _load(GRAPH)
    assert manifest["source_freeze"]["main"] == graph["source_refs"]["main"]
    assert manifest["source_freeze"]["rll/lab"] == graph["source_refs"]["rll/lab"]
    assert manifest["dependency_graph"]["nodes"] == len(graph["nodes"])
    assert manifest["dependency_graph"]["edges"] == len(graph["edges"])


def test_manifest_core_matches_declared_graph_scc() -> None:
    manifest = _load(MANIFEST)
    graph = _load(GRAPH)
    core = next(
        scc for scc in graph["strongly_connected_components"]
        if scc["id"] == manifest["dependency_graph"]["core_scc"]
    )
    assert set(manifest["compatibility_unit"]["members"]) == set(core["members"])
    assert manifest["compatibility_unit"]["strategy"] == "ATOMIC_COMPATIBILITY_GATE_NOT_ATOMIC_COMMIT"


def test_manifest_artifact_flow_counts_match_authority() -> None:
    manifest = _load(MANIFEST)
    flow = _load(ARTIFACT_FLOW)
    scope = flow["resolved_scope"]
    assert manifest["artifact_flow_graph"]["path"] == ARTIFACT_FLOW.as_posix()
    assert manifest["artifact_flow_graph"]["artifacts_mapped"] == scope["generated_artifacts_mapped"]
    assert manifest["artifact_flow_graph"]["producer_edges"] == scope["producer_edges"]
    assert manifest["artifact_flow_graph"]["executable_consumer_edges"] == scope["executable_consumer_edges"]
    assert manifest["artifact_flow_graph"]["custody_edges"] == scope["custody_edges"]
    assert manifest["artifact_flow_graph"]["documented_authority_edges"] == scope["documented_authority_edges"]


def test_required_gates_cannot_be_empty() -> None:
    payload = _load(MANIFEST)
    assert len(payload["required_acceptance_gates_before_forward_port"]) >= 10
    assert any("validate_b0_b1_artifact_flow_graph.py PASS" in gate for gate in payload["required_acceptance_gates_before_forward_port"])
    assert any("Branch Maturity Gate V2 PASS" in gate for gate in payload["required_acceptance_gates_before_forward_port"])
    assert any("full Python test suite PASS" in gate for gate in payload["required_acceptance_gates_before_forward_port"])


def test_history_materialization_and_named_consumer_gaps_remain_explicit() -> None:
    payload = _load(MANIFEST)
    assert "TOKEN_VAZIO_MAIN_RLL_LAB_HISTORY_RECONCILIATION" in payload["gaps"]
    assert "TOKEN_VAZIO_PER_BATCH_MATERIALIZATION_RECEIPT" in payload["gaps"]
    assert "TOKEN_VAZIO_EXECUTABLE_CONSUMER:A_WORKFLOW_REGISTRY" in payload["gaps"]
    assert "TOKEN_VAZIO_EXECUTABLE_CONSUMER:A_AUTO_RECEIPT" in payload["gaps"]
