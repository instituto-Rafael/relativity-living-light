#!/usr/bin/env python3
"""Fail-closed path validator for the public RLL mirror."""
from __future__ import annotations

import argparse
import fnmatch
import json
import subprocess
import sys
from pathlib import Path
from typing import Iterable


def load_policy(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("claim_allowed") is not False:
        raise ValueError("publication policy must preserve claim_allowed=false")
    if not isinstance(payload.get("deny_globs"), list) or not payload["deny_globs"]:
        raise ValueError("publication policy requires deny_globs")
    return payload


def tracked_paths(root: Path) -> list[str]:
    proc = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return [item.decode("utf-8") for item in proc.stdout.split(b"\0") if item]


def denied_matches(paths: Iterable[str], patterns: Iterable[str]) -> list[dict[str, str]]:
    blocked: list[dict[str, str]] = []
    for path in paths:
        normalized = path.replace("\\", "/")
        for pattern in patterns:
            simple = pattern.replace("**/", "*")
            if fnmatch.fnmatch(normalized, pattern) or fnmatch.fnmatch(normalized, simple):
                blocked.append({"path": normalized, "pattern": pattern})
                break
    return blocked


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument(
        "--policy",
        type=Path,
        default=Path("data/governance/rll_publication_boundary_v1.json"),
    )
    parser.add_argument("--paths-from", type=Path)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()

    try:
        policy = load_policy(args.policy)
        if args.paths_from:
            paths = [line.strip() for line in args.paths_from.read_text().splitlines() if line.strip()]
        else:
            paths = tracked_paths(args.root)
        blocked = denied_matches(paths, policy["deny_globs"])
    except (OSError, ValueError, subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        print(f"BLOCKED_VALIDATOR: {exc}", file=sys.stderr)
        return 2

    receipt = {
        "schema": "rll.publication_boundary.receipt.v1",
        "checked_paths": len(paths),
        "blocked": blocked,
        "status": "PASS" if not blocked else "BLOCKED",
        "claim_allowed": False,
    }
    if args.receipt:
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if not blocked else 3


if __name__ == "__main__":
    raise SystemExit(main())
