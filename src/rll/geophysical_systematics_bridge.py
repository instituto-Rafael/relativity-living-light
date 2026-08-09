"""Fail-closed bridge from local geophysical receipts to RLL systematics tests.

The bridge can authorize a *diagnostic* comparison only when a physical Fisica
receipt has custody, the RLL target observations can be joined in time/location,
and the residual test was preregistered. It never authorizes cosmological
parameter or likelihood mutation and never converts local geophysics into
cosmological evidence.
"""
from __future__ import annotations

from hashlib import sha256
import json
import math
import re
from typing import Any, Mapping

TOKEN_VAZIO = "TOKEN_VAZIO"
SCHEMA = "rll_geophysical_systematics_link_v1"
CANONICAL_PRODUCER = "rafaelmeloreisnovo/Fisica"
ALLOWED_RECEIPT_USE = {
    "TEST_FIXTURE_ONLY",
    "CONTEXT_ONLY",
    "LOCAL_CONTEXT_DATA_READY",
}
ALLOWED_JOIN_METHODS = {"time_location_window"}
SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA64 = re.compile(r"^[0-9a-f]{64}$")

READINESS_PATHS = (
    ("provenance", "rll_preregistration_id"),
    ("target", "observation_index_sha256"),
    ("target", "time_basis"),
    ("target", "location_basis"),
    ("join", "method"),
    ("join", "max_time_offset_s"),
    ("join", "matched_observations"),
    ("join", "total_observations"),
    ("analysis", "metric_id"),
    ("analysis", "baseline_id"),
    ("analysis", "uncertainty_model"),
    ("analysis", "multiple_testing_control"),
    ("analysis", "falsifier"),
)


def _canonical_json_bytes(value: Mapping[str, Any]) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def _is_present(value: Any) -> bool:
    return value not in (None, "", TOKEN_VAZIO)


def _valid_sha40(value: Any) -> bool:
    return isinstance(value, str) and SHA40.fullmatch(value) is not None


def _valid_sha64(value: Any) -> bool:
    return isinstance(value, str) and SHA64.fullmatch(value) is not None


def _object(payload: Mapping[str, Any], key: str, errors: list[str]) -> Mapping[str, Any]:
    value = payload.get(key)
    if not isinstance(value, dict):
        errors.append(f"{key} must be an object")
        return {}
    return value


def _read_path(payload: Mapping[str, Any], path: tuple[str, str]) -> Any:
    parent = payload.get(path[0])
    if not isinstance(parent, dict):
        return None
    return parent.get(path[1])


