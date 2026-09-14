#!/usr/bin/env python3
"""Validate repository JSON Schema contracts without mutating scientific data."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jsonschema.validators import validator_for

ROOT = Path(__file__).resolve().parents[1]
SCAN_ROOTS = (
    ROOT / "schemas",
    ROOT / "docs" / "contracts",
    ROOT / "data" / "schemas",
)
OUTPUT = ROOT / "artifacts" / "schema-contracts" / "validation.json"
BOUNDARY_VALIDATOR = ROOT / "tools" / "validate_schemas_claim_boundary.py"


def schema_files() -> list[Path]:
    found: set[Path] = set()
    for root in SCAN_ROOTS:
        if not root.exists():
            continue
        found.update(root.rglob("*.schema.json"))
        if root.name == "schemas":
            found.update(root.glob("*.json"))
    return sorted(path for path in found if path.is_file())


def validate_schema(path: Path) -> dict[str, Any]:
    record: dict[str, Any] = {
        "path": path.relative_to(ROOT).as_posix(),
        "status": "OK",
        "draft": None,
        "error": None,
    }
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise TypeError("schema root must be a JSON object")
        validator_cls = validator_for(payload)
        validator_cls.check_schema(payload)
        record["draft"] = payload.get("$schema", validator_cls.META_SCHEMA.get("$id"))
    except Exception as exc:
        record["status"] = "FAIL"
        record["error"] = f"{type(exc).__name__}: {exc}"
    return record


def run_boundary_validator() -> dict[str, Any]:
    if not BOUNDARY_VALIDATOR.exists():
        return {
            "status": "TOKEN_VAZIO",
            "path": BOUNDARY_VALIDATOR.relative_to(ROOT).as_posix(),
            "exit_code": None,
            "output": "validator not found",
        }
    process = subprocess.run(
        [sys.executable, str(BOUNDARY_VALIDATOR)],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    return {
        "status": "OK" if process.returncode == 0 else "FAIL",
        "path": BOUNDARY_VALIDATOR.relative_to(ROOT).as_posix(),
        "exit_code": process.returncode,
        "output": process.stdout[-12000:],
    }


def main() -> int:
    files = schema_files()
    records = [validate_schema(path) for path in files]
    boundary = run_boundary_validator()

    failures = [record for record in records if record["status"] == "FAIL"]
    status = "OK"
    if not files or boundary["status"] == "TOKEN_VAZIO":
        status = "TOKEN_VAZIO"
    if failures or boundary["status"] == "FAIL":
        status = "FAIL"

    payload = {
        "schema_version": "rll.schema-contract-validation.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "scan_roots": [root.relative_to(ROOT).as_posix() for root in SCAN_ROOTS],
        "summary": {
            "total": len(records),
            "ok": len(records) - len(failures),
            "fail": len(failures),
        },
        "schemas": records,
        "claim_boundary_validator": boundary,
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(payload["summary"], ensure_ascii=False))
    print(f"boundary={boundary['status']}")
    print(f"artifact={OUTPUT.relative_to(ROOT)}")

    if status == "OK":
        return 0
    if status == "TOKEN_VAZIO":
        return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
