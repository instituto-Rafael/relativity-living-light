from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "tools" / "validate_papers_rll_convergence_v1.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_papers_rll_convergence_v1", VALIDATOR)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_current_convergence_contract_passes() -> None:
    module = load_validator()
    data = module.load_contract()
    assert module.validate(data) == []


def test_unresolved_candidate_cannot_be_silently_routed() -> None:
    module = load_validator()
    data = module.load_contract()
    data["authorial_candidate_routes"][0]["rll_state"] = "ROUTED_TO_G1"
    errors = module.validate(data)
    assert any("math_gate=PASS" in e for e in errors)
    assert any("domain_relevance=ESTABLISHED" in e for e in errors)


def test_claim_allowed_must_remain_false() -> None:
    module = load_validator()
    data = module.load_contract()
    data["claim_allowed"] = True
    assert any("claim_allowed" in e for e in module.validate(data))


def test_negative_evidence_cannot_disappear() -> None:
    module = load_validator()
    data = module.load_contract()
    data["negative_evidence_preserved"] = []
    errors = module.validate(data)
    assert any("G6 blocked" in e for e in errors)
    assert any("geometry-to-RLL" in e for e in errors)


def test_branch_topology_gap_cannot_be_erased_or_bypassed() -> None:
    module = load_validator()
    data = module.load_contract()
    data["branch_topology_snapshot"]["state"] = "RESOLVED"
    errors = module.validate(data)
    assert any("branch topology gap" in e for e in errors)

    data = module.load_contract()
    data["authorial_candidate_routes"][0]["math_gate"] = "PASS"
    data["authorial_candidate_routes"][0]["domain_relevance"] = "ESTABLISHED"
    data["authorial_candidate_routes"][0]["exact_source_binding"] = "SRC-TEST"
    data["authorial_candidate_routes"][0]["target_rll_gate"] = "G1"
    data["authorial_candidate_routes"][0]["falsifier"] = "TEST-FALSIFIER"
    data["authorial_candidate_routes"][0]["rll_state"] = "ROUTED_TO_G1"
    errors = module.validate(data)
    assert any("forbidden while BRANCH_TOPOLOGY_GAP" in e for e in errors)
