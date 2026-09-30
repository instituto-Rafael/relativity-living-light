#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import time
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path
from typing import Any, Sequence

SCHEMA = "rll.diverged_ref_pr_lineage.v1"


def github_json(url: str, token: str, attempts: int = 3) -> Any:
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "rll-ref-lineage-audit-v1",
    }
    last: Exception | None = None
    for attempt in range(attempts):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as exc:  # network/API failures stay fail-closed
            last = exc
            if attempt + 1 < attempts:
                time.sleep(2 ** attempt)
    raise RuntimeError(f"GitHub API failed after {attempts} attempts: {type(last).__name__}: {last}")


def fetch_closed_prs(repo: str, token: str) -> list[dict[str, Any]]:
    encoded_repo = "/".join(urllib.parse.quote(part, safe="") for part in repo.split("/", 1))
    rows: list[dict[str, Any]] = []
    for page in range(1, 51):
        url = f"https://api.github.com/repos/{encoded_repo}/pulls?state=closed&sort=updated&direction=desc&per_page=100&page={page}"
        batch = github_json(url, token)
        if not isinstance(batch, list):
            raise RuntimeError("unexpected GitHub pulls response")
        rows.extend(batch)
        if len(batch) < 100:
            return rows
    raise RuntimeError("closed PR pagination exceeded 5000 items; explicit policy update required")


def classify(patch_receipt: dict[str, Any], prs: list[dict[str, Any]]) -> dict[str, Any]:
    by_head_sha: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for pr in prs:
        sha = ((pr.get("head") or {}).get("sha"))
        if isinstance(sha, str) and sha:
            by_head_sha[sha].append(pr)

    output_rows: list[dict[str, Any]] = []
    direct_main_absorbed = 0
    merged_non_main = 0
    unique_unresolved = 0
    patch_equivalent = 0
    for row in patch_receipt["rows"]:
        base = {
            "ref": row["ref"],
            "head_sha": row["head_sha"],
            "unique_patch_commit_count": row.get("unique_patch_commit_count", 0),
            "patch_equivalent_commit_count": row.get("patch_equivalent_commit_count", 0),
        }
        if row["state"] == "NO_UNIQUE_PATCH_AFTER_PATCH_EQUIVALENCE":
            base.update({
                "lineage_state": "PATCH_EQUIVALENT_TO_MAIN",
                "semantic_review_required": False,
                "reason": "No unique patch remains after git-cherry patch equivalence."
            })
            patch_equivalent += 1
            output_rows.append(base)
            continue

        exact = [pr for pr in by_head_sha.get(row["head_sha"], []) if pr.get("merged_at")]
        direct = [pr for pr in exact if ((pr.get("base") or {}).get("ref")) == "main"]
        if direct:
            pr = sorted(direct, key=lambda x: x.get("merged_at") or "")[-1]
            base.update({
                "lineage_state": "EXACT_HEAD_MERGED_DIRECT_TO_MAIN",
                "semantic_review_required": False,
                "reason": "GitHub records a merged PR into main whose head SHA exactly equals the frozen branch head. This proves historical absorption of that exact head, but not that every behavior remains unchanged today.",
                "pr": {
                    "number": pr["number"],
                    "title": pr.get("title"),
                    "base": (pr.get("base") or {}).get("ref"),
                    "merged_at": pr.get("merged_at"),
                    "merge_commit_sha": pr.get("merge_commit_sha"),
                },
            })
            direct_main_absorbed += 1
        elif exact:
            pr = sorted(exact, key=lambda x: x.get("merged_at") or "")[-1]
            base.update({
                "lineage_state": "EXACT_HEAD_MERGED_TO_NON_MAIN_REQUIRES_CHAIN_AUDIT",
                "semantic_review_required": True,
                "reason": "Exact head was merged, but not directly into main; promotion-chain absorption must be proven separately.",
                "pr": {
                    "number": pr["number"],
                    "title": pr.get("title"),
                    "base": (pr.get("base") or {}).get("ref"),
                    "merged_at": pr.get("merged_at"),
                    "merge_commit_sha": pr.get("merge_commit_sha"),
                },
            })
            merged_non_main += 1
        else:
            base.update({
                "lineage_state": "UNIQUE_PATCH_NO_EXACT_MERGED_PR_HEAD",
                "semantic_review_required": True,
                "reason": "Unique patches remain and no closed merged PR has an exact matching head SHA in the audited repository metadata."
            })
            unique_unresolved += 1
        output_rows.append(base)

    return {
        "schema": SCHEMA,
        "claim_allowed": False,
        "publication_ready": False,
        "source_patch_receipt": {
            "schema": patch_receipt.get("schema"),
            "cohort_size": patch_receipt["summary"]["cohort_size"],
            "refs_with_unique_patches": patch_receipt["summary"]["refs_with_unique_patches"],
            "refs_without_unique_patch_after_equivalence": patch_receipt["summary"]["refs_without_unique_patch_after_equivalence"],
        },
        "github_pr_inventory": {
            "closed_prs_fetched": len(prs),
            "matching_rule": "merged_at != null AND head.sha == frozen ref head_sha; direct absorption requires base.ref == main"
        },
        "summary": {
            "cohort_size": len(output_rows),
            "patch_equivalent_to_main": patch_equivalent,
            "exact_head_merged_direct_to_main": direct_main_absorbed,
            "exact_head_merged_to_non_main_requires_chain_audit": merged_non_main,
            "unique_patch_no_exact_merged_pr_head": unique_unresolved,
            "remaining_semantic_or_chain_review": merged_non_main + unique_unresolved,
        },
        "rows": output_rows,
        "invariants": [
            "exact merged PR head proves historical PR absorption, not current behavioral identity",
            "squash merges can make git-cherry report individual unique patches even when the exact branch head was merged",
            "non-main merged PRs still require promotion-chain proof",
            "no exact merged PR metadata does not prove a branch is valuable or should be forward-ported",
            "claim_allowed remains false"
        ],
        "F_ok": [
            "Patch-equivalence evidence is combined with exact GitHub PR-head lineage instead of relying on git history topology alone."
        ],
        "F_gap": [
            "Only refs without direct-main exact-head absorption still require semantic or promotion-chain review."
        ],
        "F_next": [
            "For remaining refs, inspect merged non-main promotion chains first; then content-review only refs with no exact merged PR head."
        ]
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--patch-receipt", type=Path, required=True)
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", ""))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    token = os.environ.get("GITHUB_TOKEN", "")
    if not args.repo or not token:
        raise SystemExit("GITHUB_REPOSITORY and GITHUB_TOKEN are required; lineage cannot be guessed")
    patch = json.loads(args.patch_receipt.read_text(encoding="utf-8"))
    prs = fetch_closed_prs(args.repo, token)
    result = classify(patch, prs)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
