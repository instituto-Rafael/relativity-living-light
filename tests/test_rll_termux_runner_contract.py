from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/termux/rll_evidence_replay_v1.sh"


def test_termux_runner_is_posix_shell_parseable() -> None:
    subprocess.run(["sh", "-n", str(RUNNER)], check=True)


def test_termux_runner_preserves_physical_receipt_contract() -> None:
    text = RUNNER.read_text(encoding="utf-8")
    for required in (
        "for cmd in python sha256sum git uname getprop awk date wc",
        "BLOCKED_INPUT_SHA",
        "BLOCKED_PHYSICAL_IDENTITY",
        '"schema": "rll.termux_physical_replay_receipt.v1"',
        '"supersedes_queue_item": "RLL-P0-TERMUX-PHYSICAL-REPLAY"',
        '"next_gate": "RLL-P0-PANTHEON-SUCCESSOR-RUN"',
        '"claim_allowed": False',
        'python tools/validate_rll_termux_physical_replay.py "$OUT_DIR"',
    ):
        assert required in text
