#!/usr/bin/env python3
"""Compare the canonical GitHub Actions Rx execution with a physical Termux replay.

This tool consumes already-produced artifacts. It never fabricates a physical
receipt and never infers parity from architecture labels alone.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from tools.validate_rll_execution_fabric_termux_replay import (
    DETERMINISTIC_FILES,
    ReplayError,
    validate_directory,
)

SCHEMA = "rll.rx.actions_termux_execution_fabric_parity.v1"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("%s root must be object" % path)
    return payload


def compare(actions_dir: Path, termux_dir: Path) -> dict[str, Any]:
    actions_dir = Path(actions_dir).resolve()
    termux_dir = Path(termux_dir).resolve()

    try:
        termux_receipt = validate_directory(termux_dir)
    except ReplayError as exc:
        return {
            "schema": SCHEMA,
            "state": "FAIL_INVALID_TERMUX_CAPSULE",
            "errors": [str(exc)],
            "claim_allowed": False,
        }

    actions_receipt_path = actions_dir / "receipt.json"
    if not actions_receipt_path.is_file():
        return {
            "schema": SCHEMA,
            "state": "FAIL_ACTIONS_RECEIPT_MISSING",
            "errors": ["missing actions receipt.json"],
            "claim_allowed": False,
        }
    actions_receipt = load_json(actions_receipt_path)

    errors: list[str] = []
    metadata_checks: dict[str, bool] = {}

    metadata_checks["actions_status_pass"] = actions_receipt.get("status") == "PASS"
    metadata_checks["actions_claim_false"] = actions_receipt.get("claim_allowed") is False

    execution = termux_receipt.get("execution", {})
    pairs = {
        "run_id": (actions_receipt.get("run_id"), execution.get("run_id")),
        "physics_contract": (
            actions_receipt.get("physics_contract"),
            execution.get("physics_contract"),
        ),
        "qualified_regimes": (
            actions_receipt.get("qualified_regimes"),
            execution.get("qualified_regimes"),
        ),
        "dispersion_operator": (
            actions_receipt.get("dispersion_operator"),
            execution.get("dispersion_operator"),
        ),
        "formula_selection_basis": (
            actions_receipt.get("formula_selection_basis"),
            execution.get("formula_selection_basis"),
        ),
    }
    for key, (left, right) in pairs.items():
        metadata_checks[key] = left == right
        if left != right:
            errors.append("%s mismatch: actions=%r termux=%r" % (key, left, right))

    for key in ("actions_status_pass", "actions_claim_false"):
        if not metadata_checks[key]:
            errors.append(key + " failed")

    file_rows = []
    for name in DETERMINISTIC_FILES:
        a = actions_dir / name
        t = termux_dir / "run1" / name
        if not a.is_file() or not t.is_file():
            file_rows.append({
                "file": name,
                "state": "MISSING",
                "actions_present": a.is_file(),
                "termux_present": t.is_file(),
            })
            errors.append("missing deterministic file: " + name)
            continue
        ah = sha256(a)
        th = sha256(t)
        equal = ah == th
        file_rows.append({
            "file": name,
            "state": "MATCH" if equal else "MISMATCH",
            "actions_sha256": ah,
            "termux_sha256": th,
        })
        if not equal:
            errors.append("deterministic mismatch: " + name)

    state = (
        "PASS_ACTIONS_TERMUX_DETERMINISTIC_PARITY"
        if not errors
        else "FAIL_ACTIONS_TERMUX_PARITY"
    )
    return {
        "schema": SCHEMA,
        "state": state,
        "actions_dir": str(actions_dir),
        "termux_dir": str(termux_dir),
        "metadata_checks": metadata_checks,
        "deterministic_files": file_rows,
        "matched_file_count": sum(row.get("state") == "MATCH" for row in file_rows),
        "total_file_count": len(DETERMINISTIC_FILES),
        "errors": errors,
        "physical_execution_proven": termux_receipt.get("state") == "PASS_PHYSICAL_RX_EXECUTION_FABRIC",
        "scientific_confirmation": False,
        "claim_allowed": False,
        "boundary": (
            "PASS proves deterministic cross-runtime parity for the declared Rx engineering plan and "
            "artifact surface. It does not validate the cosmological model, scientific truth, hardware "
            "performance, or independent scientific replication."
        ),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--actions-dir", type=Path, required=True)
    parser.add_argument("--termux-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    payload = compare(args.actions_dir, args.termux_dir)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(json.dumps({
        "state": payload["state"],
        "matched_file_count": payload.get("matched_file_count", 0),
        "total_file_count": payload.get("total_file_count", len(DETERMINISTIC_FILES)),
        "claim_allowed": False,
    }, indent=2))
    return 0 if payload["state"] == "PASS_ACTIONS_TERMUX_DETERMINISTIC_PARITY" else 2


if __name__ == "__main__":
    raise SystemExit(main())
