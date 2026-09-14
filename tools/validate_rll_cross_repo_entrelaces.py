#!/usr/bin/env python3
"""Validate the machine-readable RLL cross-repository entrelace registry.

This validator proves structural traceability and claim boundaries only.
It does not fetch external repositories, execute foreign code, or validate physics.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "knowledge_ecosystem" / "rll_cross_repo_entrelaces_v2.json"
SCHEMA = ROOT / "schemas" / "rll_cross_repo_entrelace.schema.json"
OVERLAY = ROOT / "results" / "session_grafo_fase17_20" / "current_state_overlay.json"
GAPS = ROOT / "results" / "session_grafo_fase17_20" / "gaps.jsonl"

ALLOWED_RELATION_STATES = {
    "VERIFIED_LIMITED", "PARTIAL", "BLOCKED", "TOKEN_VAZIO", "CONTRADICTION"
}
FORBIDDEN_KEYS = {
    "secret", "secrets", "password", "credential", "credentials",
    "private_key", "access_token", "api_key"
}
ACTION_PREFIXES = (
    "Emit", "Generate", "Define", "Produce", "Locate", "Import", "Recompute"
)


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: root must be an object")
    return data


def _walk_keys(value: Any, path: str = "<root>") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if str(key).strip().lower() in FORBIDDEN_KEYS:
                raise ValueError(f"forbidden sensitive key at {path}/{key}")
            _walk_keys(child, f"{path}/{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _walk_keys(child, f"{path}/{index}")


def validate_schema(data: dict[str, Any], schema: dict[str, Any]) -> None:
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(data), key=lambda err: list(err.path))
    if errors:
        details = "; ".join(
            f"{'/'.join(map(str, err.path)) or '<root>'}: {err.message}"
            for err in errors
        )
        raise ValueError(f"schema validation failed: {details}")


def load_gap_records(path: Path = GAPS) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        item = json.loads(raw)
        gap_id = item.get("gap_id")
        if not gap_id:
            raise ValueError(f"{path}:{line_number}: missing gap_id")
        if gap_id in records:
            raise ValueError(f"{path}:{line_number}: duplicate gap_id {gap_id}")
        records[gap_id] = item
    return records


def validate_relationships(data: dict[str, Any], root: Path = ROOT) -> None:
    if data.get("claim_allowed") is not False:
        raise ValueError("claim_allowed must remain false")

    policies = data["policies"]
    if not all(value is True for value in policies.values()):
        raise ValueError("all fail-closed governance policies must remain true")

    ids: set[str] = set()
    for relation in data["relationships"]:
        relation_id = relation["id"]
        if relation_id in ids:
            raise ValueError(f"duplicate relationship id: {relation_id}")
        ids.add(relation_id)

        state = relation["state"]
        if state not in ALLOWED_RELATION_STATES:
            raise ValueError(f"{relation_id}: unsupported state {state}")
        if not relation["proven"] or not relation["not_proven"]:
            raise ValueError(f"{relation_id}: proven and not_proven must both be explicit")
        if not relation["next_action"].startswith(ACTION_PREFIXES):
            raise ValueError(f"{relation_id}: next_action must start with an explicit audit verb")
        if not relation["rollback"].strip():
            raise ValueError(f"{relation_id}: rollback is required")

        for endpoint_name in ("source", "target"):
            endpoint = relation[endpoint_name]
            if endpoint["path"] == "TOKEN_VAZIO":
                raise ValueError(f"{relation_id}: {endpoint_name} path cannot be TOKEN_VAZIO")
            if endpoint["repo"] == data["owner_repository"]:
                local_path = root / endpoint["path"]
                if not local_path.exists():
                    raise ValueError(
                        f"{relation_id}: local {endpoint_name} path does not exist: {endpoint['path']}"
                    )

        artifact = relation["required_artifact"]
        if relation["relation_type"] == "RUNTIME_EVIDENCE_CONTRACT":
            if artifact["status"] == "VERIFIED" and state != "VERIFIED_LIMITED":
                raise ValueError(
                    f"{relation_id}: verified runtime artifact requires a bounded verified relation"
                )
        if relation["relation_type"] == "DOCUMENTATION_BRIDGE":
            if artifact["status"] not in {"BLOCKED", "TOKEN_VAZIO"}:
                raise ValueError(
                    f"{relation_id}: documentation bridge cannot claim runtime artifact completion"
                )

    urgent_ids = {item["id"] for item in data["urgent_gaps"]}
    required_urgent = {
        "URG-G4-SNAPSHOT-SYNC",
        "URG-CROSS-REPO-RUNTIME-EVIDENCE",
        "URG-MOBILE-HISTORICAL-PROVENANCE",
    }
    missing = required_urgent - urgent_ids
    if missing:
        raise ValueError(f"missing urgent gap(s): {sorted(missing)}")

    _walk_keys(data)


def validate_g4_overlay(
    overlay_path: Path = OVERLAY,
    gaps_path: Path = GAPS,
    root: Path = ROOT,
) -> None:
    overlay = load_json(overlay_path)
    gaps = load_gap_records(gaps_path)
    g4 = gaps.get("G4")
    if not g4:
        raise ValueError("G4 missing from historical gap ledger")
    if g4.get("status_at_snapshot_phase20") != "TOKEN_VAZIO":
        raise ValueError("G4 historical FASE20 status must remain TOKEN_VAZIO")
    if g4.get("current_status") != "VERIFIED_LIMITED":
        raise ValueError("G4 current_status must record quantified limited evidence")
    if g4.get("resolved_in_phase") != 22:
        raise ValueError("G4 current resolution must point to FASE22")
    precision_gate = str(g4.get("precision_next_gate", ""))
    if "CAMB/RECFAST" not in precision_gate:
        raise ValueError("G4 residual CAMB/RECFAST precision gate must remain explicit")

    if overlay.get("schema") != "rll.session_graph.current_state_overlay.v1":
        raise ValueError("unexpected current-state overlay schema")
    if overlay["snapshot"]["through_phase"] != 20:
        raise ValueError("overlay snapshot must stop at FASE20")
    if overlay["current_state"]["through_phase"] < 22:
        raise ValueError("overlay current state must include FASE22")
    if overlay["current_state"]["gap_states"].get("G4") != "VERIFIED_LIMITED":
        raise ValueError("overlay must map G4 to VERIFIED_LIMITED")
    if overlay["current_state"].get("claim_allowed") is not False:
        raise ValueError("overlay must keep claim_allowed=false")
    if overlay["transitions"][0]["residual_limitation"]["status"] != "TOKEN_VAZIO":
        raise ValueError("overlay must retain residual precision limitation")

    required_evidence = [
        root / "scripts" / "rll_fase22_g4_eh_bias_grid.py",
        root / "results" / "rll_fase22_g4_eh_bias_grid.json",
        root / "docs" / "cronologia-auditoria" / "21_FASE22_G4_EH_BIAS_GRID.md",
    ]
    missing = [str(path.relative_to(root)) for path in required_evidence if not path.exists()]
    if missing:
        raise ValueError(f"G4 overlay evidence path(s) missing: {missing}")


def build_report(data: dict[str, Any]) -> dict[str, Any]:
    states: dict[str, int] = {}
    artifact_states: dict[str, int] = {}
    for relation in data["relationships"]:
        states[relation["state"]] = states.get(relation["state"], 0) + 1
        artifact_state = relation["required_artifact"]["status"]
        artifact_states[artifact_state] = artifact_states.get(artifact_state, 0) + 1
    return {
        "schema": "rll.cross_repo_entrelace_registry.report.v2",
        "claim_allowed": False,
        "relationships": len(data["relationships"]),
        "relationship_states": states,
        "required_artifact_states": artifact_states,
        "urgent_gaps": len(data["urgent_gaps"]),
        "g4_snapshot_preserved": True,
        "g4_current_state_synchronized": True,
        "automatic_cross_repo_write": False,
        "automatic_merge": False,
    }


def validate_registry(
    registry_path: Path = REGISTRY,
    schema_path: Path = SCHEMA,
    root: Path = ROOT,
) -> dict[str, Any]:
    data = load_json(registry_path)
    schema = load_json(schema_path)
    validate_schema(data, schema)
    validate_relationships(data, root=root)
    validate_g4_overlay(root=root)
    return build_report(data)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, default=REGISTRY)
    parser.add_argument("--schema", type=Path, default=SCHEMA)
    parser.add_argument("--report", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = validate_registry(args.registry, args.schema)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print("OK: RLL cross-repository entrelaces are traceable, bounded and fail-closed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
