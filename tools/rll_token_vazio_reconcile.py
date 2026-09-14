#!/usr/bin/env python3
"""Reconcile RLL TOKEN_VAZIO states against materialized evidence.

The reconciler does not try to make all gaps disappear. It converts stale generic
voids into narrower successors, converts proven negative outcomes into terminal
negative facts, and preserves genuinely open work as explicit typed gaps.

A terminal or reduced state is accepted only when every declared evidence
assertion passes. Otherwise the token remains open as OPEN_EVIDENCE_MISSING.

The base rule ledger may be extended by an append-only override ledger. Overrides
replace a rule only in the derived/effective view; the earlier source ledger stays
intact for longitudinal custody.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

INPUT_SCHEMA = "rll.gap_closure_input.v1"
RULES_SCHEMA = "rll.token_vazio_closure_rules.v1"
OVERRIDES_SCHEMA = "rll.token_vazio_closure_overrides.v1"
OUTPUT_SCHEMA = "rll.token_vazio_reconciliation.v1"
DEFAULT_INPUT = Path("data/governance/RLL_GAP_CLOSURE_INPUT_20260807_V1.json")
DEFAULT_RULES = Path("data/governance/RLL_TOKEN_VAZIO_CLOSURE_RULES_20260807_V1.json")
DEFAULT_OVERRIDES = Path("data/governance/RLL_TOKEN_VAZIO_CLOSURE_OVERRIDES_20260807_V1.json")

TERMINAL = {"RESOLVED", "RESOLVED_NEGATIVE"}
NARROWING = {"REDUCED"}
OPEN = {
    "OPEN_INTERNAL",
    "OPEN_EXTERNAL",
    "OPEN_HUMAN",
    "OPEN_GOVERNANCE",
    "OPEN_MIXED",
    "OPEN_EVIDENCE_MISSING",
}
VALID = TERMINAL | NARROWING | OPEN


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: root must be object")
    return payload


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def get_path(payload: Any, dotted: str) -> tuple[bool, Any]:
    cur = payload
    for part in dotted.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        elif isinstance(cur, list) and part.isdigit() and int(part) < len(cur):
            cur = cur[int(part)]
        else:
            return False, None
    return True, cur


def assertion_passes(payload: dict[str, Any], assertion: dict[str, Any]) -> tuple[bool, str]:
    path = assertion.get("path")
    op = assertion.get("op")
    if not isinstance(path, str) or not path:
        return False, "invalid_assertion_path"
    exists, actual = get_path(payload, path)
    if op == "exists":
        expected = assertion.get("value", True)
        ok = exists is bool(expected)
    elif not exists:
        return False, f"missing:{path}"
    elif op == "eq":
        ok = actual == assertion.get("value")
    elif op == "truthy":
        ok = bool(actual)
    elif op == "in":
        values = assertion.get("value")
        ok = isinstance(values, list) and actual in values
    else:
        return False, f"unsupported_op:{op}"
    return ok, "ok" if ok else f"assertion_failed:{path}:{op}"


def validate_input(payload: dict[str, Any]) -> None:
    if payload.get("schema") != INPUT_SCHEMA:
        raise ValueError(f"input schema must be {INPUT_SCHEMA}")
    if payload.get("claim_allowed") is not False:
        raise ValueError("input must preserve claim_allowed=false")
    tokens = payload.get("tokens")
    if not isinstance(tokens, list) or not tokens:
        raise ValueError("input requires non-empty tokens")
    seen: set[str] = set()
    for item in tokens:
        if not isinstance(item, dict):
            raise ValueError("token entry must be object")
        token = item.get("token")
        if not isinstance(token, str) or not token.startswith("TOKEN_VAZIO_"):
            raise ValueError(f"invalid token entry: {token!r}")
        if token in seen:
            raise ValueError(f"duplicate input token: {token}")
        seen.add(token)
        if item.get("priority") not in {"P0", "P1", "P2"}:
            raise ValueError(f"{token}: invalid priority")


def apply_rule_overrides(
    base_payload: dict[str, Any], override_payload: dict[str, Any] | None
) -> dict[str, Any]:
    """Return a derived rules payload with append-only overrides applied."""
    if override_payload is None:
        return json.loads(json.dumps(base_payload))
    if override_payload.get("schema") != OVERRIDES_SCHEMA:
        raise ValueError(f"overrides schema must be {OVERRIDES_SCHEMA}")
    if override_payload.get("claim_allowed") is not False:
        raise ValueError("overrides must preserve claim_allowed=false")
    overrides = override_payload.get("overrides")
    if not isinstance(overrides, list) or not overrides:
        raise ValueError("overrides requires non-empty overrides")

    merged = json.loads(json.dumps(base_payload))
    rules = merged.get("rules")
    if not isinstance(rules, list):
        raise ValueError("base rules must contain a rules list")
    index: dict[str, int] = {}
    for position, rule in enumerate(rules):
        if not isinstance(rule, dict) or not isinstance(rule.get("token"), str):
            raise ValueError("base rule missing token")
        index[rule["token"]] = position

    seen_overrides: set[str] = set()
    for override in overrides:
        if not isinstance(override, dict):
            raise ValueError("override entry must be object")
        token = override.get("token")
        if not isinstance(token, str) or not token.startswith("TOKEN_VAZIO_"):
            raise ValueError(f"invalid override token: {token!r}")
        if token in seen_overrides:
            raise ValueError(f"duplicate override token: {token}")
        seen_overrides.add(token)
        if token in index:
            rules[index[token]] = json.loads(json.dumps(override))
        else:
            index[token] = len(rules)
            rules.append(json.loads(json.dumps(override)))
    return merged


def validate_rules(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    if payload.get("schema") != RULES_SCHEMA:
        raise ValueError(f"rules schema must be {RULES_SCHEMA}")
    if payload.get("claim_allowed") is not False:
        raise ValueError("rules must preserve claim_allowed=false")
    rules = payload.get("rules")
    if not isinstance(rules, list) or not rules:
        raise ValueError("rules requires non-empty rules")
    result: dict[str, dict[str, Any]] = {}
    for rule in rules:
        if not isinstance(rule, dict):
            raise ValueError("rule must be object")
        token = rule.get("token")
        state = rule.get("target_state")
        if not isinstance(token, str) or not token.startswith("TOKEN_VAZIO_"):
            raise ValueError(f"invalid rule token: {token!r}")
        if token in result:
            raise ValueError(f"duplicate rule token: {token}")
        if state not in VALID - {"OPEN_EVIDENCE_MISSING"}:
            raise ValueError(f"{token}: invalid target_state {state!r}")
        if state in TERMINAL | NARROWING:
            if not rule.get("evidence_path"):
                raise ValueError(f"{token}: terminal/reduced rule requires evidence_path")
            assertions = rule.get("assertions")
            if not isinstance(assertions, list) or not assertions:
                raise ValueError(f"{token}: terminal/reduced rule requires assertions")
            if not isinstance(rule.get("resolved_fact"), str) or not rule["resolved_fact"].strip():
                raise ValueError(f"{token}: terminal/reduced rule requires resolved_fact")
        successors = rule.get("successors", [])
        if successors is not None and (
            not isinstance(successors, list)
            or any(not isinstance(x, str) or not x.startswith("TOKEN_VAZIO_") for x in successors)
        ):
            raise ValueError(f"{token}: invalid successors")
        result[token] = rule
    return result


def evaluate_rule(repo_root: Path, item: dict[str, Any], rule: dict[str, Any]) -> dict[str, Any]:
    token = item["token"]
    target = rule["target_state"]
    result: dict[str, Any] = {
        "token": token,
        "priority": item["priority"],
        "domain": item.get("domain"),
        "classification": rule.get("classification"),
        "state": target,
        "evidence_verified": None,
        "evidence_path": rule.get("evidence_path"),
        "evidence_sha256": None,
        "assertions": [],
        "resolved_fact": rule.get("resolved_fact"),
        "next_action": rule.get("next_action"),
        "successors": list(rule.get("successors", [])),
    }

    if target in TERMINAL | NARROWING:
        evidence_path = repo_root / str(rule["evidence_path"])
        if not evidence_path.is_file():
            result["state"] = "OPEN_EVIDENCE_MISSING"
            result["evidence_verified"] = False
            result["assertions"] = [{"ok": False, "reason": "missing_evidence_file"}]
            result["successors"] = []
            result["resolved_fact"] = None
            result["next_action"] = f"MATERIALIZE_EVIDENCE:{rule['evidence_path']}"
            return result
        try:
            evidence = load_json(evidence_path)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            result["state"] = "OPEN_EVIDENCE_MISSING"
            result["evidence_verified"] = False
            result["assertions"] = [{"ok": False, "reason": f"invalid_evidence:{type(exc).__name__}"}]
            result["successors"] = []
            result["resolved_fact"] = None
            result["next_action"] = f"FIX_EVIDENCE:{rule['evidence_path']}"
            return result

        checks = []
        for assertion in rule["assertions"]:
            ok, reason = assertion_passes(evidence, assertion)
            checks.append({"path": assertion.get("path"), "op": assertion.get("op"), "ok": ok, "reason": reason})
        verified = all(check["ok"] for check in checks)
        result["assertions"] = checks
        result["evidence_verified"] = verified
        result["evidence_sha256"] = sha256_file(evidence_path)
        if not verified:
            result["state"] = "OPEN_EVIDENCE_MISSING"
            result["successors"] = []
            result["resolved_fact"] = None
            result["next_action"] = f"REPAIR_OR_REGENERATE_EVIDENCE:{rule['evidence_path']}"
    return result


def reconcile(repo_root: Path, input_payload: dict[str, Any], rules_payload: dict[str, Any], generated_at: str) -> dict[str, Any]:
    validate_input(input_payload)
    rules = validate_rules(rules_payload)
    token_items = input_payload["tokens"]
    missing_rules = sorted(item["token"] for item in token_items if item["token"] not in rules)
    if missing_rules:
        raise ValueError(f"missing rules for input tokens: {', '.join(missing_rules)}")

    results = [evaluate_rule(repo_root, item, rules[item["token"]]) for item in token_items]

    terminal_tokens = sorted(r["token"] for r in results if r["state"] in TERMINAL)
    reduced_tokens = sorted(r["token"] for r in results if r["state"] in NARROWING)
    open_results = [r for r in results if r["state"] in OPEN]

    canonical_open: set[str] = {r["token"] for r in open_results}
    input_token_set = {item["token"] for item in token_items}
    for result in results:
        if result["state"] == "REDUCED":
            canonical_open.update(result["successors"])
        elif result["state"] == "RESOLVED_NEGATIVE":
            canonical_open.update(x for x in result["successors"] if x in input_token_set)

    canonical_open.difference_update(terminal_tokens)
    canonical_open.difference_update(reduced_tokens)

    counts: dict[str, int] = {}
    for result in results:
        counts[result["state"]] = counts.get(result["state"], 0) + 1

    total = len(results)
    resolved_count = sum(counts.get(state, 0) for state in TERMINAL)
    reduced_count = counts.get("REDUCED", 0)
    uncertainty_elimination_ratio = resolved_count / total if total else 0.0
    narrowing_or_resolution_ratio = (resolved_count + reduced_count) / total if total else 0.0

    p0_open = sorted(r["token"] for r in open_results if r["priority"] == "P0")
    p1_open = sorted(r["token"] for r in open_results if r["priority"] == "P1")
    p2_open = sorted(r["token"] for r in open_results if r["priority"] == "P2")

    return {
        "schema": OUTPUT_SCHEMA,
        "generated_at": generated_at,
        "repository": input_payload.get("repository"),
        "claim_allowed": False,
        "publication_ready": False,
        "policy": {
            "terminal_requires_materialized_evidence": True,
            "negative_result_is_valid_resolution": True,
            "reduced_generic_token_is_replaced_by_narrower_successors": True,
            "open_external_is_not_failure_of_the_reconciler": True,
            "scientific_claim_promotion_is_out_of_scope": True,
            "append_only_rule_overrides_preserve_prior_ledger": True,
        },
        "summary": {
            "input_tokens": total,
            "terminal_resolved": resolved_count,
            "reduced_generic": reduced_count,
            "open": len(open_results),
            "counts_by_state": dict(sorted(counts.items())),
            "uncertainty_elimination_ratio": round(uncertainty_elimination_ratio, 6),
            "narrowing_or_resolution_ratio": round(narrowing_or_resolution_ratio, 6),
        },
        "terminal_tokens": terminal_tokens,
        "reduced_tokens": reduced_tokens,
        "canonical_open_tokens": sorted(canonical_open),
        "open_by_priority": {"P0": p0_open, "P1": p1_open, "P2": p2_open},
        "results": results,
        "F_ok": [
            "Stale generic voids can be narrowed only by verified evidence.",
            "Known negative outcomes become terminal negative facts instead of permanent uncertainty.",
            "Every remaining gap has a typed authority and next action."
        ],
        "F_gap": sorted(canonical_open),
        "F_next": [r["next_action"] for r in open_results if r.get("next_action")],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--rules", type=Path, default=DEFAULT_RULES)
    parser.add_argument("--overrides", type=Path, default=DEFAULT_OVERRIDES)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--generated-at", default=None)
    args = parser.parse_args()

    root = args.repo_root.resolve()
    input_path = args.input if args.input.is_absolute() else root / args.input
    rules_path = args.rules if args.rules.is_absolute() else root / args.rules
    overrides_path = args.overrides if args.overrides.is_absolute() else root / args.overrides
    output_path = args.output if args.output.is_absolute() else root / args.output

    generated_at = args.generated_at or datetime.now(timezone.utc).isoformat()
    base_rules = load_json(rules_path)
    overrides = load_json(overrides_path) if overrides_path.is_file() else None
    effective_rules = apply_rule_overrides(base_rules, overrides)
    receipt = reconcile(root, load_json(input_path), effective_rules, generated_at)
    receipt["input_path"] = str(input_path.relative_to(root))
    receipt["input_sha256"] = sha256_file(input_path)
    receipt["rules_path"] = str(rules_path.relative_to(root))
    receipt["rules_sha256"] = sha256_file(rules_path)
    if overrides_path.is_file():
        receipt["overrides_path"] = str(overrides_path.relative_to(root))
        receipt["overrides_sha256"] = sha256_file(overrides_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True))

    invalid = any(r["state"] == "OPEN_EVIDENCE_MISSING" for r in receipt["results"])
    return 2 if invalid else 0


if __name__ == "__main__":
    raise SystemExit(main())
