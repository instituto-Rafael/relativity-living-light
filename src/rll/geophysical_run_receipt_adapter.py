"""Fail-closed consumer for raw geophysical run receipts produced by Fisica.

A valid receipt proves only structural integrity, synchronization and custody of
local experimental channels. It never becomes cosmological evidence by itself.
"""
from __future__ import annotations

import re
from typing import Any, Mapping

CANONICAL_PRODUCER = "rafaelmeloreisnovo/Fisica"
RECEIPT_SCHEMA = "geophysical_run_receipt_v1"
REQUIRED_CHANNELS = ("stress", "acoustic", "electric", "magnetic")
SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA64 = re.compile(r"^[0-9a-f]{64}$")


def _valid_sha64(value: Any) -> bool:
    return isinstance(value, str) and SHA64.fullmatch(value) is not None


def validate_receipt_envelope(
    payload: Mapping[str, Any],
    *,
    expected_commit: str | None = None,
) -> list[str]:
    errors: list[str] = []
    if payload.get("producer_repo") != CANONICAL_PRODUCER:
        errors.append("producer_repo must be the canonical Fisica repository")

    commit = payload.get("producer_commit")
    if not isinstance(commit, str) or SHA40.fullmatch(commit) is None:
        errors.append("producer_commit must be a 40-character lowercase SHA")
    elif expected_commit is not None and commit != expected_commit:
        errors.append("producer_commit does not match the pinned contract")

    if payload.get("local_geophysics_is_cosmological_evidence") is not False:
        errors.append("local geophysics must not be marked as cosmological evidence")

    receipt = payload.get("receipt")
    if not isinstance(receipt, dict):
        errors.append("receipt must be an object")
        return errors

    if receipt.get("schema") != RECEIPT_SCHEMA:
        errors.append(f"receipt.schema must be {RECEIPT_SCHEMA}")
    if receipt.get("claim_allowed") is not False:
        errors.append("receipt.claim_allowed must be false")
    if receipt.get("winner") != "TOKEN_VAZIO":
        errors.append("raw-data receipt winner must remain TOKEN_VAZIO")
    if not _valid_sha64(receipt.get("manifest_sha256")):
        errors.append("receipt.manifest_sha256 must be lowercase SHA-256")
    if not _valid_sha64(receipt.get("receipt_sha256")):
        errors.append("receipt.receipt_sha256 must be lowercase SHA-256")

    data_class = receipt.get("data_class")
    evidence_state = receipt.get("evidence_state")
    if data_class == "synthetic_fixture":
        if evidence_state != "SYNTHETIC_FIXTURE":
            errors.append("synthetic fixture must remain SYNTHETIC_FIXTURE")
    elif data_class == "physical_measurement":
        if evidence_state not in {
            "TOKEN_VAZIO",
            "BLOCKED_CLOCK_SYNC",
            "READY_FOR_ANALYSIS",
        }:
            errors.append("physical measurement evidence_state is invalid")
    else:
        errors.append("receipt.data_class is invalid")

    channels = receipt.get("channels")
    if not isinstance(channels, dict):
        errors.append("receipt.channels must be an object")
        channels = {}
    for channel_id in REQUIRED_CHANNELS:
        channel = channels.get(channel_id)
        prefix = f"receipt.channels.{channel_id}"
        if not isinstance(channel, dict):
            errors.append(f"{prefix} is required")
            continue
        if not _valid_sha64(channel.get("sha256")):
            errors.append(f"{prefix}.sha256 must be lowercase SHA-256")
        rows = channel.get("rows")
        if not isinstance(rows, int) or isinstance(rows, bool) or rows < 2:
            errors.append(f"{prefix}.rows must be an integer >= 2")
        calibration_id = channel.get("calibration_id")
        if not isinstance(calibration_id, str) or not calibration_id:
            errors.append(f"{prefix}.calibration_id is required")

    clock = receipt.get("clock")
    if not isinstance(clock, dict):
        errors.append("receipt.clock must be an object")
    elif not isinstance(clock.get("synchronization_ok"), bool):
        errors.append("receipt.clock.synchronization_ok must be boolean")

    physical_gate = receipt.get("physical_gate")
    if not isinstance(physical_gate, dict):
        errors.append("receipt.physical_gate must be an object")
    else:
        ready = physical_gate.get("ready_for_analysis")
        if not isinstance(ready, bool):
            errors.append("receipt.physical_gate.ready_for_analysis must be boolean")
        if ready and evidence_state != "READY_FOR_ANALYSIS":
            errors.append("ready_for_analysis requires READY_FOR_ANALYSIS evidence_state")
        if data_class == "synthetic_fixture" and ready:
            errors.append("synthetic fixture cannot be ready for physical analysis")

    return errors


def classify_receipt_use(payload: Mapping[str, Any]) -> str:
    """Classify the maximum RLL use allowed for a valid local-data receipt."""
    if validate_receipt_envelope(payload):
        return "BLOCKED"
    receipt = payload["receipt"]
    if receipt["data_class"] == "synthetic_fixture":
        return "TEST_FIXTURE_ONLY"
    if (
        receipt["evidence_state"] == "READY_FOR_ANALYSIS"
        and receipt["clock"]["synchronization_ok"] is True
        and receipt["physical_gate"]["ready_for_analysis"] is True
    ):
        return "LOCAL_CONTEXT_DATA_READY"
    return "CONTEXT_ONLY"
