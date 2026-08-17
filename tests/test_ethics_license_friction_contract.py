from jsonschema import Draft202012Validator

from tools.validate_ethics_license_friction_contract import (
    CONTRACT,
    MODULE,
    MODULE_SCHEMA,
    PARABLES,
    ROOT,
    load_json,
    load_ledger,
    validate,
)


def test_current_contract_passes_fail_closed_validator() -> None:
    assert validate(ROOT) == []


def test_ethics_module_conforms_to_existing_module_schema() -> None:
    module = load_json(ROOT, MODULE)
    schema = load_json(ROOT, MODULE_SCHEMA)
    assert list(Draft202012Validator(schema).iter_errors(module)) == []


def test_license_metadata_contradiction_remains_explicit_p0() -> None:
    ledger = load_ledger(ROOT)
    row = next(item for item in ledger if item["id"] == "ETHLIC-001")
    assert row["urgency"] == "P0"
    assert row["state"] == "CONTRADICTION"
    assert row["claim_allowed"] is False
    assert row["receipt"] == []


def test_all_urgency_ids_are_unique_and_urgent_rows_are_actionable() -> None:
    ledger = load_ledger(ROOT)
    ids = [row["id"] for row in ledger]
    assert len(ids) == len(set(ids))
    for row in ledger:
        if row["urgency"] in {"P0", "P1"}:
            for key in ("source", "use", "relation", "providencia", "falsifier", "provenance"):
                assert row[key]


def test_no_terminal_closure_without_receipt() -> None:
    ledger = load_ledger(ROOT)
    for row in ledger:
        if row["state"] in {"CLOSED", "VERIFIED", "RESOLVED"}:
            assert row["receipt"]


def test_semantic_chain_keeps_promise_metaphor_and_omega_outside_proof() -> None:
    contract = load_json(ROOT, CONTRACT)
    stages = {item["stage"]: item for item in contract["transformation_chain"]}
    assert stages["METAPHORS"]["evidence_capable"] is False
    assert stages["PROMISE"]["evidence_capable"] is False
    assert "never a proof" in stages["PROMISE"]["boundary"].lower()
    assert stages["OMEGA_N"]["evidence_capable"] is False
    assert "not an infinity claim" in stages["OMEGA_N"]["boundary"].lower()


def test_executable_verb_requires_input_output_test_and_receipt() -> None:
    contract = load_json(ROOT, CONTRACT)
    executable = next(item for item in contract["transformation_chain"] if item["stage"] == "EXECUTABLE_VERB")
    assert executable["evidence_capable"] is True
    for marker in ("input", "output", "test", "receipt"):
        assert marker in executable["boundary"].lower()


def test_symbolic_limit_phrase_has_runtime_counter_invariant() -> None:
    contract = load_json(ROOT, CONTRACT)
    boundary = contract["symbolic_boundary"]
    assert boundary["phrase"] == "NENHUM_LIMITE_E_REAL"
    assert boundary["classification"] == "SYMBOLIC_NARRATIVE"
    assert boundary["runtime_counter_invariant"] == "EVERY_OBSERVED_LIMIT_MUST_BE_EXPLICIT_TESTABLE_AND_RECEIPT_BOUND"


def test_parables_are_internal_references_never_evidence() -> None:
    parables = load_json(ROOT, PARABLES)
    assert parables["claim_allowed"] is False
    assert all(ref["evidence_role"] == "NONE" for ref in parables["references"])
    assert "parable_as_proof" in parables["forbidden"]
    assert "parable_as_legal_authority" in parables["forbidden"]


def test_external_sources_remain_unbound_until_repository_hash_exists() -> None:
    parables = load_json(ROOT, PARABLES)
    assert all(item["repo_hash"].startswith("TOKEN_VAZIO") for item in parables["external_sources"])


def test_forbidden_promotions_cover_legal_scientific_and_epistemic_edges() -> None:
    contract = load_json(ROOT, CONTRACT)
    forbidden = set(contract["forbidden_promotions"])
    assert "SYMBOLIC_NARRATIVE->LEGAL_TEXT" in forbidden
    assert "SYMBOLIC_NARRATIVE->SCIENTIFIC_EVIDENCE" in forbidden
    assert "PROMISE->PROOF" in forbidden
    assert "TOKEN_VAZIO->VERIFIED_WITHOUT_RECEIPT" in forbidden
    assert "INCERTEZA->CLOSED_WITHOUT_FALSIFIER" in forbidden


def test_contract_never_authorizes_machine_license_rewrite() -> None:
    contract = load_json(ROOT, CONTRACT)
    assert contract["auto_license_rewrite"] is False
    assert contract["license_coherence"]["automatic_resolution"] == "FORBIDDEN"
    assert contract["license_coherence"]["legal_enforceability"] == "TOKEN_VAZIO_LEGAL_REVIEW"
