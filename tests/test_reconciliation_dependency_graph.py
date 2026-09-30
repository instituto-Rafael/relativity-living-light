import copy
import json
from pathlib import Path

from tools.validate_reconciliation_dependency_graph import validate


GRAPH = Path("data/governance/RLL_B0_B1_DEPENDENCY_GRAPH_20260816_V1.json")


def _payload() -> dict:
    return json.loads(GRAPH.read_text(encoding="utf-8"))


def test_canonical_b0_b1_graph_passes() -> None:
    assert validate(_payload()) == []


def test_unknown_edge_endpoint_fails() -> None:
    payload = _payload()
    payload["edges"][0]["to"] = "TOKEN_VAZIO_UNKNOWN_NODE"
    errors = validate(payload)
    assert any("target is unknown" in error for error in errors)


def test_verified_edge_requires_evidence() -> None:
    payload = _payload()
    payload["edges"][0]["evidence"] = ""
    errors = validate(payload)
    assert any("requires explicit evidence" in error for error in errors)


def test_unverified_edge_cannot_masquerade_as_verified() -> None:
    payload = _payload()
    payload["edges"][0]["state"] = "TOKEN_VAZIO_EDGE"
    errors = validate(payload)
    assert any("unverified/invalid state" in error for error in errors)


def test_declared_scc_must_really_be_strongly_connected() -> None:
    payload = _payload()
    member = "B1_MAIN_AUTO_PROPOSAL"
    payload["edges"] = [
        edge for edge in payload["edges"]
        if edge["from"] != member
    ]
    errors = validate(payload)
    assert any("not strongly connected" in error for error in errors)


def test_claim_and_auto_merge_boundaries_fail_closed() -> None:
    payload = _payload()
    payload["claim_allowed"] = True
    payload["auto_merge"] = True
    errors = validate(payload)
    assert "claim_allowed must remain false" in errors
    assert "auto_merge must remain false" in errors