def validate_systematics_link(payload: Mapping[str, Any]) -> list[str]:
    """Validate the cross-repository systematics contract without promoting it."""
    errors: list[str] = []

    if payload.get("schema") != SCHEMA:
        errors.append(f"schema must be {SCHEMA}")
    if payload.get("claim_allowed") is not False:
        errors.append("claim_allowed must be false")
    if payload.get("mode") != "diagnostic_only":
        errors.append("mode must be diagnostic_only")
    if payload.get("local_geophysics_is_cosmological_evidence") is not False:
        errors.append("local geophysics must not be cosmological evidence")
    if payload.get("likelihood_mutation_allowed") is not False:
        errors.append("likelihood_mutation_allowed must be false")
    if payload.get("cosmological_parameter_mutation_allowed") is not False:
        errors.append("cosmological_parameter_mutation_allowed must be false")

    receipt_use = payload.get("receipt_use_class")
    if receipt_use not in ALLOWED_RECEIPT_USE:
        errors.append(f"receipt_use_class must be one of {sorted(ALLOWED_RECEIPT_USE)}")

    provenance = _object(payload, "provenance", errors)
    if provenance.get("producer_repo") != CANONICAL_PRODUCER:
        errors.append("provenance.producer_repo must be the canonical Fisica repository")
    if not _valid_sha40(provenance.get("producer_commit")):
        errors.append("provenance.producer_commit must be a lowercase SHA-1")
    if not _valid_sha64(provenance.get("receipt_sha256")):
        errors.append("provenance.receipt_sha256 must be a lowercase SHA-256")

    target = _object(payload, "target", errors)
    dataset_id = target.get("dataset_id")
    if not isinstance(dataset_id, str) or not dataset_id:
        errors.append("target.dataset_id must be a non-empty string")
    observation_index = target.get("observation_index_sha256")
    if observation_index != TOKEN_VAZIO and not _valid_sha64(observation_index):
        errors.append("target.observation_index_sha256 must be TOKEN_VAZIO or SHA-256")

    join = _object(payload, "join", errors)
    method = join.get("method")
    if method != TOKEN_VAZIO and method not in ALLOWED_JOIN_METHODS:
        errors.append(f"join.method must be TOKEN_VAZIO or one of {sorted(ALLOWED_JOIN_METHODS)}")

    offset = join.get("max_time_offset_s")
    if offset != TOKEN_VAZIO:
        if (
            not isinstance(offset, (int, float))
            or isinstance(offset, bool)
            or not math.isfinite(float(offset))
            or float(offset) < 0
        ):
            errors.append("join.max_time_offset_s must be TOKEN_VAZIO or finite non-negative")

    matched = join.get("matched_observations")
    total = join.get("total_observations")
    if matched != TOKEN_VAZIO and (
        not isinstance(matched, int) or isinstance(matched, bool) or matched < 0
    ):
        errors.append("join.matched_observations must be TOKEN_VAZIO or integer >= 0")
    if total != TOKEN_VAZIO and (
        not isinstance(total, int) or isinstance(total, bool) or total <= 0
    ):
        errors.append("join.total_observations must be TOKEN_VAZIO or integer > 0")
    if isinstance(matched, int) and not isinstance(matched, bool) and isinstance(total, int) and not isinstance(total, bool):
        if total > 0 and matched > total:
            errors.append("join.matched_observations cannot exceed total_observations")

    analysis = _object(payload, "analysis", errors)
    if analysis.get("residual_mutation_allowed") is not False:
        errors.append("analysis.residual_mutation_allowed must be false")

    return errors


def missing_readiness_fields(payload: Mapping[str, Any]) -> list[str]:
    """Return TOKEN_VAZIO/absent fields that block an observational join."""
    missing: list[str] = []
    for path in READINESS_PATHS:
        if not _is_present(_read_path(payload, path)):
            missing.append(".".join(path))
    return missing


def classify_systematics_use(payload: Mapping[str, Any]) -> str:
    """Return the maximum use class allowed by the current evidence contract."""
    if validate_systematics_link(payload):
        return "BLOCKED"

    receipt_use = payload["receipt_use_class"]
    if receipt_use == "TEST_FIXTURE_ONLY":
        return "TEST_FIXTURE_ONLY"
    if receipt_use != "LOCAL_CONTEXT_DATA_READY":
        return "CONTEXT_ONLY"

    if missing_readiness_fields(payload):
        return TOKEN_VAZIO

    join = payload["join"]
    if join["matched_observations"] == 0:
        return "NO_OVERLAP"

    return "SYSTEMATICS_DIAGNOSTIC_READY"


def build_systematics_receipt(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Build a deterministic RLL-side receipt for the proposed diagnostic join."""
    errors = validate_systematics_link(payload)
    classification = "BLOCKED" if errors else classify_systematics_use(payload)
    core: dict[str, Any] = {
        "schema": "rll_geophysical_systematics_receipt_v1",
        "classification": classification,
        "claim_allowed": False,
        "likelihood_mutation_allowed": False,
        "cosmological_parameter_mutation_allowed": False,
        "source_contract_sha256": sha256(_canonical_json_bytes(payload)).hexdigest(),
        "missing_readiness_fields": missing_readiness_fields(payload),
        "validation_errors": errors,
        "boundaries": [
            "Local geophysical association is a systematics diagnostic, not cosmological evidence.",
            "A diagnostic-ready join does not authorize residual, likelihood, or parameter mutation.",
            "Synthetic fixtures are never observational evidence.",
            "A causal mechanism requires a separate preregistered analysis and falsifiers.",
        ],
    }
    core["receipt_sha256"] = sha256(_canonical_json_bytes(core)).hexdigest()
    return core
