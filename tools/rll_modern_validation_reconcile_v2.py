#!/usr/bin/env python3
from __future__ import annotations

"""Fail-closed reconciliation of Modern Validation V1 to canonical V4 tokens.

The reconciliation follows successor chains instead of interpreting an old gate
name or receipt path as the current work item. A legacy gate may have no current
OPEN target only when its declared historical chain is demonstrably non-OPEN in
V4. No token state is changed by this tool.
"""

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from tools.rll_token_vazio_reconcile_v2 import ROOT
from tools.rll_token_vazio_reconcile_v4 import build_current_view

LEGACY = Path("data/governance/RLL_MODERN_VALIDATION_GAPS_20260807_V1.json")
RECONCILIATION = Path("data/governance/RLL_MODERN_VALIDATION_RECONCILIATION_20260808_V2.json")
OUTPUT = Path("artifacts/governance/RLL_MODERN_VALIDATION_RECONCILIATION_V2_CURRENT.json")
SCHEMA = "rll.modern_validation_reconciliation.v2"
NO_OPEN_SUCCESSOR_RELATION = "HISTORICAL_REDUCED_SUCCESSOR_CHAIN_TERMINAL"
EVIDENCE_REQUIRED_STATES = {
    "HISTORICAL_CHAIN_TERMINAL_NO_CURRENT_OPEN_SUCCESSOR",
    "HISTORICAL_AND_MODERN_SN_ONLY_NESTED_EVIDENCE_EXISTS",
    "REDUCED_RUNTIME_EVIDENCE_MATERIALIZED",
    "REDUCED_NEGATIVE_AND_CONTROL_EVIDENCE",
}


@dataclass(frozen=True)
class Result:
    schema: str
    decision: str
    claim_allowed: bool
    publication_effect: str
    current_token_view: str
    legacy_gate_count: int
    mapped_gate_count: int
    unmapped_legacy_gates: list[str]
    duplicate_legacy_mappings: list[str]
    no_open_successor_legacy_gates: list[str]
    current_target_count: int
    missing_current_targets: list[str]
    nonopen_current_targets: list[str]
    reduced_mappings_without_evidence: list[str]
    invalid_historical_chain_entries: list[str]
    modern_sn_chain_closed: bool
    errors: list[str]


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: object required")
    return value


def validate_evidence(root: Path, gate_id: str, evidence: Any, errors: list[str]) -> bool:
    if not isinstance(evidence, list):
        errors.append(f"{gate_id}: evidence must be list")
        return False
    valid_count = 0
    for index, item in enumerate(evidence):
        prefix = f"{gate_id}.evidence[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix}: object required")
            continue
        kind = item.get("kind")
        fact = item.get("fact")
        if not isinstance(kind, str) or not kind.strip():
            errors.append(f"{prefix}.kind: required")
        if not isinstance(fact, str) or not fact.strip():
            errors.append(f"{prefix}.fact: required")
        evidence_path = item.get("evidence_path")
        if evidence_path is not None:
            if not isinstance(evidence_path, str) or not evidence_path.strip():
                errors.append(f"{prefix}.evidence_path: non-empty string required")
            elif not (root / evidence_path).is_file():
                errors.append(f"{prefix}.evidence_path does not exist: {evidence_path}")
            else:
                valid_count += 1
        elif item.get("run_id") is not None or item.get("artifact_id") is not None:
            if not isinstance(item.get("run_id"), int) or item["run_id"] <= 0:
                errors.append(f"{prefix}.run_id: positive integer required")
            if not isinstance(item.get("artifact_id"), int) or item["artifact_id"] <= 0:
                errors.append(f"{prefix}.artifact_id: positive integer required")
            digest = item.get("artifact_sha256")
            if not isinstance(digest, str) or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest.lower()):
                errors.append(f"{prefix}.artifact_sha256: 64 hex chars required")
            else:
                valid_count += 1
        elif kind == "repository_receipt_chain":
            # The concrete files are validated separately by historical_chain.
            valid_count += 1
        else:
            errors.append(f"{prefix}: either evidence_path or run/artifact custody is required")
    return valid_count > 0


