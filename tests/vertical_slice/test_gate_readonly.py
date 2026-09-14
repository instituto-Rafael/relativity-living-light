from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "vertical_slice" / "run_readonly_flow.sh"


def _intent(capabilities: list[str]) -> dict:
    return {
        "schema": "rafaelia.intent.v1",
        "intent_id": "intent-gate-001",
        "action": "readonly.repo.audit",
        "target": {"repo": "instituto-Rafael/relativity-living-light"},
        "inputs": [],
        "constraints": ["read_only"],
        "evidence_refs": ["chunk-gate-001"],
        "requested_capabilities": capabilities,
        "risk": "low",
        "execution_gate": "allow",
    }


def test_gate_blocks_capability_outside_allowlist(tmp_path: Path) -> None:
    intent_path = tmp_path / "intent.json"
    out_dir = tmp_path / "out"
    intent_path.write_text(json.dumps(_intent(["git.read", "network.write"])), encoding="utf-8")
    run = subprocess.run([str(SCRIPT), str(intent_path), str(out_dir)], text=True, capture_output=True, check=True)
    assert run.returncode == 0
    result = json.loads((out_dir / "execution_result.json").read_text(encoding="utf-8"))
    assert result["final_state"] == "blocked"
    assert result["executed_command"] == "blocked_by_governance"
    assert result["exit_code"] == 126
