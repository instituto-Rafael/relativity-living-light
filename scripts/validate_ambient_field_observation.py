#!/usr/bin/env python3
"""Validate the synthetic AmbientFieldObservation governance contract.

This lightweight validator uses only the Python standard library. It checks the
claim boundary and high-risk cross-field invariants that generic JSON parsing
would not protect, including absent environmental sensors, battery-vs-ambient
temperature separation, privacy gates, and the unvalidated hurricane lead-time
claim.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "ambient_field_observation.schema.json"
FIXTURE_PATH = ROOT / "fixtures" / "ambient_field_observation.example.json"

OBSERVATION_ID = re.compile(r"^AFO-[A-Z0-9_-]{4,48}$")
NODE_ID = re.compile(r"^NODE-[A-Z0-9_-]{4,48}$")


def stop(message: str) -> None:
    raise SystemExit(f"ambient field validation failed: {message}")


def load_object(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        stop(f"cannot parse {path}: {exc}")
    if not isinstance(data, dict):
        stop(f"expected JSON object: {path}")
    return data


def require_keys(obj: dict[str, Any], keys: set[str], label: str) -> None:
    missing = sorted(keys - obj.keys())
    if missing:
        stop(f"{label} missing keys: {', '.join(missing)}")


def validate_schema(schema: dict[str, Any]) -> None:
    require_keys(
        schema,
        {"$schema", "$id", "title", "description", "type", "required", "properties"},
        "schema",
    )
    description = str(schema["description"]).lower()
    if "structural" not in description or "contract" not in description:
        stop("schema description must declare structural contract status")
    if "does not authorize" not in description:
        stop("schema description must preserve the negative authorization gate")
    if schema["type"] != "object":
        stop("schema root type must be object")


def validate_fixture(fixture: dict[str, Any]) -> None:
    require_keys(
        fixture,
        {
            "observation_id",
            "node_id",
            "timestamp",
            "location",
            "device_state",
            "capabilities",
            "channels",
            "epistemic_status",
            "quality",
            "use_policy",
        },
        "fixture",
    )

    if not OBSERVATION_ID.fullmatch(str(fixture["observation_id"])):
        stop("invalid observation_id")
    if not NODE_ID.fullmatch(str(fixture["node_id"])):
        stop("invalid node_id")

    capabilities = fixture["capabilities"]
    if not isinstance(capabilities, dict):
        stop("capabilities must be an object")
    capability_keys = {
        "magnetometer",
        "barometer",
        "ambient_temperature",
        "relative_humidity",
        "gnss_raw",
        "wifi_metrics",
        "bluetooth_metrics",
        "cell_metrics",
        "acoustic_probe",
        "imu",
    }
    require_keys(capabilities, capability_keys, "capabilities")
    if any(not isinstance(capabilities[key], bool) for key in capability_keys):
        stop("all capability values must be boolean")

    channels = fixture["channels"]
    if not isinstance(channels, list) or not channels:
        stop("channels must be a non-empty array")

    required_channel_keys = {
        "channel_id",
        "modality",
        "metric",
        "value_state",
        "raw_value",
        "unit",
        "reference",
        "residual",
        "uncertainty",
        "quality_flags",
    }
    channel_by_modality: dict[str, list[dict[str, Any]]] = {}
    for index, channel in enumerate(channels):
        if not isinstance(channel, dict):
            stop(f"channel {index} must be an object")
        require_keys(channel, required_channel_keys, f"channel {index}")
        modality = str(channel["modality"])
        channel_by_modality.setdefault(modality, []).append(channel)
        uncertainty = channel["uncertainty"]
        if not isinstance(uncertainty, (int, float)) or not 0 <= uncertainty <= 1:
            stop(f"channel {index} uncertainty outside [0,1]")
        if channel["value_state"] == "absent" and channel["raw_value"] is not None:
            stop(f"channel {index}: absent values must use JSON null")

    ambient_channels = channel_by_modality.get("ambient_temperature", [])
    if capabilities["ambient_temperature"] is False:
        if not ambient_channels:
            stop("missing explicit ambient-temperature TOKEN_VAZIO channel")
        if any(channel["value_state"] != "absent" for channel in ambient_channels):
            stop("ambient temperature cannot be measured when capability is false")

    battery_channels = channel_by_modality.get("battery_temperature", [])
    if not battery_channels:
        stop("battery temperature context channel is required in this fixture")
    for channel in battery_channels:
        text = str(channel["residual"].get("interpretation", "")).lower()
        if "device thermal context" not in text:
            stop("battery temperature must be labeled as device context")

    use_policy = fixture["use_policy"]
    if use_policy.get("identity_inference") != "blocked":
        stop("identity inference must be blocked")
    if use_policy.get("payload_collection") not in {"none", "blocked"}:
        stop("payload collection must be absent or blocked")
    if use_policy.get("operational_gate") != "research_only":
        stop("synthetic fixture must remain research_only")

    hypotheses = fixture.get("hypotheses", [])
    hurricane = [h for h in hypotheses if h.get("name") == "hurricane_lead_time_gain"]
    if len(hurricane) != 1:
        stop("fixture must contain exactly one hurricane lead-time hypothesis")
    hurricane_claim = hurricane[0]
    if hurricane_claim.get("status") != "token_vazio":
        stop("hurricane lead-time claim must remain token_vazio")
    if hurricane_claim.get("probability") != 0.0:
        stop("unvalidated hurricane lead-time probability must be 0.0")

    quality = fixture["quality"]
    for name in [
        "sensor_quality",
        "calibration_quality",
        "context_quality",
        "time_quality",
        "overall",
    ]:
        value = quality.get(name)
        if not isinstance(value, (int, float)) or not 0 <= value <= 1:
            stop(f"quality.{name} outside [0,1]")


def main() -> int:
    schema = load_object(SCHEMA_PATH)
    fixture = load_object(FIXTURE_PATH)
    validate_schema(schema)
    validate_fixture(fixture)
    print("OK: AmbientFieldObservation schema and synthetic fixture are claim-bounded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