def validate_historical_chain(
    root: Path,
    gate_id: str,
    chain: Any,
    current_by_token: dict[str, dict[str, Any]],
    invalid: set[str],
    errors: list[str],
) -> bool:
    if not isinstance(chain, list) or not chain:
        errors.append(f"{gate_id}: historical_chain must be non-empty for terminal successor relation")
        invalid.add(gate_id)
        return False
    seen: set[str] = set()
    all_nonopen = True
    for index, item in enumerate(chain):
        prefix = f"{gate_id}.historical_chain[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix}: object required")
            invalid.add(gate_id)
            all_nonopen = False
            continue
        token = item.get("token")
        expected_state = item.get("expected_state")
        evidence_path = item.get("evidence_path")
        if not isinstance(token, str) or not token:
            errors.append(f"{prefix}.token: required")
            invalid.add(gate_id)
            all_nonopen = False
            continue
        if token in seen:
            errors.append(f"{prefix}: duplicate chain token {token}")
            invalid.add(gate_id)
        seen.add(token)
        row = current_by_token.get(token)
        if row is None:
            errors.append(f"{prefix}: token missing from V4: {token}")
            invalid.add(gate_id)
            all_nonopen = False
        else:
            actual_state = row.get("state")
            if expected_state != actual_state:
                errors.append(f"{prefix}: state mismatch {token}: expected={expected_state!r} actual={actual_state!r}")
                invalid.add(gate_id)
                all_nonopen = False
            if isinstance(actual_state, str) and actual_state.startswith("OPEN_"):
                errors.append(f"{prefix}: terminal-chain token is still OPEN: {token}")
                invalid.add(gate_id)
                all_nonopen = False
        if not isinstance(evidence_path, str) or not evidence_path.strip():
            errors.append(f"{prefix}.evidence_path: required")
            invalid.add(gate_id)
            all_nonopen = False
        elif not (root / evidence_path).is_file():
            errors.append(f"{prefix}.evidence_path does not exist: {evidence_path}")
            invalid.add(gate_id)
            all_nonopen = False
    return all_nonopen


