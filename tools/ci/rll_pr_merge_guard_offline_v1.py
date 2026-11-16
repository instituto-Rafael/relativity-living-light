"""Offline, read-only fail-closed PR merge gate for a *frozen* GitHub snapshot.
This is not a live provider check and never executes a merge, push, rerun or release.
An apparently clean result only means "human review candidate", not merge authority.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

SCHEMA = "rll.git_readonly_merge_triage_snapshot.v1"
_HEX = set("0123456789abcdef")


def _sha40(value):
    return isinstance(value, str) and len(value) == 40 and set(value) <= _HEX


def validate_snapshot(data):
    if not isinstance(data, dict) or data.get("schema") != SCHEMA:
        raise ValueError("SNAPSHOT_SCHEMA_MISMATCH")
    branches = data.get("branch_heads")
    prs = data.get("prs")
    if not isinstance(branches, dict) or not isinstance(prs, list) or not prs:
        raise ValueError("SNAPSHOT_MISSING_REFS_OR_PRS")
    if not _sha40(branches.get("main", {}).get("sha")) or not _sha40(branches.get("rll/lab", {}).get("sha")):
        raise ValueError("CANONICAL_HEAD_UNKNOWN")
    if data.get("claim_allowed") is not False:
        raise ValueError("SCIENTIFIC_CLAIM_BOUNDARY_REQUIRED")
    numbers = [p.get("number") for p in prs]
    if any(not isinstance(n, int) for n in numbers) or len(numbers) != len(set(numbers)):
        raise ValueError("PR_IDENTITY_COLLISION")
    for p in prs:
        if not _sha40(p.get("head_sha")) or not _sha40(p.get("base_sha")):
            raise ValueError("MISSING_EXACT_PR_SHA")
        if not isinstance(p.get("draft"), bool) or not isinstance(p.get("manual_hold"), bool):
            raise ValueError("MISSING_PR_HOLD_STATE")
        if p.get("failed_checks") is not None and not isinstance(p.get("failed_checks"), list):
            raise ValueError("INVALID_CHECKS_TYPE")
    return True


def reasons_for_hold(pr, branch_heads):
    reasons = []
    if pr["draft"]:
        reasons.append("DRAFT")
    if pr["manual_hold"]:
        reasons.append("EXPLICIT_HOLD")
    if pr.get("mergeable_state") != "clean":
        reasons.append("NOT_CLEAN_GITHUB_" + str(pr.get("mergeable_state", "UNKNOWN")).upper())
    if pr.get("failed_checks") is None:
        reasons.append("EXACT_HEAD_CHECKS_UNVERIFIED")
    elif pr["failed_checks"]:
        reasons.append("EXACT_HEAD_CHECKS_FAILURE")
    # Require at least one successful check, complete required-check list, and review.
    # Snapshot is intentionally not such an attestation.
    if pr.get("required_check_suite_attested") is not True:
        reasons.append("REQUIRED_CHECK_SET_NOT_ATTESTED")
    if pr.get("approval_status") != "APPROVED_CURRENT_HEAD":
        reasons.append("REVIEW_APPROVAL_NOT_ATTESTED")
    branch = branch_heads.get(pr["base_ref"])
    if not isinstance(branch, dict) or not _sha40(branch.get("sha")):
        reasons.append("UNKNOWN_OR_NONCANONICAL_BASE")
    elif branch["sha"] != pr["base_sha"]:
        reasons.append("BASE_SHA_STALE")
    if pr.get("dependency_ancestry_verified") is not True:
        reasons.append("DEPENDENCY_ANCESTRY_NOT_VERIFIED")
    if pr.get("regression_evidence_confirmed") is not True:
        reasons.append("REGRESSION_EVIDENCE_MISSING")
    return reasons


def evaluate_snapshot(data):
    validate_snapshot(data)
    results = []
    for pr in data["prs"]:
        reasons = reasons_for_hold(pr, data["branch_heads"])
        results.append({
            "pr": pr["number"],
            "head_sha": pr["head_sha"],
            "base": pr["base_ref"],
            "status": "BLOCKED" if reasons else "HUMAN_REVIEW_ONLY",
            "reasons": reasons,
            "automatic_merge_allowed": False,
        })
    return {
        "schema": "rll.offline_pr_merge_gate_report.v1",
        "source": "FROZEN_PROVIDER_SNAPSHOT",
        "live_head_rechecked": False,
        "snapshot_count": len(results),
        "blocked": sum(x["status"] == "BLOCKED" for x in results),
        "eligible_automatic_merge": 0,
        "claim_allowed": False,
        "results": results,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", required=True, type=Path)
    args = parser.parse_args()
    data = json.loads(args.snapshot.read_text(encoding="utf-8"))
    report = evaluate_snapshot(data)
    print(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
