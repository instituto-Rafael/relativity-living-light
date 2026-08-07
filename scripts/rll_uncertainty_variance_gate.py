#!/usr/bin/env python3
"""Validate the RLL uncertainty/variance ledger and emit a fail-closed receipt.

This gate manages uncertainty rather than pretending to remove it.  Every open
scientific uncertainty must name its variance axis, TOKEN_VAZIO state and next
falsifiable experiment.  Numeric urgency is triage metadata only; it is never a
scientific significance or posterior probability.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

LEDGER_SCHEMA = "rll.uncertainty_variance_ledger.v1"
RECEIPT_SCHEMA = "rll.uncertainty_variance_receipt.v1"
DEFAULT_LEDGER = Path("data/governance/RLL_UNCERTAINTY_VARIANCE_LEDGER_20260807_V1.json")
PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("ledger JSON root must be an object")
    return value


def git_sha(root: Path) -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=root, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def _require_token(value: Any, *, location: str) -> str:
    if not isinstance(value, str) or not value.startswith("TOKEN_VAZIO_"):
        raise ValueError(f"{location}: explicit TOKEN_VAZIO_* required")
    return value


def validate_ledger(ledger: dict[str, Any]) -> None:
    if ledger.get("schema") != LEDGER_SCHEMA:
        raise ValueError(f"schema must be {LEDGER_SCHEMA}")
    if ledger.get("claim_allowed") is not False or ledger.get("publication_ready") is not False:
        raise ValueError("ledger must preserve claim_allowed=false and publication_ready=false")

    policy = ledger.get("policy")
    if not isinstance(policy, dict):
        raise ValueError("policy must be an object")
    required_true = {
        "token_vazio_is_valid_auditable_state",
        "variance_must_name_its_axis",
        "variance_not_estimable_must_name_next_experiment",
        "negative_results_are_preserved",
        "paper_context_is_not_materialized_evidence",
        "optimizer_convergence_is_not_parameter_identifiability",
        "bic_is_not_log_evidence",
        "point_estimate_is_not_covariance",
        "stale_receipts_are_not_deleted",
        "supersession_is_append_only",
    }
    missing_policy = sorted(key for key in required_true if policy.get(key) is not True)
    if missing_policy:
        raise ValueError(f"required policy flags are not true: {missing_policy}")

    axes = ledger.get("variance_axes")
    if not isinstance(axes, dict) or not axes:
        raise ValueError("variance_axes must be a non-empty object")
    allowed_axes = set(axes)

    ci = ledger.get("ci_receipts")
    if not isinstance(ci, list) or not ci:
        raise ValueError("ci_receipts must be non-empty")
    for idx, item in enumerate(ci):
        if not isinstance(item, dict):
            raise ValueError(f"ci_receipts[{idx}] must be an object")
        if item.get("state") != "VERIFIED_CI_SUCCESS":
            raise ValueError(f"ci_receipts[{idx}] is not VERIFIED_CI_SUCCESS")
        digest = item.get("artifact_sha256")
        if not isinstance(digest, str) or len(digest) != 64:
            raise ValueError(f"ci_receipts[{idx}] requires a SHA-256 digest")

    files = ledger.get("file_states")
    if not isinstance(files, list) or not files:
        raise ValueError("file_states must be non-empty")
    seen_paths: set[str] = set()
    for idx, item in enumerate(files):
        if not isinstance(item, dict):
            raise ValueError(f"file_states[{idx}] must be an object")
        path = item.get("path")
        if not isinstance(path, str) or not path:
            raise ValueError(f"file_states[{idx}] requires path")
        if path in seen_paths:
            raise ValueError(f"duplicate file state: {path}")
        seen_paths.add(path)
        item_axes = item.get("variance_axes")
        if not isinstance(item_axes, list) or not item_axes:
            raise ValueError(f"{path}: variance_axes must be non-empty")
        unknown = sorted(set(item_axes) - allowed_axes)
        if unknown:
            raise ValueError(f"{path}: unknown variance axes {unknown}")
        if not isinstance(item.get("next"), str) or not item["next"].strip():
            raise ValueError(f"{path}: next action is required")

    papers = ledger.get("paper_adjustments")
    if not isinstance(papers, list) or not papers:
        raise ValueError("paper_adjustments must be non-empty")
    seen_papers: set[str] = set()
    for idx, item in enumerate(papers):
        if not isinstance(item, dict):
            raise ValueError(f"paper_adjustments[{idx}] must be an object")
        paper_id = item.get("id")
        if not isinstance(paper_id, str) or not paper_id:
            raise ValueError(f"paper_adjustments[{idx}] requires id")
        if paper_id in seen_papers:
            raise ValueError(f"duplicate paper id: {paper_id}")
        seen_papers.add(paper_id)
        priority = item.get("priority")
        if priority not in PRIORITY_ORDER:
            raise ValueError(f"{paper_id}: unsupported priority {priority!r}")
        _require_token(item.get("token_vazio"), location=paper_id)
        item_axes = item.get("variance_impact")
        if not isinstance(item_axes, list) or not item_axes:
            raise ValueError(f"{paper_id}: variance_impact must be non-empty")
        unknown = sorted(set(item_axes) - allowed_axes)
        if unknown:
            raise ValueError(f"{paper_id}: unknown variance axes {unknown}")
        adjustments = item.get("required_adjustments")
        if not isinstance(adjustments, list) or not adjustments or not all(
            isinstance(value, str) and value.strip() for value in adjustments
        ):
            raise ValueError(f"{paper_id}: required_adjustments must be non-empty strings")

    queue = ledger.get("urgency_queue")
    if not isinstance(queue, list) or not queue:
        raise ValueError("urgency_queue must be non-empty")
    expected_ranks = list(range(1, len(queue) + 1))
    ranks = [item.get("rank") for item in queue if isinstance(item, dict)]
    if ranks != expected_ranks:
        raise ValueError(f"urgency queue ranks must be contiguous: expected {expected_ranks}, got {ranks}")
    previous_score = 101
    previous_priority = -1
    seen_queue: set[str] = set()
    for idx, item in enumerate(queue):
        queue_id = item.get("id")
        if not isinstance(queue_id, str) or not queue_id:
            raise ValueError(f"urgency_queue[{idx}] requires id")
        if queue_id in seen_queue:
            raise ValueError(f"duplicate urgency id: {queue_id}")
        seen_queue.add(queue_id)
        priority = item.get("priority")
        if priority not in PRIORITY_ORDER:
            raise ValueError(f"{queue_id}: invalid priority")
        priority_value = PRIORITY_ORDER[priority]
        if priority_value < previous_priority:
            raise ValueError("urgency queue cannot return to a higher priority after a lower one")
        previous_priority = priority_value
        score = item.get("urgency_score")
        if not isinstance(score, int) or not 0 <= score <= 100:
            raise ValueError(f"{queue_id}: urgency_score must be integer 0..100")
        if score > previous_score:
            raise ValueError("urgency_score must be non-increasing")
        previous_score = score
        _require_token(item.get("token_vazio"), location=queue_id)
        if not isinstance(item.get("reason"), str) or not item["reason"].strip():
            raise ValueError(f"{queue_id}: reason is required")
        if not isinstance(item.get("next_test"), str) or not item["next_test"].strip():
            raise ValueError(f"{queue_id}: next_test is required")


def build_receipt(ledger: dict[str, Any]) -> dict[str, Any]:
    validate_ledger(ledger)
    files = ledger["file_states"]
    papers = ledger["paper_adjustments"]
    queue = ledger["urgency_queue"]

    variance_axis_counts: Counter[str] = Counter()
    for item in files:
        variance_axis_counts.update(item["variance_axes"])
    for item in papers:
        variance_axis_counts.update(item["variance_impact"])

    stale = [item["path"] for item in files if "STALE" in item.get("attention", "") or "SUPERSEDED" in item.get("state", "")]
    urgent_files = [item["path"] for item in files if item.get("attention") == "URGENT"]
    p0 = [item for item in queue if item["priority"] == "P0"]
    p1 = [item for item in queue if item["priority"] == "P1"]
    p2 = [item for item in queue if item["priority"] == "P2"]
    tokens = sorted({item["token_vazio"] for item in queue} | {item["token_vazio"] for item in papers})

    return {
        "schema": RECEIPT_SCHEMA,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "state": "VERIFIED_LEDGER_CONTRACT_BLOCKED_SCIENTIFIC_TOKEN_VAZIO",
        "claim_allowed": False,
        "publication_ready": False,
        "automatic_promotion_forbidden": True,
        "source_pr": ledger.get("source_pr"),
        "source_head_sha_declared": ledger.get("source_head_sha"),
        "ci_receipt_count": len(ledger["ci_receipts"]),
        "all_declared_ci_receipts_success": True,
        "file_count": len(files),
        "paper_count": len(papers),
        "queue_count": len(queue),
        "stale_or_superseded_files": stale,
        "urgent_files": urgent_files,
        "variance_axis_counts": dict(sorted(variance_axis_counts.items())),
        "priority_counts": {"P0": len(p0), "P1": len(p1), "P2": len(p2)},
        "token_vazio": tokens,
        "next_action": p0[0]["id"] if p0 else (p1[0]["id"] if p1 else (p2[0]["id"] if p2 else "HUMAN_REVIEW")),
        "next_test": p0[0]["next_test"] if p0 else (p1[0]["next_test"] if p1 else (p2[0]["next_test"] if p2 else "Independent human review")),
        "scientific_gate": "BLOCKED_P0_TOKEN_VAZIO" if p0 else ("P0_READY_P1_BLOCKED" if p1 else "READY_FOR_INDEPENDENT_HUMAN_REVIEW"),
        "triage_note": "urgency_score is operational triage only; it is not scientific significance, probability, evidence or posterior weight",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    root = args.repo_root.resolve()
    ledger_path = args.ledger if args.ledger.is_absolute() else root / args.ledger
    ledger = load_json(ledger_path)
    receipt = build_receipt(ledger)
    receipt.update(
        {
            "repository": ledger.get("repository"),
            "source_git_sha": git_sha(root),
            "ledger_path": str(ledger_path.relative_to(root)),
            "ledger_sha256": sha256_file(ledger_path),
        }
    )

    output = args.output if args.output.is_absolute() else root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True))
    return 3 if receipt["scientific_gate"].startswith("BLOCKED") else 0


if __name__ == "__main__":
    raise SystemExit(main())
