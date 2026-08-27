#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ENVELOPE = ROOT / "data/governance/RLL_ATLAS_CONTINUOUS_EVOLUTION_ENVELOPE_20260827_V1.json"
DEFAULT_TRACE = ROOT / "data/governance/RLL_ATLAS_SESSION_INTERACTION_TRACE_20260827_V1.jsonl"
DEFAULT_PREDECESSOR = ROOT / "data/governance/RLL_ATLAS_EVOLUTION_GATE_20260827_V1.json"

EXPECTED_GUARDRAILS = (
    "OMEGA6_PROVENANCE_LOCK",
    "OMEGA6_RECEIPT_CHAIN",
    "OMEGA6_CUSTODY_DAG",
    "OMEGA6_ADVERSARIAL_PARITY",
    "OMEGA6_REPRO_REPLAY",
    "OMEGA6_INDEPENDENT_REPLICATION",
)
EXPECTED_GATES = (
    "G0_SOURCE_RIGHTS_FREEZE",
    "G1_OBSERVABLE_SCHEMA",
    "G2_FULL_COVARIANCE",
    "G3_LIKELIHOOD_PARITY",
    "G4_BASELINE_RECOVERY",
    "G5_ROBUST_INFERENCE",
    "G6_GROWTH_PERTURBATIONS",
    "G7_CLAIM_DECISION",
)
STATUS_MATURITY = {
    "TOKEN_VAZIO": 0,
    "BLOCKED": 0,
    "PARTIAL": 1,
    "VERIFIED_LIMITED": 2,
    "VERIFIED": 3,
    "REPLICATED": 4,
}
MANDATORY_CLAIM_BLOCKERS = {
    "TOKEN_VAZIO_INDEPENDENT_REPLICATION",
    "TOKEN_VAZIO_DESI_DR2_OFFICIAL_JOINT_CROSSBLOCK_REPRODUCTION",
    "TOKEN_VAZIO_ACT_DR6_LCDM_POSTERIOR_CHAIN_REPRODUCTION",
    "TOKEN_VAZIO_DES_Y6_3X2PT_LIKELIHOOD",
    "TOKEN_VAZIO_RLL_PERTURBATION_CLOSURE_RELATIONS",
    "TOKEN_VAZIO_RLL_CLASS_CAMB_IMPLEMENTATION",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw.strip():
            continue
        value = json.loads(raw)
        if not isinstance(value, dict):
            raise ValueError(f"trace line {lineno} must be an object")
        rows.append(value)
    return rows


def _is_hex(value: Any, size: int) -> bool:
    return isinstance(value, str) and len(value) == size and all(c in "0123456789abcdef" for c in value.lower())


def _digest_ok(value: Any) -> bool:
    return isinstance(value, str) and value.startswith("sha256:") and _is_hex(value.split(":", 1)[1], 64)


def _graph_has_cycle(nodes: set[str], edges: list[dict[str, Any]]) -> bool:
    adjacency: dict[str, list[str]] = {node: [] for node in nodes}
    indegree = {node: 0 for node in nodes}
    for edge in edges:
        src, dst = edge.get("from"), edge.get("to")
        if src in nodes and dst in nodes:
            adjacency[src].append(dst)
            indegree[dst] += 1
    queue = [node for node, degree in indegree.items() if degree == 0]
    visited = 0
    while queue:
        node = queue.pop()
        visited += 1
        for nxt in adjacency[node]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                queue.append(nxt)
    return visited != len(nodes)


def validate_trace(trace_rows: list[dict[str, Any]], expected_sha256: str) -> list[str]:
    errors: list[str] = []
    seqs = [row.get("seq") for row in trace_rows]
    if seqs != list(range(1, len(trace_rows) + 1)):
        errors.append("session trace seq must be contiguous starting at 1")
    for idx, row in enumerate(trace_rows, start=1):
        if not _is_hex(row.get("prompt_sha256"), 64):
            errors.append(f"trace[{idx}].prompt_sha256 must be 64-char SHA-256 hex")
        if "private_reasoning" in row or "chain_of_thought" in row:
            errors.append(f"trace[{idx}] must not serialize private reasoning")
        for key in ("interaction_type", "intent", "action", "outcome", "risk_delta", "next"):
            if not isinstance(row.get(key), str) or not row[key]:
                errors.append(f"trace[{idx}].{key} is required")
    normalized = "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in trace_rows)
    actual = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    if actual != expected_sha256:
        errors.append(f"session trace SHA-256 mismatch: expected {expected_sha256}, got {actual}")
    return errors


def validate_envelope(envelope: dict[str, Any], predecessor: dict[str, Any], trace_rows: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    if envelope.get("schema") != "rll.atlas_continuous_evolution_envelope.v1":
        errors.append("schema mismatch")
    if envelope.get("append_only") is not True:
        errors.append("append_only must be true")
    if envelope.get("claim_allowed") is not False:
        errors.append("current envelope must remain claim_allowed=false")
    if envelope.get("publication_ready") is not False:
        errors.append("current envelope must remain publication_ready=false")

    pred = envelope.get("predecessor", {})
    if pred.get("record_id") != predecessor.get("record_id"):
        errors.append("predecessor record_id mismatch")
    if pred.get("path") != "data/governance/RLL_ATLAS_EVOLUTION_GATE_20260827_V1.json":
        errors.append("predecessor path mismatch")
    if not _is_hex(pred.get("git_blob_sha1"), 40):
        errors.append("predecessor git_blob_sha1 invalid")

    authority = envelope.get("authority", {})
    if authority.get("repository") != "instituto-Rafael/relativity-living-light":
        errors.append("authority repository mismatch")
    if authority.get("repository_id") != 1046495816:
        errors.append("authority repository_id mismatch")
    if authority.get("branch") != "rll/lab":
        errors.append("continuous envelope must be rooted at rll/lab")
    if not _is_hex(authority.get("head_sha"), 40) or not _is_hex(authority.get("tree_sha"), 40):
        errors.append("authority head/tree SHA invalid")
    if authority.get("promotion_pr") != 780:
        errors.append("promotion_pr must preserve PR#780 lineage")
    if authority.get("promotion_merge_commit") != authority.get("head_sha"):
        errors.append("promotion merge commit must equal pinned rll/lab head for this record")

    trace_meta = envelope.get("session_trace", {})
    if trace_meta.get("known_prompt_count") != len({row.get("prompt_sha256") for row in trace_rows}):
        errors.append("known_prompt_count mismatch")
    if trace_meta.get("known_event_count") != len(trace_rows):
        errors.append("known_event_count mismatch")
    if not _is_hex(trace_meta.get("sha256"), 64):
        errors.append("session trace sha256 invalid")
    else:
        errors.extend(validate_trace(trace_rows, trace_meta["sha256"]))

    guards = envelope.get("omega6_guardrails")
    if not isinstance(guards, list):
        errors.append("omega6_guardrails must be a list")
        guards = []
    guard_ids = [g.get("id") for g in guards if isinstance(g, dict)]
    if tuple(guard_ids) != EXPECTED_GUARDRAILS:
        errors.append(f"exact OMEGA6 guardrail set/order required: {EXPECTED_GUARDRAILS!r}")
    for guard in guards:
        if guard.get("state") != "ACTIVE":
            errors.append(f"{guard.get('id')}: guardrail must be ACTIVE")
        if guard.get("claim_blocking") is not True:
            errors.append(f"{guard.get('id')}: claim_blocking must be true")
        if not guard.get("mode") or not guard.get("failure_action"):
            errors.append(f"{guard.get('id')}: mode and failure_action required")

    urgency = envelope.get("urgency_policy", {})
    if urgency.get("truth_threshold_mutable") is not False:
        errors.append("urgency may not mutate truth threshold")
    if urgency.get("evidence_threshold_mutable") is not False:
        errors.append("urgency may not mutate evidence threshold")

    execution = envelope.get("continuous_execution", {})
    if execution.get("executor") != ".github/workflows/rll-governance-quality-gate.yml":
        errors.append("continuous executor must reuse the existing governance workflow")
    if execution.get("auto_merge") is not False:
        errors.append("auto_merge must remain false")
    forbidden = set(execution.get("forbidden_autonomous_actions", []))
    required_forbidden = {
        "automatic scientific claim promotion",
        "force-moving protected maturity refs",
        "deleting historical evidence",
        "auto-merging unreviewed scientific changes",
    }
    if not required_forbidden.issubset(forbidden):
        errors.append("continuous execution missing forbidden autonomous actions")

    receipt = envelope.get("receipt_chain", {})
    if receipt.get("append_only") is not True:
        errors.append("receipt_chain.append_only must be true")
    pred_receipt = receipt.get("predecessor_receipt", {})
    if pred_receipt.get("workflow_run_id") != 33117071438:
        errors.append("predecessor workflow receipt run mismatch")
    if not _digest_ok(pred_receipt.get("digest")):
        errors.append("predecessor receipt digest invalid")
    if not _is_hex(pred_receipt.get("head_sha"), 40):
        errors.append("predecessor receipt head_sha invalid")

    graph = envelope.get("custody_graph", {})
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    if not isinstance(nodes, list) or not isinstance(edges, list):
        errors.append("custody_graph nodes/edges must be lists")
        nodes, edges = [], []
    ids = [n.get("id") for n in nodes if isinstance(n, dict)]
    if len(ids) != len(set(ids)):
        errors.append("custody graph node IDs must be unique")
    node_set = set(ids)
    for node in nodes:
        node_id = node.get("id")
        if not node_id or not node.get("type"):
            errors.append("every custody node needs id and type")
        if node.get("type") in {"SOURCE", "EVIDENCE"} and not _is_hex(node.get("git_blob_sha1"), 40):
            errors.append(f"{node_id}: source/evidence node needs immutable git_blob_sha1")
        if node.get("type") == "GENERATED" and not _is_hex(node.get("sha256"), 64):
            errors.append(f"{node_id}: generated node needs SHA-256")
    for edge in edges:
        if edge.get("from") not in node_set or edge.get("to") not in node_set:
            errors.append("custody edge references unknown node")
        if not edge.get("relation"):
            errors.append("custody edge relation required")
    if _graph_has_cycle(node_set, edges):
        errors.append("custody graph must be acyclic")
    incoming = {node: 0 for node in node_set}
    for edge in edges:
        if edge.get("to") in incoming:
            incoming[edge["to"]] += 1
    for node in nodes:
        if node.get("type") in {"GATE", "RECEIPT"} and incoming.get(node.get("id"), 0) == 0:
            errors.append(f"{node.get('id')}: promotion node is orphaned")

    gates = envelope.get("atlas_gate_projection")
    if not isinstance(gates, list):
        errors.append("atlas_gate_projection must be a list")
        gates = []
    ids = [g.get("id") for g in gates if isinstance(g, dict)]
    if tuple(ids) != EXPECTED_GATES:
        errors.append(f"gate identity/order mismatch: {ids!r}")
    pred_by_id = {g.get("id"): g for g in predecessor.get("gates", []) if isinstance(g, dict) and isinstance(g.get("id"), str)}
    for gate in gates:
        gate_id = gate.get("id")
        status = gate.get("status")
        maturity = gate.get("maturity")
        if status not in STATUS_MATURITY:
            errors.append(f"{gate_id}: unknown status {status!r}")
            continue
        if maturity != STATUS_MATURITY[status]:
            errors.append(f"{gate_id}: status/maturity mismatch")
        pred_gate = pred_by_id.get(gate_id)
        if pred_gate is None:
            errors.append(f"{gate_id}: predecessor gate missing")
            continue
        pred_maturity = pred_gate.get("maturity")
        if gate.get("predecessor_maturity") != pred_maturity:
            errors.append(f"{gate_id}: predecessor_maturity does not match predecessor record")
        if isinstance(pred_maturity, int) and isinstance(maturity, int) and maturity < pred_maturity:
            errors.append(f"{gate_id}: maturity regression {pred_maturity}->{maturity}")
        evidence = gate.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            errors.append(f"{gate_id}: non-empty evidence list required")
        else:
            for item in evidence:
                if not isinstance(item, dict) or not item.get("path") or not _is_hex(item.get("git_blob_sha1"), 40):
                    errors.append(f"{gate_id}: each evidence pointer needs path + 40-char git blob SHA")

    gaps = envelope.get("gap_reconciliation")
    if not isinstance(gaps, list):
        errors.append("gap_reconciliation must be a list")
        gaps = []
    gap_by_token = {g.get("token"): g for g in gaps if isinstance(g, dict)}
    for token in MANDATORY_CLAIM_BLOCKERS:
        item = gap_by_token.get(token)
        if item is None:
            errors.append(f"mandatory blocker omitted: {token}")
        elif item.get("state") == "RESOLVED":
            errors.append(f"{token}: V1 continuous envelope forbids resolving mandatory claim blockers inline")

    bayes = gap_by_token.get("TOKEN_VAZIO_REAL_BAYES_INFERENCE", {})
    if bayes.get("state") not in {"REDUCED", "OPEN", "OPEN_MIXED"}:
        errors.append("generic Bayes token may be narrowed but not falsely closed by SN-only evidence")
    independent = gap_by_token.get("TOKEN_VAZIO_INDEPENDENT_REPLICATION", {})
    if independent.get("state") == "RESOLVED":
        errors.append("internal numerical replay cannot resolve independent replication")

    invariants = set(envelope.get("invariants", []))
    required_invariants = {
        "TOKEN_VAZIO_NE_PASS",
        "REDUCED_NE_RESOLVED",
        "INTERNAL_REPLAY_NE_INDEPENDENT_REPLICATION",
        "URGENCY_CHANGES_ORDER_NOT_TRUTH",
        "NEGATIVE_RESULT_IS_EVIDENCE_NOT_REGRESSION",
    }
    if not required_invariants.issubset(invariants):
        errors.append("required anti-regression invariants missing")
    return errors


def build_receipt(envelope: dict[str, Any], errors: list[str]) -> dict[str, Any]:
    gates = envelope.get("atlas_gate_projection", [])
    preclaim = [g for g in gates if isinstance(g, dict) and g.get("id") != "G7_CLAIM_DECISION"]
    maturity_total = sum(int(g.get("maturity", 0)) for g in preclaim)
    denominator = 7 * 3
    open_gaps = [g.get("token") for g in envelope.get("gap_reconciliation", []) if isinstance(g, dict) and str(g.get("state", "")).startswith("OPEN")]
    return {
        "schema": "rll.atlas_continuous_evolution_omega6.receipt.v1",
        "record_id": envelope.get("record_id"),
        "valid": not errors,
        "claim_allowed": False,
        "publication_ready": False,
        "omega6_active_count": sum(1 for g in envelope.get("omega6_guardrails", []) if isinstance(g, dict) and g.get("state") == "ACTIVE"),
        "scientific_promotion_gate_fraction": round(maturity_total / denominator, 6),
        "gate_states": {g.get("id"): g.get("status") for g in gates if isinstance(g, dict)},
        "open_gap_tokens": open_gaps,
        "errors": errors,
        "boundary": "This receipt proves repository-local governance/custody progression only. It does not certify RLL physics, statistical preference, legal compliance, external reproducibility, or independent replication.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--envelope", type=Path, default=DEFAULT_ENVELOPE)
    parser.add_argument("--trace", type=Path, default=DEFAULT_TRACE)
    parser.add_argument("--predecessor", type=Path, default=DEFAULT_PREDECESSOR)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    envelope = load_json(args.envelope)
    predecessor = load_json(args.predecessor)
    trace_rows = load_jsonl(args.trace)
    errors = validate_envelope(envelope, predecessor, trace_rows)
    receipt = build_receipt(envelope, errors)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, ensure_ascii=False, sort_keys=True))
    return 0 if receipt["valid"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