def validate(root: Path = ROOT, reconciliation_path: Path = RECONCILIATION) -> Result:
    root = root.resolve()
    errors: list[str] = []
    legacy = load(root / LEGACY)
    rec_path = reconciliation_path if reconciliation_path.is_absolute() else root / reconciliation_path
    rec = load(rec_path)

    if rec.get("schema") != SCHEMA:
        errors.append(f"schema must be {SCHEMA}")
    if rec.get("claim_allowed") is not False or rec.get("publication_ready") is not False:
        errors.append("claim_allowed/publication_ready must remain false")
    if rec.get("append_only") is not True:
        errors.append("append_only must be true")
    if rec.get("source_registry") != str(LEGACY):
        errors.append("source_registry mismatch")
    if rec.get("current_token_view") != "RLL_TOKEN_VAZIO_RECONCILIATION_V4_APPEND_ONLY":
        errors.append("current_token_view must be the canonical V4 append-only view")
    if rec.get("old_required_paths_authority") != "HISTORICAL_ONLY_UNLESS_REASSERTED_BY_V2":
        errors.append("old receipt path authority must be historical-only")

    legacy_gates = legacy.get("gates") if isinstance(legacy.get("gates"), list) else []
    legacy_by_id = {
        gate.get("id"): gate
        for gate in legacy_gates
        if isinstance(gate, dict) and isinstance(gate.get("id"), str)
    }
    mappings = rec.get("mappings") if isinstance(rec.get("mappings"), list) else []
    current_view = build_current_view(root, generated_at="2026-08-08T07:25:00Z")
    current_by_token = {row["token"]: row for row in current_view["results"]}

    seen: set[str] = set()
    duplicates: set[str] = set()
    no_open_successor: set[str] = set()
    current_targets: set[str] = set()
    missing_targets: set[str] = set()
    nonopen_targets: set[str] = set()
    reduced_without_evidence: set[str] = set()
    invalid_chain: set[str] = set()
    modern_sn_chain_closed = False

    for index, mapping in enumerate(mappings):
        prefix = f"mappings[{index}]"
        if not isinstance(mapping, dict):
            errors.append(f"{prefix}: object required")
            continue
        gate_id = mapping.get("legacy_gate_id")
        if not isinstance(gate_id, str) or gate_id not in legacy_by_id:
            errors.append(f"{prefix}.legacy_gate_id: unknown")
            continue
        if gate_id in seen:
            duplicates.add(gate_id)
        seen.add(gate_id)
        expected_legacy_token = legacy_by_id[gate_id].get("token_vazio")
        if mapping.get("legacy_token") != expected_legacy_token:
            errors.append(f"{gate_id}: legacy token mismatch")

        relation = mapping.get("relation")
        if not isinstance(relation, str) or not relation:
            errors.append(f"{gate_id}: relation required")
            relation = ""
        targets = mapping.get("current_tokens")
        if not isinstance(targets, list) or any(not isinstance(token, str) for token in targets):
            errors.append(f"{gate_id}: current_tokens must be list[str]")
            targets = []

        if not targets:
            if relation != NO_OPEN_SUCCESSOR_RELATION:
                errors.append(f"{gate_id}: empty current_tokens allowed only for {NO_OPEN_SUCCESSOR_RELATION}")
            else:
                no_open_successor.add(gate_id)
                chain_ok = validate_historical_chain(
                    root,
                    gate_id,
                    mapping.get("historical_chain"),
                    current_by_token,
                    invalid_chain,
                    errors,
                )
                if gate_id == "RLL-MOD-P0-SN-CALIBRATION-COVARIANCE":
                    modern_sn_chain_closed = chain_ok
        else:
            if relation == NO_OPEN_SUCCESSOR_RELATION:
                errors.append(f"{gate_id}: terminal successor relation cannot also expose current OPEN targets")
            for token in targets:
                current_targets.add(token)
                row = current_by_token.get(token)
                if row is None:
                    missing_targets.add(token)
                elif not str(row.get("state", "")).startswith("OPEN_"):
                    nonopen_targets.add(token)

        evidence_state = mapping.get("evidence_state")
        if not isinstance(evidence_state, str) or not evidence_state:
            errors.append(f"{gate_id}: evidence_state required")
            evidence_state = ""
        evidence_valid = validate_evidence(root, gate_id, mapping.get("evidence"), errors)
        if evidence_state in EVIDENCE_REQUIRED_STATES and not evidence_valid:
            reduced_without_evidence.add(gate_id)
        if not isinstance(mapping.get("residual"), str) or not mapping["residual"].strip():
            errors.append(f"{gate_id}: residual required")

    unmapped = sorted(set(legacy_by_id) - seen)
    if unmapped:
        errors.append("unmapped legacy gates: " + ", ".join(unmapped))
    if duplicates:
        errors.append("duplicate legacy mappings: " + ", ".join(sorted(duplicates)))
    if missing_targets:
        errors.append("missing current targets: " + ", ".join(sorted(missing_targets)))
    if nonopen_targets:
        errors.append("current target tokens must remain OPEN in V4: " + ", ".join(sorted(nonopen_targets)))
    if reduced_without_evidence:
        errors.append("evidence-bearing mappings lack valid custody: " + ", ".join(sorted(reduced_without_evidence)))
    if invalid_chain:
        errors.append("invalid historical successor chains: " + ", ".join(sorted(invalid_chain)))
    if not modern_sn_chain_closed:
        errors.append("modern SN legacy successor chain is not demonstrably non-OPEN in V4")

    return Result(
        schema="rll.modern_validation_reconciliation_gate.v2",
        decision="PASS" if not errors else "BLOCKED",
        claim_allowed=False,
        publication_effect="NONE",
        current_token_view=str(current_view.get("view")),
        legacy_gate_count=len(legacy_by_id),
        mapped_gate_count=len(seen),
        unmapped_legacy_gates=unmapped,
        duplicate_legacy_mappings=sorted(duplicates),
        no_open_successor_legacy_gates=sorted(no_open_successor),
        current_target_count=len(current_targets),
        missing_current_targets=sorted(missing_targets),
        nonopen_current_targets=sorted(nonopen_targets),
        reduced_mappings_without_evidence=sorted(reduced_without_evidence),
        invalid_historical_chain_entries=sorted(invalid_chain),
        modern_sn_chain_closed=modern_sn_chain_closed,
        errors=errors,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--reconciliation", type=Path, default=RECONCILIATION)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    result = validate(args.repo_root, args.reconciliation)
    root = args.repo_root.resolve()
    output = args.output if args.output.is_absolute() else root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(asdict(result), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "decision": result.decision,
        "legacy_gate_count": result.legacy_gate_count,
        "mapped_gate_count": result.mapped_gate_count,
        "no_open_successor_legacy_gates": result.no_open_successor_legacy_gates,
        "current_target_count": result.current_target_count,
        "modern_sn_chain_closed": result.modern_sn_chain_closed,
        "error_count": len(result.errors),
    }, sort_keys=True))
    for error in result.errors:
        print("ERROR:", error)
    return 0 if result.decision == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
