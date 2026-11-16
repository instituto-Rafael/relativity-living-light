#!/usr/bin/env python3
"""Read-only, fail-closed JSON/JSONL dedup audit of a Git commit.

No files are deleted, moved, or opened from the working tree. Git blobs are
materialized in memory with a configurable size guard. Pure stdlib, no network,
no Supabase credentials. Output is a metadata-only receipt. Whole-array order,
JSON scalar types, source paths and distinct file OIDs remain significant.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

SUFFIXES = (".json", ".jsonl", ".ndjson", ".jsonl.txt")
SCHEMA = "rll.git.json_dedup.audit.v1"


def _git(repo: Path, *args: str) -> bytes:
    completed = subprocess.run(
        ["git", "-C", str(repo), "--no-optional-locks", *args],
        check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        timeout=60,
    )
    return completed.stdout


def _reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict:
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError("DUPLICATE_JSON_KEY")
        obj[key] = value
    return obj


def _reject_nonfinite(s: str):
    raise ValueError("NON_FINITE_JSON_NUMBER:" + s)


def _parse_json(data: bytes, jsonlines: bool) -> tuple[str, list[str], int]:
    """Return canonical digest, record-level digests, and record count.

    A malformed JSONL line is a failure for the *whole file*; empty lines are
    deliberately ignored, while zero-record files are never canonicalized.
    """
    text = data.decode("utf-8-sig", errors="strict")
    def load(span: str):
        return json.loads(span, object_pairs_hook=_reject_duplicate_keys,
                          parse_constant=_reject_nonfinite)
    if jsonlines:
        spans = [s for s in text.splitlines() if s.strip()]
        if not spans:
            raise ValueError("EMPTY_JSONL_NO_RECORDS")
        content = [load(s) for s in spans]
    else:
        content = load(text)
    canonical = json.dumps(content, ensure_ascii=False, sort_keys=True,
                           separators=(",", ":"), allow_nan=False).encode("utf-8")
    digest = hashlib.sha256(canonical).hexdigest()
    records = content if isinstance(content, list) else [content]
    record_hashes = [hashlib.sha256(json.dumps(
        record, ensure_ascii=False, sort_keys=True,
        separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()
        for record in records]
    return digest, record_hashes, len(records)


def _groups(index: dict[str, list[str]], *, min_size: int = 2) -> list[dict]:
    return [{"digest": digest, "paths": sorted(paths), "count": len(paths)}
            for digest, paths in sorted(index.items()) if len(paths) >= min_size]


def inspect_repository(repo: Path, rev: str, max_file_bytes: int = 16 * 1024 * 1024) -> dict:
    if max_file_bytes < 1:
        raise ValueError("max_file_bytes must be positive")
    commit = _git(repo, "rev-parse", "--verify", "--end-of-options", rev + "^{commit}").decode().strip()
    tree = _git(repo, "ls-tree", "-r", "-z", "--full-tree", commit)
    items: list[tuple[str, str]] = []
    symlink_count = 0
    for item in tree.split(b"\0"):
        if not item:
            continue
        meta, path = item.split(b"\t", 1)
        mode, kind, oid = meta.decode("ascii").split(" ")
        filename = path.decode("utf-8", errors="surrogateescape")
        if not filename.lower().endswith(SUFFIXES):
            continue
        if kind != "blob" or mode == "120000":
            symlink_count += 1
            continue
        items.append((filename, oid))
    exact_oid: dict[str, list[str]] = defaultdict(list)
    for name, oid in items:
        exact_oid[oid].append(name)

    cache: dict[tuple[str, bool], tuple[int, str | None, str | None, int | None, list[str] | None, str | None]] = {}
    canonical: dict[str, list[str]] = defaultdict(list)
    record_index: dict[str, set[str]] = defaultdict(set)
    receipts: list[dict] = []
    failures: list[dict] = []
    size_skipped = 0
    parsed_files = 0
    for name, oid in sorted(items):
        jsonl = name.lower().endswith((".jsonl", ".ndjson", ".jsonl.txt"))
        cache_key = (oid, jsonl)
        if cache_key not in cache:
            byte_count = int(_git(repo, "cat-file", "-s", oid))
            if byte_count > max_file_bytes:
                cache[cache_key] = (byte_count, None, None, None, None, "SIZE_LIMIT")
            else:
                data = _git(repo, "cat-file", "blob", oid)
                if len(data) != byte_count:
                    raise ValueError("GIT_BLOB_SIZE_MISMATCH")
                raw = hashlib.sha256(data).hexdigest()
                try:
                    cd, rh, count = _parse_json(data, jsonl)
                    cache[cache_key] = (byte_count, raw, cd, count, rh, None)
                except (ValueError, UnicodeError, RecursionError, TypeError) as e:
                    cache[cache_key] = (byte_count, raw, None, None, None, type(e).__name__)
        byte_count, raw, cd, count, record_hashes, error_type = cache[cache_key]
        status = "PARSED" if cd else ("SIZE_LIMIT" if raw is None else "PARSE_FAILED")
        if status == "PARSE_FAILED":
            failures.append({"path": name, "status": "PARSE_FAILED", "reason": error_type})
        if status == "SIZE_LIMIT":
            size_skipped += 1
        if status == "PARSED":
            parsed_files += 1
            canonical[cd].append(name)
            for rh in record_hashes:
                record_index[rh].add(name)
        receipts.append({"path": name, "git_blob_oid": oid, "size_bytes": byte_count,
                         "raw_sha256": raw, "canonical_json_sha256": cd,
                         "record_count": count, "state": status})

    canonical_candidates = []
    oid_by_path = dict(items)
    for group in _groups(canonical):
        if len({oid_by_path[p] for p in group["paths"]}) > 1:
            canonical_candidates.append({**group, "relation": "CANONICAL_JSON_EQUAL_NOT_RAW_EQUAL"})
    record_candidates = [{"record_sha256": key, "source_paths": sorted(paths),
                          "source_file_count": len(paths)}
                         for key, paths in sorted(record_index.items()) if len(paths) > 1]
    return {
        "schema": SCHEMA,
        "source": {"repository_commit": commit, "scope": "TRACKED_COMMITTED_BLOBS_ONLY",
                   "git_tree_sha": _git(repo, "rev-parse", commit + "^{tree}").decode().strip()},
        "options": {"max_file_bytes": max_file_bytes, "no_network": True,
                    "mutate_sources": False},
        "counts": {"json_like_paths": len(items), "unique_git_blob_oids": len(exact_oid),
                   "exact_git_blob_duplicate_groups": sum(len(v)>1 for v in exact_oid.values()),
                   "extra_paths_sharing_git_blob": len(items) - len(exact_oid),
                   "parsed_files": parsed_files, "size_limit_files": size_skipped,
                   "parse_failed_unique_blobs": len({oid_by_path[x["path"]] for x in failures}),
                   "symlink_skipped": symlink_count,
                   "canonical_different_oid_equal_groups": len(canonical_candidates),
                   "cross_file_record_equal_groups": len(record_candidates)},
        "exact_git_blob_groups": _groups(exact_oid),
        "canonical_only_groups": canonical_candidates,
        "cross_file_record_groups": record_candidates,
        "file_receipts": receipts,
        "parse_failures": failures,
        "boundary": {"claim_allowed": False, "content_exported": False,
                     "metadata_only": True, "global_drive_corpus_complete": False,
                     "scientific_validation": "NOT_RUN",
                     "semantic_near_duplicates": "NOT_TESTED",
                     "candidate_not_deletion_authority": True},
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path("."))
    parser.add_argument("--rev", default="HEAD")
    parser.add_argument("--max-file-bytes", type=int, default=16 * 1024 * 1024)
    parser.add_argument("--output", type=Path, help="Create new receipt; refuse overwrites")
    args = parser.parse_args(argv)
    try:
        result = inspect_repository(args.repo, args.rev, args.max_file_bytes)
        payload = json.dumps(result, sort_keys=True, ensure_ascii=True,
                             indent=2, allow_nan=False) + "\n"
        if args.output:
            with args.output.open("x", encoding="utf-8") as f:
                f.write(payload)
        else:
            sys.stdout.write(payload)
        return 0
    except (OSError, ValueError, subprocess.SubprocessError, UnicodeError) as exc:
        print("BLOCKED: " + type(exc).__name__ + ": " + str(exc)[:160], file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
