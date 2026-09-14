#!/usr/bin/env python3
"""Validate the cross-repo relationship registry.

Structural audit only. This validator checks that beta/v2 relationship rows keep
evidence states, blocked claims, and next-verification actions. It does not
validate cross-repository integration or promote any scientific/hardware claim.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "docs" / "audits" / "CROSS_REPO_RELATIONSHIP_REGISTRY.md"
REQUIRED_COLUMNS = ["ID", "Relationship", "State", "Safe reading", "Blocked claim", "Next verification"]
ALLOWED_STATE_TOKENS = {
    "VERIFIED",
    "VERIFIED_LIMITED",
    "DECLARED_BY_AUTHOR",
    "HYPOTHESIS",
    "TOKEN_VAZIO",
    "CLAIM_BLOCKED",
}
FORBIDDEN_PROMOTION_PHRASES = [
    "already validated",
    "production ready",
    "validated integration",
    "scientific proof",
    "hardware validated",
]
STATUS_MARKERS = [
    "beta_relationship_registry / evidence_gated / no_claim_promotion",
    "v2_measured_entrelace / evidence_gated / no_claim_promotion / fail_closed",
]
WARNING_MARKERS = [
    "Do not treat this registry as proof of working integration.",
    "Do not treat the registry as proof of working integration.",
]
CHAIN_MARKERS = [
    "relationship -> evidence state -> verification -> small fix -> test -> artifact -> claim gate",
    "exact source + exact target + blob identity",
    "exact ref/path/blob SHA",
]
NEXT_ACTION_VERBS = (
    "Verify", "Define", "Check", "Keep", "Compare", "Resolve", "Use",
    "Validate", "Produce", "Locate", "Generate", "Import", "Recompute", "Emit",
    "Require", "Link",
)


def _split_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def extract_relationship_rows(text: str) -> list[dict[str, str]]:
    lines = text.splitlines()
    header_index = None
    for index, line in enumerate(lines):
        if line.startswith("| ID | Relationship | State |"):
            header_index = index
            break
    if header_index is None:
        raise ValueError("relationship table header not found")
    header = _split_row(lines[header_index])
    if header != REQUIRED_COLUMNS:
        raise ValueError(f"unexpected relationship table header: {header}")
    rows: list[dict[str, str]] = []
    for line in lines[header_index + 2 :]:
        if not line.startswith("|"):
            break
        cells = _split_row(line)
        if len(cells) != len(REQUIRED_COLUMNS):
            raise ValueError(f"malformed relationship row: {line}")
        rows.append(dict(zip(REQUIRED_COLUMNS, cells)))
    if not rows:
        raise ValueError("relationship table is empty")
    return rows


def validate_state_field(value: str) -> None:
    tokens = [token.strip() for token in value.split("/")]
    if not tokens or any(not token for token in tokens):
        raise ValueError(f"empty state token in: {value}")
    invalid = [token for token in tokens if token not in ALLOWED_STATE_TOKENS]
    if invalid:
        raise ValueError(f"unknown state token(s): {invalid}")


def validate_rows(rows: list[dict[str, str]]) -> None:
    seen_ids: set[str] = set()
    for row in rows:
        row_id = row["ID"]
        if row_id in seen_ids:
            raise ValueError(f"duplicate relationship ID: {row_id}")
        seen_ids.add(row_id)
        for column in REQUIRED_COLUMNS:
            if not row[column].strip():
                raise ValueError(f"{row_id}: empty column {column}")
        validate_state_field(row["State"])
        combined = " ".join(row.values()).lower()
        for phrase in FORBIDDEN_PROMOTION_PHRASES:
            if phrase in combined:
                raise ValueError(f"{row_id}: forbidden promotion phrase: {phrase}")
        if row["State"] != "VERIFIED" and not row["Blocked claim"].strip():
            raise ValueError(f"{row_id}: non-verified relationship must keep a blocked claim")
        action = row["Next verification"]
        if not any(verb in action for verb in NEXT_ACTION_VERBS):
            raise ValueError(
                f"{row_id}: next verification must name an explicit audit action; "
                f"expected one of {NEXT_ACTION_VERBS}"
            )


def validate_text(text: str) -> None:
    if not any(marker in text for marker in STATUS_MARKERS):
        raise ValueError(f"missing registry status marker; expected one of: {STATUS_MARKERS}")
    if not any(marker in text for marker in WARNING_MARKERS):
        raise ValueError(f"missing no-promotion warning; expected one of: {WARNING_MARKERS}")
    if not any(marker in text for marker in CHAIN_MARKERS):
        raise ValueError(f"missing traceability-chain marker; expected one of: {CHAIN_MARKERS}")
    validate_rows(extract_relationship_rows(text))


def main() -> int:
    text = REGISTRY.read_text(encoding="utf-8")
    validate_text(text)
    print("OK: cross-repo relationship registry is evidence-gated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
