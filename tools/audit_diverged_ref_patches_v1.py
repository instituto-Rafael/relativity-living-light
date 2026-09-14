#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any, Sequence

SCHEMA = "rll.diverged_ref_patch_equivalence.v1"
COHORT_SCHEMA = "rll.diverged_ref_cohort.v1"


def git(*args: str, check: bool = True) -> str:
    proc = subprocess.run(["git", *args], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if check and proc.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed rc={proc.returncode}: {proc.stderr.strip()}")
    return proc.stdout.strip()


def ref_commit(ref: str) -> str | None:
    proc = subprocess.run(["git", "rev-parse", f"{ref}^{{commit}}"], text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    return proc.stdout.strip() if proc.returncode == 0 else None


def changed_files(commit: str) -> list[str]:
    raw = git("diff-tree", "--no-commit-id", "--name-only", "-r", commit)
    return sorted({line.strip() for line in raw.splitlines() if line.strip()})


def file_categories(paths: Sequence[str]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for path in paths:
        top = path.split("/", 1)[0] if "/" in path else "ROOT"
        counts[top] += 1
    return dict(sorted(counts.items()))


def patch_equivalence(baseline: str, ref: str) -> dict[str, Any]:
    sha = ref_commit(ref)
    if sha is None:
        return {
            "ref": ref,
            "state": "MISSING_OR_NON_COMMIT_REF",
            "head_sha": None,
            "unique_patch_commits": [],
            "patch_equivalent_commits": [],
            "semantic_review_required": True,
            "changed_files_unique": [],
            "file_categories_unique": {},
        }

    merge_base = git("merge-base", baseline, ref)
    left_right = git("rev-list", "--left-right", "--count", f"{baseline}...{ref}")
    behind_s, ahead_s = left_right.split()
    cherry = git("cherry", baseline, ref, check=False)
    plus: list[str] = []
    minus: list[str] = []
    unexpected: list[str] = []
    for line in cherry.splitlines():
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) != 2 or parts[0] not in {"+", "-"}:
            unexpected.append(line)
            continue
        (plus if parts[0] == "+" else minus).append(parts[1])
    if unexpected:
        raise RuntimeError(f"unexpected git cherry output for {ref}: {unexpected}")

    files = sorted({path for commit in plus for path in changed_files(commit)})
    state = "UNIQUE_PATCHES_REQUIRE_REVIEW" if plus else "NO_UNIQUE_PATCH_AFTER_PATCH_EQUIVALENCE"
    return {
        "ref": ref,
        "state": state,
        "head_sha": sha,
        "merge_base": merge_base,
        "behind": int(behind_s),
        "ahead": int(ahead_s),
        "unique_patch_commit_count": len(plus),
        "patch_equivalent_commit_count": len(minus),
        "unique_patch_commits": plus,
        "patch_equivalent_commits": minus,
        "semantic_review_required": bool(plus),
        "changed_files_unique": files,
        "changed_file_count_unique": len(files),
        "file_categories_unique": file_categories(files),
    }


def audit(cohort_path: Path, baseline: str) -> dict[str, Any]:
    cohort = json.loads(cohort_path.read_text(encoding="utf-8"))
    if cohort.get("schema") != COHORT_SCHEMA:
        raise ValueError("invalid cohort schema")
    if cohort.get("claim_allowed") is not False:
        raise ValueError("cohort must preserve claim_allowed=false")
    refs = cohort.get("refs")
    if not isinstance(refs, list) or len(refs) != cohort.get("cohort_size"):
        raise ValueError("cohort size mismatch")
    if len(refs) != len(set(refs)):
        raise ValueError("duplicate ref in frozen cohort")

    baseline_sha = ref_commit(baseline)
    if baseline_sha is None:
        raise RuntimeError(f"baseline is not a commit: {baseline}")
    rows = [patch_equivalence(baseline, ref) for ref in refs]
    missing = [row for row in rows if row["state"] == "MISSING_OR_NON_COMMIT_REF"]
    unique = [row for row in rows if row["state"] == "UNIQUE_PATCHES_REQUIRE_REVIEW"]
    absorbed = [row for row in rows if row["state"] == "NO_UNIQUE_PATCH_AFTER_PATCH_EQUIVALENCE"]
    total_unique_commits = sum(row.get("unique_patch_commit_count", 0) for row in rows)
    total_equivalent_commits = sum(row.get("patch_equivalent_commit_count", 0) for row in rows)
    categories: Counter[str] = Counter()
    for row in unique:
        categories.update(row.get("file_categories_unique", {}))

    return {
        "schema": SCHEMA,
        "claim_allowed": False,
        "publication_ready": False,
        "baseline": {"ref": baseline, "commit_sha": baseline_sha},
        "source_cohort": {
            "path": str(cohort_path),
            "source_census_run": cohort["source_census_run"],
            "source_artifact_id": cohort["source_artifact_id"],
            "source_observed_ref_count": cohort["source_observed_ref_count"],
            "cohort_size": len(refs),
        },
        "summary": {
            "cohort_size": len(rows),
            "refs_with_unique_patches": len(unique),
            "refs_without_unique_patch_after_equivalence": len(absorbed),
            "missing_or_non_commit_refs": len(missing),
            "total_unique_patch_commits": total_unique_commits,
            "total_patch_equivalent_commits": total_equivalent_commits,
            "unique_changed_file_categories": dict(sorted(categories.items())),
        },
        "candidate_transition": "REDUCED_PATCH_EQUIVALENCE_COMPLETE" if not missing else "TOKEN_VAZIO_REF_COHORT_NOT_FULLY_RESOLVABLE",
        "successor": "TOKEN_VAZIO_UNIQUE_REF_PATCH_SEMANTIC_VALUE_REVIEW" if unique else None,
        "rows": rows,
        "invariants": [
            "git cherry patch-equivalence is narrower than semantic equivalence",
            "a plus patch is not automatically technical progress",
            "a minus patch is evidence of patch-equivalent content already upstream, not identity of history",
            "merge-only/history differences can remain even when unique patch count is zero",
            "no forward-port is authorized automatically"
        ],
        "F_ok": [
            "Every ref in the frozen diverged cohort was subjected to the same patch-equivalence rule.",
            "Unique-patch and patch-equivalent commits are separated before manual semantic review."
        ],
        "F_gap": [
            "Only refs with unique patches still require semantic/technical-value review."
        ] if unique else [],
        "F_next": [
            "Review only unique-patch refs by changed files, tests, receipts and current-main applicability; do not forward-port based on branch name or ahead count."
        ] if unique else ["No unique-patch ref remains in the frozen cohort."],
    }


def atomic_write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        tmp = Path(handle.name)
        json.dump(payload, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, path)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cohort", type=Path, required=True)
    parser.add_argument("--baseline", default="refs/remotes/origin/main")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    payload = audit(args.cohort, args.baseline)
    atomic_write(args.output, payload)
    print(json.dumps(payload["summary"], sort_keys=True))
    return 0 if payload["summary"]["missing_or_non_commit_refs"] == 0 else 3


if __name__ == "__main__":
    raise SystemExit(main())
