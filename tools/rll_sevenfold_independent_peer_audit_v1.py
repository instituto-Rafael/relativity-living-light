#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "data/governance/RLL_SEVENFOLD_INDEPENDENT_PEER_AUDIT_V1.json"

ALLOWED = {"PASS_BOUNDED", "FAIL_FALSIFIED", "TOKEN_VAZIO", "INCONCLUSIVE"}


def load_contract() -> dict[str, Any]:
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def canonical_sha256(obj: Any) -> str:
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def validate_contract() -> dict[str, Any]:
    d = load_contract()
    errors: list[str] = []
    peers = d.get("peers", [])

    if len(peers) != 7:
        errors.append(f"expected 7 peers, got {len(peers)}")

    peer_ids = [p.get("peer_id") for p in peers]
    omegas = [p.get("omega_namespace") for p in peers]
    ddaggers = [p.get("ddagger_operator") for p in peers]

    if len(set(peer_ids)) != 7:
        errors.append("peer ids must be unique")
    if len(set(omegas)) != 7:
        errors.append("Ω namespaces must be unique")
    if len(set(ddaggers)) != 7:
        errors.append("‡ falsifier operators must be unique")

    test_ids: list[str] = []
    for p in peers:
        tests = p.get("tests", [])
        if len(tests) != 7:
            errors.append(f"{p.get('peer_id')}: expected 7 tests, got {len(tests)}")
        test_ids.extend(f"{p.get('peer_id')}::{x}" for x in tests)

    if len(test_ids) != 49:
        errors.append(f"expected 49 peer tests, got {len(test_ids)}")

    indep = d.get("independence_protocol", {})
    required_forbidden = [
        "peer_verdict_visibility_before_seal",
        "cross_peer_messages_before_seal",
        "shared_conclusion_seed",
        "peer_receipt_mutation_after_seal",
        "majority_vote",
        "averaging",
        "token_vazio_compensation",
    ]
    for key in required_forbidden:
        if indep.get(key) != "FORBIDDEN":
            errors.append(f"{key} must be FORBIDDEN")

    pair = d.get("paired_review_protocol", {})
    if pair.get("roles") != ["constructive_reconstructor", "adversarial_falsifier"]:
        errors.append("paired roles mismatch")

    graph = d.get("semantic_token_graph_policy", {})
    if graph.get("externalized_graph_only") is not True:
        errors.append("semantic graph must be externalized only")
    if graph.get("internal_hidden_tokens_or_chain_of_thought_claimed") is not False:
        errors.append("hidden internal tokens/chain-of-thought must not be claimed")
    if graph.get("literal_free_will_claim") is not False:
        errors.append("literal free-will claim must remain false")

    auth = d.get("authorship_policy", {})
    if auth.get("analytical_peer_role_is_legal_author") is not False:
        errors.append("peer role must not be treated as legal author")
    if auth.get("hash_or_commit_proves_chronology_not_authorship") is not True:
        errors.append("chronology/authorship boundary missing")

    agg = d.get("global_aggregation", {})
    if agg.get("claim_allowed_after_all_pass") is not False:
        errors.append("all-pass review must not directly allow scientific claim")
    if agg.get("replication_still_required") is not True:
        errors.append("independent replication must remain required")

    atomic = d.get("atomic_target_policy", {})
    if atomic.get("one_claim_or_gap_per_round") is not True:
        errors.append("review target must be atomic")
    if atomic.get("cross_claim_compensation_forbidden") is not True:
        errors.append("cross-claim compensation must be forbidden")

    return {
        "schema": "rll.sevenfold_independent_peer_audit_validation.v1",
        "pass": not errors,
        "errors": errors,
        "peer_count": len(peers),
        "tests_per_peer": [len(p.get("tests", [])) for p in peers],
        "total_checks": sum(len(p.get("tests", [])) for p in peers),
        "contract_sha256": canonical_sha256(d),
        "claim_allowed": False,
        "status": "SEVENFOLD_CONTRACT_VALID" if not errors else "SEVENFOLD_CONTRACT_BLOCKED",
    }


def aggregate_receipts(receipts: list[dict[str, Any]]) -> dict[str, Any]:
    d = load_contract()
    expected = {p["peer_id"] for p in d["peers"]}
    errors: list[str] = []

    by_peer: dict[str, dict[str, Any]] = {}
    for r in receipts:
        pid = r.get("peer_id")
        if pid in by_peer:
            errors.append(f"duplicate receipt for {pid}")
        else:
            by_peer[pid] = r

    missing = sorted(expected - set(by_peer))
    extra = sorted(set(by_peer) - expected)
    if missing:
        errors.append(f"missing peer receipts: {missing}")
    if extra:
        errors.append(f"unexpected peer receipts: {extra}")

    verdicts: dict[str, str] = {}
    for pid, r in by_peer.items():
        verdict = r.get("verdict")
        verdicts[pid] = verdict
        if verdict not in ALLOWED:
            errors.append(f"{pid}: invalid verdict {verdict}")
        if r.get("sealed") is not True:
            errors.append(f"{pid}: receipt is not sealed")
        if r.get("peer_verdicts_visible_before_seal") is not False:
            errors.append(f"{pid}: isolation breach")
        if r.get("mandatory_test_count") != 7:
            errors.append(f"{pid}: expected 7 mandatory test results")

    if errors:
        state = "NOT_PROMOTABLE_INVALID_OR_INCOMPLETE_RECEIPTS"
    elif any(v == "FAIL_FALSIFIED" for v in verdicts.values()):
        state = "REVIEW_BLOCKED_BY_FALSIFICATION"
    elif any(v in {"TOKEN_VAZIO", "INCONCLUSIVE"} for v in verdicts.values()):
        state = "NOT_PROMOTABLE_INCOMPLETE_REVIEW"
    elif verdicts and all(v == "PASS_BOUNDED" for v in verdicts.values()):
        state = "SEVENFOLD_REVIEW_PASSED_NO_CLAIM_PROMOTION"
    else:
        state = "NOT_PROMOTABLE_INCOMPLETE_REVIEW"

    return {
        "schema": "rll.sevenfold_independent_peer_audit_aggregate.v1",
        "state": state,
        "claim_allowed": False,
        "errors": errors,
        "verdicts": verdicts,
        "sealed_receipt_count": sum(1 for r in receipts if r.get("sealed") is True),
        "required_receipt_count": 7,
        "replication_required": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = validate_contract()
    payload = json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    print(payload, end="")
    if args.output:
        out = args.output if args.output.is_absolute() else ROOT / args.output
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(payload, encoding="utf-8")
    return 0 if report["pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
