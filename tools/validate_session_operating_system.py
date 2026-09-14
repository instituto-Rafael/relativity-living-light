#!/usr/bin/env python3
"""Validate the RLL session knowledge operating-system contract.

This is a structural and governance audit. It does not fetch private repositories,
execute scientific models, validate physical claims, or copy private session content.
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "knowledge_ecosystem" / "session_operating_system.yml"
SCHEMA = ROOT / "schemas" / "session_operating_system.schema.json"

REQUIRED_STATES = {
    "VERIFIED",
    "VERIFIED_LIMITED",
    "DECLARED_BY_AUTHOR",
    "HYPOTHESIS",
    "PARTIAL",
    "TOKEN_VAZIO",
    "CLAIM_BLOCKED",
    "CONTRADICTION",
    "ROLLBACK",
}
TRACEABILITY_REQUIRED = [
    "session_group",
    "source",
    "concept",
    "formula_or_model",
    "operation",
    "materialization",
    "artifact",
    "test_or_log",
    "evidence_state",
    "claim_boundary",
    "destination",
    "next_action",
]
FORBIDDEN_KEYS = {
    "secret",
    "secrets",
    "password",
    "credential",
    "credentials",
    "private_key",
    "access_token",
    "api_key",
}
NONFATAL_GAP_STATES = {"TOKEN_VAZIO", "CLAIM_BLOCKED", "CONTRADICTION", "PARTIAL", "HYPOTHESIS"}


def load_contract(manifest: Path = MANIFEST, schema_path: Path = SCHEMA) -> tuple[dict[str, Any], dict[str, Any]]:
    data = yaml.safe_load(manifest.read_text(encoding="utf-8"))
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("session operating-system manifest must be a mapping")
    return data, schema


def validate_schema(data: dict[str, Any], schema: dict[str, Any]) -> None:
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda error: list(error.path))
    if errors:
        details = "; ".join(
            f"{'/'.join(map(str, error.path)) or '<root>'}: {error.message}" for error in errors
        )
        raise ValueError(f"schema validation failed: {details}")


def _walk_keys(value: Any, path: str = "<root>") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = str(key).strip().lower()
            if normalized in FORBIDDEN_KEYS:
                raise ValueError(f"forbidden sensitive key at {path}/{key}")
            _walk_keys(child, f"{path}/{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _walk_keys(child, f"{path}/{index}")


def validate_execution_policy(data: dict[str, Any], root: Path = ROOT) -> None:
    policy = data["execution_policy"]
    for key in ("automatic_cross_repo_write", "automatic_merge", "destructive_actions", "commit_results_default"):
        if policy[key] is not False:
            raise ValueError(f"execution policy must keep {key}=false")
    if policy["fail_closed_on_private_content"] is not True:
        raise ValueError("private-content policy must fail closed")
    if policy["continue_audit_after_nonfatal_gaps"] is not True:
        raise ValueError("audit must continue after nonfatal TOKEN_VAZIO/CLAIM_BLOCKED gaps")
    workflow = root / policy["workflow_path"]
    if not workflow.exists():
        raise ValueError(f"bound workflow path does not exist: {policy['workflow_path']}")


def validate_states(data: dict[str, Any]) -> None:
    vocabulary = set(data["state_vocabulary"])
    missing = REQUIRED_STATES - vocabulary
    if missing:
        raise ValueError(f"missing required state(s): {sorted(missing)}")
    for group in data["session_groups"]:
        if group["evidence_state"] not in vocabulary:
            raise ValueError(f"{group['id']}: unknown evidence_state {group['evidence_state']}")
        for source in group["source_links"]:
            if source["source_state"] not in vocabulary:
                raise ValueError(f"{group['id']}: unknown source state {source['source_state']}")
        for route in group["target_routes"]:
            if route["state"] not in vocabulary:
                raise ValueError(f"{group['id']}: unknown target state {route['state']}")


def validate_traceability(data: dict[str, Any]) -> None:
    if data["traceability_chain"] != TRACEABILITY_REQUIRED:
        raise ValueError("traceability_chain must preserve the canonical ordered chain")
    seen_group_ids: set[str] = set()
    for group in data["session_groups"]:
        group_id = group["id"]
        if group_id in seen_group_ids:
            raise ValueError(f"duplicate session group id: {group_id}")
        seen_group_ids.add(group_id)
        if not group["source_links"] or not group["concepts"] or not group["operations"] or not group["target_routes"]:
            raise ValueError(f"{group_id}: traceability components cannot be empty")
        if not group["claim_boundary"].strip():
            raise ValueError(f"{group_id}: claim boundary is required")
        if not group["next_action"].startswith(("Verify", "Define", "Check", "Preserve", "Classify")):
            raise ValueError(f"{group_id}: next_action must name an explicit audit action")


def validate_private_boundaries(data: dict[str, Any]) -> None:
    for group in data["session_groups"]:
        group_id = group["id"]
        for source in group["source_links"]:
            visibility = source["visibility"]
            if visibility == "private" and source["content_mode"] != "pointer_only":
                raise ValueError(f"{group_id}: private source must be pointer_only")
            if source["path"] == "TOKEN_VAZIO" and source["source_state"] not in {
                "TOKEN_VAZIO", "DECLARED_BY_AUTHOR", "HYPOTHESIS", "PARTIAL"
            }:
                raise ValueError(f"{group_id}: TOKEN_VAZIO path has an over-promoted source state")
        for route in group["target_routes"]:
            if "Private" in route["repo"] or route["destination"].startswith("private_"):
                mode = route["mode"].lower()
                if "private" not in mode and "pointer" not in mode:
                    raise ValueError(f"{group_id}: private target route must be private/pointer mode")
    _walk_keys(data)


def validate_commit_plan(data: dict[str, Any]) -> None:
    plan = data["commit_plan"]
    orders = [step["order"] for step in plan]
    if orders != list(range(1, len(plan) + 1)):
        raise ValueError("commit plan orders must be sequential from 1")
    names: set[str] = set()
    files_seen: set[str] = set()
    for step in plan:
        if step["name"] in names:
            raise ValueError(f"duplicate commit step name: {step['name']}")
        names.add(step["name"])
        if not step["rollback"].strip():
            raise ValueError(f"commit step {step['name']} has no rollback")
        for path in step["files"]:
            if path in files_seen:
                raise ValueError(f"file assigned to more than one microcommit: {path}")
            files_seen.add(path)


def build_report(data: dict[str, Any]) -> dict[str, Any]:
    source_states: list[str] = []
    route_states: list[str] = []
    for group in data["session_groups"]:
        source_states.extend(source["source_state"] for source in group["source_links"])
        route_states.extend(route["state"] for route in group["target_routes"])
    all_states = [group["evidence_state"] for group in data["session_groups"]] + source_states + route_states
    entropy_count = sum(state in NONFATAL_GAP_STATES for state in all_states)
    verified_links = sum(state in {"VERIFIED", "VERIFIED_LIMITED"} for state in source_states)
    report = {
        "schema": "rll.session_knowledge_operating_system.report.v1",
        "operation_id": data["operation_id"],
        "claim_allowed": False,
        "session_groups": len(data["session_groups"]),
        "source_links": len(source_states),
        "target_routes": len(route_states),
        "organizational_entropy_count": entropy_count,
        "organizational_syntropy_count": {
            "verified_source_links": verified_links,
            "tested_contracts": 1,
            "explicit_rollbacks": len(data["commit_plan"]),
            "source_citations": sum(len(group["references"]) for group in data["session_groups"]),
        },
        "private_sources_pointer_only": all(
            source["content_mode"] == "pointer_only"
            for group in data["session_groups"]
            for source in group["source_links"]
            if source["visibility"] == "private"
        ),
        "automatic_cross_repo_write": False,
        "destructive_actions": False,
        "claim_boundary": data["claim_boundary"],
    }
    return report


def validate_contract(data: dict[str, Any], schema: dict[str, Any], root: Path = ROOT) -> dict[str, Any]:
    if data.get("claim_allowed") is not False:
        raise ValueError("claim_allowed must remain false")
    validate_schema(data, schema)
    validate_execution_policy(data, root=root)
    validate_states(data)
    validate_traceability(data)
    validate_private_boundaries(data)
    validate_commit_plan(data)
    return build_report(data)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--schema", type=Path, default=SCHEMA)
    parser.add_argument("--report", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    data, schema = load_contract(args.manifest, args.schema)
    report = validate_contract(data, schema)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print("OK: session knowledge operating-system contract is traceable, non-destructive and privacy-gated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
