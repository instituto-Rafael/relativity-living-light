from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "rll_pipeline_deterministic.py"


def load_module():
    spec = importlib.util.spec_from_file_location("rll_pipeline_deterministic_test", MODULE_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_pipeline_exposes_only_explicit_states() -> None:
    module = load_module()
    assert module.VALID_STATES == {"OK", "FAIL", "TOKEN_VAZIO", "SKIP"}


def test_missing_metric_is_token_vazio_not_historical_fallback(tmp_path, monkeypatch) -> None:
    module = load_module()
    monkeypatch.setattr(module, "ROOT", tmp_path)
    result = module.find_metric((("results/missing.json", ("value",)),))
    assert result["state"] == "TOKEN_VAZIO"
    assert result["value"] is None
    assert result["source"] is None


def test_critical_token_vazio_blocks_gate() -> None:
    module = load_module()
    result = module.StepResult(
        number=5,
        name="schema",
        phase=0,
        origin="test",
        critical=True,
        status="TOKEN_VAZIO",
        exit_code=None,
        duration_s=0.0,
        command="",
        detail="missing",
        log_path="log",
    )
    decision = module.gate_decision(
        "dry_run",
        [result],
        {"falsifiers": []},
    )
    assert decision["status"] == "BLOCKED"
    assert decision["claim_allowed"] is False


def test_science_mode_requires_materialized_metrics() -> None:
    module = load_module()
    contract = {
        "falsifiers": [
            {"id": "F-COS-04", "state": "TOKEN_VAZIO"},
        ]
    }
    decision = module.gate_decision("apenas_ciencia", [], contract)
    assert decision["status"] == "BLOCKED"
    assert decision["metric_token_vazio"] == ["F-COS-04"]
