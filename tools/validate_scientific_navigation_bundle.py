#!/usr/bin/env python3
"""Validate one generated RLL scientific-navigation artifact fail-closed."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

OPEN_STATES = {"OPEN", "PARTIALLY_RESOLVED", "PRESERVED"}


class BundleValidationError(RuntimeError):
    """Raised when the generated navigation artifact violates its contract."""


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise BundleValidationError(f"missing JSON file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise BundleValidationError(f"invalid JSON in {path}: {exc}") from exc


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_ledger(path: Path) -> list[dict[str, Any]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError as exc:
        raise BundleValidationError(f"missing ledger: {path}") from exc
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            raise BundleValidationError(
                f"invalid JSONL at {path}:{line_number}: {exc}"
            ) from exc
        if not isinstance(payload, dict):
            raise BundleValidationError(
                f"ledger record at {path}:{line_number} must be an object"
            )
        records.append(payload)
    return records


def read_checksum_ledger(path: Path) -> dict[str, str]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError as exc:
        raise BundleValidationError(f"missing checksum ledger: {path}") from exc
    records: dict[str, str] = {}
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            digest, relative = line.split("  ", 1)
        except ValueError as exc:
            raise BundleValidationError(
                f"invalid checksum line at {path}:{line_number}"
            ) from exc
        if len(digest) != 64 or any(
            char not in "0123456789abcdef" for char in digest
        ):
            raise BundleValidationError(
                f"invalid SHA-256 at {path}:{line_number}: {digest!r}"
            )
        if not relative or relative in records:
            raise BundleValidationError(
                f"empty or duplicate checksum path at {path}:{line_number}: {relative!r}"
            )
        records[relative] = digest
    return records


def flatten_paths(mapping: Any, context: str) -> set[str]:
    if not isinstance(mapping, dict):
        raise BundleValidationError(f"{context} must be an object")
    result: set[str] = set()
    for mechanism_id, paths in mapping.items():
        if not isinstance(mechanism_id, str) or not isinstance(paths, list):
            raise BundleValidationError(f"invalid {context} entry for {mechanism_id!r}")
        for path in paths:
            if not isinstance(path, str) or not path:
                raise BundleValidationError(f"invalid path in {context}.{mechanism_id}")
            result.add(path)
    return result


def validate_bundle(
    root: Path,
    capsule_schema_path: Path,
    token_schema_path: Path,
) -> dict[str, Any]:
    root = root.resolve()
    if not root.is_dir():
        raise BundleValidationError(f"artifact root is not a directory: {root}")

    capsule_schema = read_json(capsule_schema_path.resolve())
    token_schema = read_json(token_schema_path.resolve())
    Draft202012Validator.check_schema(capsule_schema)
    Draft202012Validator.check_schema(token_schema)
    capsule_validator = Draft202012Validator(capsule_schema)
    token_validator = Draft202012Validator(token_schema)

    manifest = read_json(root / "NAVIGATION_MANIFEST.json")
    receipt = read_json(root / "RECEIPT.json")
    workflow_receipt = read_json(root / "WORKFLOW_RECEIPT.json")
    graph = read_json(root / "DEPENDENCY_GRAPH.json")

    for context, payload in (
        ("manifest", manifest),
        ("receipt", receipt),
        ("workflow receipt", workflow_receipt),
    ):
        if payload.get("claim_allowed") is not False:
            raise BundleValidationError(f"{context} violated claim_allowed=false")

    capsules: list[dict[str, Any]] = []
    capsule_paths = sorted(root.glob("capsules/*/CAPSULE.json"))
    if not capsule_paths:
        raise BundleValidationError("no evidence capsules generated")
    for path in capsule_paths:
        payload = read_json(path)
        capsule_validator.validate(payload)
        if payload.get("claim_allowed") is not False:
            raise BundleValidationError(f"claim boundary violated in {path}")
        capsules.append(payload)

    tokens = read_ledger(root / "TOKEN_VAZIO_LEDGER.jsonl")
    token_ids: list[str] = []
    for index, payload in enumerate(tokens, start=1):
        token_validator.validate(payload)
        if payload.get("claim_weight") != 0:
            raise BundleValidationError(
                f"non-zero TOKEN_VAZIO claim weight at ledger record {index}"
            )
        token_ids.append(payload["token_vazio_id"])
    if len(token_ids) != len(set(token_ids)):
        raise BundleValidationError("duplicate token_vazio_id in ledger")

    open_tokens = [item for item in tokens if item.get("state") in OPEN_STATES]
    if manifest.get("mechanism_count") != len(capsules):
        raise BundleValidationError("manifest/capsule count mismatch")
    if manifest.get("open_token_vazio_count") != len(open_tokens):
        raise BundleValidationError("manifest/ledger open TOKEN_VAZIO mismatch")
    capsule_open_count = sum(
        capsule["uncertainties"]["token_vazio_count"] for capsule in capsules
    )
    if capsule_open_count != len(open_tokens):
        raise BundleValidationError("capsule/ledger open TOKEN_VAZIO mismatch")

    missing_registered = flatten_paths(
        manifest.get("missing_required_paths", {}), "missing_required_paths"
    ) | flatten_paths(
        manifest.get("missing_evidence_paths", {}), "missing_evidence_paths"
    )
    token_sources = {
        source
        for item in tokens
        for source in item.get("source_paths", [])
        if isinstance(source, str)
    }
    uncovered = sorted(missing_registered - token_sources)
    if uncovered:
        raise BundleValidationError(
            f"registered missing paths without TOKEN_VAZIO: {uncovered}"
        )

    if graph.get("schema") != "rll.scientific_navigation_graph.v2":
        raise BundleValidationError("dependency graph is not v2")
    nodes = graph.get("nodes")
    edges = graph.get("edges")
    if not isinstance(nodes, list) or not isinstance(edges, list):
        raise BundleValidationError("dependency graph nodes/edges must be arrays")
    node_types = {node.get("type") for node in nodes if isinstance(node, dict)}
    relations = {edge.get("relation") for edge in edges if isinstance(edge, dict)}
    required_node_types = {"mechanism", "artifact", "token_vazio", "claim"}
    required_relations = {
        "has_uncertainty",
        "requires_evidence",
        "declares_claim",
    }
    if not required_node_types.issubset(node_types):
        raise BundleValidationError(
            f"dependency graph node types missing: {sorted(required_node_types - node_types)}"
        )
    if not required_relations.issubset(relations):
        raise BundleValidationError(
            f"dependency graph relations missing: {sorted(required_relations - relations)}"
        )
    if "expected_runtime_artifact" in node_types and "expects_runtime" not in relations:
        raise BundleValidationError("runtime expectation nodes lack expects_runtime edges")

    commit_ids = {
        manifest.get("commit_sha"),
        receipt.get("commit_sha"),
        workflow_receipt.get("commit_sha"),
        *(capsule.get("source", {}).get("commit_sha") for capsule in capsules),
    }
    if None in commit_ids or len(commit_ids) != 1:
        raise BundleValidationError(
            f"commit provenance mismatch: {sorted(map(str, commit_ids))}"
        )

    checksums = read_checksum_ledger(root / "CHECKSUMS.sha256")
    actual_files = {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file() and path.name != "CHECKSUMS.sha256"
    }
    listed_files = set(checksums)
    if listed_files != actual_files:
        raise BundleValidationError(
            "checksum coverage mismatch: "
            f"missing={sorted(actual_files - listed_files)} "
            f"extra={sorted(listed_files - actual_files)}"
        )
    for relative, expected_digest in checksums.items():
        actual_digest = sha256_file(root / relative)
        if actual_digest != expected_digest:
            raise BundleValidationError(
                f"checksum mismatch for {relative}: "
                f"{actual_digest} != {expected_digest}"
            )
    for late_file in ("BUILD.log", "WORKFLOW_RECEIPT.json"):
        if late_file not in checksums:
            raise BundleValidationError(
                f"late workflow file absent from checksum ledger: {late_file}"
            )

    return {
        "status": "PASS",
        "mechanisms": len(capsules),
        "tokens": len(tokens),
        "open_tokens": len(open_tokens),
        "missing_registered_paths": len(missing_registered),
        "graph_nodes": len(nodes),
        "graph_edges": len(edges),
        "checksummed_files": len(checksums),
        "commit_sha": next(iter(commit_ids)),
        "claim_allowed": False,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--capsule-schema", type=Path, required=True)
    parser.add_argument("--token-schema", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        summary = validate_bundle(
            args.root,
            args.capsule_schema,
            args.token_schema,
        )
    except Exception as exc:  # Fail closed on schema and contract errors.
        print(json.dumps({"status": "FAIL", "error": str(exc)}, sort_keys=True))
        return 1
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
