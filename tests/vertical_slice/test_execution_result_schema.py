from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "vertical_slice" / "run_readonly_flow.sh"
RESULT_SCHEMA = ROOT / "docs" / "contracts" / "execution_result.schema.json"


def _intent() -> dict:
    return {
        "schema": "rafaelia.intent.v1",
        "intent_id": "intent-result-001",
        "action": "readonly.repo.audit",
        "target": {"repo": "instituto-Rafael/relativity-living-light"},
        "inputs": [],
        "constraints": ["read_only"],
        "evidence_refs": ["chunk-result-001"],
        "requested_capabilities": ["git.read", "git.diff"],
        "risk": "low",
        "execution_gate": "allow",
    }


def test_execution_result_has_hashes_and_timestamps(tmp_path: Path) -> None:
    intent_path = tmp_path / "intent.json"
    out_dir = tmp_path / "out"
    intent_path.write_text(json.dumps(_intent()), encoding="utf-8")

    run = subprocess.run([str(SCRIPT), str(intent_path), str(out_dir)], text=True, capture_output=True, check=True)
    assert run.returncode == 0

    result_payload = json.loads((out_dir / "execution_result.json").read_text(encoding="utf-8"))
    schema_payload = json.loads(RESULT_SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator(schema_payload).validate(result_payload)

    datetime.fromisoformat(result_payload["started_at"].replace("Z", "+00:00"))
    datetime.fromisoformat(result_payload["ended_at"].replace("Z", "+00:00"))

    expected_stdout_parts = []
    expected_stderr_parts = []
    for args in ([ "status" ], [ "diff", "--stat" ]):
        proc = subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True, check=False)
        expected_stdout_parts.append(f"$ git {' '.join(args)}\n{proc.stdout}")
        expected_stderr_parts.append(f"$ git {' '.join(args)}\n{proc.stderr}")
    expected_stdout = "\n".join(expected_stdout_parts)
    expected_stderr = "\n".join(expected_stderr_parts)
    assert result_payload["stdout_sha256"] == hashlib.sha256(expected_stdout.encode("utf-8")).hexdigest()
    assert result_payload["stderr_sha256"] == hashlib.sha256(expected_stderr.encode("utf-8")).hexdigest()
    assert len(result_payload["stderr_sha256"]) == 64
