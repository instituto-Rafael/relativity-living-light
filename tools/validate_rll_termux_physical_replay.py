#!/usr/bin/env python3
"""Validate a physical Termux replay capsule without promoting scientific claims."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

EXPECTED_PANTHEON_SHA = "c7b192cfa624dde19d5628781e120ba60d8628c792f3d7037e43c1092094f7e6"
EXPECTED_BAYES_SHA = "6f5e11105d8cdd23586bd9b36238f705bf198f01f8dd662b34ea51cd29127078"
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
CHECKSUM_LINE_RE = re.compile(r"^([0-9a-f]{64})  ([A-Za-z0-9._-]+)$")
REQUIRED_FILES = {
    "TERMUX_RECEIPT.json",
    "replay-1.json",
    "replay-2.json",
    "RUN.log",
}


class PhysicalReplayError(ValueError):
    """Raised when a physical replay capsule is incomplete or inconsistent."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PhysicalReplayError(f"invalid JSON {path.name}: {exc}") from exc
    if not isinstance(payload, dict):
        raise PhysicalReplayError(f"{path.name}: root must be an object")
    return payload


def require_nonempty_string(payload: dict[str, Any], key: str, scope: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise PhysicalReplayError(f"{scope}.{key} must be a non-empty string")
    return value


def validate_checksums(root: Path) -> dict[str, str]:
    path = root / "CHECKSUMS.sha256"
    if not path.is_file():
        raise PhysicalReplayError("CHECKSUMS.sha256 is missing")

    observed: dict[str, str] = {}
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        match = CHECKSUM_LINE_RE.fullmatch(raw)
        if not match:
            raise PhysicalReplayError(f"invalid checksum line {line_number}")
        digest, name = match.groups()
        if name in observed:
            raise PhysicalReplayError(f"duplicate checksum entry: {name}")
        if name not in REQUIRED_FILES:
            raise PhysicalReplayError(f"unexpected checksum entry: {name}")
        observed[name] = digest

    if set(observed) != REQUIRED_FILES:
        missing = sorted(REQUIRED_FILES - set(observed))
        raise PhysicalReplayError(f"missing checksum entries: {missing}")

    for name, expected in observed.items():
        file_path = root / name
        if not file_path.is_file():
            raise PhysicalReplayError(f"checksummed file is missing: {name}")
        actual = sha256_bytes(file_path.read_bytes())
        if actual != expected:
            raise PhysicalReplayError(f"checksum mismatch for {name}: {actual} != {expected}")
    return observed


def validate_reconciliation(payload: dict[str, Any], name: str) -> None:
    if payload.get("schema") != "rll.evidence_reconciliation.v1":
        raise PhysicalReplayError(f"{name}: unsupported replay schema")
    if payload.get("claim_allowed") is not False:
        raise PhysicalReplayError(f"{name}: claim_allowed must remain false")
    canonical = payload.get("canonical_run")
    if not isinstance(canonical, dict):
        raise PhysicalReplayError(f"{name}: canonical_run is missing")
    if canonical.get("run_id") != 31066012098:
        raise PhysicalReplayError(f"{name}: canonical run_id mismatch")
    if canonical.get("source_head_sha") != "3191a1d289db28b09b155b4b9eba62a32ad90005":
        raise PhysicalReplayError(f"{name}: source_head_sha mismatch")
    if canonical.get("result_commit") != "cfcd8b4915fef664486bc0d93ee2a2bb6d84ec65":
        raise PhysicalReplayError(f"{name}: result_commit mismatch")


def validate_receipt(receipt: dict[str, Any], checksums: dict[str, str]) -> None:
    if receipt.get("schema") != "rll.termux_physical_replay_receipt.v1":
        raise PhysicalReplayError("unsupported receipt schema")
    if receipt.get("repository") != "instituto-Rafael/relativity-living-light":
        raise PhysicalReplayError("repository mismatch")
    if receipt.get("claim_allowed") is not False:
        raise PhysicalReplayError("claim_allowed must remain false")
    if receipt.get("supersedes_queue_item") != "RLL-P0-TERMUX-PHYSICAL-REPLAY":
        raise PhysicalReplayError("queue target mismatch")
    if receipt.get("evidence_class") != "E":
        raise PhysicalReplayError("physical receipt must use evidence class E")
    if receipt.get("state") != "PASS_PHYSICAL_TERMUX_REPLAY":
        raise PhysicalReplayError("physical receipt state mismatch")
    if receipt.get("next_gate") != "RLL-P0-PANTHEON-SUCCESSOR-RUN":
        raise PhysicalReplayError("next gate mismatch")
    require_nonempty_string(receipt, "generated_at", "receipt")

    promotion = receipt.get("promotion")
    expected_promotion = {
        "from": {
            "evidence_class": "P",
            "state": "TOKEN_VAZIO_PHYSICAL_EXECUTION",
        },
        "to": {
            "evidence_class": "E",
            "state": "PASS_PHYSICAL_TERMUX_REPLAY",
        },
    }
    if promotion != expected_promotion:
        raise PhysicalReplayError("promotion boundary mismatch")

    git = receipt.get("git")
    if not isinstance(git, dict) or not COMMIT_RE.fullmatch(str(git.get("code_commit", ""))):
        raise PhysicalReplayError("git.code_commit must be a lowercase 40-char SHA")

    runtime = receipt.get("runtime")
    if not isinstance(runtime, dict):
        raise PhysicalReplayError("runtime must be an object")
    for key in ("uname", "android_release", "device_model", "python"):
        require_nonempty_string(runtime, key, "runtime")
    if "Android" not in str(runtime["uname"]):
        raise PhysicalReplayError("runtime.uname does not identify an Android kernel")

    inputs = receipt.get("inputs")
    if not isinstance(inputs, dict):
        raise PhysicalReplayError("inputs must be an object")
    if inputs.get("pantheon_zip_sha256") != EXPECTED_PANTHEON_SHA:
        raise PhysicalReplayError("Pantheon input SHA mismatch")
    if inputs.get("bayes_zip_sha256") != EXPECTED_BAYES_SHA:
        raise PhysicalReplayError("Bayes input SHA mismatch")
    for key in ("pantheon_zip_size_bytes", "bayes_zip_size_bytes"):
        value = inputs.get(key)
        if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
            raise PhysicalReplayError(f"inputs.{key} must be a positive integer")

    output = receipt.get("output")
    if not isinstance(output, dict):
        raise PhysicalReplayError("output must be an object")
    if output.get("repeat_byte_identical") is not True:
        raise PhysicalReplayError("repeat_byte_identical must be true")
    replay_sha = output.get("replay_sha256")
    log_sha = output.get("run_log_sha256")
    if not isinstance(replay_sha, str) or not SHA_RE.fullmatch(replay_sha):
        raise PhysicalReplayError("output.replay_sha256 is invalid")
    if not isinstance(log_sha, str) or not SHA_RE.fullmatch(log_sha):
        raise PhysicalReplayError("output.run_log_sha256 is invalid")
    if replay_sha != checksums["replay-1.json"] or replay_sha != checksums["replay-2.json"]:
        raise PhysicalReplayError("receipt replay SHA does not match both replay files")
    if log_sha != checksums["RUN.log"]:
        raise PhysicalReplayError("receipt log SHA does not match RUN.log")


def validate_directory(root: Path) -> dict[str, Any]:
    root = root.resolve()
    if not root.is_dir():
        raise PhysicalReplayError(f"not a directory: {root}")

    checksums = validate_checksums(root)
    receipt = load_json(root / "TERMUX_RECEIPT.json")
    replay_1_bytes = (root / "replay-1.json").read_bytes()
    replay_2_bytes = (root / "replay-2.json").read_bytes()
    if replay_1_bytes != replay_2_bytes:
        raise PhysicalReplayError("replay outputs are not byte-identical")

    replay_1 = load_json(root / "replay-1.json")
    replay_2 = load_json(root / "replay-2.json")
    validate_reconciliation(replay_1, "replay-1.json")
    validate_reconciliation(replay_2, "replay-2.json")
    validate_receipt(receipt, checksums)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    try:
        receipt = validate_directory(args.directory)
    except PhysicalReplayError as exc:
        print(f"BLOCKED: {exc}")
        return 1
    print(
        "PASS: physical Termux replay capsule validated; "
        f"commit={receipt['git']['code_commit']} "
        f"next={receipt['next_gate']} claim_allowed=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
