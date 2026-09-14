#!/usr/bin/env python3
"""Validate the single-session, multi-lens repository interaction contract.

This validator checks structure, repository routing and epistemic boundaries. It does
not fetch private bodies, execute cross-repository code or prove scientific claims.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "data" / "knowledge" / "session_unified_interaction_20260716.json"

REQUIRED_LENSES = {
    "LENS-WORKFLOW",
    "LENS-GEOMETRY",
    "LENS-REPOSITORIES",
    "LENS-AUDIT",
}
REQUIRED_REPOSITORIES = {
    "instituto-Rafael/relativity-living-light",
    "rafaelmeloreisnovo/ChipQuantum",
    "rafaelmeloreisnovo/papers",
    "rafaelmeloreisnovo/termux-app-rafacodephi",
    "rafaelmeloreisnovo/Vectras-VM-Android",
}
REQUIRED_STATES = {"VERIFIED", "VERIFIED_LIMITED", "PARTIAL", "TOKEN_VAZIO"}
REQUIRED_INVARIANTS = {
    "private_content_copied": False,
    "automatic_cross_repo_write": False,
    "automatic_merge": False,
    "destructive_actions": False,
    "metaphor_validates_physics": False,
    "hash_proves_scientific_truth": False,
    "negative_results_preserved": True,
    "token_vazio_can_be_inferred": False,
}


def load_manifest(path: Path = DEFAULT_MANIFEST) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("unified interaction manifest must be a JSON object")
    return data


def validate_manifest(data: dict[str, Any], root: Path = ROOT) -> dict[str, Any]:
    if data.get("schema") != "rll.session_unified_interaction.v1":
        raise ValueError("unexpected unified interaction schema")
    if data.get("operation_id") != "SESSION-UNIFIED-20260716-001":
        raise ValueError("unexpected operation id")
    if data.get("claim_allowed") is not False:
        raise ValueError("claim_allowed must remain false")

    lenses = data.get("source_lenses")
    if not isinstance(lenses, list) or not lenses:
        raise ValueError("source_lenses must be a non-empty list")
    lens_ids = [str(item.get("id", "")) for item in lenses]
    if set(lens_ids) != REQUIRED_LENSES or len(lens_ids) != len(set(lens_ids)):
        raise ValueError("source lens set is incomplete or duplicated")
    for lens in lenses:
        if lens.get("private_content_copied") is not False:
            raise ValueError(f"{lens.get('id')}: private content must not be copied")
        if not str(lens.get("role", "")).strip():
            raise ValueError(f"{lens.get('id')}: role is required")

    routes = data.get("repository_routes")
    if not isinstance(routes, list) or not routes:
        raise ValueError("repository_routes must be a non-empty list")
    repositories = [str(route.get("repository", "")) for route in routes]
    if set(repositories) != REQUIRED_REPOSITORIES or len(repositories) != len(set(repositories)):
        raise ValueError("repository route set is incomplete or duplicated")
    route_by_repo = {route["repository"]: route for route in routes}
    if route_by_repo["rafaelmeloreisnovo/papers"].get("write_state") != "POINTER_ONLY":
        raise ValueError("private papers repository must remain POINTER_ONLY")
    for repo in ("rafaelmeloreisnovo/termux-app-rafacodephi", "rafaelmeloreisnovo/Vectras-VM-Android"):
        if route_by_repo[repo].get("write_state") != "NO_WRITE_THIS_OPERATION":
            raise ValueError(f"{repo}: current operation must not claim a write")

    claims = data.get("claims")
    if not isinstance(claims, list) or not claims:
        raise ValueError("claims must be a non-empty list")
    claim_ids: set[str] = set()
    states: set[str] = set()
    for claim in claims:
        claim_id = str(claim.get("id", ""))
        state = str(claim.get("state", ""))
        if not claim_id or claim_id in claim_ids:
            raise ValueError(f"invalid or duplicate claim id: {claim_id}")
        if state not in REQUIRED_STATES:
            raise ValueError(f"{claim_id}: invalid state {state}")
        for field in ("statement", "gate"):
            if not str(claim.get(field, "")).strip():
                raise ValueError(f"{claim_id}: missing {field}")
        claim_ids.add(claim_id)
        states.add(state)
    if not REQUIRED_STATES.issubset(states):
        raise ValueError("claims must exercise every required epistemic state")

    contradictions = data.get("contradictions_resolved")
    if not isinstance(contradictions, list) or len(contradictions) < 2:
        raise ValueError("resolved contradictions are incomplete")
    resolutions = {item.get("resolution") for item in contradictions}
    if {"SESSION_TARGET_REPOSITORIES", "TEMPORAL_STATE_SPLIT"} - resolutions:
        raise ValueError("mandatory contradiction resolutions are missing")

    if data.get("mandatory_invariants") != REQUIRED_INVARIANTS:
        raise ValueError("mandatory invariants changed")

    artifacts = data.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        raise ValueError("artifact list is empty")
    missing = [relative for relative in artifacts if not (root / relative).is_file()]
    if missing:
        raise ValueError(f"declared artifact(s) missing: {missing}")

    next_gate = str(data.get("next_gate", "")).strip()
    if not next_gate:
        raise ValueError("next_gate is empty")

    return {
        "schema": "rll.session_unified_interaction.report.v1",
        "valid": True,
        "claim_allowed": False,
        "lens_count": len(lenses),
        "repository_route_count": len(routes),
        "claim_count": len(claims),
        "contradiction_resolution_count": len(contradictions),
        "private_content_copied": False,
        "automatic_cross_repo_write": False,
        "next_gate": next_gate,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--report", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = validate_manifest(load_manifest(args.manifest))
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print("OK: session interactions form one source-preserving, repository-routed unit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
