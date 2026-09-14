"""Fail-closed RLL consumer for the cross-repository mathematics registry.

The adapter never converts an unknown vector into a zero vector and never
promotes deterministic mathematics or synthetic baselines to physical evidence.
"""
from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from typing import Any, Mapping

CANONICAL_PRODUCER = "rafaelmeloreisnovo/Matem-tica-"
CANONICAL_SCHEMA = "rafaelia.mathematics-papers-theorems-registry.v1"
TOKEN_VAZIO_VECTOR = "TOKEN_VAZIO_UNCOUPLED_VECTOR"
SHA40 = re.compile(r"^[0-9a-f]{40}$")


def canonical_json_sha256(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def validate_envelope(
    envelope: Mapping[str, Any],
    *,
    expected_commit: str | None = None,
    expected_blob_sha: str | None = None,
) -> list[str]:
    errors: list[str] = []
    if envelope.get("producer_repo") != CANONICAL_PRODUCER:
        errors.append("producer_repo must be the canonical Matem-tica- repository")

    commit = envelope.get("producer_commit")
    if not isinstance(commit, str) or not SHA40.fullmatch(commit):
        errors.append("producer_commit must be a 40-character lowercase SHA")
    elif expected_commit is not None and commit != expected_commit:
        errors.append("producer_commit does not match the pinned contract")

    blob_sha = envelope.get("registry_blob_sha")
    if not isinstance(blob_sha, str) or not SHA40.fullmatch(blob_sha):
        errors.append("registry_blob_sha must be a 40-character lowercase SHA")
    elif expected_blob_sha is not None and blob_sha != expected_blob_sha:
        errors.append("registry_blob_sha does not match the pinned registry blob")

    payload = envelope.get("payload")
    if not isinstance(payload, Mapping):
        errors.append("payload must be a registry object")
        return errors
    errors.extend(validate_registry(payload))
    return errors


def validate_registry(registry: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if registry.get("schema") != CANONICAL_SCHEMA:
        errors.append("unsupported mathematics registry schema")
    if registry.get("claim_allowed") is not False:
        errors.append("claim_allowed must remain false")

    vector_rule = registry.get("vector_rule")
    if not isinstance(vector_rule, Mapping):
        errors.append("vector_rule must be an object")
    else:
        if vector_rule.get("uncoupled_vector_value") is not None:
            errors.append("uncoupled_vector_value must be null")
        if vector_rule.get("uncoupled_vector_state") != TOKEN_VAZIO_VECTOR:
            errors.append("uncoupled_vector_state must preserve typed TOKEN_VAZIO")
        if vector_rule.get("zero_is_not_unknown") is not True:
            errors.append("zero_is_not_unknown must be true")

    artifacts = registry.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        errors.append("artifacts must be a non-empty array")
        return errors

    seen: set[str] = set()
    for index, artifact in enumerate(artifacts):
        prefix = f"artifacts[{index}]"
        if not isinstance(artifact, Mapping):
            errors.append(f"{prefix} must be an object")
            continue
        artifact_id = artifact.get("id")
        if not isinstance(artifact_id, str) or not artifact_id:
            errors.append(f"{prefix}.id must be a non-empty string")
        elif artifact_id in seen:
            errors.append(f"{prefix}.id is duplicated: {artifact_id}")
        else:
            seen.add(artifact_id)
        errors.extend(_validate_artifact(artifact, prefix))
    return errors


def _validate_artifact(artifact: Mapping[str, Any], prefix: str) -> list[str]:
    errors: list[str] = []
    data = artifact.get("data")
    vector = artifact.get("vector")
    physical_adapter = artifact.get("physical_adapter")

    if not isinstance(data, Mapping):
        errors.append(f"{prefix}.data must be an object")
        data = {}
    if not isinstance(vector, Mapping):
        errors.append(f"{prefix}.vector must be an object")
        vector = {}
    if not isinstance(physical_adapter, Mapping):
        errors.append(f"{prefix}.physical_adapter must be an object")
        physical_adapter = {}

    state = vector.get("state")
    value = vector.get("value")
    if state == TOKEN_VAZIO_VECTOR:
        if value is not None:
            errors.append(f"{prefix}: TOKEN_VAZIO vector value must be null")
    elif isinstance(state, str) and state.startswith("COUPLED_"):
        if not isinstance(value, list) or not value:
            errors.append(f"{prefix}: coupled vector must contain numeric values")
        elif any(not isinstance(item, (int, float)) or isinstance(item, bool) for item in value):
            errors.append(f"{prefix}: coupled vector values must be numeric")
        labels = vector.get("labels")
        if not isinstance(labels, list) or len(labels) != len(value or []):
            errors.append(f"{prefix}: coupled vector labels must match vector length")
        if not vector.get("source"):
            errors.append(f"{prefix}: coupled vector requires a source")
    else:
        errors.append(f"{prefix}: vector state must be TOKEN_VAZIO or COUPLED_*")

    data_kind = data.get("kind")
    is_real = data.get("real_world_observation")
    evidence = artifact.get("evidence_class", [])
    if is_real is True:
        if data_kind != "REAL_OBSERVATIONAL_DATA_PIPELINE":
            errors.append(f"{prefix}: real observation requires REAL_OBSERVATIONAL_DATA_PIPELINE")
        if "REAL_OBSERVATIONAL_DATA" not in evidence:
            errors.append(f"{prefix}: real observation requires REAL_OBSERVATIONAL_DATA evidence")
        if not (isinstance(state, str) and state.startswith("COUPLED_")):
            errors.append(f"{prefix}: real observation requires a coupled vector")
        if not physical_adapter.get("falsifier"):
            errors.append(f"{prefix}: real observation requires a falsifier")
    elif is_real is False:
        if data_kind == "REAL_OBSERVATIONAL_DATA_PIPELINE":
            errors.append(f"{prefix}: observational pipeline cannot be marked non-real")
    else:
        errors.append(f"{prefix}.data.real_world_observation must be boolean")

    adapter_state = physical_adapter.get("state")
    if isinstance(adapter_state, str) and adapter_state.startswith("TOKEN_VAZIO"):
        claim_state = str(artifact.get("claim_state", ""))
        if "CONFIRMED" in claim_state or "VALIDATED_PHYSICALLY" in claim_state:
            errors.append(f"{prefix}: physical claim promoted while adapter is TOKEN_VAZIO")

    if artifact.get("implementation_state") == "IMPLEMENTED":
        authority = artifact.get("authority")
        if not isinstance(authority, Mapping) or not (
            authority.get("implementation") or authority.get("document") or authority.get("result")
        ):
            errors.append(f"{prefix}: IMPLEMENTED artifact requires authority path")
    return errors


def classify_artifact(artifact: Mapping[str, Any]) -> str:
    if _validate_artifact(artifact, "artifact"):
        return "BLOCKED"
    data = artifact["data"]
    vector = artifact["vector"]
    adapter = artifact["physical_adapter"]
    if data.get("real_world_observation") is True and str(vector.get("state", "")).startswith("COUPLED_"):
        return "OBSERVATIONAL_INFERENCE_READY"
    adapter_state = str(adapter.get("state", ""))
    if adapter_state.startswith("TOKEN_VAZIO"):
        return "CONTEXT_ONLY_TOKEN_VAZIO"
    if artifact.get("claim_state") == "MATHEMATICAL_ONLY" or adapter_state == "NOT_APPLICABLE":
        return "MATHEMATICAL_ONLY"
    if data.get("kind") in {
        "MODEL_BASELINE",
        "DETERMINISTIC_MODEL",
        "DETERMINISTIC_COMBINATORICS",
        "DETERMINISTIC_ENUMERATION",
        "DETERMINISTIC_GENERATED_DOMAIN",
    }:
        return "MODEL_OR_DETERMINISTIC_ONLY"
    return "CONTEXT_ONLY"


def summarize_registry(registry: Mapping[str, Any]) -> dict[str, Any]:
    errors = validate_registry(registry)
    if errors:
        return {"status": "BLOCKED", "errors": errors, "claim_allowed": False}
    classes = Counter(classify_artifact(item) for item in registry["artifacts"])
    vectors = Counter(item["vector"]["state"] for item in registry["artifacts"])
    return {
        "status": "PASS_EMULATED_CONTRACT",
        "artifact_count": len(registry["artifacts"]),
        "classification_counts": dict(sorted(classes.items())),
        "vector_state_counts": dict(sorted(vectors.items())),
        "registry_sha256": canonical_json_sha256(registry),
        "claim_allowed": False,
        "physical_promotion_performed": False,
    }
