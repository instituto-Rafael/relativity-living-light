#!/usr/bin/env python3
"""Validate the public science/analogy correction ledger for the 2026-07-16 session.

The validator checks provenance shape, mandatory epistemic states, public paths and
non-negotiable boundaries. It does not independently prove the scientific claims.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LEDGER = ROOT / "data" / "formulas" / "session_reality_science_claims_20260716.json"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

REQUIRED_STATES = {
    "VERIFIED_STANDARD",
    "VERIFIED_LIMITED",
    "MATHEMATICAL_IDENTITY",
    "HYPOTHESIS",
    "ANALOGY_ONLY",
    "DECLARED_BY_AUTHOR",
    "CONTRADICTION",
    "TOKEN_VAZIO",
    "CLAIM_BLOCKED",
}

REQUIRED_CLAIM_STATES = {
    "AI-BACKGROUND-001": "CONTRADICTION",
    "AI-LAYERS-002": "CONTRADICTION",
    "PHOTO-DIAGNOSIS-004": "CONTRADICTION",
    "FUNDAMENTAL-FORCES-005": "VERIFIED_STANDARD",
    "IONIC-BOND-006": "VERIFIED_STANDARD",
    "IONIC-CURVATURE-007": "MATHEMATICAL_IDENTITY",
    "POISSON-EQUATION-008": "VERIFIED_STANDARD",
    "WATER-AUTOPROTOLYSIS-009": "VERIFIED_STANDARD",
    "EIGEN-ZUNDEL-010": "VERIFIED_LIMITED",
    "WATER-MEMORY-011": "ANALOGY_ONLY",
    "PROTON-PRESSURE-012": "VERIFIED_LIMITED",
    "HYPERCUBE-013": "MATHEMATICAL_IDENTITY",
    "QUANTUM-AI-014": "CONTRADICTION",
    "BIO-ION-GRADIENTS-015": "VERIFIED_STANDARD",
    "RLL-CURRENT-EVIDENCE-016": "VERIFIED_LIMITED",
    "PARABLES-017": "ANALOGY_ONLY",
}

REQUIRED_INVARIANTS = {
    "metaphor_does_not_validate_physics": True,
    "hash_does_not_prove_scientific_truth": True,
    "private_content_copied": False,
    "unsupported_large_counts_forbidden": True,
    "negative_results_preserved": True,
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_ledger(path: Path = DEFAULT_LEDGER) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("science ledger must be a JSON object")
    return data


def validate_ledger(data: dict[str, Any], ledger_path: Path = DEFAULT_LEDGER) -> dict[str, Any]:
    if data.get("schema") != "rll.session_reality_science_claims.v1":
        raise ValueError("unexpected science ledger schema")
    if data.get("claim_allowed") is not False:
        raise ValueError("claim_allowed must remain false")
    if data.get("public_safe") is not True:
        raise ValueError("ledger must remain public_safe")

    source_scope = data.get("source_scope", {})
    export = source_scope.get("historical_export", {})
    if not SHA256_RE.fullmatch(str(export.get("sha256", ""))):
        raise ValueError("historical export SHA-256 is invalid")
    if export.get("conversation_count") != 709:
        raise ValueError("historical export conversation count changed")
    if export.get("target_materialized_message_count") != 87:
        raise ValueError("target historical conversation message count changed")
    if export.get("current_2026_session_complete_in_export") is not False:
        raise ValueError("historical export must not be represented as the complete 2026 session")

    public_documents = source_scope.get("public_documents", [])
    if not public_documents:
        raise ValueError("public document list is empty")
    for relative in public_documents:
        path = ROOT / str(relative)
        if not path.is_file():
            raise ValueError(f"public document is missing: {relative}")

    vocabulary = set(data.get("state_vocabulary", []))
    if vocabulary != REQUIRED_STATES:
        missing = sorted(REQUIRED_STATES - vocabulary)
        extra = sorted(vocabulary - REQUIRED_STATES)
        raise ValueError(f"state vocabulary mismatch; missing={missing}, extra={extra}")

    claims = data.get("claims", [])
    if not isinstance(claims, list) or not claims:
        raise ValueError("claims must be a non-empty list")

    by_id: dict[str, dict[str, Any]] = {}
    for claim in claims:
        claim_id = str(claim.get("id", ""))
        if not claim_id or claim_id in by_id:
            raise ValueError(f"invalid or duplicate claim id: {claim_id}")
        state = str(claim.get("state", ""))
        if state not in vocabulary:
            raise ValueError(f"{claim_id}: invalid state {state}")
        for field in ("domain", "statement", "correction", "falsifier_or_gate"):
            if not str(claim.get(field, "")).strip():
                raise ValueError(f"{claim_id}: missing {field}")
        by_id[claim_id] = claim

    for claim_id, expected_state in REQUIRED_CLAIM_STATES.items():
        if claim_id not in by_id:
            raise ValueError(f"required claim missing: {claim_id}")
        observed = by_id[claim_id]["state"]
        if observed != expected_state:
            raise ValueError(
                f"{claim_id}: state promotion blocked; expected {expected_state}, observed {observed}"
            )

    invariants = data.get("mandatory_invariants", {})
    if invariants != REQUIRED_INVARIANTS:
        raise ValueError("mandatory invariants changed")

    if not str(data.get("next_gate", "")).strip():
        raise ValueError("next_gate is empty")

    return {
        "schema": "rll.session_reality_science_claims.report.v1",
        "valid": True,
        "claim_allowed": False,
        "claim_count": len(claims),
        "state_count": len(vocabulary),
        "contradiction_count": sum(c["state"] == "CONTRADICTION" for c in claims),
        "analogy_count": sum(c["state"] == "ANALOGY_ONLY" for c in claims),
        "ledger_sha256": sha256_file(ledger_path),
        "next_gate": data["next_gate"],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--report", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = validate_ledger(load_ledger(args.ledger), args.ledger)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print("OK: session science claims remain source-bounded and metaphor-gated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
