#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ENVELOPE = ROOT / "data/governance/RLL_ATLAS_CONTINUOUS_EVOLUTION_ENVELOPE_20260827_V2.json"
DEFAULT_TRACE = ROOT / "data/governance/RLL_ATLAS_SESSION_INTERACTION_TRACE_20260827_V2.jsonl"
DEFAULT_PREDECESSOR = ROOT / "data/governance/RLL_ATLAS_EVOLUTION_GATE_20260827_V1.json"

OMEGA6 = (
    "OMEGA6_PROVENANCE_LOCK", "OMEGA6_RECEIPT_CHAIN", "OMEGA6_CUSTODY_DAG",
    "OMEGA6_ADVERSARIAL_PARITY", "OMEGA6_REPRO_REPLAY", "OMEGA6_INDEPENDENT_REPLICATION",
)
MESH_FENCES = (
    "FENCE-01-AUTHORITY", "FENCE-02-NONREGRESSION", "FENCE-03-FALSIFIABILITY",
    "FENCE-04-ROLLBACK", "FENCE-05-DRIFT", "FENCE-06-INDEPENDENCE",
)
GATES = (
    "G0_SOURCE_RIGHTS_FREEZE", "G1_OBSERVABLE_SCHEMA", "G2_FULL_COVARIANCE",
    "G3_LIKELIHOOD_PARITY", "G4_BASELINE_RECOVERY", "G5_ROBUST_INFERENCE",
    "G6_GROWTH_PERTURBATIONS", "G7_CLAIM_DECISION",
)
MATURITY = {"TOKEN_VAZIO": 0, "BLOCKED": 0, "PARTIAL": 1, "VERIFIED_LIMITED": 2, "VERIFIED": 3, "REPLICATED": 4}
BLOCKERS = {
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
    rows = []
    for n, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if raw.strip():
            value = json.loads(raw)
            if not isinstance(value, dict):
                raise ValueError(f"trace line {n} must be an object")
            rows.append(value)
    return rows


def is_hex(value: Any, size: int) -> bool:
    return isinstance(value, str) and len(value) == size and all(c in "0123456789abcdef" for c in value.lower())


def cycle(node_ids: set[str], edges: list[dict[str, Any]]) -> bool:
    indegree = {n: 0 for n in node_ids}
    adjacency = {n: [] for n in node_ids}
    for edge in edges:
        a, b = edge.get("from"), edge.get("to")
        if a in node_ids and b in node_ids:
            adjacency[a].append(b); indegree[b] += 1
    q = [n for n, d in indegree.items() if d == 0]
    seen = 0
    while q:
        n = q.pop(); seen += 1
        for b in adjacency[n]:
            indegree[b] -= 1
            if indegree[b] == 0: q.append(b)
    return seen != len(node_ids)


def validate_trace(rows: list[dict[str, Any]], expected: str) -> list[str]:
    errors = []
    if [r.get("seq") for r in rows] != list(range(1, len(rows) + 1)):
        errors.append("session trace seq must be contiguous starting at 1")
    for i, row in enumerate(rows, 1):
        if not is_hex(row.get("prompt_sha256"), 64): errors.append(f"trace[{i}].prompt_sha256 invalid")
        if "private_reasoning" in row or "chain_of_thought" in row: errors.append(f"trace[{i}] must not contain private reasoning")
        for key in ("interaction_type", "intent", "action", "outcome", "risk_delta", "next"):
            if not isinstance(row.get(key), str) or not row[key]: errors.append(f"trace[{i}].{key} required")
    canonical = "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in rows)
    actual = hashlib.sha256(canonical.encode()).hexdigest()
    if actual != expected: errors.append(f"session trace SHA-256 mismatch: expected {expected}, got {actual}")
    return errors


def validate_envelope(env: dict[str, Any], predecessor: dict[str, Any], rows: list[dict[str, Any]]) -> list[str]:
    e: list[str] = []
    if env.get("schema") != "rll.atlas_continuous_evolution_envelope.v1": e.append("schema mismatch")
    if env.get("append_only") is not True: e.append("append_only must be true")
    if env.get("claim_allowed") is not False or env.get("publication_ready") is not False: e.append("claim/publication must remain false")

    p = env.get("predecessor", {})
    if p.get("record_id") != predecessor.get("record_id"): e.append("predecessor record_id mismatch")
    if p.get("path") != "data/governance/RLL_ATLAS_EVOLUTION_GATE_20260827_V1.json" or not is_hex(p.get("git_blob_sha1"), 40): e.append("predecessor identity invalid")

    a = env.get("authority", {})
    if (a.get("repository"), a.get("repository_id"), a.get("branch")) != ("instituto-Rafael/relativity-living-light", 1046495816, "rll/lab"): e.append("repository authority mismatch")
    if not is_hex(a.get("base_head_sha"), 40) or not is_hex(a.get("base_tree_sha"), 40): e.append("base authority SHA invalid")
    if a.get("atlas_merge_pr") != 780 or a.get("atlas_merge_commit") != "75323d72c9c8d0180c2a01dfb7c7601f5da735c5": e.append("ATLAS PR#780 lineage mismatch")
    if a.get("session_mesh_pr") != 785 or a.get("session_mesh_merge_commit") != "7ade809036c255dcdfba39bee3a4be16485c0a56": e.append("session mesh PR#785 lineage mismatch")
    if a.get("workflow_inventory_reconcile_pr") != 786 or a.get("workflow_inventory_reconcile_commit") != a.get("base_head_sha"): e.append("workflow inventory PR#786 must be current base authority")

    m = env.get("session_mesh_authority", {})
    if m.get("path") != "data/registries/rll_session_evolution_mesh.v1.json" or not is_hex(m.get("git_blob_sha1"), 40): e.append("session mesh authority pointer invalid")
    mesh_ids = tuple(m.get("existing_fence_ids", []))
    if mesh_ids != MESH_FENCES: e.append("session mesh six-fence authority mismatch")
    if m.get("relationship") != "CONSUMED_AS_AUTHORITY_OMEGA6_IS_ORTHOGONAL_COMPLEMENT": e.append("Ω6 must consume session mesh as orthogonal authority")

    wi = env.get("workflow_inventory_authority", {})
    if wi.get("path") != ".github/workflow-contract.yml" or not is_hex(wi.get("git_blob_sha1"), 40): e.append("workflow inventory authority pointer invalid")
    if wi.get("active_workflows") != 77 or wi.get("source_pr") != 786: e.append("workflow inventory must preserve PR#786 active_workflows=77 authority")

    t = env.get("session_trace", {})
    if t.get("known_event_count") != len(rows): e.append("known_event_count mismatch")
    if t.get("known_prompt_count") != len({r.get("prompt_sha256") for r in rows}): e.append("known_prompt_count mismatch")
    if not is_hex(t.get("sha256"), 64): e.append("trace sha256 invalid")
    else: e.extend(validate_trace(rows, t["sha256"]))

    guards = env.get("omega6_guardrails", [])
    ids = tuple(g.get("id") for g in guards if isinstance(g, dict))
    if ids != OMEGA6: e.append("exact complementary Ω6 guardrail set/order required")
    if set(ids) & set(mesh_ids): e.append("Ω6 guardrails must not duplicate session-mesh fence IDs")
    for g in guards:
        if g.get("state") != "ACTIVE" or g.get("claim_blocking") is not True: e.append(f"{g.get('id')}: guard must be ACTIVE and claim-blocking")
        if not g.get("mode") or not g.get("failure_action"): e.append(f"{g.get('id')}: mode/failure_action required")

    u = env.get("urgency_policy", {})
    if u.get("truth_threshold_mutable") is not False: e.append("urgency may not mutate truth threshold")
    if u.get("evidence_threshold_mutable") is not False: e.append("urgency may not mutate evidence threshold")

    x = env.get("continuous_execution", {})
    if x.get("executor") != ".github/workflows/rll-governance-quality-gate.yml": e.append("Ω6 must reuse existing governance workflow")
    if x.get("auto_merge") is not False: e.append("auto_merge must remain false")
    forbidden = {"automatic scientific claim promotion", "force-moving protected maturity refs", "deleting historical evidence", "auto-merging unreviewed scientific changes"}
    if not forbidden.issubset(set(x.get("forbidden_autonomous_actions", []))): e.append("forbidden autonomous action set incomplete")

    rc = env.get("receipt_chain", {})
    pr = rc.get("predecessor_receipt", {})
    if rc.get("append_only") is not True: e.append("receipt chain must be append-only")
    if pr.get("workflow_run_id") != 33117071438 or not (isinstance(pr.get("digest"), str) and pr["digest"].startswith("sha256:") and is_hex(pr["digest"].split(":", 1)[1], 64)): e.append("predecessor receipt invalid")
    if not is_hex(pr.get("head_sha"), 40): e.append("predecessor receipt head SHA invalid")

    graph = env.get("custody_graph", {}); nodes = graph.get("nodes", []); edges = graph.get("edges", [])
    node_ids = [n.get("id") for n in nodes if isinstance(n, dict)]
    if len(node_ids) != len(set(node_ids)): e.append("custody node IDs must be unique")
    ns = set(node_ids); incoming = {n: 0 for n in ns}
    for n in nodes:
        if not n.get("id") or not n.get("type"): e.append("every custody node needs id/type")
        if n.get("type") in {"SOURCE", "EVIDENCE"} and not is_hex(n.get("git_blob_sha1"), 40): e.append(f"{n.get('id')}: immutable git_blob_sha1 required")
        if n.get("type") == "GENERATED" and not is_hex(n.get("sha256"), 64): e.append(f"{n.get('id')}: generated node SHA-256 required")
    for edge in edges:
        if edge.get("from") not in ns or edge.get("to") not in ns or not edge.get("relation"): e.append("custody edge invalid")
        elif edge["to"] in incoming: incoming[edge["to"]] += 1
    if cycle(ns, edges): e.append("custody graph must be acyclic")
    for n in nodes:
        if n.get("type") in {"GATE", "RECEIPT"} and incoming.get(n.get("id"), 0) == 0: e.append(f"{n.get('id')}: promotion node orphaned")

    gates = env.get("atlas_gate_projection", [])
    if tuple(g.get("id") for g in gates if isinstance(g, dict)) != GATES: e.append("G0-G7 identity/order mismatch")
    pred = {g.get("id"): g for g in predecessor.get("gates", []) if isinstance(g, dict)}
    for g in gates:
        gid, status, maturity = g.get("id"), g.get("status"), g.get("maturity")
        if status not in MATURITY or maturity != MATURITY.get(status): e.append(f"{gid}: status/maturity mismatch"); continue
        old = pred.get(gid)
        if old is None: e.append(f"{gid}: predecessor gate missing"); continue
        old_maturity = old.get("maturity")
        if g.get("predecessor_maturity") != old_maturity: e.append(f"{gid}: predecessor_maturity mismatch")
        if isinstance(old_maturity, int) and maturity < old_maturity: e.append(f"{gid}: maturity regression {old_maturity}->{maturity}")
        if not g.get("evidence"): e.append(f"{gid}: evidence required")
        for item in g.get("evidence", []):
            if not isinstance(item, dict) or not item.get("path") or not is_hex(item.get("git_blob_sha1"), 40): e.append(f"{gid}: evidence path/blob invalid")

    gaps = env.get("gap_reconciliation", []); by_token = {g.get("token"): g for g in gaps if isinstance(g, dict)}
    for token in BLOCKERS:
        item = by_token.get(token)
        if item is None: e.append(f"mandatory blocker omitted: {token}")
        elif item.get("state") == "RESOLVED": e.append(f"{token}: mandatory claim blocker cannot be resolved inline")
    if by_token.get("TOKEN_VAZIO_REAL_BAYES_INFERENCE", {}).get("state") not in {"REDUCED", "OPEN", "OPEN_MIXED"}: e.append("generic Bayes token may be narrowed but not falsely closed by SN-only evidence")
    if by_token.get("TOKEN_VAZIO_INDEPENDENT_REPLICATION", {}).get("state") == "RESOLVED": e.append("internal replay cannot resolve independent replication")

    required = {"TOKEN_VAZIO_NE_PASS", "REDUCED_NE_RESOLVED", "INTERNAL_REPLAY_NE_INDEPENDENT_REPLICATION", "URGENCY_CHANGES_ORDER_NOT_TRUTH", "NEGATIVE_RESULT_IS_EVIDENCE_NOT_REGRESSION"}
    if not required.issubset(set(env.get("invariants", []))): e.append("required anti-regression invariants missing")
    return e


def build_receipt(env: dict[str, Any], errors: list[str]) -> dict[str, Any]:
    gates = env.get("atlas_gate_projection", [])
    maturity_total = sum(int(g.get("maturity", 0)) for g in gates if isinstance(g, dict) and g.get("id") != "G7_CLAIM_DECISION")
    return {
        "schema": "rll.atlas_continuous_evolution_omega6.receipt.v2",
        "record_id": env.get("record_id"),
        "valid": not errors,
        "claim_allowed": False,
        "publication_ready": False,
        "omega6_active_count": sum(1 for g in env.get("omega6_guardrails", []) if isinstance(g, dict) and g.get("state") == "ACTIVE"),
        "scientific_promotion_gate_fraction": round(maturity_total / 21, 6),
        "gate_states": {g.get("id"): g.get("status") for g in gates if isinstance(g, dict)},
        "open_gap_tokens": [g.get("token") for g in env.get("gap_reconciliation", []) if isinstance(g, dict) and str(g.get("state", "")).startswith("OPEN")],
        "errors": errors,
        "boundary": "Repository-local governance/custody progression only; not certification of RLL physics, statistical preference, legal compliance or independent replication."
    }


def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--envelope", type=Path, default=DEFAULT_ENVELOPE); ap.add_argument("--trace", type=Path, default=DEFAULT_TRACE); ap.add_argument("--predecessor", type=Path, default=DEFAULT_PREDECESSOR); ap.add_argument("--output", type=Path, required=True); args = ap.parse_args()
    env = load_json(args.envelope); predecessor = load_json(args.predecessor); rows = load_jsonl(args.trace)
    errors = validate_envelope(env, predecessor, rows); receipt = build_receipt(env, errors)
    args.output.parent.mkdir(parents=True, exist_ok=True); args.output.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, ensure_ascii=False, sort_keys=True)); return 0 if receipt["valid"] else 2


if __name__ == "__main__": raise SystemExit(main())
