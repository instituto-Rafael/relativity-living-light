from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _run(path):
    return subprocess.run(
        [sys.executable, str(ROOT / path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


def test_rx_fairness_stdlib_gate() -> None:
    result = _run("tools/validate_rx_fairness.py")
    assert result.returncode == 0, result.stdout + "\n" + result.stderr
    assert '"pass": true' in result.stdout
    assert '"claim_allowed": false' in result.stdout


def test_rx_inference_baseline_gate() -> None:
    result = _run("tools/validate_rx_inference.py")
    assert result.returncode == 0, result.stdout + "\n" + result.stderr
    assert '"pass": true' in result.stdout
    assert '"emcee_semantic_parity": "TOKEN_VAZIO"' in result.stdout
    assert '"dynesty_nested_evidence": "TOKEN_VAZIO"' in result.stdout


def test_rx_zero_dependency_gate_covers_new_modules() -> None:
    result = _run("tools/rx_zero_dependency_gate.py")
    assert result.returncode == 0, result.stdout + "\n" + result.stderr
    assert "RX_ZERO_DEPENDENCY_GATE=PASS" in result.stdout
