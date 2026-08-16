#!/usr/bin/env python3
"""Produce a read-only, falsifiable branch-divergence inventory.

This tool never merges, rebases, force-updates, or changes refs.  It records the
merge base, left/right-only commit counts, path-level changes on both sides, the
path intersection, domain counts and explicit next actions.  Divergence is an
observed state, not permission to reconcile automatically.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path
from typing import Iterable, Sequence

SCHEMA = "rll.branch_divergence_inventory.v1"


def run_git(args: Sequence[str], root: Path) -> str:
    result = subprocess.run(
        ["git", *args], cwd=root, check=True, capture_output=True, text=True
    )
    return result.stdout.strip()


def parse_left_right_count(text: str) -> tuple[int, int]:
    parts = text.replace("\t", " ").split()
    if len(parts) != 2:
        raise ValueError(f"expected two rev-list counts, got: {text!r}")
    left, right = (int(parts[0]), int(parts[1]))
    if left < 0 or right < 0:
        raise ValueError("rev-list counts cannot be negative")
    return left, right


def parse_name_status(text: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for raw in text.splitlines():
        if not raw.strip():
            continue
        parts = raw.split("\t")
        status = parts[0]
        if status.startswith(("R", "C")) and len(parts) >= 3:
            rows.append({"status": status, "path": parts[2], "previous_path": parts[1]})
        elif len(parts) >= 2:
            rows.append({"status": status, "path": parts[1]})
        else:
            raise ValueError(f"invalid name-status row: {raw!r}")
    return rows


def domain_for(path: str) -> str:
    # Git paths may be expressed as either `.github/...` or `./.github/...`.
    # Do not use lstrip("./"): lstrip removes a *set of characters* and would
    # incorrectly erase the leading dot from `.github`, turning it into
    # `github/...` and silently misclassifying workflow/governance paths.
    p = path.lower()
    if p.startswith("./"):
        p = p[2:]
    if p.startswith(".github/workflows/"):
        return "workflow"
    if p.startswith((".github/", "governance/", "data/governance/")):
        return "governance"
    if p.startswith(("tests/", "test/")):
        return "tests"
    if p.startswith(("tools/", "scripts/", "src/", "analysis/", "models/")):
        return "implementation"
    if p.startswith(("data/", "datasets/", "results/", "validation/")):
        return "data"
    if p.startswith(("docs/", "papers/")) or p.endswith(".md"):
        return "documentation"
    return "other"


def summarize_domains(paths: Iterable[str]) -> dict[str, int]:
    return dict(sorted(Counter(domain_for(path) for path in paths).items()))


def inventory(root: Path, left: str, right: str) -> dict[str, object]:
    left_sha = run_git(["rev-parse", left], root)
    right_sha = run_git(["rev-parse", right], root)
    merge_base = run_git(["merge-base", left, right], root)
    left_count, right_count = parse_left_right_count(
        run_git(["rev-list", "--left-right", "--count", f"{left}...{right}"], root)
    )

    left_rows = parse_name_status(
        run_git(["diff", "--name-status", merge_base, left_sha], root)
    )
    right_rows = parse_name_status(
        run_git(["diff", "--name-status", merge_base, right_sha], root)
    )
    left_paths = sorted({row["path"] for row in left_rows})
    right_paths = sorted({row["path"] for row in right_rows})
    overlap = sorted(set(left_paths) & set(right_paths))

    digest = hashlib.sha256()
    for value in (left, left_sha, right, right_sha, merge_base):
        digest.update(value.encode("utf-8"))
        digest.update(b"\0")
    for path in left_paths:
        digest.update(b"L\0" + path.encode("utf-8") + b"\0")
    for path in right_paths:
        digest.update(b"R\0" + path.encode("utf-8") + b"\0")

    return {
        "schema": SCHEMA,
        "left": {"ref": left, "sha": left_sha, "unique_commits": left_count},
        "right": {"ref": right, "sha": right_sha, "unique_commits": right_count},
        "merge_base": merge_base,
        "status": "IDENTICAL" if left_count == 0 and right_count == 0 else "DIVERGED",
        "left_changes": left_rows,
        "right_changes": right_rows,
        "left_path_count": len(left_paths),
        "right_path_count": len(right_paths),
        "overlap_paths": overlap,
        "overlap_path_count": len(overlap),
        "left_domains": summarize_domains(left_paths),
        "right_domains": summarize_domains(right_paths),
        "inputs_sha256": digest.hexdigest(),
        "decision": "AUDIT_ONLY_NO_MUTATION",
        "history_reconciliation": (
            "NOT_REQUIRED" if left_count == 0 and right_count == 0
            else "TOKEN_VAZIO_HISTORY_RECONCILIATION"
        ),
        "claim_allowed": False,
        "publication_effect": "NONE",
        "auto_merge": False,
        "F_next": [
            "review overlap_paths before any merge or forward-port",
            "partition one-sided paths into minimal reviewed batches",
            "run branch-maturity and repository tests for every batch",
            "bind each accepted batch to a hash-bound receipt",
        ],
    }


def write_products(out: Path, payload: dict[str, object]) -> None:
    out.mkdir(parents=True, exist_ok=True)
    json_path = out / "divergence_snapshot.json"
    json_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    lines = [
        "# Branch Divergence Inventory",
        "",
        f"- left: `{payload['left']['ref']}` @ `{payload['left']['sha']}`",
        f"- right: `{payload['right']['ref']}` @ `{payload['right']['sha']}`",
        f"- merge base: `{payload['merge_base']}`",
        f"- left-only commits: `{payload['left']['unique_commits']}`",
        f"- right-only commits: `{payload['right']['unique_commits']}`",
        f"- left changed paths from merge base: `{payload['left_path_count']}`",
        f"- right changed paths from merge base: `{payload['right_path_count']}`",
        f"- overlapping changed paths: `{payload['overlap_path_count']}`",
        f"- decision: `{payload['decision']}`",
        "- claim_allowed: `false`",
        "",
        "## Overlap requiring review",
        "",
    ]
    overlap = list(payload["overlap_paths"])
    lines.extend([f"- `{path}`" for path in overlap] or ["- `NONE`"])
    lines.extend(["", "## Next", ""])
    lines.extend([f"- {item}" for item in payload["F_next"]])
    (out / "RECONCILIATION_SUMMARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--left", required=True)
    parser.add_argument("--right", required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/branch-divergence"))
    parser.add_argument("--fail-if-diverged", action="store_true")
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        payload = inventory(args.root, args.left, args.right)
    except (subprocess.CalledProcessError, ValueError) as exc:
        print(f"ERROR BRANCH_DIVERGENCE: {exc}")
        return 2
    write_products(args.output_dir, payload)
    print(
        f"branch divergence: {payload['left']['ref']}={payload['left']['unique_commits']} "
        f"{payload['right']['ref']}={payload['right']['unique_commits']} "
        f"overlap={payload['overlap_path_count']} decision={payload['decision']}"
    )
    if args.fail_if_diverged and payload["status"] == "DIVERGED":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
