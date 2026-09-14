#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "rll.scientific-cycle-closure.v1"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: root must be an object")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verified_bayes(payload: dict[str, Any]) -> bool:
    return (
        payload.get("state") == "VERIFIED"
        and payload.get("claim_allowed") is False
        and payload.get("bayes_mode") == "inference"
        and bool(payload.get("evidence_path"))
    )


def verified_replication(payload: dict[str, Any]) -> bool:
    required = {
        "state": "PASS_INDEPENDENT_REPLICATION",
        "claim_allowed": False,
        "same_inputs": True,
        "same_model_contract": True,
        "numerical_tolerance_pass": True,
    }
    return all(payload.get(key) == value for key, value in required.items())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bayes-status", type=Path, required=True)
    parser.add_argument("--replication-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    token_vazio: list[str] = []
    bayes: dict[str, Any] = {}
    replication: dict[str, Any] = {}

    if args.bayes_status.is_file():
        bayes = load(args.bayes_status)
    else:
        token_vazio.append("TOKEN_VAZIO_REAL_BAYES_RECEIPT")

    if args.replication_receipt.is_file():
        replication = load(args.replication_receipt)
    else:
        token_vazio.append("TOKEN_VAZIO_INDEPENDENT_REPLICATION")

    bayes_ok = bool(bayes) and verified_bayes(bayes)
    replication_ok = bool(replication) and verified_replication(replication)
    if bayes and not bayes_ok:
        token_vazio.append("TOKEN_VAZIO_REAL_BAYES_NOT_VERIFIED")
    if replication and not replication_ok:
        token_vazio.append("TOKEN_VAZIO_REPLICATION_NOT_VERIFIED")

    scientific_gate = "READY_FOR_HUMAN_REVIEW" if bayes_ok and replication_ok else "BLOCKED"
    receipt = {
        "schema": SCHEMA,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scientific_gate": scientific_gate,
        "claim_allowed": False,
        "publication_ready": False,
        "automatic_promotion_forbidden": True,
        "bayes_verified": bayes_ok,
        "replication_verified": replication_ok,
        "bayes_receipt_sha256": sha256(args.bayes_status) if args.bayes_status.is_file() else None,
        "replication_receipt_sha256": sha256(args.replication_receipt) if args.replication_receipt.is_file() else None,
        "token_vazio": sorted(set(token_vazio)),
        "next_decision": (
            "INDEPENDENT_HUMAN_REVIEW_REQUIRED"
            if scientific_gate == "READY_FOR_HUMAN_REVIEW"
            else "MATERIALIZE_MISSING_RECEIPTS"
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if scientific_gate == "READY_FOR_HUMAN_REVIEW" else 3


if __name__ == "__main__":
    raise SystemExit(main())
