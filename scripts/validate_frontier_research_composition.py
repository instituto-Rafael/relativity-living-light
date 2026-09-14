#!/usr/bin/env python3
"""Fail-closed validator for the frontier research composition pipeline."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

EXPECTED_SCHEMA = "rll.frontier_research_composition.v1"
QUEUE_SCHEMA = "rll.frontier_research_queue.v1"
TOKEN_PREFIX = "TOKEN_VAZIO"


def _load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: root must be a mapping")
    return payload


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def validate_contract(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    _require(payload.get("schema") == EXPECTED_SCHEMA, "unexpected contract schema", errors)
    _require(payload.get("claim_allowed") is False, "claim_allowed must remain false", errors)
    _require(payload.get("canonical_outputs_modified") is False, "canonical outputs must remain untouched", errors)

    ordering = payload.get("ordering", {})
    _require(ordering.get("mode") == "evidence_dependency_not_size", "ordering must be evidence-dependent", errors)
    forbidden = set(ordering.get("forbidden", []))
    _require({"smallest_to_largest", "largest_to_smallest"}.issubset(forbidden), "size orderings must be forbidden", errors)

    state_policy = payload.get("state_policy", {})
    _require(state_policy.get("token_vazio_prefix") == TOKEN_PREFIX, "TOKEN_VAZIO prefix must be canonical", errors)
    for key in ("no_implicit_promotion", "no_average_compensation", "absence_is_not_zero"):
        _require(state_policy.get(key) is True, f"state policy {key} must be true", errors)

    stages = payload.get("stages", [])
    _require(isinstance(stages, list) and len(stages) >= 10, "at least ten stages are required", errors)
    ids = [stage.get("id") for stage in stages if isinstance(stage, dict)]
    _require(len(ids) == len(set(ids)), "stage ids must be unique", errors)
    orders = [stage.get("order") for stage in stages if isinstance(stage, dict)]
    _require(orders == list(range(len(stages))), "stage order must be contiguous from zero", errors)
    for stage in stages:
        if not isinstance(stage, dict):
            errors.append("each stage must be a mapping")
            continue
        sid = stage.get("id", "UNKNOWN")
        _require(bool(stage.get("produces")), f"{sid}: produces is required", errors)
        fields = stage.get("mandatory_fields")
        _require(isinstance(fields, list) and bool(fields), f"{sid}: mandatory_fields required", errors)
        _require(str(stage.get("on_missing", "")).startswith(TOKEN_PREFIX), f"{sid}: on_missing must be TOKEN_VAZIO", errors)
        _require(bool(stage.get("gate")), f"{sid}: gate required", errors)

    passes = payload.get("prompt_evolution", {}).get("passes", [])
    _require(len(passes) >= 8, "prompt evolution requires at least eight passes", errors)
    pass_ids = [item.get("id") for item in passes if isinstance(item, dict)]
    _require(len(pass_ids) == len(set(pass_ids)), "prompt pass ids must be unique", errors)
    for item in passes:
        _require(str(item.get("on_failure", "")).startswith(TOKEN_PREFIX), f"{item.get('id')}: failure must become TOKEN_VAZIO", errors)
        _require(bool(item.get("checks")), f"{item.get('id')}: checks required", errors)

    required_gates = set(payload.get("composition_policy", {}).get("required_gates", []))
    _require("no_double_counting" in required_gates, "composition requires no_double_counting gate", errors)
    _require("identifiable_parameters" in required_gates, "composition requires identifiability gate", errors)
    _require("nested_component_off_switch" in required_gates, "composition requires nested off-switch", errors)

    tracks = payload.get("frontier_tracks", [])
    _require(bool(tracks), "frontier tracks required", errors)
    track_ids = [track.get("id") for track in tracks if isinstance(track, dict)]
    _require(len(track_ids) == len(set(track_ids)), "frontier track ids must be unique", errors)
    for track in tracks:
        state = str(track.get("state", ""))
        if not state.startswith(TOKEN_PREFIX) and state not in {"IMPLEMENTED", "ROUTED_SEPARATE_AUTHORITY"}:
            errors.append(f"{track.get('id')}: unsupported frontier state {state}")
        if state.startswith(TOKEN_PREFIX):
            _require(bool(track.get("required_artifacts")), f"{track.get('id')}: TOKEN_VAZIO requires exit artifacts", errors)

    workflow = payload.get("workflow_policy", {})
    _require(workflow.get("publication_effect") == "NONE", "workflow publication effect must be NONE", errors)
    seeds = workflow.get("robust_seed_set", [])
    _require(len(seeds) >= 5 and len(seeds) == len(set(seeds)), "robust seed set must contain at least five unique seeds", errors)
    return errors


def validate_queue(payload: dict[str, Any], contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    _require(payload.get("schema") == QUEUE_SCHEMA, "unexpected queue schema", errors)
    _require(payload.get("claim_allowed") is False, "queue claim_allowed must remain false", errors)
    stage_ids = {stage["id"] for stage in contract["stages"]}
    items = payload.get("items", [])
    _require(isinstance(items, list) and bool(items), "queue must contain items", errors)
    ids: list[str] = []
    for item in items:
        if not isinstance(item, dict):
            errors.append("queue item must be a mapping")
            continue
        fid = str(item.get("fragment_id", ""))
        ids.append(fid)
        _require(fid.startswith("FRAG-"), f"{fid}: fragment_id must start FRAG-", errors)
        _require(item.get("current_stage") in stage_ids, f"{fid}: unknown current_stage", errors)
        refs = item.get("references", [])
        _require(isinstance(refs, list) and bool(refs), f"{fid}: at least one reference required", errors)
        for ref in refs:
            for field in ("source_id", "type", "locator"):
                _require(bool(ref.get(field)), f"{fid}: reference missing {field}", errors)
        gaps = item.get("gaps", [])
        _require(isinstance(gaps, list), f"{fid}: gaps must be a list", errors)
        for gap in gaps:
            _require(str(gap).startswith(TOKEN_PREFIX), f"{fid}: gap must be TOKEN_VAZIO", errors)
        state = str(item.get("state", ""))
        if not state.startswith(TOKEN_PREFIX) and state not in set(contract["state_policy"]["evidence_states"]) | {"ROUTED_SEPARATE_AUTHORITY"}:
            errors.append(f"{fid}: unsupported state {state}")
        if state.startswith(TOKEN_PREFIX):
            _require(bool(gaps), f"{fid}: TOKEN_VAZIO item requires exit gaps", errors)
    _require(len(ids) == len(set(ids)), "fragment ids must be unique", errors)
    return errors


def build_report(contract_path: Path, queue_path: Path) -> dict[str, Any]:
    contract = _load_yaml(contract_path)
    queue = _load_yaml(queue_path)
    errors = validate_contract(contract) + validate_queue(queue, contract)
    token_gaps = [
        gap
        for item in queue.get("items", [])
        for gap in item.get("gaps", [])
        if str(gap).startswith(TOKEN_PREFIX)
    ]
    return {
        "schema": "rll.frontier_research_composition.validation.v1",
        "status": "PASS" if not errors else "FAIL",
        "claim_allowed": False,
        "publication_effect": "NONE",
        "contract_sha256": _sha256(contract_path),
        "queue_sha256": _sha256(queue_path),
        "stage_count": len(contract.get("stages", [])),
        "prompt_pass_count": len(contract.get("prompt_evolution", {}).get("passes", [])),
        "frontier_track_count": len(contract.get("frontier_tracks", [])),
        "queue_item_count": len(queue.get("items", [])),
        "token_vazio_count": len(token_gaps),
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--queue", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    report = build_report(args.contract, args.queue)
    text = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
