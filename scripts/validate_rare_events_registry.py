#!/usr/bin/env python3
"""Deterministic dependency-free gate for the rare-events claim registry.

This validator checks governance invariants without interpreting scientific
truth. Unknown evidence remains TOKEN_VAZIO until promoted by a traceable source
and independent review.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REQUIRED_TOP_LEVEL = (
    "schema_version:",
    "registry_id:",
    "claim_allowed: false",
    "publication_ready: false",
    "classification:",
    "invariants:",
    "events:",
    "metrics:",
)
REQUIRED_INVARIANTS = (
    "evidence_before_claim",
    "preserve_unknowns",
    "use_intervals_without_telemetry",
    "declare_falsifiers",
    "no_victim_as_proof_of_unrelated_theory",
)
ALLOWED_STATES = {
    "PROVADO",
    "EVIDENCIADO",
    "HIPOTESE",
    "MODELO_ANALOGICO",
    "PARABOLA",
    "REFUTADO",
    "TOKEN_VAZIO",
}


def validate_text(text: str) -> list[str]:
    errors: list[str] = []
    for token in REQUIRED_TOP_LEVEL:
        if token not in text:
            errors.append(f"missing required token: {token}")
    for invariant in REQUIRED_INVARIANTS:
        if invariant not in text:
            errors.append(f"missing invariant: {invariant}")

    if re.search(r"^claim_allowed:\s*true\s*$", text, re.MULTILINE):
        errors.append("claim_allowed must remain false before independent review")
    if re.search(r"^publication_ready:\s*true\s*$", text, re.MULTILINE):
        errors.append("publication_ready must remain false before independent review")

    event_ids = re.findall(r"^\s*- event_id:\s*([^\s#]+)", text, re.MULTILINE)
    if not event_ids:
        errors.append("registry contains no events")
    if len(event_ids) != len(set(event_ids)):
        errors.append("duplicate event_id detected")

    claim_ids = re.findall(r"^\s*- id:\s*([^\s#]+)", text, re.MULTILINE)
    if not claim_ids:
        errors.append("registry contains no claims")
    if len(claim_ids) != len(set(claim_ids)):
        errors.append("duplicate claim id detected")

    states = re.findall(r"^\s*state:\s*([^\s#]+)", text, re.MULTILINE)
    unknown_states = sorted(set(states) - ALLOWED_STATES)
    if unknown_states:
        errors.append(f"unknown claim states: {', '.join(unknown_states)}")

    blocks = re.split(r"(?=^\s*- id:\s*)", text, flags=re.MULTILINE)[1:]
    for block in blocks:
        claim_match = re.search(r"^\s*- id:\s*([^\s#]+)", block, re.MULTILINE)
        if not claim_match:
            continue
        claim_id = claim_match.group(1)
        state_match = re.search(r"^\s*state:\s*([^\s#]+)", block, re.MULTILINE)
        state = state_match.group(1) if state_match else ""
        has_falsifier = bool(re.search(r"^\s*falsifier:\s*.+", block, re.MULTILINE))
        if state != "TOKEN_VAZIO" and not has_falsifier:
            errors.append(f"claim {claim_id} has state {state or '<missing>'} but no falsifier")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "registry",
        nargs="?",
        default="data/knowledge_forest/rare_events_claim_registry_v1.yml",
    )
    args = parser.parse_args()
    path = Path(args.registry)
    if not path.is_file():
        print(f"FAIL: registry not found: {path}", file=sys.stderr)
        return 2
    errors = validate_text(path.read_text(encoding="utf-8"))
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("PASS: RLL rare-events registry governance invariants satisfied")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
