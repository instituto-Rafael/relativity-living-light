#!/usr/bin/env python3
"""Compile an effective RLL execution queue from immutable queue + receipts.

The source queue remains historical. Receipts may resolve queue items only when
all promotion fields match the original state exactly. The output removes no
history: it records resolved items, satisfied dependencies, remaining blockers,
and the next executable gates while keeping ``claim_allowed`` false.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Iterable

RECEIPT_SCHEMA_RE = re.compile(r"^rll\.[a-z0-9_]+_receipt\.v1$")
URGENCY_ORDER = {"P0": 0, "P1": 1, "P2": 2}


class EffectiveQueueError(ValueError):
    """Raised when a receipt cannot safely alter the effective queue."""


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise EffectiveQueueError(f"{path}: root must be an object")
    return payload


def canonical_json_bytes(payload: Any) -> bytes:
    return (
        json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def payload_sha256(payload: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(payload)).hexdigest()


def _queue_index(queue: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    items = queue.get("queue")
    if not isinstance(items, list) or not items:
        raise EffectiveQueueError("source queue must contain a non-empty queue array")

    ordered: list[dict[str, Any]] = []
    index: dict[str, dict[str, Any]] = {}
    for raw in items:
        if not isinstance(raw, dict):
            raise EffectiveQueueError("source queue item must be an object")
        item_id = raw.get("id")
        if not isinstance(item_id, str) or not item_id:
            raise EffectiveQueueError("source queue item id must be a non-empty string")
        if item_id in index:
            raise EffectiveQueueError(f"duplicate source queue item: {item_id}")
        item = copy.deepcopy(raw)
        ordered.append(item)
        index[item_id] = item
    return ordered, index


def _validate_source_queue(queue: dict[str, Any]) -> None:
    if queue.get("schema") != "rll.execution_queue.v1":
        raise EffectiveQueueError("unsupported source queue schema")
    if queue.get("claim_allowed") is not False:
        raise EffectiveQueueError("source queue claim_allowed must remain false")
    _queue_index(queue)


def _validate_receipt(
    receipt: dict[str, Any],
    queue_index: dict[str, dict[str, Any]],
) -> tuple[str, dict[str, Any]]:
    schema = receipt.get("schema")
    if not isinstance(schema, str) or not RECEIPT_SCHEMA_RE.fullmatch(schema):
        raise EffectiveQueueError(f"unsupported receipt schema: {schema!r}")
    if receipt.get("claim_allowed") is not False:
        raise EffectiveQueueError("receipt claim_allowed must remain false")

    target_id = receipt.get("supersedes_queue_item")
    if not isinstance(target_id, str) or target_id not in queue_index:
        raise EffectiveQueueError(f"receipt targets unknown queue item: {target_id!r}")

    original = queue_index[target_id]
    promotion = receipt.get("promotion")
    if not isinstance(promotion, dict):
        raise EffectiveQueueError(f"receipt promotion missing for {target_id}")
    before = promotion.get("from")
    after = promotion.get("to")
    if not isinstance(before, dict) or not isinstance(after, dict):
        raise EffectiveQueueError(f"receipt promotion must define from/to for {target_id}")

    expected_before = {
        "evidence_class": original.get("evidence_class"),
        "state": original.get("state"),
    }
    observed_before = {
        "evidence_class": before.get("evidence_class"),
        "state": before.get("state"),
    }
    if observed_before != expected_before:
        raise EffectiveQueueError(
            f"receipt promotion.from mismatch for {target_id}: "
            f"expected {expected_before}, got {observed_before}"
        )

    receipt_after = {
        "evidence_class": receipt.get("evidence_class"),
        "state": receipt.get("state"),
    }
    observed_after = {
        "evidence_class": after.get("evidence_class"),
        "state": after.get("state"),
    }
    if observed_after != receipt_after:
        raise EffectiveQueueError(
            f"receipt promotion.to mismatch for {target_id}: "
            f"receipt {receipt_after}, promotion {observed_after}"
        )
    if receipt_after["evidence_class"] not in {"E", "C"}:
        raise EffectiveQueueError(
            f"receipt cannot resolve {target_id} with class "
            f"{receipt_after['evidence_class']!r}"
        )
    if not isinstance(receipt_after["state"], str) or "TOKEN_VAZIO" in receipt_after["state"]:
        raise EffectiveQueueError(f"receipt does not close the gap for {target_id}")

    next_gate = receipt.get("next_gate")
    if next_gate is not None and next_gate not in queue_index:
        raise EffectiveQueueError(f"receipt next_gate is unknown: {next_gate!r}")

    generated_at = receipt.get("generated_at")
    if not isinstance(generated_at, str) or not generated_at:
        raise EffectiveQueueError(f"receipt generated_at missing for {target_id}")
    return target_id, original


def build_effective_queue(
    queue: dict[str, Any],
    receipts: Iterable[dict[str, Any]],
) -> dict[str, Any]:
    """Apply valid receipts without mutating the historical source queue."""
    _validate_source_queue(queue)
    ordered_items, queue_index = _queue_index(queue)

    prepared: list[tuple[str, str, dict[str, Any]]] = []
    for raw_receipt in receipts:
        if not isinstance(raw_receipt, dict):
            raise EffectiveQueueError("receipt root must be an object")
        receipt = copy.deepcopy(raw_receipt)
        target_id, _ = _validate_receipt(receipt, queue_index)
        prepared.append((str(receipt["generated_at"]), target_id, receipt))

    prepared.sort(key=lambda row: (row[0], row[1], payload_sha256(row[2])))

    resolved: dict[str, dict[str, Any]] = {}
    applied_receipts: list[dict[str, Any]] = []
    for _, target_id, receipt in prepared:
        if target_id in resolved:
            raise EffectiveQueueError(f"multiple receipts resolve the same item: {target_id}")
        original = queue_index[target_id]
        digest = payload_sha256(receipt)
        resolved[target_id] = {
            "id": target_id,
            "previous_state": original.get("state"),
            "previous_evidence_class": original.get("evidence_class"),
            "state": receipt.get("state"),
            "evidence_class": receipt.get("evidence_class"),
            "receipt_schema": receipt.get("schema"),
            "receipt_generated_at": receipt.get("generated_at"),
            "receipt_sha256": digest,
            "next_gate": receipt.get("next_gate"),
        }
        applied_receipts.append(
            {
                "target_id": target_id,
                "schema": receipt.get("schema"),
                "generated_at": receipt.get("generated_at"),
                "sha256": digest,
            }
        )

    active: list[dict[str, Any]] = []
    queue_position = {item["id"]: pos for pos, item in enumerate(ordered_items)}
    for original in ordered_items:
        item_id = original["id"]
        if item_id in resolved:
            continue
        effective_item = copy.deepcopy(original)
        original_dependencies = list(effective_item.get("depends_on", []))
        satisfied = [dep for dep in original_dependencies if dep in resolved]
        blocked_by = [dep for dep in original_dependencies if dep not in resolved]
        effective_item["original_depends_on"] = original_dependencies
        effective_item["satisfied_dependencies"] = satisfied
        effective_item["blocked_by"] = blocked_by
        effective_item["ready"] = not blocked_by
        active.append(effective_item)

    ready_items = [item for item in active if item["ready"]]
    ready_items.sort(
        key=lambda item: (
            URGENCY_ORDER.get(str(item.get("urgency")), 99),
            queue_position[str(item["id"])],
        )
    )

    latest_receipt_at = max((row[0] for row in prepared), default=None)
    return {
        "schema": "rll.execution_queue.effective.v1",
        "generated_from": {
            "source_queue_schema": queue.get("schema"),
            "source_queue_generated_at": queue.get("generated_at"),
            "source_main_commit": queue.get("source_main_commit"),
            "source_queue_sha256": payload_sha256(queue),
            "latest_receipt_at": latest_receipt_at,
        },
        "repository": queue.get("repository"),
        "claim_allowed": False,
        "invariants": [
            "source_queue_is_immutable_history",
            "receipts_are_append_only_successors",
            "promotion_from_must_match_original_state",
            "TOKEN_VAZIO_is_not_closed_without_E_or_C_receipt",
            "physical_gates_require_physical_authority",
            "negative_results_remain_visible",
        ],
        "applied_receipts": applied_receipts,
        "resolved": [resolved[item["id"]] for item in ordered_items if item["id"] in resolved],
        "active_queue": active,
        "next_ready": [item["id"] for item in ready_items],
        "closure": {
            "F_ok": [
                f"{len(resolved)} queue item(s) resolved by matching receipts",
                "historical queue preserved without overwrite",
            ],
            "F_gap": [
                f"{len(active)} active queue item(s) remain",
                "ready state does not replace domain-specific execution receipts",
            ],
            "F_next": ready_items[0]["id"] if ready_items else "TOKEN_VAZIO_NO_READY_GATE",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "queue",
        nargs="?",
        type=Path,
        default=Path("data/governance/RLL_EXECUTION_QUEUE_20260806_V1.json"),
    )
    parser.add_argument(
        "--receipt",
        action="append",
        type=Path,
        default=[],
        help="Append-only successor receipt; may be repeated.",
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    try:
        queue = load_json(args.queue)
        receipts = [load_json(path) for path in args.receipt]
        effective = build_effective_queue(queue, receipts)
    except (OSError, json.JSONDecodeError, EffectiveQueueError) as exc:
        print(f"BLOCKED: {exc}")
        return 1

    encoded = json.dumps(effective, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    else:
        print(encoded, end="")

    next_gate = effective["closure"]["F_next"]
    print(
        "PASS: effective queue compiled; "
        f"resolved={len(effective['resolved'])} "
        f"active={len(effective['active_queue'])} "
        f"next={next_gate}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
