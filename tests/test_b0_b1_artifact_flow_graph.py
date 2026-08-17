import json
from pathlib import Path

from tools.validate_b0_b1_artifact_flow_graph import validate


GRAPH = Path("data/governance/RLL_B0_B1_ARTIFACT_FLOW_GRAPH_20260816_V1.json")


def _payload() -> dict:
    return json.loads(GRAPH.read_text(encoding="utf-8"))


def _status(payload: dict, artifact: str) -> dict:
    return next(item for item in payload["artifact_status"] if item["artifact"] == artifact)


def test_canonical_artifact_flow_graph_passes() -> None:
    assert validate(_payload()) == []


def test_custody_cannot_masquerade_as_executable_consumption() -> None:
    payload = _payload()
    _status(payload, "A_AUTO_RECEIPT")["executable_consumer"] = "VERIFIED"
    errors = validate(payload)
    assert any("without READS_EXECUTABLY edge" in error for error in errors)


def test_documentary_authority_cannot_masquerade_as_executable_consumption() -> None:
    payload = _payload()
    _status(payload, "A_WORKFLOW_REGISTRY")["executable_consumer"] = "VERIFIED"
    errors = validate(payload)
    assert any("without READS_EXECUTABLY edge" in error for error in errors)


def test_verified_reader_must_close_consumer_token_vazio() -> None:
    payload = _payload()
    _status(payload, "A_AUTO_STATE")["executable_consumer"] = "TOKEN_VAZIO_EXECUTABLE_CONSUMER"
    errors = validate(payload)
    assert any("keeps executable consumer TOKEN_VAZIO" in error for error in errors)


def test_every_artifact_requires_producer() -> None:
    payload = _payload()
    payload["edges"] = [edge for edge in payload["edges"] if not (
        edge["relation"] == "PRODUCES" and edge["to"] == "A_SYNC_RECEIPT"
    )]
    errors = validate(payload)
    assert any("A_SYNC_RECEIPT has no verified producer edge" in error for error in errors)


def test_unknown_endpoint_fails() -> None:
    payload = _payload()
    payload["edges"][0]["to"] = "TOKEN_VAZIO_UNKNOWN_ARTIFACT"
    errors = validate(payload)
    assert any("target is unknown" in error for error in errors)


def test_resolved_scope_counts_are_not_handwaved() -> None:
    payload = _payload()
    payload["resolved_scope"]["executable_consumer_edges"] = 99
    errors = validate(payload)
    assert any("resolved_scope.executable_consumer_edges" in error for error in errors)


def test_claim_and_merge_boundaries_fail_closed() -> None:
    payload = _payload()
    payload["claim_allowed"] = True
    payload["auto_merge"] = True
    errors = validate(payload)
    assert "claim_allowed must remain false" in errors
    assert "auto_merge must remain false" in errors
