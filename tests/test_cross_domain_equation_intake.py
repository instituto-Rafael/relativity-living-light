import copy
import json
from pathlib import Path

from tools.validate_cross_domain_equation_intake import (
    DEFAULT_REGISTRY,
    semantic_findings,
    validate,
    write_reports,
)


def load_registry() -> dict:
    return json.loads(DEFAULT_REGISTRY.read_text(encoding="utf-8"))


def test_registry_is_valid_fail_closed_and_quarantined() -> None:
    findings, payload = validate()
    assert not findings
    assert payload["passed"] is True
    assert payload["claim_allowed"] is False
    assert payload["direct_model_integration_allowed"] is False
    assert payload["aggregation_rule"] == "NON_COMPENSATORY"
    assert payload["record_count"] >= 10
    assert payload["integration_state_counts"].get("READY_FOR_TEST", 0) == 0


def test_non_cosmology_record_cannot_open_direct_integration() -> None:
    registry = load_registry()
    mutated = copy.deepcopy(registry)
    mutated["records"][0]["direct_model_integration_allowed"] = True
    findings = semantic_findings(mutated)
    assert any(item["code"] == "CDI_DIRECT_INTEGRATION_OPEN" for item in findings)


def test_hypothesis_without_falsifier_is_rejected_semantically() -> None:
    registry = load_registry()
    mutated = copy.deepcopy(registry)
    record = mutated["records"][0]
    record["epistemic_class"] = "H"
    record["role"] = "testable_hypothesis"
    record["falsifier"] = None
    record["predicted_observation"] = "A measurable isolated observation."
    record["promotion_gate"] = "Independent preregistered replication."
    findings = semantic_findings(mutated)
    assert any(item["code"] == "CDI_HYPOTHESIS_NOT_TESTABLE" for item in findings)


def test_protected_cosmology_target_is_rejected() -> None:
    registry = load_registry()
    mutated = copy.deepcopy(registry)
    record = mutated["records"][0]
    record["integration_state"] = "READY_FOR_TEST"
    record["rll_relevance"] = "CANDIDATE_FOR_ISOLATED_TEST"
    record["integration_targets"] = ["scripts/joint_mcmc.py"]
    findings = semantic_findings(mutated)
    assert any(item["code"] == "CDI_PROTECTED_TARGET" for item in findings)


def test_reviewed_source_requires_reference_chain() -> None:
    registry = load_registry()
    mutated = copy.deepcopy(registry)
    record = mutated["records"][0]
    record["source_status"] = "REVIEWED"
    record["source_refs"] = []
    record["source_gap"] = None
    findings = semantic_findings(mutated)
    assert any(item["code"] == "CDI_SOURCE_REFS_MISSING" for item in findings)


def test_validation_receipt_contains_boundaries_and_checksum(tmp_path: Path) -> None:
    findings, payload = validate()
    assert not findings
    write_reports(payload, tmp_path)
    report = (tmp_path / "VALIDATION.md").read_text(encoding="utf-8")
    machine = (tmp_path / "validation.json").read_text(encoding="utf-8")
    checksums = (tmp_path / "CHECKSUMS.sha256").read_text(encoding="utf-8")
    assert "NON_COMPENSATORY" in report
    assert '"claim_allowed": false' in machine
    assert "VALIDATION.md" in checksums
