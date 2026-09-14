#!/usr/bin/env python3
"""Fail-closed validator for the theory-practice calibration lattice."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

CALIBRATION_SCHEMA = "rll.theory_practice_calibration.v1"
LADDER_SCHEMA = "rll.frontier_possibility_ladder.v1"
QUEUE_SCHEMA = "rll.frontier_research_queue.v1"
EXPECTED_CALIBRATION_PATH = "data/contracts/theory_practice_calibration.v1.yml"
EXPECTED_STATES = [
    ("C5_INDEPENDENTLY_REPRODUCED", 5),
    ("C4_ROBUST_REPEATED", 4),
    ("C3_RECEIPTED_COMPARISON", 3),
    ("C2_EXECUTABLE_SHADOW", 2),
    ("C1_LINKED", 1),
    ("C0_TOKEN_VAZIO_UNCALIBRATED", 0),
]
EXPECTED_AXES = [
    "theory_scope_to_specific_model",
    "equation_or_algorithm_to_code",
    "observable_to_measurement",
    "parameter_to_configuration",
    "prediction_to_receipt",
    "falsifier_to_decision",
]
DELTA_STATES = {"EVIDENCED", "PARTIAL", "TOKEN_VAZIO"}
RELATION_STATES = {
    "APPROX_WORKING",
    "APPROX_BOUNDED",
    "NOT_EQUAL_OBSERVED",
    "TOKEN_VAZIO_UNDEFINED",
}


def load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: root must be a mapping")
    return payload


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def _nonempty_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value)


def validate_delta_axis(
    calibration_id: str,
    axis_name: str,
    axis: Any,
    errors: list[str],
) -> None:
    if not isinstance(axis, dict):
        errors.append(f"{calibration_id}/{axis_name}: delta axis must be a mapping")
        return
    state = axis.get("state")
    require(state in DELTA_STATES, f"{calibration_id}/{axis_name}: invalid delta state", errors)
    if state == "EVIDENCED":
        require(_nonempty_list(axis.get("evidence")), f"{calibration_id}/{axis_name}: EVIDENCED requires evidence", errors)
    elif state == "PARTIAL":
        require(_nonempty_list(axis.get("evidence")), f"{calibration_id}/{axis_name}: PARTIAL requires existing evidence", errors)
        require(bool(axis.get("missing")), f"{calibration_id}/{axis_name}: PARTIAL requires missing boundary", errors)
    elif state == "TOKEN_VAZIO":
        require(bool(axis.get("reason")), f"{calibration_id}/{axis_name}: TOKEN_VAZIO requires reason", errors)
        require(bool(axis.get("next_action")), f"{calibration_id}/{axis_name}: TOKEN_VAZIO requires next_action", errors)
        require(bool(axis.get("exit_criterion")), f"{calibration_id}/{axis_name}: TOKEN_VAZIO requires exit_criterion", errors)


def validate_contract(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    require(payload.get("schema") == CALIBRATION_SCHEMA, "unexpected calibration schema", errors)
    require(payload.get("claim_allowed") is False, "claim_allowed must remain false", errors)
    require(payload.get("publication_effect") == "NONE", "publication_effect must remain NONE", errors)

    notation = payload.get("symbolic_language", {})
    require(notation.get("working_relation") == "theory ~= practice", "working relation must remain theory ~= practice", errors)
    require(bool(notation.get("boundary")), "symbolic boundary is required", errors)
    for key in ("omega", "pi", "infinity", "scope_marker", "verification_marker", "provenance_marker"):
        require(bool(notation.get(key)), f"symbolic language missing {key}", errors)

    invariant = payload.get("knowledge_invariant", {})
    require(invariant.get("id") == "OMEGA_PI_INFINITY_DATA_INVARIANT", "knowledge invariant id changed", errors)
    require(invariant.get("append_only_transitions") is True, "calibration transitions must be append-only", errors)
    require(invariant.get("token_vazio_is_data") is True, "TOKEN_VAZIO must remain data", errors)
    require(invariant.get("silent_deletion_forbidden") is True, "silent deletion must remain forbidden", errors)

    states = payload.get("calibration_states", [])
    observed_states = [(item.get("id"), item.get("rank")) for item in states if isinstance(item, dict)]
    require(observed_states == EXPECTED_STATES, "calibration states must be complete and ordered C5 to C0", errors)
    require(payload.get("mandatory_delta_axes") == EXPECTED_AXES, "mandatory delta axes changed", errors)
    require(set(payload.get("delta_states", [])) == DELTA_STATES, "delta states changed", errors)

    rules = payload.get("rules", [])
    require(isinstance(rules, list) and len(rules) >= 8, "calibration rules are incomplete", errors)

    profiles = payload.get("profiles", [])
    require(_nonempty_list(profiles), "calibration profiles are required", errors)
    valid_calibration_states = {state_id for state_id, _ in EXPECTED_STATES}
    calibration_ids: list[str] = []
    fragment_ids: list[str] = []
    for profile in profiles:
        if not isinstance(profile, dict):
            errors.append("calibration profile must be a mapping")
            continue
        calibration_id = str(profile.get("calibration_id", ""))
        fragment_id = str(profile.get("fragment_id", ""))
        calibration_ids.append(calibration_id)
        fragment_ids.append(fragment_id)
        require(calibration_id.startswith("CAL-"), f"{calibration_id}: invalid calibration id", errors)
        require(fragment_id.startswith("FRAG-"), f"{calibration_id}: invalid fragment id", errors)
        require(profile.get("calibration_state") in valid_calibration_states, f"{calibration_id}: unknown calibration state", errors)
        require(profile.get("relation_state") in RELATION_STATES, f"{calibration_id}: unknown relation state", errors)
        require(bool(profile.get("exploration_tier")), f"{calibration_id}: exploration tier required", errors)
        require(bool(profile.get("promotion_state")), f"{calibration_id}: promotion state required", errors)
        require(bool(profile.get("scope_marker")), f"{calibration_id}: scope marker required", errors)
        require(_nonempty_list(profile.get("theory_anchors")), f"{calibration_id}: theory anchors required", errors)
        require(isinstance(profile.get("practice_anchors"), list), f"{calibration_id}: practice anchors must be a list", errors)
        require(bool(profile.get("next_execution")), f"{calibration_id}: next execution required", errors)

        vector = profile.get("delta_vector", {})
        require(isinstance(vector, dict), f"{calibration_id}: delta vector must be a mapping", errors)
        if isinstance(vector, dict):
            require(list(vector) == EXPECTED_AXES, f"{calibration_id}: delta axes must be complete and ordered", errors)
            for axis_name in EXPECTED_AXES:
                validate_delta_axis(calibration_id, axis_name, vector.get(axis_name), errors)

            token_count = sum(
                isinstance(vector.get(axis_name), dict)
                and vector[axis_name].get("state") == "TOKEN_VAZIO"
                for axis_name in EXPECTED_AXES
            )
            if profile.get("relation_state") == "APPROX_BOUNDED":
                require(token_count == 0, f"{calibration_id}: APPROX_BOUNDED cannot contain TOKEN_VAZIO", errors)
                require(vector.get("prediction_to_receipt", {}).get("state") == "EVIDENCED", f"{calibration_id}: bounded relation requires receipt", errors)
                require(vector.get("falsifier_to_decision", {}).get("state") == "EVIDENCED", f"{calibration_id}: bounded relation requires decision", errors)
            if profile.get("relation_state") == "NOT_EQUAL_OBSERVED":
                require(vector.get("prediction_to_receipt", {}).get("state") == "EVIDENCED", f"{calibration_id}: observed inequality requires receipt", errors)
                require(vector.get("falsifier_to_decision", {}).get("state") == "EVIDENCED", f"{calibration_id}: observed inequality requires decision", errors)
            if profile.get("calibration_state") == "C2_EXECUTABLE_SHADOW":
                require(_nonempty_list(profile.get("practice_anchors")), f"{calibration_id}: executable shadow requires practice anchor", errors)
                require(vector.get("equation_or_algorithm_to_code", {}).get("state") == "EVIDENCED", f"{calibration_id}: executable shadow requires equation-to-code evidence", errors)
            if profile.get("calibration_state") == "C0_TOKEN_VAZIO_UNCALIBRATED":
                require(profile.get("relation_state") == "TOKEN_VAZIO_UNDEFINED", f"{calibration_id}: C0 relation must be undefined", errors)

    require(len(calibration_ids) == len(set(calibration_ids)), "calibration ids must be unique", errors)
    require(len(fragment_ids) == len(set(fragment_ids)), "calibration fragment ids must be unique", errors)
    return errors


def validate_cross_links(
    calibration: dict[str, Any],
    ladder: dict[str, Any],
    queue: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    require(ladder.get("schema") == LADDER_SCHEMA, "unexpected ladder schema", errors)
    require(queue.get("schema") == QUEUE_SCHEMA, "unexpected queue schema", errors)
    require(
        ladder.get("calibration_contract") == EXPECTED_CALIBRATION_PATH,
        "ladder must point to the canonical calibration contract",
        errors,
    )
    require(
        ladder.get("separation_of_orders", {}).get("calibration_order")
        == "theory_execution_residual_decision_receipt",
        "ladder calibration order changed",
        errors,
    )
    ladder_by_id = {
        str(item.get("fragment_id")): item
        for item in ladder.get("portfolio", [])
        if isinstance(item, dict)
    }
    queue_by_id = {
        str(item.get("fragment_id")): item
        for item in queue.get("items", [])
        if isinstance(item, dict)
    }
    calibration_ids = {
        str(item.get("fragment_id"))
        for item in calibration.get("profiles", [])
        if isinstance(item, dict)
    }
    require(calibration_ids == set(ladder_by_id), "calibration must cover exactly the ranked portfolio", errors)
    for profile in calibration.get("profiles", []):
        if not isinstance(profile, dict):
            continue
        fragment_id = str(profile.get("fragment_id", ""))
        ranked = ladder_by_id.get(fragment_id)
        queued = queue_by_id.get(fragment_id)
        require(ranked is not None, f"{fragment_id}: absent from ladder", errors)
        require(queued is not None, f"{fragment_id}: absent from queue", errors)
        if ranked is not None:
            require(profile.get("exploration_tier") == ranked.get("exploration_tier"), f"{fragment_id}: exploration tier drift", errors)
            require(profile.get("calibration_id") == ranked.get("calibration_profile"), f"{fragment_id}: calibration profile drift", errors)
        if queued is not None:
            require(profile.get("promotion_state") == queued.get("state"), f"{fragment_id}: promotion state drift", errors)
    return errors


def build_report(calibration_path: Path, ladder_path: Path, queue_path: Path) -> dict[str, Any]:
    calibration = load_yaml(calibration_path)
    ladder = load_yaml(ladder_path)
    queue = load_yaml(queue_path)
    errors = validate_contract(calibration) + validate_cross_links(calibration, ladder, queue)
    delta_counts = {state: 0 for state in sorted(DELTA_STATES)}
    calibration_counts: dict[str, int] = {}
    relation_counts: dict[str, int] = {}
    for profile in calibration.get("profiles", []):
        if not isinstance(profile, dict):
            continue
        calibration_state = str(profile.get("calibration_state", "UNKNOWN"))
        relation_state = str(profile.get("relation_state", "UNKNOWN"))
        calibration_counts[calibration_state] = calibration_counts.get(calibration_state, 0) + 1
        relation_counts[relation_state] = relation_counts.get(relation_state, 0) + 1
        vector = profile.get("delta_vector", {})
        if isinstance(vector, dict):
            for axis in vector.values():
                if isinstance(axis, dict) and axis.get("state") in delta_counts:
                    delta_counts[str(axis["state"])] += 1
    return {
        "schema": "rll.theory_practice_calibration.validation.v1",
        "status": "PASS" if not errors else "FAIL",
        "claim_allowed": False,
        "publication_effect": "NONE",
        "calibration_sha256": sha256(calibration_path),
        "ladder_sha256": sha256(ladder_path),
        "queue_sha256": sha256(queue_path),
        "profile_count": len(calibration.get("profiles", [])),
        "mandatory_delta_axis_count": len(calibration.get("mandatory_delta_axes", [])),
        "calibration_state_counts": calibration_counts,
        "relation_state_counts": relation_counts,
        "delta_state_counts": delta_counts,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--calibration", type=Path, required=True)
    parser.add_argument("--ladder", type=Path, required=True)
    parser.add_argument("--queue", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    report = build_report(args.calibration, args.ladder, args.queue)
    text = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
