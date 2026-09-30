from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "data" / "pipelines" / "audit" / "public_custody_chain_gate.py"
CONTRACT_PATH = ROOT / "data" / "contracts" / "public_custody_chain_gate.v1.json"


def load_module():
    spec = importlib.util.spec_from_file_location("public_custody_chain_gate_test", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_seed_contract_passes_custody_gate_but_does_not_promote_claim() -> None:
    module = load_module()
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    result = module.validate_contract(contract)
    assert result.errors == ()
    assert result.status == "PASS_GATE_CUSTODY_ONLY"
    assert result.claim_allowed is False


def test_nonpublic_source_is_rejected() -> None:
    module = load_module()
    contract = {
        "schema": module.SCHEMA,
        "claim_allowed": False,
        "sources": [{
            "id": "S1",
            "public_record": False,
            "source_kind": "official_government",
            "url": "https://example.gov/source",
            "retrieved_at": "2026-09-28",
            "sha256": None,
        }],
        "events": [],
        "edges": [],
    }
    result = module.validate_contract(contract)
    assert "source_not_public:S1" in result.errors


def test_temporal_association_cannot_be_promoted_to_causality_without_evidence() -> None:
    module = load_module()
    base_source = {
        "public_record": True,
        "source_kind": "official_government",
        "retrieved_at": "2026-09-28",
        "sha256": None,
    }
    contract = {
        "schema": module.SCHEMA,
        "claim_allowed": False,
        "sources": [
            {"id": "S1", "url": "https://example.gov/a", **base_source},
            {"id": "S2", "url": "https://example.gov/b", **base_source},
        ],
        "events": [],
        "edges": [{
            "from": "A",
            "to": "B",
            "relation": "temporal_association",
            "state": "HYPOTHESIS",
            "causal": True,
            "source_refs": ["S1", "S2"],
            "causal_evidence_refs": ["S1"],
        }],
    }
    result = module.validate_contract(contract)
    assert "causal_edge_under_evidenced:0" in result.errors


def test_announced_investment_is_not_realized_cash_without_second_source() -> None:
    module = load_module()
    contract = {
        "schema": module.SCHEMA,
        "claim_allowed": False,
        "sources": [{
            "id": "S1",
            "public_record": True,
            "source_kind": "official_government",
            "url": "https://example.gov/announcement",
            "retrieved_at": "2026-09-28",
            "sha256": None,
        }],
        "events": [{
            "id": "E1",
            "event_type": "investment_announcement",
            "source_refs": ["S1"],
            "realized_cash": True,
        }],
        "edges": [],
    }
    result = module.validate_contract(contract)
    assert "announcement_promoted_to_cash_without_evidence:E1" in result.errors


def test_tax_record_requires_explicit_publication_basis() -> None:
    module = load_module()
    contract = {
        "schema": module.SCHEMA,
        "claim_allowed": False,
        "sources": [{
            "id": "S1",
            "public_record": True,
            "source_kind": "official_government",
            "url": "https://example.gov/disclosure",
            "retrieved_at": "2026-09-28",
            "sha256": None,
        }],
        "events": [{
            "id": "E1",
            "event_type": "tax_record",
            "source_refs": ["S1"],
        }],
        "edges": [],
    }
    result = module.validate_contract(contract)
    assert "tax_record_without_publication_basis:E1" in result.errors


def test_hazardous_procurement_routes_are_out_of_scope() -> None:
    module = load_module()
    contract = {
        "schema": module.SCHEMA,
        "claim_allowed": False,
        "sources": [{
            "id": "S1",
            "public_record": True,
            "source_kind": "official_corporate",
            "url": "https://example.com/public",
            "retrieved_at": "2026-09-28",
            "sha256": None,
        }],
        "events": [],
        "edges": [{
            "from": "supplier",
            "to": "launch_site",
            "relation": "propellant_supplier_route",
            "state": "OBSERVED",
            "causal": False,
            "source_refs": ["S1"],
        }],
    }
    result = module.validate_contract(contract)
    assert "hazardous_procurement_out_of_scope:0" in result.errors


def test_torus_stability_identity_and_wraparound() -> None:
    module = load_module()
    a = [0.1] * 7
    assert module.torus_stability(a, a) == 1.0
    stability = module.torus_stability([0.99] * 7, [0.01] * 7)
    assert 0.95 < stability <= 1.0


def test_state14_is_state_plus_delta() -> None:
    module = load_module()
    previous = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7]
    current = [0.2, 0.1, 0.3, 0.6, 0.5, 0.8, 0.4]
    state = module.state14(current, previous)
    assert state[:7] == current
    assert len(state) == 14
    expected_delta = [current_value - previous_value for current_value, previous_value in zip(current, previous)]
    assert state[7:] == expected_delta
