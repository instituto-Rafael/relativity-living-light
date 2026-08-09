from rll.geophysical_systematics_bridge import (
    TOKEN_VAZIO,
    build_systematics_receipt,
    classify_systematics_use,
    missing_readiness_fields,
    validate_systematics_link,
)


def payload(receipt_use_class="LOCAL_CONTEXT_DATA_READY"):
    return {
        "schema": "rll_geophysical_systematics_link_v1",
        "claim_allowed": False,
        "mode": "diagnostic_only",
        "local_geophysics_is_cosmological_evidence": False,
        "likelihood_mutation_allowed": False,
        "cosmological_parameter_mutation_allowed": False,
        "receipt_use_class": receipt_use_class,
        "provenance": {
            "producer_repo": "rafaelmeloreisnovo/Fisica",
            "producer_commit": "8" * 40,
            "receipt_sha256": "9" * 64,
            "rll_preregistration_id": "RLL-SYS-001",
        },
        "target": {
            "dataset_id": "RLL-OBS-TEST-001",
            "observation_index_sha256": "a" * 64,
            "time_basis": "UTC",
            "location_basis": "observatory_site_id",
        },
        "join": {
            "method": "time_location_window",
            "max_time_offset_s": 1.0,
            "matched_observations": 4,
            "total_observations": 10,
        },
        "analysis": {
            "metric_id": "preregistered_residual_association_v1",
            "baseline_id": "permuted_time_windows_v1",
            "uncertainty_model": "bootstrap_by_observation_group_v1",
            "multiple_testing_control": "benjamini_hochberg_q_0.05",
            "falsifier": "association_absent_under_independent_site_control",
            "residual_mutation_allowed": False,
        },
    }


def test_complete_physical_join_is_diagnostic_ready_only():
    value = payload()
    assert validate_systematics_link(value) == []
    assert missing_readiness_fields(value) == []
    assert classify_systematics_use(value) == "SYSTEMATICS_DIAGNOSTIC_READY"
    receipt = build_systematics_receipt(value)
    assert receipt["classification"] == "SYSTEMATICS_DIAGNOSTIC_READY"
    assert receipt["claim_allowed"] is False
    assert receipt["likelihood_mutation_allowed"] is False
    assert receipt["cosmological_parameter_mutation_allowed"] is False
    assert len(receipt["source_contract_sha256"]) == 64
    assert len(receipt["receipt_sha256"]) == 64


def test_synthetic_fixture_never_reaches_observational_diagnostic():
    value = payload("TEST_FIXTURE_ONLY")
    assert validate_systematics_link(value) == []
    assert classify_systematics_use(value) == "TEST_FIXTURE_ONLY"


def test_context_only_receipt_stays_context_only():
    value = payload("CONTEXT_ONLY")
    assert validate_systematics_link(value) == []
    assert classify_systematics_use(value) == "CONTEXT_ONLY"


def test_missing_observation_alignment_remains_token_vazio():
    value = payload()
    value["target"]["observation_index_sha256"] = TOKEN_VAZIO
    value["join"]["method"] = TOKEN_VAZIO
    value["join"]["matched_observations"] = TOKEN_VAZIO
    assert validate_systematics_link(value) == []
    missing = missing_readiness_fields(value)
    assert "target.observation_index_sha256" in missing
    assert "join.method" in missing
    assert "join.matched_observations" in missing
    assert classify_systematics_use(value) == TOKEN_VAZIO


def test_zero_overlap_is_explicit_not_success():
    value = payload()
    value["join"]["matched_observations"] = 0
    assert validate_systematics_link(value) == []
    assert classify_systematics_use(value) == "NO_OVERLAP"


def test_attempt_to_promote_local_geophysics_is_blocked():
    value = payload()
    value["local_geophysics_is_cosmological_evidence"] = True
    errors = validate_systematics_link(value)
    assert any("cosmological evidence" in error for error in errors)
    assert classify_systematics_use(value) == "BLOCKED"


def test_likelihood_or_residual_mutation_is_blocked():
    value = payload()
    value["likelihood_mutation_allowed"] = True
    value["analysis"]["residual_mutation_allowed"] = True
    errors = validate_systematics_link(value)
    assert any("likelihood_mutation_allowed" in error for error in errors)
    assert any("residual_mutation_allowed" in error for error in errors)
    assert classify_systematics_use(value) == "BLOCKED"


def test_bad_receipt_hash_is_blocked():
    value = payload()
    value["provenance"]["receipt_sha256"] = "not-a-hash"
    assert any("receipt_sha256" in error for error in validate_systematics_link(value))
    assert classify_systematics_use(value) == "BLOCKED"


def test_matched_observations_cannot_exceed_total():
    value = payload()
    value["join"]["matched_observations"] = 11
    value["join"]["total_observations"] = 10
    assert any("cannot exceed" in error for error in validate_systematics_link(value))


def test_nonfinite_time_window_is_blocked():
    value = payload()
    value["join"]["max_time_offset_s"] = float("nan")
    assert any("finite non-negative" in error for error in validate_systematics_link(value))
