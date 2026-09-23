#!/usr/bin/env python3
"""Validate the physical Android/Termux Rx Execution Fabric capsule."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

SHA_RE = re.compile(r"^[0-9a-f]{64}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
CHECKSUM_RE = re.compile(r"^([0-9a-f]{64})  ([A-Za-z0-9._/-]+)$")
DETERMINISTIC_FILES = (
    "execution_plan.json",
    "region_classification.json",
    "selected_formulas.json",
    "rejected_formulas.json",
    "covariance_contract.json",
    "metrics.json",
    "negative_results.json",
    "manifest.json",
)
ROOT_CHECKSUM_FILES = {
    "TERMUX_RECEIPT.json",
    "execution_plan_source.yml",
    "RUN.log",
    "RUN1_DETERMINISTIC.sha256",
    "RUN2_DETERMINISTIC.sha256",
}


class ReplayError(ValueError):
    pass


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_json(path):
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReplayError("invalid JSON %s: %s" % (Path(path).name, exc)) from exc
    if not isinstance(payload, dict):
        raise ReplayError("%s root must be object" % Path(path).name)
    return payload


def parse_checksum_file(path):
    rows = {}
    for number, raw in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        match = CHECKSUM_RE.fullmatch(raw)
        if not match:
            raise ReplayError("invalid checksum line %d in %s" % (number, Path(path).name))
        digest, name = match.groups()
        if name in rows:
            raise ReplayError("duplicate checksum entry: %s" % name)
        rows[name] = digest
    return rows


def validate_directory(root):
    root = Path(root).resolve()
    if not root.is_dir():
        raise ReplayError("not a directory: %s" % root)

    for name in ROOT_CHECKSUM_FILES:
        if not (root / name).is_file():
            raise ReplayError("missing capsule file: %s" % name)
    for run in ("run1", "run2"):
        for name in DETERMINISTIC_FILES + ("receipt.json",):
            if not (root / run / name).is_file():
                raise ReplayError("missing %s/%s" % (run, name))

    root_checksums = parse_checksum_file(root / "CHECKSUMS.sha256")
    if set(root_checksums) != ROOT_CHECKSUM_FILES:
        raise ReplayError("root checksum inventory mismatch")
    for name, expected in root_checksums.items():
        actual = sha256(root / name)
        if actual != expected:
            raise ReplayError("checksum mismatch for %s" % name)

    run1 = parse_checksum_file(root / "RUN1_DETERMINISTIC.sha256")
    run2 = parse_checksum_file(root / "RUN2_DETERMINISTIC.sha256")
    if set(run1) != set(DETERMINISTIC_FILES) or set(run2) != set(DETERMINISTIC_FILES):
        raise ReplayError("deterministic checksum inventory mismatch")
    if run1 != run2:
        raise ReplayError("run1/run2 deterministic checksum lists differ")
    for run_name, rows in (("run1", run1), ("run2", run2)):
        for name, expected in rows.items():
            actual = sha256(root / run_name / name)
            if actual != expected:
                raise ReplayError("checksum mismatch for %s/%s" % (run_name, name))

    receipt = load_json(root / "TERMUX_RECEIPT.json")
    if receipt.get("schema") != "rll.rx.termux_execution_fabric_receipt.v1":
        raise ReplayError("unsupported receipt schema")
    if receipt.get("repository") != "instituto-Rafael/relativity-living-light":
        raise ReplayError("repository mismatch")
    if receipt.get("workstream") != "WS16":
        raise ReplayError("workstream mismatch")
    if receipt.get("state") != "PASS_PHYSICAL_RX_EXECUTION_FABRIC":
        raise ReplayError("physical state mismatch")
    if receipt.get("claim_allowed") is not False:
        raise ReplayError("claim_allowed must remain false")
    if receipt.get("training") is not False or receipt.get("ai_runtime") is not False:
        raise ReplayError("training/ai_runtime boundary mismatch")

    git = receipt.get("git")
    if not isinstance(git, dict) or not COMMIT_RE.fullmatch(str(git.get("code_commit", ""))):
        raise ReplayError("git.code_commit invalid")
    runtime = receipt.get("runtime")
    if not isinstance(runtime, dict):
        raise ReplayError("runtime missing")
    for key in ("uname", "android_release", "device_model", "abi", "python"):
        if not isinstance(runtime.get(key), str) or not runtime[key].strip():
            raise ReplayError("runtime.%s missing" % key)
    if "Android" not in runtime["uname"] and "android" not in runtime["uname"].lower():
        raise ReplayError("runtime.uname does not identify Android")

    execution = receipt.get("execution")
    if not isinstance(execution, dict):
        raise ReplayError("execution missing")
    if execution.get("repeat_deterministic_artifacts_identical") is not True:
        raise ReplayError("deterministic repeat flag must be true")
    if not SHA_RE.fullmatch(str(execution.get("deterministic_manifest_sha256", ""))):
        raise ReplayError("deterministic_manifest_sha256 invalid")
    if execution["deterministic_manifest_sha256"] != sha256(root / "RUN1_DETERMINISTIC.sha256"):
        raise ReplayError("deterministic manifest SHA mismatch")
    if execution.get("plan_sha256") != sha256(root / "execution_plan_source.yml"):
        raise ReplayError("plan SHA mismatch")
    if execution.get("run_log_sha256") != sha256(root / "RUN.log"):
        raise ReplayError("run log SHA mismatch")
    qualified = execution.get("qualified_regimes")
    if not isinstance(qualified, list) or any(not str(x).startswith("REGIME:G") for x in qualified):
        raise ReplayError("qualified REGIME namespace missing")

    run_receipt = load_json(root / "run1" / "receipt.json")
    if run_receipt.get("status") != "PASS":
        raise ReplayError("run1 execution receipt is not PASS")
    if run_receipt.get("claim_allowed") is not False:
        raise ReplayError("run1 claim boundary mismatch")
    if run_receipt.get("physics_contract") != execution.get("physics_contract"):
        raise ReplayError("physics contract mismatch")
    if run_receipt.get("qualified_regimes") != qualified:
        raise ReplayError("qualified regime mismatch")

    return receipt


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    args = parser.parse_args(argv)
    try:
        receipt = validate_directory(args.directory)
    except ReplayError as exc:
        print("BLOCKED:", exc)
        return 1
    print(
        "PASS_PHYSICAL_RX_EXECUTION_FABRIC",
        "commit=" + receipt["git"]["code_commit"],
        "abi=" + receipt["runtime"]["abi"],
        "claim_allowed=false",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
