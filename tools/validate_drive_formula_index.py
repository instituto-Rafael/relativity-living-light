#!/usr/bin/env python3
"""Fail-closed validator for the Drive formula provenance receipt.

This validates indexing/provenance invariants only. It does not validate the
mathematical truth of any formula represented by a hash.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

HEX64 = re.compile(r"^[0-9a-f]{64}$")


def _digest(items: list[str]) -> str:
    payload = "\n".join(sorted(items)) + "\n"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def load_manifest(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def validate_manifest(data: dict) -> list[str]:
    errors: list[str] = []

    if data.get("claim_allowed") is not False:
        errors.append("claim_allowed must remain false")
    if data.get("epistemic_state") not in {"OBSERVED", "OBSERVED_LIMITED"}:
        errors.append("epistemic_state must remain observational")

    counts = data.get("counts", {})
    sources = data.get("source_summary", [])
    missing = data.get("missing_graph_formula_hashes", [])
    digests = data.get("set_digests", {})

    if counts.get("normalized_sources") != len(sources):
        errors.append("normalized_sources count mismatch")
    if sum(s.get("formula_count", -1) for s in sources) != counts.get("formula_references"):
        errors.append("formula_references count mismatch")

    for i, source in enumerate(sources):
        sid = source.get("source_id", "")
        sha = source.get("source_sha256", "")
        count = source.get("formula_count")
        if not sid.startswith("source:"):
            errors.append(f"source[{i}] malformed source_id")
        if not HEX64.fullmatch(sha):
            errors.append(f"source[{i}] malformed source_sha256")
        if not isinstance(count, int) or count < 0:
            errors.append(f"source[{i}] invalid formula_count")

    if len(missing) != counts.get("graph_missing_formula_nodes"):
        errors.append("missing graph formula count mismatch")
    if len(set(missing)) != len(missing):
        errors.append("missing graph formula hashes must be unique")
    if any(not HEX64.fullmatch(h) for h in missing):
        errors.append("missing graph formula list contains malformed hash")
    if _digest(missing) != digests.get("missing_graph_formula_hashes_sha256"):
        errors.append("missing graph formula digest mismatch")

    expected_gap = counts.get("formula_hashes_unique", -1) - counts.get("graph_formula_nodes", -1)
    if expected_gap != counts.get("graph_missing_formula_nodes"):
        errors.append("320-198 style set-count invariant is broken")
    if counts.get("graph_extra_formula_nodes") != 0:
        errors.append("unexpected graph-only formula nodes require review")

    invariants = data.get("invariants", {})
    for key in (
        "hash_identity_preserved",
        "absence_not_promoted_to_formula",
        "graph_missing_means_index_gap_not_formula_absence",
        "formula_hash_does_not_imply_mathematical_validity",
        "hypothesis_tag_does_not_imply_proof",
    ):
        if invariants.get(key) is not True:
            errors.append(f"invariant {key} must be true")

    for source_key in ("normalized", "graph"):
        source = data.get("drive_sources", {}).get(source_key, {})
        if not source.get("file_id"):
            errors.append(f"drive_sources.{source_key}.file_id missing")
        if not HEX64.fullmatch(source.get("sha256_downloaded_bytes", "")):
            errors.append(f"drive_sources.{source_key}.sha256_downloaded_bytes malformed")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "manifest",
        nargs="?",
        default="data/provenance/drive_formula_index_20260808.json",
    )
    args = parser.parse_args()
    data = load_manifest(Path(args.manifest))
    errors = validate_manifest(data)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    c = data["counts"]
    print(
        "PASS "
        f"sources={c['normalized_sources']} refs={c['formula_references']} "
        f"unique={c['formula_hashes_unique']} graph={c['graph_formula_nodes']} "
        f"gap={c['graph_missing_formula_nodes']} claim_allowed=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
