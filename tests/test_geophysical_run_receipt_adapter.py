from rll.geophysical_run_receipt_adapter import (
    classify_receipt_use,
    validate_receipt_envelope,
)

PIN = "829d8511e33a14eed70f357e7fbdd39846ef8467"


def receipt_envelope(data_class="synthetic_fixture", evidence_state="SYNTHETIC_FIXTURE"):
    channels = {
        name: {
            "sha256": character * 64,
            "rows": 11,
            "calibration_id": f"CAL-{name.upper()}-001",
        }
        for name, character in zip(
            ("stress", "acoustic", "electric", "magnetic"),
            ("1", "2", "3", "4"),
        )
    }
    return {
        "producer_repo": "rafaelmeloreisnovo/Fisica",
        "producer_commit": PIN,
        "local_geophysics_is_cosmological_evidence": False,
        "receipt": {
            "schema": "geophysical_run_receipt_v1",
            "data_class": data_class,
            "evidence_state": evidence_state,
            "claim_allowed": False,
            "winner": "TOKEN_VAZIO",
            "manifest_sha256": "a" * 64,
            "receipt_sha256": "b" * 64,
            "channels": channels,
            "clock": {"synchronization_ok": True},
            "physical_gate": {
                "ready_for_analysis": evidence_state == "READY_FOR_ANALYSIS"
            },
        },
    }


def test_synthetic_receipt_is_valid_but_fixture_only():
    payload = receipt_envelope()
    assert validate_receipt_envelope(payload, expected_commit=PIN) == []
    assert classify_receipt_use(payload) == "TEST_FIXTURE_ONLY"


def test_synthetic_receipt_cannot_be_ready_for_physical_analysis():
    payload = receipt_envelope()
    payload["receipt"]["physical_gate"]["ready_for_analysis"] = True
    errors = validate_receipt_envelope(payload)
    assert any("synthetic fixture" in error for error in errors)
    assert classify_receipt_use(payload) == "BLOCKED"


def test_physical_ready_receipt_is_only_local_context_data():
    payload = receipt_envelope("physical_measurement", "READY_FOR_ANALYSIS")
    assert validate_receipt_envelope(payload, expected_commit=PIN) == []
    assert classify_receipt_use(payload) == "LOCAL_CONTEXT_DATA_READY"


def test_nonempty_winner_is_blocked_at_receipt_layer():
    payload = receipt_envelope()
    payload["receipt"]["winner"] = "piezoelectric_quartz"
    assert any("winner" in error for error in validate_receipt_envelope(payload))
    assert classify_receipt_use(payload) == "BLOCKED"


def test_tampered_channel_hash_is_blocked():
    payload = receipt_envelope()
    payload["receipt"]["channels"]["electric"]["sha256"] = "not-a-hash"
    assert any("electric.sha256" in error for error in validate_receipt_envelope(payload))


def test_old_or_wrong_producer_pin_is_rejected():
    payload = receipt_envelope()
    payload["producer_commit"] = "a765486980e0616204ae46979ef9ac3399199c12"
    assert any(
        "pinned contract" in error
        for error in validate_receipt_envelope(payload, expected_commit=PIN)
    )


def test_local_receipt_cannot_be_cosmological_evidence():
    payload = receipt_envelope("physical_measurement", "READY_FOR_ANALYSIS")
    payload["local_geophysics_is_cosmological_evidence"] = True
    assert any(
        "cosmological evidence" in error
        for error in validate_receipt_envelope(payload)
    )
