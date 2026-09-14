#!/usr/bin/env python3
"""Validate the public mirror of the private Livro Vivo packet chain.

This validator proves only the public mirror contract: ordering, commit formats,
privacy boundaries, public formula bridge presence and explicit CI uncertainty.
It does not read or validate private packet bodies.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MIRROR = ROOT / "data" / "formulas" / "session_packet_public_mirror_20260716.json"
FORMULA_BRIDGE = ROOT / "docs" / "formulas" / "SESSION_CROSS_DOMAIN_FORMULA_BRIDGE_20260716.md"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
SENSITIVE_KEYS = {
    "passphrase",
    "password",
    "private_key",
    "derived_key",
    "ciphertext",
    "raw_private_session",
    "private_formula_body",
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize_text(value: str) -> str:
    """Collapse Markdown wrapping without changing the marker vocabulary."""
    return " ".join(value.split())


def load_mirror(path: Path = MIRROR) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("public mirror must be a JSON object")
    return data


def walk_sensitive_keys(value: Any, path: str = "<root>") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if str(key).lower() in SENSITIVE_KEYS:
                raise ValueError(f"sensitive key exposed at {path}/{key}")
            walk_sensitive_keys(child, f"{path}/{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            walk_sensitive_keys(child, f"{path}/{index}")


def validate_mirror(
    data: dict[str, Any],
    mirror_path: Path = MIRROR,
    formula_bridge: Path = FORMULA_BRIDGE,
) -> dict[str, Any]:
    if data.get("schema") != "rll.session_packet_public_mirror.v1":
        raise ValueError("unexpected public mirror schema")
    if data.get("claim_allowed") is not False:
        raise ValueError("claim_allowed must remain false")

    source = data.get("private_source", {})
    if source.get("visibility") != "private":
        raise ValueError("private source visibility must remain private")
    if source.get("private_content_copied") is not False:
        raise ValueError("private_content_copied must remain false")
    if source.get("content_mode") != "pointer_commit_and_digest_only":
        raise ValueError("private source content mode is not pointer-only")
    if not SHA_RE.fullmatch(str(source.get("base_commit", ""))):
        raise ValueError("invalid private base commit")
    if not SHA_RE.fullmatch(str(source.get("head_commit", ""))):
        raise ValueError("invalid private head commit")

    sequence = data.get("private_commit_sequence", [])
    if len(sequence) < 2:
        raise ValueError("private commit sequence is incomplete")
    orders = [entry.get("order") for entry in sequence]
    if orders != list(range(1, len(sequence) + 1)):
        raise ValueError("private commit sequence order is not contiguous")

    commits: set[str] = set()
    commit_path_pairs: set[tuple[str, str]] = set()
    path_occurrences: dict[str, int] = {}
    for entry in sequence:
        commit = str(entry.get("commit", ""))
        path = str(entry.get("path", ""))
        role = str(entry.get("role", ""))
        if not SHA_RE.fullmatch(commit):
            raise ValueError(f"invalid commit SHA: {commit}")
        if commit in commits:
            raise ValueError(f"duplicate commit SHA: {commit}")
        commits.add(commit)
        if not path or path.startswith("/") or ".." in Path(path).parts:
            raise ValueError(f"unsafe or empty private path: {path}")
        pair = (commit, path)
        if pair in commit_path_pairs:
            raise ValueError(f"duplicate commit/path pair: {commit} {path}")
        commit_path_pairs.add(pair)
        path_occurrences[path] = path_occurrences.get(path, 0) + 1
        if not role.strip():
            raise ValueError(f"empty role for {commit}")

    if sequence[-1]["commit"] != source["head_commit"]:
        raise ValueError("private head commit does not match final sequence entry")

    integrity = data.get("integrity_contract", {})
    if integrity.get("content_digest") != "SHA-256":
        raise ValueError("public mirror must require SHA-256")
    if integrity.get("passphrase_committed") is not False:
        raise ValueError("passphrase_committed must remain false")

    private_ci = data.get("private_ci", {})
    if private_ci.get("validator_execution_proven") is not False:
        raise ValueError("private validator execution must remain unproven")
    if private_ci.get("classification") != "STARTUP_FAILURE_OR_INFRASTRUCTURE_FAILURE":
        raise ValueError("private CI failure classification changed")

    bridge_path = ROOT / data.get("public_formula_bridge", "")
    if bridge_path != formula_bridge or not bridge_path.is_file():
        raise ValueError("public formula bridge is missing or mismatched")
    bridge_text = normalize_text(bridge_path.read_text(encoding="utf-8"))
    required_markers = [
        "PUBLIC_SAFE / CLAIM_GATED / PRIVATE_POINTERS_PRESERVED",
        "Shared mathematical forms do not imply shared physical ontology.",
        "private packet bodies",
        "claim-blocked",
        "SHA256",
    ]
    for marker in required_markers:
        if normalize_text(marker) not in bridge_text:
            raise ValueError(f"formula bridge missing marker: {marker}")

    walk_sensitive_keys(data)

    return {
        "schema": "rll.session_packet_public_mirror.report.v1",
        "valid": True,
        "claim_allowed": False,
        "private_content_copied": False,
        "private_commit_count": len(sequence),
        "private_unique_path_count": len(path_occurrences),
        "private_updated_path_count": sum(count > 1 for count in path_occurrences.values()),
        "private_head_commit": source["head_commit"],
        "private_validator_execution_proven": False,
        "mirror_sha256": sha256_file(mirror_path),
        "formula_bridge_sha256": sha256_file(formula_bridge),
        "next_gate": data["next_gate"],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mirror", type=Path, default=MIRROR)
    parser.add_argument("--formula-bridge", type=Path, default=FORMULA_BRIDGE)
    parser.add_argument("--report", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    data = load_mirror(args.mirror)
    report = validate_mirror(data, args.mirror, args.formula_bridge)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print("OK: public packet mirror is ordered, privacy-gated and claim-blocked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
