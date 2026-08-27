#!/usr/bin/env python3
from __future__ import annotations

"""Fail-closed ATLAS evolution gate for RLL scientific promotion.

This gate does not certify RLL physics. It validates the machine-readable G0-G7
promotion record, produces a bounded receipt, and rejects silent regression of
gate maturity, evidence custody, or invariants when a predecessor is supplied.
"""

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY = ROOT / "data/governance/RLL_ATLAS_EVOLUTION_GATE_20260827_V1.json"

REQUIRED_GATE_IDS = (
    "G0_SOURCE_RIGHTS_FREEZE",
    "G1_OBSERVABLE_SCHEMA",
    "G2_FULL_COVARIANCE",
    "G3_LIKELIHOOD_PARITY",
    "G4_BASELINE_RECOVERY",
    "G5_ROBUST_INFERENCE",
    "G6_GROWTH_PERTURBATIONS",
)
G7_ID = "G7_CLAIM_DECISION"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _evidence_key(item: dict[str, Any]) -> str:
    return json.dumps(item, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def validate_record(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if record.get("schema") != "rll.atlas_evolution_gate.v1":
        errors.append("schema must be rll.atlas_evolution_gate.v1")
    if record.get("append_only") is not True:
        errors.append("append_only must be true")
    if not isinstance(record.get("claim_allowed"), bool):
        errors.append("claim_allowed must be an exact boolean")
    if not isinstance(record.get("publication_ready"), bool):
        errors.append("publication_ready must be an exact boolean")

    status_maturity = record.get("status_maturity")
    if not isinstance(status_maturity, dict):
        errors.append("status_maturity must be an object")
        status_maturity = {}

    gates = record.get("gates")
    if not isinstance(gates, list):
        errors.append("gates must be a list")
        gates = []

    gate_ids = [g.get("id") for g in gates if isinstance(g, dict)]
    expected_ids = [*REQUIRED_GATE_IDS, G7_ID]
    if gate_ids != expected_ids:
        errors.append(f"gate order/identity mismatch: expected {expected_ids!r}, got {gate_ids!r}")

    by_id = {g.get("id"): g for g in gates if isinstance(g, dict) and isinstance(g.get("id"), str)}
    for gate_id in expected_ids:
        gate = by_id.get(gate_id)
        if gate is None:
            continue
        status = gate.get("status")
        maturity = gate.get("maturity")
        if status not in status_maturity:
            errors.append(f"{gate_id}: unknown status {status!r}")
        elif maturity != status_maturity[status]:
            errors.append(
                f"{gate_id}: maturity {maturity!r} does not match status {status!r} "
                f"({status_maturity[status]!r})"
            )
        if not isinstance(gate.get("source_state"), str) or not gate["source_state"]:
            errors.append(f"{gate_id}: source_state is required")
        if not isinstance(gate.get("required_output"), str) or not gate["required_output"]:
            errors.append(f"{gate_id}: required_output is required")
        if not isinstance(gate.get("falsifier"), str) or not gate["falsifier"]:
            errors.append(f"{gate_id}: falsifier is required")
        evidence = gate.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            errors.append(f"{gate_id}: evidence must be a non-empty list")
        else:
            for idx, item in enumerate(evidence):
                if not isinstance(item, dict):
                    errors.append(f"{gate_id}: evidence[{idx}] must be an object")
                    continue
                path = item.get("path")
                digest = item.get("git_blob_sha1")
                if not isinstance(path, str) or not path:
                    errors.append(f"{gate_id}: evidence[{idx}].path is required")
                if not isinstance(digest, str) or len(digest) != 40:
                    errors.append(f"{gate_id}: evidence[{idx}].git_blob_sha1 must be a 40-char Git blob SHA-1")

    contract = record.get("promotion_contract")
    if not isinstance(contract, dict):
        errors.append("promotion_contract must be an object")
        contract = {}

    if contract.get("required_gate_ids") != list(REQUIRED_GATE_IDS):
        errors.append("promotion_contract.required_gate_ids must exactly match G0-G6")
    minimum = contract.get("minimum_maturity_for_claim")
    if not isinstance(minimum, int) or isinstance(minimum, bool) or minimum < 1:
        errors.append("promotion_contract.minimum_maturity_for_claim must be a positive integer")
        minimum = 3

    blockers = record.get("blocking_tokens")
    if not isinstance(blockers, list):
        errors.append("blocking_tokens must be a list")
        blockers = []
    for idx, blocker in enumerate(blockers):
        if not isinstance(blocker, dict):
            errors.append(f"blocking_tokens[{idx}] must be an object")
            continue
        for key in ("token", "state", "required_for_claim"):
            if not isinstance(blocker.get(key), str) or not blocker[key]:
                errors.append(f"blocking_tokens[{idx}].{key} is required")

    preclaim_gates_pass = all(
        isinstance(by_id.get(gid), dict)
        and isinstance(by_id[gid].get("maturity"), int)
        and by_id[gid]["maturity"] >= minimum
        for gid in REQUIRED_GATE_IDS
    )
    g7 = by_id.get(G7_ID, {})
    g7_allowed = g7.get("status") in set(contract.get("g7_allowed_statuses_for_claim", []))
    blockers_closed = all(
        blocker.get("state") == blocker.get("required_for_claim")
        for blocker in blockers
        if isinstance(blocker, dict)
    )

    if record.get("claim_allowed") is True:
        if not preclaim_gates_pass:
            errors.append("claim_allowed=true requires every G0-G6 gate at minimum maturity")
        if not g7_allowed:
            errors.append("claim_allowed=true requires G7 in an allowed verified state")
        if contract.get("blocking_tokens_must_match_required_state") is True and not blockers_closed:
            errors.append("claim_allowed=true requires every blocking token at its required closure state")

    if record.get("publication_ready") is True and record.get("claim_allowed") is not True:
        errors.append("publication_ready=true requires claim_allowed=true")

    if not preclaim_gates_pass and g7.get("status") not in {"BLOCKED", "TOKEN_VAZIO"}:
        errors.append("G7 must remain BLOCKED/TOKEN_VAZIO while any G0-G6 prerequisite is below claim maturity")

    invariants = record.get("invariants")
    if not isinstance(invariants, list) or not invariants or any(not isinstance(x, str) or not x for x in invariants):
        errors.append("invariants must be a non-empty list of strings")

    authority = record.get("canonical_authority")
    if not isinstance(authority, dict):
        errors.append("canonical_authority must be an object")
    else:
        if authority.get("repository") != "instituto-Rafael/relativity-living-light":
            errors.append("canonical_authority.repository must point to the Institute RLL repository")
        if authority.get("repository_id") != 1046495816:
            errors.append("canonical_authority.repository_id mismatch")
        for key in ("head_sha", "tree_sha"):
            value = authority.get(key)
            if not isinstance(value, str) or len(value) != 40:
                errors.append(f"canonical_authority.{key} must be a 40-char SHA")

    return errors


def compare_no_regression(previous: dict[str, Any], candidate: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    prev_revision = previous.get("revision")
    cand_revision = candidate.get("revision")
    if not isinstance(prev_revision, int) or isinstance(prev_revision, bool):
        errors.append("previous revision must be an integer")
    if not isinstance(cand_revision, int) or isinstance(cand_revision, bool):
        errors.append("candidate revision must be an integer")
    elif isinstance(prev_revision, int) and cand_revision <= prev_revision:
        errors.append("candidate revision must be greater than predecessor revision")

    if candidate.get("predecessor") != previous.get("record_id"):
        errors.append("candidate.predecessor must equal previous.record_id")

    prev_gates = {g["id"]: g for g in previous.get("gates", []) if isinstance(g, dict) and "id" in g}
    cand_gates = {g["id"]: g for g in candidate.get("gates", []) if isinstance(g, dict) and "id" in g}
    for gate_id, prev_gate in prev_gates.items():
        cand_gate = cand_gates.get(gate_id)
        if cand_gate is None:
            errors.append(f"{gate_id}: gate removed")
            continue
        prev_maturity = prev_gate.get("maturity")
        cand_maturity = cand_gate.get("maturity")
        if isinstance(prev_maturity, int) and isinstance(cand_maturity, int) and cand_maturity < prev_maturity:
            errors.append(f"{gate_id}: maturity regression {prev_maturity} -> {cand_maturity}")
        prev_evidence = {_evidence_key(x) for x in prev_gate.get("evidence", []) if isinstance(x, dict)}
        cand_evidence = {_evidence_key(x) for x in cand_gate.get("evidence", []) if isinstance(x, dict)}
        removed = prev_evidence - cand_evidence
        if removed:
            errors.append(f"{gate_id}: evidence custody shrank by {len(removed)} item(s)")

    prev_invariants = set(previous.get("invariants", []))
    cand_invariants = set(candidate.get("invariants", []))
    removed_invariants = prev_invariants - cand_invariants
    if removed_invariants:
        errors.append(f"invariants removed: {sorted(removed_invariants)!r}")

    prev_tokens = {
        b.get("token"): b
        for b in previous.get("blocking_tokens", [])
        if isinstance(b, dict) and isinstance(b.get("token"), str)
    }
    cand_tokens = {
        b.get("token"): b
        for b in candidate.get("blocking_tokens", [])
        if isinstance(b, dict) and isinstance(b.get("token"), str)
    }
    removed_tokens = set(prev_tokens) - set(cand_tokens)
    if removed_tokens:
        errors.append(f"blocking tokens removed: {sorted(removed_tokens)!r}")

    return errors


def build_receipt(record: dict[str, Any], errors: list[str], regression_errors: list[str]) -> dict[str, Any]:
    gates = record.get("gates", [])
    preclaim = [g for g in gates if isinstance(g, dict) and g.get("id") in REQUIRED_GATE_IDS]
    verified_target = record.get("promotion_contract", {}).get("minimum_maturity_for_claim", 3)
    maturity_total = sum(int(g.get("maturity", 0)) for g in preclaim)
    denominator = len(REQUIRED_GATE_IDS) * int(verified_target or 1)
    readiness = maturity_total / denominator if denominator else 0.0

    return {
        "schema": "rll.atlas_evolution_gate.receipt.v1",
        "record_id": record.get("record_id"),
        "valid": not errors and not regression_errors,
        "claim_allowed": record.get("claim_allowed") is True and not errors and not regression_errors,
        "publication_ready": record.get("publication_ready") is True and not errors and not regression_errors,
        "scientific_promotion_gate_fraction": round(readiness, 6),
        "gate_states": {g.get("id"): g.get("status") for g in gates if isinstance(g, dict)},
        "blocking_tokens_open": [
            b.get("token")
            for b in record.get("blocking_tokens", [])
            if isinstance(b, dict) and b.get("state") != b.get("required_for_claim")
        ],
        "errors": errors,
        "regression_errors": regression_errors,
        "boundary": (
            "This receipt validates governance/evidence progression only. "
            "It is not evidence that RLL is physically correct or statistically preferred."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--previous", type=Path, default=None)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    candidate = load_json(args.candidate)
    errors = validate_record(candidate)
    regression_errors: list[str] = []
    if args.previous is not None:
        previous = load_json(args.previous)
        regression_errors.extend(validate_record(previous))
        regression_errors.extend(compare_no_regression(previous, candidate))

    receipt = build_receipt(candidate, errors, regression_errors)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, ensure_ascii=False, sort_keys=True))
    return 0 if receipt["valid"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
