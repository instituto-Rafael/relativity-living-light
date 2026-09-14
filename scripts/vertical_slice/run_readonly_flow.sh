#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <intent_ir.json> [output_dir]" >&2
  exit 2
fi

INTENT_PATH="$1"
OUTPUT_DIR="${2:-$ROOT_DIR/artifacts/vertical_slice}"
mkdir -p "$OUTPUT_DIR"

python3 - "$ROOT_DIR" "$INTENT_PATH" "$OUTPUT_DIR" <<'PY'
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

root = Path(sys.argv[1]).resolve()
intent_path = Path(sys.argv[2]).resolve()
out_dir = Path(sys.argv[3]).resolve()
out_dir.mkdir(parents=True, exist_ok=True)

intent_schema_path = root / "docs" / "contracts" / "intent_ir.schema.json"
plan_schema_path = root / "docs" / "contracts" / "execution_plan.schema.json"
result_schema_path = root / "docs" / "contracts" / "execution_result.schema.json"
capabilities_path = root / "internal" / "governance" / "capabilities.json"
policy_path = root / "internal" / "governance" / "policy.json"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: top-level value must be object")
    return payload


def validate_intent_schema(intent: dict[str, Any], schema: dict[str, Any]) -> None:
    try:
        from jsonschema import Draft202012Validator
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("jsonschema dependency is required") from exc
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(intent), key=lambda e: list(e.path))
    if errors:
        raise ValueError(f"intent_ir invalid: {errors[0].message}")


def classify_gate(intent: dict[str, Any], capabilities: dict[str, Any], policy: dict[str, Any]) -> str:
    precedence = {name: idx for idx, name in enumerate(policy["gate_precedence"])}
    decision = intent.get("execution_gate", "allow")
    allowlist = set(policy["allowlist"])
    cap_map = capabilities["capabilities"]
    for capability in intent.get("requested_capabilities", []):
        if capability not in allowlist:
            return "blocked"
        classification = cap_map.get(capability, {}).get("classification", policy["default_capability_decision"])
        if precedence[classification] < precedence[decision]:
            decision = classification
    return decision


def make_plan(intent: dict[str, Any], gate_decision: str) -> dict[str, Any]:
    return {
        "schema": "rafaelia.execution_plan.v1",
        "plan_id": f"plan-{intent['intent_id']}",
        "intent_id": intent["intent_id"],
        "gate_decision": gate_decision,
        "compiled_commands": [
            {"command": "git", "args": ["status"], "read_only": True},
            {"command": "git", "args": ["diff", "--stat"], "read_only": True},
        ],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def run_compiled_commands(commands: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int, str, str]:
    artifacts: list[dict[str, Any]] = []
    all_stdout: list[str] = []
    all_stderr: list[str] = []
    final_code = 0
    for step in commands:
        proc = subprocess.run(
            [step["command"], *step["args"]],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        out = proc.stdout
        err = proc.stderr
        all_stdout.append(f"$ {step['command']} {' '.join(step['args'])}\n{out}")
        all_stderr.append(f"$ {step['command']} {' '.join(step['args'])}\n{err}")
        artifacts.append(
            {
                "command": step["command"],
                "args": step["args"],
                "exit_code": proc.returncode,
                "stdout_sha256": hashlib.sha256(out.encode("utf-8")).hexdigest(),
                "stderr_sha256": hashlib.sha256(err.encode("utf-8")).hexdigest(),
            }
        )
        if proc.returncode != 0 and final_code == 0:
            final_code = proc.returncode
    return artifacts, final_code, "\n".join(all_stdout), "\n".join(all_stderr)


intent = load_json(intent_path)
intent_schema = load_json(intent_schema_path)
_ = load_json(plan_schema_path)
_ = load_json(result_schema_path)
validate_intent_schema(intent, intent_schema)
capabilities = load_json(capabilities_path)
policy = load_json(policy_path)

started_at = datetime.now(timezone.utc).isoformat()
gate_decision = classify_gate(intent, capabilities, policy)
plan = make_plan(intent, gate_decision)
(out_dir / "execution_plan.json").write_text(json.dumps(plan, indent=2, ensure_ascii=False), encoding="utf-8")

if gate_decision == "blocked":
    ended_at = datetime.now(timezone.utc).isoformat()
    stdout_full = ""
    stderr_full = "governance gate blocked requested_capabilities"
    execution_result = {
        "schema": "rafaelia.execution_result.v1",
        "intent_id": intent["intent_id"],
        "executed_command": "blocked_by_governance",
        "args": [],
        "working_directory": str(root),
        "started_at": started_at,
        "ended_at": ended_at,
        "exit_code": 126,
        "stdout_truncated": "",
        "stderr_truncated": stderr_full,
        "stdout_sha256": hashlib.sha256(stdout_full.encode("utf-8")).hexdigest(),
        "stderr_sha256": hashlib.sha256(stderr_full.encode("utf-8")).hexdigest(),
        "artifacts": [],
        "final_state": "blocked",
        "rollback_available": False,
        "source_chunk_refs": intent.get("evidence_refs", []),
    }
else:
    artifacts, exit_code, stdout_full, stderr_full = run_compiled_commands(plan["compiled_commands"])
    ended_at = datetime.now(timezone.utc).isoformat()
    execution_result = {
        "schema": "rafaelia.execution_result.v1",
        "intent_id": intent["intent_id"],
        "executed_command": "compiled_readonly_plan",
        "args": ["git status", "git diff --stat"],
        "working_directory": str(root),
        "started_at": started_at,
        "ended_at": ended_at,
        "exit_code": exit_code,
        "stdout_truncated": stdout_full[:4096],
        "stderr_truncated": stderr_full[:4096],
        "stdout_sha256": hashlib.sha256(stdout_full.encode("utf-8")).hexdigest(),
        "stderr_sha256": hashlib.sha256(stderr_full.encode("utf-8")).hexdigest(),
        "artifacts": artifacts,
        "final_state": "success" if exit_code == 0 else "failed",
        "rollback_available": False,
        "source_chunk_refs": intent.get("evidence_refs", []),
    }

(out_dir / "execution_result.json").write_text(json.dumps(execution_result, indent=2, ensure_ascii=False), encoding="utf-8")
print((out_dir / "execution_result.json").as_posix())
PY
