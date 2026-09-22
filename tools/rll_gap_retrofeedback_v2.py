#!/usr/bin/env python3
"""Validate the multidimensional RLL gap retrofeedback ledger."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "data/governance/RLL_GAP_RETROFEEDBACK_V2.json"
GAPS = ROOT / "data/governance/RLL_GAP_DECOMPOSITION_V1.json"

REQUIRED_FIELDS = {
    "id",
    "domain",
    "state",
    "token_or_gap",
    "urgency",
    "priority_rank",
    "actionable_now",
    "priority_factors",
    "provenance",
    "evidence",
    "gate",
    "providencia",
    "mitigation",
    "non_regression",
    "receipt",
    "forward_dependency",
    "direct",
    "antiderivative_backtrace",
    "inverse_falsifier",
    "reverse_rollback",
    "exclusive_boundary",
    "recursive_feedback",
    "next_step",
    "claim_allowed",
}
ALLOWED_FACTORS = {1, 2, 4, 8}
ALLOWED_URGENCY = {"P0", "P1", "P2", "P3"}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def score(factors: dict[str, Any]) -> float:
    impact = factors["impact"]
    uncertainty = factors["uncertainty_reduction"]
    effort = factors["effort"]
    return math.log2(impact) + math.log2(uncertainty) - math.log2(effort)


def build_report() -> dict[str, Any]:
    ledger = load(LEDGER)
    gaps = load(GAPS)
    errors: list[str] = []

    items = ledger.get("items", [])
    gap_items = gaps.get("items", [])
    ledger_ids = [row.get("id") for row in items]
    gap_ids = [row.get("id") for row in gap_items]

    if len(ledger_ids) != len(set(ledger_ids)):
        errors.append("duplicate ledger ids")
    if set(ledger_ids) != set(gap_ids):
        errors.append(
            "ledger/gap id mismatch: "
            f"ledger_only={sorted(set(ledger_ids)-set(gap_ids))} "
            f"gap_only={sorted(set(gap_ids)-set(ledger_ids))}"
        )

    expected_ranks = list(range(1, len(items) + 1))
    observed_ranks = sorted(row.get("priority_rank") for row in items)
    if observed_ranks != expected_ranks:
        errors.append(
            f"priority ranks must be a complete 1..N permutation: {observed_ranks}"
        )

    for row in items:
        rid = row.get("id", "<unknown>")
        missing = sorted(REQUIRED_FIELDS - set(row))
        if missing:
            errors.append(f"{rid}: missing fields {missing}")
            continue

        if row["claim_allowed"] is not False:
            errors.append(f"{rid}: claim_allowed must remain false")
        if row["urgency"] not in ALLOWED_URGENCY:
            errors.append(f"{rid}: invalid urgency {row['urgency']}")
        if not isinstance(row["provenance"], list) or not row["provenance"]:
            errors.append(f"{rid}: provenance must be non-empty")
        if not isinstance(row["evidence"], list) or not row["evidence"]:
            errors.append(f"{rid}: evidence must be non-empty")

        factors = row["priority_factors"]
        if set(factors) != {
            "impact",
            "uncertainty_reduction",
            "effort",
            "log2_priority_score",
        }:
            errors.append(f"{rid}: priority factor schema mismatch")
        else:
            raw = {
                factors["impact"],
                factors["uncertainty_reduction"],
                factors["effort"],
            }
            if not raw <= ALLOWED_FACTORS:
                errors.append(f"{rid}: priority factors must be powers of two in {sorted(ALLOWED_FACTORS)}")
            expected = score(factors)
            if not math.isclose(
                float(factors["log2_priority_score"]),
                expected,
                rel_tol=0.0,
                abs_tol=1.0e-12,
            ):
                errors.append(
                    f"{rid}: log2 priority mismatch "
                    f"stored={factors['log2_priority_score']} expected={expected}"
                )

    critical = ledger.get("critical_path", [])
    missing_critical = [rid for rid in critical if rid not in set(ledger_ids)]
    if missing_critical:
        errors.append(f"critical path references missing ids: {missing_critical}")

    best = ledger.get("best_next_step", {}).get("id")
    if not critical or best != critical[0]:
        errors.append("best_next_step must equal critical_path[0]")
    by_id = {row["id"]: row for row in items}
    if best in by_id and by_id[best]["actionable_now"] is not True:
        errors.append("best_next_step must be actionable_now=true")

    for cid in (
        "CMB-RADIATION-001",
        "CMB-ZSTAR-001",
        "CMB-CS-001",
        "CMB-RS-001",
        "CMB-BENCH-001",
    ):
        if by_id.get(cid, {}).get("state") != "EVIDENCED_FOCUSED":
            errors.append(f"{cid}: expected EVIDENCED_FOCUSED after CAMB benchmark")

    growth = by_id.get("GROWTH-THEORY-001", {})
    if growth.get("state") != "NEGATIVE_EVIDENCE_TOKEN_DECOMPOSED":
        errors.append("GROWTH-THEORY-001 must preserve decomposed negative evidence")
    if "0 of 9" not in " ".join(str(x) for x in growth.get("evidence", [])):
        errors.append("GROWTH-THEORY-001 must preserve the 0/9 negative result")

    corpus_sha = {
        "c7df8b972be9e06f0bdc9c150ad16479e1e8a0d979c33e4dc97f50860781b2c7",
        "173f76c62bb675cf08c4658195d986016279737eed5b9a9262740aad27895479",
        "1ac69f2041f7652e9c0ed32bed927b30652b2e3d8aa341fde6334aba09372e2a",
    }
    seen_corpus = {
        src.get("sha256")
        for row in items
        for src in row.get("provenance", [])
        if src.get("type") == "project_corpus_external_to_repo"
    }
    if not corpus_sha <= seen_corpus:
        errors.append("project-corpus provenance hashes are incomplete")

    return {
        "schema": "rll.gap_retrofeedback_validation.v2",
        "pass": not errors,
        "claim_allowed": False,
        "errors": errors,
        "item_count": len(items),
        "critical_path": critical,
        "best_next_step": ledger.get("best_next_step"),
        "status": "RETROFEEDBACK_VALID" if not errors else "RETROFEEDBACK_BLOCKED",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = build_report()
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    print(payload, end="")
    if args.output:
        out = args.output if args.output.is_absolute() else ROOT / args.output
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(payload, encoding="utf-8")
    return 0 if report["pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
