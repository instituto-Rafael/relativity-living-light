from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "data/governance/RLL_EXECUTION_QUEUE_20260806_V1.json"
TOOL = ROOT / "tools/validate_rll_execution_queue.py"

spec = importlib.util.spec_from_file_location("rll_execution_queue", TOOL)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def payload() -> dict:
    return json.loads(QUEUE.read_text(encoding="utf-8"))


def test_canonical_queue_passes() -> None:
    assert module.validate_document(payload()) == []


def test_claim_promotion_is_blocked() -> None:
    changed = payload()
    changed["claim_allowed"] = True
    assert "claim_allowed must remain false" in module.validate_document(changed)


def test_duplicate_implemented_item_is_blocked() -> None:
    changed = payload()
    changed["queue"][0]["id"] = changed["already_present"][0]["id"]
    assert any("duplicated in active queue" in item for item in module.validate_document(changed))


def test_unknown_dependency_is_blocked() -> None:
    changed = payload()
    changed["queue"][0]["depends_on"] = ["RLL-P0-NOT-MATERIALIZED"]
    assert any("unknown dependency" in item for item in module.validate_document(changed))


def test_dependency_cycle_is_blocked() -> None:
    changed = copy.deepcopy(payload())
    first = changed["queue"][0]["id"]
    second = changed["queue"][1]["id"]
    changed["queue"][0]["depends_on"] = [second]
    changed["queue"][1]["depends_on"] = [first]
    assert any("dependency cycle" in item for item in module.validate_document(changed))
