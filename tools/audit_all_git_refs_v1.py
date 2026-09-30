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

SCHEMA = "rll.all_git_refs_topology_census.v1"
HISTORICAL_DENOMINATOR = 582


def git(*args: str, check: bool = True) -> str:
    proc = subprocess.run(["git", *args], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if check and proc.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed rc={proc.returncode}: {proc.stderr.strip()}")
    return proc.stdout.strip()


def classify_counts(behind: int, ahead: int) -> str:
    if behind == 0 and ahead == 0:
        return "IDENTICAL_TO_BASELINE"
    if ahead == 0 and behind > 0:
        return "ANCESTOR_OF_BASELINE_AHEAD_ZERO"
    if ahead > 0 and behind == 0:
        return "DESCENDANT_OF_BASELINE"
    if ahead > 0 and behind > 0:
        return "DIVERGED_FROM_BASELINE"
    raise ValueError(f"invalid counts behind={behind} ahead={ahead}")


def commit_sha(ref: str) -> str | None:
    proc = subprocess.run(["git", "rev-parse", f"{ref}^{{commit}}"], text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    if proc.returncode != 0:
        return None
    return proc.stdout.strip()


def enumerate_refs() -> list[dict[str, Any]]:
    raw = git("for-each-ref", "--format=%(refname)|%(objectname)|%(objecttype)", "refs/remotes/origin", "refs/tags")
    rows: list[dict[str, Any]] = []
    for line in raw.splitlines():
        if not line.strip():
            continue
        refname, object_sha, object_type = line.split("|", 2)
        if refname == "refs/remotes/origin/HEAD":
            continue
        if refname.startswith("refs/remotes/origin/"):
            kind = "remote_branch"
            short = refname.removeprefix("refs/remotes/origin/")
        elif refname.startswith("refs/tags/"):
            kind = "tag"
            short = refname.removeprefix("refs/tags/")
        else:
            kind = "other"
            short = refname
        rows.append({"ref": refname, "name": short, "kind": kind, "object_sha": object_sha, "object_type": object_type})
    rows.sort(key=lambda row: (row["kind"], row["name"]))
    return rows


def audit(baseline: str) -> dict[str, Any]:
    baseline_sha = commit_sha(baseline)
    if not baseline_sha:
        raise RuntimeError(f"baseline is not a commit: {baseline}")
    refs = enumerate_refs()
    classified: list[dict[str, Any]] = []
    classes = Counter()
    semantic_review = []
    for row in refs:
        sha = commit_sha(row["ref"])
        item = dict(row)
        item["commit_sha"] = sha
        if sha is None:
            item.update({"class": "NON_COMMIT_REF", "ahead": None, "behind": None, "semantic_review_required": False})
        else:
            counts = git("rev-list", "--left-right", "--count", f"{baseline_sha}...{sha}")
            left, right = counts.split()
            behind, ahead = int(left), int(right)
            cls = classify_counts(behind, ahead)
            needs_review = cls in {"DESCENDANT_OF_BASELINE", "DIVERGED_FROM_BASELINE"}
            item.update({"class": cls, "ahead": ahead, "behind": behind, "semantic_review_required": needs_review})
            if needs_review:
                semantic_review.append(item["ref"])
        classes[item["class"]] += 1
        classified.append(item)

    observed = len(classified)
    anonymous = [row for row in classified if not row.get("class")]
    payload = {
        "schema": SCHEMA,
        "claim_allowed": False,
        "publication_ready": False,
        "baseline": {"ref": baseline, "commit_sha": baseline_sha},
        "historical_token": "TOKEN_VAZIO_NOT_YET_CLASSIFIED_ALL_582_REFS",
        "historical_label_denominator": HISTORICAL_DENOMINATOR,
        "current_observed_ref_count": observed,
        "historical_denominator_matches_current": observed == HISTORICAL_DENOMINATOR,
        "topology_classified_count": observed - len(anonymous),
        "anonymous_remainder": len(anonymous),
        "class_counts": dict(sorted(classes.items())),
        "semantic_review_required_count": len(semantic_review),
        "candidate_transition": "REDUCED_CURRENT_REF_TOPOLOGY_COMPLETE" if not anonymous else "OPEN_INTERNAL",
        "successor": "TOKEN_VAZIO_DIVERGED_OR_DESCENDANT_REF_SEMANTIC_REVIEW" if semantic_review else None,
        "invariants": [
            "topological ancestry is not semantic equivalence",
            "ahead commits are not automatically technical progress",
            "squash/merge history can create apparent ahead counts",
            "the observed denominator is measured, never forced to the historical label 582",
            "no ref may disappear from the census because its classification is inconvenient",
        ],
        "refs": classified,
        "F_ok": [
            "Every currently observed remote branch/tag ref is assigned a deterministic topology class relative to the baseline.",
            "The historical denominator 582 is compared against the current observed denominator rather than assumed."
        ],
        "F_gap": [
            "Refs that are descendant or diverged require a narrower semantic/technical review before any promotion decision."
        ] if semantic_review else [],
        "F_next": [
            "Review only descendant/diverged refs for unique technical content; absorbed ahead-zero refs need no code promotion."
        ] if semantic_review else ["No semantic-review successor remains in the current ref census."],
    }
    return payload


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
    parser.add_argument("--baseline", default="refs/remotes/origin/main")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    payload = audit(args.baseline)
    atomic_write(args.output, payload)
    print(json.dumps({k: payload[k] for k in ("current_observed_ref_count", "historical_denominator_matches_current", "topology_classified_count", "anonymous_remainder", "semantic_review_required_count", "candidate_transition")}, sort_keys=True))
    return 0 if payload["anonymous_remainder"] == 0 else 3


if __name__ == "__main__":
    raise SystemExit(main())
