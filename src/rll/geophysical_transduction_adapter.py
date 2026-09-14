"""Fail-closed adapter for geophysical-transduction results produced by Fisica."""
from __future__ import annotations

import re
from typing import Any, Mapping

CANONICAL_PRODUCER = "rafaelmeloreisnovo/Fisica"
SHA40 = re.compile(r"^[0-9a-f]{40}$")


def validate_external_result(
    payload: Mapping[str, Any],
    *,
    expected_commit: str | None = None,
) -> list[str]:
    errors: list[str] = []
    if payload.get("producer_repo") != CANONICAL_PRODUCER:
        errors.append("producer_repo must be the canonical Fisica repository")
    commit = payload.get("producer_commit")
    if not isinstance(commit, str) or not SHA40.fullmatch(commit):
        errors.append("producer_commit must be a 40-character lowercase SHA")
    elif expected_commit is not None and commit != expected_commit:
        errors.append("producer_commit does not match the pinned contract")
    if payload.get("claim_allowed") is not False:
        errors.append("claim_allowed must be false")
    if payload.get("local_geophysics_is_cosmological_evidence") is not False:
        errors.append("local geophysics must not be marked as cosmological evidence")
    mechanisms = payload.get("mechanisms")
    if not isinstance(mechanisms, dict) or not mechanisms:
        errors.append("mechanisms must be a non-empty object")
        mechanisms = {}
    winner = payload.get("winner")
    if winner != "TOKEN_VAZIO" and winner not in mechanisms:
        errors.append("winner must be TOKEN_VAZIO or a declared mechanism")
    if winner != "TOKEN_VAZIO":
        for field in (
            "preregistration_id",
            "uncertainty_model",
            "baseline_results",
            "falsifier_results",
            "raw_data_hashes",
        ):
            if not payload.get(field):
                errors.append(f"{field} is required before a non-empty winner")
    return errors


def classify_rll_use(payload: Mapping[str, Any]) -> str:
    """Return the only currently allowed RLL use class for a valid artifact."""
    errors = validate_external_result(payload)
    if errors:
        return "BLOCKED"
    if payload.get("winner") == "TOKEN_VAZIO":
        return "CONTEXT_ONLY"
    if payload.get("standard_mechanisms_rejected") is not True:
        return "CONTEXT_ONLY"
    if not payload.get("registered_rll_residual_model"):
        return "CONTEXT_ONLY"
    return "RESIDUAL_TEST_READY"
