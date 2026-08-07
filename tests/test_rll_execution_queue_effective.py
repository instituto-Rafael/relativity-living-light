from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "data/governance/RLL_EXECUTION_QUEUE_20260806_V1.json"
RECEIPT = ROOT / "results/governance/RLL_POSTMERGE_CI_RECEIPT_20260806_V1.json"
TOOL = ROOT / "tools/rll_execution_queue_effective.py"

spec = importlib.util.spec_from_file_location("rll_execution_queue_effective", TOOL)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_postmerge_receipt_resolves_first_gate_and_releases_termux() -> None:
    effective = module.build_effective_queue(load(QUEUE), [load(RECEIPT)])

    resolved_ids = [item["id"] for item in effective["resolved"]]
    assert resolved_ids == ["RLL-P0-POSTMERGE-CI-RECEIPT"]
    assert effective["claim_allowed"] is False
    assert effective["closure"]["F_next"] == "RLL-P0-TERMUX-PHYSICAL-REPLAY"
    assert effective["next_ready"][0] == "RLL-P0-TERMUX-PHYSICAL-REPLAY"

    active = {item["id"]: item for item in effective["active_queue"]}
    termux = active["RLL-P0-TERMUX-PHYSICAL-REPLAY"]
    assert termux["ready"] is True
    assert termux["blocked_by"] == []
    assert termux["satisfied_dependencies"] == ["RLL-P0-POSTMERGE-CI-RECEIPT"]


def test_build_is_deterministic() -> None:
    queue = load(QUEUE)
    receipt = load(RECEIPT)
    first = module.build_effective_queue(queue, [receipt])
    second = module.build_effective_queue(queue, [receipt])
    assert module.canonical_json_bytes(first) == module.canonical_json_bytes(second)


def test_unknown_queue_target_is_blocked() -> None:
    receipt = load(RECEIPT)
    receipt["supersedes_queue_item"] = "RLL-P0-NOT-REAL"
    with pytest.raises(module.EffectiveQueueError, match="unknown queue item"):
        module.build_effective_queue(load(QUEUE), [receipt])


def test_receipt_cannot_enable_claims() -> None:
    receipt = load(RECEIPT)
    receipt["claim_allowed"] = True
    with pytest.raises(module.EffectiveQueueError, match="claim_allowed"):
        module.build_effective_queue(load(QUEUE), [receipt])


def test_receipt_must_match_original_state() -> None:
    receipt = load(RECEIPT)
    receipt["promotion"]["from"]["state"] = "DONE_BY_ASSERTION"
    with pytest.raises(module.EffectiveQueueError, match="promotion.from mismatch"):
        module.build_effective_queue(load(QUEUE), [receipt])


def test_token_vazio_receipt_does_not_close_gate() -> None:
    receipt = load(RECEIPT)
    receipt["state"] = "TOKEN_VAZIO_STILL_OPEN"
    receipt["promotion"]["to"]["state"] = "TOKEN_VAZIO_STILL_OPEN"
    with pytest.raises(module.EffectiveQueueError, match="does not close the gap"):
        module.build_effective_queue(load(QUEUE), [receipt])


def test_duplicate_receipts_for_same_gate_are_blocked() -> None:
    receipt = load(RECEIPT)
    with pytest.raises(module.EffectiveQueueError, match="multiple receipts"):
        module.build_effective_queue(load(QUEUE), [receipt, copy.deepcopy(receipt)])
