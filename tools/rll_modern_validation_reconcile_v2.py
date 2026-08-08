#!/usr/bin/env python3
from __future__ import annotations

"""Fail-closed reconciliation of Modern Validation V1 to canonical V5 tokens."""

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from tools.rll_token_vazio_reconcile_v2 import ROOT
from tools.rll_token_vazio_reconcile_v5 import build_current_view

LEGACY = Path("data/governance/RLL_MODERN_VALIDATION_GAPS_20260807_V1.json")
RECONCILIATION = Path("data/governance/RLL_MODERN_VALIDATION_RECONCILIATION_20260808_V2.json")
OUTPUT = Path("artifacts/governance/RLL_MODERN_VALIDATION_RECONCILIATION_V2_CURRENT.json")
SCHEMA = "rll.modern_validation_reconciliation.v2"
REDUCED_STATES = {
    "REDUCED_RUNTIME_EVIDENCE_MATERIALIZED",
    "REDUCED_NEGATIVE_AND_CONTROL_EVIDENCE",
}


@dataclass(frozen=True)
class Result:
    schema: str
    decision: str
    claim_allowed: bool
    publication_effect: str
    legacy_gate_count: int
    mapped_gate_count: int
    unmapped_legacy_gates: list[str]
    duplicate_legacy_mappings: list[str]
    current_target_count: int
    missing_current_targets: list[str]
    terminal_targets_misrepresented_as_open_evidence: list[str]
    reduced_mappings_without_evidence: list[str]
    modern_sn_surfaced: bool
    errors: list[str]


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: object required")
    return value


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
    if rec.get("old_required_paths_authority") != "HISTORICAL_ONLY_UNLESS_REASSERTED_BY_V2":
        errors.append("old receipt path authority must be historical-only")

    legacy_gates = legacy.get("gates") if isinstance(legacy.get("gates"), list) else []
    legacy_by_id = {
        gate.get("id"): gate for gate in legacy_gates if isinstance(gate, dict) and isinstance(gate.get("id"), str)
    }
    mappings = rec.get("mappings") if isinstance(rec.get("mappings"), list) else []
    seen: set[str] = set()
    duplicates: list[str] = []
    current_view = build_current_view(root, generated_at="2026-08-08T07:15:00Z")
    current_by_token = {row["token"]: row for row in current_view["results"]}
    current_targets: set[str] = set()
    missing_targets: set[str] = set()
    terminal_misrep: set[str] = set()
    reduced_without_evidence: set[str] = set()

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
            duplicates.append(gate_id)
        seen.add(gate_id)
        expected_legacy_token = legacy_by_id[gate_id].get("token_vazio")
        if mapping.get("legacy_token") != expected_legacy_token:
            errors.append(f"{gate_id}: legacy token mismatch")
        targets = mapping.get("current_tokens")
        if not isinstance(targets, list) or not targets or any(not isinstance(token, str) for token in targets):
            errors.append(f"{gate_id}: current_tokens must be non-empty list[str]")
            continue
        evidence_state = mapping.get("evidence_state")
        if not isinstance(evidence_state, str) or not evidence_state:
            errors.append(f"{gate_id}: evidence_state required")
        evidence = mapping.get("evidence")
        if not isinstance(evidence, list):
            errors.append(f"{gate_id}: evidence must be list")
            evidence = []
        if evidence_state in REDUCED_STATES and not evidence:
            reduced_without_evidence.add(gate_id)
        for ev_index, item in enumerate(evidence):
            if not isinstance(item, dict):
                errors.append(f"{gate_id}.evidence[{ev_index}]: object required")
                continue
            for field in ("kind", "run_id", "artifact_id", "artifact_sha256", "fact"):
                if field not in item or item[field] in (None, ""):
                    errors.append(f"{gate_id}.evidence[{ev_index}].{field}: required")
            digest = item.get("artifact_sha256")
            if not isinstance(digest, str) or len(digest) != 64:
                errors.append(f"{gate_id}.evidence[{ev_index}].artifact_sha256: 64 hex chars required")
        if not isinstance(mapping.get("residual"), str) or not mapping["residual"].strip():
            errors.append(f"{gate_id}: residual required")
        for token in targets:
            current_targets.add(token)
            row = current_by_token.get(token)
            if row is None:
                missing_targets.add(token)
                continue
            if not str(row.get("state", "")).startswith("OPEN_"):
                terminal_misrep.add(token)

    unmapped = sorted(set(legacy_by_id) - seen)
    if unmapped:
        errors.append("unmapped legacy gates: " + ", ".join(unmapped))
    if duplicates:
        errors.append("duplicate legacy mappings: " + ", ".join(sorted(set(duplicates))))
    if missing_targets:
        errors.append("missing current targets: " + ", ".join(sorted(missing_targets)))
    if terminal_misrep:
        errors.append("mapping targets are not currently OPEN: " + ", ".join(sorted(terminal_misrep)))
    if reduced_without_evidence:
        errors.append("reduced mappings lack evidence: " + ", ".join(sorted(reduced_without_evidence)))

    sn_surfaced = "TOKEN_VAZIO_MODERN_SN_FULL_LIKELIHOOD" in current_targets and (
        current_by_token.get("TOKEN_VAZIO_MODERN_SN_FULL_LIKELIHOOD", {}).get("state") == "OPEN_MIXED"
    )
    if not sn_surfaced:
        errors.append("modern SN legacy gap was not surfaced into canonical V5")

    return Result(
        schema="rll.modern_validation_reconciliation_gate.v2",
        decision="PASS" if not errors else "BLOCKED",
        claim_allowed=False,
        publication_effect="NONE",
        legacy_gate_count=len(legacy_by_id),
        mapped_gate_count=len(seen),
        unmapped_legacy_gates=unmapped,
        duplicate_legacy_mappings=sorted(set(duplicates)),
        current_target_count=len(current_targets),
        missing_current_targets=sorted(missing_targets),
        terminal_targets_misrepresented_as_open_evidence=sorted(terminal_misrep),
        reduced_mappings_without_evidence=sorted(reduced_without_evidence),
        modern_sn_surfaced=sn_surfaced,
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
        "current_target_count": result.current_target_count,
        "modern_sn_surfaced": result.modern_sn_surfaced,
        "error_count": len(result.errors),
    }, sort_keys=True))
    for error in result.errors:
        print("ERROR:", error)
    return 0 if result.decision == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
